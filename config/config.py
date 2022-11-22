# -*- coding: utf-8 -*-
import os


def _to_boolean(val):
    if val is not None and val.lower() in ['true', 't', 'on', 'y', 'yes']:
        return True
    return False


class Config(object):

    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
    AUTH0_BASE_URL = f"https://{AUTH0_DOMAIN}"
    AUTH0_AUDIENCE = f"{AUTH0_BASE_URL}/userinfo"
    AUTHENTICATION_ON = _to_boolean(os.environ.get('AUTHENTICATION_ON'))
    S3_USER_AGENT = os.getenv('S3_USER_AGENT')
    S3_CPO_FILE_URL = os.getenv('S3_CPO_FILE_URL')
    SEARCH_URL = os.getenv('SEARCH_URL')
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True
