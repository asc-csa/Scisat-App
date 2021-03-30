import os.path

class Config:
    LANGUAGES = {'en': 'English', 'fr': 'French'}
    DEFAULT_LANGUAGE = 'fr'
    APP_URL = 'alouette/en'
    DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + r'/../../data'