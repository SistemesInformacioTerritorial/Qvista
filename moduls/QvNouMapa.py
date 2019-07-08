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

class QvNouMapa(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout=QVBoxLayout(self)
        #Fila superior
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget(objectName='layoutFosc')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)

        self.leTitol=QLineEdit(self)
        self.layout.addWidget(self.leTitol)

        self.layoutTresBotons1=QHBoxLayout(self)
        self.mapaBuit=QvToolButton(self)
        self.mapaBuit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapaBuit.setText('Mapa buit')
        self.mapaBuit.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapaBuit.setIconSize(QSize(250, 150))
        self.mapaBuit.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))

        self.mapa1=QvToolButton(self)
        self.mapa1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa1.setText('Mapa buit')
        self.mapa1.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapa1.setIconSize(QSize(250, 150))
        self.mapa1.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))

        self.mapa2=QvToolButton(self)
        self.mapa2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa2.setText('Mapa buit')
        self.mapa2.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapa2.setIconSize(QSize(250, 150))
        self.mapa2.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))
        self.layoutTresBotons1.addWidget(self.mapaBuit)
        self.layoutTresBotons1.addWidget(self.mapa1)
        self.layoutTresBotons1.addWidget(self.mapa2)

        self.layoutTresBotons2=QHBoxLayout(self)
        self.mapa3=QvToolButton(self)
        self.mapa3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa3.setText('Mapa buit')
        self.mapa3.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapa3.setIconSize(QSize(250, 150))
        self.mapa3.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))

        self.mapa4=QvToolButton(self)
        self.mapa4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa4.setText('Mapa buit')
        self.mapa4.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapa4.setIconSize(QSize(250, 150))
        self.mapa4.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))

        self.mapa5=QvToolButton(self)
        self.mapa5.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa5.setText('Mapa buit')
        self.mapa5.setIcon(QIcon('./Imatges/ProvaMapaBoto_200x150.png'))
        self.mapa5.setIconSize(QSize(250, 150))
        self.mapa5.clicked.connect(lambda: self.setAdreca('./__newProjectTemplate.qgs'))
        self.layoutTresBotons2.addWidget(self.mapa3)
        self.layoutTresBotons2.addWidget(self.mapa4)
        self.layoutTresBotons2.addWidget(self.mapa5)

        self.layout.addLayout(self.layoutTresBotons1)
        self.layout.addLayout(self.layoutTresBotons2)

        self.botoAcceptar=QvPushButton('Acceptar',destacat=True,parent=self)
        self.botoAcceptar.setEnabled(False)
        self.botoAcceptar.clicked.connect(self.carrega)
        self.layout.addWidget(self.botoAcceptar)

    def setAdreca(self,adreca):
        self.adreca=adreca
        self.botoAcceptar.setEnabled(True)
    def carrega(self):
        
        self.parentWidget().obrirProjecte(self.adreca)
        self.close()

class QvToolButton(QToolButton):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setStyleSheet('''
            QToolButton{
                padding: 0px;
                background: transparent;
                margin: 0px;
                border: 0px;
            }
        ''')
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())