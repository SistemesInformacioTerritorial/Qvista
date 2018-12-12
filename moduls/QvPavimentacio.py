from moduls.QvImports import *

class DockPavim(QDockWidget):
    def __init__(self, qV):
        super().__init__("Pavimentació")
        self.qV = qV
        fPavim = QFrame()
        fPavim.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        # fPavim.setStyleSheet("QFrame {background-color: #010101 'd:/dropbox/qvistaProd/imatges/pavim.jpg'}")
        lytPavim = QVBoxLayout(fPavim)
        lytPavim.setAlignment(Qt.AlignTop)

        fPavim.setLayout(lytPavim)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        fnt = QFont("Segoe UI", 26, weight=QFont.Normal)
        lblPavimentacio = QLabel('Gestió del paviment')
        lblPavimentacio.setFont(fnt)
        bPavim = QPushButton('Pavimentació bàsic')
        bPavim2 = QPushButton('Calçades i voreres per tipologia')
        bPavim3 = QPushButton('Nivells de prioritat')
        bPavim.clicked.connect(self.normal)
        bPavim2.clicked.connect(self.tipus)
        
        lblPavimentacio2 = QLabel()
        imatge = QPixmap('imatges/bar-chart.png')
        lblPavimentacio2.setPixmap(imatge)
        lytPavim.addWidget(lblPavimentacio)
        lytPavim.addWidget(bPavim)
        lytPavim.addWidget(bPavim2)
        lytPavim.addWidget(bPavim3)
        lytPavim.addWidget(lblPavimentacio2)

        self.browserPavim = QWebView()
        self.browserPavim.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.browserPavim.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.browserPavim.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.browserPavim.hide()

        # browserPavim.setUrl(QUrl('CatalegPavim.pdf'))
        # QDesktopServices().openUrl(QUrl('CatalegPavim.pdf'))
        lytPavim.addWidget(self.browserPavim)

        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fPavim)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()
    def tipus(self):
        self.qV.project.read('C:/qVista/Dades/CatalegProjectes/Via pública/PavimentacioGeoTipologia.qgs')       
        fnt = QFont("Segoe UI", 20, weight=QFont.Normal)
        self.qV.lblTitolProjecte.setFont(fnt)
        self.qV.lblTitolProjecte.setText(self.project.title())
    def normal(self):
        self.qV.project.read('C:/qVista/Dades/CatalegProjectes/Via pública/PavimentacioGeo.qgs')       
        fnt = QFont("Segoe UI", 20, weight=QFont.Normal)
        self.qV.lblTitolProjecte.setFont(fnt)
        self.qV.lblTitolProjecte.setText(self.project.title())

        """
        
        QDesktopServices().openUrl(QUrl('c:/temp/tempQgis.qgs'))
       """