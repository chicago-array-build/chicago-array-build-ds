from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    ENV = getenv('FLASK_ENV')
    JSON_ADD_STATUS = getenv('JSON_ADD_STATUS')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
