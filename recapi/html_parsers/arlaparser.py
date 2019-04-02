"""Arla parser class."""

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

    def get_title(self):
        """Get recipe title."""
        self.title = self.soup.find(class_="recipe-header__heading").text

    def get_image(self):
        """Get recipe main image."""
        self.image = self.soup.find(class_="image-box-recipe__image focuspoint").find("img").get("src", "")

    def get_ingredients(self):
        """Get recipe ingredients list."""
        ingredients = self.soup.find(class_="recipe-ingredients")
        ingredients = ingredients.find_all(["li"])
        ingredients = "".join(str(i) for i in ingredients)
        self.ingredients = text_maker.handle(ingredients).strip()

    def get_contents(self):
        """Get recipe description."""
        contents = self.soup.find(class_="instructions-area__text")
        self.contents = text_maker.handle(str(contents)).strip()
