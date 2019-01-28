from moduls.QvImports import *

class MarxesCiutat(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Marxes de ciutat")
        
        fMarxes = QFrame()
        fMarxes.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        # fPavim.setStyleSheet("QFrame {background-color: #010101 'd:/dropbox/qvistaProd/imatges/pavim.jpg'}")
        lytMarxes = QVBoxLayout(fMarxes)
        lytMarxes.setAlignment(Qt.AlignTop)

        fMarxes.setLayout(lytMarxes)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        bMarxes = QPushButton('Marxes de ciutat')
        lytMarxes.addWidget(bMarxes)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        lytMarxes.addItem(spacer)
        bMarxes2 = QPushButton('Marxes de ciutat')
        bMarxes3 = QPushButton('Marxes de ciutat')
        bMarxes4 = QPushButton('Marxes de ciutat')
        lytMarxes.addWidget(bMarxes2)
        lytMarxes.addWidget(bMarxes3)
        lytMarxes.addWidget(bMarxes4)

        self.browserMarxes = QWebView()
        self.browserMarxes.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.browserMarxes.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.browserMarxes.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.browserMarxes.show()

        # browserPavim.setUrl(QUrl('CatalegPavim.pdf'))
        # QDesktopServices().openUrl(QUrl('CatalegPavim.pdf'))
        lytMarxes.addWidget(self.browserMarxes)

        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fMarxes)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()

        """
        
        QDesktopServices().openUrl(QUrl('c:/temp/tempQgis.qgs'))
       """