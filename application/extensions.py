from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.flask.client import OAuth  # noqa
from flask_debugtoolbar import DebugToolbarExtension  # noqa

db = SQLAlchemy()
migrate = Migrate(db=db)
