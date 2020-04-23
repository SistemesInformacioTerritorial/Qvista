# -*- coding: utf-8 -*-

from qgis.core import (QgsSymbol, QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsUnitTypes,
                       QgsCentroidFillSymbolLayer, QgsSingleSymbolRenderer, QgsWkbTypes,
                       QgsSymbolLayer, QgsProperty, QgsFillSymbol)

from qgis.PyQt.QtCore import QObject, Qt
from qgis.PyQt.QtGui import QColor

import moduls.QvMapVars as mv
from moduls.QvApp import QvApp

import inspect

_EXPR_TIP = inspect.cleandoc('''<div style="font-size: 18px; white-space: nowrap;">
            [% CASE WHEN attribute('{}') IS NULL THEN NULL
            ELSE concat(attribute('{}'), ':', '<br/>')
            END %]
            [% format_number("{}", {}) %]
            </div>''')

_EXPR_SYM = inspect.cleandoc('''coalesce(scale_exp("{}", minimum("{}"), maximum("{}"),
            1 + {}, {} + {}, 0.57), 0)''')


class QvMapRendererParams(QObject):
    def __init__(self, tipus='Àrees'):
        super().__init__()
        self.tipusMapa = tipus
        self.capa = None
        self.iniParams()

    @classmethod
    def fromLayer(cls, capa):
        renderer = capa.renderer()
        if isinstance(renderer, QgsGraduatedSymbolRenderer):
            obj = cls('Àrees')
            obj.capa = capa
            obj.mapParamsRender(renderer)
            return obj
        elif isinstance(renderer, QgsSingleSymbolRenderer):
            obj = cls('Cercles')
            obj.capa = capa
            obj.symParamsRender(renderer)
            return obj
        else:
            obj = cls()
            obj.msgError = "Simbologia de mapa desconeguda"
            return obj

    def iniParams(self):
        self.campCalculat = 'RESULTAT'
        self.campNom = 'DESCRIPCIO'
        self.modeCategories = 'Endreçat'
        self.rangsCategories = []
        self.numDecimals = 0
        self.simbol = None
        self.msgError = ''
        if self.tipusMapa == 'Àrees':
            self.colorBase = 'Blau'
            self.colorContorn = 'Base'
            self.numCategories = 4
            self.labelFormat = '%1 - %2'
            self.increase = 0
            self.opacity = 1
        else:  # 'Cercles'
            self.colorBase = 'Porpra'
            self.colorContorn = 'Blanc'
            # self.modeCategories = 'Flannery'
            self.numCategories = 10
            self.labelFormat = ''
            self.increase = 5
            self.opacity = 0.55

    def mapRenderer(self, llegenda):
        if self.tipusMapa == 'Àrees':
            return QvMapRenderer(llegenda, self)
        elif self.tipusMapa == 'Cercles':
            return QvSymRenderer(llegenda, self)
        else:
            raise ValueError("Tipus de mapa simbòlic erroni: " + self.tipusMapa)

    def nomParam(self, param, llista):
        for nom, valor in llista.items():
            if param == valor:
                return nom
        return list(llista.keys())[0]

    def calcTip(self):
        expr = _EXPR_TIP.format(self.campNom, self.campNom, self.campCalculat, self.numDecimals)
        return inspect.cleandoc(expr)

    def nomColor(self, param, llista):
        for nom, valor in llista.items():
            if valor is not None:
                # if not isinstance(valor, QColor):
                #     valor = QColor(valor)
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

    def mapParamsRender(self, renderer):
        try:
            self.campCalculat = renderer.classAttribute()
            self.rangsCategories = renderer.ranges()
            self.numCategories = len(self.rangsCategories)
            self.modeCategories = self.nomParam(renderer.mode(), mv.MAP_METODES_MODIF)
            if self.modeCategories == 'Personalitzat':
                cat = self.rangsCategories[0]
                self.numDecimals = self.calcDecimals(cat.label())
                self.simbol = cat.symbol().clone()
                color = cat.symbol().color()
            else:
                self.numDecimals = renderer.labelFormat().precision()
                self.simbol = renderer.sourceSymbol()
                color = renderer.sourceColorRamp().color1()
            self.colorBase = self.nomColor(color, mv.MAP_COLORS)
            self.colorContorn = self.nomColor(self.simbol.symbolLayer(0).strokeColor(),
                                              mv.MAP_CONTORNS)
        except Exception as e:
            self.msgError = str(e)

    def scanParams(self, template, expr, sep='{}'):
        try:
            salida = []
            texto = expr
            segmentos = template.split(sep)
            for segmento in segmentos:
                ini = texto.find(segmento)
                if ini > 0:
                    salida.append(texto[:ini])
                texto = texto[ini+len(segmento):]
            return salida
        except Exception as e:
            self.msgError = str(e)
            return None

    def symParamsRender(self, renderer):
        try:
            symbology = renderer.symbol().symbolLayer(0)
            symbolLayer = symbology.subSymbol().symbolLayer(0)
            self.colorBase = self.nomColor(symbolLayer.fillColor(), mv.MAP_COLORS)
            self.colorContorn = self.nomColor(symbolLayer.strokeColor(), mv.MAP_CONTORNS)

            props = symbolLayer.dataDefinedProperties()
            prop = props.property(QgsSymbolLayer.PropertySize)
            params = self.scanParams(_EXPR_SYM, prop.expressionString())
            self.campCalculat = params[0]
            self.increase = int(params[3])
            self.numCategories = int(params[4])

            params = self.scanParams(_EXPR_TIP, self.capa.mapTipTemplate())
            self.campNom = params[0]
            self.numDecimals = int(params[3])

        except Exception as e:
            self.msgError = str(e)


