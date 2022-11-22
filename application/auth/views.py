import json
from urllib.parse import urlencode, quote_plus

from flask import (
    Blueprint,
    current_app,
    session,
    redirect,
    url_for,
    request,
    render_template,
)

from application.auth.utils import requires_auth

auth = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")


@auth.route("/userinfo")
@requires_auth
def dashboard():
    return render_template(
        "userinfo.html",
        userinfo=session.get("user"),
        userinfo_pretty=json.dumps(session.get("user"), indent=4),
    )


@auth.route("/login")
def login():
    session["redirect_url"] = request.args.get("redirect_url")
    oauth = current_app.config["oauth"]
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + current_app.config["AUTH0_DOMAIN"]
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("frontend.index", _external=True),
                "client_id": current_app.config["AUTH0_CLIENT_ID"],
            },
            quote_via=quote_plus,
        )
    )


@auth.route("/callback", methods=["GET", "POST"])
def callback():

    try:
        oauth = current_app.config["oauth"]
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        redirect_url = session.pop("redirect_url", None)
        if redirect_url is not None:
            return redirect(redirect_url)

    except Exception as e:
        print(e)

    return redirect(url_for("frontend.index"))
