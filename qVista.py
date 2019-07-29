# -*- coding: utf-8 -*-

# Inici del cronòmetre
import time

startGlobal = time.time()

# Fitxer principal de importació de llibreries
from moduls.QvImports import *

# Carrega de moduls Qv
iniciTempsModuls = time.time()

from moduls.QvUbicacions import QvUbicacions
from moduls.QvPrint import QvPrint
from moduls.QvCanvas import QvCanvas
from moduls.QvEinesGrafiques import QvSeleccioElement, QvSeleccioPerPoligon, QvSeleccioCercle, QvSeleccioPunt
from moduls.QvStreetView import QvStreetView
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvMapeta import QvMapeta
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QVDistrictesBarris import QVDistrictesBarris
from moduls.QvCatalegPetit import QvCataleg
from moduls.QvApp import QvApp
from moduls.QvLectorCsv import QvLectorCsv
from moduls.QvPavimentacio import DockPavim
from moduls.QvMarxesCiutat import MarxesCiutat
from moduls.QvToolTip import QvToolTip
from moduls.QvDropFiles import QvDropFiles
from moduls.QvNews import QvNews
from moduls.QvPushButton import QvPushButton
from moduls.QvGeocod import QvGeocod
from moduls.QvSuggeriments import QvSuggeriments
from moduls.QvCarregaCsv import QvCarregaCsv
from moduls.QvConstants import QvConstants
from moduls.QvAvis import QvAvis
from moduls.QvToolButton import QvToolButton
from moduls.QvMenuBar import QvMenuBar
from moduls.QvVideo import QvVideo
from moduls.QvNouMapa import QvNouMapa
from moduls.QvVisorHTML import QvVisorHTML
from moduls.QvDocumentacio import QvDocumentacio
import re
import csv
import os
from pathlib import Path
import functools #Eines de funcions, per exemple per avaluar-ne parcialment una
from PyQt5.QtGui import QPainter
# Impressió del temps de carrega dels moduls Qv
print ('Temps de carrega dels moduls Qv:', time.time()-iniciTempsModuls)

# Variable global sobre la que instanciarem la classe qVista
global qV

# Classes auxiliars 
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Raised)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

# Classe principal QVista

