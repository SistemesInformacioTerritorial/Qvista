
from qgis.PyQt.QtWidgets import QWidget, QFrame,QApplication, QLabel
from qgis.PyQt.QtGui import QPixmap
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtWebKitWidgets import QWebView , QWebPage
from qgis.PyQt.QtWebKit import QWebSettings
from qgis.PyQt.QtCore import QUrl
from platges import Ui_Form
import urllib.request
class QvPlatges(QFrame):
    def __init__(self, qV = None):
        QFrame.__init__(self)
        self.titol = 'Estat de les platges'
        self.qV = qV
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pbMarBella.clicked.connect(self.mostraMarBella)
        self.ui.pbPort1.clicked.connect(self.mostraPort1)
        self.ui.pbPort2.clicked.connect(self.mostraPort2)
        self.ui.pbSomorrostro1.clicked.connect(self.mostraSomorrostro1)
        self.ui.pbSomorrostro2.clicked.connect(self.mostraSomorrostro2)
        self.ui.pbNovaIcaria.clicked.connect(self.mostraNovaIcaria)
        if self.qV is not None:
            self.qV.lblTitolProjecte.setText('Estat de les platges de la ciutat')
 
    def mostraMarBella(self):
        # self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_5.jpg'))
        # self.ui.label.
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_5.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()

    def mostraNovaIcaria(self):
        # self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_5.jpg'))
        # self.ui.label.
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_6.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()


    def mostraSomorrostro1(self):       
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_1.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()

    def mostraSomorrostro2(self):        
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_2.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()

    def mostraPort1(self):       
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_3.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()

    def mostraPort2(self):     
        url = 'http://example.com/image.png'    
        data = urllib.request.urlopen('http://www.bcn.cat/dades/platges/images/webcam_4.jpg').read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.ui.lblCamera.setPixmap(pixmap)
        self.ui.lblCamera.show()


if __name__ == "__main__":
    
    with qgisapp() as app:
    # import sys
    # app = QApplication(sys.argv)
        platges = QvPlatges()
        platges.show()
    # sys.exit(app.exec_())