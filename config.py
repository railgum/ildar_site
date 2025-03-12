import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SLIDER_ID = 'slider'
SLIDER = 'BigPhoto'
MAX_SIZE_SLIDER = (1024, 500)
MINICARDS_ID = 'cards'
MINICARDS = 'SmallBlocks'
MAX_SIZE_MINICARDS = (256, 256)
FEATURETTE_ID = 'features'
FEATURETTE = 'BigBlocks'
MAX_SIZE_FEATURETTE = (500, 500)
FOOTER = 'Copyright'
FOOTER_ID = 'Footerblock'
