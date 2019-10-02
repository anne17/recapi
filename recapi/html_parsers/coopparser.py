"""Coop parser class."""

import re
import traceback

from flask import current_app
import html2text

from recapi.html_parsers import GeneralParser

# Set html2text options
text_maker = html2text.HTML2Text()
text_maker.emphasis_mark = "*"
text_maker.ignore_images = True
text_maker.ignore_links = True


class CoopParser(GeneralParser):
    """Parser for recipes at tasteline.com."""

    domain = "coop.se"
    name = "Coop"
    address = "https://www.coop.se/recept/"

    def __init__(self, url):
        """Init the parser."""
        self.url = url
        self.make_soup()
        self.get_title()
        self.get_image()
        self.get_portions()
        self.get_ingredients()
        self.get_contents()

    def get_title(self):
        """Get recipe title."""
        try:
            self.title = self.soup.find(itemprop="name").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:

            image = self.soup.find(itemprop="image").get("src")
            self.image = "http://" + image.lstrip("/")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find(class_="IngredientList-container")
            header = ingredients.find(class_="List-heading")  # Remove header
            header.decompose()

            for li in ingredients("li"):
                if not li.text:  # Remove empty list items
                    li.decompose()
                else:
                    if "List-heading" in li.get("class"):  # Make headers headers
                        li.name = "ul"
            self.ingredients = text_maker.handle(str(ingredients)).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(itemprop="recipeInstructions")
            for span in contents("span"):  # Remove numbers
                span.decompose()
            self.contents = text_maker.handle(str(contents)).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions."""
        try:
            portions = self.soup.find(class_="Grid-cell Grid-cell--fit").text
            portions = re.sub(r" portioner$", r"", portions)
            self.portions = portions.strip()
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
