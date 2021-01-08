"""Coop parser class."""

import traceback

import html2text
from flask import current_app

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
            self.title = self.soup.find(class_="Section").find("h1").text
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

            for li in ingredients("li"):
                if not li.text:  # Remove empty list items
                    li.decompose()
                else:
                    if "List-heading" in li.get("class"):  # Prettify headers
                        li.name = "ul"
                        li.string = li.text + ":"
            self.ingredients = text_maker.handle(str(ingredients)).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find_all(class_="Tab-panel")[-1]
            for i in contents.find_all("h2"):
                if i.text.strip() == "Gör så här":
                    i.decompose()
                else:
                    i.name = "div"
                    i.string = i.text + ":"
            self.contents = text_maker.handle(str(contents)).strip("\n")
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions."""
        try:
            portions = self.soup.find(class_="Grid-cell Grid-cell--fit").text
            self.portions = portions.strip()
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
