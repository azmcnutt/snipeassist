import sys
import logging

from PySide6.QtWidgets import QMainWindow
from PySide6 import QtGui, QtCore

from ui_snipescan import Ui_MainWindow
from snipeapi import SnipeGet
import settings
from pprint import pprint

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

        logging.config.dictConfig(settings.LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)

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

        self.refresh_comboboxes()

    @QtCore.Slot(int)
    def on_currentIndexChanged(self, row):
        it = self.model_model.item(row)
        _id = it.data()
        name = it.text()
        self.logger.debug('ComboboxModel Updated: ID: %s, Name: %s',_id, name)
    
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.comboBoxModel.currentIndexChanged[int].connect(self.on_currentIndexChanged)
    
    def refresh_comboboxes(self):
        self.logger.info('Starting Combobox Refresh')
        companies = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'companies').get_all()
        if not companies:
            self.logger.critical('API Error, unable to get companies')
            sys.exit()
        self.logger.debug('received %s companies.  Creating company combobox model', len(companies))
        self.company_model = QtGui.QStandardItemModel()
        for company in companies:
            self.logger.debug('Adding id: %s for company: %s', company['id'], company['name'])
            c = QtGui.QStandardItem(company['name'])
            c.setData(company['id'])
            self.company_model.appendRow(c)
        self.company_model.sort(0, QtCore.Qt.AscendingOrder)
        self.logger.debug('Setting company combobox model')
        self.comboBoxCompany.setModel(self.company_model)
        self.logger.info('Finished refreshing the company combobox model')
        
        models = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'models').get_all()
        if not models:
            self.logger.critical('API Error, unable to get models')
            sys.exit()
        self.logger.debug('received %s models.  Creating model combobox model', len(models))
        self.model_model = QtGui.QStandardItemModel()
        for model in models:
            self.logger.debug('Adding id: %s for model: %s', model['id'], model['name'])
            m = QtGui.QStandardItem(model['name'])
            m.setData(model['id'])
            self.model_model.appendRow(m)
        self.model_model.sort(0, QtCore.Qt.AscendingOrder)
        self.logger.debug('Setting model combobox model')
        self.comboBoxModel.setModel(self.model_model)
        self.logger.info('Finished refreshing the model combobox model')
        
        locations = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'locations').get_all()
        if not locations:
            self.logger.critical('API Error, unable to get locations')
            sys.exit()
        self.logger.debug('received %s locations.  Creating location combobox model', len(locations))
        self.location_model = QtGui.QStandardItemModel()
        for location in locations:
            l = QtGui.QStandardItem(location['name'])
            l.setData(location['id'])
            self.location_model.appendRow(l)
        self.location_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxLocation.setModel(self.location_model)
        
        statuses = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'statuslabels').get_all()
        if not statuses:
            self.logger.critical('API Error, unable to get status labels')
            sys.exit()
        self.logger.debug('received %s status labels.  Creating status combobox model', len(statuses))
        self.status_model = QtGui.QStandardItemModel()
        for status in statuses:
            s = QtGui.QStandardItem(status['name'])
            s.setData(status['id'])
            self.status_model.appendRow(s)
        self.status_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxStatus.setModel(self.status_model)
        
        suppliers = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'suppliers').get_all()
        if not suppliers:
            self.logger.critical('API Error, unable to get suppliers')
            sys.exit()
        self.logger.debug('received %s suppliers.  Creating supplier combobox model', len(suppliers))
        self.supplier_model = QtGui.QStandardItemModel()
        for supplier in suppliers:
            s = QtGui.QStandardItem(supplier['name'])
            s.setData(supplier['id'])
            self.supplier_model.appendRow(s)
        self.supplier_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxSupplier.setModel(self.supplier_model)
