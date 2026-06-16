# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 911)
        MainWindow.setStyleSheet(u"background-color: rgb(243, 247, 255);")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setMaximumSize(QSize(16777215, 900))
        self.verticalLayout_5 = QVBoxLayout(self.centralWidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.headerFrame = QFrame(self.centralWidget)
        self.headerFrame.setObjectName(u"headerFrame")
        self.headerFrame.setMaximumSize(QSize(16777215, 250))
        self.headerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.headerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.headerFrame)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.Header = QLabel(self.headerFrame)
        self.Header.setObjectName(u"Header")
        self.Header.setMinimumSize(QSize(0, 70))
        self.Header.setMaximumSize(QSize(16777215, 70))
        self.Header.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"gridline-color: rgb(0, 0, 255);\n"
"background-color: rgb(243, 247, 255);")

        self.verticalLayout_6.addWidget(self.Header)

        self.FiltersGroup = QGroupBox(self.headerFrame)
        self.FiltersGroup.setObjectName(u"FiltersGroup")
        self.FiltersGroup.setMinimumSize(QSize(0, 100))
        self.FiltersGroup.setMaximumSize(QSize(16777215, 120))
        self.FiltersGroup.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"font: 11pt \"Segoe UI\";\n"
"background-color: rgb(243, 247, 255);\n"
"border-color: rgb(0, 0, 255);")
        self.gridLayout = QGridLayout(self.FiltersGroup)
        self.gridLayout.setObjectName(u"gridLayout")
        self.comboBox_5 = QComboBox(self.FiltersGroup)
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.setObjectName(u"comboBox_5")

        self.gridLayout.addWidget(self.comboBox_5, 1, 3, 1, 1)

        self.label_5 = QLabel(self.FiltersGroup)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"background-color: rgb(243, 247, 255);")

        self.gridLayout.addWidget(self.label_5, 0, 3, 1, 1)

        self.dateEdit = QDateEdit(self.FiltersGroup)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"")

        self.gridLayout.addWidget(self.dateEdit, 1, 0, 1, 1)

        self.dateEdit_2 = QDateEdit(self.FiltersGroup)
        self.dateEdit_2.setObjectName(u"dateEdit_2")

        self.gridLayout.addWidget(self.dateEdit_2, 1, 1, 1, 1)

        self.comboBox_2 = QComboBox(self.FiltersGroup)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.gridLayout.addWidget(self.comboBox_2, 1, 2, 1, 1)

        self.label_2 = QLabel(self.FiltersGroup)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"font: 11pt \"Segoe UI\";\n"
"background-color: rgb(243, 247, 255);")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_3 = QLabel(self.FiltersGroup)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"background-color: rgb(243, 247, 255);")

        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)

        self.label_4 = QLabel(self.FiltersGroup)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color: rgb(85, 170, 255);\n"
"background-color: rgb(243, 247, 255);")

        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)

        self.pushButton = QPushButton(self.FiltersGroup)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 2)

        self.pushButton_2 = QPushButton(self.FiltersGroup)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 2, 2, 1, 2)


        self.verticalLayout_6.addWidget(self.FiltersGroup)


        self.verticalLayout_5.addWidget(self.headerFrame)

        self.bottomFrame = QFrame(self.centralWidget)
        self.bottomFrame.setObjectName(u"bottomFrame")
        self.bottomFrame.setMaximumSize(QSize(16777215, 650))
        self.bottomFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.bottomFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.bottomFrame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mapFrame = QFrame(self.bottomFrame)
        self.mapFrame.setObjectName(u"mapFrame")
        self.mapFrame.setMinimumSize(QSize(600, 0))
        self.mapFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.mapFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.mapFrame)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.horizontalLayout.addWidget(self.mapFrame)

        self.dashboardFrame = QFrame(self.bottomFrame)
        self.dashboardFrame.setObjectName(u"dashboardFrame")
        self.dashboardFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.dashboardFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.dashboardFrame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.viaFrame = QFrame(self.dashboardFrame)
        self.viaFrame.setObjectName(u"viaFrame")
        self.viaFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.viaFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.viaFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.gridLayout_2.addWidget(self.viaFrame, 0, 0, 1, 1)

        self.provincesFrame = QFrame(self.dashboardFrame)
        self.provincesFrame.setObjectName(u"provincesFrame")
        self.provincesFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.provincesFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.provincesFrame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")

        self.gridLayout_2.addWidget(self.provincesFrame, 0, 1, 1, 1)

        self.temporalFrame = QFrame(self.dashboardFrame)
        self.temporalFrame.setObjectName(u"temporalFrame")
        self.temporalFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.temporalFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.temporalFrame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.gridLayout_2.addWidget(self.temporalFrame, 1, 0, 1, 2)


        self.horizontalLayout.addWidget(self.dashboardFrame)


        self.verticalLayout_5.addWidget(self.bottomFrame)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Header.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:700;\">Crashle</span></p><p align=\"center\"><span style=\" font-size:11pt;\">Estad\u00edstiques d'accidents de tr\u00e0nsit a Catalunya (2010-2023)</span></p></body></html>", None))
        self.FiltersGroup.setTitle(QCoreApplication.translate("MainWindow", u"Filtres", None))
        self.comboBox_5.setItemText(0, QCoreApplication.translate("MainWindow", u"Seleccionar", None))
        self.comboBox_5.setItemText(1, QCoreApplication.translate("MainWindow", u"Barcelona", None))
        self.comboBox_5.setItemText(2, QCoreApplication.translate("MainWindow", u"Girona", None))
        self.comboBox_5.setItemText(3, QCoreApplication.translate("MainWindow", u"LLeida", None))
        self.comboBox_5.setItemText(4, QCoreApplication.translate("MainWindow", u"Tarragona", None))

        self.label_5.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:700;\">Prov\u00edncia</span></p></body></html>", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", u"Seleccionar", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", u"Accident greu", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", u"Accident mortal", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:700;\">Data inici</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:700;\">Data fi</span></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:700;\">Gravetat de l'accident</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Aplicar filtres", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Netejar", None))
    # retranslateUi

