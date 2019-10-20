"""Tasteline parser class."""

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


class TastelineParser(GeneralParser):
    """Parser for recipes at tasteline.com."""

    domain = "tasteline.com"
    name = "Tasteline"
    address = "https://www.tasteline.com/recept/"

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
            self.title = self.soup.find(class_="recipe-description").find("h1").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            self.image = self.soup.find(class_="recipe-header-image").find("img").get("src", "")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find_all(class_="ingredient-group")
            out = []
            for i in ingredients:
                # Convert h3 into div
                for x in i.find_all("h3"):
                    x.name = "div"
                out.append(text_maker.handle(str(i)).strip())
            self.ingredients = "\n\n".join(i for i in out)
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(class_="steps")
            contents.h2.decompose()  # Remove header
            [x.extract() for x in contents.find_all(class_='row')]  # remove meta data
            # Convert h3 into b
            for x in contents.find_all("h3"):
                x.name = "b"
            # Convert ul into ol
            for x in contents.find_all("ul"):
                x.name = "ol"
            # Remove numbers
            for x in contents.find_all("li"):
                x.string = re.sub(r"^\d{1,2}\.\s", r"", x.text)
            self.contents = text_maker.handle(str(contents)).strip()
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions."""
        try:
            portions = self.soup.find(class_="portions")
            self.portions = portions.find("option", selected=True).text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
