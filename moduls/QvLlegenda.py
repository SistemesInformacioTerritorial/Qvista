# -*- coding: utf-8 -*-

import sys
import os
_cwd = os.getcwd()
if _cwd not in sys.path:
    sys.path.insert(0, _cwd)

from qgis.core import (QgsProject, QgsLegendModel,QgsMapLayer, QgsAbstractGeometry,
                       QgsExpressionContextUtils)
from qgis.gui import QgsLayerTreeView, QgsLayerTreeMapCanvasBridge, QgsLayerTreeViewIndicator
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import pyqtSignal
from moduls.QvAccions import QvAccions
from moduls.QvAtributs import QvAtributs
from moduls.QvVideo import QvVideo
from moduls.QvEscala import QvEscala
from moduls.QvMapRenderer import QvMapRenderer
from moduls.QvMapVars import *
from moduls.QvLlegendaAux import *
from moduls.QvLlegendaMascara import QvLlegendaMascara
from configuracioQvista import imatgesDir

import os
import win32file


# Resultado de compilacion de recursos del fuente de qgis (directorio images)
# pyrcc5 images.qrc >images_rc.py
import images_rc  # NOQA

class QvLlegenda(QgsLayerTreeView):

    obertaTaulaAtributs = pyqtSignal()
    clicatMenuContexte = pyqtSignal(str)
    carregantProjecte = pyqtSignal()
    projecteCarregat = pyqtSignal(str)
    projecteModificat = pyqtSignal(str)

    def __init__(self, canvas=None, atributs=None, canviCapaActiva=None):
        QgsLayerTreeView.__init__(self)

        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.canvas = None
        self.bridge = None
        self.bridges = []
        self.atributs = atributs
        self.editable = True
        self.lastExtent = None
        self.escales = None
        self.directory = '.'
        self.mask = None
        # self.restoreExtent = 0
        # print('restoreExtent', self.restoreExtent)

        self.project.readProject.connect(self.nouProjecte)
        self.project.legendLayersAdded.connect(self.actIcones)
        self.root.layerOrderChanged.connect(self.actIcones)
        # self.project.loadingLayerMessageReceived.connect(self.msgCapes)

        # self.setWhatsThis(QvApp().carregaAjuda(self))

        # Asociar canvas y bridges
        self.mapBridge(canvas)

        # Evento de nueva capa seleccionada
        self.connectaCanviCapaActiva(canviCapaActiva)

        # Mapificaciones
        self.mapRenderer = QvMapRenderer(self)

        # Model
        self.model = QvModelLlegenda(self.root)
        self.model.setFlag(QgsLegendModel.ShowLegend, True)
        self.model.setFlag(QgsLegendModel.ShowLegendAsTree, True)
        self.editarLlegenda(True)

        self.setModel(self.model)
        if self.canvas is not None:
            self.canvas.scaleChanged.connect(self.connectaEscala)

        # Acciones disponibles
        self.accions = QvAccions()
        self.setAccions()
        # Lista de acciones que apareceran en el menú
        self.menuAccions = []
        self.setMenuProvider(QvMenuLlegenda(self))

        self.iconaFiltre = QgsLayerTreeViewIndicator()
        self.iconaFiltre.setIcon(QIcon(imatgesDir+'filter.png'))
        self.iconaFiltre.setToolTip('Filtre actiu')
        self.iconaFiltre.clicked.connect(self.filterElements)

        self.iconaMap = QgsLayerTreeViewIndicator()
        self.iconaMap.setIcon(QIcon(imatgesDir+'categories2.png'))
        self.iconaMap.setToolTip('Categories de mapificació')
        self.iconaMap.clicked.connect(self.mapRenderer.modifyRenderer)

        if self.atributs is not None:
            self.atributs.modificatFiltreCapa.connect(self.actIconaFiltre)

        self.projecteCapes = None
        self.player = None

        if self.canvas is not None:
            self.escales = QvEscala(self.canvas)
            self.project.layerLoaded.connect(self.iniProjecte)
            self.canvas.layersChanged.connect(self.capesProject)
            self.canvas.renderStarting.connect(self.fiProjecte)
            # self.canvas.renderComplete.connect(self.fiProjecte)

        self.fSignal = lambda: self.projecteModificat.emit('canvasLayersChanged')
        self.iniSignal = False

    def modificacioProjecte(self, txt='userModification'):
        if self.iniSignal:
            self.projecteModificat.emit(txt)

    def iniProjecte(self, num, tot):
        # La carga de un proyecto se inicia con la capa #0
        if self.iniSignal:
            self.bridge.canvasLayersChanged.disconnect(self.fSignal)
            self.iniSignal = False

        if self.projecteCapes is None and num == 0:
            self.projecteCapes = False
            if self.player is not None:
                self.player.show()
                self.player.mediaPlayer.play()
            self.carregantProjecte.emit()

    def capesProject(self):
        # Capas cargadas
        if self.projecteCapes is not None and not self.projecteCapes:
            self.projecteCapes = True

    def fiProjecte(self):
        # La carga de un proyecto acaba con su visualización en el canvas de todas las capas
        if self.projecteCapes is not None and self.projecteCapes:
            self.projecteCapes = None
            if self.player is not None:
                self.player.mediaPlayer.pause()
                self.player.hide()
            self.projecteCarregat.emit(self.project.fileName())
            if not self.iniSignal:
                self.bridge.canvasLayersChanged.connect(self.fSignal)
                self.iniSignal = True

    def setPlayer(self, fich, ancho=170, alto=170):
        if os.path.isfile(fich):
            self.player = QvVideo(fich, ancho, alto, self.canvas)
        else:
            self.player = None

    def deleteCanvasPosition(self):
        self.lastExtent = None

    def saveCanvasPosition(self):
        self.lastExtent = self.canvas.extent()

    def restoreCanvasPosition(self):
        if self.lastExtent is not None:
            self.canvas.setExtent(self.lastExtent)

    def printCanvasPosition(self, msg):
        e = round(self.canvas.scale(), 2)
        x = round(self.canvas.center().x(), 2)
        y = round(self.canvas.center().y(), 2)
        print(msg, ':',
              'escala -', str(e),
              'centro: (', str(x),
              '-', str(y), ')')

    def editarLlegenda(self, on=True):
        self.editable = on
        self.model.setFlag(QgsLegendModel.AllowNodeReorder, on)
        self.model.setFlag(QgsLegendModel.AllowNodeRename, on)
        self.model.setFlag(QgsLegendModel.AllowLegendChangeState, on)
        self.model.setFlag(QgsLegendModel.AllowNodeChangeVisibility, on)
        self.model.setFlag(QgsLegendModel.DeferredLegendInvalidation, on)
        # self.setAcceptDrops(on)
        # # self.setDropIndicatorShown(on)
        # print('acceptDrops', self.acceptDrops())

    def connectaEscala(self, escala):
        # print('Cambio escala:', escala)
        self.model.setScale(escala)
        for capa in self.capes():
            if capa.hasScaleBasedVisibility():
                capa.nameChanged.emit()

    def capaLocal(self, capa):
        try:
            uri = capa.dataProvider().dataSourceUri()
            drive = uri.split(':')[0]
            return win32file.GetDriveType(drive + ':') == win32file.DRIVE_FIXED
        except:
            return False

    def actIcones(self):
        if not self.editable:
            return
        for capa in self.capes():
            if capa.type() == QgsMapLayer.VectorLayer:
                node = self.root.findLayer(capa.id())
                if node is not None:
                    # Filtro
                    if capa.subsetString() != '':
                        self.addIndicator(node, self.iconaFiltre)
                    else:
                        self.removeIndicator(node, self.iconaFiltre)
                    # Mapificacón
                    var = QgsExpressionContextUtils.layerScope(capa).variable(MAP_ID)
                    if var is not None and self.capaLocal(capa):
                        self.addIndicator(node, self.iconaMap)
                    else:
                        self.removeIndicator(node, self.iconaMap)
                    capa.nameChanged.emit()

    def actIconaFiltre(self, capa):
        if not self.editable:
            return
        if capa is None or capa.type() != QgsMapLayer.VectorLayer:
            return
        node = self.root.findLayer(capa.id())
        if node is not None:
            if capa.subsetString() == '':
                self.removeIndicator(node, self.iconaFiltre)
            else:
                self.addIndicator(node, self.iconaFiltre)
            capa.nameChanged.emit()
            self.modificacioProjecte('filterModified')

    def nouProjecte(self):
        # Borrar tabs de atributos si existen
        if self.atributs is not None:
            self.atributs.deleteTabs()

        self.escales.nouProjecte(self.project)

        for layer in self.capes():
            if layer.type() == QgsMapLayer.VectorLayer:
                self.actIconaFiltre(layer)
            if layer.type() == QgsMapLayer.RasterLayer and self.capaMarcada(layer):
                node = self.root.findLayer(layer.id())
                # self.restoreExtent = 2
                # print('restoreExtent', self.restoreExtent)
                # node.visibilityChanged.connect(self.restoreCanvasPosition)
                # self.restoreCanvasPosition()
                node.setItemVisibilityChecked(False)
                # # self.restoreCanvasPosition()
                node.setItemVisibilityChecked(True)

    def connectaCanviCapaActiva(self, canviCapaActiva):
        if canviCapaActiva:
            self.currentLayerChanged.connect(canviCapaActiva)

    def mapBridge(self, canvas):
        """
        Enlaza el proyecto con un canvas. La primera vez se invoca con el canvas del
        mapa principal. El resto, con los temas.

        Arguments:
            canvas {QgsMapCanvas} -- Canvas donde se muestra el proyecto
                bridges
        """
        if canvas is None:
            return
        bridge = QgsLayerTreeMapCanvasBridge(self.root, canvas)
        if self.canvas is None:  # Canvas principal
            self.canvasSettings(canvas)
            self.canvas = canvas
            self.bridge = bridge
            self.bridge.canvasLayersChanged.connect(self.maskUpdate)
        else:
            self.bridges.append((canvas, bridge))

    def setMask(self, layer, polygonId):
        if layer is None or polygonId is None:
            self.mask = None
        else:
            self.mask = QvLlegendaMascara(self, layer, polygonId)

    def maskUpdate(self):
        if self.mask is None:
            return
        self.mask.maskInit()

    def canvasSettings(self, canvas):
        canvas.enableAntiAliasing(True)
        canvas.setWheelFactor(2)
        canvas.setCachingEnabled(True)
        canvas.setParallelRenderingEnabled(True)
        canvas.setMapUpdateInterval(250)
        canvas.setSegmentationTolerance(0.01745)
        canvas.setSegmentationToleranceType(QgsAbstractGeometry.MaximumAngle)

    def temes(self):
        return self.project.mapThemeCollection().mapThemes()

    def capaPerNom(self, nomCapa):
        """
        Devuelve el primer layer con el nombre especificado.

        Arguments:
            nomCapa {String} -- El nombre del layer que queremos recuperar.

        Returns:
            QgsMapLayer -- El layer que hemos pedido por nombre.

        """
        capes = self.project.mapLayersByName(nomCapa)
        if len(capes) > 0:
            return capes[0]
        else:
            return None

    def capes(self):
        """
        Devuelve la lista de capas de la leyenda.

        Returns:
            List de QgsMapLayers -- La lista de capas.

        """
        for capaId in self.project.mapLayers():
            yield self.project.mapLayer(capaId)

    def veureCapa(self, capa, visible=True, subCapas=True):
        """
        Hace visible o invisible una layer.

        Arguments:
            capa {QgsMapLayer} -- Layer al que queremos cambiar su visibilidad.
            visible {bool} -- True (visible) o False (invisible).
            subCapes {bool} -- True si queremos cambiar también la visibilidad de los hijos

        """
        node = self.root.findLayer(capa.id())
        if node is not None:
            if visible:
                node.setItemVisibilityCheckedParentRecursive(True)
                if subCapas:
                    node.setItemVisibilityCheckedRecursive(True)

            else:
                node.setItemVisibilityChecked(False)

    def capaVisible(self, capa):
        node = self.root.findLayer(capa.id())
        if node is not None:
            v = node.isVisible()
            if v and capa.hasScaleBasedVisibility() and self.canvas is not None:
                return capa.isInScaleRange(self.canvas.scale())
            return v
        return False

    def capaMarcada(self, capa):
        node = self.root.findLayer(capa.id())
        if node is not None:
            return node.itemVisibilityChecked()
        return False

    def setAccions(self):
        act = QAction()
        act.setText("Defineix grup")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().addGroup)
        self.accions.afegirAccio('addGroup', act)

        act = QAction()
        act.setText("Afegeix capes Qgis")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))ic_beach_access_black_48dp
        act.triggered.connect(self.addLayersFromFile)
        self.accions.afegirAccio('addLayersFromFile', act)

        act = QAction()
        act.setText("Desa capes Qgis")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))ic_beach_access_black_48dp
        act.triggered.connect(self.saveLayersToFile)
        self.accions.afegirAccio('saveLayersToFile', act)

        act = QAction()
        act.setText("Canvia nom")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.renameGroupOrLayer)  # , type = Qt.DirectConnection)
        self.accions.afegirAccio('renameGroupOrLayer', act)

        #
        # TODO:
        # Sincronizar señales para que la segunda espere al final de la primera
        #

        # if self.atributs is not None:
        #   act.triggered.connect(lambda: self.atributs.tabTaula(self.currentLayer()))

        act = QAction()
        act.setText("Esborra capa o grup")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        if self.atributs is not None:
            act.triggered.connect(lambda: self.atributs.tancarTaules(
                QgsLayerTreeUtils.collectMapLayersRecursive([self.currentNode()])))
        act.triggered.connect(self.removeGroupOrLayer)
        # No se usa defaultActions() porque elimina todos los seleccionados
        self.accions.afegirAccio('removeGroupOrLayer', act)

        act = QAction()
        act.setText("Enquadra capa")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.showLayerMap)
        self.accions.afegirAccio('showLayerMap', act)

        act = QAction()
        act.setText("Mostra contador elements")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().showFeatureCount)
        # act.setCheckable(True)
        # act.setChecked(False)
        self.accions.afegirAccio('showFeatureCount', act)

        act = QAction()
        act.setText("Mostra taula dades")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.showFeatureTable)
        self.accions.afegirAccio('showFeatureTable', act)

        act = QAction()
        act.setText("Filtra elements")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.filterElements)
        self.accions.afegirAccio('filterElements', act)

        act = QAction()
        act.setText("Esborra filtre")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.removeFilter)
        self.accions.afegirAccio('removeFilter', act)

    def calcTipusMenu(self):
        # Tipos: none, group, layer, symb
        tipo = 'none'
        idx = self.currentIndex()
        if idx.isValid():
            node = self.currentNode()
            if node is None:
                tipo = 'symb'
            else:
                tipoNodo = node.nodeType()
                if tipoNodo == QgsLayerTreeNode.NodeGroup:
                    tipo = 'group'
                elif tipoNodo == QgsLayerTreeNode.NodeLayer:
                    tipo = 'layer'
        return tipo

    def setMenuAccions(self):
        # Menú dinámico según tipo de elemento sobre el que se clicó
        self.menuAccions = []
        tipo = self.calcTipusMenu()
        if tipo == 'layer':
            capa = self.currentLayer()
            if capa is not None and capa.type() == QgsMapLayer.VectorLayer:
                if self.atributs is not None:
                    self.menuAccions += ['showFeatureTable', 'filterElements']
                self.menuAccions += ['showFeatureCount']
            if capa is not None and self.canvas is not None:
                self.menuAccions += ['showLayerMap']
            self.menuAccions += ['separator']
            if self.editable:
                self.menuAccions += ['addGroup', 'renameGroupOrLayer', 'removeGroupOrLayer']
            self.menuAccions += ['saveLayersToFile']
        elif tipo == 'group':
            if self.editable:
                self.menuAccions += ['addGroup', 'renameGroupOrLayer', 'addLayersFromFile',
                                     'removeGroupOrLayer']
            self.menuAccions += ['saveLayersToFile']
        elif tipo == 'none':
            if self.editable:
                self.menuAccions += ['addGroup', 'addLayersFromFile']
                # if QvApp().usuari in ('CPRET', 'DE1717'):
                #     self.menuAccions += ['addCustomCSV']
        else:  # 'symb'
            pass
        return tipo

    # def addGroup(self):
    #     self.projecteModificat.emit('addGroup')
    #     self.defaultActions().addGroup()

    def renameGroupOrLayer(self):
        self.modificacioProjecte('renameGroupOrLayer')
        self.defaultActions().renameGroupOrLayer()

    def removeGroupOrLayer(self):
        node = self.currentNode()
        if node is not None:
            node.parent().removeChildNode(node)

    def addLayersFromFile(self):
        dlgLayers = QFileDialog()
        nfile, ok = dlgLayers.getOpenFileName(None, "Afegir Capes Qgis",
                                              self.directory, "Capes Qgis (*.qlr)")
        if ok and nfile != '':
            self.directory = os.path.dirname(nfile)
            ok, txt = QgsLayerDefinition.loadLayerDefinition(nfile, self.project, self.root)
            if not ok:
                print('No se pudo importar capas', txt)

    def saveStyleToGeoPackage(self, capa, nom="", desc="", default=True):
        s = QgsSettings()
        s.setValue("qgis/overwriteStyle", True)
        return capa.saveStyleToDatabase(nom, desc, default, "")

    def saveLayersToFile(self):
        nodes = self.selectedNodes()
        if len(nodes) > 0:
            dlgLayers = QFileDialog()
            if self.directory is not None:
                dlgLayers.setDirectory(self.directory)
            nfile, ok = dlgLayers.getSaveFileName(None, "Desar Capes Qgis",
                                                  self.directory, "Capes Qgis (*.qlr)")
            if ok and nfile != '':
                self.directory = os.path.dirname(nfile)
                ok, txt = QgsLayerDefinition.exportLayerDefinition(nfile, nodes)
                if not ok:
                    print('No se pudo exportar capas', txt)

    def showLayerMap(self):
        if self.canvas is not None:
            layer = self.currentLayer()
            if layer is not None:
                self.veureCapa(layer)
                extent = layer.extent()
                self.canvas.setExtent(extent)
                self.canvas.refresh()

    def showFeatureTable(self):
        if self.atributs is not None:
            layer = self.currentLayer()
            if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
                self.atributs.obrirTaula(layer)
                self.atributs.show()
                self.obertaTaulaAtributs.emit()

    def filterElements(self):
        layer = self.currentLayer()
        if layer is not None and self.atributs is not None:
            self.atributs.filtrarCapa(layer, True)
            # self.actIconaFiltre(layer)
            # try:
            #     dlgFiltre = QgsSearchQueryBuilder(layer)
            #     dlgFiltre.setSearchString(layer.subsetString())
            #     dlgFiltre.exec_()
            #     layer.setSubsetString(dlgFiltre.searchString())
            #     self.actIconaFiltre(layer)
            # except Exception as e:
            #     print(str(e))

    def removeFilter(self):
        layer = self.currentLayer()
        if layer is not None and self.atributs is not None:
            self.atributs.filtrarCapa(layer, False)
            # self.actIconaFiltre(layer)
        # if layer is not None:
        #     layer.setSubsetString('')
        #     self.actIconaFiltre(layer)

    def nodes(self):
        def recurse(parent):
            for child in parent.children():
                yield child
                yield from recurse(child)
        num = self.model.rowCount()
        for row in range(num):
            index = self.model.index(row, 0)
            node = self.model.index2node(index)
            yield node
            yield from recurse(node)

    def nodePerNom(self, nom, filtre='none'):
        if filtre == 'group':
            tipus = QgsLayerTreeNode.NodeGroup
        elif filtre == 'layer':
            tipus = QgsLayerTreeNode.NodeLayer
        else:
            tipus = None
        for node in self.nodes():
            if (tipus is None or tipus == node.nodeType()) and node.name() == nom:
                return node
        return None

    def items(self):
        def recurse(item, level):
            yield QvItemLlegenda(item, level)
            if QgsLayerTree.isLayer(item):
                for cat in self.model.layerOriginalLegendNodes(item):
                    if cat.data(Qt.CheckStateRole) is not None:
                        yield QvItemLlegenda(cat, level + 1)
            for child in item.children():
                yield from recurse(child, level + 1)
        num = self.model.rowCount()
        for row in range(num):
            index = self.model.index(row, 0)
            item = self.model.index2node(index)
            yield from recurse(item, 0)

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox
    from moduls.QvApp import QvApp

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')
        # QvApp().logInici()

        def printCapaActiva():
            cLayer = leyenda.currentLayer()
            if cLayer:
                print('Capa activa:', cLayer.name())
                uri = cLayer.dataProvider().dataSourceUri()
                drive = uri.split(':')[0]
                print('URI:', uri)
                txt = ''
                if win32file.GetDriveType(drive + ':') == win32file.DRIVE_FIXED:
                    txt = '(Disco fijo)'
                print('Disco:', drive, txt)
            else:
                print('Capa activa: None')

        canv = QgsMapCanvas()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib, printCapaActiva)

        leyenda.project.read('D:/qVista/EjemploMapSin.qgs')

    # Al cargar un proyecto o capa:
    # - Ver si tiene filtro de datos para actualizar el icono del embudo
    # - Para las capas raster, ver si funciona el chech/uncheck de la capa para la visualización
    # - Ver si se produce un cambio de escala y restaurarlo
    # Evento: QgsProject -> legendLayersAdded(lista de capas)

        canv.setWindowTitle('Canvas')
        canv.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

    # Acciones personalizadas para menú contextual de la leyenda:
    #
    # - Definición de la acción y del metodo asociado
    # - Se añade la acción a la lista de acciones disponibles (llegenda.accions)
    # - Se redefine la lista de acciones que apareceran en el menú (llegenda.menuAccions)
    #   mediante la señal clicatMenuContexte según el tipo de nodo clicado
    #   (Tipos: none, group, layer, symb)

        # Acciones de usuario

        def openProject():
            dialegObertura = QFileDialog()
            dialegObertura.setDirectoryUrl(QUrl('../dades/projectes/'))
            mapes = "Tots els mapes acceptats (*.qgs *.qgz);; " \
                    "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)"
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis",
                                                      "../dades/projectes/", mapes)
            if nfile != '':
                if leyenda.player is None:
                    leyenda.setPlayer('moduls/giphy.gif', 170, 170)
                leyenda.saveCanvasPosition()
                leyenda.printCanvasPosition('==> projectRead')
                ok = leyenda.project.read(nfile)
                if ok:
                    leyenda.restoreCanvasPosition()
                else:
                    print('Error al cargar proyecto', nfile)
                    print(leyenda.project.error().summary())

        def test():
            QvApp().logRegistre('Menú Test')

            print('Items Llegenda:')
            for item in leyenda.items():
                capa = item.capa()
                if capa is None:
                    nomCapa = '-'
                else:
                    nomCapa = capa.name()
                print('  ' * item.nivell, '-',
                      'Tipo:', item.tipus,
                      'Nivel:', item.nivell,
                      'Capa:', nomCapa,
                      'Nombre:', item.nom(),
                      'Visible:', item.esVisible(),
                      'Marcado:', item.esMarcat())

        def salutacions():
            QMessageBox().information(None, 'qVista', 'Salutacions ' + QvApp().usuari)

        def editable():
            leyenda.editarLlegenda(not leyenda.editable)

        # leyenda.mask = QvMaskLabels(leyenda.capaPerNom("Zones districtes"), 3)
        # leyenda.mask = QvLlegendaMascara(leyenda, leyenda.capaPerNom("Màscara"), 1)

        def testLabels():
            print("Test Labels")
            capa = leyenda.currentLayer()
            if capa is None or capa.type() != QgsMapLayer.VectorLayer:
                return
            print("Capa: {}".format(capa.name()))
            if not capa.labelsEnabled():
                print("- Sin etiquetas")
                return

            on = leyenda.mask.isEnabled(capa)
            if on:
                print("- Activada")
            else:
                print("- No activada")

        def maskLabels():
            capa = leyenda.currentLayer()
            on = leyenda.mask.isEnabled(capa)
            leyenda.mask.switch(capa, not on)
            if leyenda.capaVisible(capa):
                canv.clearCache()
                canv.refresh()

        def maskOn():
            leyenda.mask.maskOn()

        def maskOff():
            leyenda.mask.maskOff()

        # Acciones de usuario para el menú
        act = QAction()
        act.setText("Editable")
        act.triggered.connect(editable)
        leyenda.accions.afegirAccio('editable', act)

        act = QAction()
        act.setText("Test")
        act.triggered.connect(test)
        leyenda.accions.afegirAccio('test', act)

        act = QAction()
        act.setText("Test Labels")
        act.triggered.connect(testLabels)
        leyenda.accions.afegirAccio('testLabels', act)

        act = QAction()
        act.setText("Mask Labels")
        act.triggered.connect(maskLabels)
        leyenda.accions.afegirAccio('maskLabels', act)

        act = QAction()
        act.setText("Mask Labels On")
        act.triggered.connect(maskOn)
        leyenda.accions.afegirAccio('maskOn', act)

        act = QAction()
        act.setText("Mask Labels Off")
        act.triggered.connect(maskOff)
        leyenda.accions.afegirAccio('maskOff', act)

        act = QAction()
        act.setText("Abrir proyecto")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú
        def menuContexte(tipo):
            if tipo == 'layer':
                leyenda.menuAccions.append('testLabels')
                leyenda.menuAccions.append('maskLabels')
            if tipo == 'none':
                leyenda.menuAccions.append('addLayersFromFile')
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('test')
                leyenda.menuAccions.append('testCapas')
                leyenda.menuAccions.append('maskOn')
                leyenda.menuAccions.append('maskOff')
                leyenda.menuAccions.append('editable')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)

        leyenda.projecteModificat.connect(print)

        app.aboutToQuit.connect(QvApp().logFi)
