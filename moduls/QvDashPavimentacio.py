from dashPavimentacio import Ui_DashPavimentacio
from importaciones import *
from moduls import *

class QvDashPavimentacio(QFrame, Ui_DashPavimentacio):
    def __init__(self, qv = None):
        QFrame.__init__(self)
        self.setupUi(self)
        if qv is not None:
            self.layout = QHBoxLayout(self.frameCanvas)
            self.frameCanvas.setLayout(self.layout)
            self.layout.addWidget(qv.canvas)
            qv.canvas.show()
            miMenu = qv.bar.addMenu ("Funcions específiques d'entorn")
            


if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        dash = QvDashPavimentacio()
        dash.show()