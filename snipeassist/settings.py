""" Settings for use throughout the program """
import os

from dotenv import load_dotenv

# Paths
SNIPEASSIST_PATH = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file if it exists
load_dotenv()

# SnipeIT Information - Both the API Key and URL Are required.
# URL must be in the format:
# https://snipeit.example.com/api/v1/
SNIPE_URL = os.getenv('SNIPE_URL')

# for less security, the URL and Key can be entered below within single quotes.
# for high security installations, the key and URL can be passed through
# Environment Variables or using dotenv with a .env file.
API_KEY = os.getenv('API_KEY')

# Save settings on exit
SAVE_ON_EXIT = os.getenv("SAVE_ON_EXIT", 'True').lower() in ('true', '1', 't')

# Ask before quit
ASK_BEFORE_QUIT = os.getenv("ASK_BEFORE_QUIT", 'True').lower() in ('true', '1', 't')

# Sound files
SOUND_DING = SNIPEASSIST_PATH + os.getenv("SOUND_DING", '/ding.mp3')
SOUND_SUCCESS = SNIPEASSIST_PATH + os.getenv("SOUND_SUCCESS", '/success.mp3')
SOUND_WARNING = SNIPEASSIST_PATH + os.getenv("SOUND_WARNING", '/warning.mp3')

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", 'DEBUG').upper()
LOG_FILE_LEVEL = os.getenv("LOG_FILE_LEVEL", 'INFO').upper()
LOG_NAME = os.getenv("LOG_NAME", 'snipeassist.log')
LOG_SIZE = int(os.getenv("LOG_SIZE", 1024000))
LOG_COUNT = int(os.getenv("LOG_COUNT", 3))

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
