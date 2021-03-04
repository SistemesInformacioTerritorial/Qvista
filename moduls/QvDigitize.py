# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvDigitizeFeature import QvDigitizeFeature
from moduls.QvDigitizeContext import QvDigitizeContext
from moduls.QvAccions import QvAccions
from moduls.QvSingleton import singleton

from configuracioQvista import imatgesDir

import os

@singleton
class QvDigitizeWidget(qgGui.QgsAdvancedDigitizingDockWidget):

    def __init__(self, canvas, keys="Ctrl+4"):
        self.canvas = canvas
        super().__init__(self.canvas)
        self.setWindowTitle("Digitalització avançada")
        self.shortcut = qtWdg.QShortcut(qtGui.QKeySequence(keys), self.canvas)
        self.setAllowedAreas(qtCor.Qt.LeftDockWidgetArea)
        self.hide()


@singleton
class QvSnapping:

    def __init__(self, canvas):
        self.canvas = canvas

    def config(self, enabled=True):
        snap = self.canvas.snappingUtils().config()
        snap.setType(qgCor.QgsSnappingConfig.Vertex)
        snap.setUnits(qgCor.QgsTolerance.Pixels)
        snap.setTolerance(10)
        snap.setMode(qgCor.QgsSnappingConfig.AllLayers)
        snap.setIntersectionSnapping(False)
        snap.setEnabled(enabled)
        self.canvas.snappingUtils().setConfig(snap)

    def isEnabled(self):
        return self.canvas.snappingUtils().config().enabled()

    def toggleEnabled(self):
        snap = self.canvas.snappingUtils().config()
        snap.setEnabled(not snap.enabled())
        self.canvas.snappingUtils().setConfig(snap)

