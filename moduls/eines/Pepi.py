from qgis.PyQt.QtCore import Qt, QUrl, pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QFont
from qgis.PyQt.QtWidgets import (QDockWidget, QFrame, QLabel, QSizePolicy,
                                 QSpacerItem, QVBoxLayout, QHBoxLayout, QPushButton,
                                 QWidget, QScrollArea)

from moduls.QvPushButton import QvPushButton


class CollapsibleSection(QWidget):
    """Widget colapsable para agrupar botones en secciones"""
    
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.is_expanded = False
        
        # Botón para expandir/contraer
        self.toggle_btn = QPushButton(f"▶ {title}")
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setStyleSheet("Text-align: left; font-weight: bold;")
        self.toggle_btn.clicked.connect(self.toggle)
        
        # Container para los botones
        self.content_widget = QFrame()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        self.content_widget.setVisible(False)  # Ocultar al inicio
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toggle_btn)
        main_layout.addWidget(self.content_widget)
    
    def add_button(self, button):
        """Añade un botón a la sección"""
        self.content_layout.addWidget(button)
    
    def toggle(self):
        """Expande o contrae la sección"""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        arrow = "▼" if self.is_expanded else "▶"
        self.toggle_btn.setText(f"{arrow} {self.title}")


class Pepi(QDockWidget):
    titol = 'Pepi'
    apareixDockat = True
    esEinaGeneral = False
    def __init__(self, parent):
        self.parent = parent
        super().__init__("Pepi")
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        fMarxes = QFrame()
        lytMarxes = QVBoxLayout(fMarxes)
        lytMarxes.setAlignment(Qt.AlignTop)
        lytMarxes.setContentsMargins(0, 0, 0, 0)
        lytMarxes.setSpacing(5)

        fMarxes.setLayout(lytMarxes)
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)
        
        # ========== SECCIÓN 1: DOCUMENTOS GENERALES ==========
        section1 = CollapsibleSection('1.- Documents generals 17/6')
        
        bDoc1 = QvPushButton('Localització',flat=True)
        bDoc1.setStyleSheet("Text-align: left")
        bDoc2 = QvPushButton('Propietat',flat=True)
        bDoc2.setStyleSheet("Text-align: left")
        bDoc3 = QvPushButton('Estat actual',flat=True)
        bDoc3.setStyleSheet("Text-align: left")
        bDoc4 = QvPushButton('Classificació segons superfície afectada',flat=True)
        bDoc4.setStyleSheet("Text-align: left")
        bDoc5 = QvPushButton('Classificació segons número de parcel·les afectades',flat=True)
        bDoc5.setStyleSheet("Text-align: left")
        bDoc6 = QvPushButton('Classificació segons número de propietaris',flat=True)
        bDoc6.setStyleSheet("Text-align: left")
        bDoc7 = QvPushButton('Classificació segons ús',flat=True)
        bDoc7.setStyleSheet("Text-align: left")
        bDoc8 = QvPushButton('Classificació segons estat edificatori',flat=True)
        bDoc8.setStyleSheet("Text-align: left")
        bDoc9 = QvPushButton('Classificació segons cost total',flat=True)
        bDoc9.setStyleSheet("Text-align: left")
        bDoc10 = QvPushButton('Classificació segons valoració',flat=True)
        bDoc10.setStyleSheet("Text-align: left")
        
        # Añadir botones a la sección 1
        section1.add_button(bDoc1)
        section1.add_button(bDoc2)
        section1.add_button(bDoc3)
        section1.add_button(bDoc4)
        section1.add_button(bDoc5)
        section1.add_button(bDoc6)
        section1.add_button(bDoc7)
        section1.add_button(bDoc8)
        section1.add_button(bDoc9)
        section1.add_button(bDoc10)
        
        # bMapa = QvPushButton('1.2 Mapa de Barcelona identificant les marxes realitzades',flat=True)
        # bMapa.setStyleSheet("Text-align: left")
        # section1.add_button(bMapa)
        
        # bDocGen = QvPushButton('1.3 Document general (guia lectura, info de cada marxa, annexos barri',flat=True)
        # bDocGen.setStyleSheet("Text-align: left")
        # section1.add_button(bDocGen)
        
        lytMarxes.addWidget(section1)
        
        # ========== SECCIÓN 2: RECULL INFORMATIU DE CADA MARXA ==========
        section2 = CollapsibleSection('Altres qualificacions 1')
        
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
        
        # Añadir botones a la sección 2
        section2.add_button(bMarxes1)
        section2.add_button(bMarxes2)
        section2.add_button(bMarxes3)
        section2.add_button(bMarxes4)
        section2.add_button(bMarxes5)
        section2.add_button(bMarxes6)
        section2.add_button(bMarxes7)
        section2.add_button(bMarxes8)
        section2.add_button(bMarxes9)
        section2.add_button(bMarxes10)
        section2.add_button(bMarxes11)
        
        lytMarxes.addWidget(section2)
        
        # ========== SECCIÓN 3: INFORME DE RESULTATS ==========
        section3 = CollapsibleSection('Altres qualificacions 2')
        
        bMarxes1_1 = QvPushButton('Districte de Gràcia (totes les marxes)', flat=True)
        bMarxes1_1.setStyleSheet("Text-align: left")
        bMarxes1_2 = QvPushButton('la Trinitat Nova', flat=True)
        bMarxes1_2.setStyleSheet("Text-align: left")
        bMarxes1_3 = QvPushButton('la Trinitat Vella', flat=True)
        bMarxes1_3.setStyleSheet("Text-align: left")
        bMarxes1_4 = QvPushButton('el Bon Pastor', flat=True)
        bMarxes1_4.setStyleSheet("Text-align: left")
        bMarxes1_5 = QvPushButton('la Verneda i la Pau', flat=True)
        bMarxes1_5.setStyleSheet("Text-align: left")
        bMarxes1_6 = QvPushButton('el Besós i el Maresme', flat=True)
        bMarxes1_6.setStyleSheet("Text-align: left")
        bMarxes1_7 = QvPushButton('la Marina del Prat Vermell', flat=True)
        bMarxes1_7.setStyleSheet("Text-align: left")
        
        # Añadir botones a la sección 3
        section3.add_button(bMarxes1_1)
        section3.add_button(bMarxes1_2)
        section3.add_button(bMarxes1_3)
        section3.add_button(bMarxes1_4)
        section3.add_button(bMarxes1_5)
        section3.add_button(bMarxes1_6)
        section3.add_button(bMarxes1_7)
        
        lytMarxes.addWidget(section3)
        
        # ========== SECCIÓN 4: DOCUMENTS DE RETORN ==========
        section4 = CollapsibleSection('Altres qualificacions 3')
        
        bMarxes2_1 = QvPushButton('la Trinittat Vella', flat=True)
        bMarxes2_1.setStyleSheet("Text-align: left")
        bMarxes2_2 = QvPushButton('el Bon Pastor', flat=True)
        bMarxes2_2.setStyleSheet("Text-align: left")
        
        # Añadir botones a la sección 4
        section4.add_button(bMarxes2_1)
        section4.add_button(bMarxes2_2)
        
        lytMarxes.addWidget(section4)
        
        # Espaciador al final
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lytMarxes.addItem(spacer)


        bDoc1.clicked.connect(self.mostrarDoc1)
        bDoc2.clicked.connect(self.mostrarDoc2)
        bDoc3.clicked.connect(self.mostrarDoc3)
        bDoc4.clicked.connect(self.mostrarDoc4)
        bDoc5.clicked.connect(self.mostrarDoc5)
        bDoc6.clicked.connect(self.mostrarDoc6)
        bDoc7.clicked.connect(self.mostrarDoc7)
        bDoc8.clicked.connect(self.mostrarDoc8)
        bDoc9.clicked.connect(self.mostrarDoc9)
        bDoc10.clicked.connect(self.mostrarDoc10)

        # bMapa.clicked.connect(self.mostrarMapa)
        # bDocGen.clicked.connect(self.mostrarDocGen)

        # bMarxes1.clicked.connect(self.mostrarColl)
        # bMarxes2.clicked.connect(self.mostrarSalut)
        # bMarxes3.clicked.connect(self.mostrarBesos)
        # bMarxes4.clicked.connect(self.mostrarBonPastor)
        # bMarxes5.clicked.connect(self.mostrarTNova)
        # bMarxes6.clicked.connect(self.mostrarTVella)
        # bMarxes7.clicked.connect(self.mostrarGracia)
        # bMarxes8.clicked.connect(self.mostrarVallcarca)
        # bMarxes9.clicked.connect(self.mostrarMarina)
        # bMarxes10.clicked.connect(self.mostrarGrassot)
        # bMarxes11.clicked.connect(self.mostrarVerneda)

        
        # bMarxes1_1.clicked.connect(self.mostrarInformeG)
        # bMarxes1_2.clicked.connect(self.mostrarInformeTN)
        # bMarxes1_3.clicked.connect(self.mostrarInformeTV)
        # bMarxes1_4.clicked.connect(self.mostrarInformeBP)
        # bMarxes1_5.clicked.connect(self.mostrarInformeVP)
        # bMarxes1_6.clicked.connect(self.mostrarInformeBM)
        # bMarxes1_7.clicked.connect(self.mostrarInformeMPV)

        # bMarxes2_1.clicked.connect(self.mostrarRetornTrinitatVella)
        # bMarxes2_2.clicked.connect(self.mostrarRetornBonPastor)


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

    def mostrarDoc1(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Localització del sòl 17-6.pdf'))
    def mostrarDoc2(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Propietat del sòl 17-6.pdf'))    
    def mostrarDoc3(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Estat actal del sòl 17-6.pdf'))  
    def mostrarDoc4(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del sòl 17-6 segons superfície afectada.pdf'))  
    def mostrarDoc5(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del 17-6 segons parcel·les afectades.pdf'))  
    def mostrarDoc6(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del 17-6 segons número de priopietaris.pdf'))  
    def mostrarDoc7(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del 17-6 segons ús.pdf'))  
    def mostrarDoc8(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del 17-6 segons estat edificatori.pdf'))  
    def mostrarDoc9(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificació del 17-6 segons cost total.pdf'))  
    def mostrarDoc10(self):        
        QDesktopServices().openUrl(QUrl('file:///d:/Pepi/Classificacio del 17-6  segons valoracio.pdf'))
        
           
        
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

    def mostrarRetornTrinitatVella(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.3-Retorn 180710-G-Marxa Trinitat Vella-23-07-2018.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarRetornBonPastor(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.3-Retorn-180717-H-Marxa Bon Pastor.pdf'
        QDesktopServices().openUrl(QUrl(PDF))

    # Informes
    def mostrarInformeG(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/2.2-GRACIA-Informe resultats-Passejades_FINAL_5Barris.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeTN(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-F_TRINITAT NOVA_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeTV(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-G_TRINITAT VELLA_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeBP(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-H_BON PASTOR_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeVP(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-J_LA VERNEDA I LA PAU_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeBM(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-I_BESOS MARESME_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))    

    def mostrarInformeMPV(self):
        PDF = 'file:///L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Marxes de ciutat/PdfFitxes/2.2-I_BESOS MARESME_Informe Marxa Explora.pdf'
        QDesktopServices().openUrl(QUrl(PDF))