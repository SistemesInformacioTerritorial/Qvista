# -*- coding: utf-8 -*-


import math
from pathlib import Path
from typing import List, TextIO

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtSql as qtSql
import qgis.PyQt.QtWidgets as qtWdg
import qgis.utils as qgUts

from configuracioQvista import dadesdir
from moduls.QvApp import QvApp
from moduls.QvVistacadVars import (ROTATION_FIELD, VCAD_COLORS,
                                   VCAD_FILL_STYLES, VCAD_LINE_STYLES,
                                   VCAD_SYMBOLS)


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

class QvProjectoVcad(QvObjVcad):
    
    def __init__(self, db: qtSql.QSqlDatabase):
        super().__init__(db)
        self.usuari = QvApp().usuari
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)
        self.lista = {}

    def __str__(self):
        try:
            if not hasattr(self, 'ID'): return ''
            return f"- Proyecto {self.ID}: {self.NOM}"
        except Exception as e:
            print(str(e))
            return ''

    def consulta(self) -> str:
        if self.debug and self.usuari == 'DE1717':
            return f"select p.* from vistacad_u.projectes p " \
                   f"where p.actiu = 1 " \
                   f"order by p.data_modificacio desc"
        else:
            return f"select p.* from vistacad_u.permisos u, vistacad_u.projectes p " \
                   f"where u.usuari = '{self.usuari}' and u.actiu = 1 " \
                   f"and u.id_projecte = p.id and p.actiu = 1 " \
                   f"order by p.data_creacio"

    def registro(self) -> None:
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.NOM = self.NOM.strip()
        self.DESCRIPCIO = self.query.value('DESCRIPCIO')
        self.lista[self.ID] = self.NOM

class QvAtributoVcad(QvObjVcad):

    def __init__(self, db: qtSql.QSqlDatabase, idCapa: str, lookup: bool = True, types: bool = False):
        super().__init__(db)
        self.idCapa = idCapa
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)
        self.lookup = lookup
        self.types = types
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

    def campo(self) -> str:
        # TIPUS:
        #  0 - Texto
        #  1 - Entero
        #  2 - Real
        #  3 - Fecha
        #  4 - Fecha y hora
        #  5 - Opciones de lista
        #  6 - Opción de geometria
        #  7 - Opción de lista externa
        #  8 - Enlace a fichero o URL
        #  9 - Booleano
        # 10 - Lista de subformulario
        valor = f"extractValue(attrs,'/OBJ/a{self.ID}')" 
        if self.types:
            if self.TIPUS == 1: # Entero
                valor = f"cast({valor} as NUMBER(*,0))"
            elif self.TIPUS == 2: # Real
                valor = f"cast({valor} as FLOAT)"
            elif self.TIPUS == 3: # Fecha
                valor = f"to_date({valor}, 'DD/MM/YYYY')"
            elif self.TIPUS == 4: # Fecha y hora
                valor = f"to_date({valor}, 'DD/MM/YYYY')" #...........
        alias = f"{valor} \"{self.NOM}\", "
        if self.TIPUS == 5 and self.lookup: # Opciones de lista
            alias += f"vistacad_u.VALOR_ATRIBUTO({self.ID}, {valor}) \"{self.NOM} Text\", "
        return alias

    def registro(self) -> None:
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.NOM = self.NOM.strip()
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        self.lista += self.campo()

