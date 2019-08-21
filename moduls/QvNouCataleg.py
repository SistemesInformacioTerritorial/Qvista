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
from moduls.QvRedimLayout import QvRedimLayout
from typing import Callable 


class QvNouCataleg(QWidget):
    
    def __init__(self,parent: QtWidgets.QWidget=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.actualitzaWindowFlags()
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
        self.lblCapcalera.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
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
                self.setWindowFlag(Qt.FramelessWindowHint,False)
                self.setWindowState(Qt.WindowActive)
                self.actualitzaWindowFlags()
                amplada=self.width()
                alcada=self.height()
                self.resize(0.8*amplada,0.8*alcada)
                self.show()
                self.botoRestaurar.setIcon(iconaRestaurar2)
            else:
                self.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
                self.botoRestaurar.setIcon(iconaRestaurar1)
                self.setWindowFlag(Qt.FramelessWindowHint)
                self.actualitzaWindowFlags()
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
        # self.layout.addItem(self.spacer)
        self.layoutContingut=QHBoxLayout() #El contingut del catàleg
        self.layoutContingut.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.layout.addLayout(self.layoutContingut)
        self.carregaBandaEsquerra()
        self.wCataleg=QWidget()
        self.layoutCataleg=QVBoxLayout()
        # self.layoutCataleg.setSpacing(20)
        # self.layoutCataleg.setContentsMargins(20,20,20,20)
        self.wCataleg.setLayout(self.layoutCataleg)
        self.wCataleg.setStyleSheet('background: white')
        self.scroll=QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.wCataleg)
        self.scroll.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.wCataleg.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        # self.layoutContingut.addWidget(self.wCataleg)
        self.layoutContingut.addWidget(self.scroll)
        self.oldPos = self.pos()
        self.clickTots()
    def actualitzaWindowFlags(self):
        self.setWindowFlag(Qt.Window)
        self.setWindowFlag(Qt.CustomizeWindowHint,True)
        self.setWindowFlag(Qt.WindowTitleHint,False)
        self.setWindowFlag(Qt.WindowSystemMenuHint,False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint,False)
        self.setWindowFlag(Qt.WindowCloseButtonHint,False)
    def carregaBandaEsquerra(self):
        self.wBanda=QWidget()
        self.wBanda.setStyleSheet('background: %s;'%QvConstants.COLORGRISCLARHTML)
        self.wBanda.setFixedWidth(256)
        self.layoutContingut.addWidget(self.wBanda)
        self.lBanda=QVBoxLayout()
        self.lBanda.setContentsMargins(0,0,0,0)
        self.lBanda.setSpacing(0)
        self.wBanda.setLayout(self.lBanda)

        _,dirs,_=next(os.walk(carpetaCatalegProjectesLlista))
        self.catalegs={} #Serà un dict on la clau serà el nom del directori, i el valor una llista de botons
        self.botonsLaterals=[]

        self.fav=BotoLateral('Favorits',self)
        self.fav.setCheckable(True)
        self.lBanda.addWidget(self.fav)
        
        
        self.tots=BotoLateral('Tots',self)
        self.tots.setIcon(QIcon('Imatges/cm_check_all.png'))
        self.tots.setCheckable(True)
        self.lBanda.addWidget(self.tots)

        dirs=sorted(dirs)
        for x in dirs:
            print(x)
            self.catalegs[x]=self.carregaBotons(x) #TODO
            boto=BotoLateral(x,self)
            boto.setCheckable(True)
            # boto.clicked.connect(self.mostraMapes)
            self.botonsLaterals.append(boto)
            self.lBanda.addWidget(boto)
        
        
        self.tots.clicked.connect(self.clickTots)
        self.lBanda.addStretch()
    def clickTots(self):
        for x in self.botonsLaterals:
            x.setChecked(True)
        self.tots.setChecked(True)
        self.mostraMapes()
    def carregaBotons(self,dir):
        _,_,files=next(os.walk(carpetaCatalegProjectesLlista+'/'+dir))
        files=(x[:-4] for x in files if x.endswith('.qgs'))
        files=(carpetaCatalegProjectesLlista+dir+'/'+x for x in files)
        # files=[ for x in files]
        return [MapaCataleg(x,self) for x in files]
    def mostraMapes(self):
        self.clearContingut()
        self.widsCataleg=[]
        for x in self.botonsLaterals:
            if x.isChecked():
                wid=QWidget()
                layout=QVBoxLayout()
                lbl=QLabel(x.text())
                lbl.setStyleSheet('background: %s; padding: 2px;'%QvConstants.COLORGRISCLARHTML)
                lbl.setFont(QFont('Arial',12))
                lbl.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)
                layout.addWidget(lbl)
                nlayout=QvRedimLayout(spacing=20)
                layout.addLayout(nlayout)
                self.layoutCataleg.addWidget(wid)
                # self.layoutCataleg.addLayout(layout)
                for y in self.catalegs[x.text()]:
                    nlayout.addWidget(y)
                wid.setLayout(layout)
                wid.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
                self.widsCataleg.append(wid)
        # scrollArea=QScrollArea()
        # scrollArea.setWidget(self.wCataleg)
    def clearContingut(self):
        if hasattr(self,'widsCataleg'):
            for x in self.widsCataleg:
                # x.setParent(None)
                x.hide()
        return

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.maximitzada:
                self.restaurarFunc()
            delta = QPoint(event.globalPos() - self.oldPos)
            # print(delta)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
    def mouseDoubleClickEvent(self,event):
        if event.buttons()&Qt.LeftButton:
            self.restaurarFunc()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

