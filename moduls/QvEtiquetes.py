# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsProject, QgsPalLayerSettings, QgsPropertyCollection, QgsProperty


class QvMaskLabels:

    def __init__(self, layer, polygonId):
        self.layer = layer
        self.polygonId = polygonId
        self.template = "within(centroid($geometry), geometry(get_feature_by_id('{}', {})))"
        self.key = QgsPalLayerSettings.Show
        self.on = False
        self.labels = None
        self.sets = None
        self.props = None

    def calcExpression(self):
        return self.template.format(self.layer.id(), self.polygonId)

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

    def switch(self, layer, on):
        if not self.getLabelsProps(layer):
            return

        if on:
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

    def switchAll(self, on):
        self.on = on
        for layer in QgsProject.instance().mapLayers():
            self.switch(QgsProject.instance().mapLayer(layer), on)

    def enableAll(self):
        self.switchAll(True)

    def disableAll(self):
        self.switchAll(False)
