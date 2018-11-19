# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calculadora.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Calculadora(object):
    def setupUi(self, Calculadora):
        Calculadora.setObjectName("Calculadora")
        Calculadora.resize(666, 170)
        Calculadora.setMinimumSize(QtCore.QSize(0, 170))
        Calculadora.setMaximumSize(QtCore.QSize(16777215, 170))
        self.gridLayout = QtWidgets.QGridLayout(Calculadora)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(Calculadora)
        self.groupBox.setMinimumSize(QtCore.QSize(500, 150))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.bFieldsCalculadora = QtWidgets.QPushButton(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.bFieldsCalculadora.setFont(font)
        self.bFieldsCalculadora.setObjectName("bFieldsCalculadora")
        self.gridLayout_8.addWidget(self.bFieldsCalculadora, 1, 2, 1, 1)
        self.twCalculadora = QtWidgets.QTableWidget(self.groupBox)
        self.twCalculadora.setObjectName("twCalculadora")
        self.twCalculadora.setColumnCount(0)
        self.twCalculadora.setRowCount(0)
        self.gridLayout_8.addWidget(self.twCalculadora, 1, 3, 1, 1)
        self.lwFields = QtWidgets.QListWidget(self.groupBox)
        self.lwFields.setObjectName("lwFields")
        self.gridLayout_8.addWidget(self.lwFields, 0, 0, 2, 2)
        self.cbLayers = QtWidgets.QComboBox(self.groupBox)
        self.cbLayers.setObjectName("cbLayers")
        self.gridLayout_8.addWidget(self.cbLayers, 0, 2, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(Calculadora)
        QtCore.QMetaObject.connectSlotsByName(Calculadora)

    def retranslateUi(self, Calculadora):
        _translate = QtCore.QCoreApplication.translate
        Calculadora.setWindowTitle(_translate("Calculadora", "Form"))
        self.bFieldsCalculadora.setText(_translate("Calculadora", "-->"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Calculadora = QtWidgets.QWidget()
    ui = Ui_Calculadora()
    ui.setupUi(Calculadora)
    Calculadora.show()
    sys.exit(app.exec_())

