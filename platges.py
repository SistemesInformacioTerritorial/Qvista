# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'platges.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1128, 722)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(-10, 90, 1151, 281))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("Imatges/FotoAeriaPlatges_1900px.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.pbSomorrostro1 = QtWidgets.QPushButton(Form)
        self.pbSomorrostro1.setGeometry(QtCore.QRect(300, 220, 51, 31))
        self.pbSomorrostro1.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Imatges/cctv.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pbSomorrostro1.setIcon(icon)
        self.pbSomorrostro1.setIconSize(QtCore.QSize(32, 32))
        self.pbSomorrostro1.setObjectName("pbSomorrostro1")
        self.pbSomorrostro2 = QtWidgets.QPushButton(Form)
        self.pbSomorrostro2.setGeometry(QtCore.QRect(300, 260, 51, 31))
        self.pbSomorrostro2.setText("")
        self.pbSomorrostro2.setIcon(icon)
        self.pbSomorrostro2.setIconSize(QtCore.QSize(32, 32))
        self.pbSomorrostro2.setObjectName("pbSomorrostro2")
        self.pbPort2 = QtWidgets.QPushButton(Form)
        self.pbPort2.setGeometry(QtCore.QRect(440, 230, 51, 31))
        self.pbPort2.setText("")
        self.pbPort2.setIcon(icon)
        self.pbPort2.setIconSize(QtCore.QSize(32, 32))
        self.pbPort2.setObjectName("pbPort2")
        self.pbMarBella = QtWidgets.QPushButton(Form)
        self.pbMarBella.setGeometry(QtCore.QRect(720, 190, 51, 31))
        self.pbMarBella.setText("")
        self.pbMarBella.setIcon(icon)
        self.pbMarBella.setIconSize(QtCore.QSize(32, 32))
        self.pbMarBella.setObjectName("pbMarBella")
        self.pbPort1 = QtWidgets.QPushButton(Form)
        self.pbPort1.setGeometry(QtCore.QRect(380, 240, 51, 31))
        self.pbPort1.setText("")
        self.pbPort1.setIcon(icon)
        self.pbPort1.setIconSize(QtCore.QSize(32, 32))
        self.pbPort1.setObjectName("pbPort1")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

