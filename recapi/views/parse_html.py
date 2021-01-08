"""Routes and utilities for html parsing."""

import importlib
import io
import os
import pkgutil
import re
import traceback
import urllib.parse
from urllib.request import Request, urlopen

import requests
from flask import Blueprint, current_app, request
from PIL import Image
from recapi import html_parsers, utils
from recapi.html_parsers import GeneralParser

bp = Blueprint("parser_views", __name__)


@bp.route("/parse_from_url")
def parse_from_url():
    """Extract recipe data from given url and return response with recipe data."""
    url = request.args.get("url")
    if not url.startswith("http"):
        url = "http://" + url
    if not utils.valid_url(url):
        return utils.error_response(f"Invalid URL: {url}."), 400

    import_parsers()

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
        recipe["portions_text"] = parser.portions
        image_path = download_image(parser.image)
        recipe["image"] = image_path

        return utils.success_response("Successfully extracted recipe.", data=recipe)
    else:
        return utils.error_response(f"No parser found for URL {url}."), 400


@bp.route("/get_parsers")
def get_parsers():
    """Get a list of recipe pages for which there is a parser available."""
    import_parsers()
    try:
        pages_list = [{"domain": p.domain,
                       "name": p.name,
                       "address": p.address} for p in GeneralParser.__subclasses__()]
        return utils.success_response("Successfully retrieved list of parsable pages.", data=pages_list)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return utils.error_response(f"Could not retrieve list of parsable pages: {e}"), 500


def import_parsers():
    """Import all modules from html_parsers sub package."""
    parser_module_path = os.path.dirname(html_parsers.__file__)
    for (_module_loader, name, _ispkg) in pkgutil.iter_modules([parser_module_path]):
        importlib.import_module(f"{html_parsers.__name__}.{name}", __package__)


def find_parser(parsers, url):
    """Find parser that can parse url."""
    domain = extract_domain(url)

    # Create domain dict
    domain_dict = {}
    for p in parsers:
        domain_dict[p.domain] = p

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
        # Add headers to avoid being blocked by some servers
        headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)"
                                  "Chrome/41.0.2228.0 Safari/537.3")}
        # Handle non-ascii URLs
        image_url = list(urllib.parse.urlsplit(image_url))
        image_url[2] = urllib.parse.quote(image_url[2])
        image_url = urllib.parse.urlunsplit(image_url)
        # Check content type
        file_info = urlopen(Request(url=image_url, headers=headers)).info()
        content_type = file_info.get("Content-Type")
        if not utils.IMAGE_FORMATS.get(content_type):
            current_app.logger.error(f"URL did not point to an image: {image_url}")
            return ""

        # Get image data, convert it to jpg and save in tmp dir
        img_data = requests.get(image_url).content
        filelike = io.BytesIO(img_data)
        imageobj = Image.open(filelike)
        imageobj = imageobj.convert("RGB")
        imageobj.save(filelike, format="jpeg")

        filename = utils.make_random_filename("", file_extension=".jpg")
        directory = os.path.join(current_app.instance_path, current_app.config.get("TMP_DIR"))
        utils.save_upload_data(filelike.getvalue(), filename, directory)

        return "tmp/" + filename

    except Exception:
        current_app.logger.error(traceback.format_exc())
        return ""