class QvCapaVcad(QvObjVcad):
    
    def __init__(self, db: qtSql.QSqlDatabase, idProyecto: str, idsCapas: str = '', capasIncluidas: bool = True, orden: str = 'c.nom'):
        super().__init__(db)
        self.idProyecto = idProyecto
        self.idsCapas = idsCapas
        self.capasIncluidas = capasIncluidas
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
        if self.idsCapas == '':
            filtroCapas = ''
        else:
            if self.capasIncluidas:
                switch = ''
            else:
                switch = 'not '
            filtroCapas = f"and c.id {switch}in ({self.idsCapas}) "
        return f"select p.nom nom_projecte, p.descripcio desc_projecte, c.*, s.nom nom_simbol, s.rotable rotable_simbol " \
               f"from vistacad_u.projectes p, vistacad_u.capes c, vistacad_u.construccions_grafiques s " \
               f"where p.id = {self.idProyecto} and p.actiu = 1 " \
               f"and p.id = c.id_projecte and c.actiu = 1 " \
               f"and c.id_const_grafica = s.id(+) " \
               f"{filtroCapas}" \
               f"order by {self.orden}"

    def registro(self) -> None:
        self.NOM_PROJECTE = self.query.value('NOM_PROJECTE')
        self.NOM_PROJECTE = self.NOM_PROJECTE.strip()
        self.DESC_PROJECTE = self.query.value('DESC_PROJECTE')
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.NOM = self.NOM.strip()
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        # TIPUS:
        # 1 - Punto
        # 2 - Línea
        # 3 - Polígono
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

    def selectQgis(self, atributos: QvAtributoVcad) -> str:
        if self.TIPUS == 1: # Punto
            campos = f"trunc(rotacio) \"{ROTATION_FIELD}\", "
        else:
            campos = ""
        return f"select id, {atributos.lista}{campos}" \
               f"geom from vistacad_u.geometries g " \
               f"where actiu = 1 and id_capa = {self.ID}"

    def simbologia(self, symbol: qgCor.QgsSymbol) -> None:
        if self.TIPUS == 1: # Punto
            props = self.symbolQgis()
            if props:
                props['color'] = self.lineColorQgis()
                symbolLayer = qgCor.QgsSimpleMarkerSymbolLayer.create(props)
                if self.ROTABLE_SIMBOL == 1:
                    prop = qgCor.QgsProperty()
                    prop.setExpressionString(f"-\"{ROTATION_FIELD}\"{props['angle']}") 
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

class QvVistacad:
    """ Clase para importar projectos de Visatacad a Qvista
        Tablas consultadas: permisos, projectes, capes, formularis, atributs, geometries

        Falta incorporar o comprobar:
        - Orden visualización capas
        - Simbología geometrías estatica y dinámica
        - Simbología etiquetas
        - Tipos de atributos y formulario
        - Bases cartográficas
        - Paneles
    """ 
    @classmethod
    def carregaProjecte(cls, idProjecte: str, idsCapes: str = '', capesIncluides: bool = True) -> None:
        try:
            vCad = cls()
            vCad.loadProject(idProjecte, idsCapes, capesIncluides)
        except Exception as e:
            print('Error QvVistacad.carregaProjecte: ' + str(e))

    @classmethod
    def formulariProjectes(cls) -> None:
        try:
            vCad = cls()
            vCad.formProjects()
        except Exception as e:
            print('Error QvVistacad.formulariProjectes: ' + str(e))

    def __init__(self):
        self.debug = (__name__ == "__main__")
        self.conexion = QvApp().dbQvista
        self.db = QvApp().dbLog
        if self.db is None:
            QvApp().dbLogConnexio()
            self.db = QvApp().dbLog
        self.project = qgCor.QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.gpkgFile = ''

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
            return layer
        else:
            return None

    def exportLayer(self, layer: qgCor.QgsVectorLayer, nomProyecto: str, nomCapa: str, simbologia: bool = False) -> None:
        # Guardar geopackage
        gpkgPath = Path(dadesdir, nomProyecto).with_suffix('.gpkg')
        self.gpkgFile = str(gpkgPath)
        options = qgCor.QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = nomCapa
        if gpkgPath.exists():
            options.actionOnExistingFile = qgCor.QgsVectorFileWriter.CreateOrOverwriteLayer
        else:
            options.actionOnExistingFile = qgCor.QgsVectorFileWriter.CreateOrOverwriteFile
        if QvApp().testVersioQgis(3, 10):
            res, txt = qgCor.QgsVectorFileWriter.writeAsVectorFormatV2(
                layer, self.gpkgFile, qgCor.QgsCoordinateTransformContext(), options)
        else:
            res, txt = qgCor.QgsVectorFileWriter.writeAsVectorFormat(layer, self.gpkgFile, options)
        if res != qgCor.QgsVectorFileWriter.NoError:
            print(f"*** Error guardando geopackage: {res}:{txt}")
        if simbologia:
            # Guardar fichero estilo
            qmlPath = Path(dadesdir, nomCapa).with_suffix('.qml')
            qmlFile = str(qmlPath)
            txt, res = layer.saveNamedStyle(qmlFile)
            if not res:
                print(f"*** Error guardando qml: {txt}")
            # Guardar estilo en geopackage
            gpkgLayer = qgCor.QgsVectorLayer(f'{self.gpkgFile}|layername={nomCapa}', nomCapa, 'ogr')
            if gpkgLayer.isValid():
                res = gpkgLayer.loadNamedStyle(qmlFile)
                if res:
                    s = QvApp().settings
                    s.setValue("qgis/overwriteStyle", True)
                    txt = gpkgLayer.saveStyleToDatabase("vistacad", "", True, "")
                    if txt != '':
                        print(f"*** Error guardando simbologia: {txt}")
                else:
                    print(f"*** Error fichero qml: {qmlFile}") 
            qmlPath.unlink()

    def loadProject(self, idProyecto: str, idsCapas: str = '', capasIncluidas: bool = True, srid: str = '25831',
                    agrupar: bool = False, simbologia: bool = False, geopackage: bool = False) -> None:
        if self.db is None: return
        if idProyecto is None or idProyecto == '': return
        try:
            qtWdg.QApplication.instance().setOverrideCursor(qtCor.Qt.WaitCursor)
            capa = QvCapaVcad(self.db, idProyecto, idsCapas, capasIncluidas)
            grupo = None
            self.gpkgFile = ''
            while capa.siguiente():
                if self.debug: print(capa)
                atributos = QvAtributoVcad(self.db, capa.ID)
                while atributos.siguiente():
                    if self.debug: print(atributos)
                if agrupar and capa.primero():
                    grupo = self.root.addGroup(capa.NOM_PROJECTE)
                selectLayer = capa.selectQgis(atributos)
                if self.debug: print('  ->', selectLayer)
                layer = self.loadLayer(capa.NOM, capa.TIPUS, selectLayer, srid)
                if layer is not None:
                    if simbologia:
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
                    if geopackage:
                        self.exportLayer(layer, capa.NOM_PROJECTE, capa.NOM, simbologia)
            qtWdg.QApplication.instance().restoreOverrideCursor()
            if self.gpkgFile != '':
                qtWdg.QMessageBox.information(None, 'Informació',
                    f"Les capes del projecte de Vistacad \"{capa.NOM_PROJECTE}\" s'han desat a l'arxiu \"{self.gpkgFile}\"")
            
        except Exception as e:
            qtWdg.QApplication.instance().restoreOverrideCursor()
            print(str(e))

    def formProjects(self) -> None:
        if self.db is None: return
        proyectos = QvProjectoVcad(self.db)
        while proyectos.siguiente():
            if self.debug: print(proyectos)
        if len(proyectos.lista) < 1: return
        form = QvProyectoFormVcad(proyectos.lista)
        if form.exec_() and form.idProjecte:
            self.loadProject(form.idProjecte, agrupar=form.agrupar.isChecked(), simbologia=form.simbologia.isChecked(), geopackage=form.geopackage.isChecked())

