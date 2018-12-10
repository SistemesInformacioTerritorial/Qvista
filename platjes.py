# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'platjes.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1141, 722)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(-10, 80, 1151, 461))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("Imatges/FotoAeriaPlatges_1900px.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.pbSSebastia = QtWidgets.QPushButton(Form)
        self.pbSSebastia.setGeometry(QtCore.QRect(60, 460, 51, 31))
        self.pbSSebastia.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Imatges/cctv.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pbSSebastia.setIcon(icon)
        self.pbSSebastia.setIconSize(QtCore.QSize(32, 32))
        self.pbSSebastia.setObjectName("pbSSebastia")
        self.pbSantMiquel = QtWidgets.QPushButton(Form)
        self.pbSantMiquel.setGeometry(QtCore.QRect(110, 390, 51, 31))
        self.pbSantMiquel.setText("")
        self.pbSantMiquel.setIcon(icon)
        self.pbSantMiquel.setIconSize(QtCore.QSize(32, 32))
        self.pbSantMiquel.setObjectName("pbSantMiquel")
        self.pbBarceloneta = QtWidgets.QPushButton(Form)
        self.pbBarceloneta.setGeometry(QtCore.QRect(210, 350, 51, 31))
        self.pbBarceloneta.setText("")
        self.pbBarceloneta.setIcon(icon)
        self.pbBarceloneta.setIconSize(QtCore.QSize(32, 32))
        self.pbBarceloneta.setObjectName("pbBarceloneta")
        self.pbSomorrostro = QtWidgets.QPushButton(Form)
        self.pbSomorrostro.setGeometry(QtCore.QRect(300, 290, 51, 31))
        self.pbSomorrostro.setText("")
        self.pbSomorrostro.setIcon(icon)
        self.pbSomorrostro.setIconSize(QtCore.QSize(32, 32))
        self.pbSomorrostro.setObjectName("pbSomorrostro")
        self.pbNovaIcaria = QtWidgets.QPushButton(Form)
        self.pbNovaIcaria.setGeometry(QtCore.QRect(480, 260, 51, 31))
        self.pbNovaIcaria.setText("")
        self.pbNovaIcaria.setIcon(icon)
        self.pbNovaIcaria.setIconSize(QtCore.QSize(32, 32))
        self.pbNovaIcaria.setObjectName("pbNovaIcaria")
        self.pbBogatell = QtWidgets.QPushButton(Form)
        self.pbBogatell.setGeometry(QtCore.QRect(600, 240, 51, 31))
        self.pbBogatell.setText("")
        self.pbBogatell.setIcon(icon)
        self.pbBogatell.setIconSize(QtCore.QSize(32, 32))
        self.pbBogatell.setObjectName("pbBogatell")
        self.pbMarBella = QtWidgets.QPushButton(Form)
        self.pbMarBella.setGeometry(QtCore.QRect(720, 240, 51, 31))
        self.pbMarBella.setText("")
        self.pbMarBella.setIcon(icon)
        self.pbMarBella.setIconSize(QtCore.QSize(32, 32))
        self.pbMarBella.setObjectName("pbMarBella")
        self.pbNovaMarBella = QtWidgets.QPushButton(Form)
        self.pbNovaMarBella.setGeometry(QtCore.QRect(820, 230, 51, 31))
        self.pbNovaMarBella.setText("")
        self.pbNovaMarBella.setIcon(icon)
        self.pbNovaMarBella.setIconSize(QtCore.QSize(32, 32))
        self.pbNovaMarBella.setObjectName("pbNovaMarBella")
        self.pbLlevant = QtWidgets.QPushButton(Form)
        self.pbLlevant.setGeometry(QtCore.QRect(890, 200, 51, 31))
        self.pbLlevant.setText("")
        self.pbLlevant.setIcon(icon)
        self.pbLlevant.setIconSize(QtCore.QSize(32, 32))
        self.pbLlevant.setObjectName("pbLlevant")
        self.pbZonaBanysForum = QtWidgets.QPushButton(Form)
        self.pbZonaBanysForum.setGeometry(QtCore.QRect(1050, 290, 51, 31))
        self.pbZonaBanysForum.setText("")
        self.pbZonaBanysForum.setIcon(icon)
        self.pbZonaBanysForum.setIconSize(QtCore.QSize(32, 32))
        self.pbZonaBanysForum.setObjectName("pbZonaBanysForum")

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

