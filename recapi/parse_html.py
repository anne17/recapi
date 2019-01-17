import re
from recapi.html_parsers.icaparser import ICAParser

# TODO: List parsers automatically... somehow.
PARSERS = [ICAParser]

def parse(url):
    """Parse url and return something useful."""
    p = find_parser(PARSERS, url)
    if p:
        parser = p(url)
        print(f"\nTitle:\n{parser.title}")
        print(f"\nImage:\n{parser.image}")
        print(f"\nContents:\n{parser.contents}")
        print(f"\nIngredients:\n{parser.ingredients}")
        print(f"\nSource:\n{parser.url}")
    else:
        print("No parser found for URL {url}.")


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
