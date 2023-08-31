# -*- coding: utf-8 -*-

import qgis.core as qgCor
from qgis.core import QgsRuleBasedLabeling, QgsVectorLayer, QgsProperty, QgsPalLayerSettings, QgsPropertyCollection

_TEMPLATES = dict = {
    "centroid": "NOT within(centroid($geometry), geometry(get_feature_by_id('{}', {})))",
    "intersects": "NOT intersects($geometry, geometry(get_feature_by_id('{}', {})))"
}

_DEF_TEMPLATE = "centroid"


class QvLlegendaMascara:

    def __init__(self, legend, layer, polygonId, template=_DEF_TEMPLATE):
        self.legend = legend
        self.layer = layer
        self.layerId = self.layer.id()
        self.polygonId = polygonId
        self.template = self.setTemplate(template)
        self.key = qgCor.QgsPalLayerSettings.Show
        self.active = False
        self.labels = None
        self.sets = None
        self.props = None
        self.memoryRules = {}
        self.maskInit()

    def setTemplate(self, template):
        return _TEMPLATES.get(template, _DEF_TEMPLATE)

    def calcExpression(self):
        return self.template.format(self.layerId, self.polygonId)

    # Funciones de capa

    def labelsEnabled(self, layer):
        if layer is None or layer.type() != qgCor.QgsMapLayer.VectorLayer:
            return False
        return layer.labelsEnabled()

    def getLabelsProps(self, layer):
        if self.labelsEnabled(layer):
            self.labels = layer.labeling()  # QgsVectorLayerSimpleLabeling
            self.sets = self.labels.settings()  # QgsPalLayerSettings
            self.props = self.sets.dataDefinedProperties()  # QgsPropertyCollection
            if self.props is None:
                self.props = qgCor.QgsPropertyCollection()
            return True
        else:
            return False

    def isActive(self, layer):
        if not self.getLabelsProps(layer):
            return False
        if self.props.hasProperty(self.key):
            prop = self.props.property(self.key)
            if (prop.isActive() and
               prop.propertyType() == qgCor.QgsProperty.ExpressionBasedProperty and
               prop.expressionString() == self.calcExpression()):
                return True
        return False
    
    @staticmethod
    def addExpressionProperty(property, expression):
        if property.expressionString() == '':
            return expression
        return f'({property.expressionString()}) AND {expression}'

    def switch(self, layer, active=None):
        if not self.getLabelsProps(layer):
            return
        if active is None:
            active = not self.isActive(layer)

        labeling = layer.labeling()

        if isinstance(labeling, QgsRuleBasedLabeling):
            if layer not in self.memoryRules:
                self.memoryRules[layer] = {}
            root_rule = labeling.rootRule().clone()
            for (i, rule) in enumerate(root_rule.children()):
                settings = rule.settings()
                properties = settings.dataDefinedProperties()
                name = properties.name

                if active:
                    if properties.hasProperty(self.key) and i not in self.memoryRules[layer]:
                        self.memoryRules[layer][i] = properties.property(self.key)
                    exp = self.addExpressionProperty(properties.property(self.key), self.calcExpression())
                    prop = QgsProperty()
                    prop.setExpressionString(exp)
                    properties.setProperty(self.key, prop)
                else:
                    if i in self.memoryRules[layer]:
                        properties.setProperty(self.key, self.memoryRules[layer][i])
                    else:
                        properties.setProperty(self.key, None)

                settings.setDataDefinedProperties(properties)
                rule.setSettings(settings)

            new_labeling = QgsRuleBasedLabeling(root_rule)
            layer.setLabeling(new_labeling)
        else:
            if active:
                # si ja teníem un valor, el desem abans de modificar-lo, per poder-lo recuperar
                if self.props.hasProperty(self.key) and layer not in self.memoryRules:
                    self.memoryRules[layer] = self.props.property(self.key)
                exp = self.addExpressionProperty(self.props.property(self.key), self.calcExpression())
                prop = QgsProperty()
                prop.setExpressionString(self.calcExpression())
                self.props.setProperty(self.key, prop)
            else:
                if layer in self.memoryRules:
                    self.props.setProperty(self.key, self.memoryRules[layer])
                else:
                    self.props.setProperty(self.key, None)

            self.sets.setDataDefinedProperties(self.props)
            self.labels.setSettings(self.sets)
            layer.setLabeling(self.labels)

        layer.triggerRepaint()

    # Funciones generales

    def maskInit(self):
        # node = self.legend.root.findLayer(self.layerId)
        # active = node is not None and node.isVisible()
        active = self.legend.capaVisible(self.layer)
        self.maskSwitch(active)

    def maskSwitch(self, active=None):
        if active is None:
            active = not self.active
        if active != self.active:
            self.active = active
            for layer in self.legend.project.mapLayers():
                self.switch(self.legend.project.mapLayer(layer), active)
            self.legend.canvas.redrawAllLayers()