class QvMapRenderer(QObject):

    def __init__(self, llegenda, params):
        super().__init__()
        self.llegenda = llegenda
        self.params = params

    def calcColorsGradient(self, colorBase):
        colorIni = QColor(colorBase)
        colorIni.setAlpha(mv.MAP_ALPHA_INI)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255 - mv.MAP_ALPHA_FIN)
        return colorIni, colorFi

    def setStrokeSymbology(self, sourceSymbol, color, width=1):
        symbolLayer = sourceSymbol.symbolLayer(0)
        symbolLayer.setStrokeColor(color)
        symbolLayer.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
        symbolLayer.setStrokeWidth(width)

    def calcRender(self, capa):
        if self.params.colorContorn is None:
            self.params.colorContorn = self.params.colorBase
        colorIni, colorFi = self.calcColorsGradient(self.params.colorBase)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(self.params.labelFormat, self.params.numDecimals)
        if self.params.simbol is None:
            self.params.simbol = QgsSymbol.defaultSymbol(capa.geometryType())
        self.setStrokeSymbology(self.params.simbol, self.params.colorContorn)
        renderer = QgsGraduatedSymbolRenderer.createRenderer(
            capa, self.params.campCalculat,
            self.params.numCategories, self.params.modeCategories,
            self.params.simbol, colorRamp, labelFormat)
        capa.setRenderer(renderer)
        capa.setMapTipTemplate(self.params.calcTip())
        capa.triggerRepaint()
        return renderer

    def customRender(self, capa):
        if self.params.colorContorn is None:
            self.params.colorContorn = self.params.colorBase
        total = self.params.numCategories
        alpha = mv.MAP_ALPHA_INI
        maxAlpha = (255 - mv.MAP_ALPHA_FIN)
        step = round((maxAlpha - alpha) / (total - 1))
        color = QColor(self.params.colorBase)
        decimals = self.params.maxDecimals(self.params.rangsCategories)
        categories = []
        for i, r in enumerate(self.params.rangsCategories):
            color.setAlpha(alpha)
            alpha = min(alpha + step, maxAlpha)
            if self.params.simbol is None:
                symbol = QgsSymbol.defaultSymbol(capa.geometryType())
            else:
                symbol = self.params.simbol.clone()
            self.setStrokeSymbology(symbol, self.params.colorContorn)
            symbol.setColor(color)
            f0 = self.params.numRang(r[0])
            f1 = self.params.numRang(r[1])
            label = QvApp().locale.toString(f0, 'f', decimals) + ' - ' + \
                QvApp().locale.toString(f1, 'f', decimals)
            category = QgsRendererRange(f0, f1, symbol, label)
            categories.append(category)
        renderer = QgsGraduatedSymbolRenderer(self.params.campCalculat, categories)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        # renderer.setClassAttribute(str(decimals))
        capa.setRenderer(renderer)
        capa.setMapTipTemplate(self.params.calcTip())
        capa.triggerRepaint()
        return renderer


