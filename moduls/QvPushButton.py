from moduls.QvImports import * 
from moduls.QvConstants import QvConstants

class QvPushButton(QPushButton):
    def __init__(self, icon, text, destacat=False, parent=None):
        QPushButton.__init__(self,icon,text,parent)
        self.setDestacat(destacat)
    def __init__(self, text='', destacat=False, parent=None):
        QPushButton.__init__(self,text,parent)
        self.setDestacat(destacat)
    def formata(self,destacat):
        if self.isEnabled():
            if destacat:
                colors=(QvConstants.COLORBLANC,QvConstants.COLORDESTACAT)
            else:
                colors=(QvConstants.COLORBLANC,QvConstants.COLORFOSC)
        else:
            colors=(QvConstants.COLORCLAR,QvConstants.COLORGRIS)
        self.setStyleSheet(
            "margin: 20px;"
            "border: none;"
            "padding: 5px 20px;"
            "color: %s;"
            "background-color: %s" % colors)
        self.setGraphicsEffect(QvConstants.ombraWidget())
        self.setFont(QvConstants.FONTTEXT)
    def setDestacat(self,destacat):
        self.destacat=destacat
        self.formata(destacat)
    def setEnabled(self,enabled):
        super().setEnabled(enabled)
        self.formata(self.destacat)
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)