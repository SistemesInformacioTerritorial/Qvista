from moduls.QvConstants import QvConstants
from moduls.QvImports import * 


class QvToolButton(QToolButton):
    '''Classe senzilla per implementar enterEvent i leaveEvent del QToolButton, per fer que el ratolí canviï quan es pugui fer click'''
    stylesheetDefault='''
        QvToolButton{
            background-color: transparent;
            color: #38474F;
            border: 2px;
            padding: 2px 2px;
            margin: 0px;
        }
        QToolTip{
            color: #38474F;
            background-color: #F0F0F0;
        }
    '''
    stylesheetMarcat='''
        QvToolButton{
            border: 2px solid %s;
            padding: 0px 0px;
            margin: 0px;
        }
        QToolTip{
            color: #38474F;
            background-color: #F0F0F0;
        }
    '''%QvConstants.COLORDESTACATHTML
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.setStyleSheet(QvToolButton.stylesheetDefault)
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())
    def setMarcat(self,marcat: bool):
        if marcat:
            self.setStyleSheet(QvToolButton.stylesheetMarcat)
        else:
            self.setStyleSheet(QvToolButton.stylesheetDefault)
    def getStyleSheet():
        return QvToolButton.stylesheetDefault