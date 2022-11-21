from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate(db=db)
