"""A simple program to import assets into SnipeIT"""

import logging
import logging.handlers

from dotenv import load_dotenv

load_dotenv()

def main():
    """Main function to load the program and get things started."""

    #let's setup logging
    logger = logging.getLogger('snipescan')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
    '%(asctime)s | %(name)s |  %(levelname)s: %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    log_file = "snipescan.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        backupCount=30,
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info('Snipe scan starting')
    logger.debug(f'Snipe URL: {SNIPEURL}')




if __name__ == '__main__':
    main()
