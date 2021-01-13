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
        self.menu = qtWdg.QMenu('Edicions')

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
            df.finishDlg()

    def setMenu(self):
        self.menu.clear()
        if self.modified():
            self.menu.addAction('Desa totes les modificacions', self.end)
            self.menu.addAction('Cancel·la totes les edicions', self.cancel)
            return self.menu
        return None

    def modified(self):
        for val in self.llista.values():
            _, df = self.testInfoCapa(val)
            if df is not None and df.modified():
                return True
        return False

    def finish(self, save):
        for val in self.llista.values():
            _, df = self.testInfoCapa(val)
            if df is not None:
                df.finish(save)
    
    def end(self):
        self.finish(True)

    def cancel(self):
        self.finish(False)

