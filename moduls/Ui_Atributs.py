# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\qVista\Codi\moduls\Atributs.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(567, 483)
        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setGeometry(QtCore.QRect(10, 10, 551, 411))
        self.stackedWidget.setObjectName("stackedWidget")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(10, 420, 551, 61))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.bPrev = QtWidgets.QPushButton(self.frame)
        self.bPrev.setGeometry(QtCore.QRect(20, 20, 91, 23))
        self.bPrev.setObjectName("bPrev")
        self.bNext = QtWidgets.QPushButton(self.frame)
        self.bNext.setGeometry(QtCore.QRect(120, 20, 91, 23))
        self.bNext.setObjectName("bNext")
        self.bOK = QtWidgets.QPushButton(self.frame)
        self.bOK.setGeometry(QtCore.QRect(440, 20, 91, 23))
        self.bOK.setAutoDefault(True)
        self.bOK.setDefault(True)
        self.bOK.setObjectName("bOK")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.bPrev.setText(_translate("Dialog", "Anterior"))
        self.bNext.setText(_translate("Dialog", "Següent"))
        self.bOK.setText(_translate("Dialog", "Tornar"))

