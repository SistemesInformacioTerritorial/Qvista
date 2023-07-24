# -*- coding: utf-8 -*-

import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.core as qgCor
import qgis.gui as qgGui
from moduls.QvApp import QvApp
from moduls import QvFuncions
from moduls.QvDigitizeContext import QvDigitizeContext

class QvItemLlegenda:

    def __init__(self, item, nivell):
        self.item = item
        self.nivell = nivell
        self.tipus = self.calcTipus()

    def calcTipus(self):
        clase = type(self.item).__name__
        if clase == 'QgsLayerTreeLayer':
            return 'layer'
        elif clase == 'QgsLayerTreeGroup':
            return 'group'
        elif clase in ('QgsSymbolLegendNode', 'QgsLayerTreeModelLegendNode'):
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
            return self.item.data(qtCor.Qt.DisplayRole)
        else:
            return None

    def esMarcat(self):
        if self.tipus in ('layer', 'group'):
            return self.item.itemVisibilityChecked()
        elif self.tipus == 'symb':
            return self.item.data(qtCor.Qt.CheckStateRole) != 0
        else:
            return None

    def marcar(self, switch=True):
        if self.tipus in ('layer', 'group'):
            self.item.setItemVisibilityChecked(switch)
        elif self.tipus == 'symb':
            if switch:
                self.item.setData(qtCor.Qt.Checked, qtCor.Qt.CheckStateRole)
            else:
                self.item.setData(qtCor.Qt.Unchecked, qtCor.Qt.CheckStateRole)

    def esVisible(self):
        if self.tipus in ('layer', 'group'):
            return self.item.isVisible()
        elif self.tipus == 'symb':
            return self.esMarcat() and self.item.layerNode().isVisible()
        else:
            return None

    def veure(self, switch=True, children=True):
        if self.tipus in ('layer', 'group'):
            if switch:
                self.item.setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.setItemVisibilityCheckedRecursive(True)
            else:
                self.marcar(False)
        elif self.tipus == 'symb':
            self.marcar(switch)
            if switch:
                self.item.layerNode().setItemVisibilityCheckedParentRecursive(True)
                if children:
                    self.item.layerNode().setItemVisibilityCheckedRecursive(True)

    def esExpandit(self):
        if self.tipus in ('layer', 'group'):
            return self.item.isExpanded()
        else:
            return None

    def expandir(self, switch=True):
        if self.tipus in ('layer', 'group'):
            self.item.setExpanded(switch)

