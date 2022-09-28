
from qgis.PyQt.QtCore import QMimeData, Qt
from qgis.PyQt.QtGui import QDrag, QIcon
from qgis.PyQt.QtWidgets import QPushButton, QSizePolicy, QWidget

from moduls.QvConstants import QvConstants


#Classe per crear botons amb l'estil qVista
#Un botó qVista pot ser de tres tipus:
#Pot ser pla. En aquest cas serà com si fos una label, però s'hi pot fer click a sobre. Té el fons transparent i quan poses el ratolí a sobre es posa una mà
#Si no és pla, pot ser destacat o no ser-ho. En aquest cas canvia el color
#En ambdós casos té estil Material Design i una ombra. El destacat té el color destacat, i el normal el color fosc
#NOTA: S'haurien de canviar tots els QPushButton del programa per QvPushButton, amb l'estil que decidim
class QvPushButton(QPushButton):
    def __init__(self, icon: QIcon=None, text: str='', destacat: bool=False, discret=False, flat: bool=False, parent: QWidget=None):
        '''Crea un botó amb icona
        Arguments:
            icon{QIcon} -- Icona del botó
            text{str} -- Text del botó
        Keyword Arguments:
            destacat{bool} -- True si volem que el botó tingui el color destacat, fals si volem que sigui el color per defecte
            parent{QWidget} -- El pare del botó
        '''
        QPushButton.__init__(self,icon,text,parent)
        self.flat=flat
        self.setDestacat(destacat)
        self.setDiscret(discret)
        self.setDragable(False)
        # self.icona=icon
    def __init__(self, text: str='', destacat: bool=False, discret=False, flat: bool=False, parent: QWidget=None):
        '''Crea un botó sense icona
        Arguments:
            icon{QIcon} -- Icona del botó
            text{str} -- Text del botó
        Keyword Arguments:
            destacat{bool} -- True si volem que el botó tingui el color destacat, fals si volem que sigui el color per defecte
            parent{QWidget} -- El pare del botó
        '''
        super().__init__(text,parent)
        self.flat=flat
        self.setDestacat(destacat)
        self.setDiscret(discret)
        self.setDragable(False)

    def formata(self,destacat: bool, discret: bool):
        if self.flat: return
        if self.isEnabled():
            if destacat:
                colors=(QvConstants.COLORBLANCHTML,QvConstants.COLORDESTACATHTML)
            else:
                if discret:
                    colors=(QvConstants.COLORBLANCHTML,QvConstants.COLORCLARHTML)
                else:
                    colors=(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML)
        else:
            colors=(QvConstants.COLORCLARHTML,QvConstants.COLORGRISHTML)
        self.setStyleSheet(
            # "margin-right: 20px;"
            # "margin-top: 10px;"
            # "margin-bottom: 10px;"
            "border: none;"
            "padding: 5px 20px;"
            "color: %s;"
            "background-color: %s" % colors)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        QvConstants.afegeixOmbraWidget(self)
    def setDestacat(self,destacat: bool):
        self.destacat=destacat
        self.formata(destacat,False)
    def setDiscret(self,discret: bool):
        self.discret=discret
        self.formata(False,discret)

    def setEnabled(self,enabled: bool):
        super().setEnabled(enabled)
        self.formata(self.destacat,self.discret)
    def enterEvent(self,event):
        super().enterEvent(event)
        if not self.isEnabled(): return
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())
    def showEvent(self,event):
        super().showEvent(event)
        self.formata(self.destacat,self.discret)

    def setDragable(self,drag=True):
        self.drag=drag

    def mouseMoveEvent(self,e):
        '''Arrosseguem el botó. Per exemple, per emular el funcionament de la Google Street View
        '''
        if not self.drag:
            return

        #Ens guardem la icona i posem una icona buida al botó
        self.icona=self.icon()
        self.setIcon(QIcon())

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(self.icona.pixmap(self.size())) #Posem a l'arrossegament la mateixa icona del botó
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        drag.exec_(Qt.MoveAction)
        self.setIcon(self.icona) #Restablim la icona


    def mousePressEvent(self, e):
        #Podríem utilitzar-ho per controlar coses. De moment no ho fem
        super().mousePressEvent(e)




