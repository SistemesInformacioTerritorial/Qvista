from moduls.QvConstants import QvConstants
from moduls.QvImports import * 


class QvToolButton(QToolButton):
    '''Classe senzilla per implementar enterEvent i leaveEvent del QToolButton, per fer que el ratolí canviï quan es pugui fer click'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheetDefault='''
            background-color: transparent;
            color: #38474F;
            border: 2px;
            padding: 2px 2px;
            margin: 0px;
        '''
        self.stylesheetMarcat='''
            border: 2px solid %s;
            padding: 0px 0px;
            margin: 0px;
        '''%QvConstants.COLORDESTACATHTML
        self.setStyleSheet(self.stylesheetDefault)
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())
    def setMarcat(self,marcat):
        if marcat:
            self.setStyleSheet(self.stylesheetMarcat)
        else:
            self.setStyleSheet(self.stylesheetDefault)