# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvAccions import QvAccions
from moduls.QvAtributs import QvAtributs
from moduls.QvVideo import QvVideo
from moduls.QvEscala import QvEscala
from moduls.QvMapForms import QvFormSimbMapificacio
from moduls.QvLlegendaAux import QvModelLlegenda, QvItemLlegenda, QvMenuLlegenda, QvRecarregaLlegenda
from moduls.QvLlegendaMascara import QvLlegendaMascara
from moduls.QvDiagrama import QvDiagrama
from moduls.QvTema import QvTema
from moduls.QvAnotacions import QvMapToolAnnotation
from moduls.QvCatalegCapes import QvCreadorCatalegCapes
from moduls.QvDigitizeContext import QvDigitizeContext
from moduls.QvReports import QvReports
# from moduls.QvProcessing import QvProcessing
from moduls.QvProviders import QvProjectProvider
from moduls.QvNavegacioTemporal import QvNavegacioTemporal
from moduls.QvApp import QvApp
from moduls import QvFuncions

if QvApp().testVersioQgis(3, 10):
    from moduls.QvDigitize import QvDigitize

from configuracioQvista import imatgesDir

import os

# Resultado de compilacion de recursos del fuente de qgis (directorio images)
# pyrcc5 images.qrc >images_rc.py
import images_rc  # NOQA
    
TITOL_INICIAL = 'Llegenda'


