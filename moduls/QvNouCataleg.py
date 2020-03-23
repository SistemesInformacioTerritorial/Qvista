#!/usr/bin/env python
from moduls.QvImports import * 
from qgis.PyQt import QtWidgets
import os
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvRedimLayout import QvRedimLayout
import shutil
from moduls.QvVisorHTML import QvVisorHTML
import re
from moduls.QvFavorits import QvFavorits
from moduls.QvMemoria import QvMemoria


class QvNouCataleg(QWidget):
    # Senyal per obrir un projecte. Passa un string (ruta de l'arxiu), un booleà (si aquell era favorit o no) i un widget (el botó al qual s'ha fet click). 
    # El segon i el tercer només calen si volem poder gestionar els favorits des de fora del catàleg
    obrirProjecte = pyqtSignal(str, bool, QWidget)
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
        for y in carpetaCatalegProjectesLlista+QvMemoria().getCatalegsLocals():
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
                local = y in QvMemoria().getCatalegsLocals()
                boto=BotoLateral(x,self,privat,local)
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
        for y in carpetaCatalegProjectesLlista+QvMemoria().getCatalegsLocals():
            try:
                _,_,files=next(os.walk(y+'/'+dir))
                files=(x[:-4] for x in files if x.endswith('.qgs'))
                files=(os.path.join(y,dir,x) for x in files)
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
    def obreProjecte(self, dir: str, favorit: bool, widgetAssociat):
        '''Obre el projecte amb qVista. Li indica a qVista si és favorit o no, perquè pugui posar el botó com toca'''
        try:
            # self.parent.obrirProjecteCataleg(dir, favorit, widgetAssociat)
            self.obrirProjecte.emit(dir,favorit,widgetAssociat)
            if self.parent is not None:
                self.parent.show()
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
        txt=re.sub(r'\s[\s]+',' ',txt)

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
    def __init__(self,text,cataleg,privat=False, local=False,parent=None):
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
        self.local=local
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
        elif self.esLocal():
            if checked:
                self.setIcon(QIcon(imatgesDir+'harddisk-clar.png'))
            else:
                self.setIcon(QIcon(imatgesDir+'harddisk-fosc.png'))
    def esPrivat(self):
        return self.privat
    def esLocal(self):
        return self.local

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
        self.obreQVista=lambda: cataleg.obreProjecte(dir+'.qgs',self.favorit, self)
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

class PointTool(QgsMapTool):
    click=pyqtSignal(QgsPointXY)
    def __init__(self, parent, canvas):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent

    
    # def canvasMoveEvent(self, event):
    #     self.parent.dockX = event.pos().x()
    #     self.parent.dockY = event.pos().y()

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.click.emit(point)

