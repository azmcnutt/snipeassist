import sys

from PySide2.QtWidgets import QMainWindow
from PySide2 import QtGui, QtCore

from ui_snipescan import Ui_MainWindow
from snipeapi import SnipeGet
import settings
from pprint import pprint

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

        # set up form defaults
        self.checkBoxScanAssetTag.setChecked(True)
        self.checkBoxScanSerial.setChecked(True)
        self.labelScanning.setText('')
        self.lineEditScanning.setReadOnly(True)
        self.pushButtonNext.setEnabled(False)
        self.labelScanStatus.setText('')
        self.labelCompanyError.setText('')
        self.labelModelError.setText('')
        self.labelLocationError.setText('')
        self.labelStatusError.setText('')
        self.labelSupplierError.setText('')
        self.labelNameError.setVisible(False)
        self.labelPurchaseCostError.setVisible(False)
        self.labelPurchaseDateError.setVisible(False)
        self.labelOrderNumberError.setVisible(False)
        self.labelWarrantyError.setVisible(False)
        self.labelNotesError.setVisible(False)

        companies = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'companies').get_all()
        self.company_model = QtGui.QStandardItemModel()
        for company in companies:
            c = QtGui.QStandardItem(company['name'])
            c.setData(company['id'])
            self.company_model.appendRow(c)
        self.company_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxCompany.setModel(self.company_model)
        
        models = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'models').get_all()
        self.model_model = QtGui.QStandardItemModel()
        for model in models:
            m = QtGui.QStandardItem(model['name'])
            m.setData(model['id'])
            self.model_model.appendRow(m)
        self.model_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxModel.setModel(self.model_model)

    @QtCore.Slot(int)
    def on_currentIndexChanged(self, row):
        it = self.model_model.item(row)
        _id = it.data()
        name = it.text()
        print("selected name: ",name, ", id:", _id)
    
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.comboBoxModel.currentIndexChanged[int].connect(self.on_currentIndexChanged)