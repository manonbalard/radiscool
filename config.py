import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = "Secret Key"
    SQLALCHEMY_DATABASE_URI = 'mysql://root:''@localhost/radiscool'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
