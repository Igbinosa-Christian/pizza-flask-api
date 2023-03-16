import os
import re
from decouple import config  #to store variables(python_decouple)
from datetime import timedelta

base_dir = os.path.dirname(os.path.realpath(__file__))


class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')



class DevConfig(Config):
    DEBUG = config('DEBUG', cast=bool)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'db.sqlite3')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://' #Memory Database


# For deployment
class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'db.sqlite3') 
    SQLALCHEMY_TRACK_MODIFICATION = False
    DEBUG = config('DEBUG', False, cast=bool)
    



config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}
