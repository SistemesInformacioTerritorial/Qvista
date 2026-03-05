# ---------------------------------------------
# qMaBIM.py - Script principal de la aplicación MaBIM
# ---------------------------------------------
# Este script implementa la interfaz principal de la aplicación MaBIM,
# basada en PyQt5 y QGIS Python API. Permite la gestión de capas,
# consultas, visualización de atributos y herramientas GIS personalizadas
# para la gestión de patrimonio inmobiliario del Ajuntament de Barcelona.
#
# Estructura principal:
# - Clase QMaBIM: Ventana principal, gestión de UI y lógica de negocio
# - Carga dinámica de consultas desde JSON externo
# - Integración con QvAtributs para tablas de atributos
# - Funciones para exportar, filtrar y gestionar capas
# ---------------------------------------------

#from MaBIM-ui import Ui_MainWindow
import argparse
import functools
import getpass
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence
from functools import partial

import configuracioQvista
from moduls import QvFuncions
from moduls.QvApp import QvApp
from moduls.QvAtributs import QvAtributs, QvTaulaAtributs
from moduls.QvAtributsForms import QvFitxesAtributs, QvFormAtributs
from moduls.QvCanvas import QvCanvas
from moduls.QvCanvasAuxiliar import QvCanvasAuxiliar
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QvConstants import QvConstants
from moduls.QvEinesGrafiques import QvMesuraGrafica
from moduls.QvFavorits import QvFavorits
from moduls.QvLlegenda import QvLlegenda
from moduls.QvMapetaBrujulado import QvMapetaBrujulado
from moduls.QvSingleton import Singleton
from moduls.QvStatusBar import QvStatusBar
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from qgis.core import (QgsCoordinateReferenceSystem, QgsFeatureRequest,
                       QgsGeometry, QgsMapLayer, QgsPointXY, QgsProject,
                       QgsRectangle, QgsVectorLayer, QgsExpressionContextUtils,
                       QgsLayerDefinition)
from qgis.core.contextmanagers import qgisapp
from qgis.gui import (QgsGui, QgsLayerTreeMapCanvasBridge, QgsMapTool,
                      QgsRubberBand, QgsVertexMarker)
import qgis.PyQt.QtWidgets as qtWdg

import webbrowser
from PyQt5.QtWidgets import QHeaderView, QToolButton
from PyQt5.QtGui import QIcon

