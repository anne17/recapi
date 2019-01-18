import re
import os
import importlib
import pkgutil
import urllib
import requests

from flask import current_app
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
        recipe["contents"] = parser.contents
        recipe["ingredients"] = parser.ingredients
        recipe["source"] = parser.url
        image_path = download_image(parser.image)
        recipe["image"] = image_path

        return utils.success_response("Successfully extracted recipe.", data=recipe)
    else:
        return utils.error_response(f"No parser found for URL {url}.")


def find_parser(parsers, url):
    """Find parser that can parse url."""
    domain = extract_domain(url)

    # Create domain dict
    domain_dict = {}
    for p in parsers:
        domain_dict[p.base_url] = p

    return domain_dict.get(domain)


def extract_domain(url):
    """Extract domain name from url."""
    pattern = r"^(?:https?://)?(?:[\w\.]+\.)?(\w+\.\w+)(?:/|$)"
    match = re.search(pattern, url)
    return match.group(1)


def download_image(image_url):
    """Retrieve image from URL and save it as a temporary file."""
    try:
        # Get file info, check if content type is image
        file_info = urllib.request.urlopen(image_url).info()
        content_type = file_info.get('Content-Type')
        if utils.IMAGE_FORMATS.get(content_type):
            file_ending = utils.IMAGE_FORMATS.get(content_type)
        else:
            # Not an image! TODO: log error
            return ""

        # Get image data and save in tmp dir
        img_data = requests.get(image_url).content
        filename = utils.make_filename("", file_extension=file_ending)
        directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
        utils.save_upload_data(img_data, filename, directory)

        filepath = "tmp/" + filename
        return filepath

    except Exception as e:
        print(e)
        # logging.error(traceback.format_exc())
        return ""
