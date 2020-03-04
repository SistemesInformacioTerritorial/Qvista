from moduls.QvImports import *
from moduls.QvPushButton import QvPushButton
from PyQt5.QtGui import QFont, QDesktopServices

class MarxesCiutat(QDockWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Marxes exploratòries")
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fMarxes = QFrame()
        # fMarxes.setStyleSheet("QFrame {background-image: url('c:/qvistaProd/imatges/pavim.jpg');}")
        lytMarxes = QVBoxLayout(fMarxes)
        lytMarxes.setAlignment(Qt.AlignTop)

        fMarxes.setLayout(lytMarxes)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)
        lDocuments = QLabel('1.- Documents generals del projecte')
        lDocuments.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        lDocuments.setFont(f)

        lBarris = QLabel('2.- Documents de cada marxa')
        lBarris.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        lBarris.setFont(f)

        
        lBarris2 = QLabel('2.1- Recull informatiu de cada marxa')
        lBarris2.setAlignment(Qt.AlignLeft)
        f = QFont()
        f.setBold(True)
        lBarris2.setFont(f)

        
        
        lBarris3 = QLabel('2.2- Informe de resultats de cada marxa')
        lBarris3.setAlignment(Qt.AlignLeft)
        f = QFont()
        f.setBold(True)
        lBarris3.setFont(f)
        
        lBarris4 = QLabel('2.3- Document de retorn')
        lBarris4.setAlignment(Qt.AlignLeft)
        f = QFont()
        f.setBold(True)
        lBarris4.setFont(f)


        bGuia = QvPushButton('1.1 Mapificació marxes exploratòries: Qué és el projecte?',flat=True)
        bGuia.setStyleSheet("Text-align: left")
        # bMarxes = QvPushButton('Recull marxes exploratòries dones 2017-18',flat=True)
        # bMarxes.setStyleSheet("Text-align: left")  
      
        bMapa = QvPushButton('1.2 Mapa de Barcelona identificant les marxes realitzades',flat=True)
        bMapa.setStyleSheet("Text-align: left")


        
        bDocGen = QvPushButton('1.3 Document general (guia lectura, info de cada marxa, annexos barri',flat=True)
        bDocGen.setStyleSheet("Text-align: left")

        bMapaXarxa = QvPushButton('Xarxa quotidiana',flat=True)
        bMapaXarxa.setStyleSheet("Text-align: left")
        bMapaXarxa.hide()
        lytMarxes.addWidget(lDocuments) 
        lytMarxes.addWidget(bGuia) 
        lytMarxes.addWidget(bMapa) 
        lytMarxes.addWidget(bDocGen) 
        # lytMarxes.addWidget(bMarxes)
        lytMarxes.addWidget(bMapaXarxa)
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        lytMarxes.addItem(spacer)
        lytMarxes.addWidget(lBarris) 
        lytMarxes.addWidget(lBarris2) 
        bMarxes1 = QvPushButton('   el Coll', flat=True)
        bMarxes1.setStyleSheet("Text-align: left")
        bMarxes2 = QvPushButton('   la Salut', flat=True)
        bMarxes2.setStyleSheet("Text-align: left")
        bMarxes3 = QvPushButton('   el Besós i el Maresme', flat=True)
        bMarxes3.setStyleSheet("Text-align: left")
        bMarxes4 = QvPushButton('   el Bon Pastor', flat=True)
        bMarxes4.setStyleSheet("Text-align: left")
        bMarxes5 = QvPushButton('   la Trinitat Nova', flat=True)
        bMarxes5.setStyleSheet("Text-align: left")
        bMarxes6 = QvPushButton('   la Trinitat Vella', flat=True)
        bMarxes6.setStyleSheet("Text-align: left")
        bMarxes7 = QvPushButton('   la Vila de Gràcia', flat=True)
        bMarxes7.setStyleSheet("Text-align: left")
        bMarxes8 = QvPushButton('   Vallcarca', flat=True)
        bMarxes8.setStyleSheet("Text-align: left")
        bMarxes9 = QvPushButton('   la Marina del Prat Vermell', flat=True)
        bMarxes9.setStyleSheet("Text-align: left")
        bMarxes10 = QvPushButton('   el Camp del Grassot', flat=True)
        bMarxes10.setStyleSheet("Text-align: left")
        bMarxes11 = QvPushButton('   la Verneda i la Pau', flat=True)
        bMarxes11.setStyleSheet("Text-align: left")

        bMarxes1_2 = QvPushButton('Districte de Gràcia (totes les marxes)', flat=True)
        bMarxes1_2.setStyleSheet("Text-align: left")
       
        bMarxes3_2 = QvPushButton('el Besós i el Maresme', flat=True)
        bMarxes3_2.setStyleSheet("Text-align: left")
        bMarxes4_2 = QvPushButton('el Bon pastor', flat=True)
        bMarxes4_2.setStyleSheet("Text-align: left")
        bMarxes5_2 = QvPushButton('la Trinitat Nova', flat=True)
        bMarxes5_2.setStyleSheet("Text-align: left")
        bMarxes6_2 = QvPushButton('la Trinitat Vella', flat=True)
        bMarxes6_2.setStyleSheet("Text-align: left")
        
        bMarxes9_2 = QvPushButton('la Marina del Prat vermell', flat=True)
        bMarxes9_2.setStyleSheet("Text-align: left")
        bMarxes11_2 = QvPushButton('la Verneda i la Pau', flat=True)
        bMarxes11_2.setStyleSheet("Text-align: left")

        bMarxes1_3 = QvPushButton('la Trinitat Vella', flat=True)
        bMarxes1_3.setStyleSheet("Text-align: left")
       
        bMarxes2_3 = QvPushButton('el Bon Pastor', flat=True)
        bMarxes2_3.setStyleSheet("Text-align: left")

        lytMarxes.addWidget(lBarris2)
        lytMarxes.addWidget(bMarxes1)
        lytMarxes.addWidget(bMarxes2)
        lytMarxes.addWidget(bMarxes7)
        lytMarxes.addWidget(bMarxes10)
        lytMarxes.addWidget(bMarxes8)
        lytMarxes.addWidget(bMarxes5)
        lytMarxes.addWidget(bMarxes6)
        lytMarxes.addWidget(bMarxes4)
        lytMarxes.addWidget(bMarxes11)
        lytMarxes.addWidget(bMarxes3)
        lytMarxes.addWidget(bMarxes9) 
        
        lytMarxes.addItem(spacer)
        lytMarxes.addWidget(lBarris3) 
        
        lytMarxes.addWidget(bMarxes1_2)
        lytMarxes.addWidget(bMarxes5_2)
        lytMarxes.addWidget(bMarxes6_2)
        lytMarxes.addWidget(bMarxes4_2)
        lytMarxes.addWidget(bMarxes11_2)
        lytMarxes.addWidget(bMarxes3_2)
        lytMarxes.addWidget(bMarxes9_2)

        lytMarxes.addItem(spacer)
        lytMarxes.addWidget(lBarris4) 
        lytMarxes.addWidget(bMarxes1_3)
        lytMarxes.addWidget(bMarxes2_3)


        bGuia.clicked.connect(self.mostrarGuia)
        # bMarxes.clicked.connect(self.mostrarInstruccions)
        bMapa.clicked.connect(self.mostrarMapa)
        bDocGen.clicked.connect(self.mostrarDocGen)
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
        bMarxes11.clicked.connect(self.mostrarVerneda)

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
        QDesktopServices().openUrl(QUrl('file:///L:/DADES/SIT/qVista/CATALEG/MAPES%20PRIVATS/Marxes%20de%20ciutat/PdfFitxes/QueEsElProjecte.pdf'))


        
    def mostrarInstruccions(self):
        QDesktopServices().openUrl(QUrl('file:///L:/DADES/SIT/qVista/CATALEG/MAPES%20PRIVATS/Marxes%20de%20ciutat/PdfFitxes/2017-18-190228_Marxes_exploratories_A3.pdf'))


    def mostrarMapa(self):
        QDesktopServices().openUrl(QUrl('file:///L:/DADES/SIT/qVista/CATALEG/MAPES%20PRIVATS/Marxes%20de%20ciutat/PdfFitxes/1.2-Mapa BCN_v2.pdf'))
    
    def mostrarDocGen(self):
        QDesktopServices().openUrl(QUrl('file:///L:/DADES/SIT/qVista/CATALEG/MAPES%20PRIVATS/Marxes%20de%20ciutat/PdfFitxes/1.3-190318_Marxes_exploratories_A3.pdf'))
       
      

    def mostrarMapaXarxa(self):
        # QDesktopServices().openUrl(QUrl('N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\190228_Marxes_exploratories_A4.pdf'))
        PDF = 'file:///' + r'N:\9SITEB\Publicacions\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat\PdfFitxes\Marxes_xarxa_quotidiana_A4.pdf'
        QDesktopServices().openUrl(QUrl(PDF))
        # self.w = QvPDF(PDF)
        # self.w.setGeometry(50, 50, 1200, 800)
        # self.w.setWindowTitle('Xarxa quotidiana')
        # self.w.show()

    def mostrarColl(self):
        # QDesktopServices().openUrl(QUrl('d:/MarxesCiutat/ElColl_resultats.png'))
        # QDesktopServices().openUrl(QUrl('L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/02_El_coll.pdf'))
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/02_El_coll.pdf'
        QDesktopServices().openUrl(QUrl(PDF))

    def mostrarSalut(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/03_La_salut.pdf'
        QDesktopServices().openUrl(QUrl(PDF))

    def mostrarGrassot(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/05_el_Camp_den_Grassot.pdf'
        QDesktopServices().openUrl(QUrl(PDF))
        # self.w = QvPDF(PDF)
        # self.w.setGeometry(50, 50, 1200, 800)
        # self.w.setWindowTitle("Marxa del Camp d'en Grassot")
        # self.w.show()
    def mostrarBesos(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/12_El_Besos_el_Maresme.pdf'
        
        QDesktopServices().openUrl(QUrl(PDF))
        # self.w = QvPDF(PDF)
        # self.w.setGeometry(50, 50, 1200, 800)
        # self.w.setWindowTitle('Marxa del Besós i el Maresme')
        # self.w.show()
    def mostrarBonPastor(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/09_Bon_Pastor.pdf'
        
        QDesktopServices().openUrl(QUrl(PDF))
        # self.w = QvPDF(PDF)
        # self.w.setGeometry(50, 50, 1200, 800)
        # self.w.setWindowTitle('Marxa del Bon Pastor')
        # self.w.show()
    def mostrarTNova(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/07_Trinitat_nova.pdf'
        
        QDesktopServices().openUrl(QUrl(PDF))
        # self.w = QvPDF(PDF)
        # self.w.setGeometry(50, 50, 1200, 800)
        # self.w.setWindowTitle('Marxa de Trinitat Nova')
        # self.w.show()
    def mostrarTVella(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/08_Trinitat_Vella.pdf'
        
        QDesktopServices().openUrl(QUrl(PDF))

    def mostrarGracia(self):
        PDF = 'file:///' + 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/04_Vila_de_gracia.pdf'
        
        QDesktopServices().openUrl(QUrl(PDF))
 
    def mostrarVallcarca(self):
        PDF = 'file:///' + r'L:\DADES\SIT\qVista\CATALEG\MAPES PRIVATS\Marxes de ciutat/PdfFitxes/06_Vallcarca.pdf'
        QDesktopServices().openUrl(QUrl(PDF))
    def mostrarMarina(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/11_La_Marina.pdf'

        QDesktopServices().openUrl(QUrl(PDF))    
    def mostrarVerneda(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/10_La_Verneda_la_Pau.pdf'

        QDesktopServices().openUrl(QUrl(PDF))

