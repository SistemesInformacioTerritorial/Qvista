from dashboard1 import Ui_Dashboard1
from importaciones import *

class QvDashboard1(QFrame, Ui_Dashboard1):
    def __init__(self, qv = None):
        QFrame.__init__(self)
        self.setupUi(self)
        if qv is not None:
            self.layout = QHBoxLayout(self.frameCanvas)
            self.frameCanvas.setLayout(self.layout)
            self.layout.addWidget(qv.canvas)
            qv.canvas.show()


if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        dash = QvDashboard1()
        dash.show()