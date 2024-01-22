""" Settings for use throughout the program """
import os

from dotenv import load_dotenv

load_dotenv()

# SnipeIT Information - Both the API Key and URL Are required.
# URL must be in the format:
# https://snipeit.example.com/api/v1/
SNIPE_URL = os.getenv('SNIPE_URL')

# for less security, the URL and Key can be entered below within single quotes.
# for high security installations, the key and URL can be passed through
# Environment Variables or using dotenv with a .env file.
API_KEY = os.getenv('API_KEY')

# Logging configuration
LOG_LEVEL = 'DEBUG'
LOG_FILE_LEVEL = 'DEBUG'
LOG_NAME = 'snipescan.log'
LOG_SIZE = 1024
LOG_COUNT = 3

LOGGING_CONFIG = { 
    'version':1,
    'disable_existing_loggers': False,
    'formatters':{
        'standard': {
            'format': '%(asctime)s | %(name)s | %(levelname)s: %(message)s',
            'datefmt': '%Y-%d-%m %I:%M:%S',
        },
        'complex': {
            'format': '%(asctime)s | %(name)s | %(module)s : %(lineno)d | %(levelname)s: %(message)s',
            'datefmt': '%Y-%d-%m %I:%M:%S',
        },
    },
    'handlers':{
        'console':{
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file':{
            'level': LOG_FILE_LEVEL,
            'formatter': 'complex',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_NAME,
            'maxBytes': LOG_SIZE,
            'backupCount': LOG_COUNT,
        }
    },
    'root':{
        'handlers' : ['console', 'file'],
        'level': LOG_LEVEL,
    },
}
