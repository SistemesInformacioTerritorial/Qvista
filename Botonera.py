# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\RepsQV\qVista\Botonera.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Botonera(object):
    def setupUi(self, Botonera):
        Botonera.setObjectName("Botonera")
        Botonera.resize(180, 503)
        Botonera.setMinimumSize(QtCore.QSize(180, 0))
        Botonera.setMaximumSize(QtCore.QSize(180, 16777215))
        self.gridLayout = QtWidgets.QGridLayout(Botonera)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Botonera)
        self.label.setMinimumSize(QtCore.QSize(0, 70))
        self.label.setMaximumSize(QtCore.QSize(16777215, 70))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("miniQVista.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(Botonera)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.toolBox = QtWidgets.QToolBox(Botonera)
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 160, 327))
        self.page.setObjectName("page")
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 160, 327))
        self.page_2.setObjectName("page_2")
        self.toolBox.addItem(self.page_2, "")
        self.verticalLayout.addWidget(self.toolBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Botonera)
        self.toolBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Botonera)

    def retranslateUi(self, Botonera):
        _translate = QtCore.QCoreApplication.translate
        Botonera.setWindowTitle(_translate("Botonera", "Form"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Botonera", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Botonera", "Page 2"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Botonera = QtWidgets.QWidget()
    ui = Ui_Botonera()
    ui.setupUi(Botonera)
    Botonera.show()
    sys.exit(app.exec_())

