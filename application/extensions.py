
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_migrate import Migrate
migrate = Migrate(db=db)

from authlib.flask.client import OAuth

from flask_debugtoolbar import DebugToolbarExtension