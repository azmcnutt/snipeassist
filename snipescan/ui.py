import sys
import logging
import logging.config
import copy


from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QVBoxLayout, QPushButton
from PySide6 import QtGui, QtCore, QtWidgets

from pyqtconfig import ConfigManager

from playsound3 import playsound

from ui_snipescan import Ui_MainWindow
from ui_loading import Ui_Dialog
from snipeapi import SnipeGet
import settings
# from pprint import pprint


logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class LoadingWindow(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()
        loading = LoadingWindow()
        loading.show()
        QApplication.processEvents()

        # logging.config.dictConfig(settings.LOGGING_CONFIG)
        # self.logger = logging.getLogger(__name__)

        # Set up a hack text box so I can save the Purchase Date
        self.lineEditPurchaseDate = QtWidgets.QLineEdit()
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMd'))

        # on form load, remove all tabs from the tab screen for custom fields
        self.tabWidgetCustomFields.clear()

        # create a dictionary to hold custom widgets
        self.custom_fields = {}

        # Setup object to load and save form settings
        logger.debug('Set up mappings for savings settings.  Settings will be saved to snipescan.json')
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
        self.config.add_handler('comboBoxEditCheckOutType', self.comboBoxCheckOutType)
        self.config.add_handler('comboBoxCheckoutTo', self.comboBoxCheckoutTo)

        # set up form defaults
        logger.debug('Set up defaults if settings do not exist.')
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


        self._verify_static_items()
        loading.close()
    
    def connect_signals_slots(self):
        self.action_Exit.triggered.connect(self.close)
        self.action_Save.triggered.connect(self.save_settings)
        self.dateEditPurchaseDate.dateChanged.connect(self._save_purchase_date)
        self.comboBoxCompany.currentIndexChanged[int].connect(self.company_index_changed)
        self.comboBoxModel.currentIndexChanged[int].connect(self.model_index_changed)
        self.comboBoxLocation.currentIndexChanged[int].connect(self.location_index_changed)
        self.comboBoxStatus.currentIndexChanged[int].connect(self.status_index_changed)
        self.comboBoxSupplier.currentIndexChanged[int].connect(self.supplier_index_changed)
        self.checkBoxAssetName.stateChanged.connect(self._verify_asset_name)
        self.checkBoxAppend.stateChanged.connect(self._verify_asset_name)
        self.checkBoxPurchaseDate.stateChanged.connect(self._verify_purchase_date)
        self.checkBoxOrderNumber.stateChanged.connect(self._verify_order_number)
        self.checkBoxPurchaseCost.stateChanged.connect(self._verify_purchase_cost)
        self.checkBoxWarranty.stateChanged.connect(self._verify_warranty)
        self.checkBoxNotes.stateChanged.connect(self._verify_notes)
        self.checkBoxCheckOutEnabled.stateChanged.connect(self._verify_check_out)
        self.comboBoxCheckOutType.currentIndexChanged[int].connect(self._verify_check_out)
        self.pushButtonRefresh.pressed.connect(self.refresh_comboboxes)
        self.pushButtonScan.pressed.connect(self.start_scanning)
        self.pushButtonNext.pressed.connect(self._scan_next_button)
        self.lineEditScanning.returnPressed.connect(self._scan_next_button)
        
        

    
    def refresh_comboboxes(self):
        """ Downloads information from SnipeIT API to populate the combo boxes """

        logger.info('Starting Combobox Refresh')
        companies = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'companies').get_all()
        if not companies:
            logger.critical('API Error, unable to get companies')
            sys.exit()
        logger.debug('received %s companies.  Creating company combobox model', len(companies))
        self.company_model = QtGui.QStandardItemModel()
        for company in companies:
            logger.debug('Adding id: %s for company: %s', company['id'], company['name'])
            c = QtGui.QStandardItem(company['name'])
            c.setData(company['id'])
            self.company_model.appendRow(c)
        self.company_model.sort(0, QtCore.Qt.AscendingOrder)
        logger.debug('Setting company combobox model')
        self.comboBoxCompany.setModel(self.company_model)
        logger.info('Finished refreshing the company combobox model')
        
        models = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'models').get_all()
        if not models:
            logger.critical('API Error, unable to get models')
            sys.exit()
        logger.debug('received %s models.  Creating model combobox model', len(models))
        self.model_model = QtGui.QStandardItemModel()
        for model in models:
            logger.debug('Adding id: %s for model: %s', model['id'], model['name'])
            m = QtGui.QStandardItem(model['name'])
            m.setData(model['id'])
            self.model_model.appendRow(m)
        self.model_model.sort(0, QtCore.Qt.AscendingOrder)
        logger.debug('Setting model combobox model')
        self.comboBoxModel.setModel(self.model_model)
        logger.info('Finished refreshing the model combobox model')
        
        locations = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'locations').get_all()
        if not locations:
            logger.critical('API Error, unable to get locations')
            sys.exit()
        logger.debug('received %s locations.  Creating location combobox model', len(locations))
        self.location_model = QtGui.QStandardItemModel()
        for location in locations:
            l = QtGui.QStandardItem(location['name'])
            l.setData(location['id'])
            self.location_model.appendRow(l)
        self.location_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxLocation.setModel(self.location_model)
        logger.info('Finished refreshing the location combobox model')
        
        statuses = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'statuslabels').get_all()
        if not statuses:
            logger.critical('API Error, unable to get status labels')
            sys.exit()
        logger.debug('received %s status labels.  Creating status combobox model', len(statuses))
        self.status_model = QtGui.QStandardItemModel()
        for status in statuses:
            s = QtGui.QStandardItem(status['name'])
            s.setData(status['id'])
            self.status_model.appendRow(s)
        self.status_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxStatus.setModel(self.status_model)
        logger.info('Finished refreshing the status combobox model')
        
        suppliers = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'suppliers').get_all()
        if not suppliers:
            logger.critical('API Error, unable to get suppliers')
            sys.exit()
        logger.debug('received %s suppliers.  Creating supplier combobox model', len(suppliers))
        self.supplier_model = QtGui.QStandardItemModel()
        for supplier in suppliers:
            s = QtGui.QStandardItem(supplier['name'])
            s.setData(supplier['id'])
            self.supplier_model.appendRow(s)
        self.supplier_model.sort(0, QtCore.Qt.AscendingOrder)
        self.comboBoxSupplier.setModel(self.supplier_model)
        logger.info('Finished refreshing the supplier combobox model')
        self.set_defaults()
    
    def set_defaults(self):
        logger.info('Load settings from config file')
        self.config.load()
        logger.info('Loading settings completed')
    
    def save_settings(self):
        logger.info('Save settings to config file')
        self.config.save()
        logger.info('Save settings completed')
    
    @QtCore.Slot(int)
    def company_index_changed(self, row):
        indx = self.company_model.item(row)
        _id = indx.data()
        name = indx.text()
        logger.debug('ComboboxCompany Updated: ID: %s, Name: %s', _id, name)
    
    @QtCore.Slot(int)
    def model_index_changed(self, row):
        for v in self.custom_fields.values():
            field_name = v['label'].text()
            self.config.remove_handler(field_name + '_scan')
            self.config.remove_handler(field_name + '_data')
        self.custom_fields.clear()
        self.tabWidgetCustomFields.clear()
        logger.debug(self.tabWidgetCustomFields.count())
        indx = self.model_model.item(row)
        _id = indx.data()
        name = indx.text()
        logger.debug('ComboboxModel Updated: ID: %s, Name: %s', _id, name)
        model = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'models').get_by_id(_id)
        if model['fieldset']:
            logger.debug('Custom fields found for model (%s) %s.  Setting up custom field tabs', _id, name)
            logger.debug('Fieldset id: %s', model['fieldset']['id'])
            fieldset = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'fieldsets').get_by_id(model['fieldset']['id'])
            logger.debug('Fieldset ID: %s - %s', fieldset['id'], fieldset['name'])
            for f in fieldset['fields']['rows']:
                logger.debug('Setting up Custom field %s', f['db_column_name'])
                tab = QtWidgets.QWidget()
                fieldset_tab_id = self.tabWidgetCustomFields.addTab(tab, f['name'])
                self.custom_fields[fieldset_tab_id] = {}
                self.custom_fields[fieldset_tab_id]['label'] = QtWidgets.QLabel(f['db_column_name'], tab)
                self.custom_fields[fieldset_tab_id]['label'].setGeometry(QtCore.QRect(0, 0, 300, 16))
                self.custom_fields[fieldset_tab_id]['label'].setVisible(True)
                self.custom_fields[fieldset_tab_id]['label'].setObjectName('label')
                self.custom_fields[fieldset_tab_id]['scan'] = QtWidgets.QComboBox(tab)
                self.custom_fields[fieldset_tab_id]['scan'].addItems(['Do not record', 'Fill', 'Scan'])
                self.custom_fields[fieldset_tab_id]['scan'].setGeometry(QtCore.QRect(0, 25, 300, 22))
                self.custom_fields[fieldset_tab_id]['scan'].setVisible(True)
                self.custom_fields[fieldset_tab_id]['scan'].setObjectName('scan')
                self.config.add_handler(f['db_column_name']+'_scan', self.custom_fields[fieldset_tab_id]['scan'])
                if f['field_values_array']:
                    logger.debug('Setting up a combobox for Custom field %s', f['db_column_name'])
                    self.custom_fields[fieldset_tab_id]['data'] = QtWidgets.QComboBox(tab)
                    self.custom_fields[fieldset_tab_id]['data'].addItems(f['field_values_array'])
                else:
                    logger.debug('Setting up a lineedit for Custom field %s', f['db_column_name'])
                    self.custom_fields[fieldset_tab_id]['data'] = QtWidgets.QLineEdit(tab)
                self.custom_fields[fieldset_tab_id]['data'].setGeometry(QtCore.QRect(0, 50, 300, 22))
                self.custom_fields[fieldset_tab_id]['data'].setVisible(True)
                self.custom_fields[fieldset_tab_id]['data'].setObjectName('data')
                self.config.add_handler(f['db_column_name'] + '_data', self.custom_fields[fieldset_tab_id]['data'])

                logger.debug('id: %s - name: %s - db_column: %s', f['id'], f['name'], f['db_column_name'])
                logger.debug('Choices: %s', f['field_values_array'])

    @QtCore.Slot(int)
    def location_index_changed(self, row):
        indx = self.location_model.item(row)
        _id = indx.data()
        name = indx.text()
        logger.debug('ComboboxLocation Updated: ID: %s, Name: %s', _id, name)
    
    @QtCore.Slot(int)
    def status_index_changed(self, row):
        indx = self.status_model.item(row)
        _id = indx.data()
        name = indx.text()
        logger.debug('ComboboxStatus Updated: ID: %s, Name: %s', _id, name)
    
    @QtCore.Slot(int)
    def supplier_index_changed(self, row):
        indx = self.supplier_model.item(row)
        _id = indx.data()
        name = indx.text()
        logger.debug('ComboboxSupplier Updated: ID: %s, Name: %s', _id, name)
    
    def closeEvent(self,event):
        logger.info('Main window closing')
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
                    logger.info('User Quit')
                    if hasattr(settings, 'SAVE_ON_EXIT'):
                        if settings.SAVE_ON_EXIT:
                            self.save_settings()
                    event.accept()
                else:
                    logger.info('User canceled quit')
            else:
                if hasattr(settings, 'SAVE_ON_EXIT'):
                    if settings.SAVE_ON_EXIT:
                        self.save_settings()
        else:
            if hasattr(settings, 'SAVE_ON_EXIT'):
                if settings.SAVE_ON_EXIT:
                    self.save_settings()
    
    def _save_purchase_date(self):
        logger.debug('Updating Config.PurchaseDate from Form.PurchaseDate')
        self.lineEditPurchaseDate.setText(QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyyMMdd'))
    
    def _load_purchase_date(self):
        logger.debug('Updating Form.PurchaseDate from Config.PurchaseDate')
        self.dateEditPurchaseDate.setDate(QtCore.QDate.fromString(self.lineEditPurchaseDate.text(), 'yyyyMMdd'))

    def _verify_static_items(self):
        self._verify_asset_name()
        self._verify_purchase_date()
        self._verify_order_number()
        self._verify_purchase_cost()
        self._verify_warranty()
        self._verify_notes()
    
    def _field_not_empty(self, f):
        """Returns true if a field is not empty"""
        logger.debug('Checking %s.', f.objectName())
        return bool(f.text())

    def _verify_check_out(self):
        """ If enable check out is changed or check out type is changed, update the list """
        logger.debug('Verifying Check out')
        if not self.checkBoxCheckOutEnabled.isChecked():
            # Check out is not enabled
            logger.debug('Enable Check Out not checked.  Disabled entries')
            self.comboBoxCheckOutType.setEnabled(False)
            self.comboBoxCheckoutTo.setEnabled(False)
        elif self.checkBoxCheckOutEnabled.isChecked():
            logger.debug('Enable Check out is checked.  Enable entries')
            self.comboBoxCheckOutType.setEnabled(True)
            self.comboBoxCheckoutTo.setEnabled(True)
            # Update list here
            if self.comboBoxCheckOutType.currentText() == 'User':
                self.checkout_to_refresh('users')
            elif self.comboBoxCheckOutType.currentText() == 'Asset':
                self.checkout_to_refresh('hardware')
            elif self.comboBoxCheckOutType.currentText() == 'Location':
                self.checkout_to_refresh('locations')
            else:
                self.comboBoxCheckoutTo.clear()

    def _verify_order_number(self):
        logger.debug('Verifying order_number')
        if not self.checkBoxOrderNumber.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Order Number Fill not checked.  Disabled entries')
            self.labelOrderNumberError.setVisible(False)
            self.lineEditOrderNumber.setReadOnly(True)
        elif self.checkBoxOrderNumber.isChecked():
            logger.debug('Order Number Fill is checked.  Enable entries')
            self.lineEditOrderNumber.setReadOnly(False)

    def _verify_purchase_cost(self):
        logger.debug('Verifying purchase_cost')
        if not self.checkBoxPurchaseCost.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Purchase Cost Fill not checked.  Disabled entries')
            self.labelPurchaseCostError.setVisible(False)
            self.lineEditPurchaseCost.setReadOnly(True)
        elif self.checkBoxPurchaseCost.isChecked():
            logger.debug('Purchase Cost Fill is checked.  Enable entries')
            self.lineEditPurchaseCost.setReadOnly(False)

    def _verify_warranty(self):
        logger.debug('Verifying Warranty')
        if not self.checkBoxWarranty.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Warranty Fill not checked.  Disabled entries')
            self.labelWarrantyError.setVisible(False)
            self.lineEditWarranty.setReadOnly(True)
        elif self.checkBoxWarranty.isChecked():
            logger.debug('Warranty Fill is checked.  Enable entries')
            self.lineEditWarranty.setReadOnly(False)

    def _verify_notes(self):
        logger.debug('Verifying notes')
        if not self.checkBoxNotes.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Notes Fill not checked.  Disabled entries')
            self.labelNotesError.setVisible(False)
            self.lineEditNotes.setReadOnly(True)
        elif self.checkBoxNotes.isChecked():
            logger.debug('Notes Fill is checked.  Enable entries')
            self.lineEditNotes.setReadOnly(False)

    def _verify_purchase_date(self):
        logger.debug('Verifying Purchase Date')
        if not self.checkBoxPurchaseDate.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Purchase Date Fill not checked.  Disabled entries')
            self.labelPurchaseDateError.setVisible(False)
            self.dateEditPurchaseDate.setReadOnly(True)
        elif self.checkBoxPurchaseDate.isChecked():
            logger.debug('Purchase Date Fill is checked.  Enable entries')
            self.dateEditPurchaseDate.setReadOnly(False)

    def _verify_asset_name(self):
        logger.debug('Verifying Asset Name')
        if not self.checkBoxAssetName.isChecked():
            # we are not filling Asset name or appending
            # clear any error and disable the text boxes
            logger.debug('Asset Fill not checked.  Disabled entries')
            self.labelNameError.setVisible(False)
            self.lineEditAssetName.setReadOnly(True)
            self.lineEditAssetNameAppend.setReadOnly(True)
            self.checkBoxAppend.setEnabled(False)
        elif self.checkBoxAssetName.isChecked():
            logger.debug('Asset Fill checked.  Enable entries')
            self.lineEditAssetName.setReadOnly(False)
            self.checkBoxAppend.setEnabled(True)
            if self.checkBoxAppend.isChecked():
                logger.debug('Append checked.')
                self.lineEditAssetNameAppend.setReadOnly(False)
            else:
                logger.debug('Append not checked.')
                self.lineEditAssetNameAppend.setReadOnly(True)
        logger.debug('Completed verifying Asset Name')

    def checkout_to_refresh(self, checkout_type):
        if checkout_type not in ['hardware', 'users', 'locations']:
            logger.error('Invalid checkout_type.  Received: %s, expected: hardware, users, or location', checkout_type)
        chkout_list = SnipeGet(settings.SNIPE_URL, settings.API_KEY, checkout_type).get_all()
        if not chkout_list:
            logger.critical('API Error, unable to get check out list')
            sys.exit()
        logger.debug('received %s %s.  Populating checkout model', len(chkout_list), checkout_type)
        self.checkout_model = QtGui.QStandardItemModel()
        for chkout_to in chkout_list:
            id = chkout_to['id']
            name = chkout_to['name']
            if checkout_type == 'users':
                name = chkout_to['username']
            logger.debug('Adding id: %s for checkout to: %s', id, name)
            c = QtGui.QStandardItem(name)
            c.setData(id)
            self.checkout_model.appendRow(c)
        self.checkout_model.sort(0, QtCore.Qt.AscendingOrder)
        logger.debug('Setting checkout combobox model')
        self.comboBoxCheckoutTo.setModel(self.checkout_model)
        logger.info('Finished refreshing the checkout combobox model')
    
    def _set_items_read_only(self):
        logger.debug('Setting items to read only')
        items = self.groupBoxRequired.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxStatic.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxStatic.findChildren(QtWidgets.QLineEdit)
        items += self.groupBoxStatic.findChildren(QtWidgets.QDateEdit)
        items += self.groupBoxScannable.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxCheckout.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxCheckout.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxCustom.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxCustom.findChildren(QtWidgets.QLineEdit)
        for item in items:
            logger.debug('%s deactivated', item.objectName())
            item.setEnabled(False)

    def _set_items_read_write(self):
        logger.debug('Setting items to read write')
        items = self.groupBoxRequired.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxStatic.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxStatic.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxStatic.findChildren(QtWidgets.QLineEdit)
        items += self.groupBoxStatic.findChildren(QtWidgets.QDateEdit)
        items += self.groupBoxScannable.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxCheckout.findChildren(QtWidgets.QCheckBox)
        items += self.groupBoxCheckout.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxCustom.findChildren(QtWidgets.QComboBox)
        items += self.groupBoxCustom.findChildren(QtWidgets.QLineEdit)
        for item in items:
            logger.debug('%s activated', item.objectName())
            item.setEnabled(True)
        self._verify_static_items()
    
    def _sanity_checks_passed(self) -> bool:
        checks = True
        if self.checkBoxAssetName.isChecked():
            if not self.lineEditAssetName.text():
                self.labelNameError.setVisible(True)
                checks = False
            else:
                self.labelNameError.setVisible(False)
        if (self.checkBoxAssetName.isChecked()
            and self.checkBoxAppend.isChecked()
            and self.lineEditAssetName.text()):
            if (not self.lineEditAssetNameAppend.text()
                or not self.lineEditAssetNameAppend.text().isnumeric()
            ):
                self.labelNameError.setVisible(True)
                checks = False
            else:
                self.labelNameError.setVisible(False)
        if self.checkBoxPurchaseDate.isChecked():
            if not self.dateEditPurchaseDate.text():
                self.labelPurchaseDateError.setVisible(True)
                checks = False
            else:
                self.labelPurchaseDateError.setVisible(False)
        if self.checkBoxOrderNumber.isChecked():
            if not self.lineEditOrderNumber.text():
                self.labelOrderNumberError.setVisible(True)
                checks = False
            else:
                self.labelOrderNumberError.setVisible(False)
        if self.checkBoxPurchaseCost.isChecked():
            if (not self.lineEditPurchaseCost.text()
                or not self._is_float(self.lineEditPurchaseCost.text())
            ):
                self.labelPurchaseCostError.setVisible(True)
                checks = False
            else:
                self.labelPurchaseCostError.setVisible(False)
        if self.checkBoxWarranty.isChecked():
            if (not self.lineEditWarranty.text()
                or not self.lineEditWarranty.text().isnumeric()
            ):
                self.labelWarrantyError.setVisible(True)
                checks = False
            else:
                self.labelWarrantyError.setVisible(False)
        if self.checkBoxNotes.isChecked():
            if not self.lineEditNotes.text():
                self.labelNotesError.setVisible(True)
                checks = False
            else:
                self.labelNotesError.setVisible(False)

        return checks
        
    def _is_float(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False
        
    def start_scanning(self):
        logger.debug('Scan button pressed')
        if not self._sanity_checks_passed():
            return
        if self.pushButtonScan.text() == 'Start\nScanning':
            logger.debug('Action: start scanning')
            self.pushButtonScan.setText('Stop\nScanning')
            self._set_items_read_only()
            
            # create the master asset with the default-values
            self._master_asset = {}
            self._master_asset['company_id'] = self.company_model.item(self.comboBoxCompany.currentIndex()).data()
            self._master_asset['model_id'] = self.model_model.item(self.comboBoxModel.currentIndex()).data()
            self._master_asset['location_id'] = self.location_model.item(self.comboBoxLocation.currentIndex()).data()
            self._master_asset['rtd_location_id'] = self.location_model.item(self.comboBoxLocation.currentIndex()).data()
            self._master_asset['status_id'] = self.status_model.item(self.comboBoxStatus.currentIndex()).data()
            self._master_asset['supplier_id'] = self.supplier_model.item(self.comboBoxSupplier.currentIndex()).data()
            if self.checkBoxAssetName.isChecked():
                self._master_asset['name'] = self.lineEditAssetName.text()
                # if self.checkBoxAppend.isChecked():
                #     self._master_asset['name_append'] = self.lineEditAssetNameAppend.text()
            if self.checkBoxPurchaseDate.isChecked():
                self._master_asset['purchase_date'] = QtCore.QDate(self.dateEditPurchaseDate.date()).toString('yyyy-MM-dd')
            if self.checkBoxOrderNumber.isChecked():
                self._master_asset['order_number'] = self.lineEditOrderNumber.text()
            if self.checkBoxPurchaseCost.isChecked():
                self._master_asset['purchase_cost'] = self.lineEditPurchaseCost.text()
            if self.checkBoxWarranty.isChecked():
                self._master_asset['warranty'] = self.lineEditWarranty.text()
            if self.checkBoxNotes.isChecked():
                self._master_asset['notes'] = self.lineEditNotes.text()
            if self.checkBoxScanAssetTag.isChecked():
                self._master_asset['asset_tag'] = '{{SCAN}}'
            if self.checkBoxScanSerial.isChecked():
                self._master_asset['serial'] = '{{SCAN}}'
            for i in range(self.tabWidgetCustomFields.count()):
                # name, label, scan, data
                # self.custom_fields[fieldset_tab_id]['label'] = QtWidgets.QLabel(f['db_column_name'], tab)
                # self.tab_widget.widget(tab_index)
                tab = self.tabWidgetCustomFields.widget(i)
                if tab:
                    label = tab.findChild(QtWidgets.QLabel, 'label').text()
                    scan = tab.findChild(QtWidgets.QComboBox, 'scan').currentText()
                    # 'Do not record', 'Fill', 'Scan'
                    if scan == 'Scan':
                        self._master_asset[label] = '{{SCAN}}'
                        logger.debug('Custom Field: %s - set to scan', self.tabWidgetCustomFields.tabText(i))
                    elif scan == 'Fill':
                        if tab.findChild(QtWidgets.QComboBox, 'data'):
                            self._master_asset[label] = tab.findChild(QtWidgets.QComboBox, 'data').currentText()
                            logger.debug('Custom Field: %s - set to fill with %s', 
                                         self.tabWidgetCustomFields.tabText(i),
                                         self._master_asset[label]
                            )
                        elif tab.findChild(QtWidgets.QLineEdit, 'data'):
                            self._master_asset[label] = tab.findChild(QtWidgets.QLineEdit, 'data').text()
                            logger.debug('Custom Field: %s - set to fill with %s', 
                                         self.tabWidgetCustomFields.tabText(i),
                                         self._master_asset[label]
                            )
                        else:
                            logger.warning('Unable to determine data for custom field %s', self.tabWidgetCustomFields.tabText(i))
            logger.debug(self._master_asset)
            if '{{SCAN}}' not in self._master_asset.values():
                self.labelScanning.setText('Nothing to Scan.  Nothing to do.')
                self.lineEditScanning.setReadOnly(True)
                self.pushButtonNext.setEnabled(False)
                return
            self.create_asset = SnipeGet(settings.SNIPE_URL, settings.API_KEY, 'hardware')
            self._scanning_asset = copy.deepcopy(self._master_asset)

            # Enable scanning items
            self.lineEditScanning.setReadOnly(False)
            self.pushButtonNext.setEnabled(True)
            # self.pushButtonNext.setDefault(True)
            self._scan_next_button()
        else:
            logger.debug('Action: end scanning')
            self.pushButtonScan.setText('Start\nScanning')
            self._set_items_read_write()
            
            # Disable scanning items
            self.lineEditScanning.setText('')
            self.labelScanning.setText('')
            self.labelScanStatus.setText('')
            self.lineEditScanning.setReadOnly(True)
            self.pushButtonNext.setEnabled(False)

    def _scan_next_button(self):
        if self.lineEditScanning.text():
            self._scanning_asset[self.labelScanning.text()] = self.lineEditScanning.text()
            self.lineEditScanning.setText('')
            self.labelScanStatus.setText('Data Accepted')
            playsound(settings.SOUND_DING, block=False)
        if '{{SCAN}}' in self._scanning_asset.values():
            for key, val in self._scanning_asset.items():
                if val == '{{SCAN}}':
                    self.labelScanning.setText(key)
                    self.lineEditScanning.setFocus()
                    break
        else:
            # create asset
            if self.checkBoxAppend.isChecked() and self.checkBoxAssetName.isChecked():
                logger.debug(self._scanning_asset['name'] + self.lineEditAssetNameAppend.text())
                self._scanning_asset['name'] += self.lineEditAssetNameAppend.text()
            logger.debug(self._scanning_asset)
            _created_asset = self.create_asset.create_asset(self._scanning_asset)
            if _created_asset['messages'] == 'Asset created successfully. :)':
                logger.info(f'Asset Create.  Snipe ID: {_created_asset["payload"]["id"]}')
                self.labelScanStatus.setText(f'Asset Created: {_created_asset["payload"]["id"]}')
                if self.checkBoxAppend.isChecked():
                    # self.lineEditAssetNameAppend.setEnabled(True)
                    self.lineEditAssetNameAppend.setText(str(int('9' + self.lineEditAssetNameAppend.text()) + 1)[1:])
                    # self.lineEditAssetNameAppend.setEnabled(False)
                if settings.SAVE_ON_EXIT:
                    self.save_settings()
                if self.checkBoxCheckOutEnabled.isChecked():
                    logger.debug(f'Check out is checked, Checking out SNIPE ID: {_created_asset["payload"]["id"]}')
                    _checkedout_asset = self.create_asset.checkout_asset(
                        _created_asset["payload"]["id"],
                        self.comboBoxCheckOutType.currentText(),
                        self.checkout_model.item(self.comboBoxCheckoutTo.currentIndex()).data(),
                    )
                    if _checkedout_asset['messages'] == 'Asset checked out successfully.':
                        logger.info(f'Asset Checked out.  Asset Snipe ID: {_created_asset["payload"]["id"]}, Checkout ID: {_checkedout_asset["payload"]["asset"]}')
                        self.labelScanStatus.setText(f'Asset Checked Out: {_created_asset["payload"]["id"]} - {_checkedout_asset["payload"]["asset"]}')
                        playsound(settings.SOUND_SUCCESS, block=False)
                    else:
                        logger.warning(f'Asset created, but not checked out: {_checkedout_asset["messages"]}')
                        self.labelScanStatus.setText(f'Asset Created, check out fail: {_created_asset["payload"]["id"]}')
                        playsound(settings.SOUND_WARNING, block=False)
                else:
                    self.labelScanStatus.setText(f'Asset Created: {_created_asset["payload"]["id"]}')
                    playsound(settings.SOUND_SUCCESS, block=False)
            else:
                logger.warning(f'Asset not created: {_created_asset["messages"]}')
                self.labelScanStatus.setText(f'Asset Not Created')
                playsound(settings.SOUND_WARNING, block=False)
            self._scanning_asset = copy.deepcopy(self._master_asset)
            self._scan_next_button()

