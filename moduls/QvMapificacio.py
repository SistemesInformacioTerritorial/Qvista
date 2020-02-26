# -*- coding: utf-8 -*-


# Verifica si está disponible pandas, necesario para mapificar
import importlib

_np_spec = importlib.util.find_spec("numpy")
_pd_spec = importlib.util.find_spec("pandas")
_gpd_spec = importlib.util.find_spec("geopandas")

PANDAS_ENABLED = _np_spec is not None and _pd_spec is not None and _gpd_spec is not None
PANDAS_ERROR = "No es pot mapificar perquè no s'ha instal·lat el mòdul pandas.\n\nContacti amb el personal informàtic de suport."

if PANDAS_ENABLED:
    import numpy as np
    import pandas as pd
    import geopandas as gpd

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition, QgsVectorFileWriter,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator, QgsError, QgsWkbTypes,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsReadWriteContext, QgsExpressionContextUtils)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor, QValidator, QIcon
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtWidgets import QMessageBox

import os
import sys
import csv
import time
import unicodedata
import chardet
import collections
import operator
import re

from moduls.QvApp import QvApp
from moduls.QvSqlite import QvSqlite
from moduls.QvMapVars import *

from typing import List, Tuple, Iterable

_TRANS_ALL = str.maketrans("ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöüºª€$çÇñÑ ·.,;:()[]¡!¿?|%&*/\\\'\"@#",
                           "AEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouoaEDcCnN______________________aN")

_TRANS_MINI = str.maketrans(" \'\"",
                            "___")

RUTA_LOCAL = dadesdir
RUTA_DADES = os.path.abspath('Dades').replace('\\', '/') + '/'
CAMP_QVISTA = 'QVISTA_'

