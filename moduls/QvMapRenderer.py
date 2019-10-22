# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat,)

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

    # def numRang(self, txt, decimals):
    #     num = MAP_LOCALE.toFloat(txt)
    #     val = round(num, decimals)
    #     if decimals == 0:
    #         val = int(val)
    #     return val

    def numDecimals(self, num):
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
                n = self.numDecimals(r[i])
                res = max(res, n)
        return res

    def customRender(self, capa, campCalculat, colorBase, rangs):
        total = len(rangs)
        step = 256 // (total - 1)
        alpha = 0
        color = QColor(colorBase)
        decimals = self.maxDecimals(rangs)
        categories = []
        for r in rangs:
            color.setAlpha(alpha)
            alpha += step
            sym = QgsSymbol.defaultSymbol(capa.geometryType())
            sym.setColor(color)
            f0, _ = MAP_LOCALE.toFloat(r[0])
            f1, _ = MAP_LOCALE.toFloat(r[1])
            lab0 = MAP_LOCALE.toString(f0, 'f', decimals)
            lab1 = MAP_LOCALE.toString(f1, 'f', decimals)
            label = lab0 + ' - ' + lab1
            category = QgsRendererRange(f0, f1, sym, label)
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
            # if param.red() == valor.red() and param.green() == valor.green() and param.blue() == valor.blue():
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
# TODO
                # txt = renderer.classAttribute()
                # numDecimals = int(txt)
                numDecimals = 0
                cat = rangsCategories[0]
                color = cat.symbol().color()
            else:
                numDecimals = renderer.labelFormat().precision()
                color = renderer.sourceColorRamp().color1()

            colorBase = self.nomColor(color, MAP_COLORS)
            return campCalculat, numDecimals, colorBase, numCategories, modeCategories, rangsCategories

        except Exception as e:
            return 'RESULTAT', 0, 'Blau', 4, 'Endreçat', []

    def modifyRenderer(self):
        global f
        f = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        f.show()

