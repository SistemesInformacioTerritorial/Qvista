# -*- coding: utf-8 -*-

import qgis.core as qgCor


class QvLlegendaMascara:

    def __init__(self, legend, layer, polygonId):
        self.legend = legend
        self.layer = layer
        self.layerId = self.layer.id()
        self.polygonId = polygonId
        self.template = "within(centroid($geometry), geometry(get_feature_by_id('{}', {})))"
        self.key = qgCor.QgsPalLayerSettings.Show
        self.active = False
        self.labels = None
        self.sets = None
        self.props = None
        self.maskInit()

    def calcExpression(self):
        return self.template.format(self.layerId, self.polygonId)

    # Funciones de 1 capa
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

    def switch(self, layer, active):
        if not self.getLabelsProps(layer):
            return

        if active:
            prop = qgCor.QgsProperty()
            prop.setExpressionString(self.calcExpression())
            self.props.setProperty(self.key, prop)
        else:
            self.props.setProperty(self.key, None)

        self.sets.setDataDefinedProperties(self.props)
        self.labels.setSettings(self.sets)
        layer.setLabeling(self.labels)

    def active(self, layer):
        self.switch(layer, True)

    def disactive(self, layer):
        self.switch(layer, False)

    # Funciones de todas las capas
    def switchAll(self, active):
        self.active = active
        for layer in self.legend.project.mapLayers():
            self.switch(self.legend.project.mapLayer(layer), active)

    def activeAll(self):
        self.switchAll(True)

    def disactiveAll(self):
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
            self.activeAll()
            self.legend.canvas.clearCache()
            self.legend.canvas.refresh()

    def maskOff(self):
        if self.active:
            self.disactiveAll()
            self.legend.canvas.clearCache()
            self.legend.canvas.refresh()


if __name__ == "__main__":

    import qgis.gui as qgGui
    import qgis.PyQt.QtWidgets as qtWdg

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvAtributs import QvAtributs

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canv = qgGui.QgsMapCanvas()
        atrib = QvAtributs(canv)
        leyenda = QvLlegenda(canv, atrib)

        leyenda.project.read('D:/qVista/EjemploMapSin.qgs')

        canv.setWindowTitle('Canvas')
        canv.show()
        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        # Acciones de prueba de máscara para etiquetas

        leyenda.mask = QvLlegendaMascara(leyenda, leyenda.capaPerNom("Zones districtes"), 10)

        def testLabels():
            print("Test Labels")
            if leyenda.mask is None:
                print("- Sin máscara")
                return
            capa = leyenda.currentLayer()
            print("Capa: {}".format(capa.name()))
            if not leyenda.mask.labelsEnabled(capa):
                print("- Sin etiquetas")
                return
            on = leyenda.mask.isActive(capa)
            if on:
                print("- Activada")
            else:
                print("- No activada")

        def maskLabels():
            print("Mask Labels")
            if leyenda.mask is None:
                print("- Sin máscara")
                return
            capa = leyenda.currentLayer()
            on = leyenda.mask.isActive(capa)
            leyenda.mask.switch(capa, not on)
            if leyenda.capaVisible(capa):
                canv.clearCache()
                canv.refresh()

        def maskOn():
            if leyenda.mask is not None:
                leyenda.mask.maskOn()

        def maskOff():
            if leyenda.mask is not None:
                leyenda.mask.maskOff()

        # Acciones de usuario para el menú

        act = qtWdg.QAction()
        act.setText("Test Labels")
        act.triggered.connect(testLabels)
        leyenda.accions.afegirAccio('testLabels', act)

        act = qtWdg.QAction()
        act.setText("Mask Labels")
        act.triggered.connect(maskLabels)
        leyenda.accions.afegirAccio('maskLabels', act)

        act = qtWdg.QAction()
        act.setText("Mask Labels On")
        act.triggered.connect(maskOn)
        leyenda.accions.afegirAccio('maskOn', act)

        act = qtWdg.QAction()
        act.setText("Mask Labels Off")
        act.triggered.connect(maskOff)
        leyenda.accions.afegirAccio('maskOff', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'layer':
                leyenda.menuAccions.append('testLabels')
                leyenda.menuAccions.append('maskLabels')
            if tipo == 'none':
                leyenda.menuAccions.append('maskOn')
                leyenda.menuAccions.append('maskOff')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
