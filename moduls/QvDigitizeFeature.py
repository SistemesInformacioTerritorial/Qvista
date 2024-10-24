# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvAtributsForms import QvFormAtributs
from moduls.QvEinesGrafiques import QvSeleccioElement
from moduls.QvDigitizeContext import QvDigitizeContext
from configuracioQvista import imatgesDir

import os

# 
# TODO
#
# - Edición de vértices
# - Repasar activacion dirty bit
# - Pruebas edición tabla Oracle
# - Edicion de geometría: QgsVectorLayerEditUtils
#
# - Geocodificación número 0
# - L:\Dades\SIT\VistaMonitor que apunte al nuevo QGIS
# 
# https://docs.qgis.org/3.16/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html
# 

class QvDigitizeFeature(qgGui.QgsMapToolDigitizeFeature):

    def __init__(self, digitize, capa):
        if digitize.llegenda is None or digitize.llegenda.canvas is None or capa.type() != qgCor.QgsMapLayerType.VectorLayer:
            return
        if len(qgGui.QgsGui.editorWidgetRegistry().factories()) == 0:
            qgGui.QgsGui.editorWidgetRegistry().initEditors()
        self.digitize = digitize
        self.llegenda = self.digitize.llegenda
        self.capa = capa
        self.project = self.llegenda.project
        self.canvas = self.llegenda.canvas
        self.atributs = self.llegenda.atributs
        super().__init__(self.canvas, self.llegenda.digitize.widget)
        self.setLayer(self.capa)
        self.signal = None
        self.menu = None
        self.tool = None
        self.ignoreRightButton = False

    def cadCanvasReleaseEvent(self, event):
        if event.button() == qtCor.Qt.RightButton:
            # Se ignora botón derecho cuando volvemos de otro tool
            if self.ignoreRightButton:
                self.ignoreRightButton = False
                return
            # Finaliza tool de dibujo con botón derecho cuando no hay puntos dibujados
            if (self.tool == self) and self.size() == 0:
                # Aunque, si estamos redibujando, vuelve al principio para seleccionar otro elemento
                redraw = (self.signal == self.redrawFeature)
                self.unset()
                if redraw: self.redraw()
                return
        super().cadCanvasReleaseEvent(event)

    def iniSignal(self):
        if self.signal is not None:
            self.digitizingCompleted.disconnect(self.signal)
            self.llegenda.currentLayerChanged.disconnect(self.unset)
            self.signal = None

    def newSignal(self, signal):
        if self.signal is None:
            self.signal = signal
            self.digitizingCompleted.connect(self.signal)
            self.llegenda.currentLayerChanged.connect(self.unset)
        else:
            if self.signal != signal:
                self.digitizingCompleted.disconnect(self.signal)
                self.signal = signal
                self.digitizingCompleted.connect(self.signal)

    def go(self, tool, removeSelection):
        self.tool = tool
        if removeSelection:
            self.capa.removeSelection()
        self.canvas.setMapTool(self.tool)
        self.canvas.activateWindow()

    def unset(self):
        self.iniSignal()
        self.clean()
        if self.tool is not None:
            self.canvas.unsetMapTool(self.tool)
            self.tool = None

    def start(self):
        if self.capa.isEditable() or self.capa.startEditing():
            self.iniSignal()
            self.llegenda.digitize.modifInfoCapa(self.capa, self)
            self.capa.editBuffer().layerModified.connect(lambda: self.llegenda.actIconesCapa(self.capa))
            self.llegenda.veureCapa(self.capa)
            self.llegenda.showFeatureTable()
            return True
        else:
            return False

    def finish(self, save):
        ok = False
        if self.capa.isEditable():
            self.canvas.unsetMapTool(self)
            if save:
                ok = self.capa.commitChanges()
            else:
                ok = self.capa.rollBack()
            if ok:
                self.llegenda.digitize.modifInfoCapa(self.capa, None)
            else:
                self.errors()
        return ok

    def errors(self):
        try:
            err =  self.capa.commitErrors()
            sep = "\n"
            msg = f"S'han produït errors en la capa '{self.capa.name()}':{sep}{sep}{sep.join(err)}"
            qtWdg.QMessageBox.critical(self.llegenda, "Error al finalitzar edició de capa", msg)
        except Exception as e:
            print(str(e))
            
    def stop(self):
        if self.modified():
            r = qtWdg.QMessageBox.question(self.llegenda, "Finalitza edició de capa",
                                           f"Vol desar les modificacions realitzades a la capa '{self.capa.name()}' o descartar-les?", 
                                           buttons = qtWdg.QMessageBox.Save | qtWdg.QMessageBox.Discard | qtWdg.QMessageBox.Cancel,
                                           defaultButton = qtWdg.QMessageBox.Save)
            if r == qtWdg.QMessageBox.Save: return self.end()
            elif r == qtWdg.QMessageBox.Discard: return self.cancel()
        else:
            return self.cancel()

    # def commit(self):
    #     return self.layer.commitChanges(False)

    def editing(self):
        try:
            buff = self.capa.editBuffer()
            if buff is None:
                return False
            return True
        except:
            return False

    def modified(self):
        try:
            buff = self.capa.editBuffer()
            if buff is None:
                return False
            return buff.isModified()
        except:
            return False

    def end(self):
        return self.finish(True)

    def cancel(self):
        return self.finish(False)

    ######################### Nuevo elemento

    def new(self, signal=None):
        if self.capa.isEditable():
            if signal:
                self.newSignal(signal)
                self.go(self, False)
            else:
                self.newSignal(self.newFeature)
                self.go(self, True)

    def newFeature(self, feature):
        self.dialog = QvFormAtributs.create(self.capa, feature, self.canvas, self.atributs, new=True)
        self.dialog.exec_()
        self.dialog = None

    ######################### Redibujar elemento

    def redraw(self):
        if self.capa.isEditable():
            if self.tool == self: self.unset()
            self.capa.removeSelection()
            tool = QvSeleccioElement(self.canvas, self.llegenda, senyal=True)
            tool.elementsSeleccionats.connect(self.selectFeature)
            self.go(tool, True)

    def selectFeature(self, layer, features):
        if layer.id() != self.capa.id():
            return
        self.feature = features[0]        
        QvDigitizeContext.selectAndScrollFeature(self.feature.id(), self.capa, self.atributs)
        self.canvas.unsetMapTool(self.tool)
        self.new(self.redrawFeature)

    def redrawFeature(self, feature):
        self.capa.changeGeometry(self.feature.id(), feature.geometry())
        self.capa.removeSelection()
        self.unset()
        self.redraw()

    ######################### Borrar elemento(s)

    def delete(self):
        if self.tool == self: self.unset()
        self.capa.deleteSelectedFeatures()
        self.atributs.tabTaula(self.capa)

    ######################### Undo y Redo

    def canUndo(self):
        return self.capa.undoStack().canUndo()

    def undo(self):
        if self.canUndo():
            self.capa.undoStack().undo()
            self.atributs.tabTaula(self.capa)
            self.capa.repaintRequested.emit()

    def canRedo(self):
        return self.capa.undoStack().canRedo()

    def redo(self):
        if self.canRedo():
            self.capa.undoStack().redo()
            self.atributs.tabTaula(self.capa)
            self.capa.repaintRequested.emit()

    def nomGeometria(self):
        if self.capa:
            if self.capa.geometryType() == qgCor.QgsWkbTypes.PointGeometry:
                return 'punt'
            elif self.capa.geometryType() == qgCor.QgsWkbTypes.LineGeometry:
                return 'línia'
            elif self.capa.geometryType() == qgCor.QgsWkbTypes.PolygonGeometry:
                return 'polígon'
        return 'geometria'

    def setMenu(self):
        self.unset()
        self.menu = qtWdg.QMenu('Edició')
        self.menu.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_on.png')))
        # Grupo 1 - Comandos de edición
        self.menu.addAction('Nou element', self.new)
        if self.capa.geometryType() == qgCor.QgsWkbTypes.PointGeometry:
            tipo = 'punt'
        elif self.capa.geometryType() == qgCor.QgsWkbTypes.LineGeometry:
            tipo = 'línia'
        elif self.capa.geometryType() == qgCor.QgsWkbTypes.PolygonGeometry:
            tipo = 'polígon'
        else:
            tipo = 'geometria'
        self.menu.addAction(f"Modifica {tipo} d'element", self.redraw)
        act = self.menu.addAction('Esborra seleccionat(s)', self.delete)
        act.setEnabled(self.capa.selectedFeatureCount())
        self.menu.addSeparator()
        # Grupo 2 - Undo / Redo
        act = self.menu.addAction('Desfés canvi', self.undo)
        act.setEnabled(self.canUndo())
        act = self.menu.addAction('Refés canvi', self.redo)
        act.setEnabled(self.canRedo())
        self.menu.addSeparator()
        # Grupo 3: Cierre de edición
        self.menu.addAction('Finalitza edició', self.stop)
        return self.menu

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

        # QvDigitizeFeature.configSnap(canvas)
        # digitList = {}
        # for capa in leyenda.capes():
        #     if QvDigitizeContext.testEditable(capa):
        #         digitList[capa.id()] = QvDigitizeFeature(leyenda, capa)
                
        # Acciones de usuario para el menú

        # def editStart():
        #     df = leyenda.currentDigitize()
        #     if df: df.start()

        # def editNew():
        #     df = leyenda.currentDigitize()
        #     if df: df.new()

        # # def editCommit():
        # # df = leyenda.currentDigitize()
        # #     if df: df.commit()

        # def editEnd():
        #     df = leyenda.currentDigitize()
        #     if df: df.end()

        # def editCancel():
        #     df = leyenda.currentDigitize()
        #     if df: df.cancel()

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

        # act = qtWdg.QAction()
        # act.setText("Edit: start")
        # act.triggered.connect(editStart)
        # leyenda.accions.afegirAccio('Edit: start', act)

        # act = qtWdg.QAction()
        # act.setText("Edit: new")
        # act.triggered.connect(editNew)
        # leyenda.accions.afegirAccio('Edit: new', act)

        # act = qtWdg.QAction()
        # act.setText("Edit: commit")
        # act.triggered.connect(editCommit)
        # leyenda.accions.afegirAccio('Edit: commit', act)

        # act = qtWdg.QAction()
        # act.setText("Edit: end")
        # act.triggered.connect(editEnd)
        # leyenda.accions.afegirAccio('Edit: end', act)

        # act = qtWdg.QAction()
        # act.setText("Edit: cancel")
        # act.triggered.connect(editCancel)
        # leyenda.accions.afegirAccio('Edit: cancel', act)

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
            # elif tipo == 'layer':
            #     estado, _ = leyenda.stateDigitize()
            #     if estado is None:
            #         return
            #     if estado:
            #         leyenda.menuAccions.append('separator')
            #         leyenda.menuAccions.append('Edit: new')
            #         leyenda.menuAccions.append('Edit: commit')
            #         leyenda.menuAccions.append('Edit: end')
            #         leyenda.menuAccions.append('Edit: cancel')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
