# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\qVista\Codi\moduls\NG_Selec_adreca.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogConsultaAdreca(object):
    def setupUi(self, DialogConsultaAdreca):
        DialogConsultaAdreca.setObjectName("DialogConsultaAdreca")
        DialogConsultaAdreca.resize(426, 104)
        self.lVial = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lVial.setGeometry(QtCore.QRect(9, 11, 16, 16))
        self.lVial.setObjectName("lVial")
        self.leVial = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leVial.setGeometry(QtCore.QRect(62, 11, 351, 20))
        self.leVial.setText("")
        self.leVial.setObjectName("leVial")
        self.lNumero = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lNumero.setGeometry(QtCore.QRect(9, 39, 37, 16))
        self.lNumero.setObjectName("lNumero")
        self.lLletra = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lLletra.setGeometry(QtCore.QRect(330, 40, 27, 16))
        self.lLletra.setObjectName("lLletra")
        self.leLletra = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leLletra.setGeometry(QtCore.QRect(360, 40, 50, 20))
        self.leLletra.setMaximumSize(QtCore.QSize(50, 16777215))
        self.leLletra.setText("")
        self.leLletra.setObjectName("leLletra")
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogConsultaAdreca)
        self.buttonBox.setGeometry(QtCore.QRect(260, 70, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.leNumero = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leNumero.setGeometry(QtCore.QRect(60, 40, 50, 20))
        self.leNumero.setMaximumSize(QtCore.QSize(50, 16777215))
        self.leNumero.setText("")
        self.leNumero.setObjectName("leNumero")

        self.retranslateUi(DialogConsultaAdreca)
        self.buttonBox.accepted.connect(DialogConsultaAdreca.accept)
        self.buttonBox.rejected.connect(DialogConsultaAdreca.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogConsultaAdreca)

    def retranslateUi(self, DialogConsultaAdreca):
        _translate = QtCore.QCoreApplication.translate
        DialogConsultaAdreca.setWindowTitle(_translate("DialogConsultaAdreca", "Consulta. Selecció d\'adreça"))
        self.lVial.setText(_translate("DialogConsultaAdreca", "Vial"))
        self.lNumero.setText(_translate("DialogConsultaAdreca", "Numero"))
        self.lLletra.setText(_translate("DialogConsultaAdreca", "Lletra"))