class QvMapificacio(QObject):
    """Clase que, a partir de un CSV con campos de dirección postal es capaz de:
       - Añadir a cada registro del CSV coordenadas y códigos de zona (distrito, barrio...) correspondientes a la dirección
       - Calcular una agregación a partir del código de zona para una posterior mapificación
    """

    def __init__(self, fDades: str, codi: str = '', separador: str = '', prefixe: str = CAMP_QVISTA, numMostra: int = 60):
        """Abre y prepara el fichero CSV para la mapificación
        
        Arguments:
            fDades {str} -- Nombre del fichero CSV a tratar
        
        Keyword Arguments:
            codi {str} -- Codificación de los caracteres del CSV. Por defecto, se infiere del fichero (default: {''})
            separador {str} -- Caracter separador de campos en el CSV. Por defecto, se infiere del fichero (default: {''})
            prefixe {str} -- Prefijo del campo añadido que contendra el codigo de zona;
                             el sufijo será el nombre de la zona escogida (default: {CAMP_QVISTA})
            numMostra {int} -- Número de filas de muestra a leer del CSV (default: {60})
        """
        super().__init__()
        self.fDades = self.fZones = fDades
        self.codi = codi
        self.prefixe = prefixe
        self.numMostra = numMostra
        self.mostra = []
        self.mostraCols = ''
        self.camps = []
        self.files = 0
        self.errors = 0
        self.msgError = ''
        self.cancel = False
        self.db = None
        self.iniDades(separador)

    def iniDades(self, sep: str) -> None:
        """ Inicialización a partir del fichero CSV
        
        Arguments:
            sep {str} -- Caracter separador de campos en el CSV
        """
        try:
            if not os.path.isfile(self.fDades):
                splitFile = os.path.split(self.fDades)
                local = RUTA_LOCAL + splitFile[1]
                if not os.path.isfile(local):
                    self.msgError = 'Arxiu CSV no existeix'
                    return
                else:
                    self.fDades = self.fZones = local

            if self.numMostra < 10:
                self.numMostra = 10

            if self.codi == '':
                self.codi = self.infereixCodi()

            with open(self.fDades, "r", encoding=self.codi) as csvInput:
                lenFile = os.path.getsize(self.fDades)
                # Cabecera con nombres de campos
                data = csvInput.readline()
                data = data.rstrip(''.join(csvInput.newlines))
                self.mostra = []
                self.mostraCols = data
                # Lineas de muestra
                lenMuestra = 0
                for num, data in enumerate(csvInput):
                    lenMuestra += len(data)
                    data = data.rstrip(''.join(csvInput.newlines))
                    self.mostra.append(data)
                    if num == self.numMostra:
                        break
                # Estimación de longitud de fichero y separador de campos
                lenRow = lenMuestra / num
                self.files = int(round(lenFile / lenRow))
                if sep == '':
                    sep = self.infereixSeparador()
                self.setSeparador(sep)
        except Exception as err:
            self.msgError = str(err)

    def setSeparador(self, sep: str) -> None:
        """Establece separador de campos
        
        Arguments:
            sep {str} -- Caracter separador
        """
        self.separador = sep
        if self.separador == '':
            self.msgError = 'Cal establir un caracter separador dels camps'
        else:
            self.camps = self.mostraCols.split(self.separador)

    def infereixCodi(self) -> str:
        '''Infereix la codificació d'un arxiu csv
        Returns:
            codi{str} -- El codi inferit
        '''
        with open(self.fDades, "rb") as csvInput:
            buf = csvInput.read(10000)
        val = chardet.detect(buf)
        return val['encoding']

    def infereixSeparador(self) -> str:
        '''Infereix el separador d'un arxiu csv
        Returns:
            separador{str} -- El separador inferit
        '''
        cont = collections.Counter()
        for linia in self.mostra:
            aux = linia.strip()
            aux = re.sub('"[^"]*"', '', aux) # Elimina strings entre comillas dobles
            aux = ''.join([i for i in aux if not i.isalnum()]) # Elimina caracteres alfanuméricos
            cont.update(aux)
        # Retornamos el caracter con más apariciones en total
        elems = cont.most_common(1)
        if len(elems) > 0:
            return elems[0][0]
        else:
            return ''

    def verifCampsAdreca(self, camps: List[str]) -> bool:
        """ Verifica la lista de campos de dirección postal. Han de venir en este orden:
            (Tipus_via, *Nombre_via, *Número_inicial, Letra_inicial, Número_final, Letra_final)
            Los precedidos por * son obligatorios.
            
        Arguments:
            camps {List[str]} -- Lista de campos que componen la dirección postal
        
        Returns:
            bool -- True si la verificación es correcta
        """
        try:
            if len(camps) not in list(range(3, 6+1)):
                return False
            num = 0
            for camp in camps:
                num += 1
                if num in (2, 3): # Obligatorio
                    if camp is None or camp not in self.camps:
                        return False
                else: # Opcional
                    if camp is not None and camp != '' and camp not in self.camps:
                        return False
            return True
        except Exception:
            return False

    def valorCampAdreca(self, fila: csv.OrderedDict, num: int) -> str:
        """ Retorna el valor de uno de los campos de la lista que componen la dirección postal.
        
        Arguments:
            fila {csv.OrderedDict} -- Fila leída del CSV
            num {int} -- Número de orden del campo de dirección postal
        
        Returns:
            str -- Valor del campo o '' si no se encuentra
        """
        try:
            camp = self.campsAdreca[num]
            if camp is None or camp == '':
                return ''
            else:
                return fila[camp]
        except Exception:
            return ''

    def verifZones(self, zones: List[str]) -> bool:
        """ Verifica la lista de zonas según el diccionario MAP_ZONES_COORD.
        
        Arguments:
            zones {List[str]} -- Lista de zonas.
        
        Returns:
            bool -- True si la verificación es correcta.
        """
        self.zones = zones
        self.valZones = []
        self.campsZones = []
        for zona in self.zones:
            if zona not in MAP_ZONES_COORD.keys():
                return False
            else:
                self.valZones.append(MAP_ZONES_COORD[zona])
        for v in self.valZones:
            camp = v[0]
            if isinstance(camp, str):
                self.campsZones.append(camp)
            else:
                for c in camp:
                    self.campsZones.append(c)
        return True

    @pyqtSlot()
    def cancelProces(self) -> None:
        """ Slot para cancelar el proceso de geocodificación.
        """
        self.cancel = True

    # Señales que informan de cómo va el proceso de geocodificación
    percentatgeProces = pyqtSignal(int)  # Porcentaje cubierto (0 - 100)
    procesAcabat = pyqtSignal(int)  # Tiempo transcurrido en zonificar (segundos)
    errorAdreca = pyqtSignal(dict) # Registro que no se pudo geocodificar
    filesGeocodificades = pyqtSignal(int, int) # Número de líneas geocodificadas y número total

    # def asincGeocodificacio(self, campsAdreca: List[str], zones: List[str], fZones: str = '', substituir: bool = True,
    #     percentatgeProces: pyqtSignal = None, procesAcabat: pyqtSignal = None, errorAdreca: pyqtSignal = None) -> bool:
    #     """ Versión asíncrona de la función geocodificacio, con los mismos parámetros
    #     """
    #     from multiprocessing.pool import ThreadPool
    #     pool = ThreadPool(processes=1)

    #     async_result = pool.apply_async(self.geocodificacio, (campsAdreca, zones, fZones, substituir, percentatgeProces, procesAcabat, errorAdreca))
    #     return async_result.get()

    def geocodificacio(self, campsAdreca: List[str], zones: List[str], fZones: str = '', substituir: bool = True,
        percentatgeProces: pyqtSignal = None, procesAcabat: pyqtSignal = None, errorAdreca: pyqtSignal = None, filesGeocodificades: pyqtSignal = None) -> bool:
        """Añade coordenadas y códigos de zona a cada uno de los registros del CSV, a partir de los campos de dirección postal

        Arguments:
            campsAdreca {List[str]} -- Nombre de los campos que definen la dirección postal, en este orden:
                                       TipusVia, Variant, NumIni, LletraIni, NumFi, LletraFi (mínimo 2º y 3º)
            zones List[str] -- Nombre de las zonas a añadir (ver MAP_ZONES_COORD en QvMapVars.py)
        
        Keyword Arguments:
            fZones {str} -- Nombre del fichero CSV de salida. Si no se indica, se usa el nombre del fichero
                            de entrada añadiendo el sufijo '_Geo' (default: {''})
            substituir {bool} -- En el caso de que el campo de código de zona ya exista y tenga un valor,
                                 indica si se ha de machacar o no su contenido (default: {True})
            percentatgeProces {pyqtSignal} -- Señal de progreso con el porcentaje transcurrido (default: {None})
            procesAcabat {pyqtSignal} -- Señal de finalización con tiempo transcurrido (default: {None})
            errorAdreca {pyqtSignal} -- Señal con registro erróneo (default: {None})
            filesGeocodificades {pyqtSignal} -- Señal de progreso con número de filas procesadas sobre el total (default: {None})

        Returns:
            bool -- True si ha ido bien, False si hay errores o se canceló el proceso (mensaje en self.msgError)

        """
        # Desconecta las señales si ya estaban conectadas
        try:
            self.percentatgeProces.disconnect()
        except:
            pass
        try:
            self.procesAcabat.disconnect()
        except:
            pass
        try:
            self.errorAdreca.disconnect()
        except:
            pass
        try:
            self.filesGeocodificades.disconnect()
        except:
            pass

        if self.db is None:
            self.db = QvSqlite()
        self.errors = 0
        self.msgError = ''

        if self.verifCampsAdreca(campsAdreca):
            self.campsAdreca = campsAdreca
        else:
            self.msgError = "Error als camps d'adreça"
            return False

        if not self.verifZones(zones):
            self.msgError = "Error paràmetre de zones"
            return False

        if fZones is None or fZones == '':
            base = os.path.basename(self.fDades)
            splitFile = os.path.splitext(base)
            filename = self.netejaString(splitFile[0] + '_Geo', True)
            self.fZones = RUTA_LOCAL + filename + splitFile[1]
        else:
            self.fZones = fZones

        self.substituir = substituir

        if self.files >= 100:
            nSignal = int(round(self.files / 100))
        else:
            nSignal = 1

        if percentatgeProces is not None:
            self.percentatgeProces.connect(percentatgeProces)
        if procesAcabat is not None:
            self.procesAcabat.connect(procesAcabat)
        if errorAdreca is not None:
            self.errorAdreca.connect(errorAdreca)
        if filesGeocodificades is not None:
            self.filesGeocodificades.connect(filesGeocodificades)

        self.cancel = False
        ini = time.time()

        # Fichero CSV de entrada
        with open(self.fDades, "r", encoding=self.codi) as csvInput:

            # Fichero CSV de salida geocodificado normalizado a utf-8
            with open(self.fZones, "w", encoding='utf-8') as csvOutput:

                # Cabeceras
                data = csv.DictReader(csvInput, delimiter=self.separador)
                
                # Normaliza nombres de campos
                self.camps = [self.netejaString(camp) for camp in self.camps]

                for campZona in self.campsZones:
                    campZona = QvSqlite.getAlias(campZona)
                    campSortida = self.prefixe + campZona
                    if campSortida not in self.camps:
                        self.camps.append(campSortida)
                        self.mostraCols += self.separador + campSortida
                
                writer = csv.DictWriter(csvOutput, delimiter=self.separador, fieldnames=self.camps, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y geocodificación
                tot = num = 0
                self.mostra = []
                for rowOrig in data:
                    tot += 1
                    # Normaliza nombres de campos
                    row = { self.netejaString(k): v for k, v in rowOrig.items() }

                    val = self.db.geoCampsCarrerNum(self.campsZones,
                            self.valorCampAdreca(rowOrig, 0), self.valorCampAdreca(rowOrig, 1), self.valorCampAdreca(rowOrig, 2),
                            self.valorCampAdreca(rowOrig, 3), self.valorCampAdreca(rowOrig, 4), self.valorCampAdreca(rowOrig, 5))
                    # Error en geocodificación
                    if val is None:
                        self.errorAdreca.emit(dict(rowOrig, **{'_fila':tot}))
                        num += 1
                    else:
                        for campZona in self.campsZones:
                            campZona = QvSqlite.getAlias(campZona)
                            campSortida = self.prefixe + campZona
                            campNou = (campSortida not in row.keys())
                            if campNou or self.substituir or row[campSortida] is None or row[campSortida] == '':
                                row.update([(campSortida, val[campZona])])
                    # Escritura de fila con campos
                    writer.writerow(row)

                    if self.numMostra >= tot:
                        self.mostra.append(self.separador.join(row.values()))

                    # Informe de progreso: filas y porcentaje (cada 1% o cada fila si hay menos de 100)
                    self.filesGeocodificades.emit(tot, self.files)
                    if self.files > 0 and tot % nSignal == 0:
                        self.percentatgeProces.emit(int(round(tot * 100 / self.files)))

                    # Cancelación del proceso via slot
                    if self.cancel:
                        break

            fin = time.time()
            self.errors = num

            # Informe de fin de proceso y segundos transcurridos
            if self.cancel:
                self.msgError = "Procés geocodificació cancel·lat"
            else:
                self.files = tot
                self.filesGeocodificades.emit(tot, self.files)
                self.percentatgeProces.emit(100)
            self.procesAcabat.emit(fin - ini)

            return not self.cancel

    # def calcSelect(self, camps: str = '') -> str:
    #     # Calculamos filtro
    #     if self.filtre is None or self.filtre == '':
    #         filtre = ''
    #     else:
    #         filtre = ' WHERE ' + self.filtre
    #     if self.tipusDistribucio == '':
    #         dist = ''
    #     else:
    #         dist = '/ Z.' + self.tipusDistribucio
    #     # Calculamos SELECT completo de agrupación
    #     select = "select round(I.AGREGAT " + dist + ", " + str(self.renderParams.numDecimals) + ") AS " + self.renderParams.campCalculat + \
    #              camps + " from Zona AS Z, " + \
    #              "(SELECT " + self.tipusAgregacio + " AS AGREGAT, " + self.campZona + " AS CODI " + \
    #              "FROM Info" + filtre + " GROUP BY " + self.campZona + ") AS I WHERE Z.CODI = I.CODI"
    #     return select

    def netejaString(self, txt: str, all: bool = False) -> str:
        """ Sustituye ciertos caracteres (de control, con acentos, etc) en un string.
        
        Arguments:
            txt {str} -- String a tratar
        
        Keyword Arguments:
            all {bool} -- Si es True, sustituye segín _TRANS_ALL; si no, utiliza _TRANS_MIN (default: {False})
        
        Returns:
            str -- String tratado
        """
        s = txt.strip()
        if all:
            s = s.translate(_TRANS_ALL)
        else:
            s = s.translate(_TRANS_MINI)
        return re.sub('_+', '_', s)

    def nomArxiuSortida(self, nom: str) -> str:
        """ Construye nombre completo fichero Geopakage de salida.
        
        Arguments:
            nom {str} -- Nombre del fichero sin path ni extensión
        
        Returns:
            str -- Nombre completo de fichero
        """
        return RUTA_LOCAL + nom + ".gpkg"

    def verifZona(self, zona: str) -> bool:
        """ Verifica si la zona es correcta y está disponible en el fichero de zonas
        
        Arguments:
            zona {str} -- Nombre de zona
        
        Returns:
            bool -- True si la verificación es correcta
        """
        self.zona = zona
        if self.zona is None or self.zona not in MAP_ZONES.keys():
            return False
        else:
            self.valZona = MAP_ZONES[self.zona]
        self.campZona = self.prefixe + QvSqlite.getAlias(self.valZona[0])
        if self.campZona not in self.camps:
            return False
        return True

    # def generaCapaQgis(self, nomCapa: str) -> bool:
    #     # Carga de capa de datos geocodificados
    #     infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
    #     infoLyr.setProviderEncoding(self.codi)
    #     if not infoLyr.isValid():
    #         self.msgError = "No s'ha pogut carregar capa de dades: " + self.fZones
    #         return False

    #     # Carga de capa base de zona
    #     self.fBase = RUTA_DADES + MAP_ZONES_DB + "|layername=" + self.valZona[1]
    #     zonaLyr = QgsVectorLayer(self.fBase, 'Zona', 'ogr')
    #     zonaLyr.setProviderEncoding("UTF-8")
    #     if not zonaLyr.isValid():
    #         self.msgError = "No s'ha pogut carregar capa de zones: " + self.fBase
    #         return False

    #     # Añadimos capas auxiliares a la leyenda (de forma no visible) para procesarlas
    #     self.llegenda.project.addMapLayer(infoLyr, False)
    #     self.llegenda.project.addMapLayer(zonaLyr, False)

    #     # Lista de campos de zona que se incluirán en la mapificación
    #     zonaCamps = ''
    #     for field in zonaLyr.fields():
    #         name = field.name().upper()
    #         if not name.startswith(self.prefixe) and not name.startswith('OGC_'):
    #             if field.typeName() == "Real":
    #                 zonaCamps += ", round(Z." + name + ", 2) as " + name
    #             else:
    #                 zonaCamps += ", Z." + name
    #     zonaCamps += ', Z.GEOMETRY as GEOM'

    #     # Creación de capa virtual que construye la agregación
    #     select = self.calcSelect(zonaCamps)
    #     virtLyr = QgsVectorLayer("?query=" + select, nomCapa, "virtual")
    #     virtLyr.setProviderEncoding("UTF-8")

    #     if not virtLyr.isValid():
    #         self.llegenda.project.removeMapLayer(zonaLyr.id())
    #         self.llegenda.project.removeMapLayer(infoLyr.id())
    #         self.msgError = "No s'ha pogut generar capa de agregació"
    #         return False

    #     # Guarda capa de agregación en GPKG
    #     self.fSQL = self.nomArxiuSortida(self.nomCapa)
    #     ret, msg = QgsVectorFileWriter.writeAsVectorFormat(virtLyr, self.fSQL, "UTF-8", zonaLyr.crs(), "GPKG",
    #         overrideGeometryType=QgsWkbTypes.MultiPolygon)
    #     if ret != QgsVectorFileWriter.NoError:
    #         self.llegenda.project.removeMapLayer(zonaLyr.id())
    #         self.llegenda.project.removeMapLayer(infoLyr.id())
    #         self.msgError = "No s'ha pogut desar capa de agregació: " + self.fSQL + " (Error - " + msg + ")"
    #         return False

    #     # Elimina capas de base y datos
    #     self.llegenda.project.removeMapLayer(zonaLyr.id())
    #     self.llegenda.project.removeMapLayer(infoLyr.id())
    #     return True

    # def saveGPKG(self, df, nomCapa):
    #     import fiona
    #     try:
    #         from fiona import Env as fiona_env
    #     except ImportError:
    #         from fiona import drivers as fiona_env
    #
    #     schema = gpd.io.file.infer_schema(df)
    #     with fiona_env(OGR_SQLITE_CACHE=512, OGR_SQLITE_SYNCHRONOUS=False):
    #         with fiona.open(self.fSQL, "w", driver="GPKG", crs=df.crs, schema=schema, layer=nomCapa, gt=65536) as colxn:
    #             colxn.writerecords(df.iterfeatures())

    def generaCapaGpd(self, nomCapa: str, tipusAgregacio: str, tipusDistribucio: str) -> bool:
        """ Calcula la agregación de datos, los cruza con el geopackage de zonas y genera la capa del mapa de coropletas.
        
        Arguments:
            nomCapa {str} -- Nombre de la capa del mapa
            tipusAgregacio {str} -- Tipo de agregación a aplicar
            tipusDistribucio {str} -- Tipo de distribución a aplicar
        
        Returns:
            bool -- True si se generó la capa con el  mapa correctamente
        """
        try:
            # El campo de zona se carga como string, y el de agregacion como float si hay acumulados
            if tipusAgregacio in ("Suma", "Mitjana"):
                dtypes = {self.campZona: np.string_, self.campAgregat: np.float_}
            else:
                dtypes = {self.campZona: np.string_}

            # Carga de capa de datos geocodificados
            csv = pd.read_csv(self.fZones, sep=self.separador, encoding='utf-8',
                              decimal=QvApp().locale.decimalPoint(), dtype=dtypes)

            # Aplicar filtro
            try:
                if self.filtre != '':
                    csv.query(self.filtre, inplace=True)
            except Exception as err:
                self.msgError = "Error a l'expressió de filtre"
                return False

            # Cálculo de la agreagación de datos
            if tipusAgregacio == "Cap":
                agreg = pd.Series(csv[self.campAgregat].values.round(self.renderParams.numDecimals), index=csv[self.campZona])
                if not agreg.index.is_unique:
                    msg = "El camp {} conté valors duplicats.\n" \
                          "Per poder mapificar, s'haurà de fer algun tipus d'agregació.".format(self.campZona)
                    self.msgError = msg
                    return False
            elif tipusAgregacio == "Recompte":
                agreg = csv.groupby(self.campZona).size()
            elif tipusAgregacio == "Recompte diferents":
                agreg = csv.groupby(self.campZona)[self.campAgregat].nunique()
            elif tipusAgregacio == "Suma":
                agreg = csv.groupby(self.campZona)[self.campAgregat].sum().round(self.renderParams.numDecimals)
            elif tipusAgregacio == "Mitjana":
                agreg = csv.groupby(self.campZona)[self.campAgregat].mean().round(self.renderParams.numDecimals)
            else:
                self.msgError = "Tipus de agregació '{}' incorrecte.".format(tipusAgregacio)
                return False
            agreg.index.names = ['CODI']
            res = agreg.to_frame(name='RESULTAT')

            # Carga de capa base de zona
            self.fBase = RUTA_DADES + MAP_ZONES_DB
            pols = gpd.read_file(self.fBase, driver="GPKG", layer=self.valZona[1], mode='r')
            if "AREA" in pols.columns:
                pols["AREA"] = pd.to_numeric(pols["AREA"]).round(3)
            if "POBLACIO" in pols.columns:
                pols["POBLACIO"] = pd.to_numeric(pols["POBLACIO"], downcast='integer', errors='coerce')

            # Join
            join = pols.merge(res, on='CODI', how='left')
            join['RESULTAT'].fillna(0, inplace=True)

            # Aplicar distribución
            if self.tipusDistribucio == '':
                out = join
            else:
                # Filtrar elementos para evitar division por 0
                out = join[join[self.tipusDistribucio].notnull() & (join[self.tipusDistribucio] > 0)]
                out["RESULTAT"] = (out["RESULTAT"] / out[self.tipusDistribucio]).round(self.renderParams.numDecimals)
                filtrats = len(join) - len(out)
                if filtrats > 0:
                    msg = "Hi ha {} elements de la zona {} que \n" \
                          "no tenen informació al camp {}.\n\n" \
                          "Amb aquests elements no és possible\n" \
                          "fer la distribució {} i per tant\n" \
                          "no sortiran a la mapificació.".format(filtrats, self.zona, self.tipusDistribucio,
                                                                 tipusDistribucio.lower())
                    if self.form is None:
                        print(msg)
                    else:
                        if not self.form.msgContinuarProces(msg):
                            return False

            # Guardar capa de mapa como Geopackage
            self.fSQL = self.nomArxiuSortida(nomCapa)
            out.to_file(self.fSQL, driver="GPKG", layer=nomCapa)
            return True
        except Exception as err:
            self.msgError = "Error al calcular l'agregació de dades.\n\n" + str(err)
            return False

    def agregacio(self, llegenda, nomCapa: str, zona: str, tipusAgregacio: str,
        campCalculat: str = 'RESULTAT', campAgregat: str = '', tipusDistribucio: str = "Total", filtre: str = '',
        numDecimals: int = -1, numCategories: int = 4, modeCategories: str = "Endreçat", colorBase: str = 'Blau',
        format: str = '%1 - %2', veure: bool = True, form = None) -> bool:
        """ Realiza la agragación de los datos por zona, la generación del mapa de coropletas y su simbología.
        
        Arguments:
            llegenda {QvLlegenda} -- Leyenda
            nomCapa {str} -- Nombre de la capa del mapa a generar
            zona {str} -- Zona de agregación
            tipusAgregacio {str} -- Tipo de agregación
        
        Keyword Arguments:
            campCalculat {str} -- Campo donde se guardará el resultado de la agregación (default: {'RESULTAT'})
            campAgregat {str} -- Campo que se utiliza en el cálculo de la agragación (default: {''})
            tipusDistribucio {str} -- Tipo de distribución (default: {"Total"})
            filtre {str} -- Expresión para filtrar los datos (default: {''})
            numDecimals {int} -- Número de decimales para el campo resultado (default: {-1})
            numCategories {int} -- Número de categorías en el mapa de coropletas (default: {4})
            modeCategories {str} -- Modo de generación de las categorías del mapa (default: {"Endreçat"})
            colorBase {str} -- Gama de color para las categorías del mapa (default: {'Blau'})
            format {str} -- Formato del texto de las categorías en la leyenda (default: {'%1 - %2'})
            veure {bool} -- Si es True, añade la nueva capa con el mapa en la leyenda (default: {True})
            form {QDialog} -- Formulario desde donde se invoca la función (default: {None})
        
        Returns:
            bool -- False si hubo errores (mensaje de error en self.msgError)
        """

        if not PANDAS_ENABLED:
            self.msgError = PANDAS_ERROR
            return False

        from moduls.QvMapRenderer import QvMapRendererParams

        self.fMapa = ''
        self.fSQL = ''
        self.llegenda = llegenda
        self.msgError = ''
        self.form = form
        self.descripcio = "Arxiu de dades: " + self.fZones + '\n' + \
            "Zona: " + zona + '\n' + \
            "Tipus d'agregació: " + tipusAgregacio + '\n' + \
            "Camp de càlcul: " + campAgregat + '\n' + \
            "Filtre: " + filtre + '\n' + \
            "Distribució: " + tipusDistribucio

        self.renderParams = QvMapRendererParams()

        if not self.verifZona(zona):
            self.msgError = "Error en zona"
            return False

        if campAgregat is not None and campAgregat != '':
            self.campAgregat = campAgregat
        elif tipusAgregacio == 'Recompte' and campAgregat == '':
            self.campAgregat = '*'
        else:
            self.msgError = "Error en campAgregat"
            return False

        if tipusAgregacio is None or tipusAgregacio not in MAP_AGREGACIO.keys():
            self.msgError = "Error en tipusAgregacio"
            return False
        self.tipusAgregacio = MAP_AGREGACIO[tipusAgregacio].format(self.campAgregat)

        if tipusDistribucio is None or tipusDistribucio not in MAP_DISTRIBUCIO.keys():
            self.msgError = "Error en tipusDistribucio"
            return False
        self.tipusDistribucio = MAP_DISTRIBUCIO[tipusDistribucio]

        if modeCategories is None or modeCategories not in MAP_METODES.keys():
            self.msgError = "Error en modeCategories"
            return False
        self.renderParams.modeCategories = MAP_METODES[modeCategories]

        if colorBase is None or colorBase not in MAP_COLORS.keys():
            self.msgError = "Error en colorBase"
            return False
        self.renderParams.colorBase = MAP_COLORS[colorBase]

        if numDecimals >= 0:
            self.renderParams.numDecimals = numDecimals
        elif self.tipusAgregacio.startswith('COUNT') and self.tipusDistribucio == "":
            self.renderParams.numDecimals = 0
        else:
            self.renderParams.numDecimals = 2

        self.renderParams.numCategories = numCategories
        self.filtre = filtre
        self.renderParams.campCalculat = campCalculat
        self.nomCapa = self.netejaString(nomCapa, True)

        # if not self.generaCapaQgis(nomCapa):
        #     return False

        if not self.generaCapaGpd(self.nomCapa, tipusAgregacio, tipusDistribucio):
            return False

        # Carga capa de agregación
        mapLyr = QgsVectorLayer(self.fSQL, nomCapa, "ogr")
        mapLyr.setProviderEncoding("UTF-8")
        if not mapLyr.isValid():
            self.msgError = "No s'ha pogut carregar capa de agregació: " + self.fSQL
            return False

        # Renderer para mapificar
        self.renderer = self.llegenda.mapRenderer.calcRender(mapLyr, self.renderParams)
        if self.renderer is None:
            self.msgError = "No s'ha pogut elaborar el mapa"
            return False
        else:
            mapLyr.setRenderer(self.renderer)

        # Identificador de mapificación para qVista
        QgsExpressionContextUtils.setLayerVariable(mapLyr, MAP_ID, self.descripcio)
        mapLyr.setDisplayExpression(self.renderParams.campCalculat)

        # Guarda simbología en GPKG
        err = self.llegenda.saveStyleToGeoPackage(mapLyr, MAP_ID)
        if err != '':
            self.msgError = "Hi ha hagut problemes al desar la simbologia\n({})".format(err)
            return False

        # Fin correcto
        self.fMapa = self.fSQL
        if veure:
            self.llegenda.project.addMapLayer(mapLyr)
        return True

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = True

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp
        from moduls.QvMapForms import QvFormMostra
        from qgis.gui import QgsMapCanvas
        from moduls.QvLlegenda import QvLlegenda
        from moduls.QvAtributs import QvAtributs
        from moduls.QvMapForms import QvFormNovaMapificacio

        app = QvApp()

        canv = QgsMapCanvas()
        canv.setWindowTitle('Canvas')
        canv.show()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib)
        leyenda.project.read('mapesOffline/qVista default map.qgs')
        leyenda.setWindowTitle('Llegenda')
        leyenda.show()


        # z = QvMapificacio('U:/QUOTA/Comu_imi/Becaris/CarrecsAnsi100.csv')
        # z = QvMapificacio('CarrecsUTF8.csv')
        z = QvMapificacio('C:/temp/qVista/dades/Terrasses.csv')

        if z.msgError != '':
            print('Error:', z.msgError)
            exit(1)
            
        print('Código caracteres:', z.codi)
        print('Num. líneas muestra:', z.numMostra)
        print('Delimitador:', z.separador)
        print('Muestra:', z.mostra)
        print('Campos:', z.camps)
        print(z.files, 'filas en', z.fDades)

        # w = QvFormMostra(z)
        # w.show()

        # campsAdreca = ('Tipus de via', 'Via', 'Número')
        # campsAdreca = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
        campsAdreca = ('Tipus via', 'Carrer', 'Numero')

        zones = ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica", "Secció censal")
        ok = z.geocodificacio(campsAdreca, zones,
            percentatgeProces=lambda n: print('... Procesado', str(n), '% ...'),
            errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            procesAcabat=lambda n: print('Zonas', z.zones, 'procesadas en', str(n), 'segs. en ' + z.fZones + ' -', str(z.files), 'registros,', str(z.errors), 'errores'))
            
        if ok:
            # w = QvFormMostra(z)
            # w.show()

            fMap = QvFormNovaMapificacio(leyenda, mapificacio=z)
            fMap.exec()
        else:
            print(z.msgError)
            ok = z.geocodificacio(campsAdreca, zones,
                percentatgeProces=lambda n: print('... Procesado', str(n), '% ...'),
                errorAdreca=lambda f: print('Fila sin geocodificar -', f),
                procesAcabat=lambda n: print('Zonas', z.zones, 'procesadas en', str(n), 'segs. en ' + z.fZones + ' -', str(z.files), 'registros,', str(z.errors), 'errores'))
            if ok:
                fMap = QvFormNovaMapificacio(leyenda, mapificacio=z)
                fMap.exec()
            else:
                print(z.msgError)



