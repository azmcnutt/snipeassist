import sys
import logging

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6 import QtGui, QtCore, QtWidgets
from pyqtconfig import ConfigManager, HOOKS

from ui_snipescan import Ui_MainWindow
from ui_loading import Ui_Dialog
from snipeapi import SnipeGet
import settings
from pprint import pprint

class LoadingWindow(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        loading = LoadingWindow()
        loading.show()
        QApplication.processEvents()

        logging.config.dictConfig(settings.LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)

        # Set up a hack text box so I can save the Purchase Date
        self.lineEditPurchaseDate = QtWidgets.QLineEdit()
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMd'))

        # setup another hack text box so I can save the check out to radio button
        self.lineEditCheckOutType = QtWidgets.QLineEdit()


        # Setup object to load and save form settings
        self.config = ConfigManager(filename="snipescan.json")
        self.config.add_handler('comboBoxCompany', self.comboBoxCompany)
        self.config.add_handler('comboBoxModel', self.comboBoxModel)
        self.config.add_handler('comboBoxLocation', self.comboBoxLocation)
        self.config.add_handler('comboBoxStatus', self.comboBoxStatus)
        self.config.add_handler('comboBoxSupplier', self.comboBoxSupplier)
        self.config.add_handler('checkBoxAssetName', self.checkBoxAssetName)
        self.config.add_handler('checkBoxPurchaseDate', self.checkBoxPurchaseDate)
        self.config.add_handler('checkBoxOrderNumber', self.checkBoxOrderNumber)
        self.config.add_handler('checkBoxPurchaseCost', self.checkBoxPurchaseCost)
        self.config.add_handler('checkBoxWarranty', self.checkBoxWarranty)
        self.config.add_handler('checkBoxNotes', self.checkBoxNotes)
        self.config.add_handler('lineEditAssetName', self.lineEditAssetName)
        self.config.add_handler('checkBoxAppend', self.checkBoxAppend)
        self.config.add_handler('lineEditAssetNameAppend', self.lineEditAssetNameAppend)
        self.config.add_handler('lineEditPurchaseDate', self.lineEditPurchaseDate)
        self._load_purchase_date()
        self.config.add_handler('lineEditOrderNumber', self.lineEditOrderNumber)
        self.config.add_handler('lineEditPurchaseCost', self.lineEditPurchaseCost)
        self.config.add_handler('lineEditWarranty', self.lineEditWarranty)
        self.config.add_handler('lineEditNotes', self.lineEditNotes)
        self.config.add_handler('checkBoxScanAssetTag', self.checkBoxScanAssetTag)
        self.config.add_handler('checkBoxScanSerial', self.checkBoxScanSerial)
        self.config.add_handler('checkBoxCheckOutEnabled', self.checkBoxCheckOutEnabled)
        # self.config.add_handler('radioButtonCheckoutUser', self.radioButtonCheckoutUser)
        # self.config.add_handler('radioButtonCheckoutAsset', self.radioButtonCheckoutAsset)
        # self.config.add_handler('radioButtonCheckoutLocation', self.radioButtonCheckoutLocation)
        self.config.add_handler('lineEditCheckOutType', self.lineEditCheckOutType)
        self.config.add_handler('comboBoxCheckoutTo', self.comboBoxCheckoutTo)

        # set up form defaults
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
        loading.close()
    
    def connectSignalsSlots(self):
        self.action_Exit.triggered.connect(self.close)
        self.action_Save.triggered.connect(self.save_settings)
        self.dateEditPurchaseDate.dateChanged.connect(self._save_purchase_date)
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
        self.logger.info('Load settings from config file')
        self.config.load()
        if self.lineEditCheckOutType.text() == 'user':
            self.radioButtonCheckoutUser.setChecked(True)
        elif self.lineEditCheckOutType.text() == 'asset':
            self.radioButtonCheckoutAsset.setChecked(True)
        elif self.lineEditCheckOutType.text() == 'location':
            self.radioButtonCheckoutLocation.setChecked(True)
        self.logger.info('Loading settings completed')
    
    def save_settings(self):
        self.logger.info('Save settings to config file')
        if self.radioButtonCheckoutUser.isChecked():
            self.lineEditCheckOutType.setText('user')
        elif self.radioButtonCheckoutAsset.isChecked():
            self.lineEditCheckOutType.setText('asset')
        elif self.radioButtonCheckoutLocation.isChecked():
            self.lineEditCheckOutType.setText('location')
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
        model = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'models').get_by_id(_id)
        if model['fieldset']:
            self.logger.debug('Fieldset id: %s', model['fieldset']['id'])
            fieldset = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'fieldsets').get_by_id(model['fieldset']['id'])
            self.logger.debug('Fieldset ID: %s - %s', fieldset['id'], fieldset['name'])
            for f in fieldset['fields']['rows']:
                self.logger.debug('id: %s - name: %s - db_column: %s', f['id'], f['name'], f['db_column_name'])
                self.logger.debug('Choices: %s', f['field_values_array'])


    
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
    
    def _save_purchase_date(self):
        self.logger.debug('Updating Config.PurchaseDate from Form.PurchaseDate')
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMMdd'))
    
    def _load_purchase_date(self):
        self.logger.debug('Updating Form.PurchaseDate from Config.PurchaseDate')
        self.dateEditPurchaseDate.setDate(QtCore.QDate.fromString(self.lineEditPurchaseDate.text(), 'yyyyMMdd'))
