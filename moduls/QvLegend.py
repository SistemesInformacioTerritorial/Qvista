# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsLegendModel, QgsLayerDefinition
from qgis.gui import QgsLayerTreeView, QgsLayerTreeViewMenuProvider, QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtWidgets import QMenu, QAction, QFileDialog
from qgis.PyQt.QtGui import QIcon
# import recursos

class QvLegend(QgsLayerTreeView):

    def __init__(self, canvas = None, currentLayerChanged = None):
        super().__init__()
        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()

        # Asociar canvas y bridges
        self.bridges = []
        self.bridgeCanvas(canvas)

        # Evento de nueva capa seleccionada
        self.connectCurrentLayerChanged(currentLayerChanged)
        
        # Model
        self.model = QgsLegendModel(self.root)
        self.model.setFlag(QgsLegendModel.AllowNodeReorder)
        self.model.setFlag(QgsLegendModel.AllowNodeRename)
        self.model.setFlag(QgsLegendModel.AllowLegendChangeState)
        self.model.setFlag(QgsLegendModel.AllowNodeChangeVisibility)
        self.model.setFlag(QgsLegendModel.ShowLegend)
        self.setModel(self.model)

        # Acciones predefinidas y menu contextual
        self.actions = {}
        self.setActions()
        self.menuActions = []
        self.setMenuActions()
        self.setMenuProvider(QvLegendMenu(self))

    def connectCurrentLayerChanged(self, currentLayerChanged):
        if currentLayerChanged:
            self.currentLayerChanged.connect(currentLayerChanged)
    
    def bridgeCanvas(self, canvas):
        """
        Enlaza el proyecto con un canvas.
        
        Arguments:
            canvas {QgsMapCanvas} -- Canvas donde se muestra el proyecto
                bridges
        """
        if canvas:
            bridge = QgsLayerTreeMapCanvasBridge(self.root, canvas)
            self.bridges.append((canvas, bridge))

    def layerByName(self, layerName):
        """
        Devuelve el primer layer con el nombre especificado.
        
        Arguments:
            layerName {String} -- El nombre del layer que queremos recuperar.
        
        Returns:
            QgsMapLayer -- El layer que hemos pedido por nombre.
        
        """
        layers = self.project.mapLayersByName(layerName)
        if len(layers) > 0:
            return layers[0]
        else:
            return None

    def layers(self):
        """
        Devuelve la lista de layers del proyecto.
        
        Returns:
            List de QgsMapLayers -- La lista de layers.

        """
        layersIds = self.project.mapLayers()
        layers = []
        for layerId in layersIds:
            layers.append(self.project.mapLayer(layerId))
        return layers

    def setLayerVisibility(self, layer, visibility, chidren = False):
        """
        Hace visible o invisible una layer.

        Arguments:
            layer {QgsMapLayer} -- Layer al que queremos cambiar su visibilidad.
            visibility {bool} -- True (visible) o False (invisible).
            chidren {bool} -- True si queremos cambiar también la visibilidad de los hijos
        
        """
        node = self.root.findLayer(layer.id())
        if node:
            if chidren:
                node.setItemVisibilityCheckedRecursive(visibility)
            else:
                node.setItemVisibilityChecked(visibility)

    def addAction(self, name, act):
        self.actions[name] = act

    def setActions(self):
        act = QAction()
        act.setText("Afegir grup")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().addGroup)
        self.addAction('addGroup', act)
        act = QAction()
        act.setText("Afegir capes")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.addLayersFromFile)
        self.addAction('addLayersFromFile', act)
        act = QAction()
        act.setText("Renombrar capa o grup")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().renameGroupOrLayer)
        self.addAction('renameGroupOrLayer', act)
        act = QAction()
        act.setText("Esborrar capa o grup")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().removeGroupOrLayer)
        self.addAction('removeGroupOrLayer', act)
        act = QAction()
        act.setText("Contador elements")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.defaultActions().showFeatureCount)
        self.addAction('showFeatureCount', act)

    def setMenuActions(self, lista = None):
        if lista:
            self.menuActions = lista
        else:
            self.menuActions = ['addGroup', 'addLayersFromFile', 
                               'separator', 
                               'renameGroupOrLayer', 'removeGroupOrLayer','showFeatureCount']

    def createContextMenu(self):
        menu = QMenu()
        for actName in self.menuActions:
            if actName == 'separator':
                menu.addSeparator()
            elif actName in self.actions:
                menu.addAction(self.actions[actName])
        return menu

    def addLayersFromFile(self):
        dlgLayers = QFileDialog()
        # dlgLayers.setDirectoryUrl()
        nfile, _ = dlgLayers.getOpenFileName(None, "Afegir Capes Qgis", ".", "Capes Qgis (*.qlr)")
        if nfile != '':
            QgsLayerDefinition.loadLayerDefinition(nfile, self.project, self.root)

