# -*- coding: utf-8 -*-

from typing import List

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtSql as qtSql

from moduls.QvApp import QvApp
from moduls.QvVistacadVars import *

import math

class QvObjVcad:
    def __init__(self, db: qtSql.QSqlDatabase) -> None:
        self.debug = (__name__ == "__main__")
        self.db = db

    def ejecuta(self, select: str) -> qtSql.QSqlQuery:
        if self.db is None: return None
        query = qtSql.QSqlQuery(self.db)
        try:
            if self.debug: print('Select:', select)
            query.setForwardOnly(True)
            query.exec_(select)
            return query
        except Exception as e:
            print(str(e))
            return None

    def siguiente(self) -> bool:
        if self.db is None: return False
        ok = self.query.next()
        if ok:
            self.registro()
        return ok

    def num(self) -> int:
        return self.query.at()

    def primero(self) -> bool:
        return self.num() == 0

    def registro(self) -> None:
        pass

class QvCapaVcad(QvObjVcad):
    
    def __init__(self, db: qtSql.QSqlDatabase, idProyecto: str, idsCapasExcluidas: str = '0', orden: str = ''):
        super().__init__(db)
        self.idProyecto = idProyecto
        self.idsCapasExcluidas = idsCapasExcluidas
        self.orden = orden
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)

    def __str__(self):
        try:
            if not hasattr(self, 'ID'): return ''
            if self.primero():
                if isinstance(self.DESC_PROJECTE, str) and self.DESC_PROJECTE != '':
                    linea = f"Proyecto: {self.NOM_PROJECTE} - {self.DESC_PROJECTE}"
                else:
                    linea = f"Proyecto: {self.NOM_PROJECTE}"
                print(linea)
            return f"- Capa {self.num()+1}: {self.ID}, {self.NOM}, {self.TIPUS}"
        except Exception as e:
            print(str(e))
            return ''

    def consulta(self) -> str:
        if self.idsCapasExcluidas == '':
            filtroCapas = ''
        else:
            filtroCapas = f"and c.id not in ({self.idsCapasExcluidas}) "
        return f"select p.nom nom_projecte, p.descripcio desc_projecte, c.*, s.nom nom_simbol, s.rotable rotable_simbol " \
               f"from vistacad_u.projectes p, vistacad_u.capes c, vistacad_u.construccions_grafiques s " \
               f"where p.id = {self.idProyecto} and p.actiu = 1 " \
               f"and p.id = c.id_projecte and c.actiu = 1 " \
               f"and c.id_const_grafica = s.id(+) " \
               f"{filtroCapas}" \
               f"order by ordre_visual {self.orden}"

    def registro(self) -> None:
        self.NOM_PROJECTE = self.query.value('NOM_PROJECTE')
        self.DESC_PROJECTE = self.query.value('DESC_PROJECTE')
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        self.MOSTRAR_ETIQUETA = math.trunc(self.query.value('MOSTRAR_ETIQUETA'))
        self.ESCALA_MIN = self.query.value('ESCALA_MIN')
        self.ESCALA_MAX = self.query.value('ESCALA_MAX')
        # Simbolo
        self.NOM_SIMBOL = self.query.value('NOM_SIMBOL')
        variant = self.query.value('ROTABLE_SIMBOL')
        if isinstance(variant, float):
            self.ROTABLE_SIMBOL = math.trunc(variant)
        else:
            self.ROTABLE_SIMBOL = 0
        # Línea
        self.LINIA_GRUIX = math.trunc(self.query.value('LINIA_GRUIX'))
        self.LINIA_COLOR = math.trunc(self.query.value('LINIA_COLOR'))
        self.LINIA_TIPUS = math.trunc(self.query.value('LINIA_TIPUS'))
        # Relleno
        self.NO2REL1TR0 = math.trunc(self.query.value('NO2REL1TR0')) # 0=Vacío 1=Uniforme 2=Trama
        self.OPA1TRANS0 = math.trunc(self.query.value('OPA1TRANS0')) # 0=Transparente 1=Opaco
        self.RELLENO_TIPUS = math.trunc(self.query.value('RELLENO_TIPUS'))
        self.RELLENO_COLOR = math.trunc(self.query.value('RELLENO_COLOR'))
        self.RELLENO_COLOR_TRAMA = math.trunc(self.query.value('RELLENO_COLOR_TRAMA'))

    def lineColorQgis(self) -> str:
        return VCAD_COLORS[self.LINIA_COLOR] + ',255'

    def lineStyleQgis(self) -> str:
        return VCAD_LINE_STYLES[self.LINIA_TIPUS]

    def lineWidthQgis(self) -> str:
        if self.LINIA_GRUIX == 0:
            width = 0.1
        else:
            width = 0.1 * self.LINIA_GRUIX
        return f"{width:.5f}"

    def fillColorQgis(self) -> str:
        if self.OPA1TRANS0 == 0:
            alpha = '170'
        else:
            alpha = '255'
        return VCAD_COLORS[self.RELLENO_COLOR] + ',' + alpha

    def fillStyleQgis(self) -> str:
        return VCAD_FILL_STYLES[self.RELLENO_TIPUS]

    def fillColorStyleQgis(self) -> str:
        return VCAD_COLORS[self.RELLENO_COLOR_TRAMA] + ',255'

    def symbolQgis(self) -> dict:
        if self.NOM_SIMBOL and self.NOM_SIMBOL in VCAD_SYMBOLS:
            return VCAD_SYMBOLS[self.NOM_SIMBOL]
        else:
            return None

