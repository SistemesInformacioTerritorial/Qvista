from moduls.QvConstants import QvConstants
from moduls.QvImports import * 


class QvToolButton(QToolButton):
    '''Classe senzilla per implementar enterEvent i leaveEvent del QToolButton, per fer que el ratolí canviï quan es pugui fer click'''
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())