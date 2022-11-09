from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWebKit import QWebSettings
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWidgets import QDockWidget, QFrame, QVBoxLayout

from moduls.QvPushButton import QvPushButton


class DockPavim(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Pavimentació")
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fPavim = QFrame()
        fPavim.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        lytPavim = QVBoxLayout(fPavim)
        lytPavim.setAlignment(Qt.AlignTop)

        fPavim.setLayout(lytPavim)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        bPavim = QvPushButton('Pavimentació', flat=True)
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