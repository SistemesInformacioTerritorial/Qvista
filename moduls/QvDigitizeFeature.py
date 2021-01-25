# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvAtributsForms import QvFormAtributs
from configuracioQvista import imatgesDir

import os

# 
# TODO
#
# - Al salir de qVista, controlar si hay ediciones abiertas con modificaciones pendientes
# - Leyenda: las opciones desactivadas del menú no se ven muy bien
# - Scroll a elemento de tabla no funciona con los nuevos (fid = 0)
# 
# https://docs.qgis.org/3.16/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html
# 

class QvDigitizeFeature(qgGui.QgsMapToolDigitizeFeature):

    def __init__(self, llegenda, capa):
        if llegenda.canvas is None or capa.type() != qgCor.QgsMapLayerType.VectorLayer:
            return
        if len(qgGui.QgsGui.editorWidgetRegistry().factories()) == 0:
            qgGui.QgsGui.editorWidgetRegistry().initEditors()
        self.llegenda = llegenda
        self.capa = capa
        self.project = self.llegenda.project
        self.canvas = self.llegenda.canvas
        self.atributs = self.llegenda.atributs
        super().__init__(self.canvas, self.llegenda.digitize.widget)
        self.setLayer(self.capa)
        self.signal = None
        self.menu = None

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

    def unset(self):
        self.iniSignal()
        self.clean()
        self.canvas.unsetMapTool(self)

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
        if self.capa.isEditable():
            if save:
                b = self.capa.commitChanges()
            else:
                b = self.capa.rollBack()
            self.canvas.unsetMapTool(self)
            self.llegenda.digitize.modifInfoCapa(self.capa, True)
            return b
        else:
            return False

    def stop(self):
        if self.modified():
            r = qtWdg.QMessageBox.question(self.llegenda, "Finalitza edició de capa",
                                           f"Vol desar les modificacions realitzades a la capa '{self.capa.name()}' o descartar-les?", 
                                           buttons = qtWdg.QMessageBox.Save | qtWdg.QMessageBox.Discard | qtWdg.QMessageBox.Cancel,
                                           defaultButton = qtWdg.QMessageBox.Save)
            if r == qtWdg.QMessageBox.Save: self.end()
            elif r == qtWdg.QMessageBox.Discard: self.cancel()
        else:
            self.cancel()

    # def commit(self):
    #     return self.layer.commitChanges(False)

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

    def canUndo(self):
        return self.capa.undoStack().canUndo()

    def undo(self):
        if self.canUndo():
            self.capa.undoStack().undo()
            self.atributs.tabTaula(self.capa, True)
            self.capa.repaintRequested.emit()

    def canRedo(self):
        return self.capa.undoStack().canRedo()

    def redo(self):
        if self.canRedo():
            self.capa.undoStack().redo()
            self.atributs.tabTaula(self.capa, True)
            self.capa.repaintRequested.emit()

    def new(self):
        if self.capa.isEditable():
            self.newSignal(self.newFeature)
            self.canvas.setMapTool(self)
            self.canvas.activateWindow()

    # def canvasReleaseEvent(self, e):
    #     if e.button() == qtCor.Qt.RightButton:
    #         print("Botón derecho 1")
    #     super().canvasReleaseEvent(e)

    # def cadCanvasReleaseEvent(self, e):
    #     if e.button() == qtCor.Qt.RightButton:
    #         print("Botón derecho 2")
    #     super().cadCanvasReleaseEvent(e)
    
    def newFeature(self, feature):
        self.dialog = QvFormAtributs.create(self.capa, feature, self.canvas, self.atributs, new=True)
        if self.dialog.exec_() == qtWdg.QDialog.Accepted:
            self.feature = self.dialog.reg
        self.dialog = None

    def setMenu(self):
        self.menu = qtWdg.QMenu('Edició')
        self.menu.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_on.png')))
        # Grupo 1 - Comandos de edición
        self.menu.addAction('Nou element', self.new)
        act = self.menu.addAction('Esborra seleccionat(s)', self.capa.deleteSelectedFeatures)
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
