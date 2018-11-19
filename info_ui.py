# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\RepsQV\qVista\info_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Informacio(object):
    def setupUi(self, Informacio):
        Informacio.setObjectName("Informacio")
        Informacio.setWindowModality(QtCore.Qt.ApplicationModal)
        Informacio.resize(800, 567)
        Informacio.setStyleSheet("background-image: url(:/newPrefix/fonsBarna.JPG);")
        Informacio.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(Informacio)
        self.buttonBox.setGeometry(QtCore.QRect(450, 540, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(Informacio)
        self.label.setGeometry(QtCore.QRect(636, 4, 161, 51))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("miniQVista.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Informacio)
        self.label_2.setGeometry(QtCore.QRect(5, 5, 161, 51))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("Ajuntament-Barcelona.jpg"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Informacio)
        self.label_3.setGeometry(QtCore.QRect(280, 0, 331, 81))
        font = QtGui.QFont()
        font.setPointSize(51)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.label_3.setObjectName("label_3")
        self.textEdit = QtWidgets.QTextEdit(Informacio)
        self.textEdit.setGeometry(QtCore.QRect(0, 80, 801, 451))
        self.textEdit.setObjectName("textEdit")
    #TODO
        self.retranslateUi(Informacio)
        self.buttonBox.accepted.connect(Informacio.accept)
        self.buttonBox.rejected.connect(Informacio.reject)
        QtCore.QMetaObject.connectSlotsByName(Informacio)

    def retranslateUi(self, Informacio):
        _translate = QtCore.QCoreApplication.translate
        Informacio.setWindowTitle(_translate("Informacio", "Dialog"))
        self.label_3.setText(_translate("Informacio", "qVista"))
        self.textEdit.setHtml(_translate("Informacio", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Que és qVista?</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:16pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">qVista és el programa corporatiu de consulta territorial que ha de substituir l\'actual Vista!. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Les seves funcionalitats actuals son:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">    - Obrir i guardar fitxers de projecte QGIS</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">    - Obrir capes gràfiques en format SHP, GeoPackage</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">    - Obrir capes gràfiques en format de definició de layers .QLR</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">    - Arbre de Districtes/Barris per facilitar el geoposicionament</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Quina previsió d\'implentació es preveu per el qVista?</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:16pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">La primera distribució es farà a finals d\'Octubre de 2018. Després s\'anirà incrementant en funcionalitats a ritme mensual o bimensual. Es preveu que per Juny de 2019 estigui disponible la versió qVista 1.0</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">On puc reportar errors o sugeriments?</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:16pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">qVista es troba en fase de desenvolupament, i vol contar amb els usuaris durant aquesta fase, a fi de poder incorporar les millors funcionalitats sugerides. Per a qualsevol dubte, sugeriment o notificació d\'errors, envieu un correu a Jordi Cebrián  jcebrian@bcn.cat</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Qué podem esperar trobar en les properes versions?</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:16pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Podeu trobar una llista complerta amb les funcionalitats pendents d\'incorporar en la següent adreça: www.bcn.cat</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p></body></html>"))

import recursos_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Informacio = QtWidgets.QDialog()
    ui = Ui_Informacio()
    ui.setupUi(Informacio)
    Informacio.show()
    sys.exit(app.exec_())