# Let's define the following handy function:

# def setColumnVisibility( layer, columnName, visible ):
#     config = layer.attributeTableConfig()
#     columns = config.columns()
#     for column in columns:
#         if column.name == columnName:
#             column.hidden = not visible
#             break
#     config.setColumns( columns )
#     layer.setAttributeTableConfig( config )

# And then you can call it to hide or show columns in the attribute table. For example:

# vLayer = iface.activeLayer()
# setColumnVisibility( vLayer, 'FIRST_COLUMN', False ) # Hide FIRST_COLUMN
# setColumnVisibility( vLayer, 'area', False ) # Hide area column
# setColumnVisibility( vLayer, 'FIRST_COLUMN', True ) # Show FIRST_COLUMN
# setColumnVisibility( vLayer, 'area', True ) # Show area column

    def selectQgis(self, atributos: str) -> str:
        if self.TIPUS == 1: # Punto
            campos = "trunc(rotacio) \"Rotació\", "
        else:
            campos = ""
        return f"select id, {atributos}{campos}" \
               f"geom from vistacad_u.geometries where actiu = 1 and id_capa = {self.ID}"

    def simbologia(self, symbol: qgCor.QgsSymbol) -> None:
        if self.TIPUS == 1: # Punto
            props = self.symbolQgis()
            if props:
                props['color'] = self.lineColorQgis()
                symbolLayer = qgCor.QgsSimpleMarkerSymbolLayer.create(props)
                if self.ROTABLE_SIMBOL == 1:
                    prop = qgCor.QgsProperty()
                    prop.setExpressionString(f"-\"Rotació\"{props['angle']}") 
                    symbolLayer.setDataDefinedProperty(qgCor.QgsSymbolLayer.PropertyAngle, prop)
                symbol.changeSymbolLayer(0, symbolLayer)
                if self.debug: print('NEW STYLE', symbol.symbolLayer(0).properties())
        elif self.TIPUS == 2: # Linea
            props = symbol.symbolLayer(0).properties()
            if self.debug: print('OLD STYLE', symbol.symbolLayer(0).properties())
            props['line_color'] = self.lineColorQgis()
            props['line_style'] = self.lineStyleQgis()
            props['line_width'] = self.lineWidthQgis()
            props['line_width_unit'] = 'MM'
            symbolLayer = qgCor.QgsSimpleLineSymbolLayer.create(props)
            symbol.changeSymbolLayer(0, symbolLayer)
            if self.debug: print('NEW STYLE', symbol.symbolLayer(0).properties())
        elif self.TIPUS == 3: # Polígono
            props = symbol.symbolLayer(0).properties()
            if self.debug: print('OLD STYLE', symbol.symbolLayer(0).properties())
            props['outline_color'] = self.lineColorQgis()
            props['outline_style'] = self.lineStyleQgis()
            props['outline_width'] = self.lineWidthQgis()
            props['outline_width_unit'] = 'MM'
            # Relleno
            if self.NO2REL1TR0 == 2: # Nada
                props['style'] = 'no'
                props['color'] = '0,0,0,0'
            else:
                props['style'] = 'solid'
                props['color'] = self.fillColorQgis()
                if self.NO2REL1TR0 == 0: # Trama
                    pass   # POR ACABAR
                    # props['style'] = self.fillStyleQgis()
                    # props['color'] = self.fillColorStyleQgis()
            symbolLayer = qgCor.QgsSimpleFillSymbolLayer.create(props)
            symbol.changeSymbolLayer(0, symbolLayer)
            if self.debug: print('NEW STYLE', symbol.symbolLayer(0).properties())
