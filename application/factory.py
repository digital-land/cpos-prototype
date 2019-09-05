# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask.cli import load_dotenv

from application.models import *

load_dotenv()


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 10

    register_errorhandlers(app)
    register_blueprints(app)
    register_extensions(app)
    register_filters(app)

    return app


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("error/{0}.html".format(error_code)), error_code
    for errcode in [400, 401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_extensions(app):
    from application.extensions import db
    db.init_app(app)

    from application.extensions import migrate
    migrate.init_app(app=app)

    from application.extensions import OAuth
    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        api_base_url=app.config['AUTH0_BASE_URL'],
        access_token_url=f"{app.config['AUTH0_BASE_URL']}/oauth/token",
        authorize_url=f"{app.config['AUTH0_BASE_URL']}/authorize",
        client_kwargs={
            'scope': 'openid profile',
        },
    )

    app.config['auth0'] = auth0

    from application.extensions import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)


def register_filters(app):
    from application.filters import map_la_code_to_name
    app.add_template_filter(map_la_code_to_name)
    from application.filters import flatten_tuples
    app.add_template_filter(flatten_tuples)
    from application.filters import map_cpo_status_to_tag_class
    app.add_template_filter(map_cpo_status_to_tag_class)
    from application.filters import remove_item
    app.add_template_filter(remove_item)


def register_blueprints(app):
    from application.frontend.views import frontend
    app.register_blueprint(frontend)

    from application.auth.views import auth
    app.register_blueprint(auth)

