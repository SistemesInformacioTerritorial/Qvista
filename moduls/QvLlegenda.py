# -*- coding: utf-8 -*-

from qgis.core import (QgsProject, QgsLegendModel, QgsLayerDefinition, QgsMapLayer, QgsVectorLayer,
                       QgsVectorFileWriter, QgsVectorLayerJoinInfo, QgsLayerTree, QgsLayerTreeNode,
                       QgsLayerTreeUtils, QgsVectorDataProvider, QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat)
from qgis.gui import (QgsLayerTreeView, QgsLayerTreeViewMenuProvider, QgsLayerTreeMapCanvasBridge,
                      QgsLayerTreeViewIndicator, QgsLayerTreeViewDefaultActions, QgsGradientColorRampDialog)
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import Qt, pyqtSignal, QUrl
from moduls.QvAccions import QvAccions
from moduls.QvAtributs import QvAtributs
from moduls.QvApp import QvApp
from moduls.QvVideo import QvVideo
from moduls.QvEscala import QvEscala

import os


# Resultado de compilacion de recursos del fuente de qgis (directorio images)
# pyrcc5 images.qrc >images_rc.py
import images_rc  # NOQA


class QvBotoneraLlegenda(QWidget):

    clicatBoto = pyqtSignal(int)

    def __init__(self, llegenda, nom='Llegenda', vertical=True):
        super().__init__()
        self.llegenda = llegenda
        self.items = dict()
        self.botons = dict()
        self.setWindowTitle(nom)
        if vertical:
            self.setLayout(QVBoxLayout())
        else:
            self.setLayout(QHBoxLayout())
        self.funcioFiltre = None
        self.funcioBoto = None

    def afegirBoto(self, item):
        if self.llegenda.editable:
            self.llegenda.editarLlegenda(False)
        boto = QPushButton(item.nom())
        boto.setCheckable(True)
        boto.setChecked(item.esVisible())
        self.layout().addWidget(boto)
        i = self.layout().indexOf(boto)
        self.items[i] = item
        self.botons[i] = boto
        boto.clicked.connect(self.clickBoto)
        return boto

    def esborrarBotonera(self):
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(i))
        self.repaint()
        self.items = dict()
        self.botons = dict()

    def afegirBotonera(self, funcioFiltre=None, funcioBoto=None):
        # Filtro de usuario del itema a añadir a botonera
        if funcioFiltre is not None:
            self.funcioFiltre = funcioFiltre
        # Modificación de usuario del boton generado
        if funcioBoto is not None:
            self.funcioBoto = funcioBoto
        self.esborrarBotonera()
        for item in self.llegenda.items():
            if self.funcioFiltre is None or self.funcioFiltre(item):
                boto = self.afegirBoto(item)
                if self.funcioBoto is not None:
                    self.funcioBoto(boto)

    def actBotons(self):
        for i in range(len(self.botons)):
            self.botons[i].setChecked(self.items[i].esVisible())

    def clickBoto(self):
        boto = self.sender()
        i = self.layout().indexOf(boto)
        item = self.items[i]
        item.veure(not item.esVisible())
        self.actBotons()
        self.clicatBoto.emit(i)


