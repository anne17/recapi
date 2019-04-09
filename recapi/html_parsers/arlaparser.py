"""Arla parser class."""

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
            self.title = self.soup.find(class_="recipe-header__heading").text
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            self.image = self.soup.find(class_="image-box-recipe__image").find("img").get("src", "")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find(class_="recipe-ingredients")
            ingredients = ingredients.find_all(["li"])
            ingredients = "".join(str(i) for i in ingredients)
            self.ingredients = text_maker.handle(ingredients).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(class_="instructions-area__text")
            self.contents = text_maker.handle(str(contents)).strip()
            if not contents:
                contents = self.soup.find(class_="instructions-area__steps")
                contents = text_maker.handle(str(contents)).strip()
                # Remove indentation
                self.contents = re.sub(r"\n{2}\s+", r"\n", contents)
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions."""
        try:
            # Portions in plain text
            portions = self.soup.find(class_="servings-selector__label")
            if portions:
                self.portions = portions.text.lstrip("Receptet gäller för ")
                return
            # Portions in selector
            portions = self.soup.find(class_="servings-selector__select").find("option", {"selected": "selected"})
            if portions:
                self.portions = portions.text.rstrip(" port")
                return
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
