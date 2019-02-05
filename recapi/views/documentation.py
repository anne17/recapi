"""Routes related to the API documentation."""

import os

import yaml
from flask import current_app, Blueprint, jsonify, render_template, url_for, redirect

bp = Blueprint("documentation", __name__)


@bp.route("/api_spec")
def api_spec():
    """Return open API specification in json."""
    spec_file = os.path.join(current_app.static_folder, "recapi-oas.yaml")
    with open(spec_file, encoding="UTF-8") as f:
        return jsonify(yaml.load(f))


@bp.route("/")
def base_route():
    """Redirect to /api_doc."""
    return redirect(url_for('documentation.api_doc', _external=True))


@bp.route("/api_doc")
def api_doc():
    """Render HTML API documentation."""
    current_app.logger.info("URL: %s", url_for("documentation.api_spec", _external=True))
    return render_template('apidoc.html',
                           title="recAPI documentation",
                           favicon=url_for("static", filename="favicon.ico", _external=True),
                           spec_url=url_for("documentation.api_spec", _external=True)
                           )