class QvSymRenderer(QObject):

    def __init__(self, llegenda, params):
        super().__init__()
        self.llegenda = llegenda
        self.params = params

    def calcExpr(self):
        expr = _EXPR_SYM.format(self.params.campCalculat, self.params.campCalculat,
                                self.params.campCalculat, self.params.increase,
                                self.params.numCategories, self.params.increase)
        return inspect.cleandoc(expr)

    def setStrokeSymbology(self, sourceSymbol):
        symbolLayer = sourceSymbol.symbolLayer(0)
        symbolLayer.setFillColor(self.params.colorBase)
        symbolLayer.setStrokeColor(self.params.colorContorn)
        symbolLayer.setStrokeStyle(Qt.SolidLine)
        symbolLayer.setStrokeWidth(1)
        symbolLayer.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
        expr = self.calcExpr()
        prop = QgsProperty.fromExpression(expr)
        symbolLayer.setDataDefinedProperty(QgsSymbolLayer.PropertySize, prop)

    def calcRender(self, capa):

        renderer = None
        geom = capa.geometryType()

        if (geom == QgsWkbTypes.GeometryType.PolygonGeometry):

            # Creamos simbología del punto centroide
            symbology = QgsCentroidFillSymbolLayer()
            symbology.setPointOnAllParts(False)
            symbology.setPointOnSurface(False)

            # Ajustamos valores del símbolo proporcional
            self.setStrokeSymbology(symbology.subSymbol())

            # Crear símbolo y asignarle la simbología
            sym = QgsFillSymbol.createSimple({
                'color': '{}'.format(self.params.colorBase.name()),
                'outline_color': '{}'.format(self.params.colorContorn.name())
            })
            sym.changeSymbolLayer(0, symbology)

            # Crear renderer y asignar a la capa
            renderer = QgsSingleSymbolRenderer(sym)
            capa.setRenderer(renderer)
            capa.setOpacity(self.params.opacity)
            capa.setMapTipTemplate(self.params.calcTip())
            capa.triggerRepaint()

        return renderer

    def customRender(self, capa):
        return None


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    import qgis.PyQt.QtWidgets as qtWdg
    import qgis.gui as qgGui

    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvAtributs import QvAtributs

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canv = qgGui.QgsMapCanvas()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib)

        leyenda.project.read('D:/qVista/EjemploSimbolos.qgs')

        canv.setWindowTitle('Canvas')
        canv.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        # Acciones personalizadas para menú contextual de la leyenda:
        #
        # - Definición de la acción y del metodo asociado
        # - Se añade la acción a la lista de acciones disponibles (llegenda.accions)
        # - Se redefine la lista de acciones que apareceran en el menú (llegenda.menuAccions)
        #   mediante la señal clicatMenuContexte según el tipo de nodo clicado
        #   (Tipos: none, group, layer, symb)

        # Acciones de usuario

        def readMap():
            capa = leyenda.currentLayer()  # Capa de polígonos a mapificar
            geom = capa.geometryType()

            if (geom == QgsWkbTypes.GeometryType.PolygonGeometry):
                pass

        def calcExpr(field, inc=0):
            expr = f'''coalesce(scale_exp("{field}", minimum("{field}"), maximum("{field}"),
                1 + {inc}, 10 + {inc}, 0.57), 0)'''
            return inspect.cleandoc(expr)

        def calcTip(field, name, decs=0):
            # <div style="font-size: 18px; white-space: nowrap;">
            # [% CASE WHEN attribute('DESCRIPCIO') IS NULL THEN NULL
            # ELSE concat(attribute('DESCRIPCIO'), ':', '<br/>')
            # END %]
            # [% format_number("RESULTAT", 0) %]</div>
            expr = f'''<div style="font-size: 18px; white-space: nowrap;">
                [% CASE WHEN attribute('{name}') IS NULL THEN NULL
                ELSE concat(attribute('{name}'), ':', '<br/>')
                END %]
                [% format_number("{field}", {decs}) %]
                </div>'''
            return inspect.cleandoc(expr)

        def testMap():
            # Parámetros mapa
            colorFill = mv.MAP_COLORS['Blau']
            colorOut = mv.MAP_CONTORNS['Blanc']
            inc = 8
            opacity = 0.55
            field = "RESULTAT"
            name = "DESCRIPCIO"
            decs = 0

            capa = leyenda.currentLayer()  # Capa de polígonos a mapificar
            geom = capa.geometryType()

            if (geom == QgsWkbTypes.GeometryType.PolygonGeometry):

                # Creamos simbología del punto centroide
                symbology = QgsCentroidFillSymbolLayer()
                symbology.setPointOnAllParts(False)
                symbology.setPointOnSurface(False)

                # Ajustamos valores del símbolo proporcional
                layerSymbol = symbology.subSymbol().symbolLayer(0)  # QgsSimpleMarkerSymbolLayer
                layerSymbol.setFillColor(colorFill)
                layerSymbol.setStrokeColor(colorOut)
                layerSymbol.setStrokeStyle(Qt.SolidLine)
                layerSymbol.setStrokeWidth(1.0)
                layerSymbol.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
                expr = calcExpr(field, inc)
                prop = QgsProperty.fromExpression(expr)
                layerSymbol.setDataDefinedProperty(QgsSymbolLayer.PropertySize, prop)

                # Crear símbolo y asignarle la simbología
                sym = QgsFillSymbol.createSimple({
                    'color': '{}'.format(colorFill.name()),
                    'outline_color': '{}'.format(colorOut.name())
                })
                sym.changeSymbolLayer(0, symbology)

                # Crear renderer y asignar a la capa
                renderer = QgsSingleSymbolRenderer(sym)
                capa.setRenderer(renderer)
                capa.setOpacity(opacity)
                expr = calcTip(field, name, decs)
                capa.setMapTipTemplate(expr)
                capa.triggerRepaint()

                return

        def saveMap():
            # Guardar los cambios en el proyecto
            leyenda.project.write()

        # def testOld():
        #     capa = leyenda.currentLayer()  # Capa de polígonos a mapificar
        #     geom = capa.geometryType()

        #     if (geom == QgsWkbTypes.GeometryType.PolygonGeometry):

        #         # Creamos simbología del punto centroide
        #         symbology = QgsCentroidFillSymbolLayer()
        #         symbology.setPointOnAllParts(False)
        #         symbology.setPointOnSurface(False)

        #         # Ajustamos valores del símbolo proporcional
        #         layerSymbol = symbology.subSymbol().symbolLayer(0)  # QgsSimpleMarkerSymbolLayer
        #         layerSymbol.setFillColor(mv.MAP_COLORS['Blau'])
        #         layerSymbol.setStrokeColor(mv.MAP_CONTORNS['Blanc'])
        #         layerSymbol.setStrokeStyle(Qt.SolidLine)
        #         layerSymbol.setStrokeWidth(1.0)
        #         layerSymbol.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
        #         expr = 'coalesce(scale_exp("RESULTAT", 3.14738e+06, 1.78281e+07, 8, 18, 0.57), 0)'
        #         layerSymbol.setDataDefinedProperty(
        #             QgsSymbolLayer.PropertyWidth,
        #             QgsProperty.fromExpression(expr, True)
        #         )

        #         # Borrar todas las symbolLayers...
        #         sourceSymbol = QgsSymbol.defaultSymbol(geom)  # QgsFillSymbol
        #         num = sourceSymbol.symbolLayerCount()
        #         for n in range(num, 0, -1):
        #             sourceSymbol.deleteSymbolLayer(n - 1)
        #         # ... y sustituirlas por la de punto centroide
        #         sourceSymbol.appendSymbolLayer(symbology)

        #         # Crear renderer y asignar a la capa
        #         renderer = QgsSingleSymbolRenderer(sourceSymbol)
        #         capa.setRenderer(renderer)
        #         capa.setOpacity(0.55)
        #         capa.triggerRepaint()

        #         # Guardar los cambios en el proyecto
        #         leyenda.project.write()
        #         return

        #         # markerSymbol = symbology.subSymbol()  # QgsMarkerSymbol

        #         # symbology.setDataDefinedProperty(
        #         #     QgsSymbolLayer.PropertyStrokeColor,
        #         #     QgsProperty.fromValue(mv.MAP_CONTORNS["Blanc"]))
        #         # symbology.setDataDefinedProperty(
        #         #     QgsSymbolLayer.PropertyFillColor,
        #         #     QgsProperty.fromValue(mv.MAP_COLORS["Blau"]))
        #         # symbology.symbolLayers()[0].setDataDefinedProperty(
        #         #     QgsSymbolLayer.PropertyStrokeColor,
        #         #     QgsProperty.fromValue(mv.MAP_CONTORNS["Blanc"]))
        #         # symbology.symbolLayers()[0].setDataDefinedProperty(
        #         #     QgsSymbolLayer.PropertyFillColor,
        #         #     QgsProperty.fromValue(mv.MAP_COLORS["Blau"]))

        #     else:
        #         return

        #     # Borrar todas las symbolLayers...
        #     sourceSymbol = QgsSymbol.defaultSymbol(geom)  # QgsFillSymbol
        #     num = sourceSymbol.symbolLayerCount()
        #     for n in range(num, 0, -1):
        #         sourceSymbol.deleteSymbolLayer(n)
        #     # ... y sustituirlas por la recién creada
        #     sourceSymbol.appendSymbolLayer(symbology)

        # # sym1 = QgsFillSymbol.createSimple({'color': '#fdbf6f', 'outline_color': 'black'})
        # # renderer = QgsSingleSymbolRenderer(sym1)
        # # renderer.symbols(QgsRenderContext())[0].symbolLayers()[0].setDataDefinedProperty(
        # #    QgsSymbolLayer.PropertyFillColor,
        # #    QgsProperty.fromExpression('color_rgb( (@geometry_part_num - 1) * 200, 0, 0 )'))
        # # self.layer.setRenderer(renderer)

        #     # sourceSymbol.symbolLayers()[0].setDataDefinedProperty(
        #     #     QgsSymbolLayer.PropertyFillColor,
        #     #     QgsProperty.fromValue('#0080ff'))

        #     # Aplicar nueva simbología a la capa
        #     renderer = QgsSingleSymbolRenderer(sourceSymbol)
        #     capa.setRenderer(renderer)
        #     capa.setOpacity(0.55)
        #     capa.triggerRepaint()

        #     # Guardar los cambios en el proyecto
        #     leyenda.project.write()

        # Acciones de usuario para el menú

        act = qtWdg.QAction()
        act.setText("Read Map")
        act.triggered.connect(readMap)
        leyenda.accions.afegirAccio('readMap', act)

        act = qtWdg.QAction()
        act.setText("Test Map")
        act.triggered.connect(testMap)
        leyenda.accions.afegirAccio('testMap', act)

        act = qtWdg.QAction()
        act.setText("Save Map")
        act.triggered.connect(saveMap)
        leyenda.accions.afegirAccio('saveMap', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'layer':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('readMap')
                leyenda.menuAccions.append('testMap')
                leyenda.menuAccions.append('saveMap')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)
