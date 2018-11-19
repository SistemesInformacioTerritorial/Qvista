
from moduls.QvImports import * 

from qgis.core import QgsRectangle
from botoinfomapa import Ui_BotoInfoMapa



class QvColumnaCataleg(QWidget):
    """
        Crea una columna de fichas per cada projecte de la llista amb que s'inicialitza.
 
    Cada columna porta el títol amb que s'ha inicilaitzat.
    Es un widget amb el que és pot fer el que és vulgui, sempre que sigui legal.
    """

    def __init__(self, titol, projectes, projectQgis = None, labelProjecte = None, textCerca = ''):

        QWidget.__init__(self)

        self.titol = titol
        self.projectes = projectes
        self.projectQgis = projectQgis
        self.labelProjecte = labelProjecte
        self.textCerca = textCerca

        print('Cercare: '+textCerca)

        self.scroll = QScrollArea()
        self.frame1 = QFrame()

        self.frame1.setMinimumWidth(520)
        self.frame1.setMaximumWidth(520)

        self.layoutScroll = QVBoxLayout(self.frame1)
        self.layoutScroll.setContentsMargins(8,8,8,8)
        self.frame1.setLayout(self.layoutScroll)

        self.numeroBotons = 0
        
        fnt = QFont("Segoe UI", 22, weight=QFont.Normal)

        lblTitol = QLabel(self.titol)
        lblTitol.setFont(fnt)
        # self.layoutScroll.addWidget(lblTitol)


        for projecte in projectes:      
            if self.textCerca.lower() in projecte.lower():  
                botoInfoMapa = QWidget()
                botoInfoMapa.ui = Ui_BotoInfoMapa()
                botoInfoMapa.ui.setupUi(botoInfoMapa)

                self.numeroBotons = self.numeroBotons + 1

                self.layoutScroll.addWidget(botoInfoMapa)

                botoInfoMapa.ui.lblTitol.setText(projecte)
                imatge = QPixmap('../dades/projectes/'+projecte+".png")
                imatge = imatge.scaledToWidth(200)
                imatge = imatge.scaledToHeight(200)
                
                botoInfoMapa.ui.lblImatge.setPixmap(imatge)

                # botoInfoMapa.ui.b4.clicked.connect(lambda: self.obrirEnQgis('../dades/projectes/'+projecte+'.qgs'))

                nomProjecte='../dades/projectes/'+projecte+'.qgs'
                # project = QgsProject()
                # project.read(nomProjecte)

                # botoInfoMapa.ui.label_3.setText('Autor: '+project.metadata().author())
                botoInfoMapa.ui.b1.clicked.connect(self.obrirEnQVista(nomProjecte))
                botoInfoMapa.ui.b2.clicked.connect(self.obrirEnQgis(nomProjecte))

        # for i in range(1,30):
        #     botoInfoMapa = QWidget()
        #     botoInfoMapa.ui = Ui_BotoInfoMapa()
        #     botoInfoMapa.ui.setupUi(botoInfoMapa)
        #     self.layoutScroll.addWidget(botoInfoMapa)
        
        self.scroll.setWidget(self.frame1)
        self.layoutWidget = QVBoxLayout(self)
        self.layoutWidget.setContentsMargins(0,0,0,0)
        self.setLayout(self.layoutWidget)

        self.layoutWidget.addWidget(lblTitol)
        self.layoutWidget.addWidget(self.scroll)
        # self.viewport().installEventFilter(self.frame1)
        self.scroll.setMaximumWidth(540)
        self.scroll.setMinimumWidth(540)
        self.setMaximumWidth(540)
        self.setMinimumWidth(540)
        if self.numeroBotons > 0:
            self.show()
        else:
            self.hide()
        
    # def obrirEnQgis(self, projecte):
    #     QDesktopServices().openUrl(QUrl('d:/dropbox/qvistaProd/'+projecte))


    def obrirEnQgis(self, projecte):
        
        def obertura():
            try:
                QDesktopServices().openUrl(QUrl(projecte)) 
            except:
                pass
        return obertura


    def obrirEnQVista(self, projecte):
        def obertura():
            try:
                self.projectQgis.read(projecte)
                self.labelProjecte.setText(self.projectQgis.title())
                self.parent().parent().parent().parent().hide()
            except:
                pass
        return obertura




