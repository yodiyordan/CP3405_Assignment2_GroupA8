import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MLABDB = os.environ.get('MLABDB')
    MLABURI = os.environ.get('MLABURI')

