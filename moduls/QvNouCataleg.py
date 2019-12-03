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
import shutil
from moduls.QvVisorHTML import QvVisorHTML
import re
from moduls.QvFavorits import QvFavorits


class QvNouCataleg(QWidget):
    
    def __init__(self,parent: QtWidgets.QWidget=None):
        '''Construeix el catàleg
        El codi és més o menys el mateix que s'utilitza per construir moltes altres finestres frameless. 
        -Una capçalera amb el títol, botons i icona de qVista
        -Un layout amb el cos de la finestra
        El cos conté una botonera lateral a l'esquerra, amb un botó per cada carpeta del catàleg, i un layout redimensionable que mostra el contingut dels directoris seleccionats
        '''
        super().__init__()
        self.parent=parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.actualitzaWindowFlags()
        self.setWindowTitle('Catàleg de mapes')
        #Layout gran. Tot a dins
        self.layout=QVBoxLayout(self)

        #FILA SUPERIOR
        self.layoutCapcalera=QHBoxLayout()
        self.widgetSup=QWidget(objectName='layoutFosc')
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblLogo=QLabel()
        self.lblLogo.setPixmap(QPixmap(imatgesDir+'qVistaLogo_text_40_old.png'))
        self.lblCapcalera=QLabel(objectName='fosca')
        self.lblCapcalera.setText('Catàleg de mapes')
        self.lblCapcalera.setStyleSheet('background-color: %s;' %QvConstants.COLORFOSCHTML)
        self.lblCapcalera.setFont(QvConstants.FONTTITOLS)
        self.lblCapcalera.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
        self.bCerca=QPushButton()
        self.bCerca.setIcon(QIcon(imatgesDir+'cerca.png'))
        self.bCerca.setIconSize(QSize(24, 24))
        self.bCerca.setFixedWidth(40)
        self.bCerca.setFixedHeight(40)
        self.bCerca.setStyleSheet("background-color:%s; border: 0px; margin: 0px; padding: 0px;" %QvConstants.COLORFOSCHTML)
        self.leCerca = QLineEdit()
        self.leCerca.setFixedHeight(40)
        self.leCerca.setFixedWidth(320)
        self.leCerca.setStyleSheet("background-color:%s;"
                                    "color: white;"
                                    "border: 8px solid %s;"
                                    #"border-right: 8px solid %s;"
                                    #"border-bottom: 40px solid %s;"
                                    #"border-left: 8px solid %s;"
                                    "padding: 2px"
                                    # "margin: 8px;"
                                    %(QvConstants.COLORCLARHTML, QvConstants.COLORFOSCHTML))
        self.leCerca.setFont(QvConstants.FONTTEXT)
        self.leCerca.setPlaceholderText('Cercar...')
        self.leCerca.textChanged.connect(self.filtra)
        self.accioEsborra=self.leCerca.addAction(QIcon(imatgesDir+'cm_buidar_cercar.png'),QLineEdit.TrailingPosition)
        self.accioEsborra.triggered.connect(lambda: self.leCerca.setText(''))
        self.accioEsborra.setVisible(False)
        self.lblSpacer = QLabel()
        self.lblSpacer.setFixedHeight(40)
        self.lblSpacer.setFixedWidth(40)
        self.lblSpacer.setStyleSheet("background-color:%s;"%(QvConstants.COLORFOSCHTML))

        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)
        self.layoutCapcalera.addWidget(self.bCerca)
        self.layoutCapcalera.addWidget(self.leCerca)
        self.layoutCapcalera.addWidget(self.lblSpacer)

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
        self.botoMinimitzar.setIcon(QIcon(imatgesDir+'window-minimize.png'))
        self.botoMinimitzar.setFixedSize(40,40)
        self.botoMinimitzar.clicked.connect(self.showMinimized)
        self.botoMinimitzar.setStyleSheet(stylesheetBotonsFinestra)
        self.layoutCapcalera.addWidget(self.botoMinimitzar)

        self.maximitzada=True
        iconaRestaurar1=QIcon(imatgesDir+'window-restore.png')
        iconaRestaurar2=QIcon(imatgesDir+'window-maximize.png')
        def restaurar():
            if self.maximitzada:
                self.setWindowFlag(Qt.FramelessWindowHint,False)
                self.setWindowState(Qt.WindowActive)
                self.actualitzaWindowFlags()
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
        self.botoSortir.setIcon(QIcon(imatgesDir+'window_close.png'))
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
        self.layoutCataleg.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.layoutCataleg.setSpacing(20)
        # self.layoutCataleg.setContentsMargins(20,20,20,20)
        self.wCataleg.setLayout(self.layoutCataleg)
        self.wCataleg.setStyleSheet('background: white')
        self.scroll=QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.wCataleg)
        self.scroll.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.scroll.installEventFilter(self)
        self.wCataleg.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        # self.layoutContingut.addWidget(self.wCataleg)
        self.layoutContingut.addWidget(self.scroll)
        self.oldPos = self.pos()
        self.esPotMoure=False
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
        '''Carrega els botons de la banda esquerra i, per cada directori, tots els seus mapes
        '''
        self.favorits=QvFavorits().getFavorits()
        self.wBanda=QWidget()
        self.wBanda.setStyleSheet('background: %s;'%QvConstants.COLORGRISCLARHTML)
        self.wBanda.setFixedWidth(256)
        self.layoutContingut.addWidget(self.wBanda)
        self.lBanda=QVBoxLayout()
        self.lBanda.setContentsMargins(0,0,0,0)
        self.lBanda.setSpacing(0)
        self.wBanda.setLayout(self.lBanda)

        self.tots=BotoLateral('Tots',self)
        self.tots.setIcon(QIcon(imatgesDir+'cm_check_all.png'))
        self.tots.setCheckable(True)
        self.lBanda.addWidget(self.tots)

        self.fav=BotoLateral('Favorits',self)
        self.fav.setIcon(QIcon(imatgesDir+'star.png'))
        self.fav.setCheckable(True)
        self.lBanda.addWidget(self.fav)
        
        
        self.catalegs={} #Serà un dict on la clau serà el nom del directori, i el valor una llista de botons
        self.botonsLaterals=[]
        for y in carpetaCatalegProjectesLlista:
            try:
                #os.walk(dir) ens dóna un generador que es va recorrent tots els nivells d'un directori
                #Per cada nivell ens dóna tres llistes, que són l'arrel, els directoris i els arxius
                #Com que només ens interessa el primer nivell, enlloc de recórrer el generador, fem un next i agafem només el primer nivell
                #Com que només volem els directoris, no desem enlloc les altres llistes
                _,dirs,_=next(os.walk(y))
            except:
                continue #Si una carpeta no funciona (per exemple, l'usuari no hi té accés) simplement seguim mirant les altres
            
            dirs=sorted(dirs)
            for x in dirs:
                self.catalegs[x]=self.carregaBotons(x) 
                privat = y in carpetaCatalegProjectesPrivats
                boto=BotoLateral(x,self,privat)
                boto.setCheckable(True)
                if privat:
                    boto.setIcon(QIcon(imatgesDir+'lock-clar.png'))
                self.botonsLaterals.append(boto)
                self.lBanda.addWidget(boto)
        
        
        self.tots.clicked.connect(self.clickTots)
        self.fav.clicked.connect(self.clickFavorits)
        self.lBanda.addStretch()

    def clickTots(self):
        for x in self.botonsLaterals:
            x.setChecked(True)
        self.fav.setChecked(False)
        # self.tots.setChecked(False)
        self.mostraMapes()
        
    def clickFavorits(self):
        '''Copiem el contingut de mostraMapes, adaptant-lo perquè només mostri els favorits'''
        self.clearContingut()
        self.widsCataleg=[]
        self.nlayouts=[]
        for x in self.botonsLaterals:
            wid=QWidget()
            layout=QVBoxLayout()
            layout.setContentsMargins(0,0,0,0)
            lbl=QLabel(x.text())
            lbl.setStyleSheet('background: %s; padding: 2px;'%QvConstants.COLORGRISHTML)
            lbl.setFont(QFont('Arial',12))
            lbl.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)
            layout.addWidget(lbl)
            nlayout=QvRedimLayout()
            layout.addLayout(nlayout)
            # self.layoutCataleg.addLayout(layout)
            shaMostrat=False
            for y in self.catalegs[x.text()]:
                if y.esFavorit():
                    shaMostrat=True
                    nlayout.addWidget(y)
            wid.setLayout(layout)
            wid.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
            if shaMostrat:
                self.layoutCataleg.addWidget(wid)
                self.widsCataleg.append(wid)
                self.nlayouts.append(nlayout)
        self.indexLayoutSeleccionat=-1
        self.fav.setChecked(True)

    def carregaBotons(self,dir: str):
        f=[]
        for y in carpetaCatalegProjectesLlista:
            try:
                _,_,files=next(os.walk(y+'/'+dir))
                files=(x[:-4] for x in files if x.endswith('.qgs'))
                files=(y+dir+'/'+x for x in files)
                f+=files
            except:
                continue
        botons=[MapaCataleg(x,self) for x in f]
        for x in botons:
            if x.getNomMapa() in self.favorits:
                x.setFavorit(True,actualitza=False) #No actualitzem la base de dades perquè no estem modificant-la
        return botons

    def mostraMapes(self):
        '''Es recorre els botons laterals i, per cada un d'ells, mostra els mapes associats
        '''
        self.clearContingut()
        self.widsCataleg=[]
        self.nlayouts=[]

        for x in self.botonsLaterals:
            if x.isChecked():
                wid=QWidget()
                layout=QVBoxLayout()
                layout.setContentsMargins(0,0,0,0)
                lbl=QLabel(x.text())
                lbl.setStyleSheet('background: %s; padding: 2px;'%QvConstants.COLORGRISHTML)
                lbl.setFont(QFont('Arial',12))
                lbl.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)
                layout.addWidget(lbl)
                nlayout=QvRedimLayout()
                layout.addLayout(nlayout)
                # self.layoutCataleg.addLayout(layout)
                shaMostrat=False
                for y in self.catalegs[x.text()]:
                    if self.esMostra(y):
                        shaMostrat=True
                        nlayout.addWidget(y)
                wid.setLayout(layout)
                wid.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
                if shaMostrat:
                    self.layoutCataleg.addWidget(wid)
                    self.widsCataleg.append(wid)
                    self.nlayouts.append(nlayout)
        self.indexLayoutSeleccionat=-1
        # scrollArea=QScrollArea()
        # scrollArea.setWidget(self.wCataleg)
    def clearContingut(self):
        '''Oculta tot el contingut
        '''
        if hasattr(self,'widsCataleg'):
            for x in self.widsCataleg:
                # x.setParent(None)
                x.hide()
        return
    def obrirProjecte(self, dir: str, favorit: bool, widgetAssociat):
        '''Obre el projecte amb qVista. Li indica a qVista si és favorit o no, perquè pugui posar el botó com toca'''
        try:
            self.parent.obrirProjecteCataleg(dir, favorit, widgetAssociat)
            self.parent.show()
            # self.parent.activateWindow()
            # self.hide()
        except:
            QMessageBox.warning(self,"No s'ha pogut obrir el mapa","El mapa no ha pogut ser obert. Si el problema persisteix, contacteu amb el gestor del catàleg")
    def obrirEnQGis(self,dir: str):
        '''Obre el projecte amb QGis. El copia al directori temporal, per si l'usuari modifica alguna cosa'''
        #Copiem el projecte al directori temporal, per si l'usuari modifica alguna cosa
        shutil.copy2(dir,tempdir)
        copiat=tempdir+os.path.basename(dir)
        # QDesktopServices().openUrl(QUrl(copiat))
        while not os.path.exists(copiat):
            print('Copiant')
            sleep(1)
        os.startfile(copiat)
    def obrirInfo(self,dir: str):
        '''Mostra l'arxiu HTML que conté la informació associada al mapa'''
        if os.path.exists(dir):
            visor=QvVisorHTML(dir,'Informació mapa',parent=self)
            visor.exec()
        else:
            QMessageBox.warning(self,"No s'ha trobat la informació","La informació del mapa no ha pogut ser oberta. Si el problema persisteix, contacteu amb el gestor del catàleg")
    def mousePressEvent(self, event):
        self.esPotMoure=event.windowPos().y()<41 #La capçalera té mida 40. Si fem click a la capçalera, podem moure
        self.oldPos = event.globalPos()
    def mouseReleaseEvent(self,event):
        self.esPotMoure=False

    def mouseMoveEvent(self, event):
        if not self.esPotMoure: return
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
        '''Esc tanca.
        Amb les fletxes ens podem moure
        També ens podem moure amb les tecles HJKL, com al Vim
        El botó d'enter i de return obren el projecte seleccionat amb qVista ''' 
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key()==Qt.Key_Left or event.key()==Qt.Key_H:
            self.mouEsquerra()
        elif event.key()==Qt.Key_Down or event.key()==Qt.Key_J:
            self.mouBaix()
        elif event.key()==Qt.Key_Up or event.key()==Qt.Key_K:
            self.mouDalt()
        elif event.key()==Qt.Key_Right or event.key()==Qt.Key_L:
            self.mouDreta()
        elif event.key()==Qt.Key_Return or event.key()==Qt.Key_Enter:
            if hasattr(self,'widgetSeleccionat'):
                self.widgetSeleccionat.obreQVista()
    def seleccionaElement(self,widget, teclat=False):
        if widget is None: return
        for x, y in self.catalegs.items():
            for z in y:
                z.setChecked(False)
        widget.setChecked(True)
        if teclat: self.scroll.ensureWidgetVisible(widget)
        self.widgetSeleccionat=widget
        for x in range(0,len(self.nlayouts)):
            if self.nlayouts[x].indexOf(widget)!=-1:
                self.indexLayoutSeleccionat=x
                return
    def mouHoritzontal(self,despl: int):
        if self.indexLayoutSeleccionat!=-1:
            nlayout=self.nlayouts[self.indexLayoutSeleccionat]
            i, j = nlayout.indexsOf(self.widgetSeleccionat)
            j+=despl
            if j>=nlayout.x(i):
                j=0
                i+=1
                if i>=nlayout.y():
                    if self.indexLayoutSeleccionat+1<len(self.nlayouts):
                        i=0
                        j=0
                        nlayout=self.nlayouts[self.indexLayoutSeleccionat+1]
                    else:
                        i=nlayout.y()-1
                        j=nlayout.x(i)
            elif j<0:
                i-=1
                if i>=0:
                    j=nlayout.x(i)-1
                else:
                    if self.indexLayoutSeleccionat>0:
                        nlayout=self.nlayouts[self.indexLayoutSeleccionat-1]
                        i=nlayout.y()-1
                        j=nlayout.x(i)-1
                    #Agafem el layout anterior

            self.seleccionaElement(nlayout.widgetAt(i,j), True)
    def mouVertical(self,despl: int):
        if self.indexLayoutSeleccionat!=-1:
            nlayout=self.nlayouts[self.indexLayoutSeleccionat]
            i, j = nlayout.indexsOf(self.widgetSeleccionat)
            i+=despl
            if i>=nlayout.y():
                if len(self.nlayouts)>self.indexLayoutSeleccionat+1:
                    nlayout=self.nlayouts[self.indexLayoutSeleccionat+1]
                    i=0
                else:
                    j=0
            elif i<0:
                if self.indexLayoutSeleccionat-1>=0:
                    nlayout=self.nlayouts[self.indexLayoutSeleccionat-1]
                    i=nlayout.y()-1
                else:
                    j=nlayout.x(i)-1
            wid=nlayout.widgetAt(i,j)
            self.seleccionaElement(wid, True)
    def mouEsquerra(self):
        self.mouHoritzontal(-1)  
    def mouDreta(self):
        self.mouHoritzontal(+1)
    def mouDalt(self):
        self.mouVertical(-1)
    def mouBaix(self):
        self.mouVertical(1)
    def eventFilter(self,obj,event):
        '''Si premem una tecla quan tenim el focus en algun widget fill, ho gestionarem aquí abans de passar-li a ell'''
        if event.type()==QEvent.KeyPress:
            self.keyPressEvent(event)
        return False
    def arregla(self,txt: str):
        '''
        Arregla els textos per fer que siguin case insensitive, no tinguin en compte accents, no tinguin espais al principi ni al final i ignorin múltiples espais

        Primer de tot, canvia les lletres accentuades per lletres sense accentuar. Canvia també el · per . i elimina º i ª
        Aleshores passa totes les lletres a majúscules, per poder fer les comparacions case insensitive
        Després fa un strip que elimina espais al principi i al final
        Finalment substitueix els múltiples espais per un únic, utilitzant una expressió regular que cerca dos o més espais i els substitueix per un
        '''
        trans=str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöü·ºª.',
                            'AEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOU.   ')
        txt=txt.translate(trans)
        txt=txt.upper()
        txt=txt.strip(' ')
        txt=re.sub('\s[\s]+',' ',txt)

        return txt

    def filtra(self):
        txt=self.arregla(self.leCerca.text())
        if txt!='':
            self.clickTots()
            self.accioEsborra.setVisible(True)
        else:
            self.accioEsborra.setVisible(False)
        self.mostraMapes()

    def esMostra(self,widget):
        txt=self.arregla(self.leCerca.text())

        return txt in self.arregla(widget.titol) or txt in self.arregla(widget.text)


