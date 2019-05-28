"""ICA parser class."""

import re
import traceback

from flask import current_app
import html2text

from recapi.html_parsers import GeneralParser

# Set html2text options
text_maker = html2text.HTML2Text()
text_maker.emphasis_mark = "*"


class ICAParser(GeneralParser):
    """Parser for recipes at ica.se."""

    domain = "ica.se"
    name = "ICA"
    address = "https://www.ica.se/recept/"

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
            self.title = self.soup.find(class_="recipepage__headline").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            image = self.soup.find(class_="recipe-image-square__image").get("style", "")
            match = re.match(r"background-image: url\('(.*)'\)", str(image))
            self.image = "https:" + match.group(1)
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find(class_="ingredients")
            ingredients = ingredients.find_all(["ul", "strong"])
            ingredients = "".join(str(i) for i in ingredients)
            self.ingredients = text_maker.handle(ingredients).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(class_="recipe-howto-steps").find("ol")
            contents = text_maker.handle(str(contents)).strip()
            # Remove indentation
            self.contents = re.sub(r"\n\s+", r"\n", contents)
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions for recipe."""
        try:
            self.portions = self.soup.find(class_="servings-picker__servings").text
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
