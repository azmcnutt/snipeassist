import sys

from PySide2.QtWidgets import QMainWindow

from ui_snipescan import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
    
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)