class QVista(QMainWindow, Ui_MainWindow):
    """
    Aquesta és la classe principal del QVista. 

    La finestra te com a widget central un frame sobre el que carreguerem el canvas.
    A més, a la part superior conté una botonera de funcions.

    Des de programa definirem la status bar, sobre la que indicarem escala, projecte i coordenades, 
            així com un tip de les accions que s'executen.
    """
    
    keyPressed = pyqtSignal(int)
        
    def __init__(self,app):
        """  Inicialització de QVista.
        
            Aquí fem:
            - Definir variables de la classe.
            - Instanciem canvas i l'associem a un frame.
            - Instanciem projecte i carreguem el projecte Inicial
            - Crida a funcions de:
                - Definició d'accions
                - Definició de menús de la barra superior de la finestra
                - Assignació d'accions a botons i menus
                - Preparació de:
                        llegenda
                        taula d'atributs
                        botonera lateral
                        cercador postal
                        cataleg
                        ubicacions
        
        """
        QMainWindow.__init__(self)
        self.setupUi(self)
        app.setFont(QvConstants.FONTTEXT)
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.actualitzaWindowFlags()
        # self.verticalLayout.addWidget(QSizeGrip(self),0,Qt.AlignBottom | Qt.AlignRight)

        self.app=app
        #Afegim títol a la finestra
        self.setWindowTitle(titolFinestra)

        

        # Definició dels labels de la statusBar 
        self.definirLabelsStatus()   

        # Preparació deprojecte i canvas
        self.preparacioEntornGrafic()

        # Connectar progressBar del canvas a la statusBar
        self.connectarProgressBarCanvas()


        # Inicialitzacions
        self.printActiu = False
        self.qvPrint = 0
        self.mapesOberts = False
        self.primerCop = True
        self.mapaMaxim = False
        self.layerActiu = None
        self.prepararCercador = True
        self.lblMovie = None        
        self.ubicacions= None
        self.cAdrec= None

        #Preparem el mapeta abans de les accions, ja que el necessitarem allà
        self.preparacioMapeta()

        # # Connectors i accions
        self.definicioAccions()
        
        # # Menus i preparació labels statusBar
        self.definirMenus()

        # self.keyPressed.connect(self.fesMapaMaxim)

        # Preparació botonera, mapeta, llegenda, taula d'atributs, etc.
        self.botoneraLateral()
        self.preparacioTaulaAtributs()
        self.preparacioLlegenda()
        self.preparacioArbreDistrictes()
        self.preparacioCataleg()
       
        # self.preparacioMapTips()
        self.preparacioImpressio()
        # self.preparacioGrafiques()
        self.preparacioSeleccio()
        # self.preparacioEntorns()
        

        # Eina inicial del mapa = Panning
        self.canvas.panCanvas()

        # Preparació d'una marca sobre el mapa. S'utilitzarà per cerca d'adreces i street view
        self.marcaLloc = QgsVertexMarker(self.canvas)
        self.marcaLlocPosada = False

        # Guardem el dashboard actiu per poder activar/desactivar després els dashboards
        self.dashboardActiu = [self.canvas, self.frameLlegenda, self.mapeta]

        # Aquestes línies son necesaries per que funcionin bé els widgets de qGis, com ara la fitxa d'atributs
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
        
        
        # Final del cronometratge d'arrancada
        endGlobal = time.time()
        self.tempsTotal = endGlobal - startGlobal
        print ('Total carrega abans projecte: ', self.tempsTotal)

        
        
        
        # ponemos el gpkd a readonly....
        import win32con, win32api,os
        elGpkg=projecteInicial
        pre, ext = os.path.splitext(elGpkg)
        elGpkg= pre + '.gpkg'
        win32api.SetFileAttributes(elGpkg,win32con.FILE_ATTRIBUTE_READONLY)
      



        # Carrega del projecte inicial
        self.obrirProjecte(projecteInicial)

        # Final del cronometratge de carrega de projecte
        endGlobal = time.time()
        self.tempsTotal = endGlobal - startGlobal
        print ('Total carrega després projecte: ', self.tempsTotal)

        # S'escriu el temps calculat d'arrencada sobre la label de la status bar
        self.lblTempsArrencada = QLabel()
        self.lblTempsArrencada.setFrameStyle( QFrame.StyledPanel )
        self.lblTempsArrencada.setMinimumWidth( 170 )
        self.lblTempsArrencada.setAlignment( Qt.AlignCenter )
        self.statusbar.setSizeGripEnabled( True )
        # self.statusbar.addPermanentWidget( self.lblTempsArrencada, 0 )
        self.lblTempsArrencada.setText ("Segons per arrencar: "+str('%.1f'%self.tempsTotal))

        # Drop d'arxius -> Canvas i Llegenda
        # Es permet 1 arxiu de projecte o bé N arxius de capes
        self.dropLlegenda = QvDropFiles(self.llegenda, ['.qgs', '.qgz'], ['.qlr', '.shp', '.csv', '.gpkg'])
        self.dropLlegenda.arxiusPerProcessar.connect(self.obrirArxiu)
        self.dropCanvas = QvDropFiles(self.canvas, ['.qgs', '.qgz'], ['.qlr', '.shp', '.csv', '.gpkg'])
        self.dropCanvas.arxiusPerProcessar.connect(self.obrirArxiu)

        # self.setMouseTracking(False) 

        self.oldPos = self.pos() #Per quan vulguem moure la finestra

        #Això abans ho feia al ferGran. Però allà no està bé fer-ho. Ho deixo aquí i ja ho mourem
        self.frameLlegenda.hide()
        self.frame_11.hide()
        self.dwLlegenda = QDockWidget( "Llegenda", self )
        self.dwLlegenda.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwLlegenda.setObjectName( "layers" )
        self.dwLlegenda.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwLlegenda.setContentsMargins ( 0,0,0,0)
        self.addDockWidget( Qt.LeftDockWidgetArea , self.dwLlegenda )
        self.dwLlegenda.setWidget(self.llegenda)
        self.dwLlegenda.show()
        self.ferGran()

    

    # Fins aquí teniem la inicialització de la classe. Ara venen les funcions, o métodes, de la classe. 

    def obrirArxiu(self, llista):
        """Obre una llista d'arxius (projectes i capas) passada com a parametre
        
        Arguments:
            llista d'arxius (List[String]) -- Noms (amb path) del projecte o capes a obrir        
        """
        for nfile in llista:
            _, fext = os.path.splitext(nfile)
            fext = fext.lower()
            if fext in ('.qgs', '.qgz'):
                self.obrirProjecte(nfile, self.canvas.extent())
            elif fext == '.qlr':
                afegirQlr(nfile)
            elif fext in ('.shp', '.gpkg'):
                layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
                if layer.isValid():
                    self.project.addMapLayer(layer)
                    self.setDirtyBit()
            elif fext == '.csv':
                carregarLayerCSV(nfile)

    def obrirProjecte(self, projecte, rang = None):
        """Obre un projecte passat com a parametre, amb un possible rang predeterminat.
        
        Arguments:
            projecte {String} -- Nom (amb path) del projecte a obrir
        
        Keyword Arguments:
            rang {Rect} -- El rang amb el que s'ha d'obrir el projecte (default: {None})
        """
        if projecte.strip()=='': return
        # Obrir el projecte i col.locarse en rang
        self.project.read(projecte)
        self.pathProjecteActual = projecte
        if self.project.title().strip()=='':
            # self.project.setTitle(os.path.basename(projecte))
            self.project.setTitle(Path(projecte).stem)
            self.lblTitolProjecte.setText(self.project.title())
        # self.canvisPendents = False #es el bit Dirty que ens diu si hem de guardar al tancar o no
        self.setDirtyBit(False)
        self.canvas.refresh()

        if rang is not None:
            self.canvas.setExtent(rang)

        # Labels de la statusbar (Projecció i nom del projecte)
        self.lblProjeccio.setText(self.project.crs().description())
        self.lblProjecte.setText(self.project.baseName())
        self.lblProjecte.setToolTip(self.project.fileName())
        if self.canvas.rotation() == 0:
            self.bOrientacio.setText(' Orientació: Nord')
        else:
            self.bOrientacio.setText(' Orientació: Eixample')
            

        # Titol del projecte 
        # self.lblTitolProjecte.setFont(QvConstants.FONTTITOLS)
        # self.lblTitolProjecte.setText(self.project.title())


        if self.llegenda.player is None:
            self.llegenda.setPlayer('imatges/Spinner_2.gif', 150, 150)
        self.actualitzaMapesRecents(self.pathProjecteActual)

        
        metadades=Path(self.pathProjecteActual).with_suffix('.htm')
        if os.path.isfile(metadades):
            def obrirMetadades():
                visor=QvVisorHTML(metadades,'Informació del mapa',logo=False,parent=self)
                visor.exec_()
            self.botoMetadades.show()
            self.botoMetadades.clicked.connect(obrirMetadades)
        else:
            self.botoMetadades.hide()

        # self.metadata = self.project.metadata()
        # print ('Author: '+self.metadata.author())

        # dashboard = QgsExpressionContextUtils.projectScope(self.project).variable('qV_dashboard')
        # titolEntorn = QgsExpressionContextUtils.projectScope(self.project).variable('qV_titolEntorn')

        # if dashboard is not None:
        #     exec("self.act{}.trigger()".format(dashboard))

        # if titolEntorn is not None:
        #     self.lblTirotattolProjecte.setText(titolEntorn)
    
    def startMovie(self):
        self.player = QvVideo("Imatges/Spinner_2.gif", 160, 160)
        self.player_ = QvConstants.afegeixOmbraWidget(self.player)
        self.player.setModal(True)
        self.player.activateWindow()
        self.player.show()
        self.player.mediaPlayer.play()

    def stopMovie(self):
        self.player.hide()
        self.player.mediaPlayer.pause()


    def keyPressEvent(self, event):
        """ Defineix les actuacions del qVista en funció de la tecla apretada.
        """
        # print (event.key())
        if event.key() == Qt.Key_F1:
            print ('Help')
        if event.key() == Qt.Key_F3:
            print('Cercar')
        if event.key() == Qt.Key_F11:
            self.ferGran()
        if event.key() == Qt.Key_F5:
            self.canvas.refresh()
            print('refresh')

    def botoLateral(self, text = None, tamany = 40, imatge = None, accio=None):
        """Crea un boto per a la botonera lateral.
       
        Keyword Arguments:
            text {[str]} -- [El text del botó, si en té] (default: {None})
            tamany {int} -- [tamany del botó (és quadrat)] (default: {40})
            imatge {[QImage]} -- [La imatge, si en té. Ara estem fent servir la imatge associada a l'acció, no aquesta] (default: {None})
            accio {[QAction]} -- [Una QAction associada al botó] (default: {None})
        
        """
        #Passem de QToolButton a QvPushButton pla
        #El codi queda una mica més guarro, però funciona bé
        boto = QvToolButton()
        # boto = QvPushButton(flat=True)
        boto.setMinimumHeight(tamany)
        boto.setMaximumHeight(tamany)
        boto.setMinimumWidth(tamany)
        boto.setMinimumWidth(tamany)
        boto.setDefaultAction(accio)
        boto.setIconSize(QSize(tamany, tamany))
        # if accio is not None: boto.setToolTip(accio.toolTip())
        #Si ens especifica una icona concreta, la posem. Si no, posem la icona de l'acció (si en té)
        if imatge is not None:
            icon = QIcon(imatge)
            boto.setIcon(icon)
        # elif accio is not None:
        #     boto.setIcon(accio.icon())
        # boto.clicked.connect(accio)
        self.lytBotoneraLateral.addWidget(boto)
        return boto

    def botoneraLateral(self):
        """Aquesta funció construeix la botonera lateral. 

        A dins de la funció hi ha la creació de dades per cada botó.

        TODO: Extreure les dades de construcció de la botonera fora. No crític.
        """

        self.lytBotoneraLateral.setAlignment(Qt.AlignTop)
        self.lytBotoneraLateral.setContentsMargins(6,4,4,4)

        # Botons i espaiadors.
        # self.bFerGran = self.botoLateral(tamany = 25, accio=self.actFerGran)

        # spacer = QSpacerItem(50, 50, QSizePolicy.Expanding,QSizePolicy.Maximum)
        # self.lytBotoneraLateral.addItem(spacer)

        self.bUbicacions = self.botoLateral(tamany = 25, accio=self.actAdreces)
        #self.bCataleg = self.botoLateral(tamany = 25, accio=self.actObrirCataleg)
        #self.bCatalegProjectesLlista = self.botoLateral(tamany = 25, accio=self.actObrirCatalegProjectesLlista)
        #self.bObrirEnQgis = self.botoLateral(tamany = 25, accio=self.actObrirEnQgis)
        self.bFoto =  self.botoLateral(tamany = 25, accio=self.actCanvasImg)
        self.bImprimir =  self.botoLateral(tamany = 25, accio=self.actImprimir)
        self.bTissores = self.botoLateral(tamany = 25, accio=self.actTissores)
        self.bSeleccioGrafica = self.botoLateral(tamany = 25, accio=self.actSeleccioGrafica)

        spacer2 = QSpacerItem(1000, 1000, QSizePolicy.Expanding,QSizePolicy.Maximum)
        self.lytBotoneraLateral.addItem(spacer2)
        
        self.qvNews = QvNews()
        self.bInfo = self.botoLateral(tamany = 25, accio=self.qvNews)
        # self.bInfo = self.botoLateral(tamany = 25, accio=self.actInfo)
        self.bHelp = self.botoLateral(tamany = 25, accio=self.actHelp)
        self.bBug = self.botoLateral(tamany = 25, accio=self.actBug)
        # self.bDashStandard = self.botoLateral(tamany = 25, accio=self.actDashStandard)
    
    # Funcions de preparació d'entorns 
    def preparacioStreetView(self):
        """Preparació de Street View a través de QvStreetView, i el dockwidget associat.
        """

        self.qvSv = QvStreetView(self.canvas, self)
        self.canvas.setStreetView(self.qvSv)
        self.canvas.setMapTool(self.qvSv.rp)
        # qvSv.setContentsMargins(0,0,0,0)
        self.qvSv.hide()
        # self.qvSv.qbrowser.show()
        self.dwSV = QDockWidget( "Street View", self )
        self.dwSV.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwSV.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwSV.setWidget(self.qvSv)
        self.dwSV.setContentsMargins ( 0, 0, 0, 0 )
        self.dwSV.hide()
        self.dwSV.visibilityChanged.connect(self.streetViewTancat)
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwSV)
        self.dwSV.setFloating(True)
        self.dwSV.move(575,175)

    def preparacioEntornGrafic(self):
        # Canvas
        #llistaBotons = ['apuntar', 'zoomIn', 'zoomOut', 'panning', 'centrar']
        llistaBotons = ['streetview','apuntar', 'zoomIn', 'zoomOut', 'panning', 'centrar', 'enrere', 'endavant', 'maximitza']
        
        self.canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True, pare=self)

        self.preparacioStreetView()     #fa el qvSv. necessita el canvas
        self.canvas.bstreetview.clicked.connect(self.qvSv.segueixBoto)

        self.canvas.setCanvasColor(QColor(253,253,255))
        self.canvas.setAnnotationsVisible(True)

        self.canvas.xyCoordinates.connect(self.showXY)     
        self.showXY(self.canvas.center())
        self.canvas.scaleChanged.connect(self.showScale)   
        self.canvas.mapCanvasRefreshed.connect(self.canvasRefrescat)

       

        self.layout = QVBoxLayout(self.frameCentral)
        

        self.layout.setContentsMargins(0,0,0,0)
        # self.layout.addWidget(self.botonera1)

        self.layout.addWidget(self.canvas)
        self.layoutDelsCanvasExtra = QHBoxLayout()
        self.layout.addLayout(self.layoutDelsCanvasExtra)


        
        # Definició de rubberbands i markers
        self.rubberband = QgsRubberBand(self.canvas)
        self.markers = QgsVertexMarker(self.canvas)

        # Instancia del projecte i associació canvas-projecte
        self.project = QgsProject.instance()
        self.root = QgsProject.instance().layerTreeRoot()

        self.bridge = QgsLayerTreeMapCanvasBridge(self.root, self.canvas)
        # self.bridge.setCanvasLayers()
        # self.leTitolProjecte=QLineEdit(self.frame_12)
        self.leTitolProjecte.hide() #El lineEdit estarà visible només quan anem a editar
        self.lblTitolProjecte.clicked.connect(self.editarTitol)
        self.leTitolProjecte.editingFinished.connect(self.titolEditat)

    def editarTitol(self):
        self.lblTitolProjecte.hide()
        self.leTitolProjecte.show()
        self.leTitolProjecte.setText(self.lblTitolProjecte.text())
        self.leTitolProjecte.setFocus(True)
        self.titolAnterior=self.lblTitolProjecte.text()
    def titolEditat(self):
        self.lblTitolProjecte.show()
        self.leTitolProjecte.hide()
        self.lblTitolProjecte.setText(self.leTitolProjecte.text())
        self.project.setTitle(self.leTitolProjecte.text())
        if self.titolAnterior!=self.leTitolProjecte.text(): 
            self.setDirtyBit()
    def setDirtyBit(self,bit=True):
        if bit:
            self.canvisPendents=True
            self.botoDesarProjecte.setIcon(self.iconaAmbCanvisPendents)
        else:
            self.canvisPendents=False
            self.botoDesarProjecte.setIcon(self.iconaSenseCanvisPendents)
    def canvasRefrescat(self):
        if self.marcaLlocPosada:
            self.marcaLlocPosada = False
        else:
            self.canvas.scene().removeItem(self.marcaLloc)
            
    # def preparacioCalculadora(self):
    #     self.calculadora = QWidget()

    #     self.calculadora.ui = Ui_Calculadora()
    #     self.calculadora.ui.setupUi(self.calculadora)
    #     self.calculadora.show()
    #     self.calculadora.ui.bLayersFields.clicked.connect(recorrerLayersFields)
    #     self.calculadora.ui.bFieldsCalculadora.clicked.connect(carregarFieldsCalculadora)

    def preparacioUbicacions(self):
        """
        Prepara el widget d'ubicacions, i el coloca en un dock widget, que s'inicialitza en modus hide.
        """

        self.wUbicacions = QvUbicacions(self.canvas)
        # self.wUbicacions.hide()
        self.dwUbicacions = QDockWidget( "Ubicacions", self )
        self.dwUbicacions.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwUbicacions.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwUbicacions.setWidget( self.wUbicacions)
        self.dwUbicacions.setContentsMargins ( 1, 1, 1, 1 )
        self.dwUbicacions.hide()
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwUbicacions)

    def preparacioAnotacions(self):
        self.an = QvAnotacions(self.canvas)
        self.an.show()
    
    def preparacioArbreDistrictes(self):
        """Es genera un dockWidget a la dreta, amb un arbre posicionador Districte-Barri.

        Ho fem instanciant la classe QVDistrictesBarris. 
        També connectem un click al arbre amb la funció clickArbre.
        """

        self.distBarris = QVDistrictesBarris()
        self.distBarris.view.clicked.connect(self.clickArbre)
        
        # self.dwArbreDistrictes = QDockWidget("Districtes - Barris", self)
        # self.dwArbreDistrictes.hide()
        # self.dwArbreDistrictes.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        # self.dwArbreDistrictes.setWidget( self.distBarris.view )
        # self.dwArbreDistrictes.setContentsMargins ( 2, 2, 2, 2 )
        # self.addDockWidget( Qt.RightDockWidgetArea, self.dwArbreDistrictes )

    def preparacioCataleg(self):
        """ 
        Genera el cataleg del qVista i l'incorpora a un docWidget.
        
        - Instanciem un widget i l'inicialitcem amb el ui importat. 

        - Li donem titol i el fem visible.

        - Després generem un dockWidget i el posem a la esquerra, invisible.

        - Omplim el widget de les dades llegides a carpetaCataleg
        """
        self.wCataleg = QWidget()
        self.wCataleg.ui = Ui_Cataleg()
        self.wCataleg.ui.setupUi(self.wCataleg)
        self.wCataleg.setWindowTitle("Cataleg d'Informació Territorial")
        # self.wCataleg.show()

        self.dwCataleg = QDockWidget( "Cataleg de capes", self )
        self.dwCataleg.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwCataleg.setObjectName( "catalegTaula" )
        self.dwCataleg.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwCataleg.setWidget(self.wCataleg)
        self.dwCataleg.setContentsMargins ( 0,0,0,0 )
        self.dwCataleg.hide()
        self.addDockWidget( Qt.LeftDockWidgetArea, self.dwCataleg)
        self.cataleg()


        self.wCatalegProjectesLlista = QWidget()
        self.wCatalegProjectesLlista.ui = Ui_Cataleg()
        self.wCatalegProjectesLlista.ui.setupUi(self.wCatalegProjectesLlista)
        self.wCatalegProjectesLlista.setWindowTitle("Cataleg d'Informació Territorial")
        # self.wCataleg.show()
        #dfgdfgdfg

        self.dwCatalegProjectesLlista = QDockWidget( "Cataleg de mapes", self )
        self.dwCatalegProjectesLlista.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwCatalegProjectesLlista.setObjectName( "catalegTaula2" )
        self.dwCatalegProjectesLlista.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwCatalegProjectesLlista.setWidget(self.wCatalegProjectesLlista)
        self.dwCatalegProjectesLlista.setContentsMargins ( 0,0,0,0 )
        self.dwCatalegProjectesLlista.hide()
        self.addDockWidget( Qt.LeftDockWidgetArea, self.dwCatalegProjectesLlista)
        self.catalegProjectesLlista()

    def preparacioCercadorPostal(self):
    
        """
        Un frame suelto, de prova, sobre el que van dos lineEdits, pel carrer i el número.
        Després instanciem el cercador d'adreces. 
        Connectem la senyal sHanTrobatCoordenades a trobatNumero_oNo.
        """

        # instanciamos clases necesarias    
        self.fCercador=QFrame()
        self.bottomWidget = QWidget()
        self.ubicacions = QvUbicacions(self.canvas, pare=self)
        self.splitter = QSplitter(Qt.Vertical)             #para separar ubicacion de distBarris
        self.layoutAdreca = QHBoxLayout()                  #Creamos layout, caja de diseño Horizontal
        self.layoutCercador = QVBoxLayout(self.fCercador)  #Creamos layout, caja de diseño Vertical
        self.layoutbottom = QVBoxLayout()                  #Creamos layout, caja de diseño 8Vertical

        #Elementos para layout H, del cercador

        self.lblCercadorCarrer = QLabel('    Carrer:')    #etiqueta Carrer
        self.lblCercadorNum = QLabel('Num:')              #etiqueta Num        
        self.leCarrer=QLineEdit()                           #Edit calle
        self.leCarrer.setToolTip('Introdueix adreça i selecciona de la llista')
        self.leCarrer.setMinimumWidth(200) 
        self.leNumero=QLineEdit()                           #Edit numero
        self.leNumero.setToolTip('Introdueix número, selecciona de la llista i prem RETURN')
        self.leNumero.setMaximumWidth(50)                   #Tamaño numero
        self.leNumero.setMinimumWidth(50)
        # self.leNumero.setDisabled(True)



        self.boton_bajar= QvPushButton(flat=True)
        self.boton_bajar.clicked.connect(self.CopiarA_Ubicacions)
        self.boton_bajar.setIcon(QIcon('imatges/down3-512.png'))
        self.boton_bajar.setMinimumHeight(25)
        self.boton_bajar.setMaximumHeight(25)
        self.boton_bajar.setMinimumWidth(25)
        self.boton_bajar.setMaximumWidth(25)
        self.boton_bajar.setToolTip("Copiar aquest carrer i aquest número a l'arbre d'ubicacións")

        #boton invoc_streer
        self.boton_invocarStreetView= QvPushButton(flat=True)
        self.boton_invocarStreetView.clicked.connect(self.invocarStreetView)
        self.boton_invocarStreetView.setIcon(QIcon('imatges/littleMan.png'))
        self.boton_invocarStreetView.setMinimumHeight(25)
        self.boton_invocarStreetView.setMaximumHeight(25)
        self.boton_invocarStreetView.setMinimumWidth(25)
        self.boton_invocarStreetView.setMaximumWidth(25)
        self.boton_invocarStreetView.setToolTip("Mostrar aquest carrer i aquest número en StreetView")

        self.layoutbottom.addWidget(QHLine())
        self.layoutbottom.addWidget(self.distBarris.view)
        self.bottomWidget.setLayout(self.layoutbottom)

        # llenamos layout horizontal de adreca
        self.layoutAdreca.addWidget(self.lblCercadorCarrer)
        self.layoutAdreca.addWidget(self.leCarrer)
        self.layoutAdreca.addWidget(self.lblCercadorNum)
        self.layoutAdreca.addWidget(self.leNumero)
        self.layoutAdreca.addWidget(self.boton_bajar)
        self.layoutAdreca.addWidget(self.boton_invocarStreetView)


        # llenamos splitter        
        self.splitter.addWidget(self.ubicacions)
        self.splitter.addWidget(self.bottomWidget)
        self.splitter.setContentsMargins(1,1,1,1)

        # llenamos layout cercador V con layout de adreca H
        self.layoutCercador.addLayout(self.layoutAdreca)
        self.layoutCercador.addWidget(self.splitter)

        self.fCercador.setLayout(self.layoutCercador)      #Asignamos a Frame layout        

        self.setTabOrder(self.leCarrer, self.leNumero)
        # Activem la clase de cerca d'adreces
        self.cAdrec=QCercadorAdreca(self.leCarrer, self.leNumero,'SQLITE')    # SQLITE o CSV
          
        self.cAdrec.sHanTrobatCoordenades.connect(self.trobatNumero_oNo) 

        self.dwCercador = QDockWidget( "Cercador", self )
        self.dwCercador.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwCercador.hide()
        self.dwCercador.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwCercador.setWidget( self.fCercador)
        self.dwCercador.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwCercador)

    def CopiarA_Ubicacions(self):       
         # self.ubicacions.leUbicacions.setText("->"+self.leCarrer.text()+"  "+self.leNumero.text())
        if self.cAdrec.NumeroOficial=='0':
            self.cAdrec.NumeroOficial=''

        self.ubicacions.leUbicacions.setText("->"+self.leCarrer.text()+"  "+self.cAdrec.NumeroOficial)
        self.ubicacions._novaUbicacio()


    # pillar las coordenadas y mandarlas a stretView
    def invocarStreetView(self):
        
        xx=self.cAdrec.coordAdreca[0]
        yy=self.cAdrec.coordAdreca[1]

        # xx=430537.623
        # yy=4583274.049
        
        if self.qvSv.qbrowser.isHidden():
            self.qvSv.qbrowser.show()

        if self.dwSV.isHidden():
            self.dwSV.show()
        self.qvSv.rp.llevame(xx,yy)

        self.canvas.scene().removeItem(self.marcaLloc)

        self.marcaLloc = QgsVertexMarker(self.canvas)
        self.marcaLloc.setCenter( self.cAdrec.coordAdreca )
        self.marcaLloc.setColor(QColor(255, 0, 0))
        self.marcaLloc.setIconSize(15)
        self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.marcaLloc.setPenWidth(3)
        self.marcaLloc.show()
        self.marcaLlocPosada = True

    def preparacioTaulaAtributs(self):
        """ 
        Es prepara la taula d'Atributs sobre un dockWidget.
        """
        self.taulesAtributs = QvAtributs(self.canvas)
        # self.twAtributs=QTableWidget()
        self.dwTaulaAtributs = QDockWidget( "Taula de dades", self )
        self.dwTaulaAtributs.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwTaulaAtributs.hide()
        self.dwTaulaAtributs.setObjectName( "taulaAtributs" )
        self.dwTaulaAtributs.setAllowedAreas( Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea )
        self.dwTaulaAtributs.setWidget( self.taulesAtributs)
        self.dwTaulaAtributs.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.BottomDockWidgetArea, self.dwTaulaAtributs)

    def preparacioBotonera(self):
        """ 
        Es prepara la botonera lateral sobre un dockWidget.
        """
        self.botonera = QFrame()
        self.ui = Ui_Frame()
        self.ui.setupUi(self.botonera)
        # self.botonera.show()
        self.dwBotonera = QDockWidget( "Botonera", self )
        self.dwBotonera.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwBotonera.hide()
        self.dwBotonera.setObjectName( "Botonera" )
        self.dwBotonera.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwBotonera.setWidget(self.botonera)
        self.dwBotonera.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dwBotonera)

    def preparacioNoticies(self):
        return

    def preparacioMapeta(self):
        # self.wMapeta = QtWidgets.QWidget()
        # self.wMapeta.setGeometry(0,0,267,284)
        # self.wMapeta.show()
        self.mapeta = QvMapeta(self.canvas, tamanyPetit=True, pare=self)
        self.mapeta.setGraphicsEffect(QvConstants.ombra(self,radius=30,color=QvConstants.COLORCLAR))
        self.bOrientacio.clicked.connect(self.editarOrientacio)
        self.mapeta.setParent(self.canvas)
        self.mapeta.move(20,20)
        self.mapeta.show()
        # self.dwMapeta = QDockWidget("Mapa de situació", self)
        # self.dwMapeta.setMinimumWidth(180)
        # self.dwMapeta.setMaximumWidth(180)
        # self.dwMapeta.setMaximumHeight(200)
        # self.dwMapeta.setMinimumHeight(200)
        # self.dwMapeta.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        # self.dwMapeta.setWidget(self.mapeta)
        # self.dwMapeta.setContentsMargins ( 0, 0, 0, 0 )
        # self.addDockWidget( Qt.LeftDockWidgetArea, self.dwMapeta )
        # # self.lblMapeta.show()
        # self.dwMapeta.show()
   
    def preparacioLlegenda(self):
        """Es genera un dockWidget a la dreta, amb la llegenda del projecte.
 
        Ho fem instanciant la classe QvLlegenda. 

        També connectem un click al arbre amb la funció clickArbre.

        """
        self.layoutFrameLlegenda = QVBoxLayout(self.frameLlegenda)
        self.llegenda = QvLlegenda(self.canvas, self.taulesAtributs)
        self.llegenda.currentLayerChanged.connect(self.canviLayer)
        self.llegenda.projecteModificat.connect(lambda: self.setDirtyBit(True))
        self.canvas.setLlegenda(self.llegenda)
        self.layoutFrameLlegenda.setContentsMargins ( 5, 13, 5, 0 )
        self.llegenda.setStyleSheet("QvLlegenda {color: #38474f; background-color: #F9F9F9; border: 0px solid red;}")
        self.layoutFrameLlegenda.addWidget(self.llegenda)
        self.llegenda.accions.afegirAccio('Propietats de capa', self.actPropietatsLayer)

        self.llegenda.accions.afegirAccio('actTot', self.actFerGran)
        self.llegenda.clicatMenuContexte.connect(self.menuLlegenda)
        # self.llegenda.projecteCarregat.connect(self.paraMovie)
        # self.llegenda.carregantProjecte.connect(self.startMovie)

        # self.vistaMapa1 = QvVistaMapa(self.llegenda)
        # self.vistaMapa2 = QvVistaMapa(self.llegenda)
        # self.vistaMapa3 = QvVistaMapa(self.llegenda)

        # self.frameTemes = QFrame()
        # self.layoutFrameTemes = QHBoxLayout(self.frameTemes)
        # self.frameTemes.setLayout(self.layoutFrameTemes)

        # self.layoutFrameTemes.addWidget(self.vistaMapa1)
        # self.layoutFrameTemes.addWidget(self.vistaMapa2)
        # self.layoutFrameTemes.addWidget(self.vistaMapa3)
        # self.layoutDelsCanvasExtra.addWidget(self.frameTemes)
        # self.frameTemes.hide()

        # print(self.llegenda.temes())
        
        self.llegenda.obertaTaulaAtributs.connect(self.dwTaulaAtributs.show)

        # self.dwLlegenda = QDockWidget( "Llegenda", self )
        # self.dwLlegenda.show()
        # self.dwLlegenda.setObjectName( "layers" )
        # self.dwLlegenda.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        # self.dwLlegenda.setWidget(self.llegenda)
        # self.dwLlegenda.setContentsMargins ( 2, 2, 2, 2 )
        # self.addDockWidget( Qt.LeftDockWidgetArea, self.dwLlegenda )

    # def preparacioGrafiques(self):
    #     try:
    #         self.fGrafiques = QFrame()
    #         self.lyGrafiques = QVBoxLayout(self.fGrafiques)
    #         self.fGrafiques.setLayout(self.lyGrafiques)setMouseTracking

    #         self.calculadora = QWidget()
    #         self.calculadora.ui = Ui_Calculadora()
    #         self.calculadora.ui.setupUi(self.calculadora)
    #         # self.calculadora.ui.bLayersFields.clicked.connect(self.recorrerLayersFields)
    #         # self.calculadora.ui.bFieldsCalculadora.clicked.connect(carregarFieldsCalculadora)
    #         self.calculadora.ui.bFieldsCalculadora.clicked.connect(self.ferGrafica)
    #         self.calculadora.ui.cbLayers.currentIndexChanged.connect(self.recorrerFields)
            
    #         self.calculadora.ui.lwFields.setSelectionMode(QAbstractItemView.ExtendedSelection)

    #         self.browserGrafiques = QWebView()

    #         self.dwBrowserGrafiques = QDockWidget( "Gràfiques", self )
    #         self.dwBrowserGrafiques.hide()

    #         self.dwBrowserGrafiques.setObjectName( "Gràfiques" )
    #         self.dwBrowserGrafiques.setAllowedAreas( Qt.TopDockWidgetArea |Qt.RightDockWidgetArea| Qt.BottomDockWidgetArea )
    #         self.dwBrowserGrafiques.setWidget( self.fGrafiques)
    #         self.dwBrowserGrafiques.setContentsMargins ( 0,0,0,0 )

    #         self.lyGrafiques.addWidget(self.calculadora)
    #         self.lyGrafiques.addWidget(self.browserGrafiques)
    #         self.addDockWidget( Qt.RightDockWidgetArea, self.dwBrowserGrafiques)
            
    #         self.recorrerLayersFields()
    #     except:
    #         msg = QMessageBox()
    #         msg.setIcon(QMessageBox.Warning)
            
    #         msg.setText(str(sys.exc_info()[1]))
    #         # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
    #         msg.setWindowTitle("ERROR: qVista> preparacioGrafiques")
    #         msg.setStandardButtons(QMessageBox.Close)
    #         retval = msg.exec_()
        
    def preparacioEntorns(self):
        #self.menuEntorns = self.bar.addMenu('Entorns')
                              
        self.menuEntorns.setFont(QvConstants.FONTSUBTITOLS)
        self.menuEntorns.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        for entorn in os.listdir(os.path.dirname('entorns/')):          
            if entorn == '__init__.py' or entorn[-3:] != '.py':
                pass
            else:
                # TODO: canviar el nom pel titol de la clase com a descripcio de l'acció
                tmpClass = None
                nom = entorn[:-3]
                exec('from entorns.{} import {}'.format(nom,nom))
                exec('self.act{} = QAction("{}", self)'.format(nom, nom))
                exec('self.act{}.setStatusTip("{}")'.format(nom, nom))   
                exec('self.act{}.triggered.connect(self.prepararDash({}))'.format(nom, nom))
                exec('self.menuEntorns.addAction(self.act{})'.format(nom))
        
        self.menuEntorns.addAction(self.actPavimentacio)
        self.menuEntorns.addAction(self.actMarxesCiutat)
    
    def streetViewTancat(self):
        if self.dwSV.isHidden():
            # tool = QvSeleccioElement(qV.canvas, qV.llegenda)
            # self.canvas.setMapTool(tool)
            self.canvas.panCanvas()
            self.canvas.scene().removeItem(self.qvSv.m)
        else:
            pass

    def trobatNumero_oNo(self,rsc,info_rsc):
        if rsc==0:
            self.canvas.setCenter(self.cAdrec.coordAdreca)
            self.canvas.zoomScale(1000)
            # colocación de marca (cuadradito) en lugar de ubicacion
            self.canvas.scene().removeItem(self.marcaLloc)

            self.marcaLloc = QgsVertexMarker(self.canvas)
            self.marcaLloc.setCenter( self.cAdrec.coordAdreca )
            self.marcaLloc.setColor(QColor(255, 0, 0))
            self.marcaLloc.setIconSize(15)
            self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            self.marcaLloc.setPenWidth(3)
            self.marcaLloc.show()
            self.marcaLlocPosada = True
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            
            msg.setText(info_rsc)
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("ERROR: qVista")
            msg.setDetailedText("Posa el cursor sobre els camps d'edició i segueix les instruccions.")
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()

    def adreces(self):
        if self.prepararCercador:
            self.preparacioCercadorPostal()
            self.prepararCercador = False
        self.dwCercador.show()

    def menuLlegenda(self, tipus):
        #   (Tipos: none, group, layer, symb)
        if tipus == 'layer':
            self.llegenda.menuAccions.append('separator')
            self.llegenda.menuAccions.append('Propietats de capa')
     
    def mapesTema(self):
        if self.mapesOberts:
            self.frameTemes.hide()
            self.mapesOberts = False
        else:
            self.vistaMapa1.connectaTema('NParceles', 2)
            self.vistaMapa2.connectaTema('NHabitatge', 2)
            self.vistaMapa3.connectaTema('NAparcaments', 2)
            self.frameTemes.show()
            self.mapesOberts = True

    def preparacioMapTips(self):
        
        layer = self.llegenda.currentLayer()
        self.my_tool_tip = QvToolTip(self.canvas,layer)
        self.my_tool_tip.createMapTips()

    def preparacioImpressio(self):  
        self.dwPrint = QDockWidget( "Print", self )
        self.dwPrint.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwPrint.setObjectName( "Print" )
        self.dwPrint.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwPrint.setContentsMargins ( 1, 1, 1, 1 )
        self.addDockWidget(Qt.RightDockWidgetArea, self.dwPrint)
        # self.dwPrint.setMaximumHeight(200)
        self.dwPrint.hide()

    def imprimir(self):    
        self.qvPrint = QvPrint(self.project, self.canvas, self.canvas.extent())
        self.dwPrint.setWidget(self.qvPrint)
        self.dwPrint.show()
        self.qvPrint.pucMoure = True

    def definicioAccions(self):
        """ Definició de les accions que després seran assignades a menús o botons. """

        # Obre un fitxer de tipus CSV, per veure les seves dades a una taula. 
        # Atenció, no carrega un layer, només llegeix dades del fitxer.
        self.actObrirCsv = QAction("Obrir CSV", self)
        # self.actObrirCsv.setShortcut("Ctrl+C")
        self.actObrirCsv.setStatusTip("Obre fitxer CSV")
        self.actObrirCsv.triggered.connect(loadCsv)

        # Obrir i Guardar un projecte QGIS (o qVista)
        self.actObrirProjecte = QAction("Obrir...", self)
        # icon=QIcon(':/Icones/Icones/ic_file_upload_black_48dp.png')
        # self.actObrirProjecte.setIcon(icon)
        self.actObrirProjecte.setShortcut("Ctrl+O")
        self.actObrirProjecte.setStatusTip("Obrir mapa QGis")
        self.actObrirProjecte.triggered.connect(self.obrirDialegProjecte)
        
        self.actGuardarProjecte = QAction("Desar", self)
        # icon=QIcon(':/Icones/Icones/ic_file_download_black_48dp.png')
        # self.actGuardarProjecte.setIcon(icon)
        self.actGuardarProjecte.setShortcut("Ctrl+S")
        self.actGuardarProjecte.setStatusTip("Guardar Mapa")
        self.actGuardarProjecte.triggered.connect(guardarProjecte)

        self.actGuardarComAProjecte=QAction('Anomena i desa...', self)
        self.actGuardarComAProjecte.setStatusTip("Desar una còpia del mapa actual")
        self.actGuardarComAProjecte.triggered.connect(guardarDialegProjecte)

        self.actNouMapa = QAction("Nou", self)
        self.actNouMapa.setStatusTip("Nou Mapa")
        self.actNouMapa.setShortcut('Ctrl+N')
        self.actNouMapa.triggered.connect(nouMapa)

        self.actExecuteChrome = QAction("Calculadora", self)
        iconaChrome=QIcon('imatges/calc.png')
        self.actExecuteChrome.setIcon(iconaChrome)
        self.actExecuteChrome.triggered.connect(executeChrome)
        
        self.actDocumentacio=QAction('Documentació',self)
        self.actDocumentacio.setIcon(QIcon('Imatges/file-document.png'))
        self.actDocumentacio.triggered.connect(obreDocumentacio)

        
        self.actImprimir = QAction("Imprimir", self)
        self.actImprimir.setStatusTip("Imprimir")
        icon=QIcon('imatges/printer.png')
        self.actImprimir.setIcon(icon)
        self.actImprimir.triggered.connect(self.imprimir)

        self.actCloudUpload = QAction("Pujar al núvol", self)
        self.actCloudUpload.setStatusTip("Pujar al núvol")
        icon=QIcon('imatges/cloud-upload.png')
        self.actCloudUpload.setIcon(icon)
        self.actCloudUpload.triggered.connect(self.cloudUpload)

        # Creació de layers a partir de diferents formats
        self.actAfegirNivellSHP = QAction("Afegir capa SHP", self)
        self.actAfegirNivellSHP.setStatusTip("Afegir capa SHP")
        self.actAfegirNivellSHP.triggered.connect(afegirNivellSHP)

        self.actAfegirNivellCSV = QAction("Afegir capa CSV", self)
        self.actAfegirNivellCSV.setStatusTip("Afegir capa CSV")
        self.actAfegirNivellCSV.triggered.connect(escollirNivellCSV)
        
        self.actAfegirNivellGPX = QAction("Afegir capa GPX", self)
        self.actAfegirNivellGPX.setStatusTip("Afegir capa GPX")
        self.actAfegirNivellGPX.triggered.connect(escollirNivellGPX)
        
        self.actAfegirNivellQlr = QAction("Afegir capa QLR", self)
        self.actAfegirNivellQlr.setStatusTip("Afegir capa QLR")
        self.actAfegirNivellQlr.triggered.connect(escollirNivellQlr)

        self.actAfegirCapa = QAction("Afegir...", self)
        self.actAfegirCapa.setStatusTip("Afegir capa")
        self.actAfegirCapa.triggered.connect(self.obrirDialegNovaCapa)

        self.actSeleccioExpressio= QAction("Selecció per expressió", self)
        self.actSeleccioExpressio.setStatusTip("Selecció per expressió")
        self.actSeleccioExpressio.triggered.connect(seleccioExpressio)

        self.actObrirBotonera= QAction("Obrir botonera", self)
        self.actObrirBotonera.setStatusTip("Obrir la botonera lateral")
        self.actObrirBotonera.triggered.connect(self.obrirBotonera)

        self.actObrirUbicacions= QAction("Les meves ubicacions", self)
        icon=QIcon('imatges/map-marker.png')
        self.actObrirUbicacions.setIcon(icon)
        self.actObrirUbicacions.setStatusTip("Obrir eina ubicacions")
        self.actObrirUbicacions.triggered.connect(self.obrirUbicacions)

        self.actObrirTaula= QAction("Obrir taula de dades", self)
        self.actObrirTaula.setStatusTip("Obrir taula de dades")
        self.actObrirTaula.triggered.connect(self.obrirTaula)
        
        self.actObrirTaulaAtributs= QAction("Obrir taula d'atributs", self)
        self.actObrirTaulaAtributs.setStatusTip("Obrir taula d'atributs'")
        # icon=QIcon(':/Icones/Icones/baseline_format_align_justify_black_36dp.png')
        # self.actObrirTaulaAtributs.setIcon(icon)
        self.actObrirTaulaAtributs.triggered.connect(self.obrirTaulaAtributs)
        # self.actObrirTaulaAtributs.triggered.connect(self.obrirDualWidget)
    
        self.actObrirDistrictes= QAction("Obrir arbre de districtes", self)
        self.actObrirDistrictes.setStatusTip("Obrir arbre de districtes")
        # icon=QIcon(':/Icones/Icones/if_Map_-_Location_Solid_Style_03_2216364.png')
        # self.actObrirDistrictes.setIcon(icon)
        self.actObrirDistrictes.triggered.connect(self.obrirDistrictes)
    
        # self.actObrirCalculadora= QAction("Obrir calculadora", self)
        # # icon=QIcon(':/Icones/Icones/icons8-calculator-50.png')
        # # self.actObrirCalculadora.setIcon(icon)
        # self.actObrirCalculadora.setStatusTip("Obrir calculadora")
        # self.actObrirCalculadora.triggered.connect(self.obrirCalculadora)

        self.actObrirLlegenda= QAction("Obrir llegenda", self)
        # icon=QIcon(':/Icones/Icones/ic_format_list_bulleted_black_48dp.png')
        # self.actObrirLlegenda.setIcon(icon)
        self.actObrirLlegenda.setStatusTip("Obrir llegenda")
        self.actObrirLlegenda.triggered.connect(self.obrirLlegenda)

        self.actObrirBrowserGrafiques= QAction("Obrir gràfiques", self)
        self.actObrirBrowserGrafiques.setStatusTip("Obrir gràfiques")
        self.actObrirBrowserGrafiques.triggered.connect(self.obrirBrowserGrafiques)

        self.actMartorellUTM= QAction("Martorell/UTM", self)
        self.actMartorellUTM.setStatusTip("Martorell / UTM")
        self.actMartorellUTM.triggered.connect(self.martorellUTM)

        self.actTissores = QAction("Eina per retallar pantalla", self)
        self.actTissores.setStatusTip("Eina per retallar pantalla")
        icon=QIcon('imatges/tissores.png')
        self.actTissores.setIcon(icon)
        self.actTissores.triggered.connect(self.tissores)

        self.actSeleccioGrafica = QAction("Selecció gràfica d'elements", self)
        self.actSeleccioGrafica.setStatusTip("Selecció gràfica d'elements")
        icon=QIcon('imatges/select.png')
        self.actSeleccioGrafica.setIcon(icon)
        self.actSeleccioGrafica.triggered.connect(self.seleccioGrafica)

        
        self.actPanSelected = QAction("Pan selected", self)
        self.actPanSelected.setStatusTip("Pan selected")
        self.actPanSelected.triggered.connect(self.panSelected)

        self.actZoomSelected = QAction("Zoom selected", self)
        self.actZoomSelected.setStatusTip("Zoom selected")
        self.actZoomSelected.triggered.connect(self.zoomSelected)

        self.actFiltreCanvas = QAction("Filtre canvas", self)
        self.actFiltreCanvas.setStatusTip("Filtre canvas")
        self.actFiltreCanvas.triggered.connect(self.filtreCanvas)

        self.actSeleccioClick = QAction("Selecció per click", self)
        # icon=QIcon(':/Icones/Icones/if_Map_-_Location_Solid_Style_07_2216351.png')
        # self.actSeleccioClick.setIcon(icon)
        self.actSeleccioClick.setStatusTip("Selecció per click")
        self.actSeleccioClick.triggered.connect(seleccioClick)

        self.actDisgregarDirele = QAction("Disgregar Fichero Direcciones", self)
        # icon=QIcon(':/Icones/Icones/if_Map_-_Location_Solid_Style_07_2216351.png')
        # self.actSeleccioClick.setIcon(icon)
        self.actDisgregarDirele.setStatusTip("Disgregar Fichero Direcciones")
        self.actDisgregarDirele.triggered.connect(disgregarDirele)




        self.actEsborrarSeleccio = QAction("Esborrar seleccio", self)
        self.actEsborrarSeleccio.setStatusTip("Esborrar seleccio")
        self.actEsborrarSeleccio.triggered.connect(lambda: self.esborrarSeleccio(True))

        self.actCentrar = QAction(self)
        self.actCentrar.setStatusTip("Centrar mapa")
        # icon=QIcon(':/Icones/Icones/ic_zoom_out_map_black_48dp.png')
        # self.actCentrar.setIcon(icon)
        self.actCentrar.triggered.connect(self.centrarMapa)
        
        self.actSeleccioLliure = QAction("Seleccio lliure", self)
        # icon=QIcon(':/Icones/Icones/ic_format_shapes_black_48dp.png')
        # self.actSeleccioLliure.setIcon(icon)
        self.actSeleccioLliure.setStatusTip("Seleccio lliure")
        self.actSeleccioLliure.triggered.connect(seleccioLliure)

        self.actInfo = QAction("Informació ", self)
        icon=QIcon('imatges/information.png')
        self.actInfo.setIcon(icon)
        self.actInfo.triggered.connect(self.infoQVista)

        self.actHelp = QAction("Ajuda ", self)
        icon=QIcon('imatges/help-circle.png')
        self.actHelp.setIcon(icon)
        # self.actHelp.triggered.connect(self.helpQVista)
        self.actHelp.triggered.connect(self.infoQVistaPDF)
        self.actHelp.setShortcut('Ctrl+H')
                
        # self.actBug = QAction("Ajuda ", self)
        # icon=QIcon('imatges/bug.png')
        # self.actBug.setIcon(icon)
        # self.actBug.triggered.connect(self.reportarBug)

        #bEnviar.clicked.connect(lambda: reportarProblema(leTitol.text(), leDescripcio.text()))
        self.suggeriments=QvSuggeriments(reportarProblema,self)
        self.actBug = QAction("Problemes o suggeriments ", self)
        icon=QIcon('imatges/bug.png')
        self.actBug.setIcon(icon)
        self.actBug.triggered.connect(self.suggeriments.show)
                
        self.actPintaLabels = QAction("pintaLabels", self)
        self.actPintaLabels.setStatusTip("pintaLabels")
        self.actPintaLabels.triggered.connect(self.pintaLabels)

        self.actObrirCataleg = QAction("Catàleg", self)
        self.actObrirCataleg.setStatusTip("Catàleg d'Informació Territorial")
        #self.actObrirCataleg.setIcon(QIcon('imatges/layers_2.png'))
        self.actObrirCataleg.triggered.connect(self.obrirCataleg)

        self.actObrirCatalegProjectesLlista = QAction("Mapes", self)
        self.actObrirCatalegProjectesLlista.setStatusTip("Catàleg de Mapes")
        #self.actObrirCatalegProjectesLlista.setIcon(QIcon('imatges/map-plus.png'))
        self.actObrirCatalegProjectesLlista.triggered.connect(self.obrirCatalegProjectesLlista)

        self.actObrirMapeta = QAction("Mapeta", self)
        self.actObrirMapeta.setStatusTip("Mapeta de situació")
        self.actObrirMapeta.triggered.connect(self.obrirMapeta)

        self.actMapTip = QAction("MapTip", self)
        self.actMapTip.setStatusTip("MapTip")
        self.actMapTip.triggered.connect(self.preparacioMapTips)
        
        self.actFerGran = QAction("Ampliar àrea de treball", self)
        self.actFerGran.setIcon(QIcon('imatges/arrow-expand.png'))
        self.actFerGran.setStatusTip("Ampliar àrea de treball")
        self.actFerGran.triggered.connect(self.ferGran)

        self.actObrirEnQgis = QAction("Obrir en Qgis", self)
        self.actObrirEnQgis.setIcon(QIcon('imatges/qgis3.png'))
        self.actObrirEnQgis.setStatusTip("Obrir en Qgis")
        self.actObrirEnQgis.triggered.connect(self.obrirEnQgis)

        self.actGrafiques = QAction("Gràfiques", self)
        self.actGrafiques.setIcon(QIcon('imatges/chart-bar.png'))
        self.actGrafiques.setStatusTip("Gràfiques")
        self.actGrafiques.triggered.connect(self.obrirBrowserGrafiques)

        self.actCanvasImg = QAction("Guardar imatge del canvas", self)
        self.actCanvasImg.setIcon(QIcon('imatges/camera.png'))
        self.actCanvasImg.setStatusTip("Imatge del canvas")
        self.actCanvasImg.triggered.connect(self.canvasImg)

        self.actFavorit = QAction("Favorit", self)
        self.actFavorit.setIcon(QIcon('imatges/star.png'))
        self.actFavorit.setStatusTip("Favorit")
        self.actFavorit.triggered.connect(self.favorit)

        #self.actCataleg = QAction(3*' '+"Catàleg"+3*' ', self)
        self.actCataleg = QAction("Catàleg", self)
        self.actCataleg.setStatusTip("Catàleg")
        self.actCataleg.triggered.connect(self.obrirCatalegProjectesLlista)

        self.actTemes = QAction("Temes", self)
        self.actTemes.setStatusTip("Temes")
        self.actTemes.triggered.connect(self.mapesTema)

        self.actTest = QAction("test", self)
        self.actTest.setStatusTip("test")
        self.actTest.triggered.connect(self.test)

        self.frame_15.setContentsMargins(0,0,12,0)

        #Hem de definir les accions o el que sigui
        stylesheetBotons='''
            QPushButton{
                margin: 0px;
                background: transparent;
                border: 0px;
                padding: 0px;
            }
            QToolTip{
                color: #38474F;
                background-color: #F0F0F0;
            }
        '''
        self.botoVeureLlegenda.setIcon(QIcon('Imatges/map-legend.png'))
        self.botoVeureLlegenda.setStyleSheet(stylesheetBotons)
        self.botoVeureLlegenda.setIconSize(QSize(24, 24))
        self.botoVeureLlegenda.clicked.connect(self.obrirLlegenda)
        self.botoVeureLlegenda.setCursor(QvConstants.cursorClick())

        self.iconaSenseCanvisPendents = QIcon('Imatges/content-save.png')
        self.iconaAmbCanvisPendents = QIcon('Imatges/content-save_orange.png')
        self.botoDesarProjecte.setIcon(self.iconaSenseCanvisPendents)
        self.botoDesarProjecte.setStyleSheet(stylesheetBotons)
        self.botoDesarProjecte.setIconSize(QSize(24, 24))
        self.botoDesarProjecte.clicked.connect(guardarProjecte) 
        self.botoDesarProjecte.setCursor(QvConstants.cursorClick())

        self.botoObrirQGis.setIcon(QIcon('Imatges/qgis-3.png'))
        self.botoObrirQGis.setStyleSheet(stylesheetBotons)
        self.botoObrirQGis.setIconSize(QSize(24, 24))
        self.botoObrirQGis.clicked.connect(self.obrirEnQgis)
        self.botoObrirQGis.setCursor(QvConstants.cursorClick())

        self.botoMapeta.setIcon(QIcon('Imatges/Mapeta.png'))
        self.botoMapeta.setStyleSheet(stylesheetBotons)
        self.botoMapeta.setIconSize(QSize(24,24))
        self.botoMapeta.clicked.connect(self.mapeta.ferPetit)
        self.botoMapeta.setCursor(QvConstants.cursorClick())

        self.botoMetadades.setIcon(QIcon('Imatges/information-variant.png'))
        self.botoMetadades.setStyleSheet(stylesheetBotons)
        self.botoMetadades.setIconSize(QSize(24,24))
        self.botoMetadades.setCursor(QvConstants.cursorClick())


        
        # self.actBicing = QAction("Bicing", self)
        # self.actBicing.setStatusTip("Bicing")
        # self.actBicing.triggered.connect(self.bicing)

        self.actWizard = QAction("Wizard", self)
        self.actWizard.setStatusTip("transp")
        self.actWizard.triggered.connect(self.wizard)
    
        self.actEntorns = QAction("Entorns", self)
        self.actEntorns.setStatusTip("Entorns")
        self.actEntorns.triggered.connect(self.preparacioEntorns)
    
        self.actDashStandard = QAction("Restaurar", self)
        self.actDashStandard.setIcon(QIcon('imatges/auto-fix.png'))
        self.actDashStandard.setStatusTip("Restaurar")
        self.actDashStandard.triggered.connect(self.dashStandard)

        self.actAdreces = QAction("Cerca per adreça", self)
        self.actAdreces.setIcon(QIcon('imatges/map-search.png'))
        self.actAdreces.setStatusTip("Adreces")
        self.actAdreces.triggered.connect(self.adreces)

        self.actTest2 = QAction("actTest2", self)
        self.actTest2.setStatusTip("actTest2")
        self.actTest2.triggered.connect(self.testProva)

        self.actPavimentacio = QAction("Pavimentació", self)
        self.actPavimentacio.setStatusTip("Pavimentació")
        self.actPavimentacio.triggered.connect(self.pavimentacio)

        self.actMarxesCiutat = QAction("Marxes de Ciutat", self)
        self.actMarxesCiutat.setStatusTip("Marxes de Ciutat")
        self.actMarxesCiutat.triggered.connect(self.marxesCiutat)

        self.actPlatges = QAction("Pavimentació", self)
        self.actPlatges.setStatusTip("Pavimentació")
        self.actPlatges.triggered.connect(self.platges)

        self.actPropietatsLayer = QAction("Propietats de la capa", self)
        self.actPropietatsLayer.setStatusTip("Propietats de la capa")
        self.actPropietatsLayer.triggered.connect(self.propietatsLayer)


    def platges(self):
        self.platges = QvPlatges()
        self.platges.show()

    def reportarBug(self):
        self.fitxaError = QWidget()
        self.lytFitxaError = QVBoxLayout(self.fitxaError)
        self.fitxaError.setLayout(self.lytFitxaError)
        leTitol = QLineEdit()
        leTitol.setPlaceholderText('Escriu aquí el titol del sugeriment')
        leDescripcio = QLineEdit()
        leDescripcio.setPlaceholderText('Escriu.ne aquí una breu descripció')
        bEnviar = QvPushButton('Enviar',flat=True)
        self.lblResultat = QLabel()
        bEnviar.clicked.connect(lambda: reportarProblema(leTitol.text(), leDescripcio.text()))
        self.lytFitxaError.addWidget(leTitol)
        self.lytFitxaError.addWidget(leDescripcio)
        self.lytFitxaError.addWidget(bEnviar)
        self.lytFitxaError.addWidget(self.lblResultat)
        self.fitxaError.show()

    def preparacioSeleccio(self):

        # Disseny del interface
        class QvSeleccioGrafica(QWidget):
            def __init__(self):
                QWidget.__init__(self)

        self.wSeleccioGrafica = QvSeleccioGrafica()
        
        self.wSeleccioGrafica.setWhatsThis(QvApp().carregaAjuda(self))
        self.lytSeleccioGrafica = QVBoxLayout()
        self.lytSeleccioGrafica.setAlignment(Qt.AlignTop)
        self.wSeleccioGrafica.setLayout(self.lytSeleccioGrafica)
        self.lytBotonsSeleccio = QHBoxLayout()
        self.leSel2 = QLineEdit()
        self.lytSeleccioGrafica.addWidget(self.leSel2)
        self.leSel2.editingFinished.connect(seleccioExpressio)
        self.lytSeleccioGrafica.addLayout(self.lytBotonsSeleccio)


        self.bs1 = QvPushButton(flat=True)
        # self.bs1.setCheckable(True)
        self.bs1.setIcon(QIcon('imatges/apuntar.png'))
        self.bs2 = QvPushButton(flat=True)
        # self.bs2.setCheckable(True)
        self.bs2.setIcon(QIcon('imatges/shape-polygon-plus.png'))
        self.bs3 = QvPushButton(flat=True)
        # self.bs3.setCheckable(True)
        self.bs3.setIcon(QIcon('imatges/vector-circle-variant.png'))
        self.bs4 = QvPushButton(flat=True)
        # self.bs4.setCheckable(True)
        self.bs4.setIcon(QIcon('imatges/trash-can-outline.png'))

        self.lblNombreElementsSeleccionats = QLabel('No hi ha elements seleccionats.')
        self.lblCapaSeleccionada = QLabel('No hi capa seleccionada.')
        
        self.lwFieldsSelect = QListWidget()
        self.lwFieldsSelect.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.bs5 = QvPushButton('Calcular',flat=True)
        self.bs5.clicked.connect(self.calcularSeleccio)
        
        self.bs6 = QvPushButton('Crear CSV',flat=True)
        self.bs6.clicked.connect(self.crearCsv)

        self.twResultats = QTableWidget()

        self.checkOverlap = QCheckBox('Overlap')
        self.bs1.clicked.connect(seleccioClicks)
        self.bs2.clicked.connect(seleccioLliure)
        self.bs3.clicked.connect(seleccioCercle)
        self.bs4.clicked.connect(lambda: self.esborrarSeleccio(True))

        self.lytBotonsSeleccio.addWidget(self.bs1)
        self.lytBotonsSeleccio.addWidget(self.bs2)
        self.lytBotonsSeleccio.addWidget(self.bs3)
        self.lytBotonsSeleccio.addWidget(self.bs4)
        
        self.lytSeleccioGrafica.addWidget(self.checkOverlap)
        self.lytSeleccioGrafica.addWidget(self.lblNombreElementsSeleccionats)
        self.lytSeleccioGrafica.addWidget(self.lblCapaSeleccionada)
        self.lytSeleccioGrafica.addWidget(self.lwFieldsSelect)
        # self.lytSeleccioGrafica.addWidget(self.bs5)
        self.lytSeleccioGrafica.addWidget(self.bs6)
        self.lytSeleccioGrafica.addWidget(self.twResultats)


        
        self.dwSeleccioGrafica = QDockWidget("Selecció gràfica", self)
        self.dwSeleccioGrafica.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.dwSeleccioGrafica.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwSeleccioGrafica.hide()
        self.dwSeleccioGrafica.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwSeleccioGrafica.setWidget( self.wSeleccioGrafica)
        self.dwSeleccioGrafica.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwSeleccioGrafica )
        self.dwSeleccioGrafica.hide()

        self.idsElementsSeleccionats = []

    def crearCsv(self):
        nomTriat = self.taulesAtributs.desarCSV(self.llegenda.currentLayer(), selected = True)
        self.finestraCSV = QvLectorCsv(nomTriat)
        self.finestraCSV.show()

    def calcularSeleccio(self):
        layer = self.llegenda.currentLayer()
        taula=self.twResultats
        numeroFields=0
        fila=0
        columna=0
        nombreElements = 0
        taula.setColumnCount(3)
        taula.setHorizontalHeaderLabels(['','Total', 'Mitjana'])
        nombreFieldsSeleccionats=0
        for a in self.lwFieldsSelect.selectedItems():
            nombreFieldsSeleccionats=nombreFieldsSeleccionats+1
        taula.setRowCount(nombreFieldsSeleccionats+1)
        for a in self.lwFieldsSelect.selectedItems():
            total=0
            item = QTableWidgetItem(a.text())
            taula.setItem(fila+1,0,item)
            field=layer.fields().lookupField(a.text())
            # print (field)
            nombreElements=0
            for feature in layer.selectedFeatures():
                calcul=feature.attributes()[layer.fields().lookupField(a.text())]
                total=total+calcul
                nombreElements=nombreElements+1
            if nombreElements>0:
                mitjana = total/nombreElements
            else:
                mitjana = 0
            item = QTableWidgetItem(str('% 12.2f' % total))
            taula.setItem(fila+1,1,item)
            item = QTableWidgetItem(str('% 12.2f' % mitjana))
            taula.setItem(fila+1,2,item)
            # print('Total: '+a.text()+": ",total)
            fila=fila+1
        item = QTableWidgetItem("Seleccionats:")
        taula.setItem(0,0,item)
        item = QTableWidgetItem(str(nombreElements))
        taula.setItem(0,1,item)
        taula.resizeColumnsToContents()

    def canviLayer(self):
        self.preparacioMapTips()
        self.layerActiu = self.llegenda.currentLayer()        
        self.lwFieldsSelect.clear()
        self.esborrarSeleccio(True)
        if self.layerActiu is not None:
            self.lblCapaSeleccionada.setText("Capa activa: "+ self.layerActiu.name())
            if self.layerActiu.type() == QgsMapLayer.VectorLayer:
                fields = self.layerActiu.fields()
                for field in fields:
                    # print(field.typeName())
                    # if (field.typeName()!='String' and field.typeName()!='Date' and field.typeName()!='Date'):
                    if (field.typeName()=='Real' or field.typeName()=='Integer64'):
                        self.lwFieldsSelect.addItem(field.name())
            else:
                self.lblCapaSeleccionada.setText("Capa activa sense dades.")
        else:
            self.lblCapaSeleccionada.setText("No hi ha capa activa.")

    def seleccioGrafica(self):
        self.dwSeleccioGrafica.show()
        self.canviLayer()

    def helpQVista(self):
        QWhatsThis.enterWhatsThisMode()
        pass
    
    def infoQVistaPDF(self):
        ''' Obre un pdf amb informació de qVista, utilitzant l'aplicació per defecte del sistema '''
        os.startfile(arxiuInfoQVista)


    def activarDashboard(self,nom):

        for objecte in self.dashboardActiu:
            objecte.hide() 
        dashboard = nom(self)

        self.dashboardActiu = [dashboard]
        self.layout.addWidget(dashboard)

    def wizard(self):
        self.wiz = QvWizard()
        self.wiz.show()

    def transpInfo(self):

        self.frameTranspInfo = QFrame(self.centralWidget())
        self.frameTranspInfo.setGeometry(5,5,100,100)
        self.frameTranspInfo.show()

    def activaCapa(self,capa):
        def funcioCapa():
            if self.llegenda.isLayerVisible( capaPerNom(capa)):
                self.llegenda.veureCapa(self.llegenda.capaPerNom(capa), True)
            else:
                self.llegenda.veureCapa(self.llegenda.capaPerNom(capa), False)

        return funcioCapa

    def anteriorPosicioCanvas(self):
        self.canvas.zoomToPreviousExtent()

    def obrirEnQgis(self):
        # TODO: Generalitzar opertura qGis
        self.project.write('c:/temp/tempQgis.qgs')
        QDesktopServices().openUrl(QUrl('c:/temp/tempQgis.qgs'))

    def cloudUpload(self):
        missatgeCaixa("Es podrà: Obtenir una adreça URL del mapa, publicat a Internet, per compartir-la", "Aquesta funció no està encara implementada.")
        
    def netejaCanvas(self):
        pass

    def tissores(self):
        # QDesktopServices().openUrl(QUrl('c:\windows\system32\SnippingTool.exe'))
        # subprocess.check_call([r'c:\windows\system32\SnippingTool.exe'])
        process = QProcess(self)
        pathApp = "c:\windows\system32\SnippingTool.exe"
        process.start(pathApp)
        app.processEvents()

    def definirMenus(self):
        """Definició dels menús de la barra superior.
        (Cal fer neteja.)
        """
        lblLogoQVista = QLabel()
        lblLogoQVista.setMaximumHeight(40)
        lblLogoQVista.setMinimumHeight(40)
        sizeWidget=self.frame_11.width()
        lblLogoQVista.setMaximumWidth(sizeWidget)
        lblLogoQVista.setMinimumWidth(sizeWidget)
        
        imatge = QPixmap('imatges/qVistaLogo_text_40.png')
        p = QPainter(imatge) 
        p.setPen(QPen(Qt.white))
        p.setFont(QFont("Arial", 12, QFont.Medium))
        p.drawText(106,26, versio)
        p.end()

        lblLogoQVista.setPixmap(imatge)
        lblLogoQVista.setScaledContents(False)

        # self.lblVersio = QLabel()
        # self.lblVersio.setText(versio)
        # self.lblVersio.setGeometry(100,100,100,100)

        menubar=QvMenuBar(self)
        self.setMenuBar(menubar)
        self.bar = self.menuBar()
        self.bar.setFont(QvConstants.FONTTITOLS)
        self.bar.setCornerWidget(lblLogoQVista,Qt.TopLeftCorner)

        # self._menuBarShadow = QGraphicsDropShadowEffect()
        # self._menuBarShadow.setXOffset(0)
        # self._menuBarShadow.setColor(QColor(55,57,63))
        # self._menuBarShadow.setBlurRadius(20)
        # self.bar.setGraphicsEffect(self._menuBarShadow)
        
        self._menuBarShadow=QvConstants.afegeixOmbraHeader(self.bar)

        # self.bar.setFixedHeight(40)
        self.bar.setMinimumHeight(40)
        self.fMaxim = QFrame()
        self.lytBotonsFinestra = QHBoxLayout(self.fMaxim)
        self.fMaxim.setLayout(self.lytBotonsFinestra)
        self.lytBotonsFinestra.setContentsMargins(0,0,0,0)
        
        # self.botoMaxim=QvPushButton(flat=True)
        # self.botoMaxim.clicked.connect(self.ferGran)
        # self.botoMaxim.setIcon(QIcon('imatges/arrow-expand.png'))
        # self.botoMaxim.setIconSize(QSize(30, 30))
        # self.lytMaxim=QHBoxLayout(self.frame_13)
        # self.lytMaxim.addWidget(self.botoMaxim)
        self.frame_13.setStyleSheet('background-color: %s'%QvConstants.COLORFOSCHTML)

        stylesheetBotonsFinestra='''
            QPushButton{
                background: transparent;
            }
            QPushButton::hover {
                background-color: %s;
                opacity: 1;
            }
            QPushButton::pressed{
                background-color: %s;
                opacity: 0.1;
            }
        '''%(QvConstants.COLORDESTACATHTML,QvConstants.COLORDESTACATHTML)

        self.botoMinimitzar=QvPushButton(flat=True)
        self.botoMinimitzar.setIcon(QIcon('imatges/window-minimize.png'))
        self.botoMinimitzar.setFixedSize(40,40)
        self.botoMinimitzar.clicked.connect(self.showMinimized)
        self.botoMinimitzar.setStyleSheet(stylesheetBotonsFinestra)
        self.lytBotonsFinestra.addWidget(self.botoMinimitzar)

        self.maximitzada=True
        iconaRestaurar1=QIcon('imatges/window-restore.png')
        iconaRestaurar2=QIcon('imatges/window-maximize.png')
        def restaurar():
            if self.maximitzada:
                self.setWindowFlag(Qt.FramelessWindowHint,False)
                self.setWindowState(Qt.WindowActive)
                self.actualitzaWindowFlags()
                amplada=self.width()
                alcada=self.height()
                self.resize(0.8*amplada,0.8*alcada)
                self.show()
                self.botoRestaurar.setIcon(iconaRestaurar2)
            else:
                self.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
                self.botoRestaurar.setIcon(iconaRestaurar1)
                self.setWindowFlag(Qt.FramelessWindowHint)
                self.actualitzaWindowFlags()
                self.show()
            self.maximitzada=not self.maximitzada
        self.restaurarFunc=restaurar
        self.botoRestaurar=QvPushButton(flat=True)
        self.botoRestaurar.setIcon(iconaRestaurar1)
        self.botoRestaurar.clicked.connect(restaurar)
        self.botoRestaurar.setFixedSize(40,40)
        self.botoRestaurar.setStyleSheet(stylesheetBotonsFinestra)
        self.lytBotonsFinestra.addWidget(self.botoRestaurar)

        self.botoSortir=QvPushButton(flat=True)
        self.botoSortir.setIcon(QIcon('imatges/window_close.png'))
        self.botoSortir.setFixedSize(40,40)
        self.botoSortir.clicked.connect(self.provaDeTancar)
        self.botoSortir.setStyleSheet(stylesheetBotonsFinestra)
        self.lytBotonsFinestra.addWidget(self.botoSortir)

        def ocultaBotons():
            if not self.botoSortir.isEnabled():
                self.botoSortir.setEnabled(True)
                self.botoRestaurar.setEnabled(True)
                self.botoMinimitzar.setEnabled(True)
                self.showLblFlotant(":'(")
            else:
                self.botoSortir.setEnabled(False)
                self.botoRestaurar.setEnabled(False)
                self.botoMinimitzar.setEnabled(False)
                self.showLblFlotant('Benvingut al mode "qVista Màxima Rellevància". \
    En aquest mode els botons per tancar, minimitzar i fer petita la finestra deixen de funcionar, \
    ja que qVista passa a ser el programa més important de l\'ordinador.')

        self.shortcutNoEsPotSortir=QShortcut(QKeySequence('Ctrl+Shift+Alt+Ç'),self)
        self.shortcutNoEsPotSortir.activated.connect(ocultaBotons)

        self.bar.setCornerWidget(self.fMaxim, Qt.TopRightCorner)


        self.bar.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality


        spacer = QSpacerItem(9999, 9999, QSizePolicy.Expanding,QSizePolicy.Maximum)
        #self.bar.addAction(self.actCataleg)
        self.menuMapes = self.bar.addMenu ("Mapes")
        self.menuCapes = self.bar.addMenu ("Capes")
        # self.menuEntorns = self.bar.addMenu("Entorns")
        self.menuUtilitats = self.bar.addMenu("Utilitats")
        # self.menuFuncions = self.bar.addMenu("  Eines  ")
        self.menuFuncions = QMenu()
        # self.menuCarregarNivell = self.bar.addMenu("  Finestres  ")
        # catalegMenu = self.bar.addMenu("                   Catàleg  ")

        self.menuMapes.setFont(QvConstants.FONTSUBTITOLS)
        self.menuMapes.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        self.menuMapes.addAction(self.actCataleg)
        self.menuMapes.addSeparator()
        self.menuMapes.addAction(self.actNouMapa)
        self.menuMapes.addAction(self.actObrirProjecte)
        self.menuMapes.addAction(self.actGuardarProjecte)
        self.menuMapes.addAction(self.actGuardarComAProjecte)
        #Aquí originalment creàvem el menú de Mapes recents
        #No obstant, com que a actualitzaMapesRecents es crea de nou, no cal crear-lo aquí
        self.menuRecents=QMenu('Mapes recents',self.menuMapes)
        self.actualitzaMapesRecents(None)
        self.menuMapes.addMenu(self.menuRecents)

        self.menuCapes.setFont(QvConstants.FONTSUBTITOLS)
        self.menuCapes.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        self.menuCapes.addAction(self.actObrirCataleg)
        self.menuCapes.addAction(self.actAfegirCapa)
        
        # self.menuCarregarNivell.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality

        # # self.menuCarregarNivell.addAction("Oracle")
        # self.menuCarregarNivell.addAction(self.actAfegirNivellSHP)
        # self.menuCarregarNivell.addAction(self.actAfegirNivellCSV)
        # self.menuCarregarNivell.addAction(self.actAfegirNivellGPX)
        # self.menuCarregarNivell.addAction(self.actAfegirNivellQlr)
        
        self.menuUtilitats.setFont(QvConstants.FONTSUBTITOLS)
        self.menuUtilitats.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        self.menuUtilitats.addAction(self.actExecuteChrome)
        self.menuUtilitats.addAction(self.actDocumentacio)


        self.menuFuncions.setFont(QvConstants.FONTSUBTITOLS)
        self.menuFuncions.addAction(self.actEsborrarSeleccio)
        self.menuFuncions.addAction(self.actSeleccioLliure)
        self.menuFuncions.addAction(self.actSeleccioClick)
        self.menuFuncions.addAction(self.actDisgregarDirele)
        

        # self.menuFuncions.addAction(self.actFerGran)
        self.menuFuncions.addAction(self.actMapTip)
        self.menuFuncions.addAction(self.actTemes)
        # self.menuFuncions.addAction(self.actObrirCataleg)
        # self.menuFuncions.addAction(self.actObrirDistrictes)
        # self.menuFuncions.addAction(self.actObrirTaulaAtributs)
        self.menuFuncions.addAction(self.actTest)
        self.menuFuncions.addAction(self.actInfo)
        # self.menuFuncions.addAction(self.actDashStandard)
        self.menuFuncions.addAction(self.actWizard)
        self.menuFuncions.addAction(self.actTest2)
        # self.menuFuncions.addAction(self.actObrirCalculadora)
        # self.menuFuncions.addAction(self.actObrirBrowserGrafiques)
        # self.menuFuncions.addAction(self.actBicing)
        self.menuFuncions.addAction(self.actPavimentacio)
        self.menuFuncions.addAction(self.actPlatges)
    def actualitzaWindowFlags(self):
        self.setWindowFlag(Qt.Window)
        self.setWindowFlag(Qt.CustomizeWindowHint,True)
        self.setWindowFlag(Qt.WindowTitleHint,False)
        self.setWindowFlag(Qt.WindowSystemMenuHint,False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint,False)
        self.setWindowFlag(Qt.WindowCloseButtonHint,False)
    def test(self):
        self.canvas.rotate(0)
        
    def testProva(self):
        self.canvas.setRotation(44)

    def ferGrafica(self):
        layerActiu = self.llegenda.currentLayer()
        for a in self.calculadora.ui.lwFields.selectedItems():
            campGraficable = a.text()

        noms = []
        dades = []
        dades2 = []
        
        # self.pintaLabels(campGraficable)

        nomLayer = self.calculadora.ui.cbLayers.currentText()
        if nomLayer == 'Districtes':
            campNom = 'N_Distri'
        elif nomLayer == 'Barris':
            campNom = 'N_Barri'
        else:
            return

        for feature in layerActiu.getFeatures():
            noms.append(feature.attributes()[layerActiu.fields().lookupField(campNom)])
            dades.append(feature.attributes()[layerActiu.fields().lookupField(campGraficable)])
            # dades2.append(feature.attributes()[layerActiu.fields().lookupField('Dones')])
            # print (barris, dades, dades2)

        data1 = go.Bar(
                    y=noms,
                    x=dades,
                    name=campGraficable,
                    orientation='h'
            )        
        # data2 = go.Bar(
        #             y=barris,
        #             x=dades2,
        #             name='Dones',
        #             orientation='h'
        #     )

        dades = [data1]
        layout = go.Layout(barmode='group')

        fig = go.Figure(data=dades, layout=layout)

        plotly.offline.plot(fig, filename='c:/temp/grouped-bar.html', auto_open=False)
        
        self.browserGrafiques.setUrl(QUrl('file:///c:/temp/grouped-bar.html'))
        self.browserGrafiques.show()

        # layer = QvLlegenda.capaPerNom(qV,qV.calculadora.ui.cbLayers.currentText())
        # # layer = qV.project.instance().mapLayersByName(qV.calculadora.ui.cbLayers.currentText())[0]
        # taula=qV.calculadora.ui.twCalculadora
        # numeroFields=0
        # fila=0
        # columna=0
        # taula.setColumnCount(2)
        # taula.setHorizontalHeaderLabels(['','Total'])
        # nombreFieldsSeleccionats=0
        # for a in qV.calculadora.ui.lwFields.selectedItems():
        #     nombreFieldsSeleccionats=nombreFieldsSeleccionats+1
        # taula.setRowCount(nombreFieldsSeleccionats+1)
        # for a in qV.calculadora.ui.lwFields.selectedItems():
        #     total=0
        #     item = QTableWidgetItem(a.text())
        #     taula.setItem(fila+1,0,item)
        #     nombreElements=0
        #     field=layer.fields().lookupField(a.text())
        #     # print (field)
        #     for feature in layer.selectedFeatures():
        #         calcul=feature.attributes()[layer.fields().lookupField(a.text())]
        #         total=total+calcul
        #         nombreElements=nombreElements+1
        #     item = QTableWidgetItem(str(total))
        #     taula.setItem(fila+1,1,item)
        #     # print('Total: '+a.text()+": ",total)
        #     fila=fila+1
        # item = QTableWidgetItem('Nombre elements')
        # taula.setItem(0,0,item)
        # item = QTableWidgetItem(str(nombreElements))
        # taula.setItem(0,1,item)
        # taula.resizeColumnsToContents()
    
    def prepararDash(self, nom):
        def obertura():
            for objecte in self.dashboardActiu:
                objecte.hide() 
            dashboard = nom(self)

            self.dashboardActiu = [dashboard]
            self.layout.addWidget(dashboard)

        return obertura

    def dashStandard(self):
        self.canvas.show()
        self.mapeta.show()
        self.layout.addWidget(self.canvas)
        self.frameLlegenda.show()
        self.lblTitolProjecte.setText(self.project.title())
        for objecte in self.dashboardActiu:
            objecte.hide()
        self.dashboardActiu = [self.frameLlegenda, self.canvas, self.mapeta]

    def dashX(self, Dashboard ):        
        for objecte in self.dashboardActiu:
            objecte.hide() 

        dashboard = Dashboard(self)

        self.dashboardActiu = [dashboard]
        self.layout.addWidget(dashboard)

    def catalegCool(self):
        self.catalegCool = QvCataleg(self, self.project, self.lblTitolProjecte)
        self.catalegCool.showMaximized()
    def showLblFlotant(self,txt):
        self.lblFlotant=QLabel(txt)
        self.lblFlotant.setFont(QvConstants.FONTTEXT)
        self.lblFlotant.setWordWrap(True)
        self.lblFlotant.setStyleSheet('''
            background: %s;
            color: %s;
            padding: 2px;
            border: 2px solid %s;
            border-radius: 10px;
            margin: 0px;
        '''%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML, QvConstants.COLORDESTACATHTML))
        self.lblFlotant.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.timerLblFlotant=QTimer(self)
        self.timerLblFlotant.setSingleShot(True)
        self.timerLblFlotant.timeout.connect(lambda: self.lblFlotant.hide())
        self.timerLblFlotant.start(5000)
        self.lblFlotant.show()
        self.lblFlotant.move(self.width()-500,self.height()-50)
    def hideLblFlotant(self):
        if hasattr(self,'lblFlotant'):
            self.lblFlotant.hide()
    def ferGran(self):
        # print('JOLA')

        if not self.mapaMaxim:
            self.hideLblFlotant()
            self.showMaximized()
            if hasattr(self.canvas,'bMaximitza'):
                self.canvas.bMaximitza.setIcon(self.canvas.iconaMaximitza)
            self.frame_3.show()
            self.frame_19.show()
            self.frame_2.show()
            if hasattr(self,'dockWidgetsVisibles'):
                for x in self.dockWidgetsVisibles: x.show()
            else:
                self.dwLlegenda.show()
            self.bar.show()
            self.statusbar.show()
            # self.botoMaxim.setIcon(QIcon('imatges/arrow-expand.png'))

            # Descomentar para eliminar barra de titulo
            # if self.lastMaximized:
            #     qV.showMaximized()
            # else:
            #     qV.showNormal()

        else:
            self.showLblFlotant('Prem F-11, Esc o el botó de maximitzar per sortir de la pantalla completa')
            if hasattr(self.canvas,'bMaximitza'):
                self.canvas.bMaximitza.setIcon(self.canvas.iconaMinimitza)
            self.dockWidgetsVisibles=[x for x in self.findChildren(QDockWidget) if x.isVisible()]
            for x in self.dockWidgetsVisibles: x.hide()
            self.frame_3.hide()
            self.frame_19.hide()
            self.frame_2.hide()
            self.dwLlegenda.hide()
            self.bar.hide()
            self.statusbar.hide()
            self.showFullScreen()
        self.mapaMaxim=not self.mapaMaxim

            


            # Descomentar para eliminar barra de titulo
            # self.lastMaximized = qV.isMaximized()
            # qV.showFullScreen()

    def clickArbre(self):
        rang = self.distBarris.llegirRang()
        self.canvas.zoomToFeatureExtent(rang)
        # print(self.distBarris.registre)

    def cataleg(self):
        self.qModel = QFileSystemModel()
        
        # print(self.qModel.rowCount(), self.qModel.columnCount())
        rootPath=self.qModel.setRootPath(carpetaCataleg)
        
        self.wCataleg.ui.treeCataleg.doubleClicked.connect(carregarNivellQlr) 
        self.wCataleg.ui.treeCataleg.clicked.connect(updateMetadadesCataleg) 
        self.qModel.setNameFilters(['*.qlr'])
        self.qModel.setNameFilterDisables(False)
        self.wCataleg.ui.treeCataleg.setModel(self.qModel)
        self.wCataleg.ui.treeCataleg.setRootIndex(rootPath)
        for i in range (1,4):
            self.wCataleg.ui.treeCataleg.header().hideSection(i)
        self.qModel.setHeaderData(0,Qt.Horizontal,'hola')
        self.wCataleg.ui.treeCataleg.setIndentation(20)
        self.wCataleg.ui.treeCataleg.setSortingEnabled(False)
        self.wCataleg.ui.treeCataleg.setWindowTitle("Catàleg d'Informació Territorial")
        self.wCataleg.ui.treeCataleg.resize(640, 480)
        self.wCataleg.ui.treeCataleg.adjustSize()
        self.wCataleg.ui.treeCataleg.setHeaderHidden(True)

    def catalegProjectesLlista(self):
        self.qModelProjectesLlista = QFileSystemModel()
        
        # print(self.qModel.rowCount(), self.qModel.columnCount())
        rootPath=self.qModelProjectesLlista.setRootPath(carpetaCatalegProjectesLlista)
        
        self.wCatalegProjectesLlista.ui.treeCataleg.doubleClicked.connect(carregarProjecteLlista) 
        self.wCatalegProjectesLlista.ui.treeCataleg.clicked.connect(updateMetadadesCataleg) 
        self.qModelProjectesLlista.setNameFilters(['*.qgs', '*.qgz'])
        self.qModelProjectesLlista.setNameFilterDisables(False)
        self.wCatalegProjectesLlista.ui.treeCataleg.setModel(self.qModelProjectesLlista)
        self.wCatalegProjectesLlista.ui.treeCataleg.setRootIndex(rootPath)
        for i in range (1,4):
            self.wCatalegProjectesLlista.ui.treeCataleg.header().hideSection(i)
        self.qModelProjectesLlista.setHeaderData(0,Qt.Horizontal,'hola')
        self.wCatalegProjectesLlista.ui.treeCataleg.setIndentation(20)
        self.wCatalegProjectesLlista.ui.treeCataleg.setSortingEnabled(False)
        self.wCatalegProjectesLlista.ui.treeCataleg.setWindowTitle("Catàleg de Mapes")
        self.wCatalegProjectesLlista.ui.treeCataleg.resize(640, 480)
        self.wCatalegProjectesLlista.ui.treeCataleg.adjustSize()
        self.wCatalegProjectesLlista.ui.treeCataleg.setHeaderHidden(True)

    def infoQVista(self):
        self.informacio = QDialog()
        self.informacio.setWindowOpacity(0.8)
        self.ui = Ui_Informacio()
        self.ui.setupUi(self.informacio)
        self.informacio.show()

    def pintaLabels(self, campEtiqueta):
        """Pinta sobre el canvas les etiquetas de la capa activa, segons campEtiqueta.
        
        Arguments:
        campEtiqueta {[String]} -- És el nom del camp del que volem pintar etiquetes.
        """

        layer=self.llegenda.currentLayer()
        layer_settings  = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QvConstants.FONTTEXT)
        text_format.setSize(12)

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))

        text_format.setBuffer(buffer_settings)
        layer_settings.setFormat(text_format)

        layer_settings.fieldName = campEtiqueta
        layer_settings.placement = 0

        layer_settings.enabled = True

        layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
        layer.setLabelsEnabled(True)
        layer.setLabeling(layer_settings)
        layer.triggerRepaint()

    def cercaText(self):
        """Don't pay attention
        """ 
        textCercat=""
        layer=self.llegenda.currentLayer()
        if layer is not None:
            for field in layer.fields():
                if field.typeName()=='String':
                    textCercat = textCercat + " " + fiel.name()
            print (textCercat)

    def nomCapa(self):
        capa = self.llegenda.view.currentLayer()
        # print('MENU NOM CAPA')
        # print('Nom: ', capa.name())

    def extCapa(self):
        capa = self.llegenda.view.currentLayer()
        # print('MENU EXTENSIÓ CAPA')
        # print('Extent: ', capa.extent().toString())

    def esborrarCapa(self):
        capa = self.llegenda.view.currentLayer()
        # print('MENU ESBORRAR CAPA')
        self.project.removeMapLayer(capa.id())
        self.canvas.refresh()

    def crearMenuCapa(self):
        menu = QMenu()
        menu.setFont(QvConstants.FONTSUBTITOLS)
        menu.addAction('Nom Capa', self.nomCapa)
        menu.addAction('Extensió Capa', self.extCapa)
        menu.addAction('Esborrar Capa', self.esborrarCapa)
        menu.addAction('Renombrar Capa', self.llegenda.accions.renameGroupOrLayer)
        menu.addAction('Propietats', self.propietatsLayer)
        return menu

    def capaActivada(self, mapLayer):
        if mapLayer:
            # print("CANVI CAPA")
            # print("Capa Activada: " +  mapLayer.name())
            pass

    def martorellUTM(self):
        extent=self.canvas.extent()
        self.canvas.rotate(45)
        self.canvas.setExtent(extent)

    def canvasImg(self):
        """
        Obtenim una imatge a partir del canvas en el moment en que la funció es cridada.
        
        Un dialeg demana on guardar-la.
       """    
        dialegFitxer=QFileDialog()
        dialegFitxer.setDirectoryUrl(QUrl('c:/Temp/'))

        nfile,_ = dialegFitxer.getSaveFileName(None,"Guardar imatge", ".", "(*.png)")

        self.canvas.saveAsImage(nfile)	

    def zoomSelected(self):
        """ Fem un zoom sobre els elements seleccionats del nivell actiu.
        """
        self.canvas.zoomToSelected(self.llegenda.currentLayer())

    def panSelected(self):    
        """ Fem un pan sobre els elements seleccionats del nivell actiu.
        """
        self.canvas.panToSelected(self.llegenda.currentLayer())
  
    def propietatsLayer(self):
        layer=self.llegenda.currentLayer()
        self.dlgProperties = None
        self.dlgProperties = LayerProperties( self, layer)
        self.dlgProperties.show()

    def esborrarSeleccio(self, tambePanCanvas = True):
        'Esborra les seleccions (no els elements) de qualsevol layer del canvas.'
        layers = self.canvas.layers() 
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()

        self.lblNombreElementsSeleccionats.setText('No hi ha elements seleccionats.')
        self.idsElementsSeleccionats = []

        if tambePanCanvas:
            self.canvas.panCanvas()

        try:
            qV.canvas.scene().removeItem(qV.toolSelect.rubberband)
            # taulaAtributs('Total',layer)
        except:
            pass

    def filtreCanvas(self):
        areaDInteres=self.canvas.extent()
        layer=self.view.currentLayer()
        if layer:
            it = layer.getFeatures(QgsFeatureRequest().setFilterRect(areaDInteres))
            ids = [i.id() for i in it]
            layer.selectByIds(ids)
            # taulaAtributs('Seleccionats',layer)
        else:
            missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

    def showXY(self,p):
        self.bXY.setText( str("%.2f" % p.x()) + ", " + str("%.2f" % p.y() ))
        # try:
        #     if self.qvPrint.pucMoure:
        #         self.dwPrint.move(self.qvPrint.dockX-100, self.qvPrint.dockY-120)
        # except:
        #     return

    def showScale(self,scale ):
        self.bScale.setText( " Escala 1:" + str(int(round(scale)))) 
        #Si estàvem editant l'escala i entrem aquí vol dir que hem abortat missió
        #Per tant, deixem d'editar-la
        if self.editantEscala:  
            self.editantEscala=False
            self.leScale.setParent(None)

    def definirLabelsStatus(self):    
        

        self.leSeleccioExpressio = QLineEdit()
        self.leSeleccioExpressio.setStyleSheet("QLineEdit {margin: 0px; border: 0px; padding: 0px; background-color: white;}")  #Per la barra de cerca inferior, així queda millor integrada
        
        # self.leSeleccioExpressio.setGraphicsEffect(self._menuBarShadow)
        self.leSeleccioExpressio.returnPressed.connect(seleccioExpressio)
        self.statusbar.addPermanentWidget(self.leSeleccioExpressio, 50)
        self.statusbar.setSizeGripEnabled( False )
        self.leSeleccioExpressio.setPlaceholderText('Cerca un text per filtrar elements')
        self.leSeleccioExpressio.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.leSeleccioExpressio.show()
        # spacer = QSpacerItem(1000, 1000, QSizePolicy.Expanding,QSizePolicy.Maximum)
        # self.statusbar.addPermanentWidget(spacer)
        styleheetLabel='''
            QLabel {
                background-color: #F9F9F9;
                color: #38474F;
                border: 0px;
                margin: 0px;
                padding: 4px;
            }'''
        stylesheetButton='''
            QvPushButton {
                background-color: #F9F9F9;
                color: #38474F;
                margin: 0px;
                border: 0px;
                padding: 4px;
            }'''
        stylesheetLineEdit='''
            margin: 0px; border: 0px; padding: 0px;
            '''

        self.sbCarregantCanvas = QProgressBar()
        self.sbCarregantCanvas.setRange(0,0)
        self.statusbar.addPermanentWidget( self.sbCarregantCanvas, 0 )
        # self.sbCarregantCanvas.hide()

        self.lblConnexio = QLabel()
        self.lblConnexio.setStyleSheet(styleheetLabel)
        self.lblConnexio.setFrameStyle(QFrame.StyledPanel )
        self.statusbar.addPermanentWidget( self.lblConnexio, 0 )
        self.lblConnexio.setText(estatConnexio)

        self.wXY = QWidget()
        self.lXY=QHBoxLayout()
        self.lXY.setContentsMargins(0,0,0,0)
        self.lXY.setSpacing(0)
        self.wXY.setLayout(self.lXY)
        self.bXY = QvPushButton(flat=True)
        self.bXY.clicked.connect(self.editarXY)
        self.bXY.setStyleSheet(stylesheetButton)
        self.lXY.addWidget(self.bXY)
        self.leXY = QLineEdit()
        self.leXY.setFixedHeight(24)
        self.leXY.setFixedWidth(142)
        self.leXY.setStyleSheet(stylesheetLineEdit)
        self.leXY.returnPressed.connect(self.returnEditarXY)
        self.lXY.addWidget(self.leXY)
        self.leXY.hide()
        self.statusbar.addPermanentWidget(self.wXY, 0 )
        # self.showXY(QCursor.pos())

        self.lblProjeccio = QLabel()
        self.lblProjeccio.setStyleSheet(styleheetLabel)
        self.lblProjeccio.setFrameStyle(QFrame.StyledPanel )
        # self.lblProjeccio.setMinimumWidth( 140 )
        self.statusbar.addPermanentWidget( self.lblProjeccio, 0 )


        #Per no haver de posar un Line Edit a sobre del botó, fem un widget que contingui un layout. Aquest layout contindrà el botó, i a vegades el Line Edit
        self.wScale=QWidget()
        self.lScale=QHBoxLayout()
        self.lScale.setContentsMargins(0,0,0,0)
        self.lScale.setSpacing(0)
        self.wScale.setLayout(self.lScale)
        self.bScale = QvPushButton(flat=True)
        self.bScale.setStyleSheet(stylesheetButton)
        self.lScale.addWidget(self.bScale)

        # self.bScale.setFrameStyle(QFrame.StyledPanel )
        # self.bScale.setMinimumWidth( 140 )
        self.bScale.clicked.connect(self.editarEscala)
        self.statusbar.addPermanentWidget( self.wScale, 0 )
        self.editantEscala = False

        self.bOrientacio = QvPushButton(flat=True)
        self.bOrientacio.setStyleSheet(stylesheetButton)

        # self.bScale.setFrameStyle(QFrame.StyledPanel )
        
        # self.bOrientacio.setMinimumWidth( 140 )
        self.statusbar.addPermanentWidget( self.bOrientacio, 0 )

    
        self.lblProjecte = QLabel()
        self.lblProjecte.setStyleSheet(styleheetLabel)
        self.lblProjecte.setFrameStyle(QFrame.StyledPanel )
        # self.lblProjecte.setMinimumWidth( 140 )
        self.statusbar.addPermanentWidget( self.lblProjecte, 0 )
    
    def connectarProgressBarCanvas(self):
        self.canvas.mapCanvasRefreshed.connect(self.hideSB)
        self.canvas.renderStarting.connect(self.showSB)
        self.canvas.renderComplete.connect(self.hideSB)

    def showSB(self):
        self.sbCarregantCanvas.show()

    def hideSB(self):
        self.sbCarregantCanvas.hide()

    def editarOrientacio(self):
        self.mapeta.cambiarRotacion()
              
        if self.canvas.rotation()==0:
            self.bOrientacio.setText(' Orientació: Nord')
        else:
            self.bOrientacio.setText(' Orientació: Eixample')

 
        self.canvas.refresh()

    def editarXY(self):
        self.bXY.hide()
        self.leXY.show()
        self.leXY.setText(self.bXY.text())
       
        
    def returnEditarXY(self):
        try:
            x,y = self.leXY.text().split(',')
            x = x.strip()
            y = y.strip()
            def num_ok(num):
                return all(char.isdigit() or char=='.' for char in num)
            if x is not None and y is not None:
                if num_ok(x) and num_ok(y):
                    self.canvas.setCenter(QgsPointXY(float(x),float(y)))
                    self.canvas.refresh()
        except:
            print("ERROR >> Coordenades mal escrites")
        self.bXY.show()
        self.leXY.hide()
        self.leXY.setText("")

    def editarEscala(self):
        if self.editantEscala == False:
            self.editantEscala = True
            self.bScale.setText(' Escala 1: ')
            self.leScale = QLineEdit()
            self.leScale.setStyleSheet('margin: 0px; border: 0px; padding: 0px;')
            self.lScale.addWidget(self.leScale)
            # self.leScale.setGeometry(48,0,100,20)
            self.leScale.setMinimumWidth(10)
            # self.leScale.setMaximumWidth(35)
            self.leScale.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.leScale.returnPressed.connect(self.escalaEditada)
            self.leScale.show()
            self.leScale.setFocus()
            self.onlyInt = QIntValidator()
            self.leScale.setValidator(self.onlyInt)

    def escalaEditada(self):
        escala = self.leScale.text()
        self.leScale.setParent(None)
        self.lScale.removeWidget(self.leScale)
        self.canvas.zoomScale(int(escala))
        self.editantEscala = False

    def centrarMapa(self):
        qV.canvas.zoomToFullExtent()
        qV.canvas.refresh()
  
    def obrirMapeta(self):
        if self.dwMapeta.isHidden:
            self.dwMapeta.show()
        else:
            self.dwMapeta.hide()

    def obrirUbicacions(self):
        if self.dwUbicacions.isHidden:
            self.dwUbicacions.show()
        else:
            self.dwUbicacions.hide()

    def obrirBrowserGrafiques(self):
        if self.dwBrowserGrafiques.isHidden:
            self.dwBrowserGrafiques.show()
        else:
            self.dwBrowserGrafiques.hide()

        # recorrerUbicacions()
      
    def obrirBotonera(self):
        if self.botoneraVisible:
            self.dockWidget.hide()
            self.botoneraVisible = False
        else:
            self.dockWidget.show()
            self.botoneraVisible = True

    def obrirTaula(self):
        if self.dwTaulaAtributs.isHidden():
            self.dwTaulaAtributs.show()  
        else:
            self.dwTaulaAtributs.hide()

    def obrirTaulaAtributs(self):
        if self.dwTaulaAtributs.isHidden():
            self.dwTaulaAtributs.show()  
        else:
            self.dwTaulaAtributs.hide()
            calcularAtributs()
            self.dwTaulaAtributs.setWindowTitle("Taula d'atributs")

    def obrirCalculadora(self):
        self.dwCalculadora.setWindowTitle('Calculadora QVista')
        self.dwCalculadora.show()  

    def obrirLlegenda(self):
        if self.dwLlegenda.isHidden():
            self.dwLlegenda.show()  
        else:
            self.dwLlegenda.hide()

    def obrirDistrictes(self):
        if self.dwArbreDistrictes.isHidden():
            self.dwArbreDistrictes.show()
        else:
            self.dwArbreDistrictes.hide()

    def obrirCataleg(self):
        self.dwCataleg.show()

    def obrirCatalegProjectesLlista(self):
        self.dwCatalegProjectesLlista.show()

    def obrirQgis(self):
        # TODO: Pensar i generalitzar la obertura de QGis segon directori paquetitzat
        self.project.write('c:/temp/projTemp.qgs')
        QProcess.startDetached(r'D:\OSGeo4W64\bin\qgis-bin-g7.4.1.exe c:/temp/projTemp.qgs')

    def obrirDialegProjecte(self):
        if self.teCanvisPendents(): #Posar la comprovació del dirty bit
            ret = self.missatgeDesar(titol='Crear un nou mapa',txtCancelar='Cancel·lar')
            if ret == QMessageBox.AcceptRole:
                b = guardarProjecte()
                if not b: return
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                pass
            elif ret == QMessageBox.DestructiveRole:
                return

        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl('../dades/projectes/'))
        rect = self.canvas.extent()
        nfile,_ = dialegObertura.getOpenFileName(None,"Obrir mapa Qgis", "../dades/projectes/", "Tots els mapes acceptats (*.qgs *.qgz);; Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)")

        if nfile is not None:
            self.obrirProjecte(nfile, rect)
           
    def obrirDialegNovaCapa(self):
        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl('../Dades/Capes/'))
        dialegObertura.setSupportedSchemes(["Projectes Qgis (*.qgs)", "Otro esquema"])

        nfile,_ = dialegObertura.getOpenFileName(None,"Nova capa", '../Dades/Capes/', "Totes les capes acceptats (*.csv *.shp *.gpkg *.qlr );; CSV (*.csv);; Shapes (*.shp);; Geopackage (*.gpkg);;  Layers Qgis(*.qlr)")

        if nfile is not None:
            # extensio = nfile[-3:]
            # print (extensio)
            _, extensio = os.path.splitext(nfile)
            if extensio.lower() == '.shp' or extensio.lower() =='.gpkg':
                layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
                if not layer.isValid():
                    return
                renderer=layer.renderer()
                self.project.addMapLayer(layer)
                self.setDirtyBit()
            else:
                if extensio.lower() == '.qlr':
                    # print(nfile)
                    afegirQlr(nfile)
                # QgsLayerDefinition().loadLayerDefinition(nfile, self.project, self.root)
                elif extensio.lower() == '.csv':
                    carregarLayerCSV(nfile)

    def recorrerFields(self):
        if self.potsRecorrer:
            # print (self.calculadora.ui.cbLayers.currentText())
            layer = self.project.instance().mapLayersByName(self.calculadora.ui.cbLayers.currentText())[0]
            
            self.calculadora.ui.lwFields.clear()
            fields = layer.fields()
            for field in fields:
                if (field.typeName()!='String' and field.typeName()!='Date' and field.typeName()!='Date'):
                    # print (field.typeName())
                    self.calculadora.ui.lwFields.addItem(field.name())
                    # fieldNames = [field.name() for field in fields]
                    # self.lwFields.addItems(fieldNames)
                else:
                    pass
    
    def recorrerLayersFields(self):
        try:
            self.llegenda.setCurrentLayer(self.llegenda.capaPerNom(self.calculadora.ui.cbLayers.currentText()))
            self.calculadora.ui.cbLayers.clear()
            self.potsRecorrer=False
            layers = self.canvas.layers()
            layerList = []
            for layer in layers:
                layerList.append(layer.name())
            self.calculadora.ui.cbLayers.addItems(layerList)
            selectedLayerIndex = self.calculadora.ui.cbLayers.currentIndex()

            self.selectedLayer = layers[selectedLayerIndex]
            
            self.potsRecorrer=True
            self.recorrerFields()
        except:
            pass
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Warning)
            
            # msg.setText(str(sys.exc_info()[1]))
            # # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            # msg.setWindowTitle("ERROR: qVista >> recorrerLayersFields")
            # msg.setStandardButtons(QMessageBox.Close)
            # retval = msg.exec_()


    def modeDebug(self):
        self.menuFuncions.show()

    def seleccioMapaFons(self):
        pass

    def favorit(self):
        pass

    def teCanvisPendents(self):
        return self.canvisPendents
    def missatgeDesar(self, titol="Sortir de qVista", txtDesar='Desar-los', txtDescartar='Descartar-los',txtCancelar='Romandre a qVista'):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(titol)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Hi ha canvis pendents de desar.")
        msgBox.setInformativeText("Què voleu fer?")
        msgBox.addButton(QvPushButton(txtDesar,destacat=True),QMessageBox.AcceptRole)
        msgBox.addButton(QvPushButton(txtDescartar),QMessageBox.DestructiveRole)
        msgBox.addButton(QvPushButton(txtCancelar),QMessageBox.RejectRole)
        return msgBox.exec()
    def provaDeTancar(self):
        if self.teCanvisPendents():
            
            # msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            # msgBox.setDefaultButton(QMessageBox.Save)
            ret = self.missatgeDesar()
            if ret == QMessageBox.AcceptRole:
                b = guardarProjecte()
                if not b: return
                #Si cancel·la, retornem. Si no, cridem a gestioSortida
                self.gestioSortida()
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                self.gestioSortida()
            elif ret == QMessageBox.DestructiveRole:
                return
                
        else:
            self.gestioSortida()
    def actualitzaMapesRecents(self,ultim=None):
        #Si no tenim en memòria els mapes recents, si existeixen els carreguem. Si no, doncs una llista buida
        if not hasattr(self,'mapesRecents'):
            if not os.path.isfile(arxiuMapesRecents):
                self.mapesRecents=[]
            else:
                with open(arxiuMapesRecents,'r',encoding='utf-8') as recents:
                    self.mapesRecents=list(recents.readlines())
        #Desem els mapes recents, eliminant repeticions i salts de línia que poden portar problemes
        with open(arxiuMapesRecents,'w',encoding='utf-8') as recents:
            print(self.mapesRecents)
            #Ens carreguem els salts de línia per si n'ha quedat algun, fent un map. Creem un set 
            self.mapesRecents=[x.replace('\n','') for x in self.mapesRecents]
            self.mapesRecents=sorted(set(self.mapesRecents),key=lambda x: self.mapesRecents.index(x))[:9]
            for x in self.mapesRecents:
                recents.write(x+'\n')
        #Finalment creem les accions
        # self.menuRecents=QMenu('Mapes recents',self.menuMapes)
        self.menuRecents.clear()
        self.accionsMapesRecentsDict={QAction(x):x.replace('\n','') for x in self.mapesRecents} #Fem un diccionari on la clau és l'acció i el valor és la ruta del mapa que ha d'obrir l'acció
        for x, y in self.accionsMapesRecentsDict.items():
            x.setToolTip(y)
            #functools.partial crea una funció a partir de passar-li uns determinats paràmetres a una altra
            #Teòricament serveix per passar-li només una part, però whatever
            #Si fèiem connect a lambda: self.obrirProjecte(y) o similars, no funcionava i sempre rebia com a paràmetre la última y :'(
            x.triggered.connect(functools.partial(self.obrirProjecte,y,None))
            self.menuRecents.addAction(x)
        if ultim is not None:
            self.mapesRecents.insert(0,ultim)

    def gestioSortida(self):
        
        try:
            if self.ubicacions is not None:
                self.ubicacions.ubicacionsFi()
        except Exception  as ee:
            print(str(ee))

        try:
            if self.cAdrec is not None:
                self.cAdrec.cercadorAdrecaFi()
        except Exception as ee:
            print(str(ee))
        try:
            QvApp().logFi() #fa aixo pero no arriba a tancar la app
            QCoreApplication.exit(0) #preguntar al Jordi que li sembla
        except Exception as ee:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            
            msg.setText(strin(ee))
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()

    def handleSave(self):
        self.table = self.taulesAtributs.widget(0)
        path,_ = QFileDialog.getSaveFileName(self, 'Guardar archivo', '', 'CSV(*.csv)')
        if path is not None:
            with open(path, 'w', newline='') as stream:
                writer = csv.writer(stream, delimiter='|', quotechar='¨', quoting=csv.QUOTE_MINIMAL)
                for row in range(self.table.rowCount()):
                    rowdata = []
                    for column in range(self.table.columnCount()):
                        item = self.table.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    def pavimentacio(self): 
        self.project.read('d:/qVista/Dades/CatalegProjectes/Vialitat/PavimentacioDemo.qgs')       
        # self.lblTitolProjecte.setFont(QvConstants.FONTTITOLS)
        # self.lblTitolProjecte.setText(self.project.title())
        self.dwPavim = DockPavim(self)
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwPavim)
        self.dwPavim.show()    
        
    def marxesCiutat(self): 
        self.project.read('d:/MarxesCiutat/MarxesCiutat.qgs')      
        # self.lblTitolProjecte.setFont(QvConstants.FONTTITOLS)
        # self.lblTitolProjecte.setText(self.project.title())
        self.lblTitolProjecte.setText("Marxes exploratòries")
        self.dwMarxes = MarxesCiutat(self)
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwMarxes)
        self.dwMarxes.show()    
    # def mousePressEvent(self, event):
    #     super().mouseMoveEvent(event)
    #     if event.button()==Qt.LeftButton:
    #         self.oldPos = event.globalPos()

    # def mouseMoveEvent(self, event):
    #     super().mouseMoveEvent(event)
    #     if event.buttons() & Qt.LeftButton:
    #         if self.maximitzada:
    #             self.restaurarFunc()
    #             #Desmaximitzar
    #         delta = QPoint(event.globalPos() - self.oldPos)
    #         # print(delta)
    #         self.move(self.x() + delta.x(), self.y() + delta.y())
    #         self.oldPos = event.globalPos()
    # def mouseDoubleClickEvent(self,event):
    #     super().mouseDoubleClickEvent(event)
    #     if event.button()==Qt.LeftButton:
    #         self.restaurarFunc()
    # def enterEvent(self,event):
    #     super().enterEvent(event)
    #     qApp.setCursor(QCursor(Qt.ArrowCursor))
        
