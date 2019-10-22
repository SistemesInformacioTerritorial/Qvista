from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer

class QvBafarada(QLabel):
    def __init__(self,text,parent=None):
        super().__init__(text)
        self.parent=parent
        # self.setWindowFlags(Qt.Window | Qt.WA_TranslucentBackground | Qt.FramelessWindowHint)
    def paintEvent(self,event):
        super().paintEvent(event)
    def show(self):
        super().show()
        self.move(self.parent.pos().x(),self.parent.pos().y()+10)
        self.timer=QTimer()
        self.timer.start(5000)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.oculta)
    def oculta(self):
        self.hide()
        self.timer.stop()