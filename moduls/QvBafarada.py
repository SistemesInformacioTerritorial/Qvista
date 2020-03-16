from qgis.PyQt.QtWidgets import QLabel
from qgis.PyQt.QtCore import QTimer, Qt
from moduls.QvConstants import QvConstants

class QvBafarada(QLabel):
    '''
    Mostra un text simulant una bafarada (globus) de còmic en una posició relativa al widget pare (TOPLEFT, TOPRIGHT, BOTTOMLEFT o BOTTOMRIGHT)
    Si no s'especifica pare, es mostrarà on li sembli, així que seria convenient fer-li un move a la posició que es vulgui
    La bafarada es mostra fent-li un show, i s'oculta per si sola, sense necessitat de fer res. 
    '''
    TOPLEFT=0
    TOPRIGHT=1
    BOTTOMLEFT=2
    BOTTOMRIGHT=3
    def __init__(self,text,parent=None, pos=BOTTOMRIGHT, temps=5):
        super().__init__(text)
        self.parent=parent
        self.setFont(QvConstants.FONTTEXT)
        self.setWordWrap(True)
        self.pos=pos
        self.temps=temps
        self.setStyleSheet('''
            background: %s;
            color: %s;
            padding: 2px;
            border: 2px solid %s;
            border-radius: 10px;
            margin: 0px;
        '''%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML, QvConstants.COLORDESTACATHTML))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.Window | Qt.WA_TranslucentBackground | Qt.FramelessWindowHint)
    def paintEvent(self,event):
        super().paintEvent(event)
    def show(self):
        super().show()
        self.timer=QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.hide())
        self.timer.start(self.temps*1000)
        # self.show()
        if self.parent is not None:
            #Ja que python no té switch-case, ho fem amb una llista
            pos=[(10,10),(self.parent.width()-self.width()-10,10),(10,self.parent.height()-self.height()-10),(self.parent.width()-self.width()-10,self.parent.height()-self.height()-10)][self.pos]
            self.move(*pos)
    def oculta(self):
        self.hide()
        self.timer.stop()