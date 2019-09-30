from moduls.QvImports import *
from moduls.QvPDF import QvPDF
from moduls.QvPushButton import QvPushButton

class MarxesCiutat(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Marxes exploratòries")
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fMarxes = QFrame()
        fMarxes.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        lytMarxes = QVBoxLayout(fMarxes)
        lytMarxes.setAlignment(Qt.AlignTop)

        fMarxes.setLayout(lytMarxes)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)

        bMarxes = QvPushButton('Marxes exploratories',flat=True)
        bMapa = QvPushButton('Mapa de les marxes',flat=True)
        bMapaXarxa = QvPushButton('Xarxa quotidiana',flat=True)
        lytMarxes.addWidget(bMarxes)
        lytMarxes.addWidget(bMapa)
        lytMarxes.addWidget(bMapaXarxa)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        lytMarxes.addItem(spacer)
        bMarxes1 = QvPushButton('El Coll', flat=True)
        bMarxes2 = QvPushButton('La Salut', flat=True)
        bMarxes3 = QvPushButton('el Besós i el Maresme', flat=True)
        bMarxes4 = QvPushButton('el Bon pastor', flat=True)
        bMarxes5 = QvPushButton('la Trinitat Nova', flat=True)
        bMarxes6 = QvPushButton('la Trinitat Vella', flat=True)
        bMarxes7 = QvPushButton('la Vila de Gràcia', flat=True)
        bMarxes8 = QvPushButton('Vallcarca', flat=True)
        bMarxes9 = QvPushButton('la Marina del Prat vermell', flat=True)
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
        bMapa.clicked.connect(self.mostrarMapa)
        bMapaXarxa.clicked.connect(self.mostrarMapaXarxa)
        bMarxes1.clicked.connect(self.mostrarColl)
        bMarxes2.clicked.connect(self.mostrarSalut)

        # self.browserMarxes = QWebView()
        # self.browserMarxes.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        # self.browserMarxes.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        # self.browserMarxes.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        # self.browserMarxes.show()

        # # browserPavim.setUrl(QUrl('CatalegPavim.pdf'))
        # # QDesktopServices().openUrl(QUrl('CatalegPavim.pdf'))
        # lytMarxes.addWidget(self.browserMarxes)

        self.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.setWidget(fMarxes)
        self.setContentsMargins ( 0, 0, 0, 0 )
        self.show()

        """
        
        QDesktopServices().openUrl(QUrl('c:/temp/tempQgis.qgs'))
        """
    def mostrarInstruccions(self):
        
        # QDesktopServices().openUrl(QUrl('N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'))
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxes exploratóries')
        self.w.show()

    def mostrarMapa(self):
        # QDesktopServices().openUrl(QUrl('N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\190228_Marxes_exploratories_A4.pdf'))
        PDF = 'file:///' + 'N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\Mapa_Marxes_exploratoriesA3.pdf'

        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Mapa de les marxes')
        self.w.show()

    def mostrarMapaXarxa(self):
        # QDesktopServices().openUrl(QUrl('N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\190228_Marxes_exploratories_A4.pdf'))
        PDF = 'file:///' + 'N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\Marxes_xarxa_quotidiana_A4.pdf'

        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Xarxa quotidiana')
        self.w.show()

    def mostrarColl(self):
        # QDesktopServices().openUrl(QUrl('d:/MarxesCiutat/ElColl_resultats.png'))
        QDesktopServices().openUrl(QUrl('N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/02_El_coll.pdf'))
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/02_El_coll.pdf'

        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa del Coll')
        self.w.show()

    def mostrarSalut(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/03_La_salut.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de la Salut')
        self.w.show()