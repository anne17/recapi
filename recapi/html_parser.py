import re
import requests
import html2markdown
from bs4 import BeautifulSoup

PARSERS = {
    "ica_parser": "www.ica.se/recept/"
}


def parse(url):
    parser = match_parser(url)
    if parser:
        eval(parser)(url)


def match_parser(url):
    for parser, base_url in PARSERS.items():
        pattern = re.compile(base_url)
        match = pattern.search(url)
        if match:
            return parser
    return None


def remove_attrs(soup):
    for tag in soup.findAll(True):
        tag.attrs = {}
    return soup


def remove_spans(instring):
    outstring = re.sub("<span>", "", instring)
    outstring = re.sub("</span>", "", outstring)
    return outstring


def ica_parser(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.text, "html.parser")

    title = soup.find(class_="recipepage__headline").text

    contents = soup.find(class_="recipe-howto-steps").find("ol")
    contents = html2markdown.convert(str(contents))

    ingredients = soup.find(class_="ingredients")
    ingredients = remove_attrs(ingredients).find_all("ul")
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


if __name__ == '__main__':
    url = "https://www.ica.se/recept/tikka-masala-med-fars-och-broccoli-724835/"
    parse(url)
