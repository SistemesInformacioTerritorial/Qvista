from moduls.QvImports import *
from moduls.QvPDF import QvPDF

class MarxesCiutat(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Marxes exploratòries")
        
        fMarxes = QFrame()
        fMarxes.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        # fPavim.setStyleSheet("QFrame {background-color: #010101 'd:/dropbox/qvistaProd/imatges/pavim.jpg'}")
        lytMarxes = QVBoxLayout(fMarxes)
        lytMarxes.setAlignment(Qt.AlignTop)

        fMarxes.setLayout(lytMarxes)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        bMarxes = QPushButton('Resum operatiu')
        lytMarxes.addWidget(bMarxes)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        lytMarxes.addItem(spacer)
        bMarxes1 = QPushButton('El Coll')
        bMarxes2 = QPushButton('La Salut')
        bMarxes3 = QPushButton('el Besós i el Maresme')
        bMarxes4 = QPushButton('el Bon pastor')
        bMarxes5 = QPushButton('la Trinitat Nova')
        bMarxes6 = QPushButton('la Trinitat Vella')
        bMarxes7 = QPushButton('la Vila de Gràcia')
        bMarxes8 = QPushButton('Vallcarca')
        bMarxes9 = QPushButton('la Marina del Prat vermell')
        lytMarxes.addWidget(bMarxes1)
        lytMarxes.addWidget(bMarxes2)
        lytMarxes.addWidget(bMarxes3)
        lytMarxes.addWidget(bMarxes4)
        lytMarxes.addWidget(bMarxes5)
        lytMarxes.addWidget(bMarxes6)
        lytMarxes.addWidget(bMarxes7)
        lytMarxes.addWidget(bMarxes8)
        lytMarxes.addWidget(bMarxes9)
        bMarxes.clicked.connect(self.mostrarInstruccions)
        bMarxes1.clicked.connect(self.mostrarColl)
        bMarxes2.clicked.connect(self.mostrarSalut)

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
    def mostrarInstruccions(self):
        # QDesktopServices().openUrl(QUrl('d:/MarxesCiutat/Guia_lectura_el_coll.pdf'))
        PDF = 'file:///' + 'd:/MarxesCiutat/Guia_lectura_el_coll.pdf'

        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxes exploratóries')
        self.w.show()

    def mostrarColl(self):
        QDesktopServices().openUrl(QUrl('d:/MarxesCiutat/ElColl_resultats.png'))

    def mostrarSalut(self):
        QDesktopServices().openUrl(QUrl('d:/MarxesCiutat/Salut_resultats.png'))