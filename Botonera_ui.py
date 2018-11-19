# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\RepsQV\qVista\Botonera_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(170, 463)
        Frame.setMinimumSize(QtCore.QSize(170, 0))
        Frame.setMaximumSize(QtCore.QSize(170, 16777215))
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridLayout = QtWidgets.QGridLayout(Frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Frame)
        self.label.setMinimumSize(QtCore.QSize(150, 70))
        self.label.setMaximumSize(QtCore.QSize(150, 70))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("qvista_splash.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(Frame)
        self.lineEdit.setMinimumSize(QtCore.QSize(150, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(150, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.toolBox = QtWidgets.QToolBox(Frame)
        self.toolBox.setMinimumSize(QtCore.QSize(150, 0))
        self.toolBox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 150, 287))
        self.page.setObjectName("page")
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 150, 287))
        self.page_2.setObjectName("page_2")
        self.toolBox.addItem(self.page_2, "")
        self.gridLayout.addWidget(self.toolBox, 2, 0, 1, 1)

        self.retranslateUi(Frame)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Frame", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Frame", "Page 2"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Frame = QtWidgets.QFrame()
    ui = Ui_Frame()
    ui.setupUi(Frame)
    Frame.show()
    sys.exit(app.exec_())