class QvProyectoFormVcad(qtWdg.QDialog):
    def __init__(self, lista, parent=None, modal=True):
        super().__init__(parent, modal=modal)
        self.setWindowTitle('Importar projecte de Vistacad')
        self.init()

        self.combo = qtWdg.QComboBox(self)
        self.combo.setEditable(False)
        self.combo.addItem('Selecciona projecte…')
        for id, nombre in lista.items():
            self.combo.addItem(f"{nombre} ({id})", id)

        self.agrupar = qtWdg.QCheckBox('Agrupar capes')
        self.simbologia = qtWdg.QCheckBox('Importar simbologia')
        self.geopackage = qtWdg.QCheckBox('Desar arxiu geopackage')

        self.buttons = qtWdg.QDialogButtonBox(qtWdg.QDialogButtonBox.Ok | qtWdg.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.cancel)

        self.layout = qtWdg.QVBoxLayout()
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.agrupar)
        self.layout.addWidget(self.simbologia)
        self.layout.addWidget(self.geopackage)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def init(self):
        self.idProjecte = ''

    def accept(self):
        if self.combo.currentData() is None:
            self.idProjecte = ''
        else:
            self.idProjecte = str(self.combo.currentData())
        super().accept()

    def cancel(self):
        self.init()
        super().reject()

if __name__ == "__main__":

    from moduls.QvApp import QvApp
    QvApp(produccio='True')
    QvApp().intranet = True

    from qgis.core.contextmanagers import qgisapp

    import configuracioQvista as cfg
    # from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda

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

            vCad = QvVistacad()
            vCad.formProjects()

            # 341 - CarrilsBici
            # 2761 - Superilles
            # 3461 - Idees_per_Qvista
            # QvVistacad.carregaProjecte('341')
            # QvVistacad.carregaProjecte('2761')
            # QvVistacad.carregaProjecte('3461')
            # QvVistacad.carregaProjecte('341', '3601')

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
