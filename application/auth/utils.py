from functools import wraps

from flask import session, url_for, request, current_app
from werkzeug.utils import redirect


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session and current_app.config["AUTHENTICATION_ON"]:
            return redirect(url_for("auth.login", redirect_url=request.path))
        return f(*args, **kwargs)

    return decorated


def get_current_user():
    if session and session.get("user") is not None:
        if session["user"].get("nickname") is not None:
            return session["user"].get("nickname")
        else:
            return session["user"].get("name")
    else:
        return None
