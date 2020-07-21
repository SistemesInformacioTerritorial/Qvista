# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SelectorParceles.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.layCanvas = QtWidgets.QHBoxLayout()
        self.layCanvas.setObjectName("layCanvas")
        self.verticalLayout.addLayout(self.layCanvas)
        self.layBotons = QtWidgets.QHBoxLayout()
        self.layBotons.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.layBotons.setObjectName("layBotons")
        self.bPanning = QtWidgets.QPushButton(self.centralwidget)
        self.bPanning.setEnabled(False)
        self.bPanning.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../Imatges/pan_tool_black_24x24.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.bPanning.setIcon(icon)
        self.bPanning.setObjectName("bPanning")
        self.layBotons.addWidget(self.bPanning)
        self.bSeleccio = QtWidgets.QPushButton(self.centralwidget)
        self.bSeleccio.setEnabled(False)
        self.bSeleccio.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../Imatges/apuntar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.bSeleccio.setIcon(icon1)
        self.bSeleccio.setObjectName("bSeleccio")
        self.layBotons.addWidget(self.bSeleccio)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layBotons.addItem(spacerItem)
        self.bConfirmar = QtWidgets.QPushButton(self.centralwidget)
        self.bConfirmar.setObjectName("bConfirmar")
        self.layBotons.addWidget(self.bConfirmar)
        self.bCancelar = QtWidgets.QPushButton(self.centralwidget)
        self.bCancelar.setObjectName("bCancelar")
        self.layBotons.addWidget(self.bCancelar)
        self.verticalLayout.addLayout(self.layBotons)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 18))
        self.menubar.setObjectName("menubar")
        self.menuHola = QtWidgets.QMenu(self.menubar)
        self.menuHola.setObjectName("menuHola")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionNova_sel_lecci = QtWidgets.QAction(MainWindow)
        self.actionNova_sel_lecci.setObjectName("actionNova_sel_lecci")
        self.actionObrir_sel_lecci = QtWidgets.QAction(MainWindow)
        self.actionObrir_sel_lecci.setObjectName("actionObrir_sel_lecci")
        self.actionDesar = QtWidgets.QAction(MainWindow)
        self.actionDesar.setObjectName("actionDesar")
        self.menuHola.addAction(self.actionNova_sel_lecci)
        self.menuHola.addAction(self.actionObrir_sel_lecci)
        self.menuHola.addSeparator()
        self.menuHola.addAction(self.actionDesar)
        self.menubar.addAction(self.menuHola.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.bConfirmar.setText(_translate("MainWindow", "Confirmar"))
        self.bCancelar.setText(_translate("MainWindow", "Cancelar"))
        self.menuHola.setTitle(_translate("MainWindow", "Arxiu"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionNova_sel_lecci.setText(_translate("MainWindow", "Nova sel·lecció"))
        self.actionObrir_sel_lecci.setText(_translate("MainWindow", "Obrir sel·lecció"))
        self.actionDesar.setText(_translate("MainWindow", "Desar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

