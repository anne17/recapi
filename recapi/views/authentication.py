"""Routes related to user authentication."""

from flask import request, session, current_app, Blueprint

from recapi.models.usermodel import User, get_user
from recapi import utils

bp = Blueprint("authentication", __name__)


@bp.route('/check_authentication', methods=['POST'])
def check_authentication():
    """Check if current user is authorized in the active session."""
    if session.get("authorized"):
        current_app.logger.debug("User authorized: %s" % session.get("user"))
        return utils.success_response("User authorized", authenticated=True,
                                      user=session.get("user"), admin=session.get("admin"))
    else:
        return utils.success_response("Access denied", authenticated=False)


@bp.route('/login', methods=['POST'])
def login():
    """Check user credentials and log in if authorized."""
    if session.get("authorized"):
        return utils.success_response("User already authorized!", user=session.get("user"))
    else:
        username = request.form.get("login")
        password = request.form.get("password")
        try:
            user = get_user(username)
            current_app.logger.debug(f"User: {user.username}, {user.displayname}, {user.is_authenticated(password)}")
        except User.DoesNotExist:
            return utils.error_response("Invalid username or password!"), 401

        if user.is_authenticated(password):
            session["authorized"] = True
            session["user"] = user.displayname
            session["uid"] = user.id
            session["admin"] = user.admin
            # For non-admin users make session expire when closing browser
            if not user.admin:
                session.permanent = False
            current_app.logger.debug("User %s logged in successfully" % username)
            return utils.success_response("User %s logged in successfully!" % username,
                                          user=user.displayname, admin=user.admin)
        return utils.error_response("Invalid username or password!"), 401


@bp.route('/logout', methods=['POST'])
def logout():
    """Remove session for current user."""
    session.clear()
    return utils.success_response("Logged out successfully")
