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

import math

class QvObjVcad:
    def __init__(self, db: qtSql.QSqlDatabase) -> None:
        self.db = db

    def ejecuta(self, select: str) -> qtSql.QSqlQuery:
        if self.db is None: return None
        query = qtSql.QSqlQuery(self.db)
        try:
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
        if not hasattr(self, 'ID'): return ''
        if self.primero():
            if self.DESC_PROJECTE.isNull():
                linea = f"Proyecto: {self.NOM_PROJECTE}"
            else:
                linea = f"Proyecto: {self.NOM_PROJECTE}, {self.DESC_PROJECTE}"
            print(linea)
        return f"- Capa {self.num()+1}: {self.ID}, {self.NOM}, {self.TIPUS}"

    def consulta(self) -> str:
        if self.idsCapasExcluidas == '':
            filtroCapas = ''
        else:
            filtroCapas = f"and c.id not in ({self.idsCapasExcluidas}) "
        return f"select p.nom nom_projecte, p.descripcio desc_projecte, c.* " \
               f"from vistacad_u.projectes p, vistacad_u.capes c " \
               f"where p.id = {self.idProyecto} and p.actiu = 1 " \
               f"and p.id = c.id_projecte and c.actiu = 1 " \
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

    def selectQgis(self, atributos: str) -> str:
        ini = f"select id, etiqueta, "
        fin = f"geom from vistacad_u.geometries where actiu = 1 and id_capa = {self.ID}"
        return f"{ini}{atributos}{fin}"

class QvAtributosVcad(QvObjVcad):

    def __init__(self, db: qtSql.QSqlDatabase, idCapa: str):
        super().__init__(db)
        self.idCapa = idCapa
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)
        self.lista = ''

    def __str__(self):
        if not hasattr(self, 'ID'): return ''
        return f"  + Atributo {self.num()+1}: {self.NOM}, {self.TIPUS}"

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
        self.lista = f"extractValue(attrs,'/OBJ/a{self.ID}') \"{self.NOM}\", "

    def listaQgis(self) -> str:
        return self.lista

class QvVistacad:
    """ Clase para importar projectos de Visatacad a Qvista
        Tablas consultadas: projectes, capes, formularis, atributs, geometries

        Falta incorporar:
        - Simbología geometrías
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

    def printProject(self, idProyecto: str, idsCapasExcluidas: str = '', agrupar: bool = True, srid: str = '25831') -> None:
        if self.db is None: return
        try:
            if agrupar: orden = ''
            else: orden = 'desc'
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
            if agrupar: orden = ''
            else: orden = 'desc'
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
                    # Simbología lineal:
                    # LINEA_GRUIX
                    # LINIA_COLOR
                    # LINIA_TIPUS
                    if capa.MOSTRAR_ETIQUETA == 1:
                        layer.setDisplayExpression('ETIQUETA')
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

        inicial = cfg.projecteInicial
        # inicial = 'd:/temp/test.qgs'

        leyenda = QvLlegenda(canvas)
        leyenda.readProject(inicial)

        canvas.setWindowTitle('Canvas - ' + inicial)
        canvas.show()

        leyenda.setWindowTitle('Llegenda')
        leyenda.show()

        # Acciones de usuario para el menú

        def carrilsBici():
            print('ini carrils bici')
            # vCad = QvVistacad()
            # vCad.loadProject('341', '3601, 3602')
            QvVistacad.carregaProjecte('341', '3601, 3602')
            print('fin carrils bici')

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
        act.setText("Carrils bici")
        act.triggered.connect(carrilsBici)
        leyenda.accions.afegirAccio('carrilsBici', act)

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
                leyenda.menuAccions.append('carrilsBici')
                leyenda.menuAccions.append('writeProject')
                leyenda.menuAccions.append('openProject')

        # Conexión de la señal con la función menuContexte para personalizar el menú
        leyenda.clicatMenuContexte.connect(menuContexte)
