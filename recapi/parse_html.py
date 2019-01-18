import re
import os
import importlib
import pkgutil
from recapi import utils, html_parsers
from recapi.html_parsers import GeneralParser


def parse(url):
    """Parse url and return response with recipe data."""
    # Import all modules from html_parsers sub package
    parser_module_path = os.path.dirname(html_parsers.__file__)
    for (_module_loader, name, _ispkg) in pkgutil.iter_modules([parser_module_path]):
        importlib.import_module(f"{html_parsers.__name__}.{name}", __package__)

    # Collect all parser classes
    all_parsers = [parser for parser in GeneralParser.__subclasses__()]

    p = find_parser(all_parsers, url)
    if p:
        recipe = {}
        parser = p(url)
        recipe["title"] = parser.title
        recipe["image"] = parser.image
        recipe["contents"] = parser.contents
        recipe["ingredients"] = parser.ingredients
        recipe["source"] = parser.url
        # print(f"\nTitle:\n{parser.title}")
        # print(f"\nImage:\n{parser.image}")
        # print(f"\nContents:\n{parser.contents}")
        # print(f"\nIngredients:\n{parser.ingredients}")
        # print(f"\nSource:\n{parser.url}")
        return utils.success_response("Successfully extracted recipe.", data=recipe)
    else:
        return utils.error_response(f"No parser found for URL {url}.")


def extract_domain(url):
    """Extract domain name from url."""
    pattern = r"^(?:https?://)?(?:[\w\.]+\.)?(\w+\.\w+)(?:/|$)"
    match = re.search(pattern, url)
    return match.group(1)


def find_parser(parsers, url):
    """Find parser that can parse url."""
    domain = extract_domain(url)

    # Create domain dict
    domain_dict = {}
    for p in parsers:
        domain_dict[p.base_url] = p

    return domain_dict.get(domain)
