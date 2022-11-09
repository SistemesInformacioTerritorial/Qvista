from qgis.PyQt.QtCore import QPoint, QRect, Qt, pyqtSignal
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QMenuBar, QWidget

from moduls.QvConstants import QvConstants


class QvMenuBar(QMenuBar):
    '''
    Classe per fer que la menubar del qVista faci arrossegable el programa
    Per extensió, permetria fer que qualsevol QMainWindow frameless ho sigui
    '''

    desplaca=pyqtSignal(float,float)
    posCanviada=pyqtSignal(QPoint)
    restaura=pyqtSignal()
    def __init__(self,parent: QWidget=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.menus=[]
        self.podemMoure=False
    def underMouse(self):
        pos=QCursor.pos()
        for x in self.menus:
            rect=x.rect()
            leftTop=x.mapToGlobal(QPoint(rect.left(),rect.top()))
            rightBottom=x.mapToGlobal(QPoint(rect.right(),rect.bottom()))
            globalRect=QRect(leftTop.x(),leftTop.y(),rightBottom.x(),rightBottom.y())
            if globalRect.contains(pos):
                return True
        return False
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button()==Qt.LeftButton:
            self.posCanviada.emit(event.globalPos())
            self.podemMoure=not self.underMouse()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.LeftButton:
            if not self.podemMoure: return
            self.desplaca.emit(event.globalPos().x(),event.globalPos().y())
            self.posCanviada.emit(event.globalPos())
            
    def mouseDoubleClickEvent(self,event):
        super().mouseDoubleClickEvent(event)
        if event.button()==Qt.LeftButton:
            self.restaura.emit()
    def enterEvent(self,event):
        super().enterEvent(event)
        self.setCursor(QvConstants.cursorClick())
    def leaveEvent(self,event):
        super().leaveEvent(event)
        self.setCursor(QvConstants.cursorFletxa())
    def addMenu(self,*args):
        self.menus.append(super().addMenu(*args))
        return self.menus[-1]