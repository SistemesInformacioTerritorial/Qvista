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
    def __init__(self, db):
        self.db = db

    def ejecuta(self, select):
        if self.db is None: return None
        query = qtSql.QSqlQuery(self.db)
        try:
            query.setForwardOnly(True)
            query.exec_(select)
            return query
        except Exception as e:
            print(str(e))
            return None

    def siguiente(self):
        if self.db is None: return False
        ok = self.query.next()
        if ok:
            self.registro()
        return ok

    def num(self):
        return self.query.at()

    def primero(self):
        return self.num() == 0

    def registro(self):
        pass

class QvCapaVcad(QvObjVcad):
    
    def __init__(self, db, idProyecto, idsCapasExcluidas='0', orden=''):
        super().__init__(db)
        self.idProyecto = idProyecto
        self.idsCapasExcluidas = idsCapasExcluidas
        self.orden = orden
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)

    def consulta(self):
        return f"select p.nom nom_projecte, p.descripcio desc_projecte, c.* " \
               f"from vistacad_u.projectes p, vistacad_u.capes c " \
               f"where p.id = {self.idProyecto} and p.actiu = 1 " \
               f"and p.id = c.id_projecte and c.actiu = 1 " \
               f"and c.id not in ({self.idsCapasExcluidas}) " \
               f"order by ordre_visual {self.orden}"

    def registro(self):
        self.NOM_PROJECTE = self.query.value('NOM_PROJECTE')
        self.DESC_PROJECTE = self.query.value('DESC_PROJECTE')
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        self.MOSTRAR_ETIQUETA = math.trunc(self.query.value('MOSTRAR_ETIQUETA'))
        self.ESCALA_MIN = self.query.value('ESCALA_MIN')
        self.ESCALA_MAX = self.query.value('ESCALA_MAX')

    def selectQgis(self, atributos):
        ini = f"select id, etiqueta, "
        fin = f"geom from vistacad_u.geometries where actiu = 1 and id_capa = {self.ID}"
        if atributos is None:
            select = f"{ini}{fin}"
        else:
            select = f"{ini}{atributos}{fin}"
        return select

    def __str__(self):
        if self.primero():
            if self.DESC_PROJECTE.isNull():
                linea = f"Proyecto: {self.NOM_PROJECTE}"
            else:
                linea = f"Proyecto: {self.NOM_PROJECTE}, {self.DESC_PROJECTE}"
            print(linea)
        return f"- Capa {self.num()+1}: {self.ID}, {self.NOM}, {self.TIPUS}"

class QvAtributosVcad(QvObjVcad):

    def __init__(self, db, idCapa):
        super().__init__(db)
        self.idCapa = idCapa
        self.select = self.consulta()
        self.query = self.ejecuta(self.select)
        self.lista = ''

    def consulta(self):
        return f"select a.* " \
               f"from vistacad_u.capes c, vistacad_u.formularis f, vistacad_u.atributs a " \
               f"where c.id = {self.idCapa} and c.actiu = 1 " \
               f"and c.id_formulari = f.id and f.actiu = 1 " \
               f"and a.id_formulari = f.id and a.actiu = 1 " \
               f"order by a.ordre"

    def registro(self):
        self.ID = math.trunc(self.query.value('ID'))
        self.NOM = self.query.value('NOM')
        self.TIPUS = math.trunc(self.query.value('TIPUS'))
        self.lista = f"extractValue(attrs,'/OBJ/a{self.ID}') {self.NOM}, "

    def listaQgis(self):
        return self.lista

    def __str__(self):
        return f"  + Atributo {self.num()+1}: {self.NOM}, {self.TIPUS}"

class QvVistacad:
    """ Clase para importar projectos de Visatacad a Qvista
        Tablas consultadas: projectes, capes, formularis, atributs, geometries

        Falta incorporar:
        - Simbología geometrías
        - Simbología etiquetas
        - Tipos de atributos en formulario
    """ 

    def __init__(self):
        self.conexion = QvApp().dbQvista
        self.db = QvApp().dbLog
        if self.db is None:
            QvApp().dbLogConnexio()
            self.db = QvApp().dbLog
        self.project = qgCor.QgsProject.instance()
        self.root = self.project.layerTreeRoot()

    def loadLayer(self, nom, tipus, select, srid='25831', id="ID", geom="GEOM"):
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

    def loadProject(self, idProyecto, idsCapasExcluidas='0', agrupar=True, srid='25831'):
        if self.db is None: return
        if agrupar: orden = ''
        else: orden = 'desc'
        capa = QvCapaVcad(self.db, idProyecto, idsCapasExcluidas, orden=orden)
        grupo = None
        while capa.siguiente():
            if agrupar and capa.primero():
                grupo = self.root.addGroup(capa.NOM_PROJECTE)
            # print(capa)
            atributos = QvAtributosVcad(self.db, capa.ID)
            while atributos.siguiente():
                # print(atributos)
                pass
            selectLayer = capa.selectQgis(atributos.listaQgis())
            # print('  ->', selectLayer)
            layer = self.loadLayer(capa.NOM, capa.TIPUS, selectLayer, srid)
            if layer is not None:
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
            print('carrils bici')
            vCad = QvVistacad()
            vCad.loadProject('341', '3601, 3602')

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
        act.setText("Carrega carrils bici")
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
