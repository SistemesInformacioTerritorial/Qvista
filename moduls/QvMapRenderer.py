# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsUnitTypes)

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QLocale
from qgis.PyQt.QtGui import QColor

from moduls.QvMapVars import *
from moduls.QvMapForms import QvFormSimbMapificacio
from moduls.QvApp import QvApp

_LABEL_FORMAT = '%1 - %2'

class QvMapRendererParams(QObject):
    def __init__(self):
        super().__init__()
        self.campCalculat = 'RESULTAT'
        self.numDecimals = 0
        self.colorBase = 'Blau'
        self.colorContorn = None
        self.numCategories = 4
        self.modeCategories = 'Endreçat'
        self.rangsCategories = []
        self.simbol = None
        self.msgError = ''

    def nomParam(self, param, llista):
        for nom, valor in llista.items():
            if param == valor:
                return nom
        return list(llista.keys())[0]

    def nomColor(self, param, llista):
        for nom, valor in llista.items():
            if valor is not None:
                if not isinstance(valor, QColor):
                    valor = QColor(valor)
                if param.name() == valor.name():
                    # Si es negro, mirar tambien el alpha para distinguirlo de Qt.transparent
                    if param.name() == '#000000':
                        if param.alpha() == valor.alpha():
                            return nom
                    else:
                        return nom
        return list(llista.keys())[0]

    def calcDecimals(self, num):
        num = num.strip()
        pos = num.rfind(QvApp().locale.decimalPoint())
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
        num, ok = QvApp().locale.toFloat(txt)
        if ok:
            return num
        else:
            raise ValueError("Valor d'intenval erroni: " + txt)


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

    def calcRender(self, capa, params):
        if params.colorContorn is None:
            params.colorContorn = params.colorBase
        colorIni, colorFi = self.calcColorsGradient(params.colorBase)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(_LABEL_FORMAT, params.numDecimals)
        if params.simbol is None:
            params.simbol = QgsSymbol.defaultSymbol(capa.geometryType())
        self.setStrokeSymbology(params.simbol, params.colorContorn)
        renderer = QgsGraduatedSymbolRenderer.createRenderer(capa, params.campCalculat,
            params.numCategories, params.modeCategories, params.simbol, colorRamp, labelFormat)
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def customRender(self, capa, params):
        if params.colorContorn is None:
            params.colorContorn = params.colorBase
        total = params.numCategories
        alpha = MAP_ALPHA_INI
        maxAlpha = (255 - MAP_ALPHA_FIN)
        step = round((maxAlpha - alpha) / (total - 1))
        color = QColor(params.colorBase)
        decimals = params.maxDecimals(params.rangsCategories)
        categories = []
        for i, r in enumerate(params.rangsCategories):
            color.setAlpha(alpha)
            alpha = min(alpha + step, maxAlpha)
            if params.simbol is None:
                symbol = QgsSymbol.defaultSymbol(capa.geometryType())
            else:
                symbol = params.simbol.clone()
            self.setStrokeSymbology(symbol, params.colorContorn)
            symbol.setColor(color)
            f0 = params.numRang(r[0])
            f1 = params.numRang(r[1])
            label = QvApp().locale.toString(f0, 'f', decimals) + ' - ' + QvApp().locale.toString(f1, 'f', decimals)
            category = QgsRendererRange(f0, f1, symbol, label)
            categories.append(category)
        renderer = QgsGraduatedSymbolRenderer(params.campCalculat, categories)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        # renderer.setClassAttribute(str(decimals))
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def paramsRender(self, capa):
        parms = QvMapRendererParams()
        try:
            renderer = capa.renderer()
            parms.campCalculat = renderer.classAttribute()
            parms.rangsCategories = renderer.ranges()
            parms.numCategories = len(parms.rangsCategories)
            parms.modeCategories = parms.nomParam(renderer.mode(), MAP_METODES_MODIF)
            if parms.modeCategories == 'Personalitzat':
                cat = parms.rangsCategories[0]
                parms.numDecimals = parms.calcDecimals(cat.label())
                parms.simbol = cat.symbol().clone()
                color = cat.symbol().color()
            else:
                parms.numDecimals = renderer.labelFormat().precision()
                parms.simbol = renderer.sourceSymbol()
                color = renderer.sourceColorRamp().color1()
            parms.colorBase = parms.nomColor(color, MAP_COLORS)
            parms.colorContorn = parms.nomColor(parms.simbol.symbolLayer(0).strokeColor(), MAP_CONTORNS)
        except Exception as e:
            parms.msgError = str(e)
        return parms

    def modifyRenderer(self):
        fMap = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        fMap.exec()

