import sys
import logging

from PySide6.QtWidgets import QMainWindow
from PySide6 import QtGui, QtCore, QtWidgets
from pyqtconfig import ConfigManager, HOOKS

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

        # Set up a hack text box so I can save the Purchase Date
        self.lineEditPurchaseDate = QtWidgets.QLineEdit()
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMd'))

        # Setup object to load and save form settings
        self.config = ConfigManager(filename="snipescan.json")
        self.config.add_handler('lineEditAssetName', self.lineEditAssetName)
        self.config.add_handler('lineEditPurchaseDate', self.lineEditPurchaseDate)

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
        self.set_defaults()
    
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.action_Save.triggered.connect(self.save_settings)
        self.dateEditPurchaseDate.dateChanged.connect(self._save_date)
        self.comboBoxCompany.currentIndexChanged[int].connect(self.company_index_changed)
        self.comboBoxModel.currentIndexChanged[int].connect(self.model_index_changed)
        self.comboBoxLocation.currentIndexChanged[int].connect(self.location_index_changed)
        self.comboBoxStatus.currentIndexChanged[int].connect(self.status_index_changed)
        self.comboBoxSupplier.currentIndexChanged[int].connect(self.supplier_index_changed)
    
    def refresh_comboboxes(self):
        """ Downloads information from SnipeIT API to populate the combo boxes """

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
        self.logger.info('Finished refreshing the location combobox model')
        
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
        self.logger.info('Finished refreshing the status combobox model')
        
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
        self.logger.info('Finished refreshing the supplier combobox model')
    
    def set_defaults(self):
        self.logger.info('Setting ComboBoxes to setting defaults')
        if hasattr(settings, 'DEFAULT_COMPANY'):
            self.logger.debug('Found Default Company: %s', settings.DEFAULT_COMPANY)
            self.comboBoxCompany.setCurrentText(settings.DEFAULT_COMPANY)
        if hasattr(settings, 'DEFAULT_MODEL'):
            self.logger.debug('Found Default Model: %s', settings.DEFAULT_MODEL)
            self.comboBoxModel.setCurrentText(settings.DEFAULT_MODEL)
        if hasattr(settings, 'DEFAULT_LOCATION'):
            self.logger.debug('Found Default Location: %s', settings.DEFAULT_LOCATION)
            self.comboBoxLocation.setCurrentText(settings.DEFAULT_LOCATION)
        if hasattr(settings, 'DEFAULT_STATUS'):
            self.logger.debug('Found Default Status: %s', settings.DEFAULT_STATUS)
            self.comboBoxStatus.setCurrentText(settings.DEFAULT_STATUS)
        if hasattr(settings, 'DEFAULT_SUPPLIER'):
            self.logger.debug('Found Default Supplier: %s', settings.DEFAULT_SUPPLIER)
            self.comboBoxSupplier.setCurrentText(settings.DEFAULT_SUPPLIER)
        self.logger.info('Finished setting ComboBoxes to setting defaults')
        self.logger.info('Load settings from config file')
        self.config.load()
        self.logger.info('Loading settings completed')
    
    def save_settings(self):
        self.logger.info('Save settings to config file')
        self.config.save()
        self.logger.info('Save settings completed')
    
    @QtCore.Slot(int)
    def company_index_changed(self, row):
        indx = self.company_model.item(row)
        _id = indx.data()
        name = indx.text()
        self.logger.debug('ComboboxCompany Updated: ID: %s, Name: %s',_id, name)
    
    @QtCore.Slot(int)
    def model_index_changed(self, row):
        indx = self.model_model.item(row)
        _id = indx.data()
        name = indx.text()
        self.logger.debug('ComboboxModel Updated: ID: %s, Name: %s',_id, name)
    
    @QtCore.Slot(int)
    def location_index_changed(self, row):
        indx = self.location_model.item(row)
        _id = indx.data()
        name = indx.text()
        self.logger.debug('ComboboxLocation Updated: ID: %s, Name: %s',_id, name)
    
    @QtCore.Slot(int)
    def status_index_changed(self, row):
        indx = self.status_model.item(row)
        _id = indx.data()
        name = indx.text()
        self.logger.debug('ComboboxStatus Updated: ID: %s, Name: %s',_id, name)
    
    @QtCore.Slot(int)
    def supplier_index_changed(self, row):
        indx = self.supplier_model.item(row)
        _id = indx.data()
        name = indx.text()
        self.logger.debug('ComboboxSupplier Updated: ID: %s, Name: %s',_id, name)
    
    def closeEvent(self,event):
        self.logger.info('Main window closing')
        if hasattr(settings, 'ASK_BEFORE_QUIT'):
            if settings.ASK_BEFORE_QUIT:
                result = QtWidgets.QMessageBox.question(
                    self,
                    "Confirm Exit...",
                    "Are you sure you want to exit ?",
                    QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No
                )
                event.ignore()
                if result == QtWidgets.QMessageBox.Yes:
                    self.logger.info('User Quit')
                    if hasattr(settings, 'SAVE_ON_EXIT'):
                        if settings.SAVE_ON_EXIT:
                            self.save_settings()
                    event.accept()
                else:
                    self.logger.info('User canceled quit')
            else:
                if hasattr(settings, 'SAVE_ON_EXIT'):
                    if settings.SAVE_ON_EXIT:
                        self.save_settings()
        else:
            if hasattr(settings, 'SAVE_ON_EXIT'):
                if settings.SAVE_ON_EXIT:
                    self.save_settings()
    
    def _save_date(self):
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMd'))
    
    def _load_date(self):
        self.dateEditPurchaseDate.setDate(QtCore.QDate.fromString(self.lineEditPurchaseDate.text(), 'yyyyMd'))