if __name__ == "__main__":

    import qgis.gui as qgGui
    import qgis.PyQt.QtWidgets as qtWdg

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvAtributs import QvAtributs

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = qgGui.QgsMapCanvas()
        atribs = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atribs)

        leyenda.project.read('D:/qVista/EjemploMapTestMask.qgs')
        leyenda.mask = QvLlegendaMascara(leyenda, leyenda.capaPerNom("Màscara"), 1)
        leyenda.setMinimumSize(400, 500)
        leyenda.move(0, 0)
        leyenda.show()

        canvas.setWindowTitle('Test Mask Labels')
        canvas.setMinimumSize(1300, 900)
        canvas.move(leyenda.width() + 10, 0)
        canvas.show()

        # Acciones de prueba de máscara para etiquetas

        def testLayerLabels():
            msg = "Test Layer Labels"
            if leyenda.mask is None:
                msg += '\n' + "- Sin máscara"
            else:
                capa = leyenda.currentLayer()
                msg += '\n' + "Capa: {}".format(capa.name())
                if leyenda.mask.labelsEnabled(capa):
                    on = leyenda.mask.isActive(capa)
                    if on:
                        msg += '\n' + "- Activada"
                    else:
                        msg += '\n' + "- No activada"
                else:
                    msg += '\n' + "- Sin etiquetas"
            qtWdg.QMessageBox().information(None, "Test", msg)

        def switchLayerMaskLabels():
            if leyenda.mask is None:
                qtWdg.QMessageBox().information(None, "Test", "Sin máscara")
                return
            capa = leyenda.currentLayer()
            leyenda.mask.switch(capa)
            if leyenda.capaVisible(capa):
                leyenda.canvas.redrawAllLayers()

        def switchAllMaskLabels():
            if leyenda.mask is None:
                qtWdg.QMessageBox().information(None, "Test", "Sin máscara")
                return
            leyenda.mask.maskSwitch()

        def switchRotation():
            canvas.clearCache()
            if canvas.rotation() == 0.0:
                canvas.setRotation(45.0)
            else:
                canvas.setRotation(0.0)
            canvas.refresh()

        act = qtWdg.QAction()
        act.setText("Test Layer Mask Labels")
        act.triggered.connect(testLayerLabels)
        leyenda.accions.afegirAccio('testLabels', act)

        act = qtWdg.QAction()
        act.setText("Switch Layer Mask Labels")
        act.triggered.connect(switchLayerMaskLabels)
        leyenda.accions.afegirAccio('maskLabels', act)

        act = qtWdg.QAction()
        act.setText("Switch All Mask Labels")
        act.triggered.connect(switchAllMaskLabels)
        leyenda.accions.afegirAccio('maskSwitch', act)

        act = qtWdg.QAction()
        act.setText("Switch Rotation")
        act.triggered.connect(switchRotation)
        leyenda.accions.afegirAccio('switchRotation', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'layer':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('testLabels')
                leyenda.menuAccions.append('maskLabels')
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('maskSwitch')
                leyenda.menuAccions.append('switchRotation')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