# def bicing(self):
#         self.bicing=Bicis(self)
#         self.bicing.show()

# Altres clases -------------------------------------------------------------------

class DialegCSV(QDialog):
    def __init__(self, llistaCamps=None):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self) 
        llistaProjeccions =['UTM ED50', 'UTM ETRS89', 'Lat Long']
        self.ui.cbDelProjeccio.clear()
        self.ui.cbDelProjeccio.addItems(llistaProjeccions)
        if llistaCamps is not None:
            self.ui.cbDelX.clear()
            self.ui.cbDelY.clear()
            self.ui.cbDelX.addItems(llistaCamps)
            self.ui.cbDelY.addItems(llistaCamps)
        self.exec()


    def closeEvent(self, event):
        pass

# class EstilPropi(QProxyStyle):
#     def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

#         if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
#             return 120
#         else:
#             return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)

# funcions globals QVista --------------------------------------------------------

def seleccioLliure():
    layer=qV.llegenda.currentLayer()
    qV.markers.hide()
    try:
        qV.canvas.scene().removeItem(qV.toolSelect.rubberband)
    except:
        pass

    # layerList = QgsMapLayerRegistry.instance().mapLayersByName("Illes")
    # if layerList:
    #     lyr = layerList[0]

    if layer is not None:
        qV.actionMapSelect = QAction('Seleccionar dibuixant', qV)
        qV.toolSelect = QvSeleccioPerPoligon(qV,qV.canvas, layer)

        qV.toolSelect.setOverlap(qV.checkOverlap.checkState())

        qV.toolSelect.setAction(qV.actionMapSelect)
        qV.canvas.setMapTool(qV.toolSelect)
        # taulaAtributs('Seleccionats', layer)
    else:
        missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

