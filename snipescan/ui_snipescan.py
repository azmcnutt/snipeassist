# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'snipescanFrzLSp.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.action_Exit = QAction(MainWindow)
        self.action_Exit.setObjectName(u"action_Exit")
        self.action_Save = QAction(MainWindow)
        self.action_Save.setObjectName(u"action_Save")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBoxRequired = QGroupBox(self.centralwidget)
        self.groupBoxRequired.setObjectName(u"groupBoxRequired")
        self.groupBoxRequired.setGeometry(QRect(0, 0, 801, 80))
        self.labelCompany = QLabel(self.groupBoxRequired)
        self.labelCompany.setObjectName(u"labelCompany")
        self.labelCompany.setGeometry(QRect(10, 20, 71, 16))
        self.comboBoxCompany = QComboBox(self.groupBoxRequired)
        self.comboBoxCompany.setObjectName(u"comboBoxCompany")
        self.comboBoxCompany.setGeometry(QRect(20, 40, 69, 22))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addAction(self.action_Exit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
        self.action_Save.setText(QCoreApplication.translate("MainWindow", u"&Save", None))
        self.groupBoxRequired.setTitle(QCoreApplication.translate("MainWindow", u"Required Items", None))
        self.labelCompany.setText(QCoreApplication.translate("MainWindow", u"Company:", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
    # retranslateUi

