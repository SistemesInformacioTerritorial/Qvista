
from importaciones import *

from qgis.core import QgsRectangle
from botoinfomapa import Ui_BotoInfoMapa



class QvColumnaCataleg(QWidget):
    """
        Crea una columna de fichas per cada projecte de la llista amb que s'inicialitza.
 
    Cada columna porta el títol amb que s'ha inicilaitzat.
    Es un widget amb el que és pot fer el que és vulgui, sempre que sigui legal.
    """

    def __init__(self, titol, projectes, projectQgis = None, labelProjecte = None):

        QWidget.__init__(self)

        self.titol = titol
        self.projectes = projectes
        self.projectQgis = projectQgis
        self.labelProjecte = labelProjecte

        self.scroll = QScrollArea()
        self.frame1 = QFrame()

        self.frame1.setMinimumWidth(520)
        self.frame1.setMaximumWidth(520)

        self.layoutScroll = QVBoxLayout(self.frame1)
        self.layoutScroll.setContentsMargins(0,0,0,0)
        self.frame1.setLayout(self.layoutScroll)
        
        fnt = QFont("Segoe UI", 22, weight=QFont.Normal)

        lblTitol = QLabel(self.titol)
        lblTitol.setFont(fnt)
        self.layoutScroll.addWidget(lblTitol)

        for projecte in projectes:        
            botoInfoMapa = QWidget()
            botoInfoMapa.ui = Ui_BotoInfoMapa()
            botoInfoMapa.ui.setupUi(botoInfoMapa)

            self.layoutScroll.addWidget(botoInfoMapa)

            botoInfoMapa.ui.lblTitol.setText(projecte)
            imatge = QPixmap('../dades/projectes/'+projecte+".png")
            imatge = imatge.scaledToWidth(200)
            imatge = imatge.scaledToHeight(200)
            
            botoInfoMapa.ui.lblImatge.setPixmap(imatge)

            # botoInfoMapa.ui.b4.clicked.connect(lambda: self.obrirEnQgis('../dades/projectes/'+projecte+'.qgs'))

            nomProjecte='../dades/projectes/'+projecte+'.qgs'
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
        
    # def obrirEnQgis(self, projecte):
    #     QDesktopServices().openUrl(QUrl('d:/dropbox/qvistaProd/'+projecte))


    def obrirEnQgis(self, projecte):
        
        def obertura():
            try:
                QDesktopServices().openUrl(QUrl('d:/dropbox/qvistaProd/'+projecte)) 
            except:
                pass
        return obertura


    def obrirEnQVista(self, projecte):
        def obertura():
            try:
                self.projectQgis.read('d:/dropbox/qvistaProd/'+projecte)
                self.labelProjecte.setText(self.projectQgis.title())
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
        liniaCerca = QLineEdit()

        lytCapcalera.addWidget(titol)
        lytCapcalera.addWidget(liniaCerca)


        scrollFull = QScrollArea()
        frame = QFrame()
        scrollFull.setWidget(frame)
        layoutFrame = QHBoxLayout(frame)
        layoutFrame.setAlignment(Qt.AlignLeft)
        frame.setLayout(layoutFrame)

        frame.setGeometry(10,10,4000,900)
        frame.setMaximumHeight(900)
        frame.setMinimumHeight(900)

        # frame.show()

        projectes = ['fotos', 
                    'bcn11_nord',
                    'gats'
                    'equipaments',
                    ]

        projectesUrb = ['Sentencies',
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
                    
        projectesInf = ['NombreAparcaments',
                    'Carrils bici i zones 30',
                    'CoberturaVegetal',
                    'obres',
                    'cams_VideoVigilancia_v01']
        qvColumnaCataleg = QvColumnaCataleg('Mapes generals', projectes, self.projectQgis, self.labelProjecte)
        qvColumnaCataleg2 = QvColumnaCataleg('Urbanisme', projectesUrb, self.projectQgis, self.labelProjecte)
        qvColumnaCataleg3 = QvColumnaCataleg('Infraestructures', projectesInf, self.projectQgis, self.labelProjecte)
        # qvColumnaCataleg82 = QvColumnaCataleg('Animals, gats i fures', projectes)
        # qvColumnaCataleg83 = QvColumnaCataleg('Obres de ciutat', projectes)
        # qvColumnaCataleg9 = QvColumnaCataleg('Topografia', projectes)
        # qvColumnaCataleg92 = QvColumnaCataleg('Cosmologiade ciutat', projectes)
        layoutFrame.addWidget(qvColumnaCataleg)
        layoutFrame.addWidget(qvColumnaCataleg2)
        layoutFrame.addWidget(qvColumnaCataleg3)
        # layoutFrame.addWidget(qvColumnaCataleg9)
        # layoutFrame.addWidget(qvColumnaCataleg92)
        # layoutFrame.addWidget(qvColumnaCataleg82)
        # layoutFrame.addWidget(qvColumnaCataleg83)


        # qvColumnaCataleg.show()

        layoutWidgetPrincipal.addWidget(frameCapcalera)
        layoutWidgetPrincipal.addWidget(scrollFull)
        self.show()


if __name__ == "__main__":
    with qgisapp() as app:

        cataleg = QvCataleg()
        cataleg.showMaximized()

