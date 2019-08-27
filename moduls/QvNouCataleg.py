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
from typing import Callable 


class QvNouCataleg(QWidget):
    
    def __init__(self,parent: QtWidgets.QWidget=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        #Layout gran. Tot a dins
        self.layout=QVBoxLayout(self)

        #FILA SUPERIOR
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget(objectName='layoutFosc')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo=QLabel()
        self.lblLogo.setPixmap(QPixmap('imatges/qVistaLogo_text_40_old.png'))
        self.lblCapcalera=QLabel(objectName='fosca')
        self.lblCapcalera.setText('Catàleg de mapes')
        self.lblCapcalera.setStyleSheet('background-color: %s;' %QvConstants.COLORFOSCHTML)
        self.lblCapcalera.setFont(QvConstants.FONTTITOLS)
        self.lblCapcalera.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.bCerca=QPushButton()
        self.bCerca.setIcon(QIcon('imatges/cerca.png'))
        self.bCerca.setIconSize(QSize(24, 24))
        self.bCerca.setFixedWidth(40)
        self.bCerca.setFixedHeight(40)
        self.bCerca.setStyleSheet("background-color:%s;" %QvConstants.COLORFOSCHTML)
        self.leCerca = QLineEdit()
        self.leCerca.setFixedHeight(40)
        self.leCerca.setFixedWidth(240)
        self.leCerca.setStyleSheet("background-color:%s;"
                                    "border: 8px solid %s;"
                                    "padding: 2px;"
                                    %(QvConstants.COLORCLARHTML,QvConstants.COLORFOSCHTML))
        self.leCerca.setFont(QvConstants.FONTTEXT)

        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)
        self.layoutCapcalera.addWidget(self.bCerca)
        self.layoutCapcalera.addWidget(self.leCerca)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layoutCapcalera.setContentsMargins(0,0,0,0)
        self.layoutCapcalera.setSpacing(0)
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self))
        self.widgetSup.setStyleSheet('color: %s; background-color: solid %s; border: 0px;'%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML))

        #BOTONERA MINIMITZAR MAXIMITZAR TANCAR
        stylesheetBotonsFinestra='''
            QPushButton{
                background: %s;
            }
            QPushButton::hover {
                background-color: %s;
                opacity: 1;
            }
            QPushButton::pressed{
                background-color: %s;
                opacity: 0.1;
            }
        '''%(QvConstants.COLORFOSCHTML,QvConstants.COLORDESTACATHTML,QvConstants.COLORDESTACATHTML)

        self.botoMinimitzar=QvPushButton(flat=True)
        self.botoMinimitzar.setIcon(QIcon('imatges/window-minimize.png'))
        self.botoMinimitzar.setFixedSize(40,40)
        self.botoMinimitzar.clicked.connect(self.showMinimized)
        self.botoMinimitzar.setStyleSheet(stylesheetBotonsFinestra)
        self.layoutCapcalera.addWidget(self.botoMinimitzar)

        self.maximitzada=True
        iconaRestaurar1=QIcon('imatges/window-restore.png')
        iconaRestaurar2=QIcon('imatges/window-maximize.png')
        def restaurar():
            if self.maximitzada:
                self.setWindowFlag(Qt.FramelessWindowHint)
                self.setWindowState(Qt.WindowActive)
                amplada=self.width()
                alcada=self.height()
                self.resize(0.8*amplada,0.8*alcada)
                self.move(0,0)
                self.show()
                self.botoRestaurar.setIcon(iconaRestaurar2)
            else:
                self.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
                self.botoRestaurar.setIcon(iconaRestaurar1)
                self.setWindowFlag(Qt.FramelessWindowHint)
                self.show()
            self.maximitzada=not self.maximitzada
        self.restaurarFunc=restaurar
        self.botoRestaurar=QvPushButton(flat=True)
        self.botoRestaurar.setIcon(iconaRestaurar1)
        self.botoRestaurar.clicked.connect(restaurar)
        self.botoRestaurar.setFixedSize(40,40)
        self.botoRestaurar.setStyleSheet(stylesheetBotonsFinestra)
        self.layoutCapcalera.addWidget(self.botoRestaurar)

        self.botoSortir=QvPushButton(flat=True)
        self.botoSortir.setIcon(QIcon('imatges/window_close.png'))
        self.botoSortir.setFixedSize(40,40)
        self.botoSortir.clicked.connect(self.close)
        self.botoSortir.setStyleSheet(stylesheetBotonsFinestra)
        self.layoutCapcalera.addWidget(self.botoSortir)



        #CONTINGUT CATALEG
        self.spacer = QtWidgets.QSpacerItem(99999, 99999, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)




if __name__ == "__main__":
    with qgisapp() as app:

        cataleg = QvNouCataleg()
        cataleg.showMaximized()