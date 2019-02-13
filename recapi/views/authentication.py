"""Routes related to user authentication."""

from flask import request, session, current_app, Blueprint

from recapi.models.user import User
from recapi import utils

bp = Blueprint("authentication", __name__)


@bp.route('/check_authentication', methods=['POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        current_app.logger.debug("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", authenticated=True, user=session.get("user"))
    else:
        return utils.success_response("Access denied", authenticated=False)


@bp.route('/login', methods=['POST'])
def login():
    """Check user credentials and log in if authorized."""
    if session.get("authorized"):
        return utils.success_response("User already authorized!", user=session.get("user"))
    else:
        username = request.get_json().get("login")
        password = request.get_json().get("password")
        user = User(username)
        current_app.logger.debug(f"User: {user.username}, {user.displayname}, {user.is_authenticated(password)}")

        if user.is_authenticated(password):
            session["authorized"] = True
            session["user"] = user.displayname
            session["uid"] = user.uid
            current_app.logger.debug("User %s logged in successfully" % username)
            return utils.success_response("User %s logged in successfully!" % username,
                                          user=user.displayname)
        return utils.error_response("Invalid username or password!"), 401


@bp.route('/logout', methods=['POST'])
def logout():
    """Remove session for current user."""
    session.clear()
    return utils.success_response("Logged out successfully")
