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

    def capesSelect(self, idProyecto, idsCapasExcluidas='0', orden=''):
        return f"select p.nom nom_projecte, p.descripcio desc_projecte, c.* " \
               f"from vistacad_u.projectes p, vistacad_u.capes c " \
               f"where p.id = {idProyecto} and p.actiu = 1 " \
               f"and p.id = c.id_projecte and c.actiu = 1 " \
               f"and c.id not in ({idsCapasExcluidas}) " \
               f"order by ordre_visual {orden}"

    def capaPrint(self, query):
        if query is None: return
        try:
            num = query.at()
            if num == 0:
                nom = query.value('NOM_PROJECTE')
                desc = query.value('DESC_PROJECTE')
                if desc.isNull():
                    linea = f"Proyecto: {nom}"
                else:
                    linea = f"Proyecto: {nom}, {desc}"
                print(linea)
            linea = f"- Capa {num+1}: {math.trunc(query.value('ID'))}, {query.value('NOM')}, {math.trunc(query.value('TIPUS'))}"
            print(linea)
        except Exception as e:
            print(str(e))

    def atributsSelect(self, idCapa):
        return f"select a.* " \
               f"from vistacad_u.capes c, vistacad_u.formularis f, vistacad_u.atributs a " \
               f"where c.id = {idCapa} and c.actiu = 1 " \
               f"and c.id_formulari = f.id and f.actiu = 1 " \
               f"and a.id_formulari = f.id and a.actiu = 1 " \
               f"order by a.ordre"

    def atributPrint(self, query):
        if query is None: return
        try:
            num = query.at()
            linea = f"  + Atributo {num+1}: {query.value('NOM')}, {math.trunc(query.value('TIPUS'))}"
            print(linea)
        except Exception as e:
            print(str(e))

    def capaAtributs(self, query):
        if query is None: return
        try:
            num = query.at()
            if num == 0: self.atributsCapa = ""
            item = f"extractValue(attrs,'/OBJ/a{math.trunc(query.value('ID'))}') {query.value('NOM')}"
            self.atributsCapa = f"{self.atributsCapa}{item}, "
        except Exception as e:
            print(str(e))

    def capaSelect(self, idCapa):
        ini = f"select id, etiqueta, "
        fin = f"geom from vistacad_u.geometries where actiu = 1 and id_capa = {idCapa}"
        if self.atributsCapa is None:
            return f"{ini}{fin}"
        else:
            return f"{ini}{self.atributsCapa}{fin}"

    def queryExec(self, select):
        if self.db is None: return None
        query = qtSql.QSqlQuery(self.db)
        try:
            query.setForwardOnly(True)
            query.exec_(select)
            return query
        except Exception as e:
            print(str(e))
            return None

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
        if agrupar: order = ''
        else: order = 'desc'
        queryCapes = self.queryExec(self.capesSelect(idProyecto, idsCapasExcluidas, orden=order))
        grupo = None
        while queryCapes.next():
            if agrupar and queryCapes.at() == 0:
                nomProyecto = queryCapes.value('NOM_PROJECTE')
                root = self.project.layerTreeRoot()
                grupo = root.addGroup(nomProyecto)
            # self.capaPrint(queryCapes)
            idCapa = math.trunc(queryCapes.value('ID'))
            nomCapa = queryCapes.value('NOM')
            tipusCapa = math.trunc(queryCapes.value('TIPUS'))
            queryAtributs = self.queryExec(self.atributsSelect(idCapa))
            self.atributsCapa = None
            while queryAtributs.next():
                # self.atributPrint(queryAtributs)
                self.capaAtributs(queryAtributs)
            selectCapa = self.capaSelect(idCapa)
            # print('  -> ', selectCapa)
            capa = self.loadLayer(nomCapa, tipusCapa, selectCapa, srid)
            minScale = queryCapes.value('ESCALA_MIN')
            maxScale = queryCapes.value('ESCALA_MAX')
            if minScale > 0.0 or maxScale > 0.0:
                capa.setScaleBasedVisibility(True)
                capa.setMinimumScale(maxScale)  # Al revés ????
                capa.setMaximumScale(minScale)
            else:
                capa.setScaleBasedVisibility(False)
            if capa is not None:
                if agrupar:
                    self.project.addMapLayer(capa, False)
                    grupo.addLayer(capa)
                else:
                    self.project.addMapLayer(capa)

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
