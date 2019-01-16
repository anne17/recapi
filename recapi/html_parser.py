import re
import requests
import html2markdown
from bs4 import BeautifulSoup


class GeneralParser():

    # def __init__(self, url):
    #     self.url = url
    #     self.make_soup()

    def make_soup(self):
        """Get HTML and create BeautifulSoup object."""
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")

    def get_source(self):
        """Get source URL for recipe."""
        self.source = self.url

    def can_parse(self):
        """Check if this is the right parser for the URL."""
        pattern = re.compile(self.base_url)
        match = pattern.search(selfurl)
        if match:
            return True
        return False


class ICAParser(GeneralParser):

    def __init__(self, url):
        self.base_url = "www.ica.se/recept/"
        self.url = url
        self.make_soup()


def parse(url):
    parser = match_parser(url)
    if parser:
        parser(url)


def match_parser(url):
    for parser, base_url in PARSERS.items():
        pattern = re.compile(base_url)
        match = pattern.search(url)
        if match:
            return parser
    return None


def ica_parser(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.text, "html.parser")

    title = soup.find(class_="recipepage__headline").text

    contents = soup.find(class_="recipe-howto-steps").find("ol")
    contents = html2markdown.convert(str(contents))

    ingredients = soup.find(class_="ingredients")
    ingredients = remove_attrs(ingredients).find_all(["ul", "strong"])
    ingredients = "".join(str(i) for i in ingredients)
    ingredients = html2markdown.convert(ingredients)
    ingredients = remove_spans(ingredients)

    image = soup.find(class_="recipe-image-square__image").get("style", "")
    match = re.match(r"background-image: url\('\/*(.*)'\)", str(image))
    image = match.group(1)

    print(f"\nTitle:\n{title}")
    print(f"\nImage:\n{image}")
    print(f"\nContents:\n{contents}")
    print(f"\nIngredients:\n{ingredients}")
    print(f"\nSource:\n{url}")


PARSERS = {
    ica_parser: "www.ica.se/recept/"
}

#############
# Auxiliaries
#############

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


if __name__ == '__main__':
    # url = "https://www.ica.se/recept/tikka-masala-med-fars-och-broccoli-724835/"
    url = "https://www.ica.se/recept/morotssoppa-med-kokos-722533/"
    # parse(url)
    ica_parser = ICAParser(url)
    print(ica_parser.soup)
