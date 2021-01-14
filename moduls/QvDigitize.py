# -*- coding: utf-8 -*-

import qgis.core as qgCor
# import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
# import qgis.PyQt.QtGui as qtGui
# import qgis.PyQt.QtCore as qtCor

from moduls.QvDigitizeFeature import QvDigitizeFeature
from moduls.QvDigitizeContext import QvDigitizeContext

class QvDigitize:

    def __init__(self, llegenda):
        self.llegenda = llegenda
        self.llista = {}
        self.menu = None

    def configSnap(self, canvas):
        snap = canvas.snappingUtils().config()
        snap.setType(qgCor.QgsSnappingConfig.VertexAndSegment)
        snap.setUnits(qgCor.QgsTolerance.Pixels)
        snap.setTolerance(10)
        snap.setMode(qgCor.QgsSnappingConfig.AllLayers)
        snap.setIntersectionSnapping(True)
        snap.setEnabled(True)
        canvas.snappingUtils().setConfig(snap)

    def nouProjecte(self, canvas):
        self.llista = {}
        self.configSnap(canvas)

    def modifInfoCapa(self, capa, val):
        self.llista[capa.id()] = val
        self.llegenda.actIconesCapa(capa)

    def iniInfoCapa(self, capa):
        self.modifInfoCapa(capa, QvDigitizeContext.testEditable(capa))

    def testInfoCapa(self, val):
        if isinstance(val, QvDigitizeFeature):
            return True, val    # Edición activada
        elif val:
            return False, None  # Edición activable
        return None, None   # Edición prohibida

    def infoCapa(self, capa):
        val = self.llista.get(capa.id())
        return self.testInfoCapa(val)

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

    def setMenu(self):
        if self.started():
            self.menu = qtWdg.QAction()
            self.menu.setText("Finalitza les edicions")
            self.menu.triggered.connect(self.stop)
            return self.menu
        return None

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

