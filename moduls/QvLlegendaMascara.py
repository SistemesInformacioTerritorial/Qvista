# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsPalLayerSettings, QgsPropertyCollection, QgsProperty

class QvLlegendaMascara:

    def __init__(self, legend, layer, polygonId):
        self.legend = legend
        self.layer = layer
        self.layerId = self.layer.id()
        self.polygonId = polygonId
        self.template = "within(centroid($geometry), geometry(get_feature_by_id('{}', {})))"
        self.key = QgsPalLayerSettings.Show
        self.active = False
        self.labels = None
        self.sets = None
        self.props = None
        self.maskInit()

    def calcExpression(self):
        return self.template.format(self.layerId, self.polygonId)

    # Funciones de 1 capa
    def labelsEnabled(self, layer):
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            return False
        return layer.labelsEnabled()

    def getLabelsProps(self, layer):
        if self.labelsEnabled(layer):
            self.labels = layer.labeling() # QgsVectorLayerSimpleLabeling
            self.sets = self.labels.settings() # QgsPalLayerSettings
            self.props = self.sets.dataDefinedProperties() # QgsPropertyCollection
            if self.props is None:
                self.props = QgsPropertyCollection()
            return True
        else:
            return False

    def isEnabled(self, layer):
        if not self.getLabelsProps(layer):
            return False

        if self.props.hasProperty(self.key):
            prop = self.props.property(self.key)
            if prop.isActive() and prop.propertyType() == QgsProperty.ExpressionBasedProperty and \
               prop.expressionString() == self.calcExpression():
                return True
        return False

    def switch(self, layer, active):
        if not self.getLabelsProps(layer):
            return

        if active:
            prop = QgsProperty()
            prop.setExpressionString(self.calcExpression())
            self.props.setProperty(self.key, prop)
        else:
            self.props.setProperty(self.key, None)

        self.sets.setDataDefinedProperties(self.props)
        self.labels.setSettings(self.sets)
        layer.setLabeling(self.labels)

    def enable(self, layer):
        self.switch(layer, True)

    def disable(self, layer):
        self.switch(layer, False)

    # Funciones de todas las capas
    def switchAll(self, active):
        self.active = active
        for layer in self.legend.project.mapLayers():
            self.switch(self.legend.project.mapLayer(layer), active)

    def enableAll(self):
        self.switchAll(True)

    def disableAll(self):
        self.switchAll(False)

    # Funciones de leyenda

    def maskInit(self):
        node = self.legend.root.findLayer(self.layerId)
        if node is not None and node.isVisible():
            self.maskOn()
        else:
            self.maskOff()

    def maskOn(self):
        if not self.active:
            self.enableAll()
            self.legend.canvas.clearCache()
            self.legend.canvas.refresh()

    def maskOff(self):
        if self.active:
            self.disableAll()
            self.legend.canvas.clearCache()
            self.legend.canvas.refresh()