def seleccioClick():    
    tool = QvSeleccioElement(qV.canvas, qV.llegenda)
    qV.canvas.setMapTool(tool)
    # qV.taulesAtributs.taula.toggleSelection(True)
    # taulaAtributs('Seleccionats', layer)
    # taulaAtributsSeleccionats()


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        


import shutil

def disgregarDirele():

    __numerosCSV = r'Dades\TAULA_DIRELE.csv'
    __path_disgregados= r'Dades\dir_ele\\'
    """

    """


    if os.path.isdir(__path_disgregados):
        shutil.rmtree(__path_disgregados)
        # os.rmdir(__path_disgregados)
    
    createFolder(__path_disgregados)



    if __numerosCSV:
        f_read = open(__numerosCSV, 'r')
        with f_read:
            reader = csv.reader(f_read, delimiter = ',')
            count=0
            codi_carrer_old=''
            for row in reader:    
                if count==0:
                    cabecera=row
                else:
                    codi_carrer=row[0]
                    if codi_carrer != codi_carrer_old:
                        path= __path_disgregados+str(codi_carrer)+'.csv'
                        try:
                            f_write.close()
                        except:
                            pass

                        f_write = open(path, 'a')
                        writer = csv.writer(f_write)
                        writer.writerow(cabecera)
                        writer.writerow(row)
                    else:
                        writer.writerow(row)
                        
                    codi_carrer_old= codi_carrer
                count += 1
            f_write.close()




    pass

