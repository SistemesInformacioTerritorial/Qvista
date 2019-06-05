from moduls.QvImports import *
class QvMenuBar(QMenuBar):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMouseTracking(False)
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parentWidget().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.parentWidget().mouseMoveEvent(event)
    def mouseDoubleClickEvent(self,event):
        super().mouseDoubleClickEvent(event)
        self.parentWidget().mouseDoubleClickEvent(event)