class QvItemLlegenda(object):

    def __init__(self, item, nivell):
        super().__init__()
        self.item = item
        self.nivell = nivell
        self.tipus = self.calcTipus()

    def calcTipus(self):
        clase = type(self.item).__name__
        if clase == 'QgsLayerTreeLayer':
            return 'layer'
        elif clase == 'QgsLayerTreeGroup':
            return 'group'
        elif clase == 'QgsLayerTreeModelLegendNode':
            return 'symb'
        else:
            return 'none'

    def capa(self):
        if self.tipus == 'layer':
            return self.item.layer()
        elif self.tipus == 'group':
            return None
        elif self.tipus == 'symb':
            return self.item.layerNode().layer()
        else:
            return None

    def nom(self):
        if self.tipus in ('layer', 'group'):
            return self.item.name()
        elif self.tipus == 'symb':
            return self.item.data(Qt.DisplayRole)
        else:
            return None

    def esMarcat(self):
        if self.tipus in ('layer', 'group'):
            return self.item.itemVisibilityChecked()
        elif self.tipus == 'symb':
            return self.item.data(Qt.CheckStateRole) != 0
        else:
            return None

    def marcar(self, on=True):
        if self.tipus in ('layer', 'group'):
            self.item.setItemVisibilityChecked(on)
        elif self.tipus == 'symb':
            if on:
                self.item.setData(Qt.Checked, Qt.CheckStateRole)
            else:
                self.item.setData(Qt.Unchecked, Qt.CheckStateRole)

    def esVisible(self):
        if self.tipus in ('layer', 'group'):
            return self.item.isVisible()
        elif self.tipus == 'symb':
            return self.esMarcat() and self.item.layerNode().isVisible()
        else:
            return None

    def veure(self, on=True, children=True):
        if self.tipus in ('layer', 'group'):
            if on:
                self.item.setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.setItemVisibilityCheckedRecursive(True)
            else:
                self.marcar(False)
        elif self.tipus == 'symb':
            self.marcar(on)
            if on:
                self.item.layerNode().setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.layerNode().setItemVisibilityCheckedRecursive(True)


