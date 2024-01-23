"""A simple program to import assets into SnipeIT"""

import sys
import logging
import logging.config

from PySide2.QtWidgets import QApplication

import settings
from ui import Window


def main():
    """Main function to load the program and get things started."""

    #let's setup logging
    logging.config.dictConfig(settings.LOGGING_CONFIG)
    logger = logging.getLogger('snipescan')
    logger.info('Snipe scan starting')
    logger.debug('Snipe URL: %s', settings.SNIPE_URL)

    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
