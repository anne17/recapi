"""Arla parser class."""

import json
import re
import traceback

from flask import current_app
import html2text

from recapi.html_parsers import GeneralParser

# Set html2text options
text_maker = html2text.HTML2Text()
text_maker.emphasis_mark = "*"
text_maker.ignore_images = True


class ArlaParser(GeneralParser):
    """Parser for recipes at ica.se."""

    domain = "arla.se"
    name = "Arla"
    address = "https://www.arla.se/recept/"

    def __init__(self, url):
        """Init the parser."""
        self.url = url
        self.make_soup()
        self.get_title()
        self.get_image()
        self.get_ingredients()
        self.get_contents()
        self.get_portions()

    def get_title(self):
        """Get recipe title."""
        try:
            self.title = self.soup.find(class_="c-recipe__details").find("h1").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            self.image = self.soup.find(class_="c-recipe__image").find("picture").find("img").get("src", "")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients_raw = self.soup.find(class_="c-recipe__ingredients-inner").find_all("div")
            ingredients = []
            for i in ingredients_raw:
                model = json.loads(i.get("data-model", "{}"))
                if model.get("ingredientGroups"):
                    ilist = model["ingredientGroups"]
                    for sublist in ilist:
                        if sublist.get("title"):
                            ingredients.append(f"\n{sublist.get('title')}\n")
                        for x in sublist.get("ingredients", []):
                            ingredients.append(f"* {x.get('formattedAmount')} {x.get('formattedName')}")

            self.ingredients = "\n".join(ingredients).strip()
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents_raw = self.soup.find(class_="c-recipe__instructions-steps").find_all("div")
            contents = []
            for c in contents_raw:
                model = json.loads(c.get("data-model"))
                for section in model.get("sections", []):
                    if section.get("title"):
                        contents.append(f"\n{section.get('title')}:")
                    for i, step in enumerate(section.get("steps", []), 1):
                        contents.append(f"{i}. {step.get('text').strip()}")
            self.contents = "\n".join(contents).strip()

        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions."""
        try:
            portions = self.soup.find(class_="c-recipe__ingredients-inner").find("div").get("data-model")
            model = json.loads(portions)
            # Portions in plain text
            if model.get("notScalablePortionText"):
                self.portions = model.get("notScalablePortionText").lstrip("Receptet gäller för ")
                return
            # Portions in selector
            self.portions = str(model.get("portionCount")) + " portioner"
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
