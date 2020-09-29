import μqVista_ui
import configuracioQvista
from moduls.QvApp import QvApp
from moduls.QvCanvas import QvCanvas
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvMapetaBrujulado import QvMapetaBrujulado
from moduls.QvConstants import QvConstants

from qgis.PyQt.QtWidgets import QMainWindow, QStyleFactory, QDockWidget, QLabel, QMenu
from qgis.PyQt.QtGui import QIcon, QColor, QPixmap, QPainter, QPen, QFont
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsLayerTreeMapCanvasBridge

import os


class μqVista(QMainWindow, μqVista_ui.Ui_MainWindow):
    def __init__(self, prjInicial):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('μqVista')

        QgsProject.instance().read(prjInicial)

        self.prepararCanvas()
        self.prepararTaulaAtributs()
        self.prepararLlegenda()
        self.prepararMapeta()
        self.prepararMenu()


    def prepararCanvas(self):
        llistaBotons = ['streetview','apuntar', 'zoomIn', 'zoomOut', 'panning', 'centrar', 'enrere', 'endavant', 'maximitza']
        self.canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True, pare=self)
        self.canvas.canviMaximitza.connect(self.ferGran)
        self.canvas.desMaximitza.connect(self.desmaximitza)

        self.canvas.setCanvasColor(QColor(253,253,255))
        self.canvas.xyCoordinates.connect(self.showXY)     
        self.canvas.scaleChanged.connect(self.showScale)   
        self.canvas.scaleChanged.connect(self.corrijoScale)   

        self.canvas.mapCanvasRefreshed.connect(self.canvasRefrescat)
        # self.layout = QVBoxLayout(self.frameCentral)
    
        self.layCentral.setContentsMargins(0,0,0,0)
        self.layCentral.addWidget(self.canvas)

        self.root = QgsProject.instance().layerTreeRoot()
        QgsLayerTreeMapCanvasBridge(self.root, self.canvas)
    def prepararTaulaAtributs(self):
        """ 
        Es prepara la taula d'Atributs sobre un dockWidget.
        """
        self.taulesAtributs = QvAtributs(self.canvas)
        self.dwTaulaAtributs = QDockWidget( "Taula de dades", self )
        self.dwTaulaAtributs.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwTaulaAtributs.hide()
        self.dwTaulaAtributs.setObjectName( "taulaAtributs" )
        self.dwTaulaAtributs.setAllowedAreas( Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea )
        self.dwTaulaAtributs.setWidget( self.taulesAtributs)
        self.dwTaulaAtributs.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.BottomDockWidgetArea, self.dwTaulaAtributs)
    def prepararLlegenda(self):
        self.llegenda = QvLlegenda(self.canvas, self.taulesAtributs)
        self.llegenda.currentLayerChanged.connect(self.canviLayer)
        self.llegenda.projecteModificat.connect(lambda: self.setDirtyBit(True)) #Activa el dirty bit al fer servir el dwPrint (i no hauria)
        self.canvas.setLlegenda(self.llegenda)
        self.llegenda.setStyleSheet("QvLlegenda {color: #38474f; background-color: #F9F9F9; border: 0px solid red;}")
        # self.layoutFrameLlegenda.addWidget(self.llegenda)
        # self.llegenda.accions.afegirAccio("Opcions de visualització", self.actPropietatsLayer)

        # self.llegenda.accions.afegirAccio('actTot', self.actFerGran)
        # self.llegenda.clicatMenuContexte.connect(self.menuLlegenda)
        self.llegenda.obertaTaulaAtributs.connect(self.dwTaulaAtributs.show)
        
        self.dwLlegenda = QDockWidget( "Llegenda", self )
        self.dwLlegenda.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwLlegenda.setObjectName( "layers" )
        self.dwLlegenda.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwLlegenda.setContentsMargins ( 0,0,0,0)

        # El 230 de la següent instrucció és empiric, i caldria fer-lo dependre de la'amplada de la llegenda que es carrega.
        self.dwLlegenda.setMinimumWidth(230*QvApp().zoomFactor())
        self.dwLlegenda.setMaximumWidth(9999)
        self.addDockWidget( Qt.LeftDockWidgetArea , self.dwLlegenda )
        self.dwLlegenda.setWidget(self.llegenda)
        # self.dwLlegenda.setWindowFlag(Qt.Window)
        self.dwLlegenda.show()
    def prepararMapeta(self):
        self.mapetaDefaultPng= "mapesOffline/default.png"
        self.mapeta  = QvMapetaBrujulado(self.mapetaDefaultPng, self.canvas,  pare=self.canvas, mapeta_default="mapesOffline/default.png")

        self.mapeta.setGraphicsEffect(QvConstants.ombra(self,radius=30,color=QvConstants.COLOROMBRA))
        self.mapeta.Sig_MuestraMapeta.connect(self.editarOrientacio)
        

        self.mapeta.setParent(self.canvas)
        self.mapeta.move(20,20)
        self.mapeta.show()
        self.mapetaVisible = True
    def prepararMenu(self):
        lblLogoQVista = QLabel()
        lblLogoQVista.setMaximumHeight(40)
        lblLogoQVista.setMinimumHeight(40)
        sizeWidget=self.dwLlegenda.width()
        lblLogoQVista.setMaximumWidth(sizeWidget)
        lblLogoQVista.setMinimumWidth(sizeWidget)
        
        imatge = QPixmap(os.path.join(configuracioQvista.imatgesDir,'qVistaLogo_text_40.png'))
        p = QPainter(imatge) 
        p.setPen(QPen(Qt.white))
        p.setFont(QFont("Arial", 12, QFont.Medium))
        p.drawText(106,26, configuracioQvista.versio)
        p.end()

        lblLogoQVista.setPixmap(imatge)
        lblLogoQVista.setScaledContents(False)

        self.menuBar().setCornerWidget(lblLogoQVista,Qt.TopLeftCorner)
        self.menuBar().setFont(QvConstants.FONTTITOLS)
        menus = self.menuBar().findChildren(QMenu)
        for x in menus:
            x.setFont(QvConstants.FONTSUBTITOLS)
    def ferGran(self):
        pass
    def desmaximitza(self):
        pass
    def showXY(self, xy):
        pass
    def showScale(self, scale):
        pass
    def corrijoScale(self, scale):
        pass
    def canvasRefrescat(self):
        pass
    def canviLayer(self):
        pass
    def editarOrientacio(self):
        pass

if __name__=='__main__':
    with qgisapp(sysexit=False) as app:
        QvApp().carregaIdioma(app,'ca')
        
        # Splash?

        app.setWindowIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'QVistaLogo_256.png')))

        with open('style.qss') as st:
            app.setStyleSheet(st.read())

        ok = QvApp().logInici()            # Por defecto: family='QVISTA', logname='DESKTOP'
        if not ok:
            print('ERROR LOG >>', QvApp().logError())
        
        app.setStyle(QStyleFactory.create('fusion'))

        qV = μqVista(configuracioQvista.projecteInicial)
        qV.showMaximized()

        # QvApp().logRegistre('LOG_TEMPS', qV.lblTempsArrencada.text())