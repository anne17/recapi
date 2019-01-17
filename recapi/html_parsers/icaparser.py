import re
import html2markdown

from recapi.html_parsers import GeneralParser


class ICAParser(GeneralParser):

    base_url = "ica.se"

    def __init__(self, url):
        self.url = url
        self.make_soup()
        self.get_title()
        self.get_image()
        self.get_ingredients()
        self.get_contents()

    def get_title(self):
        self.title = title = self.soup.find(class_="recipepage__headline").text

    def get_image(self):
        image = self.soup.find(class_="recipe-image-square__image").get("style", "")
        match = re.match(r"background-image: url\('\/*(.*)'\)", str(image))
        self.image = match.group(1)

    def get_ingredients(self):
        ingredients = self.soup.find(class_="ingredients")
        ingredients = remove_attrs(ingredients).find_all(["ul", "strong"])
        ingredients = "".join(str(i) for i in ingredients)
        ingredients = html2markdown.convert(ingredients)
        self.ingredients = remove_spans(ingredients)

    def get_contents(self):
        contents = self.soup.find(class_="recipe-howto-steps").find("ol")
        self.contents = html2markdown.convert(str(contents))


def remove_attrs(soup):
    """Remove all attributes from all nodes in a BeautifulSoup object."""
    for tag in soup.findAll(True):
        tag.attrs = {}
    return soup

def remove_spans(instring):
    """Remove span tags from string."""
    outstring = re.sub("<span>", "", instring)
    outstring = re.sub("</span>", "", outstring)
    return outstring