class QvCataleg(QWidget):
    
    def __init__(self, projectQgis = None, labelProjecte = None):
        self.projectQgis = projectQgis
        self.labelProjecte = labelProjecte
        QWidget.__init__(self)
        layoutWidgetPrincipal = QVBoxLayout(self)
        self.setLayout(layoutWidgetPrincipal)

        frameCapcalera = QFrame()
        frameCapcalera.setMaximumHeight(70)
        frameCapcalera.setMinimumHeight(70)
        frameCapcalera.setStyleSheet('QFrame {background-color: #aaaaaa')

        lytCapcalera = QVBoxLayout(frameCapcalera)
        frameCapcalera.setLayout(lytCapcalera)
        lytCapcalera.setContentsMargins(0,0,0,0)

        fnt = QFont("Segoe UI", 22, weight=QFont.Normal)
        titol = QLabel("Catàleg d'Informació Territorial")
        titol.setFont(fnt)
        self.liniaCerca = QLineEdit()
        self.liniaCerca.setMaximumWidth(300)
        self.liniaCerca.setClearButtonEnabled(True)
        self.liniaCerca.returnPressed.connect(self.filtra)

        lytCapcalera.addWidget(titol)
        lytCapcalera.addWidget(self.liniaCerca)

        scrollFull = QScrollArea()
        frame = QFrame()
        scrollFull.setWidget(frame)
        self.layoutFrame = QHBoxLayout(frame)
        self.layoutFrame.setAlignment(Qt.AlignLeft)
        frame.setLayout(self.layoutFrame)

        frame.setGeometry(10,10,4000,900)
        frame.setMaximumHeight(900)
        frame.setMinimumHeight(900)

        # frame.show()

        self.projectes = ['fotos', 
                    'bcn11_nord',
                    'gats'
                    'equipaments',
                    'MarxesCiutat'
                    ]

        self.projectesUrb = ['Sentencies',
                    'Projectes_urbanitzacio',
                    'Ambits_planejament',
                    'Ambits_gestio',
                    'PECAB 2015',
                    'PECAB (no vigent)',
                    'Suspensions de Llicències',
                    'Parceles DAP',
                    'Alineacions vigents',
                    'piu',
                    'Catàleg de Patrimoni Protegit']
                    
        self.projectesInf = ['NombreAparcaments',
                    'Carrils bici i zones 30',
                    'CoberturaVegetal',
                    'obres',
                    'cams_VideoVigilancia_v01',
                    'pavimentacioGeo'] 
        self.projectesAMB = ['Vol 1961 AMB',
                    'Vol 1965 AMB',
                    'Imatge satel·lit 2011 AMB',
                    'OpenStreetMap']
        self.qvColumnaCataleg = QvColumnaCataleg('Mapes generals', self.projectes, self.projectQgis, self.labelProjecte)
        self.qvColumnaCataleg2 = QvColumnaCataleg('Urbanisme', self.projectesUrb, self.projectQgis, self.labelProjecte)
        self.qvColumnaCataleg3 = QvColumnaCataleg('Infraestructures', self.projectesInf, self.projectQgis, self.labelProjecte)
        self.qvColumnaCataleg4 = QvColumnaCataleg('AMB', self.projectesAMB, self.projectQgis, self.labelProjecte)
        # qvColumnaCataleg82 = QvColumnaCataleg('Animals, gats i fures', projectes)
        # qvColumnaCataleg83 = QvColumnaCataleg('Obres de ciutat', projectes)
        # qvColumnaCataleg9 = QvColumnaCataleg('Topografia', projectes)
        # qvColumnaCataleg92 = QvColumnaCataleg('Cosmologiade ciutat', projectes)
        self.layoutFrame.addWidget(self.qvColumnaCataleg)
        self.layoutFrame.addWidget(self.qvColumnaCataleg2)
        self.layoutFrame.addWidget(self.qvColumnaCataleg3)
        self.layoutFrame.addWidget(self.qvColumnaCataleg4)
        # layoutFrame.addWidget(qvColumnaCataleg9)
        # layoutFrame.addWidget(qvColumnaCataleg92)
        # layoutFrame.addWidget(qvColumnaCataleg82)
        # layoutFrame.addWidget(qvColumnaCataleg83)


        # qvColumnaCataleg.show()

        layoutWidgetPrincipal.addWidget(frameCapcalera)
        layoutWidgetPrincipal.addWidget(scrollFull)
        self.show()


    def filtra(self):
        print("Filtra: "+self.liniaCerca.text())        
        
        # Maravilloses dues línies
        for i in reversed(range(self.layoutFrame.count())): 
            self.layoutFrame.itemAt(i).widget().setParent(None)
        self.qvColumnaCataleg = QvColumnaCataleg('Mapes generals', self.projectes, self.projectQgis, self.labelProjecte, textCerca=self.liniaCerca.text())
        self.qvColumnaCataleg2 = QvColumnaCataleg('Urbanisme', self.projectesUrb, self.projectQgis, self.labelProjecte, textCerca=self.liniaCerca.text())
        self.qvColumnaCataleg3 = QvColumnaCataleg('Infraestructures', self.projectesInf, self.projectQgis, self.labelProjecte, textCerca=self.liniaCerca.text())
        self.qvColumnaCataleg4 = QvColumnaCataleg('AMB', self.projectesAMB, self.projectQgis, self.labelProjecte, textCerca=self.liniaCerca.text())
        self.layoutFrame.addWidget(self.qvColumnaCataleg)
        self.layoutFrame.addWidget(self.qvColumnaCataleg2)
        self.layoutFrame.addWidget(self.qvColumnaCataleg3)


if __name__ == "__main__":
    with qgisapp() as app:

        cataleg = QvCataleg()
        cataleg.showMaximized()

