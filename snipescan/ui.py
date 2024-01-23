import sys

from PyQt6.QtWidgets import QMainWindow

from ui_snipescan import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
    
    def connectSignalsSlots(self):
        self.actione_Xit.triggered.connect(self.close)