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
            self.title = self.soup.find(class_="Recipe-title").text
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            image = self.soup.find(class_="Recipe-imageWrapperContainer").find("img").get("src", "")
            self.image = "http://" + image.lstrip("/")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find(class_="Recipe-ingredients")
            portions = ingredients.find(class_="Recipe-portions")  # Remove portions
            portions.decompose()
            legend = ingredients.find(class_="Recipe-ingredientLegend")
            legend.decompose()
            for h2 in ingredients("h2"):  # Remove "Ingredients"
                h2.decompose()
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
            portions = self.soup.find(class_="Recipe-portionsCount").text
            self.portions = re.sub(r" portioner$", r"", portions)
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