class QvLlegendaModel(QgsLegendModel):
    def __init__(self, root):
        super().__init__(root)
        self.setScale(1.0)

    def setScale(self, scale):
        self.scale = scale

    def data(self, index, role):
        if index.isValid() and role == Qt.ForegroundRole:
            node = self.index2node(index)
            if node is not None and node.nodeType() == QgsLayerTreeNode.NodeLayer:  # and node.isVisible():
                layer = node.layer()
                if layer is not None and layer.hasScaleBasedVisibility():
                    if layer.isInScaleRange(self.scale):
                        color = QColor('#000000')
                    else:
                        color = QColor('#c0c0c0')
                    return color
        return super().data(index, role)


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
        # self.restoreExtent = 0
        # print('restoreExtent', self.restoreExtent)

        self.project.readProject.connect(self.nouProjecte)
        # self.project.loadingLayerMessageReceived.connect(self.msgCapes)

        self.setWhatsThis(QvApp().carregaAjuda(self))

        # Asociar canvas y bridges
        self.mapBridge(canvas)

        # Evento de nueva capa seleccionada
        self.connectaCanviCapaActiva(canviCapaActiva)

        # Model
        self.model = QvLlegendaModel(self.root)
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
        # self.iconaFiltre.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        self.iconaFiltre.setIcon(QIcon('imatges/filter.png'))
        self.iconaFiltre.setToolTip('Filtre actiu')

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
        # self.defActions = QgsLayerTreeViewDefaultActions(self)

    # def msgCapes(self, nomCapa, msgs):
    #     print('Capa:', nomCapa)
    #     for m in msgs:
    #         print(m[0], '-', m[1])

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

    # def iniProjecte(self, num, tot):
    #     # La carga de un proyecto se inicia con la capa #0
    #     self.projecteCapes = [num, tot]
    #     if num == 0:
    #         if self.player is not None:
    #             self.player.show()
    #             self.player.mediaPlayer.play()
    #         self.carregantProjecte.emit()

    # def fiProjecte(self):
    #     # La carga de un proyecto acaba con su visualización en el canvas de todas las capas
    #     num = self.projecteCapes[0]
    #     tot = self.projecteCapes[1]
    #     if num == tot:
    #         self.projecteCapes = [0, 1]
    #         if self.player is not None:
    #             self.player.mediaPlayer.pause()
    #             self.player.hide()
    #         self.projecteCarregat.emit(self.project.fileName())

    def setPlayer(self, fich, ancho=170, alto=170):
        if os.path.isfile(fich):
            self.player = QvVideo(fich, ancho, alto, self.canvas)
        else:
            self.player = None

    # def printSignals(self):
    # void 	loadingLayer (const QString &layerName)
    #  	Emitted when a layer is loaded. More...
    # void 	loadingLayerMessageReceived (const QString &layerName,
    #                                    const QList< QgsReadWriteContext::ReadWriteMessage > &messages)
    #  	Emitted when loading layers has produced some messages. More...
    #     self.canvas.mapCanvasRefreshed.connect(lambda: self.printCanvasPosition('>> Canvas mapCanvasRefreshed'))
    #     self.canvas.extentsChanged.connect(lambda: self.printCanvasPosition('Canvas extentsChanged'))
    #     self.canvas.layersChanged.connect(lambda: self.printCanvasPosition('Canvas layersChanged'))
    #     # self.canvas.renderStarting.connect(lambda: self.printCanvasPosition('Canvas renderStarting'))
    #     self.canvas.renderComplete.connect(lambda: self.printCanvasPosition('Canvas renderComplete'))
    #     self.project.layerLoaded.connect(lambda num, tot: print("Project layerLoaded %d / %d" % (num, tot)))
    #     self.project.readProject.connect(lambda: self.printCanvasPosition('Project readProject'))
    #     self.carregantProjecte.connect(lambda: print('*** Llegenda carregantProjecte'))
    #     self.projecteCarregat.connect(lambda f: print('*** Llegenda projecteCarregat ' + f))

    def deleteCanvasPosition(self):
        self.lastExtent = None

    def saveCanvasPosition(self):
        self.lastExtent = self.canvas.extent()

    def restoreCanvasPosition(self):
        if self.lastExtent is not None:
            self.canvas.setExtent(self.lastExtent)

    #  QgsRectangle r = mapSettings().extent();
    #  r.scale( scaleFactor, center );
    #  setExtent( r, true );

    def printCanvasPosition(self, msg):
        e = round(self.canvas.scale(), 2)
        x = round(self.canvas.center().x(), 2)
        y = round(self.canvas.center().y(), 2)
        print(msg, ':',
              'escala -', str(e),
              'centro: (', str(x),
              '-', str(y), ')')

    #     if msg == 'Canvas layersChanged':
    #         self.saveCanvasPosition()
    #     if msg == '>> Canvas mapCanvasRefreshed' and self.restoreExtent > 0:
    #         self.restoreExtent -= 1
    #         print('restoreExtent', self.restoreExtent)
    #     if msg == 'Canvas extentsChanged':
    #         self.restoreCanvasPosition()
    #     if msg == 'Canvas renderStarting' and self.restoreCanvasPosition():
    #         self.printCanvasPosition('restoreCanvasPosition')

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

    # def dragEnterEvent(self, event):
    #     self.dragFiles = []
    #     self.dragExts = ['.qlr', '.shp', '.csv'] # pueden haber varios
    #     self.dragProj = ['.qgs', '.qgz'] # solo uno
    #     data = event.mimeData()
    #     if data.hasUrls():
    #         for url in data.urls():
    #             fich = url.toLocalFile()
    #             if os.path.isfile(fich):
    #                 _, fext = os.path.splitext(fich)
    #                 if fext.lower() in self.dragExts:
    #                     print('url', fich)
    #                     self.dragFiles.append(fich)
    #     if len(self.dragFiles) > 0:
    #         event.acceptProposedAction()

    # def dragMoveEvent(self, event):
    #     event.acceptProposedAction()

    # def dropEvent(self, event):
    #     print('Abrir ficheros')
    #     event.acceptProposedAction()

    # def dragLeaveEvent(self, event):
    #     self.dragFiles = []
    #     event.accept()

    def connectaEscala(self, escala):
        # print('Cambio escala:', escala)
        self.model.setScale(escala)
        for capa in self.capes():
            if capa.hasScaleBasedVisibility():
                capa.nameChanged.emit()

    def actIconaFiltre(self, capa):
        if capa.type() != QgsMapLayer.VectorLayer:
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

        # Establecer escala inicial
        # print('Escala:', escala)
        # if self.canvas is not None:
        #     self.canvas.zoomScale(escala)

        # print('Capes Llegenda:')
        # for layer in leyenda.capes():
        #     print('-', layer.name(), ', Visible:', leyenda.capaVisible(layer),
        #                              ', Marcada:', leyenda.capaMarcada(layer),
        #                              ', Filtro escala:', layer.hasScaleBasedVisibility())
        #     if layer.type() == QgsMapLayer.VectorLayer:
        #         print(' ', 'Filtro datos:', layer.subsetString())
        #         leyenda.actIconaFiltre(layer)

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
            self.canvas = canvas
            self.bridge = bridge
        else:
            self.bridges.append((canvas, bridge))

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
        act.triggered.connect(self.removeGroupOrLayer)  # No usa defaultActions() porque elimina todos los seleccionados
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

        # act = QAction()
        # act.setText("Afegeix capa CSV")
        # # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))ic_beach_access_black_48dp
        # act.triggered.connect(self.addCustomCSV)
        # self.accions.afegirAccio('addCustomCSV', act)

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
                self.menuAccions += ['addGroup', 'renameGroupOrLayer', 'addLayersFromFile', 'removeGroupOrLayer']
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
        nfile, ok = dlgLayers.getOpenFileName(None, "Afegir Capes Qgis", self.directory, "Capes Qgis (*.qlr)")
        if ok and nfile != '':
            self.directory = os.path.dirname(nfile)
            ok, txt = QgsLayerDefinition.loadLayerDefinition(nfile, self.project, self.root)
            if not ok:
                print('No se pudo importar capas', txt)

    # def addLayersFromFile(self):
    #     dlgLayers = QFileDialog()
    #     nfile, ok = dlgLayers.getOpenFileName(None, "Afegir Capes Qgis", self.directory, "Capes Qgis (*.qlr)")
    #     if ok and nfile != '':
    #         layers = QgsLayerDefinition.loadLayerDefinitionLayers(nfile)
    #         if layers is not None and len(layers) > 0:
    #             loaded = self.project.addMapLayers(layers, True)
    #             if loaded is not None and len(loaded) > 0:
    #                 if set(layers) != set(loaded):
    #                     print('Alguna capa no se pudo cargar')
    #         self.directory = os.path.dirname(nfile)

    # def addCustomCSV(self):
    #     dlgLayers = QFileDialog()
    #     nfile, ok = dlgLayers.getOpenFileName(None, "Afegir Capa CSV", self.directory, "Capes CSV (*.csv)")
    #     if ok and nfile != '':
    #         # uri = 'file:///' + nfile + '?delimiter=;'
    #         # uri = 'file:///' + nfile + '?delimiter=;&crs=epsg:25831&xField=XCalculadaqVista&yField=YCalculadaqVista'
    #         uri = 'file:///' + nfile + '?delimiter=;&crs=epsg:25831&wktField=GEOMETRIA'
    #         layer = QgsVectorLayer(uri, os.path.basename(nfile), 'delimitedtext')
    #         addLayer = self.project.addMapLayer(layer)
    #         if addLayer is None:
    #             print('Error al añadir capa')
    #         self.directory = os.path.dirname(nfile)

    def saveLayersToFile(self):
        nodes = self.selectedNodes()
        if len(nodes) > 0:
            dlgLayers = QFileDialog()
            if self.directory is not None:
                dlgLayers.setDirectory(self.directory)
            nfile, ok = dlgLayers.getSaveFileName(None, "Desar Capes Qgis", self.directory, "Capes Qgis (*.qlr)")
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


