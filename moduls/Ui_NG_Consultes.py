# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\projectes_py\novageo\NG_Consultes.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(277, 500)
        Form.setMaximumSize(QtCore.QSize(16777215, 500))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_10 = QtWidgets.QPushButton(Form)
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout.addWidget(self.pushButton_10, 0, 0, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(Form)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout.addWidget(self.pushButton_7, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setEnabled(False)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(Form)
        self.pushButton_6.setEnabled(False)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout.addWidget(self.pushButton_6, 3, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 4, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 5, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setEnabled(False)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 6, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 7, 0, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(Form)
        self.pushButton_8.setEnabled(False)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout.addWidget(self.pushButton_8, 8, 0, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(Form)
        self.pushButton_9.setEnabled(False)
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout.addWidget(self.pushButton_9, 9, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Consultes"))
        self.pushButton_10.setText(_translate("Form", "Adreces"))
        self.pushButton_7.setText(_translate("Form", "Vials"))
        self.pushButton.setText(_translate("Form", "Explorar una illa o solar"))
        self.pushButton_6.setText(_translate("Form", "Variants"))
        self.pushButton_2.setText(_translate("Form", " Domi  ci lis"))
        self.pushButton_3.setText(_translate("Form", "Entitats"))
        self.pushButton_4.setText(_translate("Form", "Punts quilomètrics"))
        self.pushButton_5.setText(_translate("Form", "Accessos a rondes"))
        self.pushButton_8.setText(_translate("Form", "Adreces tipus illa"))
        self.pushButton_9.setText(_translate("Form", "Illes"))

