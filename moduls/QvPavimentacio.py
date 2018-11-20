from moduls.QvImports import *

class DockPavim(QDockWidget):
    def __init__(self):
        super().__init__("Pavimentació")
        
        fPavim = QFrame()
        fPavim.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        # fPavim.setStyleSheet("QFrame {background-color: #010101 'd:/dropbox/qvistaProd/imatges/pavim.jpg'}")
        lytPavim = QVBoxLayout(fPavim)
        lytPavim.setAlignment(Qt.AlignTop)

        fPavim.setLayout(lytPavim)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        bPavim = QPushButton('Pavimentació')
        lytPavim.addWidget(bPavim)

        self.browserPavim = QWebView()
        self.browserPavim.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.browserPavim.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.browserPavim.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.browserPavim.show()

        # browserPavim.setUrl(QUrl('CatalegPavim.pdf'))
        # QDesktopServices().openUrl(QUrl('CatalegPavim.pdf'))
        lytPavim.addWidget(self.browserPavim)

        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fPavim)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()

        """
        
        QDesktopServices().openUrl(QUrl('c:/temp/tempQgis.qgs'))
       """