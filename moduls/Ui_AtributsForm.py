# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\AtributsForm.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AtributsForm(object):
    def setupUi(self, AtributsForm):
        AtributsForm.setObjectName("AtributsForm")
        AtributsForm.setWindowModality(QtCore.Qt.WindowModal)
        AtributsForm.resize(600, 650)
        AtributsForm.setModal(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(AtributsForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(AtributsForm)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 578, 579))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.stackedWidget = QtWidgets.QStackedWidget(self.scrollAreaWidgetContents)
        self.stackedWidget.setObjectName("stackedWidget")
        self.verticalLayout_3.addWidget(self.stackedWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QFrame(AtributsForm)
        self.groupBox.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.groupBox.setFrameShadow(QtWidgets.QFrame.Raised)
        self.groupBox.setLineWidth(0)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bPrev = QtWidgets.QPushButton(self.groupBox)
        self.bPrev.setMinimumSize(QtCore.QSize(100, 23))
        self.bPrev.setMaximumSize(QtCore.QSize(100, 23))
        self.bPrev.setObjectName("bPrev")
        self.horizontalLayout_2.addWidget(self.bPrev)
        self.bNext = QtWidgets.QPushButton(self.groupBox)
        self.bNext.setMinimumSize(QtCore.QSize(100, 23))
        self.bNext.setMaximumSize(QtCore.QSize(100, 23))
        self.bNext.setObjectName("bNext")
        self.horizontalLayout_2.addWidget(self.bNext)
        self.horizontalLayout.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(AtributsForm)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setMinimumSize(QtCore.QSize(100, 36))
        self.buttonBox.setMaximumSize(QtCore.QSize(100, 36))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(AtributsForm)
        QtCore.QMetaObject.connectSlotsByName(AtributsForm)

    def retranslateUi(self, AtributsForm):
        _translate = QtCore.QCoreApplication.translate
        AtributsForm.setWindowTitle(_translate("AtributsForm", "Atributs d\'element"))
        self.bPrev.setText(_translate("AtributsForm", "Anterior"))
        self.bNext.setText(_translate("AtributsForm", "Següent"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AtributsForm = QtWidgets.QDialog()
    ui = Ui_AtributsForm()
    ui.setupUi(AtributsForm)
    AtributsForm.show()
    sys.exit(app.exec_())