plantillaMetadades='''<html>
<head>
<meta http-equiv=Content-Type content="text/html; charset=windows-1252">
<meta name=Generator content="Microsoft Word 14 (filtered)">
<style>
<!--
 /* Font Definitions */
 @font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
 /* Style Definitions */
 p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:0cm;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
a:link, span.MsoHyperlink
	{font-family:"Times New Roman","serif";
	color:blue;
	text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
	{color:purple;
	text-decoration:underline;}
p.MsoListParagraph, li.MsoListParagraph, div.MsoListParagraph
	{margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:36.0pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxspfirst, li.msolistparagraphcxspfirst, div.msolistparagraphcxspfirst
	{mso-style-name:msolistparagraphcxspfirst;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:0cm;
	margin-left:36.0pt;
	margin-bottom:.0001pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxspmiddle, li.msolistparagraphcxspmiddle, div.msolistparagraphcxspmiddle
	{mso-style-name:msolistparagraphcxspmiddle;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:0cm;
	margin-left:36.0pt;
	margin-bottom:.0001pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msolistparagraphcxsplast, li.msolistparagraphcxsplast, div.msolistparagraphcxsplast
	{mso-style-name:msolistparagraphcxsplast;
	margin-top:0cm;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:36.0pt;
	line-height:115%%;
	font-size:11.0pt;
	font-family:"Calibri","sans-serif";}
p.msochpdefault, li.msochpdefault, div.msochpdefault
	{mso-style-name:msochpdefault;
	margin-right:0cm;
	margin-left:0cm;
	font-size:12.0pt;
	font-family:"Calibri","sans-serif";}
p.msopapdefault, li.msopapdefault, div.msopapdefault
	{mso-style-name:msopapdefault;
	margin-right:0cm;
	margin-bottom:10.0pt;
	margin-left:0cm;
	line-height:115%%;
	font-size:12.0pt;
	font-family:"Times New Roman","serif";}
.MsoChpDefault
	{font-size:10.0pt;
	font-family:"Calibri","sans-serif";}
.MsoPapDefault
	{margin-bottom:10.0pt;
	line-height:115%%;}
@page WordSection1
	{size:595.3pt 841.9pt;
	margin:70.85pt 3.0cm 70.85pt 3.0cm;}
div.WordSection1
	{page:WordSection1;}
-->
</style>

</head>

<body lang=CA link=blue vlink=purple>

<div class=WordSection1>

<p class=MsoNormal><b><span style='font-family:"Arial","sans-serif";color:#595959'>%s</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Contingut</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Propietari</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><b><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>Font de les dades</span></b></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>%s </span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

<p class=MsoNormal style='margin-bottom:0cm;margin-bottom:.0001pt'><span
style='font-size:9.0pt;line-height:115%%;font-family:"Arial","sans-serif";
color:#595959'>&nbsp;</span></p>

</div>

</body>

</html>'''

