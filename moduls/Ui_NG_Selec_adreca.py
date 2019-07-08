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
        DialogConsultaAdreca.resize(273, 121)
        self.gridLayout = QtWidgets.QGridLayout(DialogConsultaAdreca)
        self.gridLayout.setObjectName("gridLayout")
        self.lVial = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lVial.setObjectName("lVial")
        self.gridLayout.addWidget(self.lVial, 0, 0, 1, 1)
        self.leVial = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leVial.setText("")
        self.leVial.setObjectName("leVial")
        self.gridLayout.addWidget(self.leVial, 0, 1, 1, 3)
        self.lNumero = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lNumero.setObjectName("lNumero")
        self.gridLayout.addWidget(self.lNumero, 1, 0, 1, 1)
        self.leNumero = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leNumero.setMaximumSize(QtCore.QSize(50, 16777215))
        self.leNumero.setText("")
        self.leNumero.setObjectName("leNumero")
        self.gridLayout.addWidget(self.leNumero, 1, 1, 1, 1)
        self.lLletra = QtWidgets.QLabel(DialogConsultaAdreca)
        self.lLletra.setObjectName("lLletra")
        self.gridLayout.addWidget(self.lLletra, 1, 2, 1, 1)
        self.leLletra = QtWidgets.QLineEdit(DialogConsultaAdreca)
        self.leLletra.setMaximumSize(QtCore.QSize(50, 16777215))
        self.leLletra.setText("")
        self.leLletra.setObjectName("leLletra")
        self.gridLayout.addWidget(self.leLletra, 1, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogConsultaAdreca)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 2)

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

