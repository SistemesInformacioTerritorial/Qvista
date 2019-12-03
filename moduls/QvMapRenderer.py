# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsUnitTypes)

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QLocale
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
        colorIni.setAlpha(MAP_ALPHA_INI)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255 - MAP_ALPHA_FIN)
        return colorIni, colorFi

    def setStrokeSymbology(self, sourceSymbol, color, width=1):
        symbolLayer = sourceSymbol.symbolLayer(0)
        symbolLayer.setStrokeColor(QColor(color))
        symbolLayer.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
        symbolLayer.setStrokeWidth(width)

    def calcRender(self, capa, campCalculat, numDecimals, colorBase, colorContorn,
                   numCategories, modeCategories, sourceSymbol=None):
        if colorContorn is None:
            colorContorn = colorBase
        colorIni, colorFi = self.calcColorsGradient(colorBase)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(_LABEL_FORMAT, numDecimals)
        if sourceSymbol is None:
            sourceSymbol = QgsSymbol.defaultSymbol(capa.geometryType())
        self.setStrokeSymbology(sourceSymbol, colorContorn)
        renderer = QgsGraduatedSymbolRenderer.createRenderer(capa, campCalculat,
            numCategories, modeCategories, sourceSymbol, colorRamp, labelFormat)
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def calcDecimals(self, num):
        num = num.strip()
        pos = num.rfind(MAP_LOCALE.decimalPoint())
        if pos == -1:
            return 0
        else:
            return len(num) - pos - 1

    def maxDecimals(self, rangs):
        res = 0
        for r in rangs:
            for i in (0, 1):
                n = self.calcDecimals(r[i])
                res = max(res, n)
        return res

    def numRang(self, txt):
        num, ok = MAP_LOCALE.toFloat(txt)
        if ok:
            return num
        else:
            raise ValueError("Valor d'intenval erroni: " + txt)

    def customRender(self, capa, campCalculat, colorBase, colorContorn, rangs, sourceSymbol=None):
        if colorContorn is None:
            colorContorn = colorBase
        total = len(rangs)
        alpha = MAP_ALPHA_INI
        maxAlpha = (255 - MAP_ALPHA_FIN)
        step = round((maxAlpha - alpha) / (total - 1))
        color = QColor(colorBase)
        decimals = self.maxDecimals(rangs)
        categories = []
        for i, r in enumerate(rangs):
            color.setAlpha(alpha)
            alpha = min(alpha + step, maxAlpha)
            if sourceSymbol is None:
                symbol = QgsSymbol.defaultSymbol(capa.geometryType())
            else:
                symbol = sourceSymbol.clone()
            self.setStrokeSymbology(symbol, colorContorn)
            symbol.setColor(color)
            f0 = self.numRang(r[0])
            f1 = self.numRang(r[1])
            label = MAP_LOCALE.toString(f0, 'f', decimals) + ' - ' + MAP_LOCALE.toString(f1, 'f', decimals)
            category = QgsRendererRange(f0, f1, symbol, label)
            categories.append(category)
        renderer = QgsGraduatedSymbolRenderer(campCalculat, categories)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        # renderer.setClassAttribute(str(decimals))
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
            if param.name() == valor.name():
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
                cat = rangsCategories[0]
                numDecimals = self.calcDecimals(cat.label())
                color = cat.symbol().color()
            else:
                numDecimals = renderer.labelFormat().precision()
                color = renderer.sourceColorRamp().color1()
            colorBase = self.nomColor(color, MAP_COLORS)
            sourceSymbol = renderer.sourceSymbol()
            colorContorn = sourceSymbol.symbolLayer(0).strokeColor()
            return True, (campCalculat, numDecimals, colorBase, colorContorn, numCategories, modeCategories, rangsCategories, sourceSymbol)

        except Exception as e:
            return False, ('RESULTAT', 0, 'Blau', 4, 'Endreçat', [], None)

    def modifyRenderer(self):
        fMap = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        fMap.exec()