class BotoLateral(QPushButton):
    def __init__(self,text,cataleg,privat=False,parent=None):
        super().__init__(text,parent)
        self.setCursor(QvConstants.cursorClick())
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
        '''%(QvConstants.COLORFOSCHTML,QvConstants.COLORMIGHTML)
        self.setStyleSheet(stylesheet)
        self.setFont(QFont('Arial',12))
        self.privat=privat
    def mousePressEvent(self,event):
        if self==self.cataleg.tots:
            super().mousePressEvent(event)
            self.setChecked(False)
        elif self==self.cataleg.fav:
            super().mousePressEvent(event)
            self.setIcon(QIcon(imatgesDir+'star-blanc.png'))
            # self.setChecked(True)
        if event.modifiers()==Qt.ShiftModifier:
            #Multiselecció
            pass
        elif event.modifiers()==Qt.ControlModifier:
            #Seleccionar aquest botó mantenint els seleccionats
            self.setChecked(not self.isChecked())
        else:
            for x in self.cataleg.botonsLaterals:
                if x==self: continue
                x.setChecked(False)
            self.cataleg.tots.setChecked(False)
            if self!=self.cataleg.fav:
                self.cataleg.fav.setChecked(False)
            self.setChecked(True)
        self.cataleg.leCerca.setText('')
        self.cataleg.mostraMapes()
        if self!=self.cataleg.fav:
            self.cataleg.fav.setIcon(QIcon(imatgesDir+'star.png'))
    def setChecked(self,checked=True):
        super().setChecked(checked)
        if self.esPrivat():
            if checked:
                self.setIcon(QIcon(imatgesDir+'lock-clar.png'))
            else:
                self.setIcon(QIcon(imatgesDir+'lock-fosc.png'))
    def esPrivat(self):
        return self.privat

class MapaCataleg(QFrame):
    '''Widget que representa la preview del mapa
    Conté una imatge i un text
    Es pot seleccionar posant el ratolí a sobre, fent-hi click o amb el teclat
    Quan es selecciona apareixen quatre botons
    -Fav: Marca/desmarca el mapa com a favorit
    -Obrir amb qVista: Obre el mapa amb qVista. Cal, lògicament, haver obert el catàleg amb qVista
    -Obrir amb QGis: Obre el mapa amb QGis. Cal tenir-lo instal·lat
    -Info: Mostra la informació associada al mapa
    '''
    def __init__(self,dir: str, cataleg: QvNouCataleg=None): #Dir ha de contenir la ruta de l'arxiu (absoluta o relativa) i no només el seu nom. Ha de ser sense extensió
        super().__init__()
        self.setFrameStyle(QFrame.Panel)
        self.setCursor(QvConstants.cursorClick())
        self.checked=False
        self.cataleg=cataleg
        self.nomMapa=os.path.basename(dir) #Per tenir el nom per les bases de dades
        # midaWidget=QSize(300,241)
        midaWidget=QSize(320,274)
        self.setFixedSize(midaWidget)
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(6,0,6,0)
        self.layout.setSpacing(0)

        self.imatge=QPixmap(dir)
        self.lblImatge=QLabel()
        self.lblImatge.setPixmap(self.imatge)
        self.lblImatge.setFixedSize(300,180) #La mida que volem, restant-li el que ocuparà el border
        self.lblImatge.setScaledContents(True)
        self.lblImatge.setToolTip("Obrir mapa en qVista")
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
            self.titol=''
            self.text=''
            self.lblText=QLabel('<p><strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 10pt;">Títol no disponible<br /></span></strong><span style="color: #38474f; font-family: arial, helvetica, sans-serif; font-size: 8pt;">Descripció no disponible</span></p>')
            self.layout.addWidget(self.lblText)


        self.lblImatge.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self.lblText.setAlignment(Qt.AlignTop)
        self.lblText.setFixedHeight(66)
        self.lblText.setAlignment(Qt.AlignTop)

        stylesheet='''
            QPushButton{
                background: rgba(255,255,255,0.66); 
                margin: 0px; 
                padding: 0px;
                border: 0px;
            }
        '''
        self.favorit=False
        self.iconaFavDesmarcat=QIcon(imatgesDir+'cm_bookmark_off.png')
        self.iconaFavMarcat=QIcon(imatgesDir+'cm_bookmark_on.png')
        self.botoFav=QPushButton(parent=self)
        self.botoFav.setIcon(self.iconaFavDesmarcat)
        self.botoFav.move(280,16)
        self.botoFav.setIconSize(QSize(24,24))
        self.botoFav.setFixedSize(24,24)
        self.botoFav.setToolTip("Marcar/Desmarcar Favorit")
        self.botoFav.clicked.connect(self.switchFavorit)
        self.botoObre=QPushButton(parent=self)
        self.botoObre.setIcon(QIcon(imatgesDir+'cm_play.png'))
        self.botoObre.move(280,100)
        self.botoObre.setToolTip("Obrir el mapa en qVista")
        self.obreQVista=lambda: cataleg.obrirProjecte(dir+'.qgs',self.favorit, self)
        self.botoObre.clicked.connect(self.obreQVista)
        self.botoObre.setIconSize(QSize(24,24))
        self.botoObre.setFixedSize(24,24)
        self.botoQGis=QPushButton(parent=self)
        self.botoQGis.setIcon(QIcon(imatgesDir+'cm_qgis.png'))
        self.botoQGis.move(280,160)
        self.botoQGis.setIconSize(QSize(24,24))
        self.botoQGis.clicked.connect(lambda: cataleg.obrirEnQGis(dir+'.qgs'))
        self.botoQGis.setFixedSize(24,24)
        self.botoQGis.setToolTip("Obrir el mapa en QGis")
        self.botoInfo=QPushButton(parent=self)
        self.botoInfo.setIcon(QIcon(imatgesDir+'cm_info.png'))
        self.botoInfo.move(280,130)
        self.botoInfo.setIconSize(QSize(24,24))
        self.botoInfo.clicked.connect(lambda: cataleg.obrirInfo(dir+'.htm'))
        self.botoInfo.setFixedSize(24,24)
        self.botoInfo.setToolTip("Informació sobre el mapa")


        self.botoFav.setStyleSheet(stylesheet)
        self.botoObre.setStyleSheet(stylesheet)
        self.botoQGis.setStyleSheet(stylesheet)
        self.botoInfo.setStyleSheet(stylesheet)
        
        

        self.setChecked(False)
    def mousePressEvent(self,event):
        if event.buttons() & Qt.LeftButton:
            self.cataleg.seleccionaElement(self)
            # for x,y in self.cataleg.catalegs.items():
            #     for z in y:
            #         z.setChecked(False)
            # self.setChecked(True)
    def enterEvent(self,event):
        super().enterEvent(event)
        self.cataleg.seleccionaElement(self)
    def mouseDoubleClickEvent(self,event):
        self.obreQVista()
    def setChecked(self,checked: bool):
        self.checked=checked
        if checked:
            self.setStyleSheet('MapaCataleg{border: 4px solid %s;}'%QvConstants.COLORCLARHTML)
            # QvConstants.afegeixOmbraWidgetSeleccionat(self)
            self.botoFav.show()
            self.botoObre.show()
            self.botoInfo.show()
            self.botoQGis.show()
            
            
        else:
            # self.setGraphicsEffect(None)
            self.setStyleSheet('MapaCataleg{border: 4px solid white;}')
            self.botoFav.hide()
            self.botoObre.hide()
            self.botoQGis.hide()
            self.botoInfo.hide()
        self.update()
    def setFavorit(self,fav: bool,actualitza: bool=True):
        if fav:
            if actualitza:
                #Si no podem afegir-lo com a favorit, retornem
                if not QvFavorits().afegeixFavorit(self.getNomMapa()):
                    return
            self.botoFav.setIcon(self.iconaFavMarcat)
        else:
            if actualitza:
                if not QvFavorits().eliminaFavorit(self.getNomMapa()):
                    return
            self.botoFav.setIcon(self.iconaFavDesmarcat)
        self.favorit=fav
        if hasattr(self.cataleg.parent,'widgetAssociat') and self.cataleg.parent.widgetAssociat==self:
            self.cataleg.parent.actualitzaBotoFav(fav)
    def esFavorit(self):
        return self.favorit
    def switchFavorit(self):
        self.setFavorit(not self.favorit)
    def getNomMapa(self):
        return self.nomMapa
            


if __name__ == "__main__":
    with qgisapp() as app:
        app.setStyleSheet(open('style.qss').read())
        cataleg = QvNouCataleg()
        cataleg.showMaximized()
        # mapa=MapaCataleg("N:/9SITEB/Publicacions/qVista/CATALEG/Mapes - en preparació per XLG/2. Ortofotos/Imatge de satel·lit 2011 de l'AMB")
        # mapa.show()