def nivellCsv(fitxer: str,delimitador: str,campX: str,campY: str, projeccio: int = 23031, nomCapa: str = 'Capa sense nom', color = 'red', symbol = 'circle'):
    uri = "file:///"+fitxer+"?type=csv&delimiter=%s&xField=%s&yField=%s" % (delimitador,campX,campY)
    layer = QgsVectorLayer(uri, nomCapa, 'delimitedtext')
    layer.setCrs(QgsCoordinateReferenceSystem(projeccio, QgsCoordinateReferenceSystem.EpsgCrsId))
    if layer is not None or layer is not NoneType:
        symbol = QgsMarkerSymbol.createSimple({'name': symbol, 'color': color})
        if layer.renderer() is not None: 
            layer.renderer().setSymbol(symbol)
        qV.project.addMapLayer(layer)
        print("add layer")
        qV.canvisPendents=True
        qV.botoDesarProjecte.setIcon(qV.iconaAmbCanvisPendents)
    else: print ("no s'ha pogut afegir la nova layer")

    #symbol = QgsMarkerSymbol.createSimple({'name': 'square', 'color': 'red'})
    #layer.renderer().setSymbol(symbol)
    #https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#modify-features

# def carregaCSVWizard(fitxer: str,delimitador: str,campX: str,campY: str, projeccio: int = 23031, nomCapa: str = 'Capa sense nom', color, symbol):
#     uri = "file:///"+fitxer+"?type=csv&delimiter=%s&xField=%s&yField=%s" % (delimitador,campX,campY)
#     layer = QgsVectorLayer(uri, nomCapa, 'delimitedtext')
#     layer.setCrs(QgsCoordinateReferenceSystem(projeccio, QgsCoordinateReferenceSystem.EpsgCrsId))
#     if layer is not None:
#         symbol = QgsMarkerSymbol.createSimple({'name': symbol, 'color': color})
#         layer.renderer().setSymbol(symbol)
#         qV.project.addMapLayer(layer)
#         print("add layer")

