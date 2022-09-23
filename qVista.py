# -*- coding: utf-8 -*-

# Inici del cronòmetre
import time

startGlobal = time.time()

start = time.time()
# Fitxer principal de importació de llibreries
from qgis.core import (QgsExpressionContextUtils, QgsMapLayer, QgsProject,
                       QgsRasterLayer, QgsVectorLayer)
from qgis.core.contextmanagers import qgisapp, sys
from qgis.gui import (QgsGui, QgsLayerTreeMapCanvasBridge, QgsRubberBand,
                      QgsVertexMarker)
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import (QCoreApplication, QDateTime, QProcess, QSize, Qt,
                              QUrl, pyqtSignal)
from qgis.PyQt.QtGui import (QColor, QDesktopServices, QFont, QIcon,
                             QKeySequence, QPainter, QPen, QPixmap)
from qgis.PyQt.QtWidgets import (QAction, QCheckBox, QDialog, QDockWidget,
                                 QFileDialog, QFrame, QHBoxLayout, QLabel,
                                 QLineEdit, QMainWindow, QMenu, QMessageBox,
                                 QShortcut, QSizePolicy, QSpacerItem,
                                 QSplashScreen, QSplitter, QStyleFactory,
                                 QToolButton, QVBoxLayout, QWhatsThis, QWidget,
                                 qApp)

from configuracioQvista import (QvTempdir, arxiuInfoQVista,
                                carpetaCatalegProjectesLlista, configdir,
                                dadesdir, imatgesDir, projecteInicial,
                                titolFinestra, versio)
from cubista3 import Ui_MainWindow
from info_ui import Ui_Informacio

print ('QvImports: ',time.time()-start)

# Carrega de moduls Qv
iniciTempsModuls = time.time()


import functools  # Eines de funcions, per exemple per avaluar-ne parcialment una
import importlib
import itertools
import os
import re
from pathlib import Path

from moduls import QvFuncions
from moduls.QvApp import QvApp
from moduls.QvAtributs import QvAtributs
from moduls.QvAvis import QvAvis
from moduls.QvBafarada import QvBafarada
from moduls.QvCanvas import QvCanvas
from moduls.QvCanvasAuxiliar import QvCanvasAuxiliar
from moduls.QvCarregadorGPKG import QvCarregadorGPKG
from moduls.QvCatalegCapes import QvCatalegCapes, QvCreadorCatalegCapes
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QvConstants import QvConstants
from moduls.QvCrearMapeta import QvCrearMapetaConBotones
from moduls.QVDistrictesBarris import QVDistrictesBarris
from moduls.QvDocumentacio import QvDocumentacio
from moduls.QvDropFiles import QvDropFiles
from moduls.QvEines import QvEines
from moduls.QvEinesGrafiques import (QvMesuraGrafica, QvSeleccioGrafica,
                                     carregaMascara, eliminaMascara)
from moduls.QvLlegenda import QvLlegenda
from moduls.QvMapetaBrujulado import QvMapetaBrujulado
from moduls.QvMemoria import QvMemoria
from moduls.QvMenuBar import QvMenuBar
from moduls.QvNews import QvNews
from moduls.QvNouCataleg import QvCreadorCataleg, QvNouCataleg
from moduls.QvNouCatalegCapes import QvNouCatalegCapes
from moduls.QvNouMapa import QvNouMapa
from moduls.QvPavimentacio import DockPavim
from moduls.QvPrint import QvPrint
from moduls.QvPushButton import QvPushButton
from moduls.QvSabiesQue import QvSabiesQue
from moduls.QvSobre import QvSobre
from moduls.QvStatusBar import QvStatusBar
from moduls.QvSuggeriments import QvSuggeriments
from moduls.QvToolButton import QvToolButton
# from moduls.QvMarxesCiutat import MarxesCiutat
from moduls.QvToolTip import QvToolTip
from moduls.QvUbicacions import QvUbicacions
from moduls.QvVisorHTML import QvVisorHTML
from moduls.QvVisualitzacioCapa import QvVisualitzacioCapa

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


