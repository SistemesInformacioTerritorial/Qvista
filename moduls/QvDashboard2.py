from dashboard2 import Ui_Dashboard2
from importaciones import *

class QvDashboard2(QFrame, Ui_Dashboard2):
    def __init__(self, qv = None):
        QFrame.__init__(self)
        self.setupUi(self)
        self.qv = qv
        if self.qv is not None:
            self.layout = QHBoxLayout(self.frameCanvas)
            self.frameCanvas.setLayout(self.layout)
            self.layout.addWidget(self.qv.canvas)
            self.qv.canvas.show()
            self.qv.lblTitolProjecte.setText('Exemple de dashboard')


if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        dash = QvDashboard2()
        dash.show()