class QvModelLlegenda(qgCor.QgsLegendModel):
    def __init__(self, root):
        super().__init__(root)
        self.setScale(1.0)

    def setScale(self, scale):
        self.scale = scale

    def layerInScale(self, index):
        node = self.index2node(index)
        if node is not None and node.nodeType() == qgCor.QgsLayerTreeNode.NodeLayer:
            layer = node.layer()
            if layer is not None:
                if node.isVisible() and layer.isInScaleRange(self.scale):
                    return True
                else:
                    return False
        return None

    def data(self, index, role):

        # *** Tratamiento de capas con visibilidad controlada por escala
        # - Texto en itálica cuando la capa no se ve
        if index.isValid() and role == qtCor.Qt.FontRole:
            inScale = self.layerInScale(index)
            if inScale is not None:
                italic = not inScale
                font = super().data(index, role)
                font.setItalic(italic)
                return font
        # - Texto en gris cuando la capa no se ve
        if index.isValid() and role == qtCor.Qt.ForegroundRole:
            inScale = self.layerInScale(index)
            if inScale is not None:
                if inScale:
                    color = qtGui.QColor('#000000')
                else:
                    color = qtGui.QColor('#909090')
                brush = super().data(index, role)
                brush.setColor(color)
                return brush

        # *** Muestra contador de elementos de capa para v.3.22
        if QvApp().testVersioQgis(3, 22) and index.isValid() and role == qtCor.Qt.DisplayRole:
            node = self.index2node(index)
            if qgCor.QgsLayerTree.isLayer(node):
                layer = node.layer()
                if layer:
                    name = layer.name()
                    status = node.customProperty("showFeatureCount")
                    if status is None: status = False
                    if status and name[-1] != ']':
                        sign = ''
                        if layer.dataProvider() and qgCor.QgsDataSourceUri(layer.dataProvider().dataSourceUri()).useEstimatedMetadata(): sign = '≈'
                        num = 'N/A'
                        count = layer.featureCount()
                        if count >= 0: num = QvApp().locale.toString(count)
                        name = f"{name} [{sign}{num}]"
                        return name

        # *** Resto
        return super().data(index, role)

    #   QgsLayerTreeModel.cpp
    #
    #   QgsLayerTreeNode *node = index2node( index );
    # if ( QgsLayerTree::isLayer( node ) )
    # {
    #   QgsLayerTreeLayer *nodeLayer = QgsLayerTree::toLayer( node );
    #   QString name = nodeLayer->name();
    #   QgsVectorLayer *vlayer = qobject_cast<QgsVectorLayer *>( nodeLayer->layer() );
    #   if ( vlayer && nodeLayer->customProperty( QStringLiteral( "showFeatureCount" ), 0 ).toInt() && role == Qt::DisplayRole )
    #   {
    #     const bool estimatedCount = vlayer->dataProvider() ? QgsDataSourceUri( vlayer->dataProvider()->dataSourceUri() ).useEstimatedMetadata() : false;
    #     const qlonglong count = vlayer->featureCount();

    #     // if you modify this line, please update QgsSymbolLegendNode::updateLabel
    #     name += QStringLiteral( " [%1%2]" ).arg(
    #               estimatedCount ? QStringLiteral( "≈" ) : QString(),
    #               count != -1 ? QLocale().toString( count ) : tr( "N/A" ) );
    #   }
    #   return name;
    
class QvMenuLlegenda(qgGui.QgsLayerTreeViewMenuProvider):

    def __init__(self, llegenda):
        qgGui.QgsLayerTreeViewMenuProvider.__init__(self)
        self.llegenda = llegenda

    def createContextMenu(self):
        tipo = self.llegenda.setMenuAccions()
        self.llegenda.clicatMenuContexte.emit(tipo)
        return self.llegenda.accions.menuAccions(self.llegenda.menuAccions)