# Classe principal QVista
class QVista(QMainWindow, Ui_MainWindow):
    """
    Aquesta és la classe principal del QVista. 

    La finestra te com a widget central un frame sobre el que carreguerem el canvas.
    A més, a la part superior conté una botonera de funcions.

    Des de programa definirem la status bar, sobre la que indicarem escala, projecte i coordenades, 
            així com un tip de les accions que s'executen.
    """
    dicCanvasDw ={}
    dicNumCanvas = {}

    def __init__(self,app, prjInicial, titleFinestra):
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
        # Evita docks tabulados
        self.setDockOptions(QMainWindow.AnimatedDocks)
        self.tempState = self.saveState()

        


        # Definicions globals
        app.setFont(QvConstants.FONTTEXT)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)


        self.actualitzaWindowFlags()

        #Afegim títol a la finestra
        self.setWindowTitle(titleFinestra)

        self.crearMapetaConBotones=None

        # Preparació de projecte i canvas
        self.preparacioEntornGrafic()

        # Preparació del modul de Street View
        self.preparacioStreetView()

        # Inicialitzacions de variables de la classe
        self.canvisPendents=False
        self.titolProjecte = ""
        self.qvPrint = 0
        self.mapesOberts = False
        self.mapaMaxim = False
        self.layerActiu = None
        self.prepararCercador = True
        self.ubicacions= None
        self.cAdrec= None
        self.catalegMapes = None
        self.numCanvasAux = []
        self.sortida = True # para gestioSortida

        #Preparem el mapeta abans de les accions, ja que el necessitarem allà
        self.preparacioMapeta()

        # # Connectors i accions
        self.definicioAccions()

        # Definicio de botons
        self.definicioBotons()
        
        # # Menus i preparació labels statusBar
        self.definirMenus()

        # Preparació botonera, mapeta, llegenda, taula d'atributs, etc.
        self.botoneraLateral()
        self.preparacioTaulaAtributs()
        self.preparacioLlegenda()
        self.preparacioArbreDistrictes()
        # self.preparacioCataleg()
       
        # self.preparacioMapTips() ???
        self.preparacioImpressio()
        self.preparacioMesura()
        # self.preparacioGrafiques() ???
        self.preparacioSeleccio()
        # self.preparacioEntorns()

        # CrearMapeta - Comentado porque hay un error al salir en la 3.16
        # 
        # self.preparacioCrearMapeta()
        
        # Definició dels labels de la statusBar 
        self.definirLabelsStatus()  

        
        # Eina inicial del mapa = Panning
        self.canvas.panCanvas()

        # Preparació d'una marca sobre el mapa. S'utilitzarà per cerca d'adreces i street view
        self.marcaLloc = QgsVertexMarker(self.canvas)
        self.marcaLlocPosada = False

        # Guardem el dashboard actiu per poder activar/desactivar després els dashboards
        # Ara no ho utilitzem, però permetria canviar la disposició dels elements de la app, i retornar-hi
        self.dashboardActiu = [self.canvas, self.frameLlegenda, self.mapeta]

        # Aquestes línies son necesaries per que funcionin bé els widgets de qGis, com ara la fitxa d'atributs
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
                
        # Final del cronometratge d'arrancada
        endGlobal = time.time()
        self.tempsTotal = endGlobal - startGlobal
        print ('Total carrega abans projecte: ', self.tempsTotal)

        # possem el projecte inicial a readonly...
        try:
            pre, _ = os.path.splitext(prjInicial)
            elGpkg= pre + '.gpkg'
            QvFuncions.setReadOnlyFile(elGpkg)
        except:
            print ("No s'ha pogut fer el readonly del geopackage")      

        # Carrega del projecte inicial
        self.obrirProjecte(prjInicial)
        self.canvas.refresh()

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
        self.lblTempsArrencada.setText ("Segons per arrencar: "+str('%.1f'%self.tempsTotal))

        # Drop d'arxius -> Canvas i Llegenda
        # Es permet 1 arxiu de projecte o bé N arxius de capes
        self.dropLlegenda = QvDropFiles(self.llegenda, ['.qgs', '.qgz'], ['.qlr', '.shp', '.csv', '.gpkg'])
        self.dropLlegenda.arxiusPerProcessar.connect(self.obrirArxiu)
        self.dropCanvas = QvDropFiles(self.canvas, ['.qgs', '.qgz'], ['.qlr', '.shp', '.csv', '.gpkg'])
        self.dropCanvas.arxiusPerProcessar.connect(self.obrirArxiu) 

        #Això abans ho feia al ferGran. Però allà no està bé fer-ho. Ho deixo aquí i ja ho mourem
        self.frameLlegenda.hide()
        self.frame_11.hide()

        self.ferGran()

    # Fins aquí teniem la inicialització de la classe. Ara venen les funcions, o métodes, de la classe. 
    def obrirArxiu(self, llista):
        """Obre una llista d'arxius (projectes i capas) passada com a parametre

        Arguments:
            llista {Iterable(str)} -- Noms (amb path) del projecte o capes a obrir
        """
        for nfile in llista:
            _, fext = os.path.splitext(nfile)
            fext = fext.lower()
            if fext in ('.qgs', '.qgz'):
                self.obrirProjecteAmbRang(nfile)
            else:
                self.carregarCapa(nfile)

    def obrirProjecteCataleg(self, projecte, fav, widgetAssociat, volemRang=True):
        """Obre un projecte des del catàleg. Fa el mateix que la funció obrirProjecte, però mostrant el botó de favorits

        Arguments:
            projecte {str} -- Ruta del projecte que volem obrir
            fav {bool} -- True si el projecte està entre els favorits. False si no
            widgetAssociat {QWidget} -- El widget associat al projecte (des del qual l'hem triat al catàleg)

        Keyword Arguments:
            volemRang {bool} -- Indica si volem conservar el rang del projecte actual o no (default: {True})
        """
        #Fem que aparegui el botó de fav
        if volemRang:
            self.obrirProjecteAmbRang(projecte)
        else:
            self.obrirProjecte(projecte)
        self.botoFavorits.show()
        self.mapaCataleg=True
        self.actualitzaBotoFav(fav)
        self.widgetAssociat=widgetAssociat

    def actualitzaBotoFav(self,fav):
        self.favorit=fav
        self.botoFavorits.setIcon(self.iconaFavMarcat if fav else self.iconaFavDesmarcat)

    def obrirRecentAmbRang(self, projecte):
        """Obre un projecte recent passant-li el rang que tingui el projecte actual

        Arguments:
            projecte {str} -- Ruta del projecte que volem obrir
        """
        if self.teCanvisPendents(): #Posar la comprovació del dirty bit
            ret = self.missatgeDesar(titol='Desa el mapa',txtCancelar='Cancel·lar')
            if ret == QMessageBox.AcceptRole:
                b = self.desarProjecte(False)
                if not b: return
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                pass
            elif ret == QMessageBox.DestructiveRole:
                return
        self.obrirProjecteAmbRang(projecte)

    def projecteGpkg(self, file):
        try:
            type = "geopackage"
            projectStorage = QvApp().appQgis.projectStorageRegistry().projectStorageFromType(type)
            projectsList = projectStorage.listProjects(file)
            if projectsList is None or len(projectsList) == 0:
                QMessageBox.warning(self, "Mapa inexistent", f"L'arxiu {type} '{file}' no conté cap mapa definit")
                return None
            if len(projectsList) == 1:
                projectName = projectsList[0]
            else:
                from QvFormMapesGPKG import QvFormMapesGPKG
                projectName = QvFormMapesGPKG.executa(projectsList)
            if projectName is None:
                return None
            else:
                return f"{type}:{file}?projectName={projectName}"
        except Exception as e:
            QMessageBox.warning(self, f"Error al obrir mapa d'arxiu {type}", f"No es pot obrir el mapa de l'arxiu '{file}'")
            print(str(e))
            return None

    def obrirProjecteAmbRang(self, projecte):
        """Obre un projecte passant-li el rang que tingui el projecte actual

        Arguments:
            projecte {str} -- Ruta del projecte que volem obrir
        """
        if Path(projecte).suffix.lower() == '.gpkg':
            projecte = self.projecteGpkg(projecte)
        if projecte is not None:
            self.obrirProjecte(projecte, self.canvas.extent())

    def obrirProjecte(self, projecte, rang = None, nou=False):
        """Obre un projecte passat com a parametre, amb un possible rang predeterminat.
        
        Arguments:
            projecte {String} -- Nom (amb path) del projecte a obrir
        
        Keyword Arguments:
            rang {Rect} -- El rang amb el que s'ha d'obrir el projecte (default: {None})
        """
        self.botoFavorits.hide()
        if hasattr(self,'mapaCataleg'): delattr(self,'mapaCataleg')
        if projecte.strip()=='': return
        # Obrir el projecte i col.locarse en rang
        # Se utiliza la función readProject() de la leyenda
        # para poder borrar adecuadamente las anotaciones
        self.llegenda.readProject(projecte)

        if nou:
            md=self.project.metadata()
            md.setCreationDateTime(QDateTime.currentDateTime())
            self.project.setMetadata(md)

        self.pathProjecteActual = projecte
        if self.project.title().strip()=='':
            self.project.setTitle(Path(projecte).stem)

        self.lblTitolProjecte.setText(self.project.title())
        self.titolProjecte = self.project.title()
        self.setDirtyBit(False)
        self.canvas.refresh()
        # self.showXY(self.canvas.center())

        for x in self.findChildren(QvDockWidget):
            if isinstance(x.widget(),QvCanvas):
                if x.isVisible():
                    x.close()
                x.setParent(None)
        
        if rang is not None and QgsExpressionContextUtils.projectScope(self.project).variable('qV_useProjectExtent') != 'True':
            def posaExtent():
                self.canvas.setExtent(rang)
                try:
                    self.canvas.mapCanvasRefreshed.disconnect()
                except:
                    pass
            posaExtent()
            self.canvas.mapCanvasRefreshed.connect(posaExtent)
            # TODO: Comprobar si funciona. setExtent lanza mapCanvasRefreshed? o es mapCanvasRefreshed 


        # self.bOrientacio.setText('Disponible')

        if self.llegenda.player is None:
            self.llegenda.setPlayer(os.path.join(imatgesDir,'Spinner_2.gif'), 150, 150)
        self.actualitzaMapesRecents(self.pathProjecteActual)

        # Lectura de les metadades del projecte per veure si hi ha un entorn associat
        # Caldria generalitzar-ho i treure-ho d'aquesta funció

        self.carregaEntorns()
        # if entorn == "'MarxesExploratories'":
        #     self.marxesCiutat()

        # Gestió de les metadades
        metadades=Path(self.pathProjecteActual).with_suffix('.htm')

        if os.path.isfile(metadades):
            def obrirMetadades():
                visor=QvVisorHTML(metadades,'Informació del mapa',logo=False,parent=self)
                visor.exec_()
            self.botoMetadades.show()
            self.botoMetadades.disconnect()
            self.botoMetadades.clicked.connect(obrirMetadades)
        else:
            self.botoMetadades.hide()

        carregaMascara(self)

        # if len(self.llegenda.temes())>0:
        #     self.cbEstil.show()
        #     self.cbEstil.clear()
        #     self.cbEstil.addItem('Tema per defecte')
        #     self.cbEstil.addItems(self.llegenda.temes())
        # else:
        #     self.cbEstil.hide()
    
    def startMovie(self):
        QvFuncions.startMovie()
        
    def stopMovie(self):
        QvFuncions.stopMovie()

   

    def keyPressEvent(self, event):
        """Actuacions del qVista en funció de la tecla premuda

        Arguments:
            event {QKeyEvent} -- [description]
        """
        if event.key() == Qt.Key_F1:
            print ('Help')
            
        if event.key() == Qt.Key_F3:
            print('Cercar')
        if event.key() == Qt.Key_F11:
            self.ferGran()
        if event.key() == Qt.Key_F5:
            self.canvas.refresh()
            print('refresh')

                      

    def botoLateral(self, text = None, tamany = 40, imatge = None, accio=None, menu=None):
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
        boto.setMinimumHeight(tamany)
        boto.setMaximumHeight(tamany)
        boto.setMinimumWidth(tamany)
        boto.setMinimumWidth(tamany)
        boto.setDefaultAction(accio)
        boto.setIconSize(QSize(tamany, tamany))
        #Si ens especifica una icona concreta, la posem. Si no, posem la icona de l'acció (si en té)
        if imatge is not None:
            icon = QIcon(imatge)
            boto.setIcon(icon)
        if menu is not None:
            boto.setPopupMode(QToolButton.InstantPopup)           
            boto.setMenu(menu)
        self.lytBotoneraLateral.addWidget(boto)
        return boto

    def botoneraLateral(self):
        """Aquesta funció construeix la botonera lateral. 

        A dins de la funció hi ha la creació de dades per cada botó.

        TODO: Extreure les dades de construcció de la botonera fora. No crític.
        """

        self.lytBotoneraLateral.setAlignment(Qt.AlignTop)
        self.lytBotoneraLateral.setContentsMargins(6,4,4,4)

        self.bUbicacions = self.botoLateral(tamany = 25, accio=self.actAdreces)
        menuFoto=QMenu()
        accioCopia=QAction('Copiar al portaretalls',self)
        accioCopia.setIcon(QIcon(os.path.join(imatgesDir,'content-copy.png')))
        accioCopia.triggered.connect(self.canvas.copyToClipboard)
        menuFoto.addAction(self.actCanvasImg)
        menuFoto.addAction(accioCopia)
        self.bFoto =  self.botoLateral(tamany = 25, accio=self.actCanvasImg, menu=menuFoto)
        self.bFoto.setToolTip('Capturar imatge del mapa')

        self.bImprimir =  self.botoLateral(tamany = 25, accio=self.actImprimir)
        self.bTisores = self.botoLateral(tamany = 25, accio=self.actTisores)
        self.bSeleccioGrafica = self.botoLateral(tamany = 25, accio=self.actSeleccioGrafica)
        self.bMesuraGrafica = self.botoLateral(tamany = 25, accio=self.actMesuraGrafica)
        self.bNouCanvas = self.botoLateral(tamany=25, accio=self.actNouCanvas)

        spacer2 = QSpacerItem(1000, 1000, QSizePolicy.Expanding,QSizePolicy.Maximum)
        self.lytBotoneraLateral.addItem(spacer2)
        
        self.qvNews = QvNews()
        self.bInfo = self.botoLateral(tamany = 25, accio=self.qvNews)
        self.bHelp = self.botoLateral(tamany = 25, accio=self.actHelp)
        self.bBug = self.botoLateral(tamany = 25, accio=self.actBug)
    
    # Funcions de preparació d'entorns 
    def preparacioStreetView(self):
        self.qvSv = self.canvas.getStreetView()
        self.canvas.mostraStreetView.connect(lambda: self.dwSV.show())
        self.dwSV = QvDockWidget( "Street View", self )
        self.dwSV.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwSV.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwSV.setWidget(self.qvSv)
        self.dwSV.setContentsMargins ( 0, 0, 0, 0 )
        self.dwSV.hide()
        self.dwSV.visibilityChanged.connect(self.streetViewTancat)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dwSV)
        self.dwSV.setFloating(True)
        self.dwSV.setDockatInici(False)
        self.dwSV.move(575,175)

    def preparacioEntornGrafic(self):
        """Preparacio entorn grafic del canvas"""

        # llistaBotons = ['streetview','apuntar', 'zoomIn', 'zoomOut', 'panning', 'centrar', 'enrere', 'endavant', 'maximitza']
        llistaBotons = ['apuntar', 'panning', 'centrar', 'zoomIn', 'zoomOut', 'anotacions', 'streetview', 'maximitza']
        
        self.canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True, pare=self)
        self.canvas.canviMaximitza.connect(self.ferGran)
        self.canvas.desMaximitza.connect(self.desmaximitza)

        self.canvas.setCanvasColor(QColor(253,253,255))

        # self.canvas.mapCanvasRefreshed.connect(self.canvasRefrescat)
        self.canvas.extentsChanged.connect(self.eliminaMarcaCercador)
        self.layout = QVBoxLayout(self.frameCentral)
    
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.canvas)
        self.layoutDelsCanvasExtra = QHBoxLayout()
        self.layout.addLayout(self.layoutDelsCanvasExtra)
        
        # Definició de rubberbands i markers
        self.rubberband = QgsRubberBand(self.canvas)
        self.markers = QgsVertexMarker(self.canvas)

        # Instancia del projecte i associació canvas-projecte
        self.project = QgsProject.instance()
        self.root = QgsProject.instance().layerTreeRoot()

        QgsLayerTreeMapCanvasBridge(self.root, self.canvas)
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
        if not hasattr(self, "titolAnterior"):
            self.titolAnterior = self.leTitolProjecte.text()
        self.lblTitolProjecte.show()
        self.leTitolProjecte.hide()
        #TODO: definir el títol anterior
        self.lblTitolProjecte.setText(self.leTitolProjecte.text())
        self.project.setTitle(self.leTitolProjecte.text())
        self.titolProjecte=self.leTitolProjecte.text()
        if self.titolAnterior!=self.leTitolProjecte.text(): 
            self.setDirtyBit()

    def setDirtyBit(self,bit=True):
        #TRUE: Hi ha canvis pendents
        #FALSE: No hi ha canvis pendents
        if bit:
            self.canvisPendents=True
            self.botoDesarProjecte.setIcon(self.iconaAmbCanvisPendents)
        else:
            self.canvisPendents=False
            self.botoDesarProjecte.setIcon(self.iconaSenseCanvisPendents)

    def canvasRefrescat(self):
        return # hem canviat això de lloc
        if self.marcaLlocPosada:
            self.marcaLlocPosada = False
            self.canvas.scene().removeItem(self.marcaLloc)
        else:
            pass
            # try:
            #     self.canvas.scene().removeItem(self.marcaLloc)
            # except Exception as e:
            #     print(e)
    def eliminaMarcaCercador(self):
        if hasattr(self,'marcaLlocPosada') and self.marcaLlocPosada:
            self.marcaLlocPosada = False
            self.canvas.scene().removeItem(self.marcaLloc)

    def preparacioUbicacions(self): #???
        """
        Prepara el widget d'ubicacions, i el coloca en un dock widget, que s'inicialitza en modus hide.
        """
        self.wUbicacions = QvUbicacions(self.canvas)
        self.dwUbicacions = QvDockWidget( "Ubicacions", self )
        self.dwUbicacions.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwUbicacions.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwUbicacions.setWidget( self.wUbicacions)
        self.dwUbicacions.setContentsMargins ( 1, 1, 1, 1 )
        self.dwUbicacions.hide()
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwUbicacions)
    
    def preparacioArbreDistrictes(self):
        """Es genera un dockWidget a la dreta, amb un arbre posicionador Districte-Barri.

        Ho fem instanciant la classe QVDistrictesBarris. 
        També connectem un click al arbre amb la funció clickArbre.
        """

        self.distBarris = QVDistrictesBarris()
        self.distBarris.view.clicked.connect(self.clickArbre)
    
    @QvFuncions.mostraSpinner
    def preparacioCataleg(self):
        """ 
        Genera el catàleg de capes del qVista i l'incorpora a un docWidget.
        
        - Instanciem un widget i l'inicialitcem amb el ui importat. 

        - Li donem titol i el fem visible.

        - Després generem un dockWidget i el posem a la esquerra, invisible.

        - Omplim el widget de les dades llegides a carpetaCataleg
        """

        self.wCataleg=QvCatalegCapes(self)
        self.wCataleg.afegirCapa.connect(lambda x: QvFuncions.afegirQlr(x, self.llegenda))

        # self.wCatalegGran=QvNouCatalegCapes(self)
        # self.wCatalegGran.afegirCapa.connect(lambda x: QvFuncions.afegirQlr(x, self.llegenda))
        

        self.dwCataleg = QvDockWidget( "Catàleg de capes", self )
        self.dwCataleg.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwCataleg.setObjectName( "catalegTaula" )
        self.dwCataleg.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwCataleg.setWidget(self.wCataleg)
        self.dwCataleg.setContentsMargins ( 0,0,0,0 )
        self.dwCataleg.hide()
        self.addDockWidget( Qt.LeftDockWidgetArea, self.dwCataleg)

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
        self.splitter = QSplitter(Qt.Vertical)             
        self.layoutAdreca = QHBoxLayout()                  
        self.layoutCercador = QVBoxLayout(self.fCercador)  
        self.layoutbottom = QVBoxLayout()                  
        #Elementos para layout H, del cercador
        self.lblCercadorCarrer = QLabel('    Carrer:')    
        self.lblCercadorNum = QLabel('Num:')                      
        self.leCarrer=QLineEdit()                           
        self.leCarrer.setToolTip('Introdueix adreça i selecciona de la llista')
        self.leCarrer.setMinimumWidth(200) 
        self.leNumero=QLineEdit()                           
        self.leNumero.setToolTip('Introdueix número, selecciona de la llista i prem RETURN')
        self.leNumero.setMaximumWidth(50)                   
        self.leNumero.setMinimumWidth(50)

        self.boton_bajar= QvPushButton(flat=True)
        self.boton_bajar.clicked.connect(self.CopiarA_Ubicacions)
        self.boton_bajar.setIcon(QIcon(os.path.join(imatgesDir,'down3-512.png')))
        self.boton_bajar.setMinimumHeight(25)
        self.boton_bajar.setMaximumHeight(25)
        self.boton_bajar.setMinimumWidth(25)
        self.boton_bajar.setMaximumWidth(25)
        self.boton_bajar.setToolTip("Copiar aquest carrer i aquest número a l'arbre d'ubicacións")

        #boton invoc_streer
        self.boton_invocarStreetView= QvPushButton(flat=True)
        self.boton_invocarStreetView.clicked.connect(self.invocarStreetView)
        self.boton_invocarStreetView.setIcon(QIcon(os.path.join(imatgesDir,'littleMan.png')))
        self.boton_invocarStreetView.setMinimumHeight(25)
        self.boton_invocarStreetView.setMaximumHeight(25)
        self.boton_invocarStreetView.setMinimumWidth(25)
        self.boton_invocarStreetView.setMaximumWidth(25)
        self.boton_invocarStreetView.setToolTip("Mostrar aquest carrer i aquest número en StreetView")

        self.layoutbottom.addWidget(QHLine())

        self.canviarMapeta = QCheckBox("Canviar mapeta")
        self.canviarMapeta.stateChanged.connect(lambda: self.handleCM())
        self.layoutbottom.addWidget(self.canviarMapeta)
        #self.canviarMapeta.setChecked()

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
          
        self.cAdrec.sHanTrobatCoordenades.connect(self.trobatNumero_oNoLat) 

        # creamos DockWidget
        self.dwCercador = QvDockWidget( "Cercador", self )
        self.dwCercador.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwCercador.hide()
        self.dwCercador.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwCercador.setWidget( self.fCercador)
        self.dwCercador.setContentsMargins ( 2, 2, 2, 2 )
        # a qVista se le añade un DockWidget
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwCercador)

    def handleCM(self):
        if not self.canviarMapeta.isChecked():
            self.enviarMapetaTemporal("Imatges\\capturesMapeta\\Barcelona.png") 

    def CopiarA_Ubicacions(self):       
        if self.cAdrec.NumeroOficial=='0':
            self.cAdrec.NumeroOficial=''

        self.ubicacions.leUbicacions.setText("->"+self.leCarrer.text()+"  "+self.cAdrec.NumeroOficial)
        self.ubicacions._novaUbicacio()

    def invocarStreetView(self):
        try:
            xx=self.cAdrec.coordAdreca[0]
            yy=self.cAdrec.coordAdreca[1]

        except Exception as ee:
            print(str(ee))
            return

        
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
        self.dwTaulaAtributs = QvDockWidget( "Taula de dades", self )
        self.dwTaulaAtributs.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwTaulaAtributs.hide()
        self.dwTaulaAtributs.setObjectName( "taulaAtributs" )
        self.dwTaulaAtributs.setAllowedAreas( Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea )
        self.dwTaulaAtributs.setWidget( self.taulesAtributs)
        self.dwTaulaAtributs.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.BottomDockWidgetArea, self.dwTaulaAtributs)

    def enviarMapetaTemporal(self,fichero):
        self.mapeta.PngPgwDroped_MB([fichero])

    def preparacioMapeta(self):
        self.mapetaDefaultPng= "mapesOffline/default.png"
        self.mapeta  = QvMapetaBrujulado(self.mapetaDefaultPng, self.canvas,  pare=self.canvas, mapeta_default="mapesOffline/default.png")

        self.mapeta.setGraphicsEffect(QvConstants.ombra(self,radius=10,color=QvConstants.COLOROMBRA))

        # CrearMapeta - Comentado porque hay un error al salir en la 3.16
        #
        # self.mapeta.Sig_MuestraMapeta.connect(self.editarOrientacio)

        self.mapeta.setParent(self.canvas)
        self.mapeta.move(20,20)
        self.mapeta.show()
        self.mapetaVisible = True
   
    # CrearMapeta - Comentado porque hay un error al salir en la 3.16
    #
    # def preparacioCrearMapeta(self):
    #     self.crearMapetaConBotones = QvCrearMapetaConBotones(self.canvas)
    #     self.crearMapetaConBotones.setGraphicsEffect(QvConstants.ombra(self,radius=30,color=QvConstants.COLOROMBRA))
    #     self.crearMapetaConBotones.setParent(self.canvas)  #vaya sitio!!!

    #     self.crearMapetaConBotones.Sig_MapetaTemporal.connect(self.enviarMapetaTemporal)

    #     """
    #     Amb aquesta linia:
    #     crearMapeta.show()
    #     es veuria el widget suelto, separat del canvas.
    #     Les següents línies mostren com integrar el widget 'crearMapeta' com a dockWidget.
    #     """
    #     # Creem un dockWdget i definim les característiques
    #     self.dwcrearMapeta = QDockWidget( "CrearMapeta", self )
    #     self.dwcrearMapeta.setContextMenuPolicy(Qt.PreventContextMenu)
    #     self.dwcrearMapeta.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
    #     self.dwcrearMapeta.setContentsMargins ( 1, 1, 1, 1 )
        
    #     # AÑADIMOS  nuestra instancia al dockwidget
    #     self.dwcrearMapeta.setWidget(self.crearMapetaConBotones)

    #     # Coloquem el dockWidget al costat esquerra de la finestra
    #     self.addDockWidget( Qt.LeftDockWidgetArea, self.dwcrearMapeta)

    #     # Fem visible el dockWidget
    #     self.dwcrearMapeta.hide()  #atencion

    def preparacioLlegenda(self):
        """Es genera un dockWidget a la dreta, amb la llegenda del projecte.
 
        Ho fem instanciant la classe QvLlegenda. 

        També connectem un click al arbre amb la funció clickArbre.

        """
        self.layoutFrameLlegenda = QVBoxLayout(self.frameLlegenda)
        self.llegenda = QvLlegenda(self.canvas, self.taulesAtributs)


        # self.dwLlegenda.setFloating(True)
        #r = 250
        #self.llegenda.setMinimumWidth(r) #si es posa un numero a pelo (250), es mostra en finestra petita
        self.llegenda.currentLayerChanged.connect(self.canviLayer)
        self.llegenda.projecteModificat.connect(self.setDirtyBit) #Activa el dirty bit al fer servir el dwPrint (i no hauria)
        self.canvas.setLlegenda(self.llegenda)
        self.layoutFrameLlegenda.setContentsMargins ( 5, 13, 5, 0 )
        self.llegenda.setStyleSheet("QvLlegenda {color: #38474f; background-color: #F9F9F9; border: 0px solid red;}")
        self.layoutFrameLlegenda.addWidget(self.llegenda)
        self.llegenda.accions.afegirAccio("Opcions de visualització", self.actPropietatsLayer)

        self.llegenda.accions.afegirAccio('actTot', self.actFerGran)
        self.llegenda.clicatMenuContexte.connect(self.menuLlegenda)
        self.llegenda.obertaTaulaAtributs.connect(self.dwTaulaAtributs.show)
        if QvApp().testVersioQgis(3, 10):
            self.llegenda.setMenuEdicio(self.menuEdicio)
        
        self.dwLlegenda = QvDockWidget( "Llegenda", self )
        self.dwLlegenda.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwLlegenda.setObjectName( "layers" )
        self.dwLlegenda.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwLlegenda.setContentsMargins ( 0,0,0,0)

        # El 230 de la següent instrucció és empiric, i caldria fer-lo dependre de la'amplada de la llegenda que es carrega.
        self.dwLlegenda.setMinimumWidth(round(230*QvApp().zoomFactor()))
        self.dwLlegenda.setMaximumWidth(9999)
        self.addDockWidget( Qt.LeftDockWidgetArea , self.dwLlegenda )
        self.dwLlegenda.setWidget(self.llegenda)
        self.dwLlegenda.setWindowFlag(Qt.Window)
        self.dwLlegenda.show()

        if self.llegenda.digitize is not None:
            self.addDockWidget( Qt.LeftDockWidgetArea , self.llegenda.digitize.widget )

    def preparacioEntorns(self):             
        self.menuEntorns.setFont(QvConstants.FONTSUBTITOLS)
        self.menuEntorns.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality #???
        for entorn in os.listdir(os.path.dirname('entorns/')):          
            if entorn == '__init__.py' or entorn[-3:] != '.py':
                pass
            else:
                # TODO: canviar el nom pel titol de la clase com a descripcio de l'acció
                nom = entorn[:-3]
                exec('from entorns.{} import {}'.format(nom,nom))
                exec('self.act{} = QAction("{}", self)'.format(nom, nom))
                exec('self.act{}.setStatusTip("{}")'.format(nom, nom))   
                exec('self.act{}.triggered.connect(self.prepararDash({}))'.format(nom, nom))
                exec('self.menuEntorns.addAction(self.act{})'.format(nom))
        
        # self.menuEntorns.addAction(self.actPavimentacio)
        # self.menuEntorns.addAction(self.actMarxesCiutat)
    
    def streetViewTancat(self):
        if self.dwSV.isHidden():
            self.canvas.panCanvas()
            self.canvas.scene().removeItem(self.qvSv.m)

    def trobatNumero_oNo(self,rsc,info_rsc,cercador):
        if rsc==0:
            self.canvas.setCenter(cercador.coordAdreca)
            self.canvas.zoomScale(1000)
            self.canvas.scene().removeItem(self.marcaLloc)

            self.marcaLloc = QgsVertexMarker(self.canvas)
            self.marcaLloc.setCenter( cercador.coordAdreca )
            self.marcaLloc.setColor(QColor(255, 0, 0))
            self.marcaLloc.setIconSize(15)
            self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            self.marcaLloc.setPenWidth(3)
            self.marcaLloc.show()
            self.marcaLlocPosada = True
    
    def trobatNumero_oNoLat(self, rsc,info_rsc):
        self.trobatNumero_oNo(rsc,info_rsc,self.cAdrec)

    def trobatNumero_oNoSup(self,rsc,info_rsc):
        self.trobatNumero_oNo(rsc,info_rsc,self.cAdrecSup)

    def adreces(self):
        if self.prepararCercador:
            self.preparacioCercadorPostal()
            self.prepararCercador = False
        self.dwCercador.show()

    def menuLlegenda(self, tipus):                                 
        #   (Tipos: none, group, layer, symb)
        if tipus == 'layer':
            self.llegenda.menuAccions.append('separator')
            self.llegenda.menuAccions.append("Opcions de visualització")

    def preparacioMapTips(self):
        layer = self.llegenda.currentLayer()
        self.my_tool_tip = QvToolTip(self.canvas,layer)
        self.my_tool_tip.createMapTips()

    def preparacioImpressio(self):  
        estatDirtybit = self.canvisPendents
        self.dwPrint = QvDockWidget( "Imprimir a PDF", self )
        self.dwPrint.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwPrint.setObjectName( "Print" )
        self.dwPrint.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        self.dwPrint.setContentsMargins ( 1, 1, 1, 1 )
        self.addDockWidget(Qt.RightDockWidgetArea, self.dwPrint)
        # self.dwPrint.setMaximumHeight(200)
        self.dwPrint.hide()
        self.setDirtyBit(estatDirtybit)

    def imprimir(self):
        estatDirtybit = self.canvisPendents
        # No és tant fàcil fer que només es creï un cop aquest objecte (i que funcioni bé després)
        self.qvPrint = QvPrint(self.project, self.canvas, self.canvas.extent(), parent = self)
        self.dwPrint.setWidget(self.qvPrint)
        self.qvPrint.leTitol.setText(self.titolProjecte) #el titol pot haver canviat (o el projecte)
        self.dwPrint.show()
        self.qvPrint.pucMoure = True #Mala idea modificar atributs des d'aquí

        def destruirQvPrint(x):
            if x: return
            self.qvPrint.oculta()

        self.dwPrint.visibilityChanged.connect(destruirQvPrint)
        self.setDirtyBit(estatDirtybit)
    def sobre(self):
        about = QvSobre(self)
        about.exec()

    def definicioAccions(self):
        """ Definició de les accions que després seran assignades a menús o botons. """
        self.actObrirProjecte = QAction("Obrir...", self)
        self.actObrirProjecte.setShortcut("Ctrl+O")
        self.actObrirProjecte.setStatusTip("Obrir mapa QGis")
        self.actObrirProjecte.triggered.connect(self.obrirDialegProjecte)
        
        self.actdesarProjecte = QAction("Desar", self)
        self.actdesarProjecte.setShortcut("Ctrl+S")
        self.actdesarProjecte.setStatusTip("Guardar Mapa")
        self.actdesarProjecte.triggered.connect(self.desarProjecte)

        self.actGuardarComAProjecte=QAction('Anomena i desa...', self)
        self.actGuardarComAProjecte.setStatusTip("Desar una còpia del mapa actual")
        self.actGuardarComAProjecte.triggered.connect(self.dialegDesarComA)

        self.actNouMapa = QAction("Nou", self)
        self.actNouMapa.setStatusTip("Nou Mapa")
        self.actNouMapa.setShortcut('Ctrl+N')
        self.actNouMapa.triggered.connect(self.nouMapa)

        self.actcartoBCN = QAction("CartoBCN", self)
        #iconaChrome=QIcon(os.path.join(imatgesDir,'calc.png')) #es poden posar icones
        #self.actcartoBCN.setIcon(iconaChrome)
        self.actcartoBCN.triggered.connect(cartoBCN)

        self.actgeoportalBCN = QAction("Geoportal BCN", self)
        self.actgeoportalBCN.triggered.connect(geoportalBCN)

        self.actopendataBCN = QAction("Open Data BCN", self)
        self.actopendataBCN.triggered.connect(opendataBCN)

        self.actbcnPIC = QAction("BCN PIC", self)
        self.actbcnPIC.triggered.connect(bcnPIC)

        self.actplanolBCN = QAction("Plànol BCN", self)
        self.actplanolBCN.triggered.connect(planolBCN)

        self.actpiuPortal = QAction("Portal PIU info. urb.", self)
        self.actpiuPortal.triggered.connect(piuPortal)

        self.actSobre = QAction('Quant a...', self)
        self.actSobre.triggered.connect(self.sobre)
        
        self.actDocumentacio=QAction('Documentació',self)
        self.actDocumentacio.setIcon(QIcon(os.path.join(imatgesDir,'file-document.png')))
        self.actDocumentacio.triggered.connect(self.obreDocumentacio)
        
        self.actImprimir = QAction("Imprimir", self)
        self.actImprimir.setStatusTip("Imprimir a PDF")
        icon=QIcon(os.path.join(imatgesDir,'printer.png'))
        self.actImprimir.setIcon(icon)
        self.actImprimir.triggered.connect(self.imprimir)

        self.actAfegirNivellSHP = QAction("Afegir capa SHP", self)
        self.actAfegirNivellSHP.setStatusTip("Afegir capa SHP")
        self.actAfegirNivellSHP.triggered.connect(lambda x: QvFuncions.afegirNivellSHP(self.project))

        self.actAfegirCapa = QAction("Afegir capa QGIS (qlr)", self)
        self.actAfegirCapa.setStatusTip("Afegir capa")
        self.actAfegirCapa.triggered.connect(self.obrirDialegNovaCapaQLR)

        self.actCrearCapa1 = QAction("Crear capa des d'arxiu GIS", self)
        self.actCrearCapa1.setStatusTip("Crea una capa des d'un geopackage o un shapefile")
        self.actCrearCapa1.triggered.connect(self.obrirDialegNovaCapaGIS)

        self.actCrearCapa2 = QAction("Crear capa des d'arxiu CSV", self)
        self.actCrearCapa2.setStatusTip("Crea una capa des d'un arxiu csv amb adreces o coordenades")
        self.actCrearCapa2.triggered.connect(self.obrirDialegNovaCapaCSV)

        self.actTisores = QAction("Eina per retallar pantalla", self)
        self.actTisores.setStatusTip("Eina per retallar pantalla")
        icon=QIcon(os.path.join(imatgesDir,'tisores.png'))
        self.actTisores.setIcon(icon)
        self.actTisores.triggered.connect(self.tisores)

        self.actSeleccioGrafica = QAction("Seleccionar/emmascarar", self)
        self.actSeleccioGrafica.setStatusTip("Seleccionar/emmascarar")
        icon=QIcon(os.path.join(imatgesDir,'select.png'))
        self.actSeleccioGrafica.setIcon(icon)
        self.actSeleccioGrafica.triggered.connect(self.seleccioGrafica)

        #Eina de mesura -nexus-
        self.actMesuraGrafica = QAction("Mesurar", self)
        self.actMesuraGrafica.setStatusTip("Mesurar")
        icon=QIcon(os.path.join(imatgesDir,'regle.png'))
        self.actMesuraGrafica.setIcon(icon)
        self.actMesuraGrafica.triggered.connect(self.mesuraGrafica)

        self.actNouCanvas = QAction("Nou canvas", self)
        self.actNouCanvas.setStatusTip('Afegir un nou canvas')
        icon=QIcon(os.path.join(imatgesDir,'map-plus.png'))
        self.actNouCanvas.setIcon(icon)
        self.actNouCanvas.triggered.connect(self.nouCanvas)

        self.actHelp = QAction("Contingut de l'ajuda", self)
        icon=QIcon(os.path.join(imatgesDir,'help-circle.png'))
        self.actHelp.setIcon(icon)
        self.actHelp.triggered.connect(self.infoQVistaPDF)
        self.actHelp.setShortcut('Ctrl+H')

        #bEnviar.clicked.connect(lambda: reportarProblema(leTitol.text(), leDescripcio.text()))
        self.suggeriments=QvSuggeriments(QvFuncions.reportarProblema,self)
        self.actBug = QAction("Problemes i suggeriments ", self)
        icon=QIcon(os.path.join(imatgesDir,'bug.png'))
        self.actBug.setIcon(icon)
        self.actBug.triggered.connect(self.suggeriments.show)

        self.actObrirCataleg = QAction("Catàleg", self)
        self.actObrirCataleg.setStatusTip("Catàleg d'Informació Territorial")
        #self.actObrirCataleg.setIcon(QIcon(os.path.join(imatgesDir,'layers_2.png')))
        self.actObrirCataleg.triggered.connect(self.obrirCataleg)

        self.actObrirCatalegLateral = QAction("Catàleg lateral", self)
        self.actObrirCatalegLateral.setStatusTip("Catàleg d'Informació Territorial")
        #self.actObrirCataleg.setIcon(QIcon(os.path.join(imatgesDir,'layers_2.png')))
        self.actObrirCatalegLateral.triggered.connect(self.obrirCatalegLateral)

        self.actCreadorCataleg = QAction('Afegir al catàleg')
        self.actCreadorCataleg.setStatusTip('Afegir entrada al catàleg de capes')
        self.actCreadorCataleg.triggered.connect(self.afegirCatalegCapes)
        
        self.actFerGran = QAction("Ampliar àrea de treball", self)
        self.actFerGran.setIcon(QIcon(os.path.join(imatgesDir,'arrow-expand.png')))
        self.actFerGran.setStatusTip("Ampliar àrea de treball")
        self.actFerGran.triggered.connect(self.ferGran)

        self.actCanvasImg = QAction("Desar com a PNG", self)
        self.actCanvasImg.setIcon(QIcon(os.path.join(imatgesDir,'camera.png')))
        self.actCanvasImg.setStatusTip("Imatge del canvas")
        self.actCanvasImg.triggered.connect(self.canvasImg)

        self.actCataleg = QAction("Catàleg", self)
        self.actCataleg.setStatusTip("Catàleg")

        #@QvFuncions.ignoraArgs
        @QvFuncions.mostraSpinner
        @QvFuncions.cronometraDebug
        def activaCataleg():
            if self.catalegMapes is None:
                # self.startMovie()
                self.catalegMapes = QvNouCataleg(self)
                self.catalegMapes.obrirProjecte.connect(self.obrirProjecteCataleg)
                # self.stopMovie()
            if not self.catalegMapes.isVisible():
                self.catalegMapes.showMaximized()
            self.catalegMapes.activateWindow()

        self.actCataleg.triggered.connect(lambda _: activaCataleg())

        self.actAfegirCataleg = QAction('Afegir al catàleg',self)
        self.actAfegirCataleg.setStatusTip('Afegir el mapa actual al catàleg')
        def afegirCataleg():
            wid=QvCreadorCataleg(self.canvas, self.project, self.catalegMapes, self)
            wid.show()
        self.actAfegirCataleg.triggered.connect(afegirCataleg)

        self.actAdreces = QAction("Cercar per adreça", self)
        self.actAdreces.setIcon(QIcon(os.path.join(imatgesDir,'map-search.png')))
        self.actAdreces.setStatusTip("Adreces")
        self.actAdreces.triggered.connect(self.adreces)

        self.actPavimentacio = QAction("Pavimentació", self)
        self.actPavimentacio.setStatusTip("Pavimentació")
        self.actPavimentacio.triggered.connect(self.pavimentacio)

        # self.actMarxesCiutat = QAction("Marxes de Ciutat", self)
        # self.actMarxesCiutat.setStatusTip("Marxes de Ciutat")
        # self.actMarxesCiutat.triggered.connect(self.marxesCiutat)

        self.actPropietatsLayer = QAction("Opcions de visualització", self)
        self.actPropietatsLayer.setStatusTip("Opcions de visualització")
        self.actPropietatsLayer.triggered.connect(self.propietatsLayer)

    def definicioBotons(self):
        self.frame_15.setContentsMargins(0,0,12,0)
        stylesheetLineEdits="""
            background-color:%s;
            color: %s;
            border: 1px solid %s;
            border-radius: 2px;
            padding: 1px"""%(QvConstants.COLORCERCADORHTML, QvConstants.COLORFOSCHTML, QvConstants.COLORCERCADORHTML)
        
        self.leCercaPerAdreca.setStyleSheet(stylesheetLineEdits)
        self.leCercaPerAdreca.setFont(QvConstants.FONTTEXT)
        self.leCercaPerAdreca.setPlaceholderText('Carrer, plaça...')
        self.leCercaPerAdreca.setFixedWidth(320)

        self.leNumCerca.setStyleSheet(stylesheetLineEdits)
        self.leNumCerca.setFont(QvConstants.FONTTEXT)
        self.leNumCerca.setPlaceholderText('Núm...')
        self.leNumCerca.setFixedWidth(80)

        self.cAdrecSup=QCercadorAdreca(self.leCercaPerAdreca, self.leNumCerca,'SQLITE')    # SQLITE o CSV
        self.bCercaPerAdreca.clicked.connect(lambda: self.leCercaPerAdreca.setText(''))
        self.bCercaPerAdreca.clicked.connect(self.leCercaPerAdreca.setFocus)
        self.bCercaPerAdreca.setCursor(QvConstants.cursorClick())
        self.leCercaPerAdreca.textChanged.connect(lambda x: self.bCercaPerAdreca.setIcon(QIcon(os.path.join(imatgesDir,('magnify.png' if x=='' else 'cp_elimina.png')))))
        self.cAdrecSup.sHanTrobatCoordenades.connect(self.trobatNumero_oNoSup)

        self.lSpacer.setText("")
        self.lSpacer.setFixedWidth(24)

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
        self.botoVeureLlegenda.setIcon(QIcon(os.path.join(imatgesDir,'map-legend.png')))
        self.botoVeureLlegenda.setStyleSheet(stylesheetBotons)
        self.botoVeureLlegenda.setIconSize(QSize(24, 24))
        self.botoVeureLlegenda.clicked.connect(self.obrirLlegenda)
        self.botoVeureLlegenda.setCursor(QvConstants.cursorClick())

        self.iconaSenseCanvisPendents = QIcon(os.path.join(imatgesDir,'content-save.png'))
        self.iconaAmbCanvisPendents = QIcon(os.path.join(imatgesDir,'content-save_orange.png'))
        self.botoDesarProjecte.setIcon(self.iconaSenseCanvisPendents)
        self.botoDesarProjecte.setStyleSheet(stylesheetBotons)
        self.botoDesarProjecte.setIconSize(QSize(24, 24))
        self.botoDesarProjecte.clicked.connect(self.desarProjecte) 
        self.botoDesarProjecte.setCursor(QvConstants.cursorClick())

        self.botoObrirQGis.setIcon(QIcon(os.path.join(imatgesDir,'qgis-3.png')))
        self.botoObrirQGis.setStyleSheet(stylesheetBotons)
        self.botoObrirQGis.setIconSize(QSize(24, 24))
        self.botoObrirQGis.clicked.connect(self.obrirEnQgis)
        self.botoObrirQGis.setCursor(QvConstants.cursorClick())

        self.botoMapeta.setIcon(QIcon(os.path.join(imatgesDir,'Mapeta.png')))
        self.botoMapeta.setStyleSheet(stylesheetBotons)
        self.botoMapeta.setIconSize(QSize(24,24))
        self.botoMapeta.clicked.connect(self.VerOcultarMapeta)
        self.botoMapeta.setCursor(QvConstants.cursorClick())

        self.botoMon.setIcon(QIcon(os.path.join(imatgesDir,'earth.png')))
        self.botoMon.setStyleSheet(stylesheetBotons)
        self.botoMon.setIconSize(QSize(24,24))
        self.botoMon.clicked.connect(self.fonsMapa)
        self.botoMon.setCursor(QvConstants.cursorClick())
        self.fonsVisible = False

        self.botoMostraEntorn.setIcon(QIcon(os.path.join(imatgesDir,'entorn.png')))
        self.botoMostraEntorn.setStyleSheet(stylesheetBotons)
        self.botoMostraEntorn.setIconSize(QSize(24,24))
        self.botoMostraEntorn.clicked.connect(lambda: self.dwEntorn.hide() if self.dwEntorn.isVisible() else self.dwEntorn.show())
        self.botoMostraEntorn.setCursor(QvConstants.cursorClick())
        self.botoMostraEntorn.hide()

        self.botoMetadades.setIcon(QIcon(os.path.join(imatgesDir,'information-variant.png')))
        self.botoMetadades.setStyleSheet(stylesheetBotons)
        self.botoMetadades.setIconSize(QSize(24,24))
        self.botoMetadades.setCursor(QvConstants.cursorClick())

        self.bCercaPerAdreca.setIcon(QIcon(os.path.join(imatgesDir,'magnify.png')))
        self.bCercaPerAdreca.setIconSize(QSize(24, 24))
        self.bCercaPerAdreca.setStyleSheet("background-color:%s; border: 0px; margin: 0px; padding: 0px;" %QvConstants.COLORCLARHTML)

        self.iconaFavDesmarcat=QIcon(os.path.join(imatgesDir,'qv_bookmark_off.png'))
        self.iconaFavMarcat=QIcon(os.path.join(imatgesDir,'qv_bookmark_on.png'))
        self.botoFavorits.setIcon(self.iconaFavDesmarcat)
        self.botoFavorits.setStyleSheet(stylesheetBotons)
        self.botoFavorits.setIconSize(QSize(24,24))
        self.botoFavorits.setCursor(QvConstants.cursorClick())
        self.botoFavorits.clicked.connect(self.switchFavorit)

        self.botoReload.setIcon(QIcon(os.path.join(imatgesDir,'reload.png')))
        self.botoReload.setStyleSheet(stylesheetBotons)
        self.botoReload.setIconSize(QSize(24,24))
        self.botoReload.setCursor(QvConstants.cursorClick())
        self.botoReload.clicked.connect(self.reload)
        
    def preparacioSeleccio(self):
        self.wSeleccioGrafica = QvSeleccioGrafica(self.canvas, self.project, self.llegenda)

        self.dwSeleccioGrafica = QvDockWidget("Selecció gràfica", self)
        self.dwSeleccioGrafica.setContextMenuPolicy(Qt.PreventContextMenu)
        self.dwSeleccioGrafica.hide()
        self.dwSeleccioGrafica.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwSeleccioGrafica.setWidget( self.wSeleccioGrafica)
        self.dwSeleccioGrafica.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwSeleccioGrafica )
        self.dwSeleccioGrafica.hide()
        self.dwSeleccioGrafica.visibilityChanged.connect(self.foraEines)

    #Eina de mesura sobre el mapa -nexus-foraEinaSeleccio
    def preparacioMesura(self):
        self.wMesuraGrafica = QvMesuraGrafica(self.canvas, self.llegenda, self.bMesuraGrafica)
        
        self.dwMesuraGrafica = QDockWidget("Medició de distàncies i àrees", self)
        self.dwMesuraGrafica.hide()
        self.dwMesuraGrafica.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.dwMesuraGrafica.setWidget( self.wMesuraGrafica)
        self.dwMesuraGrafica.setContentsMargins ( 2, 2, 2, 2 )
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwMesuraGrafica )
        self.dwMesuraGrafica.setFloating(True)
        self.wMesuraGrafica.acabatMesurar.connect(self.dwMesuraGrafica.hide)
        self.dwMesuraGrafica.resize(400,150)
        
        self.dwMesuraGrafica.hide()
        self.dwMesuraGrafica.visibilityChanged.connect(self.wMesuraGrafica.canviaVisibilitatDw)

    def calcularSeleccio(self):
        self.wSeleccioGrafica.calcularSeleccio()

    def canviLayer(self):
        self.preparacioMapTips()
        self.layerActiu = self.llegenda.currentLayer()        
        self.wSeleccioGrafica.lwFieldsSelect.clear()
        # self.esborrarSeleccio(True)
        self.esborrarMesures(True)
        
        if self.layerActiu is not None:
            self.wSeleccioGrafica.setInfoLbl("Capa activa: "+ self.layerActiu.name())
            if self.layerActiu.type() == QgsMapLayer.VectorLayer:
                self.wSeleccioGrafica.calculaFields(self.layerActiu)
                self.wSeleccioGrafica.canviLayer()
            else:
                self.wSeleccioGrafica.setInfoLbl("Capa activa sense dades.")
        else:
            self.wSeleccioGrafica.setInfoLbl("No hi ha capa activa.")

    def seleccioGrafica(self):
        self.dwSeleccioGrafica.show()
        self.canviLayer()

    def mesuraGrafica(self):
        self.dwMesuraGrafica.show()
        pos=self.bMesuraGrafica.mapToGlobal(self.bMesuraGrafica.pos())
        self.dwMesuraGrafica.move(pos.x()-400,pos.y())
        self.canviLayer()
    
    def nouCanvas(self):        
        canvas = QvCanvasAuxiliar(self.canvas, temaInicial=self.llegenda.tema.buscaTema(), botoneraHoritzontal=True,posicioBotonera='SE')
        canvas.Sig_canviTema.connect(self.actualizarTitleCanvasAux)
        root = QgsProject.instance().layerTreeRoot()

        canvas.bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        crs = self.canvas.mapSettings().destinationCrs()
        canvas.setDestinationCrs(crs)

        canvas.setRotation(self.canvas.rotation())
        num = self.numCanvasAux[-1]+1 if len(self.numCanvasAux)>0 else 1
        dwCanvas = QvDockWidget(f'Vista auxiliar del mapa ({num})')

        dwCanvas.resize(self.canvas.width()/2.5,self.canvas.height()/2.5)   #JNB

        dwCanvas.tancat.connect(lambda: self.numCanvasAux.remove(num))
        dwCanvas.tancat.connect(lambda: self.actualizoDiccionarios(num))
        
        self.numCanvasAux.append(num)
        dwCanvas.setWidget(canvas)

        # Guardo el titulo creado para poder añadirle el tema
        tituloCurrent = dwCanvas.windowTitle() 
        aConservar = tituloCurrent[0 :tituloCurrent.find(')')+1] 
        nuevoTitulo = aConservar + " Tema: " + canvas.currentTeme
        dwCanvas.setWindowTitle(nuevoTitulo)
        # Añado a diccionario, el id del canvas y de su dw
        self.dicCanvasDw.setdefault(str(id(canvas)),str(id(dwCanvas)))
        # Añado a diccionario, el num de vista y el id del canvas 
        self.dicNumCanvas.setdefault(num,str(id(canvas)))

        self.addDockWidget(Qt.RightDockWidgetArea, dwCanvas)
        dwCanvas.setFloating(True)


    def actualizoDiccionarios(self,num):
        print("borro: ",num)
        canvas = self.dicNumCanvas.get(num)
        del self.dicNumCanvas[num]
        del self.dicCanvasDw[canvas]


    def actualizarTitleCanvasAux(self,idenCanvas,tema):
        try:
            suDw = int(self.dicCanvasDw.get(idenCanvas))
            import _ctypes
            tituloCurrent = _ctypes.PyObj_FromPtr(suDw).windowTitle() 
            
            aConservar = tituloCurrent[0 :tituloCurrent.find(')')+1] 
            nuevoTitulo = aConservar + " Tema " + tema
            _ctypes.PyObj_FromPtr(suDw).setWindowTitle(nuevoTitulo)        
            
        except Exception as ee:
            pass
        

    def reload(self):
        #comprovar si hi ha canvis
        if self.teCanvisPendents(): #Posar la comprovació del dirty bit
            ret = self.missatgeDesar(titol='Recàrrega del mapa',txtCancelar='Cancel·lar')
            if ret == QMessageBox.AcceptRole:
                b = self.desarProjecte()
                if not b: return
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                pass
            elif ret == QMessageBox.DestructiveRole:
                return
        if hasattr(self,'mapaCataleg'):
            self.obrirProjecteCataleg(self.pathProjecteActual,self.favorit,self.widgetAssociat)
        else:
            senseCanvis = False
            if self.teCanvisPendents(): #Posar la comprovació del dirty bit
                ret = self.missatgeDesar(titol='Recàrrega del mapa',txtCancelar='Cancel·lar')
                if ret == QMessageBox.AcceptRole:
                    b = self.desarProjecte()
                    if b:
                        self.obrirProjecte(self.pathProjecteActual) 
                    else:
                        return
                elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                    pass
                elif ret == QMessageBox.DestructiveRole:
                    return
            else:
                senseCanvis = True
            if hasattr(self,'mapaCataleg'):
                self.obrirProjecteCataleg(self.pathProjecteActual,self.favorit,self.widgetAssociat)
                pass
            else:
                self.obrirProjecteAmbRang(self.pathProjecteActual)
            if senseCanvis:
                self.setDirtyBit(False)


    def switchFavorit(self):
        if self.favorit:
            self.botoFavorits.setIcon(self.iconaFavDesmarcat)
        else:
            self.botoFavorits.setIcon(self.iconaFavMarcat)
        self.favorit=not self.favorit
        self.widgetAssociat.setFavorit(self.favorit)

    def helpQVista(self): #Ara no es fa servir, però en el futur es pot utilitzar per saber què és un element
        QWhatsThis.enterWhatsThisMode()
    
    @staticmethod
    def infoQVistaPDF():
        ''' Obre un pdf amb informació de qVista, utilitzant l'aplicació per defecte del sistema '''
        try:
            os.startfile(arxiuInfoQVista)
        except:
            msg=QMessageBox()
            msg.setText("No s'ha pogut accedir a l'arxiu de help      ")
            msg.setWindowTitle('qVista')
            msg.exec_()

    def activarDashboard(self,nom): #???
        for objecte in self.dashboardActiu:
            objecte.hide() 
        dashboard = nom(self)
        self.dashboardActiu = [dashboard]
        self.layout.addWidget(dashboard)

    def obrirEnQgis(self):
        path = os.path.join(QvTempdir,'tempQgis.qgs')
        self.project.write(path)
        QDesktopServices().openUrl(QUrl(path))

    def VerOcultarMapeta(self):
        if self.mapeta.isHidden():
            self.mapeta.show()
        else:
            self.mapeta.hide()

    def fonsMapa(self):
        if not self.fonsVisible:
            urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
            self.rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')  
            self.project.addMapLayer(self.rlayer)
            self.fonsVisible = True
        else:
            self.project.removeMapLayer(self.project.mapLayersByName('OpenStreetMap')[0].id())
            self.canvas.refresh()
            self.fonsVisible = False

    def tisores(self):
        process = QProcess(self)
        pathApp = r"c:\windows\system32\SnippingTool.exe"
        process.start(pathApp)
        qApp.processEvents()

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
        
        imatge = QPixmap(os.path.join(imatgesDir,'qVistaLogo_text_40.png'))
        p = QPainter(imatge) 
        p.setPen(QPen(Qt.white))
        p.setFont(QFont("Arial", 12, QFont.Medium))
        p.drawText(106,26, versio)
        p.end()

        lblLogoQVista.setPixmap(imatge)
        lblLogoQVista.setScaledContents(False)

        menubar=QvMenuBar(self)
        self.setMenuBar(menubar)
        self.bar = self.menuBar()
        
        def desplaca(x,y):
            if self.maximitzada:
                self.restaurarFunc()
            self.move(round(self.x()+x-self.oldPos.x()), round(self.y()+y-self.oldPos.y()))
        
        def posCanviada(p):
            self.oldPos=p
        self.bar.desplaca.connect(desplaca)
        self.bar.posCanviada.connect(posCanviada)
        self.bar.restaura.connect(self.restaurarFunc)
        self.bar.setFont(QvConstants.FONTTITOLS)
        self.bar.setCornerWidget(lblLogoQVista,Qt.TopLeftCorner)
        
        QvConstants.afegeixOmbraHeader(self.bar)

        self.bar.setMinimumHeight(40)
        self.fMaxim = QFrame()
        self.lytBotonsFinestra = QHBoxLayout(self.fMaxim)
        self.fMaxim.setLayout(self.lytBotonsFinestra)
        self.lytBotonsFinestra.setContentsMargins(0,0,0,0)

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
        self.botoMinimitzar.setIcon(QIcon(os.path.join(imatgesDir,'window-minimize.png')))
        self.botoMinimitzar.setFixedSize(40,40)
        self.botoMinimitzar.clicked.connect(self.showMinimized)
        self.botoMinimitzar.setStyleSheet(stylesheetBotonsFinestra)
        self.lytBotonsFinestra.addWidget(self.botoMinimitzar)

        self.maximitzada=True
        self.iconaRestaurar1=QIcon(os.path.join(imatgesDir,'window-restore.png'))
        self.iconaRestaurar2=QIcon(os.path.join(imatgesDir,'window-maximize.png'))

        self.botoRestaurar=QvPushButton(flat=True)
        self.botoRestaurar.setIcon(self.iconaRestaurar1)
        self.botoRestaurar.clicked.connect(self.restaurarFunc)
        self.botoRestaurar.setFixedSize(40,40)
        self.botoRestaurar.setStyleSheet(stylesheetBotonsFinestra)
        self.lytBotonsFinestra.addWidget(self.botoRestaurar)

        self.botoSortir=QvPushButton(flat=True)
        self.botoSortir.setIcon(QIcon(os.path.join(imatgesDir,'window_close.png')))
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
                self.showLblFlotant('Benvingut al mode "qVista Màxima Rellevància". '
                'En aquest mode els botons per tancar, minimitzar i fer petita la finestra deixen de funcionar, '
                'ja que qVista passa a ser el programa més important de l\'ordinador.')

        self.shortcutNoEsPotSortir=QShortcut(QKeySequence('Ctrl+Shift+Alt+Ç'),self)
        self.shortcutNoEsPotSortir.activated.connect(ocultaBotons)
        self.bar.setCornerWidget(self.fMaxim, Qt.TopRightCorner)
        self.bar.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality #???

        self.menuMapes = self.bar.addMenu ("Mapes")
        self.menuCapes = self.bar.addMenu ("Capes")

        if QvApp().testVersioQgis(3, 10):
            self.menuEdicio = self.bar.addMenu('Edició')
            self.menuEdicio.setFont(QvConstants.FONTSUBTITOLS)
            self.menuEdicio.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality

        self.menuUtilitats = self.bar.addMenu("Utilitats")
        self.menuEines = self.bar.addMenu('Eines')
        self.menuAjuda = self.bar.addMenu('Ajuda')

        self.menuMapes.setFont(QvConstants.FONTSUBTITOLS)
        self.menuMapes.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality #???
        self.menuMapes.addAction(self.actCataleg)
        self.menuMapes.addAction(self.actAfegirCataleg)
        self.menuMapes.addSeparator()
        self.menuMapes.addAction(self.actNouMapa)
        self.menuMapes.addAction(self.actObrirProjecte)
        self.menuMapes.addAction(self.actdesarProjecte)
        self.menuMapes.addAction(self.actGuardarComAProjecte)
        #Aquí originalment creàvem el menú de Mapes recents
        #No obstant, com que a actualitzaMapesRecents es crea de nou, no cal crear-lo aquí
        self.menuRecents=QMenu('Mapes recents',self.menuMapes)
        self.actualitzaMapesRecents(None)
        self.menuMapes.addMenu(self.menuRecents)

        self.menuCapes.setFont(QvConstants.FONTSUBTITOLS)
        self.menuCapes.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality #???
        self.menuCapes.addAction(self.actObrirCataleg)
        self.menuCapes.addAction(self.actObrirCatalegLateral)
        self.menuCapes.addAction(self.actCreadorCataleg)
        self.menuCapes.addSeparator()
        self.menuCapes.addAction(self.actAfegirCapa)
        self.menuCapes.addAction(self.actCrearCapa1)
        self.menuCapes.addAction(self.actCrearCapa2)
        
        self.menuUtilitats.setFont(QvConstants.FONTSUBTITOLS)
        self.menuUtilitats.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        self.menuUtilitats.addAction(self.actcartoBCN)
        self.menuUtilitats.addAction(self.actgeoportalBCN)
        self.menuUtilitats.addAction(self.actopendataBCN)
        self.menuUtilitats.addAction(self.actbcnPIC)
        self.menuUtilitats.addAction(self.actplanolBCN)
        self.menuUtilitats.addSeparator()
        self.menuUtilitats.addAction(self.actpiuPortal)
        # self.menuUtilitats.addAction(self.actDocumentacio)

        self.menuEines.setFont(QvConstants.FONTSUBTITOLS)
        self.menuUtilitats.styleStrategy = QFont.PreferAntialias or QFont.PreferQuality
        self.carregaEines()

        self.menuAjuda.setFont(QvConstants.FONTSUBTITOLS)
        self.menuAjuda.addAction(self.actHelp)
        self.menuAjuda.addAction(self.actBug)
        self.menuAjuda.addSeparator()
        self.menuAjuda.addAction(self.actSobre)

    def carregaEines(self):
        eines = filter(lambda x: x.endswith('py'), os.listdir('moduls/eines'))
        self.accionsEines = []
        for x in eines:
            nom = Path(x).stem
            try:
                eina = importlib.import_module(f'moduls.eines.{nom}')
                classe = getattr(eina,nom)
                if hasattr(classe,'esEinaGlobal') and classe.esEinaGlobal:
                    titol = classe.titol if hasattr(classe,'titol') else classe.__name__
                    act = QAction(titol)
                    act.triggered.connect(functools.partial(self.obreEina,classe))
                    self.menuEines.addAction(act)
                    self.accionsEines.append(act)
            except Exception as e:
                print(e)
    def carregaEntorns(self):
        def llistaDesDeStr(s):
            s = s.replace('[','').replace(']','').split(',')
            s = [x.strip() for x in s]
            return s
        def obteTitol(classe):
            if hasattr(classe,'titol'):
                return classe.titol
            return classe.__name__
        try:
            if hasattr(self,'dwEines'):
                for x in self.dwEines:
                    # x.setParent(None)
                    x.hide()
            self.dwEines = []
            if hasattr(self,'actEines'):
                for x in self.actEines:
                    self.menuEines.removeAction(x)
            self.actEines = []
            nomsEntorns = QgsExpressionContextUtils.projectScope(self.project).variable('qV_entorn')
            if nomsEntorns is not None:
                nomsEntorns = llistaDesDeStr(nomsEntorns)
                for nomEntorn in nomsEntorns:
                    Entorn = QvEines.entorn(nomEntorn)
                    dockWidgets = self.findChildren(Entorn)
                    if len(dockWidgets)>0:
                        dwEntorn = dockWidgets[0]
                    else:
                        dwEntorn = Entorn(self)
                    self.addDockWidget(Qt.RightDockWidgetArea, dwEntorn)
                    if hasattr(dwEntorn,'apareixDockat'):
                        dwEntorn.setFloating(not dwEntorn.apareixDockat)
                    else:
                        dwEntorn.setFloating(True)
                    self.dwEines.append(dwEntorn)
            nomsEines = QgsExpressionContextUtils.projectScope(self.project).variable('qV_eines')
            if nomsEines is not None:
                self.menuEines.addSeparator()
                nomsEines = llistaDesDeStr(nomsEines)
                for nomEina in itertools.chain(nomsEntorns,nomsEines):
                    Eina = QvEines.entorn(nomEina)
                    titol=obteTitol(Eina)
                    # comprovem si ja hi ha alguna acció amb aquest nom. Si hi és, no la repetim
                    accions = self.menuEines.actions()
                    accions = [x for x in accions if x.text()==titol]
                    if len(accions)==0:
                        act = QAction(titol)
                        act.triggered.connect(functools.partial(self.obreEina,Eina))
                        self.actEines.append(act)
                        self.menuEines.addAction(act)
        except Exception as e:
            print(e)
    def obreEina(self,eina):
        dockWidgets = self.findChildren(eina)
        if len(dockWidgets)>0:
            for x in dockWidgets:
                x.show()
        else:
            dwEina = eina(self)
            self.addDockWidget(Qt.RightDockWidgetArea,dwEina)
            dwEina.setFloating(True)

    def restaurarFunc(self):
        if self.maximitzada:
            self.setWindowFlag(Qt.FramelessWindowHint,False)
            self.setWindowState(Qt.WindowActive)
            self.actualitzaWindowFlags()
            amplada=self.width()
            alcada=self.height()
            self.resize(round(0.8*amplada), round(0.8*alcada))
            self.show()
            self.botoRestaurar.setIcon(self.iconaRestaurar2)
        else:
            self.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
            self.botoRestaurar.setIcon(self.iconaRestaurar1)
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.actualitzaWindowFlags()
            self.show()
        self.maximitzada=not self.maximitzada

    def actualitzaWindowFlags(self):
        self.setWindowFlag(Qt.Window)
        self.setWindowFlag(Qt.CustomizeWindowHint,True)
        self.setWindowFlag(Qt.WindowTitleHint,False)
        self.setWindowFlag(Qt.WindowSystemMenuHint,False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint,False)
        self.setWindowFlag(Qt.WindowCloseButtonHint,False)
    
    def prepararDash(self, nom): #???
        def obertura():
            for objecte in self.dashboardActiu:
                objecte.hide() 
            dashboard = nom(self)
            self.dashboardActiu = [dashboard]
            self.layout.addWidget(dashboard)

        return obertura

    def dashStandard(self): #???
        self.canvas.show()
        self.mapeta.show()
        self.layout.addWidget(self.canvas)
        self.frameLlegenda.show()
        self.lblTitolProjecte.setText(self.project.title())
        for objecte in self.dashboardActiu:
            objecte.hide()
        self.dashboardActiu = [self.frameLlegenda, self.canvas, self.mapeta]

    def showLblFlotant(self,txt):
        self.lblFlotant=QvBafarada(txt,self)
        self.lblFlotant.show()

    def hideLblFlotant(self):
        if hasattr(self,'lblFlotant'):
            self.lblFlotant.hide()

    def ferGran(self):
        if not self.mapaMaxim:
            self.desmaximitza()

        else:
            self.showLblFlotant('Premeu F-11, Esc o el botó de maximitzar per sortir de la pantalla completa')
            if hasattr(self.canvas,'bMaximitza'):
                self.canvas.actualitzaBotoMaximitza(True)
            self.dockWidgetsVisibles=[x for x in self.findChildren(QvDockWidget) if x.isVisible()]
            for x in self.dockWidgetsVisibles:
                x.hide()
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
    def desmaximitza(self):
        self.hideLblFlotant()
        self.showMaximized()
        if hasattr(self.canvas,'bMaximitza'):
            self.canvas.actualitzaBotoMaximitza(False)
        self.frame_3.show()
        self.frame_19.show()
        self.frame_2.show()
        if hasattr(self,'dockWidgetsVisibles'):
            for x in self.dockWidgetsVisibles: x.showtq()
        else:
            self.dwLlegenda.setFloating(False)
        self.bar.show()
        self.statusbar.show()

    def clickArbre(self):
        rang = self.distBarris.llegirRang() 
        self.canvas.zoomToFeatureExtent(rang) 

        if self.canviarMapeta.isChecked():
            zona = self.distBarris.llegirNom() 
            location = os.path.join("Imatges\\capturesMapeta\\", zona +".png") 
            self.enviarMapetaTemporal(location) 

    def infoQVista(self):
        self.informacio = QDialog()
        self.informacio.setWindowOpacity(0.8)
        self.ui = Ui_Informacio()
        self.ui.setupUi(self.informacio)
        self.informacio.show()


    def canvasImg(self):
        """
        Obtenim una imatge a partir del canvas en el moment en que la funció es cridada.
        
        Un dialeg demana on guardar-la.
       """    
        dialegFitxer=QFileDialog()

        titol=self.lblTitolProjecte.text()
        nfile,_ = dialegFitxer.getSaveFileName(None,"Guardar imatge", QvMemoria().getDirectoriDesar()+'/'+titol, "(*.png)")

        self.canvas.saveAsImage(nfile)	

    def propietatsLayer(self):
        layer=self.llegenda.currentLayer()
        self.dlgProperties = None
        self.dlgProperties = QvVisualitzacioCapa( self, layer)
        self.dlgProperties.show()

    def esborrarSeleccio(self, tambePanCanvas = True, mascara=False):
        """Esborra les seleccions (no els elements) de qualsevol layer del canvas.

        Keyword Arguments:
            tambePanCanvas {bool} -- Indica si volem tornar al panning sobre el canvas (default: {True})
            mascara {bool} -- Indica si volem eliminar també la màscara (default: {False})
        """
        layers = self.canvas.layers() 
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()
        #Movem el self.canvas.panCanvas a una funció que es diu foraEines per poder treure les eines del mapa sense treure les seleccions, màscares...
        if tambePanCanvas:
            self.foraEines()
        try:
            self.canvas.scene().removeItem(self.toolSelect.rubberband)
        except:
            pass
        if mascara:
            try:
                eliminaMascara(qV)
                self.canvas.refresh()
            except Exception as e:
                print(e)

    def foraEines(self):
        self.canvas.panCanvas()

    def esborrarMesures(self, tambePanCanvas = True):
        """Elimina les mesures sobre el mapa

        Keyword Arguments:
            tambePanCanvas {bool} -- Indica si volem passar al panning també (default: {True})
        """
        if tambePanCanvas:
            self.canvas.panCanvas()
        try:
            self.canvas.scene().removeItem(self.toolMesura.rubberband)
            self.canvas.scene().removeItem(self.toolMesura.rubberband2)
            for x in self.toolMesura.rubberbands:
                self.canvas.scene().removeItem(x)
            for x in self.toolMesura.cercles:
                self.canvas.scene().removeItem(x)
            self.wMesuraGrafica.clear()
            for ver in self.toolMesura.markers:
                self.canvas.scene().removeItem(ver)
            self.wMesuraGrafica.setDistanciaTotal(0)
            self.wMesuraGrafica.setArea(0)
            self.wMesuraGrafica.setDistanciaTempsReal(0)
        except:
            pass


    def definirLabelsStatus(self):    
        styleheetLabel='''
            QLabel {
                background-color: %s;
                color: %s;
                border: 0px;
                margin: 0px;
                padding: 4px;
            }'''%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML)
        stylesheetButton='''
            QvPushButton {
                background-color: %s;
                color: %s;
                margin: 0px;
                border: 0px;
                padding: 4px;
            }'''%(QvConstants.COLORBLANCHTML,QvConstants.COLORFOSCHTML)
        stylesheetLineEdit='''
            QLineEdit {
                margin: 0px; border: 0px; padding: 0px;
            }
            '''
        stylesheetLineEditFiltre=stylesheetLineEdit+'''
            QLineEdit[text=""] {
                color: %s;
            }'''%QvConstants.COLORTEXTHINTHTML

        alcada=24

        # self.bOrientacio = QvPushButton(flat=True)
        # self.bOrientacio.setStyleSheet(stylesheetButton)
        # self.bOrientacio.setFixedHeight(alcada)



        # self.cbEstil = QComboBox()
        # self.cbEstil.currentTextChanged.connect(self.canviaTema)
        # # self.cbEstil.setFrameStyle(QFrame.StyledPanel )
        # self.cbEstil.setFixedHeight(alcada)

        #Afegim tots els widgets de cop
        #Així fer una reordenació serà més senzill
        self.statusbar = QvStatusBar(self,['nomProjecte','capaSeleccionada',('seleccioExpressio',1), 'progressBar', 'connexio',('coordenades',1),'projeccio', 'escala'],self.canvas,self.llegenda)
        self.setStatusBar(self.statusbar)
        self.statusbar.setStyleSheet('QLabel{border: 1px solid black}')
        # self.statusbar.addPermanentWidget( self.lblProjecte, 0 )
        # self.statusbar.addPermanentWidget(self.lblCapaSeleccionadaInf)
        # self.statusbar.addPermanentWidget(self.leSeleccioExpressio, 1)
        # self.statusbar.addPermanentWidget( self.sbCarregantCanvas, 0 )
        # self.statusbar.addPermanentWidget( self.lblConnexio, 0 )
        # self.statusbar.addPermanentWidget(self.wXY, 1 )
        # self.statusbar.addPermanentWidget( self.lblProjeccio, 0 )
        # self.statusbar.addPermanentWidget( self.wScale, 0 )
    

    # CrearMapeta - Comentado porque hay un error al salir en la 3.16
    #
    # def editarOrientacio(self):
    #     # puenteo funcion para probar crear mapeta
    #     if self.dwcrearMapeta.isHidden():
    #         self.dwcrearMapeta.show()
    #     else:
    #         self.dwcrearMapeta.hide()
    #     self.canvas.refresh()

    def obrirLlegenda(self):
        if self.dwLlegenda.isHidden():
            self.dwLlegenda.show()
            self.dwLlegenda.setFloating(False)
        else:
            self.dwLlegenda.hide()

    def obrirCataleg(self):
        if not hasattr(self, 'wCatalegGran') or self.wCatalegGran is None:
            self.wCatalegGran=QvNouCatalegCapes(self)
            self.wCatalegGran.afegirCapa.connect(lambda x: QvFuncions.afegirQlr(x, self.llegenda))
        try:
            self.wCatalegGran.showMaximized()
        except Exception as e:
            QMessageBox.warning(self,'Error en el catàleg',"Hi ha hagut un error durant l'execució del catàleg de capes. Si l'error persisteix, contacteu amb el vostre responsable")
    def obrirCatalegLateral(self):
        # dock widget catàleg de capes
        if not hasattr(self,'dwCataleg'):
            self.preparacioCataleg()
        self.dwCataleg.show()
    def afegirCatalegCapes(self):
        nodes = self.llegenda.selectedNodes()
        if nodes is not None and len(nodes)>0:
            dial = QvCreadorCatalegCapes(nodes, self.canvas, self.project, parent=self)
            dial.show()
        else:
            QMessageBox.information(self,'Atenció','Seleccioneu una capa o grup a la llegenda per poder-la afegir al catàleg')
            pass

    def obrirDialegProjecte(self):
        if self.teCanvisPendents(): #Posar la comprovació del dirty bit
            ret = self.missatgeDesar(titol='Crear un nou mapa',txtCancelar='Cancel·lar')
            if ret == QMessageBox.AcceptRole:
                b = self.desarProjecte()
                if b:
                    self.obrirProjecte(self.pathProjecteActual)
                else:
                    return
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                pass
            elif ret == QMessageBox.DestructiveRole:
                return

        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl('../dades/projectes/'))
        nfile,_ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis", "../dades/projectes/",
            "Tots els mapes acceptats (*.qgs *.qgz *.gpkg);; Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz);;Mapes GeoPackage (*.gpkg)")

        if nfile is not None:
            self.obrirProjecteAmbRang(nfile)
    
    def carregarCapa(self,nfile):
        ext = Path(nfile).suffix.lower()
        if ext=='.qlr':
            QvFuncions.afegirQlr(nfile, self.llegenda)
        elif ext=='.shp':
            layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
            if not layer.isValid():
                return
        elif ext=='.gpkg':
            nomsCapes = QvCarregadorGPKG.triaCapes(nfile,self)
            capes = [QgsVectorLayer(f'{nfile}|layername={x}',x,'ogr') for x in nomsCapes]
            if len(capes)==0: return
            self.project.addMapLayers(capes)
        elif ext=='.csv':
            QvFuncions.carregarLayerCSV(nfile, self.project, self.llegenda)
        
        self.setDirtyBit()
           
    def obrirDialegNovaCapa(self, esquemes, arxiusPermesos):
        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl('../Dades/Capes/'))
        dialegObertura.setSupportedSchemes(esquemes)

        nfile,_ = dialegObertura.getOpenFileName(None,"Nova capa", '../Dades/Capes/', arxiusPermesos)
        if nfile is not None:
            self.carregarCapa(nfile)

    def obrirDialegNovaCapaQLR(self):
        self.obrirDialegNovaCapa(["Projectes Qgis (*.qgs)", "Otro esquema"],"Capes QGIS (*.qlr);;Tots els arxius (*.*)")

    def obrirDialegNovaCapaGIS(self):
        self.obrirDialegNovaCapa(["Arxius GIS (*.shp *.gpkg)", "Otro esquema"],"Arxius GIS (*.shp *.gpkg);; ShapeFile (*.shp);; Geopackage (*.gpkg);;Tots els arxius (*.*)")
            
    def obrirDialegNovaCapaCSV(self):
        self.obrirDialegNovaCapa(["Arxius csv (*.csv)", "Otro esquema"],"CSV (*.csv);;Tots els arxius (*.*)")

    def teCanvisPendents(self):
        if self.llegenda.digitize is not None: self.llegenda.digitize.stop(True)
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

    #A més de desar, retornarà un booleà indicant si l'usuari ha desat (True) o ha cancelat (False)
    def desarProjecte(self, reload=True):
        """ la funcio retorna si s'ha acabat guardant o no
            Protecció dels projectes read-only: tres vies:
        -       Variable del projecte qV_readOnly=’True’
        -       Ubicació en una carpeta de només-lectura
        -       Ubicació en una de les subcarpetes de N:\\SITEBAPL\PyQgis\qVista
        -       Ubicació en una de les subcarpetes de N:\9SITEB\Publicacions\qVista
        """
        self.teCanvisPendents()
        if QgsExpressionContextUtils.projectScope(self.project).variable('qV_readOnly') == 'True':
            b = self.dialegDesarComA()
        elif not self.directoriValidDesar(self.pathProjecteActual):
            b = self.dialegDesarComA()
        # elif self.pathProjecteActual == 'mapesOffline/qVista default map.qgs':
        #     b = self.dialegDesarComA()
        # elif self.pathProjecteActual.startswith( 'n:/siteb/apl/pyqgis/qvista' ):
        #     b = self.dialegDesarComA()
        # elif self.pathProjecteActual.startswith( 'n:/9siteb/publicacions/qvista' ):
        #     b = self.dialegDesarComA()
        elif hasattr(self,'mapaCataleg'):
            b = self.dialegDesarComA()
        else:
            self._desaElProjecte(self.pathProjecteActual)
            b = True
        if b and reload:
            self.obrirProjecte(self.pathProjecteActual)
        return b
    def directoriValidDesar(self,nfile):
        def path_fill(p1,p2):
            # retorna true si p1 penja de p2
            # per exemple, 'C:/' i 'C:/hola.qgs'
            p1 = Path(p1).absolute()
            p2 = Path(p2).absolute()

            d1, _ = os.path.splitdrive(p1)
            d2, _ = os.path.splitdrive(p2)
            # si són discs diferents, fora
            if d1!=d2: return False
            res = Path(os.path.commonpath([p1,p2]))==p2
            return res
        # si comparem strings, podem tenir problemes 
        #  ('C:/exemple.qgs' és diferent de 'C://exemple.qgs' i de 'C:\exemple.qgs')
        # A python 3.9 podrem fer path.is_relative_to(x)
        path = Path(nfile).absolute()
        # return path!=Path(projecteInicial) and not any(path.is_relative_to, carpetaCatalegProjectesLlista)
        return path!=Path(projecteInicial).absolute() and not any(map(lambda x: path_fill(path,x), carpetaCatalegProjectesLlista+QvMemoria().getCatalegsLocals()))
        # return not(nfile.endswith('mapesOffline/qVista default map.qgs') or nfile.startswith( 'n:/siteb/apl/pyqgis/qvista' ) or nfile.startswith( 'n:/9siteb/publicacions/qvista' ))
    
    # Gestiona el diàleg "Desar com a" (guardar como)
    def dialegDesarComA(self):
        #https://stackoverflow.com/a/46801075
        def get_valid_filename(s):
            s = str(s).strip().replace(' ', '_')
            return re.sub(r'(?u)[^-\w.]', '', s)
        pathDesarPerDefecte = QvMemoria().getDirectoriDesar()

        # nom = re.sub(r'?a[\W_]+','',self.titolProjecte).strip()
        nom = get_valid_filename(self.titolProjecte)

        pathOnDesem = os.path.join(pathDesarPerDefecte,nom)
        nfile,_ = QFileDialog.getSaveFileName(None,"Desar Projecte Qgis", pathOnDesem, "Projectes Qgis (*.qgs)")
        
        if nfile=='': return False
        elif not self.directoriValidDesar(nfile):
            QMessageBox.warning(self,'Advertència','No es pot desar en aquesta adreça. Proveu de fer-ho en una altra')
            # msgBox = QMessageBox()
            # msgBox.setWindowTitle("Advertència")
            # msgBox.setIcon(QMessageBox.Warning)
            # msgBox.setText("No pots guardar el teu mapa en aquesta adreça.")
            # msgBox.setInformativeText("Prova de fer-ho en una altre.")
            # msgBox.setStandardButtons(QMessageBox.Ok)
            # msgBox.setDefaultButton(QMessageBox.Ok)
            # msgBox.exec()
            return False 
        self._desaElProjecte(nfile)
        QvMemoria().setDirectoriDesar(str(Path(nfile).parent))
        return True

    @QvFuncions.mostraSpinner
    def _desaElProjecte(self,proj):
        '''La funció que desa el projecte com a tal
           No invocar directament. Per desar un projecte, cal utilitzar self.dialegDesarComA() o bé self.desarProjecte()'''
        qApp.setOverrideCursor(QvConstants.cursorOcupat())

        # si hem desat un nou mapa, aquest no serà readOnly
        QgsExpressionContextUtils.setProjectVariable(self.project,'qV_readOnly','False')

        # l'autor d'aquest projecte serà l'usuari actual, i no pas el creador del projecte base
        md=self.project.metadata()
        md.setAuthor(QvApp().nomUsuari())
        self.project.setMetadata(md)

        # si estem desant a un lloc diferent de l'actual, passem a apuntar al lloc nou
        if proj!=self.pathProjecteActual:
            self.pathProjecteActual=proj

        # desem com a tal
        self.project.write(proj)
        qApp.restoreOverrideCursor()
        qApp.processEvents()
        # Deixem de tenir canvis pendents
        self.setDirtyBit(False)

    def provaDeTancar(self):
        QvMemoria().pafuera()
        if self.teCanvisPendents():
            ret = self.missatgeDesar()
            if ret == QMessageBox.AcceptRole:
                b = self.desarProjecte()
                if not b: return
                #Si cancel·la, retornem. Si no, cridem a gestioSortida
                self.gestioSortida()
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                self.gestioSortida()
            elif ret == QMessageBox.DestructiveRole:
                return
        else:
            self.gestioSortida()

    def closeEvent(self,event):
        self.provaDeTancar()

    def actualitzaMapesRecents(self,ultim=None):
        self.mapesRecents=QvMemoria().getMapesRecents()
        #Desem els mapes recents, eliminant repeticions i salts de línia que poden portar problemes
        self.mapesRecents=[x.replace('\n','') for x in self.mapesRecents]
        #Eliminem repeticions amb el set. Com que el set perd l'ordre, després els ordenem utilitzant com a clau l'índex de la llista
        self.mapesRecents=sorted(set(self.mapesRecents),key=lambda x: self.mapesRecents.index(x))[:9]
        QvMemoria().setMapesRecents(self.mapesRecents)
        #Finalment creem les accions
        self.menuRecents.clear()
        self.accionsMapesRecentsDict={QAction(x):x.replace('\n','') for x in self.mapesRecents} #Fem un diccionari on la clau és l'acció i el valor és la ruta del mapa que ha d'obrir l'acció
        for x, y in self.accionsMapesRecentsDict.items():
            x.setToolTip(y)
            #functools.partial crea una funció a partir de passar-li uns determinats paràmetres a una altra
            #Teòricament serveix per passar-li només una part, però whatever
            #Si fèiem connect a lambda: self.obrirProjecte(y) o similars, no funcionava i sempre rebia com a paràmetre la última y :'(
            x.triggered.connect(functools.partial(self.obrirRecentAmbRang,y))
            self.menuRecents.addAction(x)
        if ultim is not None:
            self.mapesRecents.insert(0,ultim)

    def gestioSortida(self):
        if self.sortida:
            self.sortida = False
        else:
            return
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
            QvApp().logFi() 
            QCoreApplication.exit(0) 
        except Exception as ee:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            
            msg.setText(str(ee))
            msg.setStandardButtons(QMessageBox.Close)
            msg.exec_()

    def pavimentacio(self): 
        self.project.read('d:/qVista/Dades/CatalegProjectes/Vialitat/PavimentacioDemo.qgs')       
        self.dwPavim = DockPavim(self)
        self.addDockWidget( Qt.RightDockWidgetArea, self.dwPavim)
        self.dwPavim.show()    
        
    # def marxesCiutat(self): 
    #     self.dwMarxes = MarxesCiutat(self)
    #     self.addDockWidget( Qt.RightDockWidgetArea, self.dwMarxes)
    #     self.dwMarxes.show()    

    

    def nouMapa(self):
        if self.teCanvisPendents(): #Posar la comprovació del dirty bit
            ret = self.missatgeDesar(titol='Crear un nou mapa',txtCancelar='Cancel·lar')
            if ret == QMessageBox.AcceptRole:
                b = self.desarProjecte()
                if b:
                    self.obrirProjecte(self.pathProjecteActual)
                else: 
                    return
            elif ret ==  QMessageBox.RejectRole: #Aquest i el seguent estàn invertits en teoria, però així funciona bé
                pass
            elif ret == QMessageBox.DestructiveRole:
                return
        def carregarMapa(ruta, titol):
            self.obrirProjecte(ruta,nou=True)
            self.lblTitolProjecte.setText(titol)
            self.titolProjecte=titol
        dialegNouMapa = QvNouMapa(carregarMapa,self)
        dialegNouMapa.exec()

    def obreDocumentacio(self):
        self.startMovie()
        doc=QvDocumentacio(self)
        doc.comencaCarrega.connect(self.startMovie)
        doc.acabaCarrega.connect(self.stopMovie)
        self.stopMovie()
        doc.show()