class QvDigitize:

    def __init__(self, llegenda):
        self.llegenda = llegenda
        self.canvas = self.llegenda.canvas
        self.widget = QvDigitizeWidget(self.canvas)
        self.widget.shortcut.activated.connect(self.widgetVisible)
        self.snap = QvSnapping(self.canvas)
        self.snap.config()
        self.llista = {}
        self.accions = QvAccions()
        self.menuAccions = []
        self.menu = None

    def widgetVisible(self):
        if self.started():
            self.widget.toggleUserVisible()
        else:
            self.widget.hide()

    def nouProjecte(self):
        self.llista = {}

    ### Gestión de lista de capas editables

    def altaInfoCapa(self, capa):
        if QvDigitizeContext.testEditable(capa):
            self.modifInfoCapa(capa, None)

    def modifInfoCapa(self, capa, df):
        self.llista[capa.id()] = df
        self.llegenda.actIconesCapa(capa)

    def bajaInfoCapa(self, capaId):
        if capaId in self.llista:
            del self.llista[capaId]

    def infoCapa(self, capa):
        if capa.id() in self.llista:
            df = self.llista[capa.id()]
            if df is None:
                return False, None  # Edición activable
            else:
                return True, df     # Edición activada
        return None, None           # Edición prohibida

    ### Inicio / fin de edición de capa

    def activaCapa(self, switch):
        capa = self.llegenda.currentLayer()
        if capa is None or capa.type() != qgCor.QgsMapLayerType.VectorLayer: return
        estado, df = self.infoCapa(capa)
        if estado is None: return
        if switch:
            if not estado: df = QvDigitizeFeature(self, capa)
            df.start()
        elif estado:
            df.stop()

    def setAccions(self, parent=None):
        self.accions = QvAccions()

        act = qtWdg.QAction('Dibuixa nou element', parent)
        act.setEnabled(False)
        self.accions.afegirAccio('newElement', act)

        act = qtWdg.QAction("Modifica geometria d'element", parent)
        act.setEnabled(False)
        self.accions.afegirAccio('modGeometria', act)

        act = qtWdg.QAction('Esborra element(s) seleccionat(s)', parent)
        act.setEnabled(False)
        self.accions.afegirAccio('delElements', act)

        act = qtWdg.QAction('Desfés canvi', parent)
        act.setEnabled(False)
        self.accions.afegirAccio('undo', act)

        act = qtWdg.QAction('Refés canvi', parent)
        act.setEnabled(False)
        self.accions.afegirAccio('redo', act)

        act = qtWdg.QAction("Activa l'ajust de digitalització", parent)
        act.setCheckable(True)
        act.triggered.connect(self.snap.toggleEnabled)
        act.setChecked(self.snap.isEnabled())
        act.setEnabled(self.started())
        self.accions.afegirAccio('snap', act)

        act = qtWdg.QAction('Mostra digitalització avançada', parent)
        act.setCheckable(True)
        act.triggered.connect(self.widgetVisible)
        act.setChecked(self.widget.isVisible())
        act.setEnabled(self.started())
        self.accions.afegirAccio('showWidget', act)

        act = qtWdg.QAction('Finalitza edició de capa activa', parent)
        act.setEnabled(False)
        self.accions.afegirAccio('endLayer', act)

        act = qtWdg.QAction('Finalitza totes les edicions', parent)
        act.triggered.connect(self.stop)
        act.setEnabled(self.started())
        if act.isEnabled():
            act.setText(act.text() + "\tCtrl+.") 
        self.accions.afegirAccio('endAll', act)

    def modAccions(self, df):
        if self.accions is None or df is None: return
        act = self.accions.accio('newElement')
        if act is not None:
            if df:
                act.triggered.connect(df.new)
                act.setText("Dibuixa nou element\tCtrl++")
                act.setEnabled(True)
            else:
                act.setEnabled(False)
        act = self.accions.accio('modGeometria')
        if act is not None:
            if df:
                act.setText(f"Modifica {df.nomGeometria()} d'element\tCtrl+*")
                act.triggered.connect(df.redraw)
                act.setEnabled(True)
            else:
                act.setEnabled(False)
        act = self.accions.accio('delElements')
        if act is not None:
            if df:
                act.triggered.connect(df.delete)
                act.setEnabled(df.capa.selectedFeatureCount())
            else:
                act.setEnabled(False)
        txt = "Esborra element(s) seleccionat(s)"
        if act.isEnabled(): txt += "\tCtrl+-"
        act.setText(txt)
        act = self.accions.accio('undo')
        if act is not None:
            if df:
                act.triggered.connect(df.undo)
                act.setEnabled(df.canUndo())
            else:
                act.setEnabled(False)
            txt = "Desfés canvi"
            if act.isEnabled(): txt += "\tCtrl+Z"
            act.setText(txt)
        act = self.accions.accio('redo')
        if act is not None:
            if df:
                act.triggered.connect(df.redo)
                act.setEnabled(df.canRedo())
            else:
                act.setEnabled(False)
            txt = "Refés canvi"
            if act.isEnabled(): txt += "\tCtrl+Y"
            act.setText(txt)
        act = self.accions.accio('endLayer')
        if act is not None:
            if df:
                act.triggered.connect(df.stop)
                act.setEnabled(True)
            else:
                act.setEnabled(False)

    def setMenuAccions(self):
        self.menuAccions = []
        # Grupo 1 - Comandos de edición
        self.menuAccions += ['newElement', 'modGeometria', 'delElements']
        self.menuAccions += ['separator']
        # Grupo 2 - Undo / Redo
        self.menuAccions += ['undo', 'redo']
        self.menuAccions += ['separator']
        # Grupo 3: Parámetros de edición y snap
        self.menuAccions += ['snap', 'showWidget']
        self.menuAccions += ['separator']
        # Grupo 4: Cierre de ediciones
        self.menuAccions += ['endLayer', 'endAll']

    def dfCommand(self, name):
        df = self.df()
        if df is not None:
            try:
                method = getattr(df, name)
                method()
            except Exception as e:
                print(str(e))

    def setShortcuts(self, parent):
        self.ctrlPlus = qtWdg.QShortcut("Ctrl++", parent)
        self.ctrlPlus.activated.connect(lambda: self.dfCommand('new'))
        self.ctrlAsterisk = qtWdg.QShortcut("Ctrl+*", parent)
        self.ctrlAsterisk.activated.connect(lambda: self.dfCommand('redraw'))
        self.ctrlMinus = qtWdg.QShortcut("Ctrl+-", parent)
        self.ctrlMinus.activated.connect(lambda: self.dfCommand('delete'))
        self.ctrlZ = qtWdg.QShortcut("Ctrl+Z", parent)
        self.ctrlZ.activated.connect(lambda: self.dfCommand('undo'))
        self.ctrlY = qtWdg.QShortcut("Ctrl+Y", parent)
        self.ctrlY.activated.connect(lambda: self.dfCommand('redo'))
        self.ctrlDot = qtWdg.QShortcut("Ctrl+.", parent)
        self.ctrlDot.activated.connect(self.stop)

    def setMenu(self, menu):
        self.menu = menu
        self.setShortcuts(self.menu.parent().parent()) # Se asigna a QVista (QMainWindow)
        self.setMenuAccions()
        self.menu.aboutToShow.connect(self.showMenu)
        return self.menu

    def df(self):
        val = None
        capa = self.llegenda.currentLayer()
        if capa is not None:
            val = self.edition(capa)
        return val

    def showMenu(self):
        if self.menu is None: return
        self.setAccions()
        self.modAccions(self.df())
        self.accions.menuAccions(self.menuAccions, menu=self.menu)

    ### Gestión de estados

    def editing(self, capa):
        ret, _ = self.infoCapa(capa)
        if ret is None or not ret:
            return False
        else:
            return True

    def edition(self, capa):
        ret, df = self.infoCapa(capa)
        if ret is None or not ret:
            return None
        else:
            return df

    def editable(self):
        if len(self.llista) > 0:
            return True
        else:
            return False

    def editions(self):
        for df in self.llista.values():
            if df is not None:
                yield df

    def started(self):
        for df in self.editions():
            return True
        return False

    def modified(self):
        for df in self.editions():
            if df.modified():
                return True
        return False

    def finish(self, save):
        self.widget.hide()
        for df in self.editions():
            df.finish(save)
    
    def end(self):
        self.finish(True)

    def cancel(self):
        self.finish(False)

    def stop(self):
        if self.modified():
            r = qtWdg.QMessageBox.question(self.llegenda, "Finalitza edicions del mapa",
                                           f"Vol desar les modificacions realitzades al mapa o descartar-les totes?", 
                                           buttons = qtWdg.QMessageBox.Save | qtWdg.QMessageBox.Discard | qtWdg.QMessageBox.Cancel,
                                           defaultButton = qtWdg.QMessageBox.Save)
            if r == qtWdg.QMessageBox.Save: self.end()
            elif r == qtWdg.QMessageBox.Discard: self.cancel()
        else:
            self.cancel()
