# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

from moduls.QvDigitizeFeature import QvDigitizeFeature
from moduls.QvDigitizeContext import QvDigitizeContext
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
        self.llista = {}
        self.menu = None
        self.editable = False

    def widgetVisible(self):
        if self.started():
            self.widget.toggleUserVisible()
        else:
            self.widget.hide()

    def nouProjecte(self):
        self.llista = {}
        self.editable = False
        self.snap.config()

    def modifInfoCapa(self, capa, val):
        self.llista[capa.id()] = val
        if val: self.editable = True
        self.llegenda.actIconesCapa(capa)

    def iniInfoCapa(self, capa):
        self.modifInfoCapa(capa, QvDigitizeContext.testEditable(capa))

    def testInfoCapa(self, val):
        if isinstance(val, QvDigitizeFeature):
            return True, val    # Edición activada
        elif val:
            return False, None  # Edición activable
        return None, None       # Edición prohibida

    def infoCapa(self, capa):
        val = self.llista.get(capa.id())
        return self.testInfoCapa(val)

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

    def activaCapa(self, switch):
        capa = self.llegenda.currentLayer()
        estado, df = self.infoCapa(capa)
        if estado is None: return
        if switch:
            if not estado:
                df = QvDigitizeFeature(self.llegenda, capa)
            df.start()
        elif estado:
            df.stop()

    def setMenu(self, menu=None):
        self.menu = menu
        if self.started():
            if self.menu is None:
                self.menu = qtWdg.QMenu('Edició')
            self.menu.setIcon(qtGui.QIcon(os.path.join(imatgesDir, 'edit_on.png')))
            # Grupo 1: Parámetros de edición y snap
            act = self.menu.addAction("Activa l'ajust de digitalització", self.snap.toggleEnabled)
            act.setCheckable(True)
            act.setChecked(self.snap.isEnabled())
            act = self.menu.addAction("Mostra digitalització avançada", self.widgetVisible)
            act.setCheckable(True)
            act.setChecked(self.widget.isVisible())
            self.menu.addSeparator()
            # Grupo 2: Fin de ediciones
            self.menu.addAction("Finalitza les edicions", self.stop)
        return self.menu

    def editions(self):
        for val in self.llista.values():
            _, df = self.testInfoCapa(val)
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

