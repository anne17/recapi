"""Allt om Mat parser class."""

import re
import traceback

from flask import current_app
import html2text

from recapi.html_parsers import GeneralParser

# Set html2text options
text_maker = html2text.HTML2Text()
text_maker.emphasis_mark = "*"
text_maker.ignore_tables = True


class ICAParser(GeneralParser):
    """Parser for recipes at alltommat.se."""

    domain = "alltommat.se"
    name = "Allt om Mat"
    address = "https://alltommat.se/recept/"

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
            self.title = self.soup.find(class_="entry-title").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            image = self.soup.find(class_="featured-image-body").find("style").text
            match = re.match(r".*background-image: url\((.*)\)", image)
            self.image = match.group(1)
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find_all(class_=["recipe-table", "table-list-header"])
            ingredients_list = []
            for elem in ingredients:
                if elem.name == "h4" and elem.text.strip() != "":
                    ingredients_list.append("\n\n" + elem.text.strip() + "\n\n")
                elif elem.name == "table":
                    rows = text_maker.handle(str(elem)).split("\n")
                    rows = "\n".join("* " + r for r in rows if r.strip())
                    ingredients_list.append(rows)
            self.ingredients = "".join(ingredients_list).strip()
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(class_="entry-content").find("ol")
            contents = text_maker.handle(str(contents)).strip()
            # Remove indentation
            self.contents = re.sub(r"\n\s+", r"\n", contents)
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions for recipe."""
        try:
            portions = self.soup.find(class_="recipe-servings").text
            portions = portions.rstrip(":")
            portions = re.sub(r"^För ", r"", portions)
            self.portions = re.sub(r"personer$", r"portioner", portions)
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