class BotoLateral(QPushButton):
    def __init__(self,text,cataleg,parent=None):
        super().__init__(text,parent)
        self.cataleg=cataleg
        stylesheet='''
            BotoLateral{
                background: transparent;
                color: %s;
                border: none;
                width: 256px;
                height: 36px;
                text-align: left;
                padding-left: 10px;
            }
            BotoLateral:checked{
                background: solid %s;
                color: white;
                border: none;
            }
        '''%(QvConstants.COLORFOSCHTML,QvConstants.COLORCLARHTML)
        self.setStyleSheet(stylesheet)
        self.setFont(QFont('Arial',12))
    def mousePressEvent(self,event):
        if self==self.cataleg.tots:
            super().mousePressEvent(event)
        if event.modifiers()==Qt.ShiftModifier:
            #Multiselecció
            pass
        elif event.modifiers()==Qt.ControlModifier:
            #Seleccionar aquest botó mantenint els seleccionats
            self.setChecked(True)
            pass
        else:
            for x in self.cataleg.botonsLaterals:
                if x==self: continue
                x.setChecked(False)
            self.cataleg.tots.setChecked(False)
            if self!=self.cataleg.fav:
                self.cataleg.fav.setChecked(False)
            self.setChecked(True)
        self.cataleg.mostraMapes()

class MapaCataleg(QFrame):
    def __init__(self,dir,cataleg=None): #Dir ha de contenir la ruta de l'arxiu (absoluta o relativa) i no només el seu nom. Ha de ser sense extensió
        super().__init__()
        self.setFrameStyle(QFrame.Panel)
        self.checked=False
        self.cataleg=cataleg
        midaWidget=QSize(300,241)
        self.setFixedSize(midaWidget)
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.imatge=QPixmap(dir)
        self.lblImatge=QLabel()
        self.lblImatge.setPixmap(self.imatge)
        self.lblImatge.setFixedSize(300-4,180) #La mida que volem, restant-li el que ocuparà el border
        self.lblImatge.setScaledContents(True)
        midaLblImatge=self.lblImatge.sizeHint()
        self.layout.addWidget(self.lblImatge)
        try:
            with open(dir+'.txt') as text:
                self.titol=text.readline()

                self.text=text.read()
                self.lblText=QLabel('<p><strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 10pt;">%s<br /></span></strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 8pt;">%s</span></p>'%(self.titol,self.text))
                self.lblText.setWordWrap(True)
                self.layout.addWidget(self.lblText)
        except:
            self.lblText=QLabel('<p><strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 10pt;">Títol no disponible<br /></span></strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 8pt;">Descripció no disponible</span></p>')
            self.layout.addWidget(self.lblText)


        self.lblImatge.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.lblText.setAlignment(Qt.AlignTop)
        self.lblText.setFixedHeight(56)
        self.lblText.setAlignment(Qt.AlignTop)

        stylesheet='''
            QPushButton{
                background: solid white; margin: none; height: 40; width: 40;
            }
        '''

        self.botoFav=QPushButton('Fav',parent=self)
        self.botoFav.move(230,0)
        self.botoObre=QPushButton(parent=self)
        self.botoObre.setIcon(QIcon('Imatges/cm_play.png'))
        self.botoObre.move(230,100)
        self.botoObre.setIconSize(QSize(24,24))
        self.botoQGis=QPushButton(parent=self)
        self.botoQGis.setIcon(QIcon('Imatges/cm_qgis.png'))
        self.botoQGis.move(230,125)
        self.botoQGis.setIconSize(QSize(24,24))
        self.botoInfo=QPushButton(parent=self)
        self.botoInfo.setIcon(QIcon('Imatges/cm_info.png'))
        self.botoInfo.move(230,150)
        self.botoInfo.setIconSize(QSize(24,24))

        self.botoFav.setStyleSheet(stylesheet)
        self.botoObre.setStyleSheet(stylesheet)
        self.botoQGis.setStyleSheet(stylesheet)
        self.botoInfo.setStyleSheet(stylesheet)
        

        self.setChecked(False)
    def mousePressEvent(self,event):
        if event.buttons() & Qt.LeftButton:
            for x,y in self.cataleg.catalegs.items():
                for z in y:
                    z.setChecked(False)
            self.setChecked(True)
    def setChecked(self,checked):
        self.checked=checked
        if checked:
            self.setStyleSheet('MapaCataleg{border: 2px solid %s;}'%QvConstants.COLORFOSCHTML)
            self.botoFav.show()
            self.botoObre.show()
            self.botoQGis.show()
            self.botoInfo.show()
            
        else:
            self.setStyleSheet('MapaCataleg{border: 2px transparent;}')
            self.botoFav.hide()
            self.botoObre.hide()
            self.botoQGis.hide()
            self.botoInfo.hide()
        self.update()
    # def paintEvent(self,event):
    #     if self.checked:
    #         painter=QPainter(self)
    #         painter.setRenderHint(QPainter.Antialiasing)
    #         path=QPainterPath()
    #         path.addRect(QRectF(10,10,100,50))
    #         pen=QPen(Qt.black,10)
    #         painter.setPen(pen)
    #         painter.drawPath(path)
    #         painter.fillPath(path,Qt.red)
    #     super().paintEvent(event)
            


if __name__ == "__main__":
    with qgisapp() as app:
        app.setStyleSheet(open('style.qss').read())
        cataleg = QvNouCataleg()
        cataleg.showMaximized()
        # mapa=MapaCataleg("N:/9SITEB/Publicacions/qVista/CATALEG/Mapes - en preparació per XLG/2. Ortofotos/Imatge de satel·lit 2011 de l'AMB")
        # mapa.show()