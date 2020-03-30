# -*- coding: utf-8 -*-

import qgis.core as qgCor

_TEMPLATES = dict = {
    "within": "within(centroid($geometry), geometry(get_feature_by_id('{}', {})))",
    "intersects": "intersects($geometry, geometry(get_feature_by_id('{}', {})))"
}


class QvLlegendaMascara:

    def __init__(self, legend, layer, polygonId, template='within'):
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
        self.maskInit()

    def setTemplate(self, template):
        return _TEMPLATES.get(template, 'within')

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

    def switch(self, layer, active=None):
        if not self.getLabelsProps(layer):
            return
        if active is None:
            active = not self.isActive(layer)
        if active:
            prop = qgCor.QgsProperty()
            prop.setExpressionString(self.calcExpression())
            self.props.setProperty(self.key, prop)
        else:
            self.props.setProperty(self.key, None)
        self.sets.setDataDefinedProperties(self.props)
        self.labels.setSettings(self.sets)
        layer.setLabeling(self.labels)

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
        leyenda.move(0, 0)
        leyenda.show()

        canvas.setWindowTitle('Test Mask Labels')
        canvas.move(leyenda.width(), 0)
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
        leyenda.accions.afegirAccio('rotationSwitch', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'layer':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('testLabels')
                leyenda.menuAccions.append('maskLabels')
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('maskSwitch')
                leyenda.menuAccions.append('rotationSwitch')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
