"""A simple program to import assets into SnipeIT"""

import sys
import logging
import logging.config

from PySide6.QtWidgets import QApplication

import settings
from snipeapi import SnipeGet
from ui import Window


def main():
    """Main function to load the program and get things started."""
    #let's setup logging
    logging.config.dictConfig(settings.LOGGING_CONFIG)
    logger = logging.getLogger('snipeassist')
    logger.info('***************************************')
    logger.info('          Snipe Assist starting')
    logger.info('***************************************')
    logger.debug('Snipe URL:            %s', settings.SNIPE_URL)
    logger.debug('API Key:              [Hidden for security]')
    logger.debug('Save on exit:         %s', settings.SAVE_ON_EXIT)
    logger.debug('Ask before quit:      %s', settings.ASK_BEFORE_QUIT)
    logger.debug('Sound Ding:           %s', settings.SOUND_DING)
    logger.debug('Sound Success:        %s', settings.SOUND_SUCCESS)
    logger.debug('Sound Warning:        %s', settings.SOUND_WARNING)
    logger.debug('Log Level Console:    %s', settings.LOG_LEVEL)
    logger.debug('Log Level File:       %s', settings.LOG_FILE_LEVEL)
    logger.debug('Log File Name:        %s', settings.LOG_NAME)
    logger.debug('Log File Size:        %s', settings.LOG_SIZE)
    logger.debug('Log File Count:       %s', settings.LOG_COUNT)

    # Test connectivity to the Snipe server.  For a properly configured
    # Snipe deployment there should be at least one user returned.  If
    # 0 or None is returned, then exit the program with an error.

    if SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'users').count():
        logger.info('Successfully connected to the Snipe Server')
    else:
        logger.critical('No connection to the Snipe Server.')
        logger.critical(settings.SNIPE_URL)
        sys.exit()

    
    # Launch the UI
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec()


if __name__ == '__main__':
    main()
