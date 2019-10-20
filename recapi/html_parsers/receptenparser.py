"""recepten.se parser class."""

import re
import traceback

from flask import current_app
import html2text

from recapi.html_parsers import GeneralParser

# Set html2text options
text_maker = html2text.HTML2Text()
text_maker.emphasis_mark = "*"
text_maker.ignore_links = True
text_maker.ignore_images = True


class ICAParser(GeneralParser):
    """Parser for recipes at recepten.se."""

    domain = "recepten.se"
    name = "recepten.se"
    address = "https://www.recepten.se/recept/"

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
            self.title = self.soup.find(id="content").find("h1").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            image = self.soup.find(id="content").find(id="mainImageContainer").find("img").get("src", "")
            self.image = "https://recepten.se" + image
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find(class_="list ingredients")
            ingredients = text_maker.handle(str(ingredients))
            ingredients = ingredients.strip()
            # Remove indentation
            self.ingredients = re.sub(r"\n\s+", r"\n", ingredients)
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(class_="list instructionItem")
            # Remove ingredients lists
            for i in contents.find_all("ul"):
                i.decompose()
            # Remove image information
            for i in contents.find_all("div"):
                if i.get("class") and "clearAfter" in i.get("class"):
                    i.decompose()
            contents = text_maker.handle(str(contents))
            # Remove indentation
            contents = contents.strip()
            self.contents = re.sub(r"\n\s+", r"\n", contents)
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions for recipe."""
        try:
            self.portions = self.soup.find_all(class_="property")[-1].text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
