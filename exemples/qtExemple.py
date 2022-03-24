#from MaBIM-ui import Ui_MainWindow
import argparse
import functools
import getpass
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

import configuracioQvista
from moduls import QvFuncions
from moduls.QvApp import QvApp
from moduls.QvAtributs import QvAtributs
from moduls.QvAtributsForms import QvFitxesAtributs
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
                       QgsRectangle, QgsVectorLayer)
from qgis.core.contextmanagers import qgisapp
from qgis.gui import (QgsGui, QgsLayerTreeMapCanvasBridge, QgsMapTool,
                      QgsRubberBand, QgsVertexMarker)


class ConstantsMaBIM:
    DB_MABIM_PRO = {
        'Database': 'QOCISPATIAL',
        'HostName': 'GEOPR1.imi.bcn',
        'Port': 1551,
        'DatabaseName': 'GEOPR1',
        'UserName': 'PATRIMONI_CONS',
        'Password': 'PATRIMONI_CONS'
    }

    rutaUI= 'exemples/qtExemple.ui'
    rutaProjecte = 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/PPM_CatRegles_geopackage.qgs'
    rutaProjecteEdicio = 'L:/DADES/SIT/qVista/CATALEG/MAPES PRIVATS/Patrimoni/mabimEDICIO_v3.qgs'

    rutaLogoAjuntament = 'imatges/escutDreta.png'

    nomCapaPH = 'Entitats en PH'
    nomCapaPV = 'Entitats en PV'

    nomsCapes = [nomCapaPH, nomCapaPV]

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


    CONSULTA_INFO_BIM_Z2 = '''SELECT BIM, ESTAT, ADSCRIT,
                               DESCRIPCIO_BIM, DENOMINACIO_BIM,
                               TIPOLOGIA_BIM, SUBTIPOLOGIA_BIM, TIPUS_IMMOBLE, QUALIFICACIO_JURIDICA
                               FROM
                               ZAFT_0002
                               WHERE
                               ((BIM LIKE '%'||:pText||'%')
                                   OR (UPPER(DESCRIPCIO_BIM) LIKE '%'||:pText||'%')
                                   OR (UPPER(DENOMINACIO_BIM) LIKE '%'||:pText||'%')
                                   OR (UPPER(REF_CADASTRE_BIM) LIKE '%'||:pText||'%'))
                               AND (ROWNUM < 100)'''

    # Consulta que obté informació de ZAFT_0003 a partir del codi BIM
    CONSULTA_INFO_BIM_Z3 = '''SELECT TIPUS_VIA, NOM_VIA, NUM_INI,
                               LLETRA_INI, NUM_FI, LLETRA_FI, DISTRICTE, BARRI, MUNICIPI, CP,
                               PROVINCIA, TIPUS
                               FROM ZAFT_0003
                               WHERE
                               ((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

    CONSULTA_INFO_BIM_Z13 = '''SELECT PROPIETARI_SOL, PROPIETARI_CONS, SUP_REGISTRAL_SOL, SUP_REGISTRAL_CONS
                                FROM ZAFT_0013
                                WHERE
                                ((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''

    CONSULTA_INFO_BIM_Z11 = '''SELECT FINCA, NUM_REGISTRE, MUNICIPI, SECCIO, TOM, LLIBRE, FOLI, INSCRIP, CRU, SUP_REGISTRAL_SOL, SUP_REGISTRAL_CONS
                                FROM ZAFT_0011
                                WHERE
                                ((BIM LIKE '%'||:pText||'%') AND (ROWNUM<100))'''


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
        def comenca(x):
            # Volem comprovar si alguna de les subparaules de x comença per word
            # Una manera de mirar-ho és mirar si x comença per word o x conté ' 'word
            return x.startswith(word) or f' {word}' in x
        def no_comenca(x):
            return not comenca(x)
        return list(filter(comenca,llista)), list(filter(no_comenca,llista))
    def update(self, text):
        # actualitza el contingut del completer en funció del text cercat
        # fa la consulta a la base de dades, i ordena el resultat
        self.llista=Consulta().consulta(ConstantsMaBIM.CONSULTA_CERCADOR,{':pText':text.upper()},(0,1,2))
        self.m_word = text
        # converteix el resultat de la consulta
        #  (llista de llistes, amb els camps de la base de dades)
        #  en una llista de strings, que conté els camps no nuls separats per espais
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

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
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
        msgBox = QMessageBox()
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
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())

            features = []
            node = self.llegenda.nodePerNom('Inventari municipal')
            for nodeLayer in node.findLayers():
                layer = nodeLayer.layer()
                if layer.type()==QgsMapLayer.VectorLayer and 'BIM' in layer.fields().names():
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.buttonBox.removeButton(self.ui.buttonBox.buttons()[0])
        self.ui.bSeleccionar = self.ui.buttonBox.addButton('Seleccionar', QtWidgets.QDialogButtonBox.ActionRole)
        self.ui.bSeleccionar.clicked.connect(self.selecciona)
        self.ui.buttonBox.setFixedWidth(300)
        for x in (self.ui.bNext, self.ui.bPrev, *self.ui.buttonBox.buttons()):
            x.setStyleSheet('QAbstractButton{font-size: 14px; padding: 2px}')
            x.setFixedSize(100,30)
    def selecciona(self):
        index = self.ui.stackedWidget.currentIndex()
        feature = self.features[index]
        codi = str(feature.attribute('BIM'))
        self.parentWidget().leCercador.setText(codi)
        self.parentWidget().consulta()
        self.close()


class Cercador:
    """Classe de conveniència per encapsular el cercador (lineedits, icona i funcions que fan la cerca)
    """
    MIDALBLCARRER = 400, 40
    MIDALBLNUMERO = 80, 40
    MIDALBLICONA = 20, 20
    def __init__(self, canvas, leCarrer, leNumero, lblIcona):
        super().__init__()
        self.canvas = canvas
        self.marcaLloc = None
        self.leCarrer = leCarrer
        self.leCarrer.setPlaceholderText('Carrer')
        self.leNumero = leNumero
        self.leNumero.setPlaceholderText('Número')
        self.lblIcona = lblIcona
        self.cercador = QCercadorAdreca(self.leCarrer, self.leNumero, 'SQLITE')
        self.marcaLlocPosada = False

        self.cercador.sHanTrobatCoordenades.connect(self.resultatCercador)

    def resultatCercador(self, codi, info):
        if codi == 0:
            self.canvas.setCenter(self.cercador.coordAdreca)
            self.canvas.zoomScale(1000)
            self.canvas.scene().removeItem(self.marcaLloc)

            self.marcaLloc = QgsVertexMarker(self.canvas)
            self.marcaLloc.setCenter( self.cercador.coordAdreca )
            self.marcaLloc.setColor(QtGui.QColor(255, 0, 0))
            self.marcaLloc.setIconSize(15)
            self.marcaLloc.setIconType(QgsVertexMarker.ICON_BOX)
            self.marcaLloc.setPenWidth(3)
            self.marcaLloc.show()
            self.marcaLlocPosada = True
            self.leCarrer.clear()
            self.leNumero.clear()
    def eliminaMarcaLloc(self):
        if self.marcaLlocPosada:
            self.canvas.scene().removeItem(self.marcaLloc)
            self.marcaLlocPosada = False

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
            self.mostra_error(QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError().text())
            return False
        query=QSqlQuery(self.db)
        query.prepare(self.consultaAfegeix.format(**self.dadesTaula))
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_FAVORIT',favorit)
        query.bindValue(':OBSERVACIONS', observacio)
        executada = query.exec()
        self.__DESCONNECTA_BASE_DADES__(usuari)
        if not executada:
            self.mostra_error(QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError.text())
        return executada
    def actualitzaObservacio(self,favorit,observacio,usuari=getpass.getuser().upper()):
        if not self.__CONNECTA_BASE_DADES__(usuari):
            self.mostra_error(QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError().text())
            return False
        query=QSqlQuery(self.db)
        query.prepare(self.consultaUpdate.format(**self.dadesTaula))
        query.bindValue(':IDUSER',usuari)
        query.bindValue(':NOM_FAVORIT',favorit)
        query.bindValue(':OBSERVACIONS', observacio)
        executada = query.exec()
        self.__DESCONNECTA_BASE_DADES__(usuari)
        if not executada:
            self.mostra_error(QMessageBox.Warning, 'Atenció', "No s'ha pogut afegir a favorits. Intenteu-ho més tard, si us plau", None, self.db.lastError.text())
        return executada


class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self, projecte, *args,**kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(ConstantsMaBIM.rutaUI,self)

        self.llistaBotons = (self.bFavorits, self.bBIMs, self.bPIP, self.bProjectes, self.bConsultes)

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

        self.bObrirQGIS.clicked.connect(self.obrirEnQGIS)
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
        # res3 = cons.consulta(ConstantsMaBIM.CONSULTA_DATA_DADES,{':pText':txt3})[0][0].toString(QtCore.Qt.ISODate)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(5)

        self.l_DataCSV.setFont(font)
        self.l_DataCarregaCSV.setFont(font)
        self.l_DataCSV.setText(self.replace(res1, 'T', ' - '))
        self.l_DataCarregaCSV.setText(self.replace(res2, 'T', ' - '))


    # function to convert qdatetime to text
    def mostraMesures(self):
        self.wMesuraGrafica.show()

    # function to replace a string in a string
    def replace(self, text, buscar, reempla):
        return reempla.join(text.split(buscar))

    def dialegSetFavorit(self):
        if self.bAfegirFavorit.isChecked():
            text, ok = QtWidgets.QInputDialog.getText(self, 'Afegir com a favorit', "Observacions", flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
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
        form = FormulariAtributs(self.getCapaBIMs(), feats, self)
        form.moveWid(self.width()-form.width(),(self.height()-form.height())//2)
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
            (self.bProjectes, 'botonera-projectes'),
            (self.bConsultes, 'botonera-consultes')
        )
        for (boto, icona) in parelles:
            boto.setIcon(QtGui.QIcon(f'Imatges/MaBIM/{icona}'))

    def connectaDB(self):
        pass
    def connectaCercador(self):
        completer = Completador()
        self.leCercador.setCompleter(completer)
        completer.activated.connect(self.consulta)
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
        self.dadesLabelsDades[0] = self.dadesLabelsDades[0].replace('0000', ' ').lstrip()

        self.bAfegirFavorit.show()
        self.bAfegirFavorit.setChecked(self.dadesLabelsDades[0] in self.favorits)
        # Labels pestanya "Dades Identificatives"
        labels = (self.lNumBIM, self.lEstatBIM, self.lBIMAdscrit,
                  self.lDescripcioBIM, self.lDenominacioBIM,
                  self.lTipologiaReal, self.lSubtipologiaReal, self.lTipusBeReal, self.lQualificacioJuridica)
        # totes les labels tindran la mateixa font. Per tant, agafem la d'una qualsevol
        font = self.lNumBIM.font()
        for (lbl,txt) in zip(labels, self.dadesLabelsDades):
            if str(txt).upper()!='NULL':
                lbl.setText(txt)

                lbl.setFont(font)
                lbl.setWordWrap(True)
            else:
                lbl.setText('')
        self.lTipologiaRegistral.setText(self.lTipologiaReal.text())
        self.lSubtipologiaRegistral.setText(self.lSubtipologiaReal.text())
        self.lTipusBeRegistral.setText(self.lTipusBeReal.text())
        self.lTipologiaRegistral.setFont(font)
        self.lSubtipologiaRegistral.setFont(font)
        self.lTipusBeRegistral.setFont(font)

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
        labels = (self.lPropietariSol, self.lPropietariCons, self.lSupSolReg, self.lSupConsReg)

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
        self.twFinquesRegistrals.resizeColumnsToContents()

        cerca = f"BIM LIKE '0000{self.dadesLabelsDades[0]}'"

        layers = self.getCapesBIMs()
        for layer in layers:
            layer.setSubsetString(cerca)
        # Si no hi ha cap feature després d'aplicar el filtre, eliminem el filtre i mostrem tota l'extensió
        if sum(layer.featureCount() for layer in layers)==0:
            self.netejaFiltre()
            QtWidgets.QMessageBox.warning(self,"Atenció!", "No s'ha pogut localitzar el BIM en el mapa.")
        self.canvasA.setExtent(layer.extent())

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

        taulesAtributs = QvAtributs(self.canvasA)
        taulesAtributs.setWindowTitle("Taules d'atributs")
        self.llegenda = QvLlegenda(self.canvasA, taulesAtributs)
        self.canvasA.setLlegenda(self.llegenda)
        self.llegenda.resize(500, 600)

        self.canvasA.bCentrar.disconnect()
        self.canvasA.bCentrar.clicked.connect(self.centrarMapa)

        # instanciem el mapeta
        self.mapetaA = QvMapetaBrujulado(mapetaPng, self.canvasA, pare=self.canvasA)

        self.cerca1 = Cercador(self.canvasA, self.leCarrer, self.leNumero, self.lblIcona)
        self.cerca1.cercador.sHanTrobatCoordenades.connect(lambda: self.tabCentral.setCurrentIndex(2))

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

    @QvFuncions.cronometraDebug
    def inicialitzaProjecte(self, projecte):
        self.llegenda.readProject(projecte)
        self.centrarMapa()

        # cal comprovar si les capes ... i ... són visibles
        def nodeConteBaixa(node):
            nomNode = node.data(QtCore.Qt.DisplayRole).lower()
            return 'baixa' in nomNode or 'baixes' in nomNode
        model = self.llegenda.model
        capes = (self.llegenda.capaPerNom(nomCapa) for nomCapa in ConstantsMaBIM.nomsCapes)
        nodesCapes = (QgsProject.instance().layerTreeRoot().findLayer(capa.id()) for capa in capes)
        self.nodesBaixes = [node for nodeCapa in nodesCapes for node in model.layerLegendNodes(nodeCapa) if nodeConteBaixa(node)]


        QgsProject.instance().layerTreeRoot().visibilityChanged.connect(self.canviVisibilitatLlegenda)
        for x in self.nodesBaixes:
            x.dataChanged.connect(lambda: self.canviVisibilitatLlegenda(x))

        self.nodeRegistrals = QgsProject.instance().layerTreeRoot().findLayer(self.llegenda.capaPerNom('SECCIONS_REGISTRALS').id())

        self.cbBaixesVisibles.clicked.connect(self.swapVisibilitatBaixes)
        self.cbRegistresPropietat.clicked.connect(self.swapVisibilitatRegistre)

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
        elif node==self.nodeRegistrals:
            self.cbRegistresPropietat.setChecked(node.isVisible())

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

    def getCapaBIMs(self):
        # Retorna una capa amb camp de BIMs
        #  nota: millor evitar-la, això només per quan ens veiem forçats a passar una única capa
        # return self.llegenda.capaPerNom('Entitats en PV')
        return self.getCapesBIMs()[0]
    def getCapesBIMs(self):
        return [capa for capa in self.llegenda.capes() if 'BIM' in capa.fields().names()]

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
    return parser.parse_args()
def main():
    with qgisapp(sysexit=False) as app:
        args = arguments()
        app.setWindowIcon(QtGui.QIcon('imatges/MaBIM/MaBIM vermell.png'))
        splash = splashScreen()
        app.processEvents()
        main = QMaBIM(args.projecte)
        splash.finish(main)
        main.showMaximized()

if __name__ == '__main__':
    main()