class QvRecarregaLlegenda:

    def __init__(self, llegenda):
        self.llegenda = llegenda
        self.timerData = qtCor.QTimer() # Timer para auto recarga de datos de proyecto (por capas)
        self.timerData.timeout.connect(self.updateProjectData)
        self.timerDataSecs = 0
        self.updateDataLayers = []
        self.timerGraph = qtCor.QTimer() # Timer para auto recarga gráfica de proyecto (por capas)
        self.timerGraph.timeout.connect(self.updateProjectGraph)
        self.timerGraphSecs = 0
        self.updateGraphLayers = []

    def resetTimers(self):
        if self.timerData.isActive():
            self.timerData.stop()
            self.timerDataSecs = 0
            self.updateDataLayers = []
        if self.timerGraph.isActive():
            self.timerGraph.stop()
            self.timerGraphSecs = 0
            self.updateGraphLayers = []

    def isUpdateDataLayer(self, layer):
        return self.timerData.isActive() and layer in self.updateDataLayers

    def isUpdateGraphLayer(self, layer):
        return self.timerGraph.isActive() and layer in self.updateGraphLayers

    def toggleUpdateData(self, sender):
        if self.timerData.isActive():
            self.timerData.stop()
            sender.setChecked(False)
        else:
            self.timerData.start(self.timerDataSecs * 1000)
            sender.setChecked(True)
        self.llegenda.actIcones()

    def toggleUpdateGraph(self, sender):
        if self.timerGraph.isActive():
            self.timerGraph.stop()
            sender.setChecked(False)
        else:
            self.timerGraph.start(self.timerGraphSecs * 1000)
            sender.setChecked(True)
        self.llegenda.actIcones()

    def autoRecarrega(self):
        segData = segGraph = 0
        self.updateDataLayers = []
        self.updateGraphLayers = []
        try:
            var = qgCor.QgsExpressionContextUtils.projectScope(self.llegenda.project).variable('qV_autoRecarrega')
            var = QvDigitizeContext.varClear(var)
            if var is not None and var != '':
                prms = QvDigitizeContext.varList(var, str)
                if prms is not None: 
                    try:
                        segData = int(prms[0])
                    except:
                        segData = 0
                    if segData > 0:
                        self.timerData.start(segData * 1000)
                        print('autoProjectUpdateData: ', str(segData), 's')
                    try:
                        segGraph = int(prms[1])
                    except:
                        segGraph = 0
                    if segGraph > 0:
                        self.timerGraph.start(segGraph * 1000)
                        print('autoProjectUpdateGraph: ', str(segGraph), 's')
                    if segData > 0 or segGraph > 0:
                        self.getActiveUpdateLayers()
                        self.llegenda.actIcones()
        except Exception as e:
            print(str(e))
        finally:
           self.timerDataSecs, self.timerGraphSecs = segData, segGraph
        #  return segData, segGraph

    def getActiveUpdateLayers(self):
        self.updateDataLayers = []
        self.updateGraphLayers = []
        for layer in self.llegenda.capes():
            prm = qgCor.QgsExpressionContextUtils.layerScope(layer).variable('qV_autoRecarrega')
            if prm is None: continue
            if self.timerData.isActive() and layer.isValid() and layer.type() == qgCor.QgsMapLayer.VectorLayer:
                self.updateDataLayers.append(layer)
            if self.timerGraph.isActive() and layer.isValid() and layer.type() == qgCor.QgsMapLayer.VectorLayer and layer.isSpatial():
                self.updateGraphLayers.append(layer)

    def updateProjectGraph(self):
        self.getActiveUpdateLayers()
        if QvFuncions.debugging(): print('update Graph Layers', self.updateGraphLayers)
        for layer in self.updateGraphLayers:
            layer.triggerRepaint(False)
            if QvFuncions.debugging(): print('update Graph', layer.name())
        self.llegenda.actIcones()

    def updateProjectData(self):
        self.getActiveUpdateLayers()
        if QvFuncions.debugging(): print('update Data Layers', self.updateDataLayers)
        for layer in self.updateDataLayers:
            self.updateLayerData(layer, False)
            if QvFuncions.debugging(): print('update Data', layer.name())
        self.llegenda.actIcones()

    def updateLayerData(self, layer, msgError=True):
        try:
            if QvApp().testVersioQgis(3, 22):
                layer.dataProvider().reloadData()
            else:   
                layer.dataProvider().forceReload()
            # Hay que forzar la actualización de los contadores de las categorías, si existen
            self.updateLayerSymb(layer)
        except Exception as e:
            if msgError:
                qtWdg.QMessageBox.warning(self, "Error al actualitzar dades de capa", layer.name(), str(e))
            else:
                print(str(e))

    def updateLayerSymb(self, layer):
        if layer is not None and layer.isValid() and layer.type() == qgCor.QgsMapLayer.VectorLayer:
            r = layer.renderer()
            if type(r) in (qgCor.QgsCategorizedSymbolRenderer, qgCor.QgsRuleBasedRenderer, qgCor.QgsGraduatedSymbolRenderer):
                layer.setRenderer(r.clone())
                # Comentado, no funciona. Lo solucionamos sutituyendo el renderer
                # node = self.llegenda.root.findLayer(layer.id())
                # if node is not None:
                #     self.llegenda.model.refreshLayerLegend(node)

