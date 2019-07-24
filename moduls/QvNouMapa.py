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
from moduls.QvToolButton import QvToolButton

class QvNouMapa(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.layout=QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        #Fila superior
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget(objectName='layout')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.lblLogo = QLabel()
        self.lblLogo.setPixmap(
            QPixmap('imatges/QVistaLogo_40_32.png'))
        self.lblLogo.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.lblCapcalera = QLabel(objectName='Fosca')
        self.lblCapcalera.setText('  Crear un nou mapa')
        self.lblCapcalera.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.layoutCapcalera.setContentsMargins(0, 0, 0, 0)
        self.layoutCapcalera.setSpacing(0)
        self.widgetSup.setGraphicsEffect(QvConstants.ombraHeader(self.widgetSup))
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)
        self.layoutCapcalera.addStretch()
        self.widgetSup.setStyleSheet('background: %s'%QvConstants.COLORFOSCHTML)
        self.layout.addWidget(self.widgetSup)

        wImage = 210
        hImage = 160

        self.layoutContingut=QVBoxLayout()
        self.layoutContingut.setContentsMargins(20,20,20,20)
        self.layoutContingut.setSpacing(20)

        self.layoutTitol = QHBoxLayout()
        self.lblTitle = QLabel()
        self.offset1 = QLabel()
        self.leTitol= QLineEdit()
        self.lblTitle.setText("Títol del projecte:")
        self.layoutTitol.addWidget(self.lblTitle)
        self.layoutTitol.addWidget(self.offset1)
        self.layoutTitol.addWidget(self.leTitol)
        self.leTitol.textChanged.connect(lambda: self.setTitol(self.leTitol.text()))
        #self.leTitol.setPlaceholderText("Títol del projecte")
        self.layoutContingut.addLayout(self.layoutTitol)

        self.lblExplicacio = QLabel()
        self.lblExplicacio.setText("Trieu amb quina base cartogràfica voleu iniciar el mapa. Més endavant podreu afergir-hi altres capes")
        self.layoutContingut.addWidget(self.lblExplicacio)

        self.layoutTresBotons1=QHBoxLayout(self)
        self.mapaBuit=QvToolButton(self)
        self.mapaBuit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapaBuit.setText('Parcel·lari')
        self.mapaBuit.setIcon(QIcon('./Imatges/nou_parcel·lari.png'))
        self.mapaBuit.setIconSize(QSize(wImage, hImage))
        self.mapaBuit.clicked.connect(lambda: self.botoClick(self.mapaBuit))

        self.mapa1=QvToolButton(self)
        self.mapa1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa1.setText('Topogràfic')
        self.mapa1.setIcon(QIcon('./Imatges/nou_topogràfic.png'))
        self.mapa1.setIconSize(QSize(wImage, hImage))
        self.mapa1.clicked.connect(lambda: self.botoClick(self.mapa1))

        self.mapa2=QvToolButton(self)
        self.mapa2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa2.setText('Plànol guia')
        self.mapa2.setIcon(QIcon('./Imatges/nou_guia.png'))
        self.mapa2.setIconSize(QSize(wImage, hImage))
        self.mapa2.clicked.connect(lambda: self.botoClick(self.mapa2))
        

        self.layoutTresBotons2=QHBoxLayout(self)
        self.mapa3=QvToolButton(self)
        self.mapa3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa3.setText('Ortofotos 1:1000')
        self.mapa3.setIcon(QIcon('./Imatges/nou_ortofoto.png'))
        self.mapa3.setIconSize(QSize(wImage, hImage))
        self.mapa3.clicked.connect(lambda: self.botoClick(self.mapa3))

        self.mapa4=QvToolButton(self)
        self.mapa4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa4.setText('Unitats administratives')
        self.mapa4.setIcon(QIcon('./Imatges/nou_divisions_administratives.png'))
        self.mapa4.setIconSize(QSize(wImage, hImage))
        self.mapa4.clicked.connect(lambda: self.botoClick(self.mapa4))

        self.mapa5=QvToolButton(self)
        self.mapa5.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mapa5.setText('Mapa buit')
        self.mapa5.setIcon(QIcon('./Imatges/nou_buit.png'))
        self.mapa5.setIconSize(QSize(wImage, hImage))
        self.mapa5.clicked.connect(lambda: self.botoClick(self.mapa5))

        self.layoutTresBotons1.addWidget(self.mapaBuit)
        self.layoutTresBotons1.addWidget(self.mapa1)
        self.layoutTresBotons1.addWidget(self.mapa2)
        self.layoutTresBotons2.addWidget(self.mapa3)
        self.layoutTresBotons2.addWidget(self.mapa4)
        self.layoutTresBotons2.addWidget(self.mapa5)
        
        

        self.layoutContingut.addLayout(self.layoutTresBotons1)
        self.layoutContingut.addLayout(self.layoutTresBotons2)

        self.layoutBotons=QHBoxLayout()
        self.botoAcceptar=QvPushButton('Acceptar',destacat=True,parent=self)
        self.botoAcceptar.setEnabled(False)
        self.botoAcceptar.clicked.connect(self.carrega)

        self.botoCancelar=QvPushButton('Cancel·lar',parent=self)
        self.botoCancelar.clicked.connect(self.close)

        self.layoutBotons.addStretch()
        self.layoutBotons.addWidget(self.botoAcceptar)
        self.layoutBotons.addWidget(self.botoCancelar)
        self.layoutContingut.addLayout(self.layoutBotons)
        self.layout.addLayout(self.layoutContingut)

    def botoClick(self,boto):
        botons=set([self.mapaBuit,self.mapa1,self.mapa2,self.mapa3,self.mapa4,self.mapa5])
        boto.setMarcat(True)
        botons.remove(boto)
        for x in botons: x.setMarcat(False)
        if boto is self.mapaBuit:
            self.setAdreca(docdirPlantilles+'parcelari.qgs')
        elif boto is self.mapa1:
            self.setAdreca(docdirPlantilles+'Topografic.qgs')
        elif boto is self.mapa2:
            self.setAdreca(docdirPlantilles+'PlanolGuia.qgs')
        elif boto is self.mapa3:
            self.setAdreca(docdirPlantilles+'Ortofotos1000.qgs')
        elif boto is self.mapa4:
            self.setAdreca(docdirPlantilles+'UnitatsAdministratives.qgs')
        elif boto is self.mapa5:
            self.setAdreca(docdirPlantilles+'MapaEnBlanc.qgs')

    def setAdreca(self,adreca):
        self.adreca=adreca
        if self.leTitol.text()!='': 
            self.botoAcceptar.setEnabled(True)
    def setTitol(self,titol):
        self.titol=titol
        if titol!='':
            if hasattr(self,'adreca'):
                self.botoAcceptar.setEnabled(True)
        else:
            self.botoAcceptar.setEnabled(False)
    def carrega(self):
        
        self.parentWidget().obrirProjecte(self.adreca)
        self.parentWidget().lblTitolProjecte.setText(self.titol)
        self.close()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        # print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Return:
            self.close()

# class QvToolButton(QToolButton):
#     def __init__(self,parent=None):
#         super().__init__(parent)
#         self.setStyleSheet('''
#             QToolButton{
#                 padding: 0px;
#                 background: transparent;
#                 margin: 0px;
#                 border: 0px;
#             }
#         ''')
#     def enterEvent(self,event):
#         super().enterEvent(event)
#         self.setCursor(QvConstants.cursorClick())
#     def leaveEvent(self,event):
#         super().leaveEvent(event)
#         self.setCursor(QvConstants.cursorFletxa())