class QvLegendMenu(QgsLayerTreeViewMenuProvider):

    def __init__(self, legend):
        QgsLayerTreeViewMenuProvider.__init__(self)
        self.legend = legend

    def createContextMenu(self):
        return self.legend.createContextMenu()

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox
    from functools import partial

    with qgisapp():
 
        # Si se define primero el proyecto hace cosas raras !!??

        canvas = QgsMapCanvas()
        canvas.setWindowTitle('MapCanvas')
        canvas.show()

        project = QgsProject.instance()
        project.read('../dades/projectes/bcn11.qgs')

        legend = QvLegend(canvas)
        legend.setWindowTitle('Legend')
        legend.show()

        #
        # Funciones de layers:
        # layers(), layerByName(), currentLayer(), setCurrentLayer(), setLayerVisibility()
        #

        for layer in legend.layers():
            print(layer.name())

        legend.setLayerVisibility(legend.layerByName('BCN_Barri_ETRS89_SHP'), True)
        legend.setLayerVisibility(legend.layerByName('BCN_Districte_ETRS89_SHP'), True)
        legend.setLayerVisibility(legend.layerByName('BCN_Illes_ETRS89_SHP'), False)

        legend.setCurrentLayer(legend.layerByName('BCN_Barri_ETRS89_SHP'))
        print(legend.currentLayer().name())

        #
        # Acciones personalizadas para menú contextual de la leyenda:
        #
        # - Definición de la acción y del metodo asociado
        # - Se añade la acción a la lista de acciones disponibles
        # - Se redefine la lista de acciones que apareceran en el menú
        #

        # Acción salutacions
        def salutacions():
            QMessageBox().information(None, "Salutacions", 'QvLegend qVista')

        act = QAction()
        act.setText("Salutacions")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(salutacions)

        legend.addAction('salutacions', act)

        # Acción veureCapaActiva
        def veureCapaActiva(capa, canvas):
            cLayer = capa.currentLayer()
            if cLayer:
                extent = cLayer.extent()
                canvas.setExtent(extent)
                canvas.refresh()

        act = QAction()
        act.setText("Veure Capa Activa")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(lambda: veureCapaActiva(legend, canvas))

        legend.addAction('veureCapaActiva', act)

        # Acción defaultMenu
        def defaultMenu(legend):
            legend.setMenuActions()
            legend.menuActions.append('separator')
            legend.menuActions.append('menuExtended')

        act = QAction()
        act.setText("Menú per defecte")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(lambda: defaultMenu(legend))

        legend.addAction('defaultMenu', act)

        # Acción menuExtended
        def menuExtended(legend):
            legend.setMenuActions()
            legend.menuActions.append('separator')
            legend.menuActions.append('veureCapaActiva')
            legend.menuActions.append('salutacions')
            legend.menuActions.append('defaultMenu')

        act = QAction()
        act.setText("Menú ampliat")
        act.setIcon(QIcon('imatges/ic_file_upload_black_48dp.png'))
        act.triggered.connect(lambda: menuExtended(legend))

        legend.addAction('menuExtended', act)

        # De entrada, menú corto
        defaultMenu(legend)

