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


class QvNews(QtWidgets.QAction):
    def __init__(self,parent=None):
        self.ICONA=QIcon('Imatges/News.png')
        self.ICONADESTACADA=QIcon('Imatges/NewsDestacada.png')
        #QtWidgets.QAction.__init__(self,self.ICONA,'Notícies',parent)
        super().__init__(self.ICONA,'Notícies',parent)
        self.ARXIUNEWS='d:/qVista/codi/News/Noticies.htm'
        self.ARXIUTMP=tempfile.gettempdir()+'\\ultimaNewOberta'
        if self.calNoticiaNova():
            self.timer=QTimer()
            self.timer.timeout.connect(self.blink)
            self.timer.start(200)
        self.setStatusTip('Notícies')
        self.triggered.connect(self.mostraNoticies)

    def blink(self):
        if not hasattr(self,'light'):
            self.light=False
            self.numBlinks=0

        if self.light:
            self.setIcon(self.ICONADESTACADA)
            self.numBlinks+=1
        else:
            self.setIcon(self.ICONA)

        if self.numBlinks==4:
            delattr(self,'timer')
            #self.setVisible(True)
            delattr(self,'numBlinks')

        self.light=not self.light

    def mostraNoticies(self):
        self.news=QvNewsAux(self.ARXIUNEWS)
        self.news.show()
        with open(self.ARXIUTMP,'w') as arxiu:
            #Escrivim alguna cosa. Realment no caldria
            import time
            arxiu.write(str(time.time()))
    def calNoticiaNova(self):
        #Si no existeix l'arxiu temporal vol dir que mai hem obert notícies :(
        if not os.path.isfile(self.ARXIUNEWS):
            return False
        if not os.path.isfile(self.ARXIUTMP):
            return True
        return os.path.getmtime(self.ARXIUTMP)<os.path.getmtime(self.ARXIUNEWS)

class QvNewsAux(QFrame):
    def __init__(self, file, parent=None):
        super().__init__(parent)
        #Layout gran. Tot a dins
        self.layout=QVBoxLayout(self)

        #FILA SUPERIOR
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget()
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo=QLabel()
        self.lblLogo.setPixmap(QPixmap('imatges/qVistaLogoVerdSenseText2.png').scaledToHeight(40))
        self.lblCapcalera=QLabel()
        self.lblCapcalera.setText('  Novetats qVista')
        self.lblCapcalera.setStyleSheet('color: %s'%QvConstants.COLORFOSC)
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)

        #Text de la notícia
        self.caixaText=QtWidgets.QTextEdit()
        self.caixaText.setHtml(open(file).read())
        self.layout.addWidget(self.caixaText)

        #Botó de sortida
        self.layoutBoto=QHBoxLayout()
        self.layout.addLayout(self.layoutBoto)
        self.layoutBoto.addItem(QSpacerItem(20, 5, QSizePolicy.Expanding,QSizePolicy.Minimum))
        self.exitButton=QvPushButton('Tancar')
        self.exitButton.clicked.connect(self.close)
        self.layoutBoto.addWidget(self.exitButton)

        self.formata()
    def formata(self):
        self.caixaText.viewport().setAutoFillBackground(False)
        self.caixaText.setReadOnly(True)
        self.caixaText.setEnabled(True) #Millor que es pugui seleccionar el text? O que no es pugui?
        self.caixaText.setFrameStyle(QFrame.NoFrame)
        self.caixaText.verticalScrollBar().setStyleSheet(
            "QScrollBar:vertical:hover {"
            "    background:%s;"
            "    margin: 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "    background: %s;"
            "    min-height: 0px;"
            "}"
            "QScrollBar::add-line:vertical {"
            "    background: %s;"
            "    height: 0px;"
            "}"
            "QScrollBar::sub-line:vertical {"
            "    background: %s;"
            "    height: 0 px;"
            "}"%(QvConstants.COLORGRIS, QvConstants.COLORGRIS, QvConstants.COLORGRIS, QvConstants.COLORGRIS))
        self.caixaText.setStyleSheet('margin: 20px 2px 20px 20px')
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
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0,0,0,0)
        self.layoutCapcalera.setSpacing(0)
        self.layoutBoto.setContentsMargins(0,0,0,0)
        self.layoutBoto.setSpacing(0)

        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self))
        
        self.setWindowTitle("qVista - Noticies")
        self.resize(640,480)
        self.oldPos=self.pos()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        #print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Escape or event.key()==Qt.Key_Return:
            self.close()

class QvPushButton(QPushButton):
    def __init__(self, text='', parent=None):
        QPushButton.__init__(self,text,parent)
        
        self.setStyleSheet(
            "margin: 20px;"
            "border: none;"
            "padding: 5px 20px;"
            "color: %s;"
            "background-color: %s" % (QvConstants.COLORBLANC,QvConstants.COLORFOSC))
        self.setGraphicsEffect(QvConstants.ombraWidget())
        self.setFont(QvConstants.FONTTEXT)

    def enterEvent(self,event):
        QPushButton.enterEvent(self,event)
        self.setCursor(Qt.PointingHandCursor)
    def leaveEvent(self,event):
        QPushButton.leaveEvent(self,event)
        self.setCursor(Qt.ArrowCursor)

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    news=QvNews()
    menu=QMenu()
    menu.addAction(news)
    menu.show()
    sys.exit(app.exec_())