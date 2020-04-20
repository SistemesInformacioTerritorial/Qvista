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


class QvMapRendererParams(QObject):
    def __init__(self):
        super().__init__()
        self.campCalculat = 'RESULTAT'
        self.campNom = 'DESCRIPCIO'
        self.numDecimals = 0
        self.colorBase = 'Blau'
        self.colorContorn = 'Blanc'
        self.numCategories = 4
        self.modeCategories = 'Endreçat'
        self.labelFormat = '%1 - %2'
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


class QvMapRenderer(QObject):

    def __init__(self, llegenda):
        super().__init__()
        self.llegenda = llegenda

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

    def calcRender(self, capa, params):
        if params.colorContorn is None:
            params.colorContorn = params.colorBase
        colorIni, colorFi = self.calcColorsGradient(params.colorBase)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(params.labelFormat, params.numDecimals)
        if params.simbol is None:
            params.simbol = QgsSymbol.defaultSymbol(capa.geometryType())
        self.setStrokeSymbology(params.simbol, params.colorContorn)
        renderer = QgsGraduatedSymbolRenderer.createRenderer(
            capa, params.campCalculat,
            params.numCategories, params.modeCategories, params.simbol, colorRamp, labelFormat)
        capa.setRenderer(renderer)
        capa.triggerRepaint()
        return renderer

    def customRender(self, capa, params):
        if params.colorContorn is None:
            params.colorContorn = params.colorBase
        total = params.numCategories
        alpha = mv.MAP_ALPHA_INI
        maxAlpha = (255 - mv.MAP_ALPHA_FIN)
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
            label = QvApp().locale.toString(f0, 'f', decimals) + ' - ' + \
                QvApp().locale.toString(f1, 'f', decimals)
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
            parms.modeCategories = parms.nomParam(renderer.mode(), mv.MAP_METODES_MODIF)
            if parms.modeCategories == 'Personalitzat':
                cat = parms.rangsCategories[0]
                parms.numDecimals = parms.calcDecimals(cat.label())
                parms.simbol = cat.symbol().clone()
                color = cat.symbol().color()
            else:
                parms.numDecimals = renderer.labelFormat().precision()
                parms.simbol = renderer.sourceSymbol()
                color = renderer.sourceColorRamp().color1()
            parms.colorBase = parms.nomColor(color, mv.MAP_COLORS)
            parms.colorContorn = parms.nomColor(parms.simbol.symbolLayer(0).strokeColor(),
                                                mv.MAP_CONTORNS)
        except Exception as e:
            parms.msgError = str(e)
        return parms

    def modifyRenderer(self):
        from moduls.QvMapForms import QvFormSimbMapificacio

        fMap = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        fMap.exec()


class QvSymRenderer(QObject):

    def __init__(self, llegenda):
        super().__init__()
        self.llegenda = llegenda

        def calcExpr(self, field, inc=0):
            expr = f'''coalesce(scale_exp("{field}", minimum("{field}"), maximum("{field}"),
                1 + {inc}, 10 + {inc}, 0.57), 0)'''
            return inspect.cleandoc(expr)

        def calcTip(self, field, name, decs=0):
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

    def setStrokeSymbology(self, sourceSymbol, params, inc=0):
        symbolLayer = sourceSymbol.symbolLayer(0)
        symbolLayer.setFillColor(params.colorBase)
        symbolLayer.setStrokeColor(params.colorContorn)
        symbolLayer.setStrokeStyle(Qt.SolidLine)
        symbolLayer.setStrokeWidth(1)
        symbolLayer.setStrokeWidthUnit(QgsUnitTypes.RenderPixels)
        expr = self.calcExpr(self.campCalculat, inc)
        prop = QgsProperty.fromExpression(expr)
        symbolLayer.setDataDefinedProperty(QgsSymbolLayer.PropertySize, prop)

    def calcRender(self, capa, params):

        inc = 0
        opacity = 0.55

        renderer = None
        geom = capa.geometryType()

        if (geom == QgsWkbTypes.GeometryType.PolygonGeometry):

            # Creamos simbología del punto centroide
            symbology = QgsCentroidFillSymbolLayer()
            symbology.setPointOnAllParts(False)
            symbology.setPointOnSurface(False)

            # Ajustamos valores del símbolo proporcional
            self.setStrokeSymbology(symbology.subSymbol(), params, inc)

            # Crear símbolo y asignarle la simbología
            sym = QgsFillSymbol.createSimple({
                'color': '{}'.format(params.colorBase.name()),
                'outline_color': '{}'.format(params.colorContorn.name())
            })
            sym.changeSymbolLayer(0, symbology)

            # Crear renderer y asignar a la capa
            renderer = QgsSingleSymbolRenderer(sym)
            capa.setRenderer(renderer)
            capa.setOpacity(opacity)

            expr = calcTip(self.campCalculat, self.campNom, self.numDecimals)
            capa.setMapTipTemplate(expr)
            capa.triggerRepaint()

        return renderer

    def customRender(self, capa, params):
        return None

    def paramsRender(self, capa):
        parms = QvMapRendererParams()
        try:
            renderer = capa.renderer()
            parms.campCalculat = renderer.classAttribute()
            parms.rangsCategories = renderer.ranges()
            parms.numCategories = len(parms.rangsCategories)
            parms.modeCategories = parms.nomParam(renderer.mode(), mv.MAP_METODES_MODIF)
            if parms.modeCategories == 'Personalitzat':
                cat = parms.rangsCategories[0]
                parms.numDecimals = parms.calcDecimals(cat.label())
                parms.simbol = cat.symbol().clone()
                color = cat.symbol().color()
            else:
                parms.numDecimals = renderer.labelFormat().precision()
                parms.simbol = renderer.sourceSymbol()
                color = renderer.sourceColorRamp().color1()
            parms.colorBase = parms.nomColor(color, mv.MAP_COLORS)
            parms.colorContorn = parms.nomColor(parms.simbol.symbolLayer(0).strokeColor(),
                                                mv.MAP_CONTORNS)
        except Exception as e:
            parms.msgError = str(e)
        return parms

    def modifyRenderer(self):
        fMap = QvFormSimbMapificacio(self.llegenda, self.llegenda.currentLayer())
        fMap.exec()


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
