# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtSql as qtSql

from moduls.QvSingleton import singleton
from moduls.QvAtributs import QvFitxesAtributs

class QvDigitizeFeature(qgGui.QgsMapToolDigitizeFeature):

    @classmethod
    def new(cls, layer, canvas, attributes=None):
        try:
            if layer.type() == qgCor.QgsMapLayerType.VectorLayer:
                if layer.isEditable() or layer.startEditing():
                    dig = cls(layer, canvas, attributes)
                    dig.newInit()
        except Exception as e:
            print('Error QvDigitizeFeature.new: ' + str(e))

    def __init__(self, layer, canvas, attributes=None):
        if len(qgGui.QgsGui.editorWidgetRegistry().factories()) == 0:
            qgGui.QgsGui.editorWidgetRegistry().initEditors()
        self.layer = layer
        self.canvas = canvas
        self.attributes = attributes
        self.widget = QvDigitizeWidget(self.canvas)
        super().__init__(self.canvas, self.widget)
        self.setLayer(self.layer)
        self.snap = QvSnapping(self.canvas)
        # self.activate()

    # def canvasReleaseEvent(self, e):
    #     if e.button() == qtCor.Qt.RightButton:
    #         print("Botón derecho 1")
    #     super().canvasReleaseEvent(e)

    # def cadCanvasReleaseEvent(self, e):
    #     if e.button() == qtCor.Qt.RightButton:
    #         print("Botón derecho 2")
    #     super().cadCanvasReleaseEvent(e)

    def newInit(self):
        self.digitizingCompleted.connect(self.newFeature)
        self.digitizingFinished.connect(self.end)
        self.canvas.setMapTool(self)
        self.canvas.activateWindow()

    def newFeature(self, feature):
        # if self.layer.isEditable():
        #     self.layer.commitChanges()
            # self.layer.commitErrors()
        print('New feature')
        dialog = qgGui.QgsAttributeDialog(self.layer, feature, False, self.canvas)
        dialog.setMode(qgGui.QgsAttributeEditorContext.AddFeatureMode)
        dialog.setAttribute(qtCor.Qt.WA_DeleteOnClose)
        if dialog.exec_() == qtWdg.QDialog.Accepted:
            # self.feature = self.dialog.feature()
            self.layer.commitChanges() # Si no, no se graba
            if self.attributes is not None:
                self.attributes.tabTaula(self.layer, True)
                # Falta refrescar tabla datos
        # self.canvas.unsetLastMapTool()

    def end(self):
        if self.layer.isEditable():
            self.layer.rollBack()
        # self.widget.clear()
        # self.widget.hide()
        print('End')

@singleton
class QvDigitizeWidget(qgGui.QgsAdvancedDigitizingDockWidget):

    def __init__(self, canvas, keys="Ctrl+4"):
        self.canvas = canvas
        super().__init__(self.canvas)
        self.setWindowTitle("Digitalització avançada")
        self.shortcut = qtWdg.QShortcut(qtGui.QKeySequence(keys), self.canvas)
        self.shortcut.activated.connect(self.toggleUserVisible)

class QvSnapping(qgCor.QgsSnappingConfig):

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setEnabled(True)
        self.setType(qgCor.QgsSnappingConfig.VertexAndSegment)
        self.setUnits(qgCor.QgsTolerance.Pixels)
        self.setTolerance(10)
        self.setMode(qgCor.QgsSnappingConfig.AllLayers)
        self.setIntersectionSnapping(True)
        self.snapUtils = qgGui.QgsMapCanvasSnappingUtils(self.canvas)
        self.snapUtils.setConfig(self)
        self.canvas.setSnappingUtils(self.snapUtils)

if __name__ == "__main__":

    # https://anitagraser.com/pyqgis-101-introduction-to-qgis-python-programming-for-non-programmers/pyqgis101-creating-editing-a-new-vector-layer/

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = QvCanvas()
        atributos = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atributos)

        # inicial = cfg.projecteInicial
        inicial = 'd:/temp/TestDigitize.qgs'
        leyenda.readProject(inicial)

        leyenda.setWindowTitle('Llegenda')
        leyenda.setGeometry(100, 50, 400, 600)
        leyenda.show()

        canvas.setWindowTitle('Canvas - ' + inicial)
        canvas.setGeometry(510, 50, 900, 600)
        canvas.show()

        atributos.setWindowTitle('Atributs')
        atributos.setGeometry(100, 700, 1310, 300)
        leyenda.obertaTaulaAtributs.connect(atributos.show)

        # Acciones de usuario para el menú

        def testDigitize():
            print('ini test digitize')
            QvDigitizeFeature.new(leyenda.currentLayer(), canvas, atributos)
            print('fin test digitize')

        def writeProject():
            print('write file')
            leyenda.project.write()

        def openProject():
            dialegObertura = qtWdg.QFileDialog()
            dialegObertura.setDirectoryUrl(qtCor.QUrl('D:/Temp/'))
            mapes = "Tots els mapes acceptats (*.qgs *.qgz);; " \
                    "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)"
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis",
                                                      "D:/Temp/", mapes)
            if nfile != '':
                print('read file ' + nfile)
                ok = leyenda.readProject(nfile)
                if ok:
                    canvas.setWindowTitle('Canvas - ' + nfile)
                else:
                    print(leyenda.project.error().summary())

        act = qtWdg.QAction()
        act.setText("Test Digitize")
        act.triggered.connect(testDigitize)
        leyenda.accions.afegirAccio('testDigitize', act)

        act = qtWdg.QAction()
        act.setText("Desa projecte")
        act.triggered.connect(writeProject)
        leyenda.accions.afegirAccio('writeProject', act)

        act = qtWdg.QAction()
        act.setText("Obre projecte")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('writeProject')
                leyenda.menuAccions.append('openProject')
            elif tipo == 'layer':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('testDigitize')


        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
