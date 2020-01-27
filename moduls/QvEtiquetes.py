# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsProject, QgsPalLayerSettings, QgsPropertyCollection, QgsProperty


class QvMaskLabels:

    def __init__(self, layerMask="Màscara", idPolygon=1):
        self.layerMask = layerMask  # Nombre o ID
        self.idPolygon = idPolygon        # ID del polígono
        self.key = QgsPalLayerSettings.Show
        self.expression = self.calcExpression()

    def calcExpression(self, template="within(centroid($geometry), geometry(get_feature_by_id('{}', {})))"):
        return template.format(self.layerMask, self.idPolygon)

    def labelsEnabled(self, layer):
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            return False
        return layer.labelsEnabled()

    def isEnabled(self, layer):
        if not self.labelsEnabled(layer):
            return False

        labels = layer.labeling()
        sets = labels.settings()
        props = sets.dataDefinedProperties()

        if props.hasProperty(self.key):
            prop = props.property(self.key)
            if prop.isActive() and prop.propertyType() == QgsProperty.ExpressionBasedProperty and \
               prop.expressionString() == self.expression:
                return True
        return False

    def switch(self, layer, on):
        if not self.labelsEnabled(layer):
            return

        labels = layer.labeling()
        sets = labels.settings()
        props = sets.dataDefinedProperties()
        if props is None:
            props = QgsPropertyCollection()

        if on:
            prop = QgsProperty()
            prop.setExpressionString(self.expression)
            props.setProperty(self.key, prop)
        else:
            props.setProperty(self.key, None)

        sets.setDataDefinedProperties(props)
        labels.setSettings(sets)
        layer.setLabeling(labels)

    def enable(self, layer):
        self.switch(layer, True)

    def disable(self, layer):
        self.switch(layer, False)

    def switchAll(self, on):
        for layerId in QgsProject.instance().mapLayers():
            self.switch(QgsProject.instance().mapLayer(layerId), on)

    def enableAll(self):
        self.switchAll(True)

    def disableAll(self):
        self.switchAll(False)