def seleccioCercle():
    seleccioClick()
    layer=qV.llegenda.currentLayer()  
    try:
        qV.canvas.scene().removeItem(qV.toolSelect.rubberband)
    except:
        pass
    qV.toolSelect = QvSeleccioCercle(qV, 10, 10, 30)
    qV.toolSelect.setOverlap(qV.checkOverlap.checkState())
    qV.canvas.setMapTool(qV.toolSelect)

def seleccioClicks():
    seleccioClick()
    layer=qV.llegenda.currentLayer()  
    try:
        qV.canvas.scene().removeItem(qV.toolSelect.rubberband)
    except:
        pass

    tool = QvSeleccioPunt(qV, qV.canvas)
    qV.canvas.setMapTool(tool)
    # taulaAtributsSeleccionats()

# def plotMapa():
#     mapRenderer = qV.canvas.mapRenderer()
#     c = QgsComposition(mapRenderer)
#     c.setPlotStyle(QgsComposition.print())

def seleccioExpressio():
    if qV.leSeleccioExpressio.text().lower() == 'help':
        qV.infoQVista()
        return

    if qV.leSeleccioExpressio.text().lower() == 'direle':
        disgregarDirele()
        return

    if qV.leSeleccioExpressio.text().lower() == 'version':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        
        msg.setText('20190621 12:12  con gpkd-shm y gpkg-wal')
        # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
        msg.setWindowTitle("qVista version")
        msg.setStandardButtons(QMessageBox.Close)
        retval = msg.exec_()
        return     
    if (qV.leSeleccioExpressio.text().lower() == 'qvdebug') :
        qV.modeDebug()
        return

    if (qV.leSeleccioExpressio.text().lower() == 'qvtemps') :
        missatgeCaixa('Temps per arrancar:', str('%.1f'%qV.tempsTotal))
        return

    layer=qV.llegenda.currentLayer()
    if layer is not None:
    #     expr = QgsExpression( qV.leSeleccioExpressio.text())
    #     it = layer.getFeatures( QgsFeatureRequest( expr ) )
    #     ids = [i.id() for i in it]
    #     layer.selectByIds(ids)
    #     # taulaAtributs('Seleccionats',layer) 
        textCercat=""
        layer=qV.llegenda.currentLayer()
        if layer is not None:
            for field in layer.fields():
                if field.typeName()=='String' or field.typeName()=='text'  or field.typeName()[0:4]=='VARC':
                    textCercat = textCercat + field.name()+" LIKE '%" + qV.leSeleccioExpressio.text()+ "%'"
                    textCercat = textCercat + ' OR '

            layer.setSubsetString(textCercat[:-4])
            ids = [feature.id() for feature in layer.getFeatures()]
            qV.canvas.zoomToFeatureIds(layer, ids)
            print (textCercat[:-4])
    else:
        missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