class QvAtributosVcad(QvObjVcad):

    def __init__(self, db: qtSql.QSqlDatabase, idCapa: str):
        super().__init__(db)
        self.idCapa = idCapa
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)
        self.lista = ''

    def __str__(self):
        try:
            if not hasattr(self, 'ID'): return ''
            return f"  + Atributo {self.num()+1}: {self.NOM}, {self.TIPUS}"
        except Exception as e:
            print(str(e))
            return ''

    def consulta(self) -> str:
        return f"select a.* " \
               f"from vistacad_u.capes c, vistacad_u.formularis f, vistacad_u.atributs a " \
               f"where c.id = {self.idCapa} and c.actiu = 1 " \
               f"and c.id_formulari = f.id and f.actiu = 1 " \
               f"and a.id_formulari = f.id and a.actiu = 1 " \
               f"order by a.ordre"

    def registro(self) -> None:
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        self.lista += f"extractValue(attrs,'/OBJ/a{self.ID}') \"{self.NOM}\", "

    def listaQgis(self) -> str:
        return self.lista

class QvVistacad:
    """ Clase para importar projectos de Visatacad a Qvista
        Tablas consultadas: projectes, capes, formularis, atributs, geometries

        Falta incorporar:
        - Orden visualización capas
        - Simbología geometrías estatica y dinámica
        - Simbología etiquetas
        - Tipos de atributos y formulario
        - Bases cartográficas
        - Paneles
    """ 
    @classmethod
    def carregaProjecte(cls, idProjecte: str, idsCapesExcluides: str = '', agrupar: bool = True, srid: str = '25831') -> None:
        try:
            vCad = cls()
            vCad.loadProject(idProjecte, idsCapesExcluides, agrupar, srid)
        except Exception as e:
            print('Error QvVistacad.carregaProjecte: ' + str(e))

    def __init__(self):
        self.debug = (__name__ == "__main__")
        self.conexion = QvApp().dbQvista
        self.db = QvApp().dbLog
        if self.db is None:
            QvApp().dbLogConnexio()
            self.db = QvApp().dbLog
        self.project = qgCor.QgsProject.instance()
        self.root = self.project.layerTreeRoot()

    # def setVisibiltyColumn(self, layer, columnName, visible):
    #     config = layer.attributeTableConfig()
    #     columns = config.columns()
    #     for column in columns:
    #         if column.name == columnName:
    #             column.hidden = not visible
    #             config.setColumns(columns)
    #             layer.setAttributeTableConfig(config)
    #             break

    def loadLayer(self, nom: str, tipus: int, select: str, srid: str = '25831', id: str = 'ID', geom: str = 'GEOM') -> qgCor.QgsVectorLayer:
        uri = qgCor.QgsDataSourceUri()
        uri.setConnection(self.conexion['HostName'],
                          str(self.conexion['Port']),
                          self.conexion['DatabaseName'],
                          self.conexion['UserName'],
                          self.conexion['Password'])       
        uri.setDataSource("", '(' + select + ')', geom, "", id)
        uri.setWkbType(tipus)
        uri.setSrid(srid)
        layer = qgCor.QgsVectorLayer(uri.uri(), nom, "oracle")
        if layer.isValid():
            # if tipus == 1: # No funciona
            #     self.setVisibiltyColumn(layer, "Rotació", False)
            return layer
        else:
            return None

    def printProject(self, idProyecto: str, idsCapasExcluidas: str = '', agrupar: bool = True, srid: str = '25831') -> None:
        if self.db is None: return
        try:
            if agrupar: orden = 'desc'
            else: orden = ''
            capa = QvCapaVcad(self.db, idProyecto, idsCapasExcluidas, orden=orden)
            while capa.siguiente():
                print(capa)
                atributos = QvAtributosVcad(self.db, capa.ID)
                while atributos.siguiente():
                    print(atributos)
                selectLayer = capa.selectQgis(atributos.listaQgis())
                print('  ->', selectLayer)
        except Exception as e:
            print(str(e))

    def loadProject(self, idProyecto: str, idsCapasExcluidas: str = '', agrupar: bool = True, srid: str = '25831') -> None:
        if self.db is None: return
        try:
            qtWdg.QApplication.instance().setOverrideCursor(qtCor.Qt.WaitCursor)
            if agrupar: orden = 'desc'
            else: orden = ''
            capa = QvCapaVcad(self.db, idProyecto, idsCapasExcluidas, orden=orden)
            grupo = None
            while capa.siguiente():
                if self.debug: print(capa)
                atributos = QvAtributosVcad(self.db, capa.ID)
                while atributos.siguiente():
                    if self.debug: print(atributos)
                if agrupar and capa.primero():
                    grupo = self.root.addGroup(capa.NOM_PROJECTE)
                selectLayer = capa.selectQgis(atributos.listaQgis())
                if self.debug: print('  ->', selectLayer)
                layer = self.loadLayer(capa.NOM, capa.TIPUS, selectLayer, srid)
                if layer is not None:
                    capa.simbologia(layer.renderer().symbol())
                    # if capa.MOSTRAR_ETIQUETA == 1:
                    #     layer.setDisplayExpression('ETIQUETA')
                    if capa.ESCALA_MIN > 0.0 or capa.ESCALA_MAX > 0.0:
                        layer.setScaleBasedVisibility(True)
                        layer.setMinimumScale(capa.ESCALA_MAX)  # Al revés ????
                        layer.setMaximumScale(capa.ESCALA_MIN)
                    else:
                        layer.setScaleBasedVisibility(False)
                    if agrupar:
                        self.project.addMapLayer(layer, False)
                        grupo.addLayer(layer)
                    else:
                        self.project.addMapLayer(layer)
        except Exception as e:
            print(str(e))
        finally:
            qtWdg.QApplication.instance().restoreOverrideCursor()

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    # from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = qgGui.QgsMapCanvas()
        # canvas = QvCanvas()

        # inicial = cfg.projecteInicial
        inicial = 'd:/temp/TestVistacad.qgs'

        leyenda = QvLlegenda(canvas)
        leyenda.readProject(inicial)

        canvas.setWindowTitle('Canvas - ' + inicial)
        canvas.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        # Acciones de usuario para el menú

        def testVistacad():
            print('ini test Vistacad')
            # vCad = QvVistacad()
            # vCad.loadProject('341', '3601, 3602')
            # 341 - CarrilsBici
            # 2761 - Superilles
            # 3461 - Idees_per_Qvista
            QvVistacad.carregaProjecte('341')
            QvVistacad.carregaProjecte('2761')
            QvVistacad.carregaProjecte('3461')
            print('fin test Vistacad')

            # layer = leyenda.capaPerNom('Senyals')
            # renderer = layer.renderer()
            # symbol = renderer.symbol()
            # print('OLD:', symbol.symbolLayer(0).properties())
            # newSymbolLayer = qgCor.QgsSimpleLineSymbolLayer.create(
            # {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'MM', 'draw_inside_polygon': '0', 
            # 'joinstyle': 'bevel', 'line_color': '255,0,0,255', 'line_style': 'dash', 'line_width': '3', 'line_width_unit': 'Pixel', 'offset': '0', 
            # 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}
            # )
            # symbol.changeSymbolLayer(0, newSymbolLayer)
            # print('NEW:', symbol.symbolLayer(0).properties())
            # leyenda.refreshLayerSymbology(layer.id())
            # layer.triggerRepaint()

        def writeProject():
            print('write file')
            leyenda.project.write()

        def openProject():
            dialegObertura = qtWdg.QFileDialog()
            dialegObertura.setDirectoryUrl(qtCor.QUrl('D:/Temp/'))
            mapes = "Tots els mapes acceptats (*.qgs *.qgz);; " \
                    "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)"
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis",
                                                      "D:/Temp/", mapes)
            if nfile != '':

                print('read file ' + nfile)
                ok = leyenda.readProject(nfile)
                if ok:
                    canvas.setWindowTitle('Canvas - ' + nfile)
                else:
                    print(leyenda.project.error().summary())

        act = qtWdg.QAction()
        act.setText("Test Vistacad")
        act.triggered.connect(testVistacad)
        leyenda.accions.afegirAccio('testVistacad', act)

        act = qtWdg.QAction()
        act.setText("Desa projecte")
        act.triggered.connect(writeProject)
        leyenda.accions.afegirAccio('writeProject', act)

        act = qtWdg.QAction()
        act.setText("Obre projecte")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('testVistacad')
                leyenda.menuAccions.append('writeProject')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)
