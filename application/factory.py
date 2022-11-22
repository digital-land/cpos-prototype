# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask.cli import load_dotenv

from application.models import *  # noqa

load_dotenv()


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 10

    register_errorhandlers(app)
    register_blueprints(app)
    register_extensions(app)
    register_filters(app)
    register_commands(app)

    return app


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template("error/{0}.html".format(error_code)), error_code

    for errcode in [400, 401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_extensions(app):
    from application.extensions import db

    db.init_app(app)

    from application.extensions import migrate

    migrate.init_app(app=app)

    from authlib.integrations.flask_client import OAuth

    oauth = OAuth(app)

    oauth.register(
        "auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid profile email",
        },
    )

    app.config["oauth"] = oauth


def register_filters(app):
    from application.filters import map_la_code_to_name

    app.add_template_filter(map_la_code_to_name)
    from application.filters import flatten_tuples

    app.add_template_filter(flatten_tuples)
    from application.filters import map_cpo_status_to_tag_class

    app.add_template_filter(map_cpo_status_to_tag_class)
    from application.filters import remove_item

    app.add_template_filter(remove_item)
    from application.filters import tuple_list_to_dict

    app.add_template_filter(tuple_list_to_dict)
    from application.filters import count_with_investigation

    app.add_template_filter(count_with_investigation)
    from application.filters import map_cpo_status_display_name

    app.add_template_filter(map_cpo_status_display_name)
    from application.filters import cap_first_letter

    app.add_template_filter(cap_first_letter)


def register_blueprints(app):
    from application.frontend.views import frontend

    app.register_blueprint(frontend)

    from application.auth.views import auth

    app.register_blueprint(auth)


def register_commands(app):
    from application.commands import load_pdfs

    app.cli.add_command(load_pdfs, name="load_pdfs")
