# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qvistawizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(919, 713)
        Wizard.setSizeGripEnabled(False)
        Wizard.setModal(False)
        Wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.wizardPage_2 = QtWidgets.QWizardPage()
        self.wizardPage_2.setObjectName("wizardPage_2")
        self.label = QtWidgets.QLabel(self.wizardPage_2)
        self.label.setGeometry(QtCore.QRect(50, 60, 831, 511))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("../dades/../dades/imatges/capturaQVista.PNG"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        Wizard.addPage(self.wizardPage_2)
        self.wizardPage1 = QtWidgets.QWizardPage()
        self.wizardPage1.setObjectName("wizardPage1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wizardPage1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.wizardPage1)
        self.pushButton_2.setMinimumSize(QtCore.QSize(250, 250))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.wizardPage1)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 250))
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 250))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        Wizard.addPage(self.wizardPage1)
        self.wizardPage2 = QtWidgets.QWizardPage()
        self.wizardPage2.setObjectName("wizardPage2")
        self.toolBox = QtWidgets.QToolBox(self.wizardPage2)
        self.toolBox.setGeometry(QtCore.QRect(230, 150, 101, 161))
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 101, 107))
        self.page.setObjectName("page")
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.page_2.setObjectName("page_2")
        self.toolBox.addItem(self.page_2, "")
        self.radioButton = QtWidgets.QRadioButton(self.wizardPage2)
        self.radioButton.setGeometry(QtCore.QRect(40, 390, 82, 17))
        self.radioButton.setObjectName("radioButton")
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.wizardPage2)
        self.commandLinkButton.setGeometry(QtCore.QRect(500, 190, 185, 41))
        self.commandLinkButton.setObjectName("commandLinkButton")
        Wizard.addPage(self.wizardPage2)
        self.wizardPage = QtWidgets.QWizardPage()
        self.wizardPage.setObjectName("wizardPage")
        self.toolButton = QtWidgets.QToolButton(self.wizardPage)
        self.toolButton.setGeometry(QtCore.QRect(130, 150, 141, 101))
        self.toolButton.setObjectName("toolButton")
        self.toolButton_2 = QtWidgets.QToolButton(self.wizardPage)
        self.toolButton_2.setGeometry(QtCore.QRect(350, 160, 151, 111))
        self.toolButton_2.setObjectName("toolButton_2")
        Wizard.addPage(self.wizardPage)

        self.retranslateUi(Wizard)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Wizard"))
        self.wizardPage1.setTitle(_translate("Wizard", "Escull la capa base"))
        self.wizardPage1.setSubTitle(_translate("Wizard", "Aquest capa mostrarà el fons cartogràfic."))
        self.pushButton_2.setText(_translate("Wizard", "PushButton"))
        self.pushButton.setText(_translate("Wizard", "PushButton"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Wizard", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Wizard", "Page 2"))
        self.radioButton.setText(_translate("Wizard", "RadioButton"))
        self.commandLinkButton.setText(_translate("Wizard", "CommandLinkButton"))
        self.toolButton.setText(_translate("Wizard", "..."))
        self.toolButton_2.setText(_translate("Wizard", "..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Wizard = QtWidgets.QWizard()
    ui = Ui_Wizard()
    ui.setupUi(Wizard)
    Wizard.show()
    sys.exit(app.exec_())

