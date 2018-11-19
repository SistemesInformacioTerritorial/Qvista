from qgis.PyQt.QtWidgets import QWidget, QPushButton, QFrame, QStyleFactory,QHBoxLayout
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtCore import (
                            QUrl,
                            )


from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings

class EnllumenatFals(QFrame):
    def __init__(self, qv=None):
        QFrame.__init__(self)
        self.browser = QWebView()
        self.browser.setUrl(QUrl("http://www.qt.io"))
        self.browser.setParent(self)
        self.browser.setGeometry(5,5,500,500)
        self.browser.show()        
        
        # if qv is not None:
        #    self.boto.clicked.connect(qv.dashStandard)

        # if self.frameCanvas is not None:
        #     self.layout = QHBoxLayout(self.frameCanvas)
        #     self.frameCanvas.setLayout(self.layout)
        #     self.layout.addWidget(qv.canvas)
        #     qv.canvas.show()


if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        dash = EnllumenatFals()
        dash.show()