# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat)

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor

from moduls.QvMapVars import *
from moduls.QvMapForms import QvFormSimbMapificacio

_LABEL_FORMAT = '%1 - %2'

class QvMapRenderer(QObject):

    def __init__(self, llegenda):
        super().__init__()
        self.llegenda = llegenda
    
    def calcColorsGradient(self, colorBase):
        colorIni = QColor(colorBase)
        colorIni.setAlpha(0)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255)
        return colorIni, colorFi

    def calcRender(self, capa, campCalculat, numDecimals, colorBase,
                   numCategories, modeCategories):
        colorIni, colorFi = self.calcColorsGradient(colorBase)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(_LABEL_FORMAT, numDecimals)
        symbol = QgsSymbol.defaultSymbol(capa.geometryType())
        renderer = QgsGraduatedSymbolRenderer.createRenderer(capa, campCalculat,
            numCategories, modeCategories, symbol, colorRamp, labelFormat)
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def numRang(self, txt, numDecimals):
        v = round(float(txt), numDecimals)
        if numDecimals == 0:
            v = int(v)
        return v

    def customRender(self, capa, campCalculat, numDecimals, colorBase, rangs):
        total = len(rangs)
        step = 256 // (total - 1)
        alpha = 0
        color = QColor(colorBase)
        categories = []
        for r in rangs:
            color.setAlpha(alpha)
            alpha += step
            sym = QgsSymbol.defaultSymbol(capa.geometryType())
            sym.setColor(color)
            label = r[0] + ' - ' + r[1]
            category = QgsRendererRange(self.numRang(r[0], numDecimals),
                self.numRang(r[1], numDecimals), sym, label)
            categories.append(category)
        renderer = QgsGraduatedSymbolRenderer(campCalculat, categories)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def nomParam(self, param, llista):
        for nom, valor in llista.items():
            if param == valor:
                return nom
        return list(llista.keys())[0]

    def nomColor(self, param, llista):
        for nom, valor in llista.items():
            if param.red() == valor.red() and param.green() == valor.green() and param.blue() == valor.blue():
                return nom
        return list(llista.keys())[0]

    def paramsRender(self, capa):
        try:
            renderer = capa.renderer()
            campCalculat = renderer.classAttribute()
            rangsCategories = renderer.ranges()
            numCategories = len(rangsCategories)
            modeCategories = self.nomParam(renderer.mode(), MAP_METODES_MODIF)

            if modeCategories == 'Personalitzat':
# TODO:
                numDecimals = 0
                cat = rangsCategories[0]
                color = cat.symbol().color()
            else:
                numDecimals = renderer.labelFormat().precision()
                color = renderer.sourceColorRamp().color1()
                # color.setAlpha(0)

            colorBase = self.nomColor(color, MAP_COLORS)
            return campCalculat, numDecimals, colorBase, numCategories, modeCategories, rangsCategories
        except Exception as e:
            return 'RESULTAT', 0, 'Blau', 4, 'Endreçat', []

    def modifyRenderer(self):
        global f
        f = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        f.show()

