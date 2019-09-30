# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat)

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor

from moduls.QvMapificacio import QvFormSimbMapificacio

# TODO: arrays globales

class QvMapRenderer(QObject):

    def __init__(self, llegenda, iniAlpha=8):
        super().__init__()
        self.llegenda = llegenda
        self.iniAlpha = iniAlpha
    
    def calcColorsGradient(self, colorBase):
        colorIni = QColor(colorBase)
        colorIni.setAlpha(self.iniAlpha)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255 - self.iniAlpha)
        return colorIni, colorFi

    def calcRender(self, capa, campCalculat, numDecimals, colorBase,
                   numCategories, modeCategories, format):
        try:
            colorIni, colorFi = self.calcColorsGradient(colorBase)
            colorRamp = QgsGradientColorRamp(colorIni, colorFi)
            labelFormat = QgsRendererRangeLabelFormat(format, numDecimals)
            symbol = QgsSymbol.defaultSymbol(capa.geometryType())
            renderer = QgsGraduatedSymbolRenderer.createRenderer(capa, campCalculat,
                numCategories, modeCategories, symbol, colorRamp, labelFormat)
            return renderer
        except Exception as e:
            return None

    def numRang(self, txt, numDecimals):
        if numDecimals == 0:
            v = int(txt)
        else:
            v = round(float(num), numDecimals)
        return v

    def customRender(self, capa, campCalculat, numDecimals, colorBase, rangs, format):
        try:
            total = len(rangs)
            alpha = self.iniAlpha
            step = (256 - (2 * alpha)) // total
            color = QColor(colorBase)
            primero = True
            categories = []
            for r in rangs:
                if primero:
                    primero = False
                else:
                    alpha += step
                color.setAlpha(alpha)
                sym = QgsSymbol.defaultSymbol(capa.geometryType())
                sym.setColor(color)
                label = r[0] + ' - ' + r[1]
                category = QgsRendererRange(self.numRang(r[0], numDecimals),
                    self.numRang(r[1], numDecimals), sym, label)
                categories.append(category)
            renderer = QgsGraduatedSymbolRenderer(campCalculat, categories)
            renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
            return renderer
        except Exception as e:
            return None

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
            cats = renderer.ranges()
            numCategories = len(cats)
            modeCategories = self.nomParam(renderer.mode(), _METODES_MODIF)

            if modeCategories == 'Personalitzat':
                pass
# TODO:
            else:
                numDecimals = renderer.labelFormat().precision()
                color = renderer.sourceColorRamp().color1()
                color.setAlpha(0)
                colorBase = self.nomColor(color, _COLORS)
                format = renderer.labelFormat().format()

            return campCalculat, numDecimals, colorBase, numCategories, modeCategories, format
        except Exception as e:
            return 'RESULTAT', 0, 'Blau', 4, 'Endreçat', '%1 - %2'

    def modifyRenderer(self):
        global f
        f = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        f.show()

