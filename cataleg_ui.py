# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\RepsQV\qVista\cataleg_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Cataleg(object):
    def setupUi(self, Cataleg):
        Cataleg.setObjectName("Cataleg")
        Cataleg.resize(650, 846)
        Cataleg.setMinimumSize(QtCore.QSize(650, 0))
        Cataleg.setMaximumSize(QtCore.QSize(650, 16777215))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        Cataleg.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(Cataleg)
        self.gridLayout.setObjectName("gridLayout")
        self.treeCataleg = QtWidgets.QTreeView(Cataleg)
        self.treeCataleg.setMinimumSize(QtCore.QSize(300, 0))
        self.treeCataleg.setMaximumSize(QtCore.QSize(300, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.treeCataleg.setFont(font)
        self.treeCataleg.setObjectName("treeCataleg")
        self.gridLayout.addWidget(self.treeCataleg, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.txtMetadadesCataleg = QtWidgets.QTextEdit(Cataleg)
        self.txtMetadadesCataleg.setMinimumSize(QtCore.QSize(300, 0))
        self.txtMetadadesCataleg.setMaximumSize(QtCore.QSize(300, 16777215))
        self.txtMetadadesCataleg.setAcceptRichText(True)
        self.txtMetadadesCataleg.setObjectName("txtMetadadesCataleg")
        self.verticalLayout_3.addWidget(self.txtMetadadesCataleg)
        self.lblMapaCataleg = QtWidgets.QLabel(Cataleg)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMapaCataleg.sizePolicy().hasHeightForWidth())
        self.lblMapaCataleg.setSizePolicy(sizePolicy)
        self.lblMapaCataleg.setMinimumSize(QtCore.QSize(300, 300))
        self.lblMapaCataleg.setMaximumSize(QtCore.QSize(300, 300))
        self.lblMapaCataleg.setFrameShape(QtWidgets.QFrame.Box)
        self.lblMapaCataleg.setText("")
        self.lblMapaCataleg.setPixmap(QtGui.QPixmap("../../QPIC/Parcelari.gif"))
        self.lblMapaCataleg.setScaledContents(True)
        self.lblMapaCataleg.setObjectName("lblMapaCataleg")
        self.verticalLayout_3.addWidget(self.lblMapaCataleg)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.treeCataleg.raise_()
        self.txtMetadadesCataleg.raise_()
        self.lblMapaCataleg.raise_()

        self.retranslateUi(Cataleg)
        QtCore.QMetaObject.connectSlotsByName(Cataleg)

    def retranslateUi(self, Cataleg):
        _translate = QtCore.QCoreApplication.translate
        Cataleg.setWindowTitle(_translate("Cataleg", "Form"))
        self.txtMetadadesCataleg.setHtml(_translate("Cataleg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:8pt; font-weight:600; color:#7f7f7f;\">[Spatial] Parcel·lari Municipal</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Format</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Oracle Spatial</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\"> </span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Resum</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Parcel·lari derivat del topogràfic 1:1000, amb illes.</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">També conté números de portals i noms de carrers i places.</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\"> </span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Escales de visibilitat</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Inferior a 1:6000, depenent de cada capa.</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\"> </span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Contingut</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">VW_GEO_PARCELARI_POL = Polígons de parcel·la</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">VW_GEO_ILLA_POL = Polígons d’illa</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">VW_GEO_NUM_POST_TEX = Números de policia, portals</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">VW_GEO_TOPONIMIA_1000_PUNTS = Toponímia, noms de carrers, vies urbanes, vials interiors i places.</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\"> </span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Ubicació de les dades</span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">: Connexió Oracle</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Base de Dades=GEOPR1</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Servidor= GEOPR1.imi.bcn</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Port=1551</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Usuari=SIU_CONS</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Symbol\'; font-size:9pt; color:#7f7f7f;\">·</span><span style=\" font-family:\'Times New Roman\'; font-size:7pt; color:#7f7f7f;\">  </span><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Contrasenya=SIU_CONS</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\"> </span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; font-weight:600; color:#7f7f7f;\">Propietari</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Pla de la Ciutat</span><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial,sans-serif\'; font-size:9pt; color:#7f7f7f;\">Ajuntament de Barcelona</span><span style=\" font-size:8pt;\"> </span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Cataleg = QtWidgets.QWidget()
    ui = Ui_Cataleg()
    ui.setupUi(Cataleg)
    Cataleg.show()
    sys.exit(app.exec_())

