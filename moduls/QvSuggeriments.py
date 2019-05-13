#!/usr/bin/env python
from moduls.QvImports import * 
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor
import os
import tempfile
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton

class QvSuggeriments(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        #Layout gran. Tot a dins
        self.layout=QVBoxLayout(self)

        #FILA SUPERIOR
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget()
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo=QLabel()
        self.lblLogo.setPixmap(QPixmap('imatges/bug_cap_sugg.png'))
        self.lblCapcalera=QLabel()
        self.lblCapcalera.setText(' Problemes? Suggeriments?')
        self.lblCapcalera.setStyleSheet('color: %s'%QvConstants.COLORFOSC)
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        #info
        self.info = QLabel()
        self.info.setFont(QvConstants.FONTTEXT)
        #self.info.setAlignment(Qt.AlignCenter)
        self.info.setContentsMargins(20,20,20,20)
        self.info.setText("Heu trobat algun problema? \nVoleu fer-nos algun suggeriment? \nSiusplau, Descriviu-lo breument a continuació. \nEl vostre suport ens ajudarà a millorar")
        self.layout.addWidget(self.info)

        #Text de la notícia
        self.caixaText=QtWidgets.QTextEdit()
        self.layoutDescripcio = QHBoxLayout()
        self.offset1 = QLabel()
        self.offset2 = QLabel()
        self.layoutDescripcio.addWidget(self.offset1)
        self.layoutDescripcio.addWidget(self.caixaText)
        self.layoutDescripcio.addWidget(self.offset2)
        self.layout.addLayout(self.layoutDescripcio)

        #Botons
        self.layoutBoto=QHBoxLayout()
        self.layout.addLayout(self.layoutBoto)
        #self.layoutBoto.addItem(QSpacerItem(10, 5, QSizePolicy.Expanding,QSizePolicy.Minimum))
        self.acceptButton=QvPushButton('Acceptar',destacat=True)
        self.acceptButton.clicked.connect(self.close)
        self.layoutBoto.addWidget(self.acceptButton)
        self.exitButton=QvPushButton('Cancel·lar')
        self.exitButton.clicked.connect(self.close)
        self.layoutBoto.addWidget(self.exitButton)

        self.formata()

    def formata(self):
        self.caixaText.viewport().setAutoFillBackground(False)
        self.caixaText.setEnabled(True) #Millor que es pugui seleccionar el text? O que no es pugui?
        #self.caixaText.setFrameStyle(QFrame.NoFrame)
        self.caixaText.setFont(QvConstants.FONTTEXT)
        self.caixaText.setStyleSheet("border:1px solid %s" % QvConstants.COLORCLAR)
        self.caixaText.verticalScrollBar().setStyleSheet(QvConstants.SCROLLBARSTYLESHEET)
        #self.caixaText.verticalScrollBar().setFrameStyle(QFrame.NoFrame)
        #Comentar si volem que s'oculti la scrollbar quan no s'utilitza
        #self.caixaText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.caixaText.setContentsMargins(0,0,0,0)
        self.caixaText.setViewportMargins(5,5,5,5)
        self.offset1.setFixedWidth(20)
        self.offset2.setFixedWidth(20)
        self.lblCapcalera.setStyleSheet('color: %s'%QvConstants.COLORFOSC)
        self.setStyleSheet('background-color: %s; QFrame {border: 0px} QLabel {border: 0px}'%QvConstants.COLORBLANC)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.lblLogo.setStyleSheet('background-color: %s; border: 0px'%QvConstants.COLORFOSC)
        self.lblLogo.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        #self.lblLogo.setGraphicsEffect(QvConstants.ombra(self))
        self.lblCapcalera.setStyleSheet('background-color: %s; color: %s; border: 0px'%(QvConstants.COLORFOSC,QvConstants.COLORBLANC))
        self.lblCapcalera.setFont(QvConstants.FONTTITOLS)
        self.lblCapcalera.setFixedHeight(40)
        #self.lblCapcalera.setGraphicsEffect(QvConstants.ombra(self))
        self.layout.setContentsMargins(0,0,0,0)
        #self.layout.setContentsMargins(20,0,20,0)
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0,0,0,0)
        self.layoutCapcalera.setSpacing(0)
        self.layoutBoto.setContentsMargins(0,0,0,0)
        self.layoutBoto.setSpacing(0)

        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self))
        
        self.setWindowTitle("qVista - Noticies")
        self.resize(480,360)
        self.oldPos=self.pos()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        #print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self,event):
        super().keyPressEvent(event)
        if event.key()==Qt.Key_Escape or event.key()==Qt.Key_Return:
            self.close()



if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    news=QvSuggeriments()
    news.show()
    sys.exit(app.exec_())