class QvLlegenda(qgGui.QgsLayerTreeView):

    obertaTaulaAtributs = qtCor.pyqtSignal()
    clicatMenuContexte = qtCor.pyqtSignal(str)
    carregantProjecte = qtCor.pyqtSignal()
    projecteCarregat = qtCor.pyqtSignal(str)
    projecteModificat = qtCor.pyqtSignal(str)

    def __init__(self, canvas=None, atributs=None, canviCapaActiva=None,
                 anotacions=True, editable=True):
        qgGui.QgsLayerTreeView.__init__(self)

        # OJO: la inicialización en QGIS se realiza en: QgisApp::initLayerTreeView()

        self.setTitol()
        self.project = qgCor.QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.canvas = None
        self.bridge = None
        self.bridges = []
        self.atributs = atributs
        if self.atributs is not None:
            self.atributs.llegenda = self
        self.editable = editable
        self.lastExtent = None
        self.escales = None
        self.directory = '.'
        self.renaming = None
        self.mask = None
        self.removing = False
        self.tema = QvTema(self)
        self.anotacions = None
        self.menuEdicio = None
        # self.restoreExtent = 0
        # print('restoreExtent', self.restoreExtent)

        self.reports = QvReports(self)
        self.recarrega = QvRecarregaLlegenda(self)
        
        # L'opertura de projectes Oracle va lenta si és la primera
        # Obrim un arxiu "inútil", i així s'obren més ràpid
        if self.project.homePath()=='':
            try:
                self.project.read('mapesOffline/accelerator.qgs')
            except:
                pass
        self.project.readProject.connect(self.nouProjecte)
        self.project.legendLayersAdded.connect(self.actIcones)
        self.root.layerOrderChanged.connect(self.actIcones)
        # self.project.loadingLayerMessageReceived.connect(self.msgCapes)

        # self.setWhatsThis(QvApp().carregaAjuda(self))

        # Asociar canvas y bridges; digitalización
        self.mapBridge(canvas)
        if QvApp().testVersioQgis(3, 10):
            self.digitize = QvDigitize(self)
        else:
            self.digitize = None

        # Evento de nueva capa seleccionada
        self.connectaCanviCapaActiva(canviCapaActiva)

        # Model
        self.model = QvModelLlegenda(self.root)
        self.model.setFlag(qgCor.QgsLegendModel.ShowLegend, True)
        self.model.setFlag(qgCor.QgsLegendModel.ShowLegendAsTree, True)
        if QvApp().testVersioQgis(3, 10):
            self.model.setFlag(qgCor.QgsLegendModel.UseTextFormatting, True)
        self.editarLlegenda()
        self.setModel(self.model)
        self.model.dataChanged.connect(self.itemChanged)

        if self.canvas is not None:
            self.canvas.scaleChanged.connect(self.connectaEscala)
            # Anotaciones (solo a partir de la versión 3.10)
            if anotacions and QvApp().testVersioQgis(3, 10):
                self.anotacions = QvMapToolAnnotation(self)

        # Lista de acciones que apareceran en el menú
        self.menuAccions = []
        # Acciones disponibles
        self.accions = QvAccions()
        self.setAccions()
        if self.editable:
            self.setMenuProvider(QvMenuLlegenda(self))
        else:
            self.setMenuProvider(None)

        self.iconaFiltre = qgGui.QgsLayerTreeViewIndicator()
        self.iconaFiltre.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'filter.png')))
        self.iconaFiltre.setToolTip('Filtre actiu')
        self.iconaFiltre.clicked.connect(self.filterElements)

        self.iconaRecarregaD = qgGui.QgsLayerTreeViewIndicator()
        self.iconaRecarregaD.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'update_time.png')))
        self.iconaRecarregaD.setToolTip('Recàrrega automàtica de dades')

        self.iconaRecarregaG = qgGui.QgsLayerTreeViewIndicator()
        self.iconaRecarregaG.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'update_time.png')))
        self.iconaRecarregaG.setToolTip('Recàrrega gràfica automàtica')

        self.iconaRecarregaDG = qgGui.QgsLayerTreeViewIndicator()
        self.iconaRecarregaDG.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'update_time.png')))
        self.iconaRecarregaDG.setToolTip('Recàrrega automàtica de dades i gràfica')

        self.iconaTemporal = qgGui.QgsLayerTreeViewIndicator()
        self.iconaTemporal.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'temporal.png')))
        self.iconaTemporal.setToolTip('Navegació temporal')
        self.iconaTemporal.clicked.connect(QvNavegacioTemporal.switch)

        self.iconaMap = qgGui.QgsLayerTreeViewIndicator()
        self.iconaMap.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'categories2.png')))
        self.iconaMap.setToolTip('Categories de mapificació')
        self.iconaMap.clicked.connect(lambda: QvFormSimbMapificacio.executa(self))

        self.iconaRequired = qgGui.QgsLayerTreeViewIndicator()
        self.iconaRequired.setIcon(qtGui.QIcon(':/images/themes/default/mIndicatorNonRemovable.svg'))
        self.iconaRequired.setToolTip('Capa necessària per al mapa')

        self.iconaEditForm = qgGui.QgsLayerTreeViewIndicator()
        self.iconaEditForm.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_form.png')))
        self.iconaEditForm.setToolTip('Capa amb modificació de la fitxa dels elements')

        if self.digitize is not None:
            self.iconaEditOff = qgGui.QgsLayerTreeViewIndicator()
            self.iconaEditOff.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_off.png')))
            self.iconaEditOff.setToolTip('Inicia edició')
            self.iconaEditOff.clicked.connect(lambda: self.digitize.activaCapa(True))
                        
            self.iconaEditOn = qgGui.QgsLayerTreeViewIndicator()
            self.iconaEditOn.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_on.png')))
            self.iconaEditOn.setToolTip('Finalitza edició')
            self.iconaEditOn.clicked.connect(lambda: self.digitize.activaCapa(False))

            self.iconaEditMod = qgGui.QgsLayerTreeViewIndicator()
            self.iconaEditMod.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_mod.png')))
            self.iconaEditMod.setToolTip('Finalitza edició')
            self.iconaEditMod.clicked.connect(lambda: self.digitize.activaCapa(False))

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

        # ANULADO
        # Emitted when the set of layers (or order of layers) visible in the canvas changes. 
        # self.fSignal = lambda: self.projecteModificat.emit('canvasLayersChanged')

        self.iniSignal = False

    def qVista(self):
        try:
            return self.parent().parent()
        except:
            return None

    def editing(self, capa):
        if self.digitize is not None:
            return self.digitize.editing(capa)
        else:
            return False

    def edition(self, capa):
        if self.digitize is not None:
            return self.digitize.edition(capa)
        else:
            return None

    def msgErrorlayers(self):
        msg = ''
        try:
            for capa in self.capes():
                if not capa.isValid():
                    msg += '- Capa ' + capa.name()
                    err = capa.error()
                    if err.isEmpty():
                        msg += '\n'
                    else:
                        msg += ':\n' + err.summary() + '\n'
                    p = capa.dataProvider()
                    if p is not None and not p.isValid():
                        msg += p.lastError() + '\n'
        except:
            msg = ''
        return msg
    

    # 
    def readProject(self, fileName):
        """
        Lee proyecto dentro de qVista
        """
        self.recarrega.resetTimers()
        if self.anotacions is not None:
            self.anotacions.removeAnnotations()
        self.project.read(fileName)
        self.projectMacros('qVopenProject')
        msg = self.msgErrorlayers()
        if msg:
            qtWdg.QMessageBox.warning(self, "Capes amb errors", msg)
            return False
        return True

    # Macros de proyecto: openProject()
    # - Para que actúe solo desde QGIS, codificar solo openProject():
    #   def openProject():
    #       [código que puede usar iface]
    # - Para que actúe solo desde qVista, codificar solo qVopenProject():
    #   def openProject():
    #       pass
    #   ...
    #   def qVopenProject():
    #       [código sin iface]
    # - Para que actúe igual tanto en QGIS como en qVista, codificar función qVopenProject() y llamarla desde openProject()
    #   def openProject():
    #       qVopenProject()
    #   ...
    #   def qVopenProject():
    #       [código sin iface]
    # - Por último, también podrían actuar las dos con comportamientos diferentes
    def projectMacros(self, funcion):
        rc = False
        try:
            macros, ok = self.project.readEntry("Macros", "/pythonCode")
            if ok and funcion in macros:
                ret = qtWdg.QMessageBox.question(self, 'Atenció: macro de Python',
                                                 "Aquest mapa conté una macro amb un programa Python.\n\n" \
                                                 "Si esteu segur de que s'executi, premeu 'Sí'.\n" \
                                                 "Si en teniu dubtes, premeu 'No' i consulteu l'equip de suport de qVista.",
                                                 defaultButton=qtWdg.QMessageBox.No)
                if ret == qtWdg.QMessageBox.Yes:
                    exec(macros)
                    f = locals().get(funcion, '')
                    if str(type(f)) == "<class 'function'>":
                        exec(funcion + '()')
                        rc = True
        except Exception as e:
            print(str(e))
        finally:
            return rc

    def setTitol(self, titol=TITOL_INICIAL):
        self.setWindowTitle(titol)
        if self.parent() is not None:
            self.parent().setWindowTitle(titol)

    def modificacioProjecte(self, txt='layersChanged'):

        # Emite señal cuando hay cambios en los filtros y:
        #
        #                |  Grupo  |  Capa  | Anotación
        # ---------------+---------+--------+-----------
        # Alta           |    X    |   X    |     X     
        # Modificación   |    X    |   X    |     X     
        # Movimiento     |   (*)   |   X    |     X     
        # Visibilidad    |   (*)   |   X    |     X     
        # Borrado        |    X    |   X    |     X     
        # 
        # (*) - Solo cuando el cambio en el grupo
        #       afecta también a alguna capa

        if self.iniSignal:
            # print('-> Emit projecteModificat', txt)
            self.projecteModificat.emit(txt)

    def iniProjecte(self, num, tot):
        # La carga de un proyecto se inicia con la capa #0
        if self.iniSignal:
            # self.bridge.canvasLayersChanged.disconnect(self.fSignal)
            # self.project.layerLoaded.disconnect(self.modificacioProjecte)
            # self.project.layerRemoved.disconnect(self.modificacioProjecte)
            self.canvas.layersChanged.disconnect(self.modificacioProjecte)
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
                # self.bridge.canvasLayersChanged.connect(self.fSignal)
                # self.project.layerLoaded.connect(self.modificacioProjecte)
                # self.project.layerRemoved.connect(self.modificacioProjecte)
                self.canvas.layersChanged.connect(self.modificacioProjecte)
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

    def editarLlegenda(self, on=None):
        if on is None: on = self.editable
        self.model.setFlag(qgCor.QgsLegendModel.AllowNodeReorder, on)
        self.model.setFlag(qgCor.QgsLegendModel.AllowNodeRename, on)
        self.model.setFlag(qgCor.QgsLegendModel.AllowLegendChangeState, on)
        self.model.setFlag(qgCor.QgsLegendModel.AllowNodeChangeVisibility, True) # Siempre True
        self.model.setFlag(qgCor.QgsLegendModel.DeferredLegendInvalidation, on)
        # self.setAcceptDrops(on)
        # # self.setDropIndicatorShown(on)
        # print('acceptDrops', self.acceptDrops())

    def connectaEscala(self, escala):
        # print('Cambio escala:', escala)
        self.model.setScale(escala)
        b = self.iniSignal
        self.iniSignal = False
        for capa in self.capes():
            if capa.hasScaleBasedVisibility():
                capa.nameChanged.emit()
        self.iniSignal = b

    def capaLocal(self, capa):
        try:
            uri = capa.dataProvider().dataSourceUri()
            drive = uri.split(':')[0]
            return QvFuncions.isDriveFixed(drive)
        except Exception:
            return False

    def actIconesCapa(self, capa, modif=True):
        if not self.editable: return
        if capa is not None and capa.type() == qgCor.QgsMapLayer.VectorLayer:
            node = self.root.findLayer(capa.id())
            if node is not None:
                self.removeIndicator(node, self.iconaFiltre)
                self.removeIndicator(node, self.iconaRecarregaD)
                self.removeIndicator(node, self.iconaRecarregaG)
                self.removeIndicator(node, self.iconaRecarregaDG)
                self.removeIndicator(node, self.iconaTemporal)
                self.removeIndicator(node, self.iconaMap)
                self.removeIndicator(node, self.iconaRequired)
                self.removeIndicator(node, self.iconaEditForm)
                if self.digitize is not None:
                    self.removeIndicator(node, self.iconaEditOn)
                    self.removeIndicator(node, self.iconaEditOff)
                    self.removeIndicator(node, self.iconaEditMod)
                # Requerida
                if not self.isLayerRemovable(capa):
                    self.addIndicator(node, self.iconaRequired)
                # Filtro
                if capa.subsetString() != '':
                    self.addIndicator(node, self.iconaFiltre)
                # Recarga automática
                rd = self.recarrega.isUpdateDataLayer(capa)
                rg = self.recarrega.isUpdateGraphLayer(capa)
                if rd:
                    if rg:
                        self.addIndicator(node, self.iconaRecarregaDG)
                    else:
                        self.addIndicator(node, self.iconaRecarregaD)
                else:
                    if rg:
                        self.addIndicator(node, self.iconaRecarregaG)
                # Navegación temporal
                if QvNavegacioTemporal.isActive(capa):
                    self.addIndicator(node, self.iconaTemporal)
                # Mapificación
                var = QvDiagrama.capaAmbMapificacio(capa)
                if var is not None and self.capaLocal(capa) and self.editable:
                    self.addIndicator(node, self.iconaMap)
                # Edición
                if self.digitize is not None:
                    estado, df = self.digitize.infoCapa(capa)
                    if estado is not None:
                        if estado:
                            if df.modified():
                                self.addIndicator(node, self.iconaEditMod)
                            else:
                                self.addIndicator(node, self.iconaEditOn)
                        else:
                            self.addIndicator(node, self.iconaEditOff)
                # Modificación atributos
                if self.isLayerEditForm(capa):
                    self.addIndicator(node, self.iconaEditForm)
                if modif:
                    capa.nameChanged.emit()

    def actIcones(self):
        if self.removing:
            return
        for capa in self.capes():
            self.actIconesCapa(capa, False)

    def actIconaFiltre(self, capa):
        self.actIconesCapa(capa)
        self.modificacioProjecte('filterModified')

    def mapaEditable(self):
        if self.digitize and self.digitize.editable():
            return True
        return False

    def botoQgisVisible(self, visible):
        qV = self.qVista()
        if qV is not None:
            try:
                qV.botoObrirQGis.setEnabled(visible)
                qV.botoObrirQGis.setVisible(visible)
            except:
                pass

    def menuEdicioVisible(self, visible=None):
        if visible is None:               
            visible = self.mapaEditable()
        if self.menuEdicio is not None:
            self.menuEdicio.menuAction().setEnabled(visible)
            self.menuEdicio.menuAction().setVisible(visible)
        return visible

    def setMenuEdicio(self, menu):
        if self.digitize is not None:
            self.menuEdicio = self.digitize.setMenu(menu)
        self.menuEdicioVisible(False)

    def nouProjecte(self, doc):
        # Lee modelos de proyecto
        QvProjectProvider.readProject(doc)

        self.setTitol()
        # Borrar tabs de atributos si existen
        if self.atributs is not None:
            self.atributs.deleteTabs()
            if self.atributs.parent() is not None:
                self.atributs.parent().close()

        self.escales.nouProjecte(self.project)

        if self.digitize is not None:
            self.digitize.nouProjecte()

        for capa in self.capes():
            # if layer.type() == qgCor.QgsMapLayer.VectorLayer:
            #     self.actIconaFiltre(layer)

            if self.digitize is not None:
                self.digitize.altaInfoCapa(capa)

            if self.capaMarcada(capa) and (capa.type() == qgCor.QgsMapLayer.RasterLayer or capa.providerType() == "WFS"):
                node = self.root.findLayer(capa.id())
                # self.restoreExtent = 2
                # print('restoreExtent', self.restoreExtent)
                # node.visibilityChanged.connect(self.restoreCanvasPosition)
                # self.restoreCanvasPosition()
                node.setItemVisibilityChecked(False)
                # # self.restoreCanvasPosition()
                node.setItemVisibilityChecked(True)

        visible = self.menuEdicioVisible()
        self.botoQgisVisible(not visible)

        self.tema.temaInicial()

        self.recarrega.autoRecarrega()

    def connectaCanviCapaActiva(self, canviCapaActiva):
        if canviCapaActiva is not None:
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
        bridge = qgGui.QgsLayerTreeMapCanvasBridge(self.root, canvas)
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
        canvas.setSegmentationToleranceType(qgCor.QgsAbstractGeometry.MaximumAngle)

    def isFeatureVisible(self, renderer, ctx, feature):
        ctx.expressionContext().setFeature(feature)
        return renderer.willRenderFeature(feature, ctx)
        # return renderer.capabilities().testFlag(qgCor.QgsFeatureRenderer.Filter) or renderer.willRenderFeature(feature, ctx)

    def getLayerVisibleFeatures(self, layer, selected=True, request=qgCor.QgsFeatureRequest(), max=0):
    # Iterador de elementos de capa visibles
        num = 0
        if layer.type() != qgCor.QgsMapLayerType.VectorLayer: return None
        # if self.canvas is not None and layer.hasScaleBasedVisibility() and not layer.isInScaleRange(self.canvas.scale()): return None
        renderer = layer.renderer()
        if renderer is None:
            return None
        try:
            renderer = renderer.clone()
        except Exception as e:
            print(str(e))
            return None
        ctx = qgCor.QgsRenderContext()
        renderer.startRender(ctx, qgCor.QgsFields())
        if selected:
            iterator = layer.getSelectedFeatures
        else:
            iterator = layer.getFeatures
        for feature in iterator(request):
            if self.isFeatureVisible(renderer, ctx, feature):
                yield feature
                num += 1
                if max > 0 and num >= max: break
        renderer.stopRender(ctx)

    def numLayerVisibleFeatures(self, layer, selected=True, request=qgCor.QgsFeatureRequest()):
    # Contador de elementos de capa visibles
        num = 0
        if layer.type() != qgCor.QgsMapLayerType.VectorLayer: return num
        # if self.canvas is not None and layer.hasScaleBasedVisibility() and not layer.isInScaleRange(self.canvas.scale()): return num
        renderer = layer.renderer()
        if renderer is None:
            return num
        else:
            renderer = renderer.clone()
        ctx = qgCor.QgsRenderContext()
        renderer.startRender(ctx, qgCor.QgsFields())
        if selected:
            iterator = layer.getSelectedFeatures
        else:
            iterator = layer.getFeatures
        for feature in iterator(request):
            if self.isFeatureVisible(renderer, ctx, feature):
                num += 1
        renderer.stopRender(ctx)
        return num

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

    def capaVisible(self, capa, escala=True):
        node = self.root.findLayer(capa.id())
        if node is not None:
            v = node.isVisible()
            if escala:
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
        act = qtWdg.QAction()
        act.setText("Expandir llegenda")
        act.triggered.connect(self.expandLegend)
        self.accions.afegirAccio('expandLegend', act)

        act = qtWdg.QAction()
        act.setText("Contraure llegenda")
        act.triggered.connect(self.collapseLegend)
        self.accions.afegirAccio('collapseLegend', act)

        act = qtWdg.QAction()
        act.setText("Defineix grup")
        act.triggered.connect(self.addGroup)
        self.accions.afegirAccio('addGroup', act)

        act = qtWdg.QAction()
        act.setText("Afegeix capes Qgis")
        act.triggered.connect(self.addLayersFromFile)
        self.accions.afegirAccio('addLayersFromFile', act)

        act = qtWdg.QAction()
        act.setText("Desa capes Qgis")
        act.triggered.connect(self.saveLayersToFile)
        self.accions.afegirAccio('saveLayersToFile', act)

        act = qtWdg.QAction()
        act.setText("Afegeix al catàleg de capes")
        act.triggered.connect(self.addCatalogueLayers)
        self.accions.afegirAccio('addCatalogueLayers', act)

        act = qtWdg.QAction()
        act.setText("Veure anotacions")
        act.setCheckable(True)
        act.triggered.connect(self.viewAnnotations)
        self.accions.afegirAccio('viewAnnotations', act)

        act = qtWdg.QAction()
        act.setText("Recàrrega de dades")
        act.setCheckable(True)
        act.triggered.connect(self.autoUpdateData)
        self.accions.afegirAccio('autoUpdateData', act)

        act = qtWdg.QAction()
        act.setText("Refresc gràfic")
        act.setCheckable(True)
        act.triggered.connect(self.autoUpdateGraph)
        self.accions.afegirAccio('autoUpdateGraph', act)

        act = qtWdg.QAction()
        act.setText("Canvia nom")
        act.triggered.connect(self.renameGroupOrLayer)  # , type = Qt.DirectConnection)
        self.accions.afegirAccio('renameGroupOrLayer', act)

        #
        # TODO:
        # Sincronizar señales para que la segunda espere al final de la primera
        #

        # if self.atributs is not None:
        #   act.triggered.connect(lambda: self.atributs.tabTaula(self.currentLayer()))

        act = qtWdg.QAction()
        act.setText("Esborra capa o grup")
        # No se usa defaultActions() porque elimina todos los seleccionados; además, hay que cerrar las tablas de datos
        act.triggered.connect(self.removeGroupOrLayer)
        self.accions.afegirAccio('removeGroupOrLayer', act)

        act = qtWdg.QAction()
        act.setText("Enquadra capa")
        act.triggered.connect(self.showLayerMap)
        self.accions.afegirAccio('showLayerMap', act)

        act = qtWdg.QAction()
        act.setText("Mostra contador elements")
        act.triggered.connect(self.showLayerCounter)
        self.accions.afegirAccio('showLayerCounter', act)

        act = qtWdg.QAction()
        act.setText("Mostra diagrama barres")
        act.triggered.connect(self.showBarChart)
        self.accions.afegirAccio('showBarChart', act)

        act = qtWdg.QAction()
        act.setText("Mostra taula dades")
        act.triggered.connect(self.showFeatureTable)
        self.accions.afegirAccio('showFeatureTable', act)

        act = qtWdg.QAction()
        act.setText("Filtra elements")
        act.triggered.connect(self.filterElements)
        self.accions.afegirAccio('filterElements', act)

        act = qtWdg.QAction()
        act.setText("Suprimeix filtre")
        act.triggered.connect(self.removeFilter)
        self.accions.afegirAccio('removeFilter', act)

    def calcTipusMenu(self, idx=None):
        # Tipos: none, group, layer, symb
        tipo = 'none'
        if idx is None: idx = self.currentIndex()
        if idx.isValid():
            node = self.currentNode()
            if node is None:
                tipo = 'symb'
            else:
                tipoNodo = node.nodeType()
                if tipoNodo == qgCor.QgsLayerTreeNode.NodeGroup:
                    tipo = 'group'
                elif tipoNodo == qgCor.QgsLayerTreeNode.NodeLayer:
                    tipo = 'layer'
        return tipo

    def testFlags(self, flags, mask):
        return int(flags & mask) == mask

    def isGroupRemovable(self, node=None):
        if node is None: node = self.currentNode()
        if node is None: return False
        for item in node.findLayers():
            capa = item.layer()
            if not self.isLayerRemovable(capa):
                return False
        return True

    def isLayerRemovable(self, capa=None):
        if capa is None: capa = self.currentLayer()
        if capa is None: return False
        return self.testFlags(capa.flags(), qgCor.QgsMapLayer.LayerFlag.Removable)

    def isLayerEditable(self, capa=None):
        if capa is None: capa = self.currentLayer()
        if capa is None: return False
        if not capa.isValid(): return False
        if capa.readOnly(): return False
        if capa.type() != qgCor.QgsMapLayerType.VectorLayer: return False
        dP = capa.dataProvider()
        if dP is None: return False
        return self.testFlags(dP.capabilities(), qgCor.QgsVectorDataProvider.EditingCapabilities)

    def isLayerEditForm(self, capa=None, depurar=False):
        if capa is None: capa = self.currentLayer()
        if capa is None: return False
        if not depurar:
            if not self.isLayerEditable(capa): return False
            return QvDigitizeContext.testUserEditable(capa, nom='qV_editForm') and not QvDigitizeContext.testUserEditable(capa)
        else:
            ret = self.isLayerEditable(capa)
            if not ret: 
                print(f'Capa {capa.name()} no editable: por definición')
                return False
            ret = QvDigitizeContext.testUserEditable(capa, nom='qV_editForm')
            if not ret:
                print(f'Capa {capa.name()} no editable: usuario no está en qV_editForm')
                return False
            ret = QvDigitizeContext.testUserEditable(capa)
            if ret:
                print(f'Capa {capa.name()} no editable: usuario está en qV_editable')
                return False
            print(f'Capa {capa.name()} EDITABLE')
            return True

    def setMenuAccions(self):
        # Menú dinámico según tipo de elemento sobre el que se clicó
        self.menuAccions = []
        menuTemas = self.tema.setMenu()
        if menuTemas is not None:
            self.accions.afegirAccio('menuTema', menuTemas)
            self.menuAccions += ['menuTema', 'separator']
        tipo = self.calcTipusMenu()
        if tipo == 'layer':
            capa = self.currentLayer()
            if capa is not None and capa.type() == qgCor.QgsMapLayer.VectorLayer:
                if QvDiagrama.capaAmbDiagrama(capa) != '':
                    self.menuAccions += ['showBarChart']
                if self.atributs is not None:
                    self.menuAccions += ['showFeatureTable']
                    if self.editable:
                        self.menuAccions += ['filterElements']
                self.menuAccions += ['showLayerCounter']
            if capa is not None and self.canvas is not None:
                self.menuAccions += ['showLayerMap']
            self.menuAccions += ['separator']
            if self.editable:
                self.menuAccions += ['addGroup', 'renameGroupOrLayer']
                if capa is not None and self.isLayerRemovable(capa):
                    self.menuAccions += ['removeGroupOrLayer']
            self.menuAccions += ['saveLayersToFile', 'addCatalogueLayers']
        elif tipo == 'group':
            if self.editable:
                self.menuAccions += ['addGroup', 'renameGroupOrLayer', 'addLayersFromFile']
                if self.isGroupRemovable():
                    self.menuAccions += ['removeGroupOrLayer']
            self.menuAccions += ['saveLayersToFile', 'addCatalogueLayers']
        elif tipo == 'none':
            self.menuAccions += ['expandLegend', 'collapseLegend', 'separator']
            if self.editable:
                self.menuAccions += ['addGroup', 'addLayersFromFile']
            if self.anotacions and \
               self.anotacions.menuVisible(self.accions.accio('viewAnnotations')):
                self.menuAccions += ['separator', 'viewAnnotations']
            # Informes
            menuInformes = self.reports.setMenu()
            if menuInformes is not None:
                self.accions.afegirAccio('menuInforme', menuInformes)
                self.menuAccions += ['separator', 'menuInforme']
            # Procesos
            from moduls.QvProcessing import QvProcessing
            menuProcessos = QvProcessing().setMenu(self)
            # *** Pruebas
            # if menuProcessos is not None:
            #     menuProcessos.addSeparator()
            #     QvProcessing().addMenuProcess("native:dbscanclustering", "Clustering")
            #     QvProcessing().addMenuProcess("grass7:v.to.lines", "To lines")
            # ***
            if menuProcessos is not None:
                self.accions.afegirAccio('menuProceso', menuProcessos)
                self.menuAccions += ['separator', 'menuProceso']
            # Auto recarga
            if self.recarrega.timerDataSecs > 0 or self.recarrega.timerGraphSecs > 0:
                self.menuAccions += ['separator']
            if self.recarrega.timerDataSecs > 0:
                self.accions.accio('autoUpdateData').setText(f"Recàrrega de dades ({self.recarrega.timerDataSecs}s)")
                self.accions.accio('autoUpdateData').setChecked(self.recarrega.timerData.isActive())
                self.menuAccions += ['autoUpdateData']
            if self.recarrega.timerGraphSecs > 0:
                self.accions.accio('autoUpdateGraph').setText(f"Refresc gràfic ({self.recarrega.timerGraphSecs}s)")
                self.accions.accio('autoUpdateGraph').setChecked(self.recarrega.timerGraph.isActive())
                self.menuAccions += ['autoUpdateGraph']

        else:  # 'symb'
            pass
        return tipo

    def itemChanged(self, index1, index2):
        if self.renaming is not None and self.renaming == index1 and self.renaming == index2:
            self.modificacioProjecte('renameGroupOrLayer')
            self.renaming = None
            if self.atributs is not None and self.calcTipusMenu() == 'layer':
                self.atributs.tabTaula(self.currentNode().layer())

    def renameGroupOrLayer(self):
        self.renaming = self.currentIndex()
        self.defaultActions().renameGroupOrLayer()

    def nodeEditing(self, node):
        tipoNodo = node.nodeType()
        if tipoNodo == qgCor.QgsLayerTreeNode.NodeLayer:
            capa = node.layer()
            return self.editing(capa)
        if tipoNodo == qgCor.QgsLayerTreeNode.NodeGroup:
            for item in node.findLayers():
                capa = item.layer()
                if self.editing(capa):
                    return True
        return False

    def expandLegend(self):
        self.expandAll(True)

    def collapseLegend(self):
        self.expandAll(False)

    def addGroup(self):
        self.defaultActions().addGroup()
        self.modificacioProjecte('addGroup')

    def removeGroupOrLayer(self):
        self.removing = True
        node = self.currentNode()
        if node is not None:
            if self.mapaEditable() and self.nodeEditing(node):
                qtWdg.QMessageBox.information(self, "Atenció", "No es pot esborrar una capa quan s'està editant")
            else:
                if self.atributs is not None:
                    self.atributs.tancarTaules(qgCor.QgsLayerTreeUtils.collectMapLayersRecursive([node]))
                node.parent().removeChildNode(node)
                self.modificacioProjecte('removeGroupOrLayer')
        self.removing = False

    def addLayersFromFile(self):
        dlgLayers = qtWdg.QFileDialog()
        nfile, ok = dlgLayers.getOpenFileName(None, "Afegir Capes Qgis",
                                              self.directory, "Capes Qgis (*.qlr)")
        if ok and nfile != '':
            self.directory = os.path.dirname(nfile)
            ok, txt = qgCor.QgsLayerDefinition.loadLayerDefinition(nfile, self.project, self.root)
            if not ok:
                print('No se pudo importar capas', txt)

    def addCatalogueLayers(self):
        nodes = self.selectedNodes()
        if nodes is not None and len(nodes) > 0:
            dial = QvCreadorCatalegCapes(nodes, self.canvas, self.project, parent=self)
            dial.show()
        else:
            qtWdg.QMessageBox.information(self,'Atenció', 'Seleccioneu capa o grup a la llegenda per poder-la afegir al catàleg')

    def viewAnnotations(self):
        self.sender().setChecked(self.anotacions.toggleAnnotations())

    def autoUpdateData(self):
        self.recarrega.toggleUpdateData(self.sender())

    def autoUpdateGraph(self):
        self.recarrega.toggleUpdateGraph(self.sender())

    def saveStyleToGeoPackage(self, capa, nom="", desc="", default=True):
        s = qgCor.QgsSettings()
        s.setValue("qgis/overwriteStyle", True)
        return capa.saveStyleToDatabase(nom, desc, default, "")

    def saveLayersToFile(self):
        nodes = self.selectedNodes()
        if len(nodes) > 0:
            dlgLayers = qtWdg.QFileDialog()
            if self.directory is not None:
                dlgLayers.setDirectory(self.directory)
            nfile, ok = dlgLayers.getSaveFileName(None, "Desar Capes Qgis",
                                                  self.directory, "Capes Qgis (*.qlr)")
            if ok and nfile != '':
                self.directory = os.path.dirname(nfile)
                ok, txt = qgCor.QgsLayerDefinition.exportLayerDefinition(nfile, nodes)
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

    def showLayerCounter(self):
        self.defaultActions().showFeatureCount()
        # La primera vez que se muestran los contadores de las categorías, lo hace bien,
        # sea con filtro o no. Si se modifica el filtro después, los contadores de las
        # categorías no se actualizan, hay que forzarlo con updateLayerSymb()






    def showBarChart(self):
        self.diagrama = QvDiagrama.barres(self.currentLayer())
        if self.diagrama is not None:
            self.diagrama.show()

    def showFeatureTable(self):
        if self.atributs is not None:
            layer = self.currentLayer()
            if layer is not None and layer.type() == qgCor.QgsMapLayer.VectorLayer:
                self.atributs.obrirTaula(layer)
                self.atributs.show()
                self.obertaTaulaAtributs.emit()

    def filterElements(self):
        layer = self.currentLayer()
        if layer is not None and self.atributs is not None:
            self.atributs.filtrarCapa(layer, True)

    def removeFilter(self):
        layer = self.currentLayer()
        if layer is not None and self.atributs is not None:
            self.atributs.filtrarCapa(layer, False)

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
            tipus = qgCor.QgsLayerTreeNode.NodeGroup
        elif filtre == 'layer':
            tipus = qgCor.QgsLayerTreeNode.NodeLayer
        else:
            tipus = None
        for node in self.nodes():
            if (tipus is None or tipus == node.nodeType()) and node.name() == nom:
                return node
        return None

    def expandAll(self, switch=True):
        for item in self.items():
            item.expandir(switch)

    def items(self):
        def recurse(item, level):
            yield QvItemLlegenda(item, level)
            if qgCor.QgsLayerTree.isLayer(item):
                for cat in self.model.layerOriginalLegendNodes(item):
                    if cat.data(qtCor.Qt.CheckStateRole) is not None:
                        yield QvItemLlegenda(cat, level + 1)
            for child in item.children():
                yield from recurse(child, level + 1)
        num = self.model.rowCount()
        for row in range(num):
            index = self.model.index(row, 0)
            item = self.model.index2node(index)
            yield from recurse(item, 0)

    def printItems(self, soloCapa=None):
        print('Items Llegenda:')
        seguir = soloCapa is None
        for item in self.items():
            capa = item.capa()
            if capa is None:
                nomCapa = '-'
            else:
                nomCapa = capa.name()
            if item.tipus == 'layer':
                seguir = soloCapa is not None and soloCapa.id() == capa.id()
            elif item.tipus == 'group':
                seguir = False
            if not seguir: continue
            expandit = item.esExpandit()
            if expandit is None:
                txtExpandit = ''
            elif expandit:
                txtExpandit = '(expandido)'
            else:
                txtExpandit = '(no expandido)'
            print('  ' * item.nivell, '-',
                    'Tipo:', item.tipus,
                    txtExpandit,
                    'Nivel:', item.nivell,
                    'Capa:', nomCapa,
                    'Nombre:', item.nom(),
                    'Visible:', item.esVisible(),
                    'Marcado:', item.esMarcat())


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')
        # QvApp().logInici()

        # canv = qgGui.QgsMapCanvas()

        # atrib = QvAtributs(canv)

        # leyenda = QvLlegenda(canv, atrib)

        # leyenda.project.read('D:/qVista/EjemploMapSin.qgs')

        # canv.setWindowTitle('Canvas')
        # canv.show()

        # leyenda.setWindowTitle('Llegenda')
        # leyenda.show()

        def printCapaActiva():
            cLayer = leyenda.currentLayer()
            if cLayer:
                print('Capa activa:', cLayer.name())
                uri = cLayer.dataProvider().dataSourceUri()
                drive = uri.split(':')[0]
                print('URI:', uri)
                txt = ''
                if QvFuncions.isDriveFixed(drive):
                    txt = '(Disco fijo)'
                print('Disco:', drive, txt)
            else:
                print('Capa activa: None')

        canv = qgGui.QgsMapCanvas()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib, printCapaActiva, editable=False)
        leyenda.projecteModificat.connect(print)

        # leyenda.project.read('D:/qVista/EjemploMapSin.qgs')
        leyenda.project.read(cfg.projecteInicial)

        canv.setWindowTitle('Canvas')
        canv.show()
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
            dialegObertura = qtWdg.QFileDialog()
            dialegObertura.setDirectoryUrl(qtCor.QUrl('../dades/projectes/'))
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
            # QvApp().logRegistre('Menú Test')
            leyenda.printItems()
            leyenda.expandAll()

        def salutacions():
            qtWdg.QMessageBox().information(None, 'qVista', 'Salutacions ' + QvApp().usuari)

        # def editable():
        #     leyenda.editarLlegenda(not leyenda.editable)

        # Acciones de usuario para el menú

        # act = qtWdg.QAction()
        # act.setText("Editable")
        # act.triggered.connect(editable)
        # leyenda.accions.afegirAccio('editable', act)

        act = qtWdg.QAction()
        act.setText("Test")
        act.triggered.connect(test)
        leyenda.accions.afegirAccio('test', act)

        act = qtWdg.QAction()
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
                leyenda.menuAccions.append('editable')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)

        # app.aboutToQuit.connect(QvApp().logFi)
