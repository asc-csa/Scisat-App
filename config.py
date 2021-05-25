import os.path

class Config:
    LANGUAGES = {'en': 'English', 'fr': 'French'}
    DEFAULT_LANGUAGE = 'en'
    APP_PREFIX = '/app/scisat/'
    DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + r'/../../data'
    EN_LINK = '../app/scisat' #url for the english version
    FR_LINK = '../app/scisat-fr' #url for the french version
