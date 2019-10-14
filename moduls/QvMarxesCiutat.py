from moduls.QvImports import *
from moduls.QvPDF import QvPDF
from moduls.QvPushButton import QvPushButton
from PyQt5.QtGui import QFont

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
        lDocuments = QLabel('Documents generals del projecte')
        lDocuments.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        lDocuments.setFont(f)

        lBarris = QLabel('Resultats de cada marxa')
        lBarris.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        lBarris.setFont(f)

        bGuia = QvPushButton('Marxes exploratòries: Qué és el projecte?',flat=True)
        bGuia.setStyleSheet("Text-align: left")
        # bMarxes = QvPushButton('Recull marxes exploratòries dones 2017-18',flat=True)
        # bMarxes.setStyleSheet("Text-align: left")  
      
        bMapa = QvPushButton('Mapa Barcelona de les marxes',flat=True)
        bMapa.setStyleSheet("Text-align: left")
        bMapaXarxa = QvPushButton('Xarxa quotidiana',flat=True)
        bMapaXarxa.setStyleSheet("Text-align: left")
        
        lytMarxes.addWidget(lDocuments) 
        lytMarxes.addWidget(bGuia) 
        lytMarxes.addWidget(bMapa) 
        # lytMarxes.addWidget(bMarxes)
        lytMarxes.addWidget(bMapaXarxa)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        lytMarxes.addItem(spacer)
        lytMarxes.addWidget(lBarris) 
        bMarxes1 = QvPushButton('El Coll', flat=True)
        bMarxes1.setStyleSheet("Text-align: left")
        bMarxes2 = QvPushButton('La Salut', flat=True)
        bMarxes2.setStyleSheet("Text-align: left")
        bMarxes3 = QvPushButton('el Besós i el Maresme', flat=True)
        bMarxes3.setStyleSheet("Text-align: left")
        bMarxes4 = QvPushButton('el Bon pastor', flat=True)
        bMarxes4.setStyleSheet("Text-align: left")
        bMarxes5 = QvPushButton('la Trinitat Nova', flat=True)
        bMarxes5.setStyleSheet("Text-align: left")
        bMarxes6 = QvPushButton('la Trinitat Vella', flat=True)
        bMarxes6.setStyleSheet("Text-align: left")
        bMarxes7 = QvPushButton('la Vila de Gràcia', flat=True)
        bMarxes7.setStyleSheet("Text-align: left")
        bMarxes8 = QvPushButton('Vallcarca', flat=True)
        bMarxes8.setStyleSheet("Text-align: left")
        bMarxes9 = QvPushButton('la Marina del Prat vermell', flat=True)
        bMarxes9.setStyleSheet("Text-align: left")
        bMarxes10 = QvPushButton('el Camp del Grassot', flat=True)
        bMarxes10.setStyleSheet("Text-align: left")
        lytMarxes.addWidget(bMarxes1)
        lytMarxes.addWidget(bMarxes2)
        lytMarxes.addWidget(bMarxes3)
        lytMarxes.addWidget(bMarxes4)
        lytMarxes.addWidget(bMarxes5)
        lytMarxes.addWidget(bMarxes6)
        lytMarxes.addWidget(bMarxes7)
        lytMarxes.addWidget(bMarxes8)
        lytMarxes.addWidget(bMarxes9)
        lytMarxes.addWidget(bMarxes10)
        bGuia.clicked.connect(self.mostrarGuia)
        # bMarxes.clicked.connect(self.mostrarInstruccions)
        bMapa.clicked.connect(self.mostrarMapa)
        bMapaXarxa.clicked.connect(self.mostrarMapaXarxa)
        bMarxes1.clicked.connect(self.mostrarColl)
        bMarxes2.clicked.connect(self.mostrarSalut)
        bMarxes3.clicked.connect(self.mostrarBesos)
        bMarxes4.clicked.connect(self.mostrarBonPastor)
        bMarxes5.clicked.connect(self.mostrarTNova)
        bMarxes6.clicked.connect(self.mostrarTVella)
        bMarxes7.clicked.connect(self.mostrarGracia)
        bMarxes8.clicked.connect(self.mostrarVallcarca)
        bMarxes9.clicked.connect(self.mostrarMarina)
        bMarxes10.clicked.connect(self.mostrarGrassot)

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
    def mostrarGuia(self):        
        # QDesktopServices().openUrl(QUrl('N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'))
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2017-18-190228_Marxes_exploratories_A3.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxes exploratóries')
        self.w.show()
        
    def mostrarInstruccions(self):
        
        # QDesktopServices().openUrl(QUrl('N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'))
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2017-18-190228_Marxes_exploratories_A3.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxes exploratóries')
        self.w.show()

    def mostrarMapa(self):
        # QDesktopServices().openUrl(QUrl('N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\190228_Marxes_exploratories_A4.pdf'))
        PDF = 'file:///' + 'N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\Mapa BCN_v2.pdf'

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
        # QDesktopServices().openUrl(QUrl('N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/02_El_coll.pdf'))
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
    def mostrarGrassot(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/05_el_Camp_den_Grassot.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle("Marxa del Camp d'en Grassot")
        self.w.show()
    def mostrarBesos(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa del Besós i el Maresme')
        self.w.show()
    def mostrarBonPastor(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/09_Bon_Pastor.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa del Bon Pastor')
        self.w.show()
    def mostrarTNova(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/07_Trinitat_nova.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de Trinitat Nova')
        self.w.show()
    def mostrarTVella(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/08_Trinitat_Vella.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de Trinitat Vella')
        self.w.show()
    def mostrarGracia(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/04_Vila_de_gracia.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de la Vila de Gràcia')
        self.w.show()
    def mostrarVallcarca(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/06_Vallcarca.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de Vallcarca')
        self.w.show()
    def mostrarMarina(self):
        PDF = 'file:///' + 'N:/9SITEB/Publicacions/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/11_La_Marina.pdf'
        self.w = QvPDF(PDF)
        self.w.setGeometry(50, 50, 1200, 800)
        self.w.setWindowTitle('Marxa de la Marina del Port Vermell')
        self.w.show()