#A més de desar, retornarà un booleà indicant si l'usuari ha desat (True) o ha cancelat (False)

def guardarProjecte():
    """ la funcio retorna si s'ha acabat guardant o no """
    """  Protecció dels projectes read-only: tres vies:
    -       Variable del projecte qV_readOnly=’True’
    -       Ubicació en una carpeta de només-lectura
    -       Ubicació en una de les subcarpetes de N:\SITEB\APL\PyQgis\qVista
    -       Ubicació en una de les subcarpetes de N:\9SITEB\Publicacions\qVista
    """
    #Pensar què fer quan es dona al botó de gurdar i no hi ha canvis per guardar

    if QgsExpressionContextUtils.projectScope(qV.project).variable('qV_readOnly') == 'True':
        return guardarDialegProjecte()
    elif qV.pathProjecteActual == 'mapesOffline/qVista default map.qgs':
        return guardarDialegProjecte()
    elif qV.pathProjecteActual.startswith( 'n:/siteb/apl/pyqgis/qvista' ):
        return guardarDialegProjecte()
    elif qV.pathProjecteActual.startswith( 'n:/9siteb/publicacions/qvista' ):
        return guardarDialegProjecte()
    else:
        qV.project.write(qV.pathProjecteActual)
        qV.canvisPendents = False
        qV.botoDesarProjecte.setIcon(qV.iconaSenseCanvisPendents)
        return True
        