def cartoBCN():
    obreURL('https://w20.bcn.cat/cartobcn/')

def geoportalBCN():
    obreURL('http://www.bcn.cat/geoportal/ca/geoportal.html')

def opendataBCN():
    obreURL('https://opendata-ajuntament.barcelona.cat/')

def bcnPIC():
    obreURL('http://www.bcn.cat/guia/bcnpicc.html')
    
def planolBCN():
    obreURL('https://w33.bcn.cat/planolBCN/ca/')

def piuPortal():
    obreURL('https://ajuntament.barcelona.cat/informaciourbanistica/cerca/ca/')

def obreURL(urlstr=''):
    url = QtCore.QUrl(urlstr)
    try:
        b = QDesktopServices().openUrl(url)
        if not b:
            try:
                os.system('start firefox ' + urlstr)
            except: 
                QMessageBox.warning(qV,'Error de navegador', "No s'ha pogut obrir el navegador. Si us plau, comproveu la vostre connexió.")
    except:
        QMessageBox.warning(qV,'Error de navegador', "No s'ha pogut obrir el navegador. Si us plau, comproveu la vostre connexió.")


def missatgeCaixa(textTitol,textInformacio):
    QMessageBox.warning(qV,textTitol,textInformacio)
    # msgBox=QMessageBox()
    # msgBox.setText(textTitol)
    # msgBox.setInformativeText(textInformacio)
    # msgBox.exec()