class QvMenuLlegenda(QgsLayerTreeViewMenuProvider):

    def __init__(self, llegenda):
        QgsLayerTreeViewMenuProvider.__init__(self)
        self.llegenda = llegenda

    def createContextMenu(self):
        tipo = self.llegenda.setMenuAccions()
        self.llegenda.clicatMenuContexte.emit(tipo)
        return self.llegenda.accions.menuAccions(self.llegenda.menuAccions)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')
        # QvApp().logInici()

        def printCapaActiva():
            cLayer = leyenda.currentLayer()
            if cLayer:
                print('Capa activa:', leyenda.currentLayer().name())
            else:
                print('Capa activa: None')

        canv = QgsMapCanvas()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib, printCapaActiva)
        # leyenda.printSignals() # Para debug

        # leyenda.project.read('../Dades/Projectes/Imatge satel·lit 2011 AMB.qgs')
        leyenda.project.read('../dades/projectes/bcn11.qgs')
        # leyenda.project.read('../dades/projectes/Prototip GUIA OracleSpatial_WMS.qgz')

    # Al cargar un proyecto o capa:
    # - Ver si tiene filtro de datos para actualizar el icono del embudo
    # - Para las capas raster, ver si funciona el chech/uncheck de la capa para la visualización
    # - Ver si se produce un cambio de escala y restaurarlo
    # Evento: QgsProject -> legendLayersAdded(lista de capas)

        canv.setWindowTitle('Canvas')
        canv.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        #
        # Funciones de capes:
        # capes(), capaPerNom(), veureCapa(), capaVisible(), capaMarcada(), currentLayer(), setCurrentLayer()
        #
        #
        # Funciones de nodes:
        # nodes(), nodePerNom(), node.isVisible(), node.itemVisibilityChecked()
        #

        # leyenda.veureCapa(leyenda.capaPerNom('BCN_Barri_ETRS89_SHP'), True)
        # leyenda.veureCapa(leyenda.capaPerNom('BCN_Districte_ETRS89_SHP'), False)
        # leyenda.veureCapa(leyenda.capaPerNom('BCN_Illes_ETRS89_SHP'), True)

        # leyenda.setCurrentLayer(leyenda.capaPerNom('BCN_Barri_ETRS89_SHP'))

        # Acciones personalizadas para menú contextual de la leyenda:
        #
        # - Definición de la acción y del metodo asociado
        # - Se añade la acción a la lista de acciones disponibles (llegenda.accions)
        # - Se redefine la lista de acciones que apareceran en el menú (llegenda.menuAccions)
        #   mediante la señal clicatMenuContexte según el tipo de nodo clicado
        #   (Tipos: none, group, layer, symb)

        # Generación de botoneras de leyenda
        def filtroBotonera(item):
            return item.tipus in ('layer', 'group')

        def filtroRangos(item):
            return item.tipus in ('symb')

        def modifBoton(boton):
            boton.setFlat(True)

        def botonCapa(i):
            if leyenda.capaVisible(leyenda.capaPerNom('BCN_Districte_ETRS89_SHP')):
                testSimbologia()
            else:
                if rangos is not None:
                    rangos.close()

        botonera = None
        rangos = None

        # Acciones de usuario

        def openProject():
            dialegObertura = QFileDialog()
            dialegObertura.setDirectoryUrl(QUrl('../dades/projectes/'))
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis", "../dades/projectes/",
                                                      "Tots els mapes acceptats (*.qgs *.qgz);; " +
                                                      "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)")
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

        def testCapas():
            global botonera
            botonera = QvBotoneraLlegenda(leyenda, 'Botonera')
            botonera.afegirBotonera(filtroBotonera, modifBoton)
            botonera.clicatBoto.connect(botonCapa)
            botonera.show()
            if leyenda.capaVisible(leyenda.capaPerNom('BCN_Districte_ETRS89_SHP')):
                testSimbologia()

        def testSimbologia():
            global rangos
            rangos = QvBotoneraLlegenda(leyenda, 'Rangos', False)
            rangos.afegirBotonera(filtroRangos, modifBoton)
            rangos.show()

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
            if leyenda.editable:
                if rangos is not None:
                    rangos.close()
                if botonera is not None:
                    botonera.close()

        def testMapificacio():
            from moduls.QvMapificacio import QvMapificacio

            z = QvMapificacio('CarrecsANSI_BARRI.csv', 'Barri')

            # z = QvMapificacio('D:/qVista/CarrecsANSI.csv', 'Barri')
            # print(z.rows, 'filas en', z.fDades)
            # print('Muestra:', z.mostra)

            # camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
            # z.zonificacio(camps,
            #     afegintZona=lambda n: print('... Procesado', str(n), '% ...'),
            #     errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            #     zonaAfegida=lambda n: print('Zona', z.zona, 'procesada en', str(n), 'segs. en ' + z.fZones + ' -', str(z.rows), 'registros,', str(z.errors), 'errores'))

            z.agregacio('Càrrecs per Barri', 'Recompte')

            z.agregacio('Recaudació urbans (milers €)', 'Suma',
                        campAgregat="QUOTA_TOTAL / 1000",
                        filtre="TIPUS_DE_BE = 'UR'",
                        colorBase='Taronja')

            z.agregacio('Valor cadastral m2 (€)', 'Mitjana',
                        campAgregat="V_CAD_ANY_ACTUAL / SUPERFICIE",
                        colorBase='Verd')

        def testJoin():

            import sys
            import csv
            import time
            from moduls.QvSqlite import QvSqlite

            ruta = 'D:/qVista/'
            fich = 'CarrecsANSI'
            code = 'ANSI'
            camp = 'BARRI'
            showErrors = False

            # TODO: Método de cálculo de zonas de Geocod
            # TODO: Probar la geocodificación en una layer directamente

            # ini = time.time()

            # # Fichero de salida de errores
            # # sys.stdout = open(ruta + fich + '_ERR.txt', 'w')
            # print('*** FICHERO:', fich)

            # # Fichero CSV de entrada
            # with open(ruta + fich + '.csv', encoding=code) as csvInput:

            #     # Fichero CSV de salida con columna extra
            #     with open(ruta + fich + '_' + camp + '.csv', 'w', encoding=code) as csvOutput:

            #         # Cabeceras
            #         data = csv.DictReader(csvInput, delimiter=';')
            #         fields = data.fieldnames
            #         fields.append('QVISTA_' + camp)

            #         writer = csv.DictWriter(csvOutput, fieldnames=fields, lineterminator='\n')
            #         writer.writeheader()

            #         # Lectura de filas y geocodificación
            #         tot = num = 0
            #         dbgeo = QvSqlite()
            #         for row in data:
            #             tot += 1
            #             val = dbgeo.geoCampCarrerNum(camp, '', row['NOM_CARRER_GPL'], row['NUM_I_GPL'], '', row['NUM_F_GPL'], '')
            #             # Error en geocodificación
            #             if val is None:
            #                 num += 1
            #                 print('- ERROR', '|', row['NFIXE'], row['NOM_CARRER_GPL'], row['NUM_I_GPL'], '', row['NUM_F_GPL'])

            #             # Escritura de fila con X e Y
            #             row.update([('QVISTA_' + camp, val)])
            #             writer.writerow(row)

            #     fin = time.time()
            #     print('==> REGISTROS:', str(tot), '- ERRORES:', str(num))
            #     print('==> TIEMPO:', str(fin - ini), 'segundos')

            # print(QgsVectorDataProvider.availableEncodings())
            # ANSI / ISO-8859-1 / latin1
            # CP1252 /  windows-1252
            # UTF-8

            vectorLyr = QgsVectorLayer('D:/qVista/Barris.sqlite', 'Barris' , "ogr")
            vectorLyr.setProviderEncoding("UTF-8")
            if vectorLyr.isValid():
                leyenda.project.addMapLayer(vectorLyr, True)


            infoLyr = QgsVectorLayer(ruta + fich + '_' + camp + '.csv', fich , "ogr")
            infoLyr.setProviderEncoding("System")
            if infoLyr.isValid():
                leyenda.project.addMapLayer(infoLyr, False)

            tipusJoin = 'left' if showErrors else 'inner'

            # Nombre fichero antes de ?quuery= !!!!!
            vlayer = QgsVectorLayer( "?query="
               "select C.NUM_CARRECS, B.CODI_BARRI, B.NOM_BARRI, B.DISTRICTE, B.GEOMETRY as GEOM from "
                "(select count(*) AS NUM_CARRECS, QVISTA_BARRI from " + fich + " group by "
                "QVISTA_BARRI) as C " + tipusJoin + " join "
                "Barris as B on C.QVISTA_BARRI = B.CODI_BARRI", "CarrecsBarriGroup", "virtual" )
            #    "select C.NUM_CARRECS, C.TIPUS_PROPI, C.DESC_TIPUS_PROPI, B.CODI_BARRI, B.NOM_BARRI, B.DISTRICTE, B.GEOMETRY as GEOM from "
            #     "(select count(*) AS NUM_CARRECS, QVISTA_BARRI, TIPUS_PROPI, DESC_TIPUS_PROPI from " + fich + " group by "
            #     "QVISTA_BARRI, TIPUS_PROPI, DESC_TIPUS_PROPI) as C " + tipusJoin + " join "
            #     "Barris as B on C.QVISTA_BARRI = B.CODI_BARRI", "CarrecsBarriGroup", "virtual" )
            vlayer.setProviderEncoding("UTF-8")            
            if not vlayer.isValid():
                return

            QgsVectorFileWriter.writeAsVectorFormat(vlayer, "D:/qVista/CarrecsBarriGroup.sqlite", "UTF-8", vectorLyr.crs(), "SQLite")
            leyenda.project.removeMapLayer(infoLyr.id())

            joinLyr = QgsVectorLayer('D:/qVista/CarrecsBarriGroup.sqlite', 'Càrrecs per Barri' , "ogr")
            joinLyr.setProviderEncoding("UTF-8")
            if joinLyr.isValid():

                field = "NUM_CARRECS"

            #     minRango, _ = joinLyr.aggregate(QgsAggregateCalculator.Min, 'NUM_CARRECS')
            #     maxRango, _ = joinLyr.aggregate(QgsAggregateCalculator.Max, 'NUM_CARRECS')

            # # TODO: Método de simbología por rangos
            # # TODO: Calcular valores mínimo y máximo y step correspondiente para un número de elementos

            #     elements = [
            #         ("Menys de 1000", 0.0, 1000.0),
            #         ("1000 - 2000", 1000.0, 2000.0),
            #         ("2000 - 3000", 2000.0, 3000.0),
            #         ("3000 - 4000", 3000.0, 4000.0),
            #         ("Més de 4000", 4000.0, 5000.0)
            #     ]

            #     categories = []

            #     total = len(elements)
            #     step = 256 // total
            #     color = QColor(0, 128, 255)
            #     alpha = 0

            #     for label, lower, upper in elements:
            #         sym = QgsSymbol.defaultSymbol(joinLyr.geometryType())
            #         if alpha == 0:
            #             alpha += step // 2
            #             primero = False
            #         else:
            #             alpha += step
            #         color.setAlpha(alpha)
            #         sym.setColor(color)
            #         category = QgsRendererRange(lower, upper, sym, label)
            #         categories.append(category)

                # renderer = QgsGraduatedSymbolRenderer(field, categories)
                
                
                # QgsGradientColorRampDialog 

                numItems = 5
                numDecimals = 0
                iniAlpha = 8
                symbol = QgsSymbol.defaultSymbol(joinLyr.geometryType())
                colorRamp = QgsGradientColorRamp(QColor(0, 128, 255, iniAlpha),
                                                 QColor(0, 128, 255, 255 - iniAlpha))
                    # , 'stops':'0.25;255,255,0,255:0.50;0,255,0,255:0.75;0,255,255,255')
                # QgsGradientColorRampDialog(colorRamp)
                format = QgsRendererRangeLabelFormat('%1 - %2', numDecimals)
                renderer = QgsGraduatedSymbolRenderer.createRenderer(joinLyr, field, numItems,
                    QgsGraduatedSymbolRenderer.Pretty, symbol, colorRamp, format)

                joinLyr.setRenderer(renderer)
                leyenda.project.addMapLayer(joinLyr, True) 

            # TODO: Método de simbología por categorías

                # elements = {
                #     "0001": (QColor(0, 128, 255, 21), "Tipus 1"),
                #     "0002": (QColor(0, 128, 255, 63), "Tipus 2"),
                #     "0003": (QColor(0, 128, 255, 105), "Tipus 3"),
                #     "0004": (QColor(0, 128, 255, 147), "Tipus 4"),
                #     "0005": (QColor(0, 128, 255, 189), "Tipus 5"),
                #     "0006": (QColor(0, 128, 255, 231), "Tipus 6"),
                # }

                # categories = []
                # for num, (color, label) in elements.items():
                #     sym = QgsSymbol.defaultSymbol(joinLyr.geometryType())
                #     sym.setColor(color)
                #     category = QgsRendererCategory(num, sym, label)
                #     categories.append(category)

                # field = "TIPUS_PROPI"
                # renderer = QgsCategorizedSymbolRenderer(field, categories)
                # joinLyr.setRenderer(renderer)


                # elements = {
                #     "1": ("yellow"  , "1 càrrec"),
                #     "2": ("darkcyan", "2 càrrecs"),
                #     "3": ("green"   , "3 càrrecs")
                # }

                # elements = {
                #     "1": (QColor(0, 128, 255, 43), "1 càrrec"),
                #     "2": (QColor(0, 128, 255, 128), "2 càrrecs"),
                #     "3": (QColor(0, 128, 255, 213), "3 càrrecs")
                # }

                # categories = []
                # for num, (color, label) in elements.items():
                #     sym = QgsSymbol.defaultSymbol(joinLyr.geometryType())
                #     # sym.setColor(QColor(color))
                #     sym.setColor(color)
                #     category = QgsRendererCategory(num, sym, label)
                #     categories.append(category)

                # field = "NUM_CARRECS"
                # renderer = QgsCategorizedSymbolRenderer(field, categories)
                # joinLyr.setRenderer(renderer)

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
        act.setText("Test Botonera")
        act.triggered.connect(testCapas)
        leyenda.accions.afegirAccio('testCapas', act)

        act = QAction()
        act.setText("Test Simbologia")
        act.triggered.connect(testSimbologia)
        leyenda.accions.afegirAccio('testSimbologia', act)

        act = QAction()
        act.setText("Test Join")
        act.triggered.connect(testJoin)
        leyenda.accions.afegirAccio('testJoin', act)

        act = QAction()
        act.setText("Test Mapificacio")
        act.triggered.connect(testMapificacio)
        leyenda.accions.afegirAccio('testMapificacio', act)

        act = QAction()
        act.setText("Abrir proyecto")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú
        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('addLayersFromFile')
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('test')
                leyenda.menuAccions.append('testCapas')
                # leyenda.menuAccions.append('testSimbologia')
                leyenda.menuAccions.append('testJoin')
                leyenda.menuAccions.append('testMapificacio')
                leyenda.menuAccions.append('editable')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)

        leyenda.projecteModificat.connect(print)

        app.aboutToQuit.connect(QvApp().logFi)

    #######

        # QgsLayerTreeNode --> nameChanged()

        # from qgis.gui import QgsCategorizedSymbolRendererWidget
        # from qgis.core import QgsStyle

        # layer = llegenda.currentLayer()
        # renderer = layer.renderer()
        # cats = QgsCategorizedSymbolRendererWidget(layer, QgsStyle.defaultStyle(), renderer)
        # cats.show()
        # cats.applyChanges()
