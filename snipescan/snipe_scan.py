"""A simple program to import assets into SnipeIT"""

import logging
import logging.config

import settings


def main():
    """Main function to load the program and get things started."""

    #let's setup logging
    logging.config.dictConfig(settings.LOGGING_CONFIG)
    logger = logging.getLogger('snipescan')
    logger.info('Snipe scan starting')
    logger.debug('Snipe URL: %s', settings.SNIPE_URL)

if __name__ == '__main__':
    main()