class ConstantsMaBIM:
    DB_MABIM_PRO = {
        'Database': 'QOCISPATIAL',
        'HostName': 'GEOPR1.imi.bcn',
        'Port': 1551,
        'DatabaseName': 'GEOPR1',
        'UserName': 'PATRIMONI_CONS',
        'Password': 'PATRIMONI_CONS'
    }

    rutaUI= 'Programes especifics/MaBIM/MaBIM.ui'
    rutaProjecte = 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/PPM_CatRegles_geopackage.qgs'
    #rutaProjecte = 'u:/Quota/comu_imi/jca/PPM_CatRegles_geopackage.qgs'
    rutaProjecteEdicio = 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/mabimEDICIO_v3.qgs'

    rutaLogoAjuntament = 'imatges/escutDreta.png'

    nomCapaPH = 'Entitats en PH'
    nomCapaPV = 'Entitats en PV'
    nomCapaQuioscos = 'Altres Béns i Drets'
    urlPIP = 'https://netiproa.corppro.imi.bcn:447/pip/ca/'

    nomsCapes = [nomCapaPH, nomCapaPV, nomCapaQuioscos]
    # nomCapaRegistrals = 'Registrals'
    nomGrupRegistrals = 'Registrals'

    rangBarcelona = QgsRectangle(QgsPointXY(405960, 4572210), QgsPointXY(452330 , 4595090))


    # Consulta a partir del text escrit al camp de cerca.
    # Obté el codi BIM, la descripció i la denominació.
    CONSULTA_DATA_DADES = '''SELECT DATA FROM DATES_PROCESSOS WHERE (PROCES LIKE '%'||:pText||'%')'''
    
    CONSULTA_CERCADOR = '''SELECT BIM, DESCRIPCIO_BIM, DENOMINACIO_BIM
                            FROM
                            ZAFT_0002
                            WHERE
                            ((BIM LIKE '%'||:pText||'%')
                                OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
                                OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
                                OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
                            AND (ROWNUM < 100)''' #aquesta consulta haurà d'estar en un arxiu, però ja es farà'''

    #Informacio identificativa del bim
    #Pel camp superficie utilitzable de la taula ZAFT_0012 cal agafar la divisio 0000 que agrupa les altres dues 

    CONSULTA_INFO_BIM_Z2 = '''SELECT A.BIM, A.ESTAT,A.SUBGOOD_STATUS, A.DESCRIPCIO_BIM, A.DENOMINACIO_BIM,
                              A.TIPOLOGIA_BIM, A.SUBTIPOLOGIA_BIM, A.GRUP_BIM, A.SUBGRUP_BIM,A.TIPUS_IMMOBLE,
                              A.QUALIFICACIO_JURIDICA,C.QUALIFICACIO_URB,
                              E.SUP_UTILITZABLE,
                              B.SUP_CADASTRAL_SOL,B.SUP_CADASTRAL_CONS,D.SUP_REGISTRAL_SOL,D.SUP_REGISTRAL_CONS,
                              B.REF_CADASTRE,B.NUM_IMMOBLES,B.ESTAT_CADASTRAL
                              FROM 
                              ZAFT_0002 A
                              LEFT OUTER JOIN ZAFT_0007 B 
                              ON A.BIM = B.BIM
                              LEFT OUTER JOIN ZAFT_0005 C
                              ON C.BIM = A.BIM
                              LEFT OUTER JOIN ZAFT_0013 D
                              ON D.BIM = A.BIM
                              LEFT OUTER JOIN ZAFT_0012 E
                              ON E.BIM = A.BIM AND E.DG='000000'
                              WHERE 
                              ((A.BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

    # Consulta que obté adreces de ZAFT_0003 a partir del codi BIM
    CONSULTA_INFO_BIM_Z3 = '''SELECT TIPUS_VIA, NOM_VIA, NUM_INI,
                               LLETRA_INI, NUM_FI, LLETRA_FI, DISTRICTE, BARRI, MUNICIPI, CP,
                               PROVINCIA, TIPUS
                               FROM ZAFT_0003
                               WHERE
                               ((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

    # Consulta dades titularitat
    CONSULTA_INFO_BIM_Z13 = '''SELECT PROPIETARI_SOL, PROPIETARI_CONS, TO_CHAR(DATA_ADQ_HD, 'DD/MM/YYYY'), TITOL_ADQ_HD, PERCENT_PROP_HD,
                                ESTAT_INSCRIPCIO,  TO_CHAR(DATA_INSCRIPCIO, 'DD/MM/YYYY'),
                                CASE 
                                WHEN DATA_INSCRIPCIO_CARTO IS NULL THEN 'No'
                                ELSE 'Sí'
                                END AS INSCRIT,
                                TO_CHAR(DATA_INSCRIPCIO_CARTO, 'DD/MM/YYYY')
                                FROM ZAFT_0013
                                WHERE
                                ((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

    # Consulta titularitat detall
    CONSULTA_INFO_BIM_Z11 = '''SELECT A.FINCA, A.NUM_REGISTRE, B.TIPUS_PROP_FINCA_REG, B.DESCRIPCIO_FINCA_REG,
                               A.SUP_REGISTRAL_SOL, A.SUP_REGISTRAL_CONS, A.CARREGUES
                               FROM 
                               ZAFT_0011 A
                               JOIN 
                               ZAFT_0009 B 
                               ON A.BIM = B.BIM
                               WHERE 
                               ((A.BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''
    
    campEditorsQGIS = 'qMaBIM_QGISEditors'


# això estaria millor dins de la classe Consulta, però no va
# No es pot utilitzar fora d'aquesta classe
# és un decorador que garanteix que la Base de Dades estigui oberta
def connexio(func):
    def _funcio(self,*args,**kwargs):
        if self.OBRE_DB():
            return func(self,*args,**kwargs)
        return []
    return _funcio

class Consulta(Singleton):
    def __init__(self):
        if hasattr(self,'db'):
            return
        self.dbMaBIM=ConstantsMaBIM.DB_MABIM_PRO
        self.obte_camps_restants()
        self.db = QSqlDatabase.addDatabase(self.dbMaBIM['Database'], 'CERCADOR')
        if self.db.isValid():
            self.db.setHostName(self.dbMaBIM['HostName'])
            self.db.setPort(self.dbMaBIM['Port'])
            self.db.setDatabaseName(self.dbMaBIM['DatabaseName'])
            self.db.setUserName(self.dbMaBIM['UserName'])
            self.db.setPassword(self.dbMaBIM['Password'])
        else:
            # missatge avisant de que no funciona, que tornin a intentar-ho
            pass

    # ACTUALMENT NO FA RES
    # Serviria per si no podem desar l'usuari i la contrasenya en el codi, que el propi usuari pugui introduir-los durant l'execució
    # Es conserva per si fes falta
    def obte_camps_restants(self):
        while self.dbMaBIM['UserName'] in (None, ''):
            self.dbMaBIM['UserName'], _ = QtWidgets.QInputDialog.getText(None,'Usuari de la base de dades',f"Introduïu el nom d'usuari de la base de dades {self.dbMaBIM['DatabaseName']}")
        while self.dbMaBIM['Password'] in (None, ''):
            self.dbMaBIM['Password'], _ = QtWidgets.QInputDialog.getText(None,'Contrasenya de la base de dades',f"Introduïu la contrasenya de la base de dades {self.dbMaBIM['DatabaseName']}",QtWidgets.QLineEdit.Password)

    @connexio
    def consulta(self, consulta: str, binds: dict = {}, camps: Sequence[int]=None):
        """
        Realitza una consulta a la base de dades

        Arguments:
            consulta {str} -- Consulta SQL que volem executar

        Keyword Arguments:
            binds {dict} -- Arguments que volem lligar a la consulta.
            camps {Sequence[int]} -- Columnes que volem quedar-nos del resultat de la consulta

        """
        res = []
        query=QSqlQuery(self.db)
        query.prepare(consulta)
        for (x,y) in binds.items():
            query.bindValue(x,y)
        query.exec()
        res = []
        while query.next():
            if camps is None:
                camps = range(query.record().count())
            vals = [query.value(i) for i in camps]
            res.append(vals)
        return res

    def OBRE_DB(self):
        if self.dbMaBIM is None:
            self.connectaDB()
        # Si ja està oberta, retornem True. Si no, intentem obrir-la, i retornem el que retorni
        # Lazy evaluation :D
        return self.db.isOpen() or self.db.open()
    def TANCA_DB(self):
        return self.db.close()
    def __del__(self):
        if not self.TANCA_DB() and self.db.isOpen():
            # No s'ha tancat la base de dades :'(
                pass

class Completador(QtWidgets.QCompleter):
    """Completador pel cercador. Gestiona les suggerències quan cerques alguna cosa
       - Filtra en funció de si el contingut conté el string cercat
       - Primer mostra les que contenen algun substring que comenci per la cerca, i després les que contenen la cerca
    """
    def __init__(self):
        super().__init__()
        self.setModel(QtCore.QStringListModel())
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterMode(QtCore.Qt.MatchContains)
    @staticmethod
    def separa(llista, word):
        # Filtra insensible a majúscules i sense espais extres
        word = word.strip().upper()
        def comenca(x):
            x_ = x.strip().upper()
            return x_.startswith(word) or f' {word}' in x_
        def no_comenca(x):
            return not comenca(x)
        return list(filter(comenca,llista)), list(filter(no_comenca,llista))
    def update(self, text):
        # actualitza el contingut del completer en funció del text cercat
        # fa la consulta a la base de dades, i ordena el resultat
        text = text.strip()
        if not text:
            self.model().setStringList([])
            return
        # Força la cerca a majúscules i sense espais
        text_upper = text.upper()
        # Consulta que busca BIMs que contengan, empiecen o sean exactamente el texto
        consulta = '''SELECT BIM, DESCRIPCIO_BIM, DENOMINACIO_BIM
                      FROM ZAFT_0002
                      WHERE ((UPPER(BIM) = :pText)
                             OR (UPPER(BIM) LIKE :pTextPrefix)
                             OR (UPPER(BIM) LIKE :pTextAny)
                             OR (UPPER(BIM) LIKE :pTextAny2)
                             OR (UPPER(DESCRIPCIO_BIM) LIKE :pTextAny)
                             OR (UPPER(DENOMINACIO_BIM) LIKE :pTextAny)
                             OR (UPPER(REF_CADASTRE_BIM) LIKE :pTextAny))
                      AND (ROWNUM < 100)'''
        binds = {
            ':pText': text_upper,
            ':pTextPrefix': text_upper + '%',
            ':pTextAny': '%' + text_upper + '%',
            ':pTextAny2': '%' + text_upper
        }
        self.llista = Consulta().consulta(consulta, binds, (0,1,2))
        self.m_word = text
        res = [' '.join([str(y) for y in x if str(y).upper()!='NULL']) for x in self.llista]
        comencen, contenen = self.separa(res, text)
        self.model().setStringList(comencen+contenen)
        self.complete()
    def splitPath(self,path):
        # funció que en els QCompleter rep el que vols cercar
        #  i retorna una llista de strings per fer el match
        #  en aquest cas aprofitem per actualitzar el model que conté els resultats,
        #  ja que la nostra cerca es basa en una base de dades
        self.update(path)
        return [path]

class QvSeleccioBIM(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat.
    """

    elementsSeleccionats = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, canvas, llegenda, radi=10):
        """[summary]

        Arguments:
            canvas {QgsMapCanvas} -- El canvas de la app
            llegenda {QvLlegenda} -- La llegenda de la app

        Keyword Arguments:
            radi {int} -- [El radi de tolerancia de la seleccio (default: 10)
        """

        super().__init__(canvas)
        self.canvas = canvas
        self.llegenda = llegenda
        self.radi = radi
        self.setCursor(QvConstants.cursorDit())

    # Funció de conveniència per mostrar missatges informatius 
    def missatgeCaixa(self, textTitol, textInformacio):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        msgBox.exec()

    def canvasReleaseEvent(self, event):
        # Llegim posició del mouse
        # Donat que el cursor no selecciona exactament al centre, desplacem un petit offset
        x = event.pos().x()-1
        y = event.pos().y()-8
        try:
            # Per fer la selecció triarem dues cantonades (esquerra-dalt i dreta-baix) d'un rectangle
            #  si tenim una rotació aplicada, caldrà rotar també els punts
            if self.canvas.rotation() == 0:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x - self.radi, y-self.radi)
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x + self.radi, y+self.radi)
            else:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*math.sqrt(2), y+self.radi*math.sqrt(2))
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())

            features = []
            node = self.llegenda.nodePerNom('Inventari municipal')
            if node is not None:
                for nodeLayer in node.findLayers():
                    layer = nodeLayer.layer()
                    if layer.type()==QgsMapLayer.VectorLayer and 'BIM' in layer.fields().names():
                        # la funció getFeatures retorna un iterable. Volem una llista
                        featsAct = [(feat, layer) for feat in layer.getFeatures(QgsFeatureRequest().setFilterRect(rect).setFlags(QgsFeatureRequest.ExactIntersect))]
                        features.extend(featsAct)

            node = self.llegenda.nodePerNom(ConstantsMaBIM.nomGrupRegistrals)
            if node is not None:
                for nodeLayer in node.findLayers():
                    layer = nodeLayer.layer()
                    if layer.type()==QgsMapLayer.VectorLayer and self.llegenda.capaVisible(layer):
                        # la funció getFeatures retorna un iterable. Volem una llista
                        featsAct = [(feat, layer) for feat in layer.getFeatures(QgsFeatureRequest().setFilterRect(rect).setFlags(QgsFeatureRequest.ExactIntersect))]
                        features.extend(featsAct)

            if len(features) > 0:
                    self.elementsSeleccionats.emit(features)
        except Exception as e:
            print(str(e))

class FormulariAtributs(QvFitxesAtributs):
    """Formulari d'atributs del qVista, ampliat per tenir un botó extra de seleccionar
        Per fer-ho, bàsicament a la funció __init__ afegim el botó
    """
    def __init__(self, llegenda, features, *args, **kwargs):
        super().__init__(features[0][1], features, *args, **kwargs)
        self.llegenda = llegenda
        self.layersPerFeats = {x:y for (x,y) in features}
        self.ui.buttonBox.removeButton(self.ui.buttonBox.buttons()[0])
        self.ui.bSeleccionar = self.ui.buttonBox.addButton('Seleccionar', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bSeleccionar.clicked.connect(self.selecciona)
        self.ui.bMostrarPIP = self.ui.buttonBox.addButton('Mostrar PIP', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bMostrarPIP.clicked.connect(self.mostraPIP)

        self.ui.buttonBox.setFixedWidth(300)
        self.ui.bEditar = self.ui.buttonBox.addButton('Editar', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bEditar.clicked.connect(self.edita)
        self.updateBotoEditar()
        for x in (self.ui.bNext, self.ui.bPrev, *self.ui.buttonBox.buttons()):
            x.setStyleSheet('QAbstractButton{font-size: 14px; padding: 2px}')
            x.setFixedSize(100,30)
        self.ui.stackedWidget.adjustSize()
    
    def mostraPIP(self):
        index = self.ui.stackedWidget.currentIndex()
        feature = self.features[index]
        codi = str(feature.attribute('BIM')).replace('0000','')
        #self.parentWidget().leCercador.setText(codi)
        #self.parentWidget().consulta()
        #self.close()
        url = ConstantsMaBIM.urlPIP + f'fitxa/{codi}'
        webbrowser.open_new(url)
        
    def selecciona(self):
        index = self.ui.stackedWidget.currentIndex()
        feature = self.features[index]
        codi = str(feature.attribute('BIM'))
        self.parentWidget().leCercador.setText(codi)
        self.parentWidget().consulta()
        self.close()
    def edita(self):
        index = self.ui.stackedWidget.currentIndex()
        feature = self.features[index]
        self.layersPerFeats[feature].updateFeature(feature)
        form = QvFormAtributs.create(self.layersPerFeats[feature], feature, parent=self, attributes=self.llegenda.atributs)  
        form.exec()
        wid = self.ui.stackedWidget.currentWidget()
        if isinstance(wid, QtWidgets.QScrollArea):
            wid = wid.widget()
        wid.refreshFeature()
        # self.refresh()   
    def updateBotoEditar(self):
        n = self.ui.stackedWidget.currentIndex()
        if hasattr(self, 'layersPerFeats'):
            feature = self.features[n]
            capa = self.layersPerFeats[feature]
            self.ui.bEditar.setVisible(self.llegenda.isLayerEditForm(capa, True))
            self.ui.bSeleccionar.setVisible('BIM' in capa.fields().names())
            # self.formResize(capa)

    def go(self, n):
        super().go(n)
        feat = self.features[n]
        if hasattr(self, 'layersPerFeats'): self.layer = self.layersPerFeats[feat]
        self.updateBotoEditar()
        self.setMenuBar(feat)


class Cercador:
    """Classe de conveniència per encapsular el cercador (lineedits, icona i funcions que fan la cerca)
    """
    MIDALBLCARRER = 400, 40
    MIDALBLNUMERO = 80, 40
    MIDALBLICONA = 20, 20
    def __init__(self, canvas, leCarrer, leNumero, lblIcona):
        super().__init__()
        self.canvas = canvas
        self.marca_geometria = None
        self.leCarrer = leCarrer
        self.leCarrer.setPlaceholderText('Carrer')
        self.leNumero = leNumero
        self.leNumero.setPlaceholderText('Número')
        self.lblIcona = lblIcona
        self.cercador = QCercadorAdreca(self.leCarrer, 'SQLITE', self.leNumero)
        self.marcaLlocGeometria = False

        self.cercador.coordenades_trobades.connect(self.resultatCercador)

    def resultatCercador(self, codi, info):
        if codi == 0:
            self.canvas.setCenter(self.cercador.coordAdreca)
            self.canvas.zoomScale(1000)
            self.canvas.scene().removeItem(self.marca_geometria)

            self.marca_geometria = QgsVertexMarker(self.canvas)
            self.marca_geometria.setCenter( self.cercador.coordAdreca )
            self.marca_geometria.setColor(QtGui.QColor(255, 0, 0))
            self.marca_geometria.setIconSize(15)
            self.marca_geometria.setIconType(QgsVertexMarker.ICON_BOX)
            self.marca_geometria.setPenWidth(3)
            self.marca_geometria.show()
            self.marcaLlocGeometria = True
            self.leCarrer.clear()
            self.leNumero.clear()
    def eliminaMarcaLloc(self):
        if self.marcaLlocGeometria:
            self.canvas.scene().removeItem(self.marca_geometria)
            self.marcaLlocGeometria = False

class FavoritsMaBIM(QvFavorits):
    dadesDB = ConstantsMaBIM.DB_MABIM_PRO

    dadesTaula = {'nomCampInfo':'NOM_MAPA',
                  'nomTaula':'BIMS_FAVORITS',
                  'nomCampId':'IDUSER',
                  'nomCampObs': 'OBSERVACIONS'}
    consultaGet = "select {nomCampInfo},{nomCampObs} from {nomTaula} where {nomCampId}=:IDUSER"
    consultaAfegeix = "insert into {nomTaula} ({nomCampId}, {nomCampInfo}, {nomCampObs}) values (:IDUSER,:NOM_FAVORIT,:OBSERVACIONS)"
    consultaUpdate = "update {nomTaula} set {nomCampObs}=:OBSERVACIONS where {nomCampId}=:IDUSER and {nomCampInfo}=:NOM_FAVORIT"

    def getFavorits(self,usuari=getpass.getuser().upper()):
        '''Comentari explicant'''
        if not self.__CONNECTA_BASE_DADES__(usuari):
            return []
        query=QSqlQuery(self.db)
        consulta = self.consultaGet.format(**self.dadesTaula)
        query.prepare(consulta)
        query.bindValue(':IDUSER',usuari)
        query.exec()
        res=[]
        while query.next():
            res.append((query.value(0), query.value(1)))
        self.__DESCONNECTA_BASE_DADES__(usuari,False)
        return res
    def afegeixFavorit(self,favorit,observacio=None,usuari=getpass.getuser().upper()):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            self.mostra_error(QtWidgets.QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError().text())
            return False
        query=QSqlQuery(self.db)
        query.prepare(self.consultaAfegeix.format(**self.dadesTaula))
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_FAVORIT',favorit)
        query.bindValue(':OBSERVACIONS', observacio)
        executada = query.exec()
        self.__DESCONNECTA_BASE_DADES__(usuari)
        if not executada:
            self.mostra_error(QtWidgets.QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError.text())
        return executada
    def actualitzaObservacio(self,favorit,observacio,usuari=getpass.getuser().upper()):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            self.mostra_error(QtWidgets.QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError().text())
            return False
        query=QSqlQuery(self.db)
        query.prepare(self.consultaUpdate.format(**self.dadesTaula))
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_FAVORIT',favorit)
        query.bindValue(':OBSERVACIONS', observacio)
        executada = query.exec()
        self.__DESCONNECTA_BASE_DADES__(usuari)
        if not executada:
            self.mostra_error(QtWidgets.QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError.text())
        return executada


class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self, projecte, BIM, *args,**kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ConstantsMaBIM.rutaUI,self)

        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPIP)

        self.connectBotons()
        self.connectaCercador()
        self.configuraPlanols()
        self.inicialitzaProjecte(projecte)
        self.connectaDB()
        self.setIcones() 

        self.einaSeleccio = QvSeleccioBIM(self.canvasA, self.llegenda)
        self.einaSeleccio.elementsSeleccionats.connect(self.seleccioGrafica)

        self.wMesuraGrafica = QvMesuraGrafica(self.canvasA, self.llegenda, self.canvasA)
        self.wMesuraGrafica.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.wMesuraGrafica.setWindowTitle('Mesures gràfiques')

        self.setStatusBar(QvStatusBar(self,['progressBar',('coordenades',1), 'escala'],self.canvasA,self.llegenda))
        self.statusBar().afegirWidget('lblSIT',QtWidgets.QLabel("SIT - Sistemes d'Informació Territorial"),0,0)
        self.statusBar().afegirWidget('lblSIT',QtWidgets.QLabel("Direcció de Patrimoni"),0,1)
        self.statusBar().afegirWidget('spacer',QtWidgets.QWidget(),1,2)

        self.wMapesContent.setVisible(False)
        self.tbMapesHeader.setArrowType(QtCore.Qt.RightArrow)
        self.tbMapesHeader.toggled.connect(self.toggle_mapes_panel)

        self.bObrirQGIS.clicked.connect(self.obrirEnQGIS)
        # només podrà veure el botó qui aparegui a la llista d'editors
        # TODO: si no hi ha editors definits, pot veure-ho tothom? Ningú? (comportament actual: ningú)
        # TODO: Cal permetre posar '*' per tothom? Cal permetre posar wildcards? ("DE*", per exemple)
        editors = QgsExpressionContextUtils.projectScope(QgsProject.instance()).variable(ConstantsMaBIM.campEditorsQGIS)
        if editors is not None and QvApp().usuari in editors:
            self.bObrirQGIS.show()
        else:
            self.bObrirQGIS.hide()
        node = self.llegenda.nodePerNom(ConstantsMaBIM.nomGrupRegistrals)

        if node is not None and len(node.findLayers())>0:
            self.cbRegistralsVisibles.show()
        else:
            self.cbRegistralsVisibles.hide()

        #Recuperem layers wms per generar els chec
        self.nodes_wms = self.llegenda.capesPerProveidor('wms')

        layout = self.verticalLayoutMapes

        layout_grup = qtWdg.QVBoxLayout()
        layout_grup.setSpacing(10) 
        grupCapesFons = qtWdg.QButtonGroup(self)
        grupCapesFons.setExclusive(True)

        #iniciem variable per marcar que s'està actualitzant visibilitat de capes de fons
        self._updating_base_layers = False
        self._radio_by_node = {}


        # Radios per node
        for node in self.nodes_wms:
            if node is None:
                continue

            text = node.name()
            text = text if len(text) <= 35 else text[:35] + "..."

            chk = qtWdg.QRadioButton(text, self)
            chk.toggled.connect(partial(self.on_base_layer_toggled, node=node))

            # Guardem la relació node→radio
            self._radio_by_node[node] = chk

            # Un sol callback per canvis al layer tree
            node.visibilityChanged.connect(partial(self.on_node_visibility_changed, node=node))

            grupCapesFons.addButton(chk)
            layout_grup.addWidget(chk)

        # "CAP SELECCIONAT"
        self.chk_none = qtWdg.QRadioButton("Cap", self)
        self.chk_none.toggled.connect(self.on_none_toggled)
        grupCapesFons.addButton(self.chk_none)
        layout_grup.addWidget(self.chk_none)

        # Sincronització inicial
        self._sync_base_layer_radios()

        layout.addLayout(layout_grup)        
        layout.addStretch()

        # Inicialització del panel desplegable de Consultes
        self.wConsultesContent.setVisible(False)
        self.tbConsultesHeader.setArrowType(QtCore.Qt.RightArrow)
        self.tbConsultesHeader.toggled.connect(self.toggle_consultes_panel)
        
        # Cargar configuración de consultas y crear botones dinámicamente
        self._carrega_consultes_config()
        self._crear_botons_consultes()
        
        # NO usar setTabsClosable globalmente - los botones X se agregarán solo donde sea necesario

        self.bAfegirFavorit.clicked.connect(self.dialegSetFavorit)
        self.bAfegirFavorit.clicked.connect(self.mostraFavorits)
        self.bAfegirFavorit.hide()
        self.actualitzaLlistaFavorits()

        self.tFavorits.cellDoubleClicked.connect(self.favoritsCelaDobleClick)
        self.tFavorits.cellChanged.connect(self.observacioEditada)

        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
         
        cons = Consulta()
        txt1 = 'Generació de CSV'
        txt2 = 'Càrrega de CSV'
        txt3 = 'Tall de fulls'

        res1 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt1})[0][0].toString(QtCore.Qt.ISODate)
        res2 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt2})[0][0].toString(QtCore.Qt.ISODate)
        res3 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt3})[0][0].toString(QtCore.Qt.ISODate)

        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(5)


        # Crear botón para mostrar las fechas en una ventana modal
        self.bMostrarFechas = QtWidgets.QPushButton("Mostrar dates de carrega", self)
        self.bMostrarFechas.setFont(font)
        # Ubicar el botón donde estaban los labels (ajusta si es necesario)
        layout = self.l_DataCSV.parentWidget().layout()
        if layout is not None:
            layout.addWidget(self.bMostrarFechas)
        else:
            self.bMostrarFechas.move(self.l_DataCSV.x(), self.l_DataCSV.y())
        self.l_DataCSV.hide()
        self.l_DataCarregaCSV.hide()
        self.l_DataGrafic.hide()
        self.bMostrarFechas.clicked.connect(self.mostrarFechasProcesos)


    def _sync_base_layer_radios(self):
        """Sincronitza l'estat dels QRadioButton amb la visibilitat actual dels nodes."""
        if self._updating_base_layers:
            return

        self._updating_base_layers = True
        try:
            any_visible = False

            # 1) Actualitzar radios de capes
            for node, chk in self._radio_by_node.items():
                visible = node.isVisible()
                any_visible = any_visible or visible

                block = chk.blockSignals(True)
                chk.setChecked(visible)
                chk.blockSignals(block)

            # 2) Actualitzar "CAP SELECCIONAT"
            block = self.chk_none.blockSignals(True)
            self.chk_none.setChecked(not any_visible)
            self.chk_none.blockSignals(block)

        finally:
            self._updating_base_layers = False

    def on_base_layer_toggled(self, checked, node):
        if not checked or self._updating_base_layers:
            return

        self._apply_exclusive_base_layer(node)
        self._sync_base_layer_radios()
        
    def on_none_toggled(self, checked):
        if not checked or self._updating_base_layers:
            return

        self._apply_exclusive_base_layer(None)
        self._sync_base_layer_radios()

    def _apply_exclusive_base_layer(self, selected_node):
        """
        Si selected_node és None → apaga totes.
        Si selected_node és un node → deixa només aquest visible.
        """
        if self._updating_base_layers:
            return

        self._updating_base_layers = True
        try:
            for node in self._radio_by_node.keys():
                node.setItemVisibilityChecked(node is selected_node)
        finally:
            self._updating_base_layers = False

    def on_node_visibility_changed(self, state, node):
        if self._updating_base_layers:
            return

        # Si algú ha encès una capa manualment, imposar exclusivitat
        if node.isVisible():
            self._apply_exclusive_base_layer(node)

        self._sync_base_layer_radios()

    def mostrarFechasProcesos(self):
        # Recuperar los textos de las fechas
        cons = Consulta()
        txt1 = 'Generació de CSV'
        txt2 = 'Càrrega de CSV'
        txt3 = 'Tall de fulls'
        try:
            res1 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt1})[0][0].toString(QtCore.Qt.ISODate)
            res2 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt2})[0][0].toString(QtCore.Qt.ISODate)
            res3 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt3})[0][0].toString(QtCore.Qt.ISODate)
        except Exception:
            res1 = res2 = res3 = "-"
        msg = (
            f"Generació de CSV: {self.replace(res1, 'T', ' - ')}\n"
            f"Càrrega de CSV: {self.replace(res2, 'T', ' - ')}\n"
            f"Tall de fulls: {self.replace(res3, 'T', ' - ')}"
        )
        QtWidgets.QMessageBox.information(self, "Dates de processos", msg)

        self.swapVisibilitatBaixes(self.cbBaixesVisibles.isChecked())


    # function to convert qdatetime to text
    def mostraMesures(self):
        self.wMesuraGrafica.show()

    # function to replace a string in a string
    def replace(self, text, buscar, reempla):
        return reempla.join(text.split(buscar))

    def dialegSetFavorit(self):
        if self.bAfegirFavorit.isChecked():
            text, ok = QtWidgets.QInputDialog.getText(self, 'Afegir amb a favorit', "Observacions", flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
            if ok:
                self.setFavorit(observacio=text)
        else:
            self.setFavorit()
    def actualitzaLlistaFavorits(self):
        favorits = [(str(x),y) for (x,y) in FavoritsMaBIM().getFavorits()]

        self.favObs = dict(favorits)
        self.favorits = set(self.favObs.keys())
        pass

    def setFavorit(self, BIM=None, fav=None, observacio=''):
        if BIM is None:
            if not hasattr(self,'dadesLabelsDades'):
                return
            BIM = self.dadesLabelsDades[0]
        if fav is None:
            fav = not BIM in self.favorits
        if fav:
            FavoritsMaBIM().afegeixFavorit(BIM, observacio)
        else:
            FavoritsMaBIM().eliminaFavorit(BIM)
        self.actualitzaLlistaFavorits()
        self.actualitzaBotoFavorit()
    

    def actualitzaBotoFavorit(self):
        if hasattr(self,'dadesLabelsDades'):
            self.bAfegirFavorit.setChecked(self.dadesLabelsDades[0].replace('0000','') in self.favorits)

    def obrirEnQGIS(self):
        # L'executable de Python acostuma a estar a la ruta [DIR]/OSGeo4W{64,}/apps/Python[NUM]/python.exe
        # A partir d'ell podem trobar la carpeta d'instal·lació de OSGeo4W
        executablePython = sys.executable
        rutaOSGEO = str(Path(executablePython).parent.parent.parent)

        # Per si de cas falla, posem alguna ruta extra on buscar
        rutesInstalacio = (rutaOSGEO, 'C:/OSGeo4W', 'C:/OSGeo4W64', 'D:/OSGeo4W', 'D:/OSGeo4W64')

        possiblesRutes = (f'{x}/bin' for x in rutesInstalacio if os.path.isdir(x))

        for ruta in possiblesRutes:
            executables = [rutaExe for rutaExe in (f'{ruta}/{nomExe}' for nomExe in ('qgis-ltr.bat','qgis.bat')) if os.path.isfile(rutaExe)]
            if len(executables)!=0:
                extensio = self.canvasA.extent()
                cmd = executables[0], '--project', ConstantsMaBIM.rutaProjecteEdicio, '--extent', f'{extensio.xMinimum()},{extensio.yMinimum()},{extensio.xMaximum()},{extensio.yMaximum()}'
                p = subprocess.Popen(cmd, env=os.environ, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                return

        # Si arribem aquí, ens queixem
    def showEvent(self, e):
        super().showEvent(e)
        self.tabCentral.setCurrentIndex(2)

    def seleccioGrafica(self, feats):
        form = FormulariAtributs(self.llegenda, feats, self)
        form.move(self.width()-form.width(),(self.height()-form.height())//2)
        form.exec()
        self.canvasA.bPanning.click()

    def setIcones(self):
        self.setIconesBotons()
        # Qt com a tal no permet fer  una label amb imatge i text. HTML sí que ho permet
        # Ja que les labels permeten tenir com a contingut un HTML,
        # doncs posem un mini HTML amb la imatge i el text
        self.lblLogoMaBIM.setFixedSize(275,60)
        self.lblLogoMaBIM.setText(f"""<html><img src=imatges/MaBIM/MaBIM-text.png height={self.lblLogoMaBIM.height()}><span style="font-size:18pt; color:#ffffff;"></span></html>""")
        self.lblLogoAjuntament.setFixedHeight(82)
        self.lblLogoAjuntament.setPixmap(QtGui.QPixmap(ConstantsMaBIM.rutaLogoAjuntament).scaledToHeight(82))

    def setIconesBotons(self):
        # afegir les icones des del designer donava problemes
        # per tant, les afegim aquí i té un comportament més consistent
        parelles = (
            (self.bFavorits, 'botonera-fav.png'),
            (self.bBIMs, 'botonera-BIM.png'),
            (self.bPIP, 'botonera-PIP.png'),
            #(self.bProjectes, 'botonera-projectes'),
            (self.tbConsultesHeader, 'botonera-consultes')
        )
        for (boto, icona) in parelles:
            boto.setIcon(QtGui.QIcon(f'Imatges/MaBIM/{icona}'))

    def connectaDB(self):
        pass
    def connectaCercador(self):
        completer = Completador()
        self.leCercador.setCompleter(completer)
        completer.activated.connect(self.consulta)
        popup = completer.popup()
        popup.setFixedWidth(800)          # ancho fijo en píxeles
        # o: popup.setMinimumWidth(self.leCercador.width() + 150)
    def consulta(self):
        # funció que fa les consultes a la Base de Dades, per omplir els diferents camps i taules

        # Donat que el primer camp del Line Edit és el BIM, l'utiltizarem per fer la consulta definitiva
        txt = self.leCercador.text().split(' ')[0]
        cons = Consulta()
        try:
            self.dadesLabelsDades = cons.consulta(ConstantsMaBIM.CONSULTA_INFO_BIM_Z2,{':pText':txt})[0]
            self.dadesTaula = cons.consulta(ConstantsMaBIM.CONSULTA_INFO_BIM_Z3,{':pText':txt})
            self.dadesTitularitat = cons.consulta(ConstantsMaBIM.CONSULTA_INFO_BIM_Z13, {':pText':txt})[0]
            self.dadesFinquesRegistrals = cons.consulta(ConstantsMaBIM.CONSULTA_INFO_BIM_Z11, {':pText':txt})
        except IndexError:
            # la consulta no funciona :(
            return
        self.recarregaLabelsDades()


    def recarregaLabelsDades(self):
        # un cop hem obtingut la nova informació, recarreguem la informació de les labels i taules

        # Eliminem la marca del cercador
        self.cerca1.eliminaMarcaLloc()
        # No modificar el código BIM original, para que el filtro funcione con cualquier prefijo
        # self.dadesLabelsDades[0] = self.dadesLabelsDades[0].replace('0000', ' ').lstrip()

        self.bAfegirFavorit.hide()
        self.bAfegirFavorit.setChecked(self.dadesLabelsDades[0] in self.favorits)
        # Labels pestanya "Dades Identificatives"
        labels = (self.lNumBIM, self.lSituacio,self.ltipusSituacio,self.lDescripcioBIM,self.lDenominacio,
                  self.lTipologia,self.lSubtipologia,self.lGrup,self.lSubgrup,self.lTipusImmoble,
                  self.lQualJurd,self.lQualUrb,self.lSupTotalGestio, self.lSupCadSol,
                  self.lSupCadCons,self.lSupRegSol, self.lSupRegCons,
                  self.lRefCad,self.lNumImmCad, self.lEstatCad)

        # totes les labels tindran la mateixa font. Per tant, agafem la d'una qualsevol
        font = self.lNumBIM.font()
        for (lbl,txt) in zip(labels, self.dadesLabelsDades):
            if type(txt)!=str:
                    txt = str(txt)

            if txt.upper()!='NULL':
                lbl.setText(txt)

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')
        
        # Taula pestanya "Dades Identificatives"
        self.twDadesBIM.setRowCount(len(self.dadesTaula))
        for (i,x) in enumerate(self.dadesTaula):
            for (j,elem) in enumerate(x):
                if type(elem)!=str:
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twDadesBIM.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        self.twDadesBIM.resizeColumnsToContents()

        # Labels pestanya "Titularitat i Registral"
        labels = (self.lNumBIM2, self.lSituacio2, self.ltipusSituacio2, self.lDescripcioBIM2,self.lDenominacio2)
        for (lbl,txt) in zip(labels, self.dadesLabelsDades):
            if str(txt).upper()!='NULL':
                lbl.setText(str(txt))

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')
        
 
        labels = (self.lPropietariSol, self.lPropietariCons, self.lDataAdqBim, self.lTitolAdq,
                  self.lPercEstatProp, self.lEstatInsc,self.lDataInsc, self.lInscritCartoMun,self.lDataCoordCart )


        for (lbl,txt) in zip(labels, self.dadesTitularitat):
            if str(txt).upper()!='NULL':
                lbl.setText(str(txt))

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')


        self.twFinquesRegistrals.setRowCount(len(self.dadesFinquesRegistrals))
        for (i,x) in enumerate(self.dadesFinquesRegistrals):
            for (j, elem) in enumerate(x):
                if not isinstance(x, str):
                    elem = str(elem)
                    if elem=='NULL': elem=''
                self.twFinquesRegistrals.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
        #self.twFinquesRegistrals.resizeColumnsToContents()

        #Posem mes espai a Descric
        self.twFinquesRegistrals.setColumnWidth(3, 450)
        self.twFinquesRegistrals.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        #header = self.twFinquesRegistrals.horizontalHeader()
        #header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Ara el filtre busca el BIM permetent zeros a l'esquerra (o qualsevol prefix)
        cerca = f"BIM LIKE '%{self.dadesLabelsDades[0]}'"

        layers = self.getCapesBIMs()
        for layer in layers:
            layer.setSubsetString(cerca)
        # Buscar la primera capa amb features tras aplicar el filtre
        layer_con_features = next((l for l in layers if l.featureCount() > 0), None)
        if layer_con_features is None:
            self.netejaFiltre()
            QtWidgets.QMessageBox.warning(self,"Atenció!", "No s'ha pogut localitzar el BIM en el mapa. Comproveu que la capa corresponent sigui visible")
        else:
            self.canvasA.setExtent(layer_con_features.extent())

        # Si intentes eliminar el contingut d'un QLineEdit que té un QCompleter associat,
        #  el propi QCompleter torna a completar el QLineEdit, provocant que no es pugui netejar
        # Fent servir un QTimer es pot saltar això
        # https://stackoverflow.com/a/49032473
        QtCore.QTimer.singleShot(0, self.leCercador.clear)

    def netejaFiltre(self):
        layers = self.getCapesBIMs()
        for layer in layers:
            layer.setSubsetString('')
        self.bAfegirFavorit.hide()
    def _llegir_bims_des_de_csv(self, path: str) -> list:
        """
        Lee BIMs desde un CSV.
        - Si hay cabecera y existe columna BIM/CODI_BIM, usa esa.
        - Si no, usa la primera columna.
        Acepta separadores típicos (, ; \t |).
        """
        import csv

        bims = []
        if not path or not os.path.exists(path):
            return bims

        with open(path, 'r', encoding='utf-8-sig', newline='') as f:
            sample = f.read(4096)
            f.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t,")
            except Exception:
                dialect = csv.excel
                dialect.delimiter = ';' if ';' in sample else ','

            reader = csv.reader(f, dialect)
            rows = list(reader)

        if not rows:
            return bims

        header = [str(x).strip().upper() for x in rows[0]]
        col_idx = None
        for candidate in ("BIM", "CODI_BIM", "CODI", "CODIGO_BIM", "CODIGO"):
            if candidate in header:
                col_idx = header.index(candidate)
                break

        start_row = 1 if col_idx is not None else 0
        if col_idx is None:
            col_idx = 0

        for r in rows[start_row:]:
            if not r or col_idx >= len(r):
                continue
            val = str(r[col_idx]).strip()
            if not val:
                continue
            val = val.strip().strip('"').strip("'").upper()
            val = " ".join(val.split())
            bims.append(val)

        seen = set()
        out = []
        for x in bims:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out


    def filtraPVPH_desdeCSV(self):
        """
        Botón de consulta:
        - Seleccionas CSV con BIMs
        - Filtra SOLO 'Entitats en PV' y 'Entitats en PH'
        """
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Selecciona CSV con códigos BIM",
            "",
            "CSV (*.csv *.txt);;Todos (*.*)"
        )
        if not path:
            return

        bims = self._llegir_bims_des_de_csv(path)
        if not bims:
            QtWidgets.QMessageBox.warning(self, "Atención", "No se han encontrado BIMs en el CSV.")
            return

        parts = []
        for bim in bims:
            bim_esc = bim.replace("'", "''")
            parts.append(f"BIM LIKE '%{bim_esc}'")
        where = " OR ".join(parts)

        capas_objetivo = [ConstantsMaBIM.nomCapaPV, ConstantsMaBIM.nomCapaPH]
        layers_filtradas = []
        for nom in capas_objetivo:
            layer = self.llegenda.capaPerNom(nom)
            if layer is None:
                for lyr in QgsProject.instance().mapLayers().values():
                    if lyr.name() == nom:
                        layer = lyr
                        break

            if layer is not None and layer.type() == QgsMapLayer.VectorLayer and 'BIM' in layer.fields().names():
                layer.setSubsetString(where)
                layers_filtradas.append(layer)

        if not layers_filtradas:
            QtWidgets.QMessageBox.warning(
                self, "Atención",
                "No se han encontrado las capas 'Entitats en PV' / 'Entitats en PH' (o no tienen campo BIM)."
            )
            return

        layer_con_features = next((l for l in layers_filtradas if l.featureCount() > 0), None)
        if layer_con_features is None:
            QtWidgets.QMessageBox.information(
                self, "Filtrado aplicado",
                "Se ha aplicado el filtro, pero no hay resultados visibles en PV/PH con esos BIMs."
            )
            return

        extent = None
        for l in layers_filtradas:
            if l.featureCount() <= 0:
                continue
            if extent is None:
                extent = l.extent()
            else:
                extent.combineExtentWith(l.extent())

        if extent is not None and extent.isFinite():
            self.canvasA.setExtent(extent)
            self.canvasA.refresh()

        QtWidgets.QMessageBox.information(
            self, "Filtrado aplicado",
            f"Filtrado aplicado desde CSV:\n{os.path.basename(path)}\n\nBIMs: {len(bims)}"
        )
    @QvFuncions.cronometraDebug
    def configuraPlanols(self):
        root = QgsProject.instance().layerTreeRoot()
        planolA = self.tabCentral.widget(2)

        mapetaPng = "mapesOffline/default.png"
        botons = ['panning', 'streetview', 'zoomIn', 'zoomOut', 'centrar']

        # instanciem el canvas que representarà el Plànol de l'Ajuntament
        self.canvasA = QvCanvas(planolA, posicioBotonera='SE', llistaBotons=botons)
        QgsLayerTreeMapCanvasBridge(root, self.canvasA)
        planolA.layout().addWidget(self.canvasA)
        self.canvasA.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:25831'))
        self.canvasA.mostraStreetView.connect(self.canvasA.getStreetView().show)

        self.atributs = QvAtributs(self.canvasA)
        self.atributs.setWindowTitle("Taules d'atributs")
        self.llegenda = QvLlegenda(self.canvasA, self.atributs)
        self.canvasA.setLlegenda(self.llegenda)
        self.llegenda.resize(500, 600)

        self.canvasA.bCentrar.disconnect()
        self.canvasA.bCentrar.clicked.connect(self.centrarMapa)

        # instanciem el mapeta
        self.mapetaA = QvMapetaBrujulado(mapetaPng, self.canvasA, pare=self.canvasA)
        self.mapetaA.setGraphicsEffect(QvConstants.ombra(self,radius=10,color=QvConstants.COLOROMBRA))
        # Copiem la part que ens interessa del stylesheet del qVista
        self.mapetaA.setStyleSheet('''QMenu{background-color: #DDDDDD;color: #38474F;}QMenu::item:selected{background-color: #FF6215;color: #F9F9F9;}''')

        self.cerca1 = Cercador(self.canvasA, self.leCarrer, self.leNumero, self.lblIcona)
        self.cerca1.cercador.coordenades_trobades.connect(lambda: self.tabCentral.setCurrentIndex(2))

        botoSelecciona = self.canvasA.afegirBotoCustom('botoSelecciona', 'imatges/apuntar.png', 'Selecciona BIM gràficament', 1)
        def setEinaSeleccionar():
            self.canvasA.setMapTool(self.einaSeleccio)
            botoSelecciona.setChecked(True)
        botoSelecciona.clicked.connect(setEinaSeleccionar)
        botoSelecciona.setCheckable(True)
        botoNeteja = self.canvasA.afegirBotoCustom('botoNeteja', 'imatges/MaBIM/canvas_neteja_filtre.png', 'Mostra tots els BIMs', 2)
        botoNeteja.clicked.connect(self.netejaFiltre)
        botoNeteja.setCheckable(False)
        botoLlegenda = self.canvasA.afegirBotoCustom('botoLlegenda', 'imatges/map-legend.png', 'Mostrar/ocultar llegenda', 3)
        botoLlegenda.clicked.connect(lambda: self.llegenda.setVisible(not self.llegenda.isVisible()))
        botoLlegenda.setCheckable(False)
        botoMapeta = self.canvasA.afegirBotoCustom('botoMapeta', 'imatges/mapeta.png', 'Mostrar/ocultar mapa de situació',4)
        botoMapeta.clicked.connect(lambda: self.mapetaA.setVisible(not self.mapetaA.isVisible()))
        botoMapeta.setCheckable(False)
        botoCaptura = self.canvasA.afegirBotoCustom('botoCaptura','imatges/content-copy.png','Copiar una captura del mapa al portarretalls')
        botoCaptura.clicked.connect(self.canvasA.copyToClipboard)
        botoCaptura.setCheckable(False)
        botoMesures = self.canvasA.afegirBotoCustom('botoMesura', 'imatges/regle.png', 'Mesures gràfiques sobre el mapa')
        botoMesures.clicked.connect(self.mostraMesures)
        botoMesures.setCheckable(False)

        # Donem estil als canvas
        estilCanvas = '''
            QvPushButton {
                background-color: #F9F9F9 transparent;
                color: #38474F;
                margin: 0px;
                border: 0px;
            }

            QvPushButton:checked{
                background-color: #DDDDDD;
                color: #38474F;
                border: 2px solid #FF6215;
                padding: 2px 2px;
            }'''
        self.canvasA.setStyleSheet(estilCanvas)




        self.tabCentral.currentChanged.connect(self.canviaTab)

    def centrarMapa(self):
        self.canvasA.setExtent(ConstantsMaBIM.rangBarcelona)
        self.canvasA.refresh()
        self.canvasA.bCentrar.setChecked(False)

    def _centrar_despres_refresc(self):
        # Ens desconnectem per no repetir
        self.canvasA.mapCanvasRefreshed.disconnect(self._centrar_despres_refresc)
        self.centrarMapa()

    @QvFuncions.cronometraDebug
    def inicialitzaProjecte(self, projecte):
        # # L'opertura de projectes Oracle va lenta si és la primera
        # # Obrim un arxiu "inútil", i així s'obren més ràpid
        # if self.llegenda.project.homePath()=='':
        #     try:
        #         self.llegenda.read('mapesOffline/accelerator.qgs')
        #     except:
        #         pass
        self.llegenda.readProject(projecte)
        self.canvasA.mapCanvasRefreshed.connect(self._centrar_despres_refresc)
        self.centrarMapa()

        # cal comprovar si les capes ... i ... són visibles
        def nodeConteBaixa(node):
            nomNode = node.data(QtCore.Qt.DisplayRole).lower()
            return 'baixa' in nomNode or 'baixes' in nomNode
        model = self.llegenda.model
        capes = (self.llegenda.capaPerNom(nomCapa) for nomCapa in ConstantsMaBIM.nomsCapes)
        nodesCapes = (QgsProject.instance().layerTreeRoot().findLayer(capa.id()) for capa in capes if capa is not None)
        self.nodesBaixes = [node for nodeCapa in nodesCapes for node in model.layerLegendNodes(nodeCapa) if nodeConteBaixa(node)]


        QgsProject.instance().layerTreeRoot().visibilityChanged.connect(self.canviVisibilitatLlegenda)
        for x in self.nodesBaixes:
            x.dataChanged.connect(lambda: self.canviVisibilitatLlegenda(x))

        self.nodeSeccionsRegistrals = self.llegenda.nodePerNom('SECCIONS_REGISTRALS')
        self.nodeGrupRegistrals = self.llegenda.nodePerNom(ConstantsMaBIM.nomGrupRegistrals)
        if self.nodeGrupRegistrals is not None:
            self.nodesRegistrals = self.nodeGrupRegistrals.findLayers()
        else:
            self.nodeRegistrals = None

        self.cbBaixesVisibles.setChecked(False)  # Inicialmente en off
        self.cbBaixesVisibles.clicked.connect(self.swapVisibilitatBaixes)
        self.cbAltresBens.setChecked(False)  # Inicialmente en off
        self.cbAltresBens.clicked.connect(self.swapVisibilitatAltresBens)
        self.cbRegistresPropietat.clicked.connect(self.swapVisibilitatRegistre)
        self.cbRegistralsVisibles.clicked.connect(self.swapVisibilitatRegistrals)
        self.swapVisibilitatBaixes(False)  # Asegura que las capas de baixes estén ocultas al inicio
        self.swapVisibilitatRegistrals(False)

    def canviVisibilitatLlegenda(self,node):
        if node in self.nodesBaixes:
            visibles = [x.data(QtCore.Qt.CheckStateRole)==QtCore.Qt.Checked for x in self.nodesBaixes]
            if all(visibles):
                self.cbBaixesVisibles.setTristate(False)
                self.cbBaixesVisibles.setCheckState(QtCore.Qt.Checked)
                self.cbBaixesVisibles.setChecked(True)
            elif any(visibles):
                self.cbBaixesVisibles.setTristate(True)
                self.cbBaixesVisibles.setCheckState(QtCore.Qt.PartiallyChecked)
            else:
                self.cbBaixesVisibles.setTristate(False)
                self.cbBaixesVisibles.setChecked(False)
        elif node==self.nodeSeccionsRegistrals:
            self.cbRegistresPropietat.setChecked(node.isVisible())
        elif node==self.nodeGrupRegistrals:
            self.cbRegistralsVisibles.setChecked(node.isVisible())

    def swapVisibilitatBaixes(self,check):
        self.cbBaixesVisibles.setTristate(False)
        if check:
            for x in self.nodesBaixes:
                x.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        else:
            for x in self.nodesBaixes:
                x.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)

    def swapVisibilitatRegistre(self,check):
        capa = self.llegenda.capaPerNom('SECCIONS_REGISTRALS')
        self.llegenda.setLayerVisible(capa, check)
    def swapVisibilitatRegistrals(self, check):
        node = self.llegenda.nodePerNom(ConstantsMaBIM.nomGrupRegistrals)
        if node is not None:
            node.setItemVisibilityChecked(check)
            # for nodeLayer in node.findLayers():
            #     capa = nodeLayer.layer()
            #     self.llegenda.setLayerVisible(capa, check)

    def swapVisibilitatAltresBens(self, check):
        """Activa o desactiva la capa 'Altres Béns i Drets' en la llegenda."""
        try:
            capa = self.llegenda.capaPerNom(ConstantsMaBIM.nomCapaQuioscos)
            if capa is not None:
                self.llegenda.setLayerVisible(capa, check)
            else:
                # intentar localizar por nodo si existe
                node = self.llegenda.nodePerNom(ConstantsMaBIM.nomCapaQuioscos)
                if node is not None:
                    node.setItemVisibilityChecked(check)
        except Exception:
            pass

    def getCapaBIMs(self):
        # Retorna una capa amb camp de BIMs
        #  nota: millor evitar-la, això només per quan ens veiem forçats a passar una única capa
        # return self.llegenda.capaPerNom('Entitats en PV')
        return self.getCapesBIMs()[0]

    def getCapesBIMs(self):
        layers = []
        for capa in self.llegenda.capes():
            if capa.type() == QgsMapLayer.VectorLayer:
                if 'BIM' in capa.fields().names():
                    layers.append(capa)
        return layers



    def canviaTab(self):
        # abans s'utilitzava per mostrar i ocultar la llegenda
        # queda la funció buida per si en algun moment cal fer alguna cosa en canviar de pestanya
        return

    def selecciona(self, BIM):
        self.leCercador.setText(BIM)
        self.consulta()
        self.actualitzaLlistaFavorits()
        self.bAfegirFavorit.setChecked(BIM in self.favorits)
        self.bBIMs.click()

    def actualitzaFav(self,fila, columna):
        BIM = self.tFavorits.item(fila,0).text()
        observacio = self.tFavorits.item(fila,5).text()
        self.setFavorit(BIM, not BIM in self.favorits, observacio)


    def mostraFavorits(self):
        self.actualitzaLlistaFavorits()
        self.tFavorits.blockSignals(True)
        self.tFavorits.setRowCount(len(self.favorits))
        for (i,x) in enumerate(self.favorits):
            info = Consulta().consulta(ConstantsMaBIM.CONSULTA_CERCADOR,{':pText':x},(0,1,2))
            if len(info)==0 or len(info[0])==0: continue
            info[0][0]=info[0][0].replace('0000','')
            for (j, elem) in enumerate(info[0]):
                if elem is not None and not isinstance(elem, QtCore.QVariant):
                    self.tFavorits.setItem(i,j,QtWidgets.QTableWidgetItem(elem))
                else:
                    self.tFavorits.setItem(i,j,QtWidgets.QTableWidgetItem(''))
                self.tFavorits.item(i,j).setFlags(self.tFavorits.item(i,j).flags()&~QtCore.Qt.ItemIsEditable)
            bSelecciona = QtWidgets.QPushButton('Seleccionar')
            # Equivaldria a:
            #  bSelecciona.clicked.connect(lambda: self.selecciona(BIM))
            # No obstant, quan fas connects així dins d'un for a vegades fa coses inesperades
            # EXEMPLE DE L'ERROR:
            #  aux = [lambda x: x*i for i in range(10)]
            #  for func in aux: print(func(2))
            #  Esperaríem que ens mostrés 0, 2, 4, 6, 8,...,18. No obstant, ens imprimeix 18, 18, 18...
            # functools.partial evita aquest tipus d'errors
            BIM = info[0][0]
            bSelecciona.clicked.connect(functools.partial(self.selecciona, BIM))
            bSelecciona.setCursor(QvConstants.cursorClick())
            self.tFavorits.setCellWidget(i,3,bSelecciona)
            cbDesmarcaFav = QtWidgets.QCheckBox('Favorit')
            cbDesmarcaFav.setChecked(True)
            cbDesmarcaFav.clicked.connect(functools.partial(self.actualitzaFav,i,4))
            self.tFavorits.setCellWidget(i,4,cbDesmarcaFav)
            observacio = self.favObs[BIM]
            self.tFavorits.setItem(i,5,QtWidgets.QTableWidgetItem(observacio if isinstance(observacio,str) else ''))
        self.tFavorits.resizeColumnsToContents()
        self.tFavorits.blockSignals(False)

    def favoritsCelaDobleClick(self, fila, columna):
        if columna==5:
            pass
        else:
            BIM = self.tFavorits.item(fila, 0).text()
            self.selecciona(BIM)
            self.actualitzaBotoFavorit()
    def observacioEditada(self,fila,columna):
        if columna==5:
            BIM = self.tFavorits.item(fila,0).text()
            if BIM in self.favorits:
                FavoritsMaBIM().actualitzaObservacio(BIM, self.tFavorits.item(fila,5).text())
    
    def toggle_mapes_panel(self, checked):
        # Mostra o amaga el contingut
        self.wMapesContent.setVisible(checked)

        # Canvia la fletxa per donar feedback visual
        if checked:
            self.tbMapesHeader.setArrowType(QtCore.Qt.DownArrow)
        else:
            self.tbMapesHeader.setArrowType(QtCore.Qt.RightArrow)

    def toggle_consultes_panel(self, checked):
        # Mostra o amaga el contingut
        self.wConsultesContent.setVisible(checked)

        # Canvia la fletxa per donar feedback visual
        if checked:
            self.tbConsultesHeader.setArrowType(QtCore.Qt.DownArrow)
        else:
            self.tbConsultesHeader.setArrowType(QtCore.Qt.RightArrow)

    def _carrega_consultes_config(self):
        """Carga la configuración de consultas desde el archivo JSON"""
        try:
            ruta_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'consultes_config.json')
            if os.path.exists(ruta_config):
                with open(ruta_config, 'r', encoding='utf-8') as f:
                    self.consultes_config = json.load(f)
            else:
                print(f"Archivo de configuración no encontrado: {ruta_config}")
                self.consultes_config = {'consultas': []}
        except Exception as e:
            print(f"Error al cargar configuración de consultas: {e}")
            self.consultes_config = {'consultas': []}

    def _crear_botons_consultes(self):
        """Crea dinámicamente los botones de consultas basados en la configuración"""
        for consulta in self.consultes_config.get('consultas', []):
            texto = consulta.get('texto', consulta.get('id', 'Consulta'))
            funcion_nombre = consulta.get('funcion')
            archivo_qlr = consulta.get('archivo_qlr')

            boto = QtWidgets.QPushButton(texto, self)
            boto.consulta_config = consulta

            # 1) Si define "funcion", ejecuta método del QMaBIM
            if funcion_nombre and hasattr(self, funcion_nombre):
                fn = getattr(self, funcion_nombre)
                boto.clicked.connect(lambda checked=False, fn=fn: fn())

            # 2) Si define "archivo_qlr", usa el flujo actual
            elif archivo_qlr:
                boto.clicked.connect(lambda checked=False, config=consulta: self._ejecutar_consulta(config))

            else:
                # Config inválida
                boto.clicked.connect(lambda: QtWidgets.QMessageBox.warning(
                    self, "Error", "Consulta sin 'funcion' ni 'archivo_qlr' en consultes_config.json"
                ))

            self.verticalLayoutConsultes.addWidget(boto)

        self.verticalLayoutConsultes.addStretch()
    def _ejecutar_consulta(self, config_consulta):
        """Ejecuta una consulta basada en su configuración usando QvTaulaAtributs"""
        try:
            archivo_qlr = config_consulta.get('archivo_qlr')
            nombre_consulta = config_consulta.get('nombre')
            
            if not archivo_qlr:
                QtWidgets.QMessageBox.warning(self, "Error", "La configuración de consulta no especifica un archivo QLR")
                return
            
            # Obtener la ruta del archivo QLR
            ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
            ruta_qlr = os.path.join(ruta_carpeta, archivo_qlr)
            
            # Verificar que el fichero existe
            if not os.path.exists(ruta_qlr):
                QtWidgets.QMessageBox.warning(self, "Error", f"No s'ha trobat el fitxer: {ruta_qlr}")
                return
            
            # Primero verificar si la pestaña ya existe
            pestanya_nom = nombre_consulta
            index_pestanya_existente = -1
            for i in range(self.tabCentral.count()):
                if self.tabCentral.tabText(i) == pestanya_nom:
                    index_pestanya_existente = i
                    break
            
            # Si la pestaña ya existe, simplemente mostrarla
            if index_pestanya_existente >= 0:
                self.tabCentral.setCurrentIndex(index_pestanya_existente)
                return
            
            # Si no existe la pestaña, cargar la capa
            project = QgsProject.instance()
            
            # Obtenir les capes actuals
            capes_antes = set(project.mapLayers().keys())
            
            # Verificar si la capa ya existe por nombre
            capa = None
            for layer in project.mapLayers().values():
                if layer.name() == nombre_consulta:
                    capa = layer
                    break
            
            # Si no existe, cargar desde el archivo QLR
            if capa is None:
                # Caregar usando QgsLayerDefinition
                root = project.layerTreeRoot()
                success = QgsLayerDefinition.loadLayerDefinition(ruta_qlr, project, root)
                
                if not success:
                    QtWidgets.QMessageBox.warning(self, "Error", "No s'ha pogut cargar el fitxer QLR")
                    return
                
                # Obtenir la capa nova (la diferencia)
                capes_despues = set(project.mapLayers().keys())
                capes_nuevas = capes_despues - capes_antes
                
                if not capes_nuevas:
                    QtWidgets.QMessageBox.warning(self, "Error", "No s'ha carregat cap capa nova")
                    return
                
                # Obtenir la primera capa nova
                capa_id = list(capes_nuevas)[0]
                capa = project.mapLayers()[capa_id]
            
            # Crear tabla de atributos usando QvTaulaAtributs
            taula = QvTaulaAtributs(parent=self, layer=capa, canvas=self.canvasA, readOnly=True)
            
            # Crear widget contenedor
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Crear layout horizontal para el botón
            btn_layout = QtWidgets.QHBoxLayout()
            btn_layout.setContentsMargins(5, 5, 5, 5)
            
            # Crear botón para exportar a CSV
            btn_export_csv = QtWidgets.QPushButton("Exportar a CSV")
            btn_export_csv.setIcon(QIcon("imatges/file-delimited.png"))
            btn_export_csv.setMaximumHeight(32)
            btn_export_csv.setMaximumWidth(150)
            btn_export_csv.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn_export_csv.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: 1px solid #0078D4;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1084D8;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
            """)
            btn_export_csv.clicked.connect(taula.saveToCSV)
            
            # Agregar botón al layout horizontal (izquierda)
            btn_layout.addWidget(btn_export_csv)
            btn_layout.addStretch()
            
            # Agregar layout del botón y tabla al layout principal
            layout.addLayout(btn_layout)
            layout.addWidget(taula)
            
            # Crear la nova pestanya
            num_features = capa.featureCount()
            self.tabCentral.addTab(widget, pestanya_nom)
            new_index = self.tabCentral.count() - 1
            self.tabCentral.setCurrentWidget(widget)
            # Agregar botón de cierre solo a esta pestaña
            self._agregar_boto_tancament(new_index)
            
            # Mostrar mensaje de confirmación
            QtWidgets.QMessageBox.information(self, nombre_consulta, f"Dades carregades: {num_features} registres")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error al executar consulta: {str(e)}")

    def _agregar_boto_tancament(self, index_pestanya):
        """Agrega un botón de cierre personalizado a una pestaña específica"""
        # Crear botón de cierre
        btn_tanca = QToolButton()
        btn_tanca.setText('✕')
        btn_tanca.setStyleSheet('QToolButton { border: none; padding: 0px; background: transparent; }')
        btn_tanca.setFixedSize(16, 16)
        btn_tanca.clicked.connect(lambda: self.tancaPestanya(index_pestanya))
        
        # Agregar el botón al tab bar
        self.tabCentral.tabBar().setTabButton(index_pestanya, QtWidgets.QTabBar.RightSide, btn_tanca)

    def executarConsulta1(self):
        """Método legado para compatibilidad hacia atrás. Ejecuta Consulta1 desde la configuración."""
        # Buscar la configuración de Consulta1
        for consulta in self.consultes_config.get('consultas', []):
            if consulta.get('id') == 'consulta1':
                self._ejecutar_consulta(consulta)
                return
        
        # Si no hay configuración, mostrar error
        QtWidgets.QMessageBox.warning(self, "Error", "No se encontró la configuración de Consulta1")

    def tancaPestanya(self, index):
        # Funció per tancar una pestanya quan es fa clic a la X
        # Només permet tancar la pestanya Consulta1 (o la que tenga el texto de la consulta1)
        tab_text = self.tabCentral.tabText(index)
        # Permitir cerrar tanto "Consulta1" como el nombre configurado en el JSON
        nombres_validos = ["Consulta1", "Bims sense geometria"]
        if tab_text in nombres_validos:
            self.tabCentral.removeTab(index)

    def desarCSV(self, layer, colOrder):
        """Exporta la capa a un fitxer CSV"""
        import csv
        from moduls.QvFuncions import startMovie, stopMovie
        from moduls.QvApp import QvApp
        
        path = ''
        player = None
        selected = (layer.selectedFeatureCount() > 0)
        filtered = (layer.subsetString() != '')
        if selected:
            sel = "els elements seleccionats"
        elif filtered:
            sel = "els elements filtrats"
        else:
            sel = "tots els elements"
        colNum, colName, asc = colOrder
        if colNum is None:
            request = QgsFeatureRequest()
        else:
            request = QgsFeatureRequest().addOrderBy(colName, asc, asc)

        numElems = 0
        try:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Desa {sel} a arxiu", '', 'CSV (*.csv)')
            if path:
                player = startMovie()
                with open(path, 'w', encoding="utf-8", newline='') as stream:
                    writer = csv.writer(stream, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(layer.fields().names())
                    if selected:
                        iterator = layer.getSelectedFeatures()
                    else:
                        iterator = layer.getFeatures(request)
                    for feature in iterator:
                        row = [str(feature.attribute(field.name())) for field in layer.fields()]
                        writer.writerow(row)
                        numElems += 1
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error al desar l'arxiu CSV", f"No s'ha pogut desar correctament l'arxiu: \n\n{path}")
            print(str(e))
            path = ''
        finally:
            if player is not None: 
                stopMovie(player)
        
        if path: 
            QtWidgets.QMessageBox.information(self, "Arxiu CSV desat correctament", f"S'han desat {sel} ({QvApp().locale.toString(numElems)}) a l'arxiu: \n\n{path}")
        
        return path
   
    def connectBotons(self):
        self.llistaBotons[0].clicked.connect(self.mostraFavorits)
        for (i,x) in enumerate(self.llistaBotons):
            x.clicked.connect(functools.partial(self.desmarcaBotons,x))
            x.clicked.connect(functools.partial(self.switchPantallaP,i))
        
    def switchPantallaP(self,i):
        self.stackedWidget.setCurrentIndex(i)
    def desmarcaBotons(self,aExcepcio):
        for x in self.llistaBotons:
            if x is not aExcepcio:
                x.setChecked(False)
            else:
                x.setChecked(True)
    
    def closeEvent(self, e):
        # Solo cerrar la aplicación si se cierra la ventana principal
        if self.isWindow() and self.isVisible():
            super().closeEvent(e)
            sys.exit(0)
        else:
            super().closeEvent(e)

def splashScreen():
    splash_pix = QtGui.QPixmap('imatges/MABIM/MABIMSplash.png')
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.setEnabled(True)
    splash.showMessage("""Institut Municipal d'Informàtica (IMI) MaBIM""",QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom, QvConstants.COLORFOSC)
    splash.setFont(QtGui.QFont(QvConstants.NOMFONT,8))
    splash.show()
    return splash
def arguments():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--projecte',help='Ruta del projecte del MaBIM', default=ConstantsMaBIM.rutaProjecte)
    parser.add_argument('--codi-bim', help='Codi BIM que es vol obrir', default=None)
    return parser.parse_args()
def main():
    with qgisapp(sysexit=False) as app:
        QvApp().carregaIdioma(app, 'ca')
        args = arguments()
        app.setWindowIcon(QtGui.QIcon('imatges/MaBIM/MaBIM vermell.png'))
        splash = splashScreen()
        app.processEvents()
        main = QMaBIM(args.projecte, args.codi_bim)
        splash.finish(main)
        main.showMaximized()

if __name__ == '__main__':
    main()