class QvDockWidget(QDockWidget):
    tancat = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDockatInici()
    def setDockatInici(self,dockat=True):
        self.dockat=dockat
    def show(self):
        super().show()
        if self.dockat: self.setFloating(False)
    def showtq(self):
        #Show tal qual. És a dir, ho mostra on estigués abans
        super().show()
    def closeEvent(self,e):
        super().closeEvent(e)
        self.tancat.emit()

def migraConfigs():
    arxius=('ultimAvisObert','ultimaNewOberta','mapesRecents','directoriDesar','volHints','dadesMascara','geocod.json','geocodificats.json','catalegsLocals')
    for x in arxius:
        aMoure=os.path.join(dadesdir,x)
        if os.path.isfile(aMoure):
            os.replace(aMoure,os.path.join(configdir,x))

def qvSplashScreen(imatge):
    splash_pix = QPixmap(os.path.join(imatgesDir,'SplashScreen_qVista.png'))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(True)
    splash.showMessage("""Institut Municipal d'Informàtica (IMI) Versió """+versio+'  ',Qt.AlignRight | Qt.AlignBottom, QvConstants.COLORFOSC)
    splash.setFont(QFont(QvConstants.NOMFONT,8))
    splash.show()
    return splash

# Cos de la funció principal  d'arranque de qVista
def main(argv):
    # Definició 
    global qV
    
    # Ajustes de pantalla ANTES de crear la aplicación
    QvFuncions.setDPI()

    with qgisapp(sysexit=False) as app: 
        
        # Se instancia QvApp al principio para el control de errores e idioma
        qVapp = QvApp()
        qVapp.carregaIdioma(app, 'ca')

        # Splash image al començar el programa. La tancarem amb splash.finish(qV)
        splash = qvSplashScreen(os.path.join(imatgesDir,'SplashScreen_qVista.png'))
      
        # Logo de la finestra
        app.setWindowIcon(QIcon(os.path.join(imatgesDir,'QVistaLogo_256.png')))
        
        #Esborrem els temporals de la sessió anterior
        QvFuncions.esborraCarpetaTemporal()
        migraConfigs()
        app.processEvents()

        # Lectura fitxer d'estil
        try:
            with open('style.qss') as st:
                app.setStyleSheet(st.read())
        except FileNotFoundError:
            # no hi ha stylesheet
            pass

        # Preparació log de l'aplicació
        ok = qVapp.logInici()            # Por defecto: family='QVISTA', logname='DESKTOP'
        if not ok and not QvFuncions.debugging():
            print('ERROR LOG >>', qVapp.logError())
       
        # Estil visual de l'aplicació
        app.setStyle(QStyleFactory.create('fusion'))
        
        # Proyecto inicial
        if len(argv) > 1:
            iniProj = argv[1] # Lo toma de la línea de comandos o...
        else:
            iniProj = projecteInicial # ...de configuracioQvista.py

        # Instanciem la classe QVista i fem qV global per poder ser utilitzada arreu
        # Paso app, para que QvCanvas pueda cambiar cursores
        qV = QVista(app, iniProj, titolFinestra)
       
        # Restauració del est
        qV.restoreState(qV.tempState) 
        qV.showMaximized()

        # Tanquem la imatge splash.
        splash.finish(qV)

        # Avisos de l'aplicació
        try:
            QvAvis()
        except:
            print('no es pot accedir als avisos')

        # Sabies que...
        try:
            QvSabiesQue(qV)
        except:
            print('No hem pogut mostrar el "sabies que..."')
        
        # Guardem el temps d'arrancada
        qVapp.logRegistre('LOG_TEMPS', qV.lblTempsArrencada.text())

        # Gestió de la sortida
        app.aboutToQuit.connect(qV.gestioSortida)


# Arranque de l'aplicació qVista
if __name__ == "__main__":
    try:
        main(sys.argv)
        
    except Exception as err:
        QvApp().bugException(err)