class QvCreadorCataleg(QDialog):
    def __init__(self, canvas, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Afegir mapa al catàleg')
        self._project=project
        self._canvas=canvas
        self._canvas.xyCoordinates.connect(self._mouMouse)
        self._tool=PointTool(self,self._canvas)
        self._tool.click.connect(self.puntClick)
        self._toolSet=False
        # self._canvas.setMapTool(self._tool)
        self.incX=300
        self.incY=180
        self._layer = QgsVectorLayer('Point?crs=epsg:25831', "Capa temporal d'impressió","memory")
        project.addMapLayer(self._layer, False)


        # self._pucMoure=False
        self._lay=QVBoxLayout()
        self.setLayout(self._lay)
        lblCapcalera=QLabel('Afegir mapa al catàleg')
        lblCapcalera.setFont(QvConstants.FONTTITOLS)
        self._lay.addWidget(lblCapcalera)
        
        

        layTitCat=QVBoxLayout()
        frameTitCat=self.getFrame(layTitCat)
        self._lay.addWidget(frameTitCat)

        layTitol=QHBoxLayout()
        layTitCat.addLayout(layTitol)
        layTitol.addWidget(QLabel('Títol: ',self))
        self._leTitol=QLineEdit(self)
        self._leTitol.textChanged.connect(self.actualitzaEstatBDesar)
        self._leTitol.setPlaceholderText('Títol que es visualitzarà al catàleg')
        layTitol.addWidget(self._leTitol)
        # self._lay.addLayout(layTitol)

        lblText=QLabel('Descripció:')
        layTitCat.addWidget(lblText)
        self._teText=QTextEdit(self)
        self._teText.setPlaceholderText('Descripció del projecte que es visualitzarà al catàleg.\nIntenteu no sobrepassar els 150 caràcters, ja que el text es podria veure tallat')
        self._teText.textChanged.connect(self.actualitzaEstatBDesar)
        layTitCat.addWidget(self._teText)
        # self._lay.addWidget(frameDescripcio)

        
        self._layImatge=QVBoxLayout()
        frameImatge=self.getFrame(self._layImatge)
        self._layImatge.addWidget(QLabel('Vista prèvia escollida:'))
        self._imatge=QWidget()
        self._imatge.setFixedSize(self.incX,self.incY)
        self._layImatge.addWidget(self._imatge)
        self._lay.addWidget(frameImatge)

        layCat=QVBoxLayout()
        frameCat=self.getFrame(layCat)
        self._lay.addWidget(frameCat)
        lblCatalegs=QLabel('Trieu el catàleg on desarem el resultat')
        self._cbCatalegs=QComboBox()
        self._cbCatalegs.addItems(QvMemoria().getCatalegsLocals())
        self._cbCatalegs.addItem('Un altre catàleg')
        self._cbCatalegs.activated.connect(self._cbCatalegsCanviat)
        layCat.addWidget(lblCatalegs)
        layCat.addWidget(self._cbCatalegs)

        lblSubcarpeta=QLabel('Trieu la categoria on desarem el resultat')
        self._cbSubcarpetes=QComboBox()
        self._cbSubcarpetes.currentIndexChanged.connect(self._cbSubCarpetesCanviat)
        self._leNovaCat=QLineEdit()
        self._populaSubCarpetes()
        self._leNovaCat.setPlaceholderText('Nom de la nova categoria')
        self._leNovaCat.textChanged.connect(self.actualitzaEstatBDesar)
        layCat.addWidget(lblSubcarpeta)
        layCat.addWidget(self._cbSubcarpetes)
        layCat.addWidget(self._leNovaCat)
        self._cbSubCarpetesCanviat(0)


        layBotons=QHBoxLayout()
        self._bGenerarImatge=QvPushButton('Capturar vista prèvia')
        self._bGenerarImatge.clicked.connect(self._swapCapturar)
        self._bDesar=QvPushButton('Desar',destacat=True)
        self._bDesar.clicked.connect(self._desar)
        layBotons.addWidget(self._bGenerarImatge)
        layBotons.addWidget(self._bDesar)
        self._lay.addLayout(layBotons)

        self._rubberband = QgsRubberBand(self._canvas)
        self._rubberband.setColor(QvConstants.COLORDESTACAT)
        self._rubberband.setWidth(2)
        self.pintarRectangle(self._canvas.extent())
        self._rubberband.hide()

        self.actualitzaEstatBDesar()
    def getFrame(self,l):
        f=QFrame(self)
        f.setLayout(l)
        f.setFrameStyle(QFrame.Box)
        return f
    def _cbCatalegsCanviat(self,i):
        catalegsLocals=QvMemoria().getCatalegsLocals()
        if not os.path.exists(self._cbCatalegs.currentText()):
            ret=QFileDialog.getExistingDirectory(self,'Trieu la carpeta del catàleg',QvMemoria().getDirectoriDesar())
            if ret=='':
                self._cbCatalegs.setCurrentIndex(0)
                return
            if ret in carpetaCatalegProjectesLlista:
                r=QMessageBox.question(self,'Heu triat un catàleg compartit','La carpeta que heu triat és un catàleg compartit. Esteu segur que voleu i podeu modificar-lo?', QMessageBox.Yes, QMessageBox.No)
                if r==QMessageBox.No:
                    self._cbCatalegs.setCurrentIndex(0)
                    return
            elif ret not in catalegsLocals:
                #Aquí preguntar si vol desar-ho com a catàleg local
                resp=QMessageBox.question(self,'Afegir el catàleg','Voleu convertir aquesta carpeta en un catàleg de mapes local?', QMessageBox.Yes, QMessageBox.No)
                if resp==QMessageBox.Yes:
                    QvMemoria().setCatalegLocal(ret)
                self._cbCatalegs.insertItem(i,ret)
                self._cbCatalegs.setCurrentIndex(i)
                self._populaSubCarpetes()
    def _cbSubCarpetesCanviat(self,i):
        print(i)
        print(self._cbSubcarpetes.count()-1)
        if i==self._cbSubcarpetes.count()-1:
            self._leNovaCat.show()
        else:
            self._leNovaCat.hide()
    def _populaSubCarpetes(self):
        root, dirs, _ = next(os.walk(self._cbCatalegs.currentText()))
        if len(dirs)==0:
            # Avisar de que hauran de crear algun directori
            pass
        self._cbSubcarpetes.clear()
        self._cbSubcarpetes.addItems(dirs)
        self._cbSubcarpetes.addItem('Una nova categoria')
        pass
        # self._cbSubcarpetes
    def _desar(self):
        # catalegsLocals=QvMemoria().getCatalegsLocals()
        # ret=QFileDialog.getExistingDirectory(self,'Trieu la carpeta del catàleg',catalegsLocals[0])
        # if ret=='':
        #     return
        # if ret not in catalegsLocals:
        #     #Aquí preguntar si vol desar-ho com a catàleg local
        #     print(':D')
        if self._leNovaCat.isVisible():
            cat=self._leNovaCat.text()
            ret=os.path.join(self._cbCatalegs.currentText(),cat)
            os.mkdir(ret)
        else:
            ret=os.path.join(self._cbCatalegs.currentText(),self._cbSubcarpetes.currentText())
        nom=self._project.baseName()
        fRes=os.path.join(ret,nom)
        # os.mkdir(fRes)
        # fRes=os.path.join(fRes,nom)
        #desar mapa
        if os.path.isfile(fRes+'.txt'):
            r=QMessageBox.question(self,'Aquest projecte ja existeix','Aquest projecte ja existeix. Voleu substituir-lo?',QMessageBox.Yes,QMessageBox.No)
            if r==QMessageBox.No: return
        with open(fRes+'.txt','w') as f:
            f.write(self._leTitol.text()+'\n')
            f.write(self._teText.toPlainText())
        self._project.write(fRes+'.qgs')
        self._pixmap.save(fRes+'.png')

        wid=QDialog()
        lay=QVBoxLayout()
        wid.setLayout(lay)
        titol=QLabel('Introduïu les metadades associades al projecte')
        titol.setFont(QvConstants.FONTTITOLS)
        lay.addWidget(titol)

        layCont=QVBoxLayout()
        frameCont=self.getFrame(layCont)
        layCont.addWidget(QLabel('Contingut:'))
        teContingut=QTextEdit()
        layCont.addWidget(teContingut)
        lay.addWidget(frameCont)

        layProp=QVBoxLayout()
        frameProp=self.getFrame(layProp)
        layProp.addWidget(QLabel('Propietari:'))
        tePropietari=QTextEdit()
        layProp.addWidget(tePropietari)
        lay.addWidget(frameProp)

        layFont=QVBoxLayout()
        frameFont=self.getFrame(layFont)
        layFont.addWidget(QLabel('Font de les dades:'))
        teFont=QTextEdit()
        layFont.addWidget(teFont)
        lay.addWidget(frameFont)

        bDesar=QvPushButton('Desar',destacat=True)
        lay.addWidget(bDesar,alignment=QtCore.Qt.AlignRight)
        def desarMetadades():
            with open(fRes+'.htm','w') as f:
                cont=teContingut.toPlainText().replace('\n','<br>')
                prop=tePropietari.toPlainText().replace('\n','<br>')
                font=teFont.toPlainText().replace('\n','<br>')
                f.write(plantillaMetadades%(self._leTitol.text(),cont,prop,font))

            wid.close()
        bDesar.clicked.connect(desarMetadades)
        wid.exec()
        self.close()
        
    def _swapCapturar(self):
        if self._toolSet:
            self._bGenerarImatge.setText('Capturar imatge')
            self._canvas.unsetMapTool(self._tool)
            pass
        else:
            self._bGenerarImatge.setText('Desplaçar mapa')
            self._canvas.setMapTool(self._tool)
            pass
        self._toolSet=not self._toolSet
    def actualitzaEstatBDesar(self):
        b=isinstance(self._imatge,QLabel) and self._leTitol.text()!='' and self._teText.toPlainText()!=''
        if not b:
            self._bDesar.setEnabled(False)
            return

        if self._cbSubcarpetes.currentIndex()<self._cbSubcarpetes.count()-1:
            self._bDesar.setEnabled(True)
        else:
            self._bDesar.setEnabled(self._leNovaCat.text()!='')
    def puntClick(self,p):
        self._p=p
        self.imprimirPlanol(p.x(),p.y(),self._canvas.scale(),self._canvas.rotation())
        
    def _mouMouse(self,p):
        if not self.isVisible() or not self._toolSet:
            self._rubberband.hide()
        else:
            # p=self._canvas.mapToGlobal(p)
            p=self._canvas.mapFromGlobal(QCursor.pos())
            points=[QgsPoint(self._canvas.getCoordinateTransform().toMapCoordinates(*x)) for x in ((p.x()+self.incX,p.y()+self.incY), (p.x()+self.incX,p.y()), (p.x(),p.y()), (p.x(),p.y()+self.incY), (p.x()+self.incX,p.y()+self.incY))]
            self._requadre=QgsGeometry.fromPolyline(points)
            self._rubberband.setToGeometry(self._requadre,self._layer)
            self._rubberband.show()

    def pintarRectangle(self,poligon):
        points=[QgsPointXY(0,0),QgsPointXY(0,10),QgsPointXY(10,10),QgsPointXY(0,10),QgsPointXY(0,0)]
        poligono=QgsGeometry.fromRect(poligon)
        self._rubberband.setToGeometry(poligono,self._layer)
    def imprimirPlanol(self,x, y, escala, rotacion):
        #Preguntar on desem
        #Crear document de text
        #Crear metadades

        image_location = os.path.join(tempdir, "render.png")

        options = QgsMapSettings()
        options.setLayers(self._canvas.layers())
        options.setBackgroundColor(QColor(255, 255, 255))
        options.setOutputSize(QSize(300, 180))
        options.setExtent(self._rubberband.asGeometry().boundingBox())

        render = QgsMapRendererParallelJob(options)

        def finished():
            # global render
            try:
                render
            except Exception as e:
                print(e)
                import time
                time.sleep(0.5)
                finished()
            img = render.renderedImage()
            # save the image; e.g. img.save("/Users/myuser/render.png","png")
            img.save(image_location, "png")
            print("saved")
            self._pixmap=QPixmap(image_location)
            lblImatge=QLabel()
            lblImatge.setPixmap(self._pixmap)
            self._layImatge.replaceWidget(self._imatge,lblImatge)
            self._imatge=lblImatge
            self.actualitzaEstatBDesar()

        render.finished.connect(finished)

        render.start()
    def hideEvent(self,e):
        super().hideEvent(e)
        if self._toolSet:
            self._canvas.unsetMapTool(self._tool)
        

if __name__ == "__main__":
    from configuracioQvista import *
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        with open('style.qss') as f:
            app.setStyleSheet(f.read())
        canvas = QvCanvas(llistaBotons=["panning","zoomIn","zoomOut","streetview"])
        canvas.show()
        atributs = QvAtributs(canvas)
        projecte = QgsProject.instance()
        root = projecte.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root,canvas)
        projecte.read(projecteInicial)
        llegenda = QvLlegenda(canvas, atributs)
        llegenda.show()
        cataleg = QvNouCataleg()
        cataleg.showMaximized()
        cataleg.obrirProjecte.connect(lambda x: projecte.read(x))
        creador=QvCreadorCataleg(canvas, projecte)
        creador.show()
        # mapa=MapaCataleg("N:/9SITEB/Publicacions/qVista/CATALEG/Mapes - en preparació per XLG/2. Ortofotos/Imatge de satel·lit 2011 de l'AMB")
        # mapa.show()
