
from PyQt5.QtWidgets import QWidget, QApplication
from qgis.core.contextmanagers import qgisapp
from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtCore import QUrl
from platges import Ui_Form

class QvPlatges(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pbMarBella.clicked.connect(self.mostraMarBella)
        self.ui.pbPort1.clicked.connect(self.mostraPort1)
        self.ui.pbPort2.clicked.connect(self.mostraPort2)
        self.ui.pbSomorrostro1.clicked.connect(self.mostraSomorrostro1)
        self.ui.pbSomorrostro2.clicked.connect(self.mostraSomorrostro2)
        self.ui.browser = QWebView()
        self.ui.browser.show()

    def mostraMarBella(self):
        self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_5.jpg'))


    def mostraSomorrostro1(self):
        self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_1.jpg'))

    def mostraSomorrostro2(self):
        self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_2.jpg'))

    def mostraPort1(self):
        self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_3.jpg'))

    def mostraPort2(self):
        self.ui.browser.setUrl(QUrl('http://www.bcn.cat/dades/platges/images/webcam_4.jpg'))


if __name__ == "__main__":
    
    with qgisapp() as app:
    # import sys
    # app = QApplication(sys.argv)
        platges = QvPlatges()
        platges.show()
    # sys.exit(app.exec_())