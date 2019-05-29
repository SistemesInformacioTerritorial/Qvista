from moduls.QvImports import * 
from moduls.QvConstants import QvConstants



#Classe per crear botons amb l'estil qVista
class QvPushButton(QPushButton):
    def __init__(self, icon: QIcon=None, text: str='', destacat: bool=False, parent: QWidget=None):
        '''Crea un botó amb icona
        Arguments:
            icon{QIcon} -- Icona del botó
            text{str} -- Text del botó
        Keyword Arguments:
            destacat{bool} -- True si volem que el botó tingui el color destacat, fals si volem que sigui el color per defecte
            parent{QWidget} -- El pare del botó
        '''
        QPushButton.__init__(self,icon,text,parent)
        self.setDestacat(destacat)
    def __init__(self, text: str='', destacat: bool=False, parent: QWidget=None):
        '''Crea un botó sense icona
        Arguments:
            icon{QIcon} -- Icona del botó
            text{str} -- Text del botó
        Keyword Arguments:
            destacat{bool} -- True si volem que el botó tingui el color destacat, fals si volem que sigui el color per defecte
            parent{QWidget} -- El pare del botó
        '''
        super().__init__(text,parent)
        self.setDestacat(destacat)
    
    def formata(self,destacat: bool):
        if self.isEnabled():
            if destacat:
                colors=(QvConstants.COLORBLANCHTML,QvConstants.COLORDESTACATHTML)
            else:
                colors=(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML)
        else:
            colors=(QvConstants.COLORCLARHTML,QvConstants.COLORGRISHTML)
        self.setStyleSheet(
            "margin: 10px;"
            "border: none;"
            "padding: 5px 20px;"
            "color: %s;"
            "background-color: %s" % colors)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        QvConstants.afegeixOmbraWidget(self)
        self.setFont(QvConstants.FONTTEXT)
    def setDestacat(self,destacat: bool):
        self.destacat=destacat
        self.formata(destacat)
    def setEnabled(self,enabled: bool):
        super().setEnabled(enabled)
        self.formata(self.destacat)
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)
    def showEvent(self,event):
        super().showEvent(event)
        self.formata(self.destacat)