#Anomena i desa (AKA Guardar como)
def guardarDialegProjecte():
    nfile,_ = QFileDialog.getSaveFileName(None,"Guardar Projecte Qgis", ".", "Projectes Qgis (*.qgs)")
    if nfile=='': return False
    elif nfile.endswith('mapesOffline/qVista default map.qgs') or nfile.startswith( 'n:/siteb/apl/pyqgis/qvista' ) or nfile.startswith( 'n:/9siteb/publicacions/qvista' ):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Advertència")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("No pots guardar el teu mapa en aquesta direcció.")
        msgBox.setInformativeText("Prova de fer-ho en una altre.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec()
        return False 
    qV.project.write(nfile)
    qV.pathProjecteActual = nfile
    qV.lblProjecte.setText(qV.project.baseName())
    qV.botoDesarProjecte.setIcon(qV.iconaSenseCanvisPendents)
    qV.canvisPendents = False
    return True
    #print(scale)

def nouMapa():
    if qV.teCanvisPendents(): #Posar la comprovació del dirty bit
        ret = qV.missatgeDesar(titol='Crear un nou mapa',txtCancelar='Cancel·lar')
        if ret == QMessageBox.AcceptRole:
            b = guardarProjecte()
            if not b: return
        elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
            pass
        elif ret == QMessageBox.DestructiveRole:
            return
    dialegNouMapa = QvNouMapa(qV)
    dialegNouMapa.exec()
    # qV.obrirProjecte("./__newProjectTemplate.qgs")

def executeChrome():
    process = QProcess(qV)
    pathChrome = "c:/windows/system32/calc.exe"
    process.start(pathChrome)
    app.processEvents()
def obreDocumentacio():
    qV.startMovie()
    doc=QvDocumentacio(qV)
    qV.stopMovie()
    doc.show()
def carregarFieldsCalculadora():
    # print(qV.calculadora.ui.cbLayers.currentText())
    layer = QvLlegenda.capaPerNom(qV,qV.calculadora.ui.cbLayers.currentText())
    # layer = qV.project.instance().mapLayersByName(qV.calculadora.ui.cbLayers.currentText())[0]
    taula=qV.calculadora.ui.twCalculadora
    numeroFields=0
    fila=0
    columna=0
    taula.setColumnCount(2)
    taula.setHorizontalHeaderLabels(['','Total'])
    nombreFieldsSeleccionats=0
    for a in qV.calculadora.ui.lwFields.selectedItems():
        nombreFieldsSeleccionats=nombreFieldsSeleccionats+1
    taula.setRowCount(nombreFieldsSeleccionats+1)
    for a in qV.calculadora.ui.lwFields.selectedItems():
        total=0
        item = QTableWidgetItem(a.text())
        taula.setItem(fila+1,0,item)
        nombreElements=0
        field=layer.fields().lookupField(a.text())
        # print (field)
        for feature in layer.selectedFeatures():
            calcul=feature.attributes()[layer.fields().lookupField(a.text())]
            total=total+calcul
            nombreElements=nombreElements+1

        item = QTableWidgetItem(str(total))
        taula.setItem(fila+1,1,item)
        # print('Total: '+a.text()+": ",total)
        fila=fila+1
    item = QTableWidgetItem('Nombre elements')
    taula.setItem(0,0,item)
    item = QTableWidgetItem(str(nombreElements))
    taula.setItem(0,1,item)
    taula.resizeColumnsToContents()

def calcularAtributs():
    layer=qV.llegenda.currentLayer()
    if layer:
        pass
    else:
        missatgeCaixa('a','b')

def escollirNivellGPX():
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir GPKG", ".", "Fitxers Shape (*.gpkg)")
    #fileInfo = QFileInfo(nfile)
    layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
    if not layer.isValid():
        return
    renderer=layer.renderer()
    # print(renderer.type())
    
    qV.project.addMapLayer(layer)
    qV.canvisPendents=True
    qV.botoDesarProjecte.setIcon(qV.iconaAmbCanvisPendents)
    # features=layer.getFeatures()
    # taulaAtributs('Total',layer)

def escollirNivellCSV():
    # layer = qV.llegenda.view.currentLayer()
    # qV.project.removeMapLayer(layer)
    # qV.canvas.refresh()
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer CSV", "U:\QUOTA\Comu_imi\Becaris", "CSV (*.csv)")
   
    # print(dCSV.ui.cbDelimitador.currentText())
    # print("D"+dCSV.ui.cbDelimitador.currentText()+"D")
    if nfile:
        with open(nfile) as f:
            reader = csv.DictReader(f, delimiter=';')
            llistaCamps = reader.fieldnames
        #print (llistaCamps)
        projeccio = 25831
        titol = 'Còpia de Models adreces.csv'
        nivellCsv(nfile,';','XNUMPOST','YNUMPOST', projeccio, nomCapa = titol)
        
# def escollirNivellCSV():
#     # layer = qV.llegenda.view.currentLayer()
#     # qV.project.removeMapLayer(layer)
#     # qV.canvas.refresh()
#     nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer CSV", ".", "CSV (*.csv)")

    
#     dCSV = DialegCSV()
#     dCSV.finished.connect(dCSV)
   
#     # print(dCSV.ui.cbDelimitador.currentText())
#     # print("D"+dCSV.ui.cbDelimitador.currentText()+"D")
#     projeccio = 0
#     if nfile:
#         with open(nfile) as f:
#             reader = csv.DictReader(f, delimiter=dCSV.ui.cbDelimitador.currentText())
#             llistaCamps = reader.fieldnames
#         # print (llistaCamps)
        
#         dCSV = DialegCSV(llistaCamps)

#         if dCSV.ui.cbDelProjeccio.currentText() == 'UTM ED50':
#             projeccio = 23031
#         elif dCSV.ui.cbDelProjeccio.currentText() == 'UTM ETRS89':
#             projeccio = 25831
#         elif dCSV.ui.cbDelProjeccio.currentText() == 'Lat Long':
#             projeccio = 4326
#         titol = dCSV.ui.leNomCapa.text()
#         nivellCsv(nfile,dCSV.ui.cbDelimitador.currentText(),dCSV.ui.cbDelX.currentText(),dCSV.ui.cbDelY.currentText(), projeccio, nomCapa = titol)
#         #carregarCsvATaula(nfile,';')
    

globalLlistaCamps=None
tamanyReader=0
def carregarLayerCSV(nfile):
        if nfile: 
            qV.startMovie()
            qApp.setOverrideCursor(Qt.WaitCursor)
            assistent=QvCarregaCsv(nfile,nivellCsv,qV)
            qApp.restoreOverrideCursor()
            assistent.setModal(True)
            #assistent.setGraphicsEffect(QvConstants.ombra(assistent,radius=30,color=QvConstants.COLORCLAR))
            #assistent.setWindowFlags(assistent.windowFlags() | Qt.Popup)
            #assistent.setWindowFlags(assistent.windowFlags() | Qt.WindowStaysOnTopHint)
            #qV.raise_()
            qV.stopMovie()
            assistent.show()
            #assistent.raise_()
            #qV.setFocus()
            

def carregarNivellQlr():
    index = qV.wCataleg.ui.treeCataleg.currentIndex()
    mpath=qV.qModel.fileInfo(index).absoluteFilePath()
    afegirQlr(mpath)

def carregarProjecteLlista():
    index = qV.wCatalegProjectesLlista.ui.treeCataleg.currentIndex()
    mpath=qV.qModelProjectesLlista.fileInfo(index).absoluteFilePath()
    qV.obrirProjecte(mpath)

def updateMetadadesCataleg():
    index = qV.wCataleg.ui.treeCataleg.currentIndex()
    # print('Index: ', index)
    nom=qV.qModel.fileInfo(index).baseName()
    path=qV.qModel.fileInfo(index).path()
    # print(path+nom+'.jpg')
    imatge = QPixmap(path+'/'+nom+'.jpg')
    qV.wCataleg.ui.lblMapaCataleg.setPixmap(imatge)
    doc=QTextDocument()
    doc.setHtml(path+'/'+nom+'.htm')
    qV.wCataleg.ui.txtMetadadesCataleg.setDocument(doc)
    try:
        text=open(path+'/'+nom+'.htm').read()
        qV.wCataleg.ui.txtMetadadesCataleg.setHtml(text)
    except:
        # print ('Error carrega HTML')
        pass

def imatgeClickada():
    # print ('Clickada imatge')
    pass

def escollirNivellQlr():
    # layer = qV.view.currentLayer()
    # qV.project.removeMapLayer(layer)
    # qV.canvas.refresh()

    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer QLR", ".", "QLR (*.qlr)")

    if nfile:
        afegirQlr(nfile)

def afegirQlr(nom): 

    layers = QgsLayerDefinition.loadLayerDefinitionLayers(nom)

    qV.project.addMapLayers(layers, True)
    qV.canvisPendents=True
    qV.botoDesarProjecte.setIcon(qV.iconaAmbCanvisPendents)
    # QgsLayerDefinition().loadLayerDefinition(nom, qV.project, qV.llegenda.root)
    return

def afegirNivellSHP():
    nfile,_ = QFileDialog.getOpenFileName(None, "Obrir SHP", ".", "Fitxers Shape (*.shp)")
    #fileInfo = QFileInfo(nfile)
    layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
    if not layer.isValid():
        return
    renderer=layer.renderer()
    # print(renderer.type())
    
    qV.project.addMapLayer(layer)
    qV.canvisPendents=True
    qV.botoDesarProjecte.setIcon(qV.iconaAmbCanvisPendents)
    # features=layer.getFeatures()
    # taulaAtributs('Total',layer)

    #Imprimir els camps de dades del nivell
    # for field in layer.fields():
    #   print(field.name(), field.typeName())
    #   for feature in features:
    #     print(feature[field.name()])
    # renderer = layer.renderer()

def loadCsv():
    fileName, _ = QFileDialog.getOpenFileName(None, "Open CSV",(QDir.homePath()), "CSV (*.csv *.tsv)")
    qV.modelTaula =  QStandardItemModel(qV)
        
    qV.tableView.setModel(qV.modelTaula)
    qV.tableView.horizontalHeader().setStretchLastSection(True)
    qV.tableView.setShowGrid(True)
    #qV.tableView.setGeometry(10, 50, 780, 645)
    if fileName:
        # print(fileName)
        ff = open(fileName, 'r')
        mytext = ff.read()
        # print(mytext)
        ff.close()
        f = open(fileName, 'r')
        with f:
            #  self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
            #  self.setWindowTitle(self.fname)
            if mytext.count(';') <= mytext.count('\t'):
                reader = csv.reader(f, delimiter = '\t')
                qV.modelTaula.clear()
                for row in reader:    
                    items = [QStandardItem(field) for field in row]
                    qV.modelTaula.appendRow(items)
                    qV.tableView.resizeColumnsToContents()
            else:
                reader = csv.reader(f, delimiter = ';')
                qV.modelTaula.clear()
                for row in reader:    
                    items = [QStandardItem(field) for field in row]
                    qV.modelTaula.appendRow(items)
                    qV.tableView.resizeColumnsToContents()
    qV.dwTaula.show()



def missatgeCaixa(textTitol,textInformacio):
    msgBox=QMessageBox()
    msgBox.setText(textTitol)
    msgBox.setInformativeText(textInformacio)
    ret = msgBox.exec()



def sortir():
    sys.exit()

# Funcio per carregar problemes a GITHUB
def reportarProblema(titol: str, descripcio: str=None):

    if QvApp().bugUser(titol, descripcio):
        print ('Creat el problema {0:s}'.format(titol))
        return True
        #qV.lblResultat.setText("S'ha enviat correctament.")
    else:
        print ('Error al crear el problema {0:s}'.format(titol))
        return False
        #qV.lblResultat.setText('Error al crear el problema {0:s}'.format(titol))

    # '''Crea un "issue" a github'''
    # USUARI = 'qVistaHost'
    # REPOSITORI = 'qVista'
    # PASSWORD = 'XXXXXXXXXXXXXXXXX'

    # # url per crear issues
    # url = 'https://api.github.com/repos/%s/%s/issues' % (USUARI, REPOSITORI)
    # print (url)
    # # Creem una sessió
    # session = requests.Session()
    # session.auth = (USUARI, PASSWORD)

    # # creem el problema
    # problema = {"title": QvApp().usuari+": "+titol,
    #         "body": descripcio}

    # # Afegim el problema
    # r = session.post(url, json.dumps(problema))

    # if r.status_code == 201:
    #     print ('Creat el problema {0:s}'.format(titol))
    #     qV.lblResultat.setText("S'ha enviat correctament.")
    # else:
    #     print ('Error al crear el problema {0:s}'.format(titol))
    #     qV.lblResultat.setText('Error al crear el problema {0:s}'.format(titol))

def esborraCarpetaTemporal():
    '''Esborra el contingut de la carpeta temporal en iniciar qVista
    '''
    #Esborrarem el contingut de la carpeta temporal
    for file in os.scandir(tempdir):
        try:
            #Si no podem esborrar un arxiu, doncs és igual. Deu estar obert. Ja s'esborrarà en algun moment
            os.unlink(file.path)
        except:
            pass

def main(argv):
    # import subprocess
    global qV
    global app
    with qgisapp(sysexit=False) as app: 
        
        # Se instancia QvApp al principio para el control de errores
        qVapp = QvApp()

        # Splash image al començar el programa. La tancarem amb splash.finish(qV)
        # splash_pix = QPixmap('imatges/qvistaLogo2.png')
        splash_pix = QPixmap('imatges/SplashScreen_qVista.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.setEnabled(True)
        splash.showMessage("""Institut Municipal d'Informàtica (IMI) Versió """+versio+'  ',Qt.AlignRight | Qt.AlignBottom, QvConstants.COLORFOSC)
        splash.setFont(QFont(QvConstants.NOMFONT,8))
        splash.show()
        app.setWindowIcon(QIcon('imatges/QVistaLogo_256.png'))
        esborraCarpetaTemporal() #Esborrem els temporals de la sessió anterior
        app.processEvents()
        with open('style.qss') as st:
            app.setStyleSheet(st.read())

        ok = qVapp.logInici()            # Por defecto: family='QVISTA', logname='DESKTOP'
        if not ok:
            print('ERROR LOG >>', qVapp.logError())
            ok = qVapp.logRegistre('Capa1')
            ok = qVapp.logRegistre('Atributs')

        

        # # Idioma
        qVapp.carregaIdioma(app, 'ca')

        app.setStyle(QStyleFactory.create('fusion'))
        

        # estil = EstilPropi('Fusion')   
        # app.setStyle('fusion')
        


        # Prova d'escriure sobre la imatge
        # splash.showMessage("<h1><font color='black'>Versió 0.1 - Work in progress</font></h1>", Qt.AlignTop | Qt.AlignCenter, Qt.white)
        
        # Instanciem la classe QVista i fem qV global per poder ser utilitzada arreu
        # Paso app, para que QvCanvas pueda cambiar cursores
        qV = QVista(app)
       


        # qV.showFullScreen()
        qV.showMaximized()

        # Tanquem la imatge splash.
        splash.finish(qV)
        try:
            avisos=QvAvis()
        except:
            print('no es pot accedir als avisos')
        qVapp.logRegistre('LOG_TEMPS', qV.lblTempsArrencada.text())
        app.aboutToQuit.connect(qV.gestioSortida)

if __name__ == "__main__":
    try:
        main(sys.argv)
        
    except Exception as err:
        QvApp().bugException(err)

    # except Exception as e:
    #     print(str(e))