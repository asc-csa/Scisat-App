import os.path

class Config:
    LANGUAGES = {'en': 'English', 'fr': 'French'}
    DEFAULT_LANGUAGE = 'en'
    APP_PREFIX = '/scisat/'
    DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + r'/../../data'
    EN_LINK = '/scisat' #url for the english version
    FR_LINK = '/scisat-fr' #url for the french version
