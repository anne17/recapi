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
            self.title = self.soup.find(class_="recipe-header__title").text.strip()
        except Exception:
            current_app.logger.error(f"Could not extract title: {traceback.format_exc()}")
            self.title = ""

    def get_image(self):
        """Get recipe main image."""
        try:
            self.image = self.soup.find(class_="recipe-header__desktop-image-wrapper").find("img").get("src", "")
        except Exception:
            current_app.logger.error(f"Could not extract image: {traceback.format_exc()}")
            self.image = ""

    def get_ingredients(self):
        """Get recipe ingredients list."""
        try:
            ingredients = self.soup.find_all(class_="ingredients-list-group")
            ingredients_list = []
            for i in ingredients:
                if "extra" in i.get("class", []):
                    continue
                heading = i.find(class_="ingredients-list-group__heading")
                if heading:
                    ingredients_list.append("\n" + heading.text + ":\n")
                for row in i.find_all(class_="ingredients-list-group__card"):
                    quantity = text_maker.handle(str(row.find(class_="ingredients-list-group__card__qty"))).strip()
                    if quantity in ["-", "None"]:
                        quantity = ""
                    else:
                        quantity += " "
                    ingredient = text_maker.handle(str(row.find(class_="ingredients-list-group__card__ingr"))).strip()
                    ingredients_list.append("* " + quantity + ingredient)
            self.ingredients = "\n".join(ingredients_list)
        except Exception:
            current_app.logger.error(f"Could not extract ingredients: {traceback.format_exc()}")
            self.ingredients = ""

    def get_contents(self):
        """Get recipe description."""
        try:
            contents = self.soup.find(id="steps").find_all(class_="cooking-steps-main--step")
            contents_list = []

            for n, div in enumerate(contents, start=1):
                for i in div.find_all(class_="timer-wrapper"):
                    i.decompose()
                contents_list.append(str(n) + ". " + text_maker.handle(str(div)).strip())
            self.contents = "\n".join(contents_list)
            # Remove indentation
            # self.contents = re.sub(r"\n\s+", r"\n", contents)
        except Exception:
            current_app.logger.error(f"Could not extract contents: {traceback.format_exc()}")
            self.contents = ""

    def get_portions(self):
        """Get number of portions for recipe."""
        try:
            portions = self.soup.find(class_="default-portions")
            if portions:
                self.portions = portions.text
            else:
                portions = self.soup.find(class_="ingredients-change-portions").get("default-portions", "")
                self.portions = portions + " portioner" if portions else ""
        except Exception:
            current_app.logger.error(f"Could not extract portions: {traceback.format_exc()}")
            self.portions = ""
