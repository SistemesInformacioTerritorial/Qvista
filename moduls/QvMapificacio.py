# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsVectorLayer, QgsLayerDefinition, QgsVectorFileWriter,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator, QgsError,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsReadWriteContext, QgsExpressionContextUtils)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor, QValidator, QIcon
from qgis.PyQt.QtXml import QDomDocument

import os
import sys
import csv
import time
import unicodedata

from moduls.QvSqlite import QvSqlite
from moduls.QvMapVars import *

from typing import List, Tuple, Iterable

_TRANS = str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöüºª€@$·.,;:()[]¡!¿?|@#%&ç*',
                       'AEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouoaEaD____________________')

RUTA_LOCAL = 'C:/temp/qVista/dades/'
RUTA_DADES = 'D:/qVista/Codi/Dades/'

class QvMapificacio(QObject):
    """Clase que, a partir de un CSV con campos de dirección postal es capaz de:
       - Añadir a cada registro del CSV coordenadas y códigos de zona (distrito, barrio...) correspondientes a la dirección
       - Calcular una agregación a partir del código de zona para una posterior mapificación
    """

    def __init__(self, fDades: str, code: str = 'ANSI', delimiter: str = ';', numMostra: int = 60):
        """Abre y prepara el fichero CSV para la mapificación
        
        Arguments:
            fDades {str} -- Nombre del fichero CSV a tratar
        
        Keyword Arguments:
            code {str} -- Codificación de los caracteres del CSV (default: {'ANSI'})
            delimiter {str} -- Caracter separador de campos en el CSV (default: {';'})
            numMostra {int} -- Número de filas de muestra a leer del CSV para hacer una estimación del número total
                               de registros. Útil solo para la geocodificación (default: {60})
        """
        super().__init__()
        self.fDades = self.fZones = fDades
        self.code = code
        self.delimiter = delimiter
        self.numMostra = numMostra
        self.mostra = []
        self.fields = []
        self.rows = 0
        self.errors = 0
        self.msgError = ''
        self.cancel = False
        self.iniDades()
        self.db = QvSqlite()

    def iniDades(self) -> None:
        if not os.path.isfile(self.fDades):
            splitFile = os.path.split(self.fDades)
            local = RUTA_LOCAL + splitFile[1]
            if not os.path.isfile(local):
                return
            else:
                self.fDades = self.fZones = local

        with open(self.fDades, "r", encoding=self.code) as csvInput:
            lenFile = os.path.getsize(self.fDades)
            data = csvInput.readline()
            self.fields = data.rstrip(csvInput.newlines).split(self.delimiter)
            self.mostra = []
            if self.numMostra > 0:
                lenMuestra = 0
                maxMuestra = self.numMostra
                num = 0
                for data in csvInput:
                    num += 1
                    data = data.encode(self.code)
                    self.mostra.append(data)
                    lenMuestra += len(data)
                    if num == maxMuestra:
                        break
                lenRow = lenMuestra / num
                self.rows = int(round(lenFile / lenRow))

    def verifCampsAdreca(self, camps: List[str]) -> bool:
        try:
            if len(camps) not in list(range(3, 6+1)):
                return False
            num = 0
            for camp in camps:
                num += 1
                if num in (2, 3): # Obligatorio
                    if camp is None or camp not in self.fields:
                        return False
                else: # Opcional
                    if camp is not None and camp != '' and camp not in self.fields:
                        return False
            return True
        except Exception:
            return False
    
    def valorCampAdreca(self, fila: csv.OrderedDict, num: int) -> str:
        try:
            camp = self.campsAdreca[num]
            if camp is None or camp == '':
                return ''
            else:
                return fila[camp]
        except Exception:
            return ''
    
    @pyqtSlot()
    def cancelZonificacio(self) -> None:
        self.cancel = True

    percentatgeProces = pyqtSignal(int)  # Porcentaje cubierto (0 - 100)
    procesAcabat = pyqtSignal(int)  # Tiempo transcurrido en zonificar (segundos)
    errorAdreca = pyqtSignal(dict) # Registro que no se pudo geocodificar

    def verifZones(self, zones: List[str], prefixe: str = 'QVISTA_') -> bool:
        self.zones = zones
        self.prefixe = prefixe
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

    def geocodificacio(self, campsAdreca: List[str], zones: List[str], prefixe: str = 'QVISTA_', fZones: str ='', substituir: bool = True,
        percentatgeProces: pyqtSignal = None, procesAcabat: pyqtSignal = None, errorAdreca: pyqtSignal = None) -> bool:
        """Añade coordenadas y códigos de zona a cada uno de los registros del CSV, a partir de los campos de dirección postal

        Arguments:
            campsAdreca {List[str]} -- Nombre de los campos que definen la dirección postal, en este orden:
                                       TipusVia, Variant, NumIni, LletraIni, NumFi, LletraFi (mínimo 2º y 3º)
            zona List[str] -- Nombre de las zonas a añadir (ver MAP_ZONES_COORD en QvMapVars.py)
        
        Keyword Arguments:
            prefixe {str} -- Prefijo del campo añadido que contendra el codigo de zona;
                             el sufijo será el nombre de la zona escogida (default: {'QVISTA_'})
            fZones {str} -- Nombre del fichero CSV de salida. Si no se indica, se usa el nombre del fichero
                            de entrada añadiendo el nombre de la zona (default: {''})
            substituir {bool} -- En el caso de que el campo de código de zona ya exista y tenga un valor,
                                 indica si se ha de machacar o no su contenido (default: {True})
            percentatgeProces {pyqtSignal} -- Señal de progreso con el porcentaje transcurrido (default: {None})
            procesAcabat {pyqtSignal} -- Señal de finalización con tiempo transcurrido (default: {None})
            errorAdreca {pyqtSignal} -- Señal con registro erróno (default: {None})

        Returns:
            bool -- True si ha ido bien, False si hay errores (mensaje en self.msgError)

        """
        self.msgError = ''

        if self.verifCampsAdreca(campsAdreca):
            self.campsAdreca = campsAdreca
        else:
            self.msgError = "Error als camps d'adreça"
            return False

        if not self.verifZones(zones, prefixe):
            self.msgError = "Error paràmetre de zones"
            return False

        if fZones is None or fZones == '':
            base = os.path.basename(self.fDades)
            splitFile = os.path.splitext(base)
            self.fZones = RUTA_LOCAL + splitFile[0] + '_Geo' + splitFile[1]
        else:
            self.fZones = fZones

        self.substituir = substituir

        if self.rows >= 100:
            nSignal = int(round(self.rows / 100))
        else:
            nSignal = 1

        if percentatgeProces is not None:
            self.percentatgeProces.connect(percentatgeProces)
        if procesAcabat is not None:
            self.procesAcabat.connect(procesAcabat)
        if errorAdreca is not None:
            self.errorAdreca.connect(errorAdreca)

        self.cancel = False
        ini = time.time()

        # Fichero CSV de entrada
        with open(self.fDades, "r", encoding=self.code) as csvInput:

            # Fichero CSV de salida geocodificado
            with open(self.fZones, "w", encoding=self.code) as csvOutput:

                # Cabeceras
                data = csv.DictReader(csvInput, delimiter=self.delimiter)

                for campZona in self.campsZones:
                    campSortida = self.prefixe + campZona
                    if campSortida not in self.fields:
                        self.fields.append(campSortida)

                writer = csv.DictWriter(csvOutput, delimiter=self.delimiter, fieldnames=self.fields, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y geocodificación
                tot = num = 0
                for row in data:
                    tot += 1

                    val = self.db.geoCampsCarrerNum(self.campsZones,
                            self.valorCampAdreca(row, 0), self.valorCampAdreca(row, 1), self.valorCampAdreca(row, 2),
                            self.valorCampAdreca(row, 3), self.valorCampAdreca(row, 4), self.valorCampAdreca(row, 5))
                    # Error en geocodificación
                    if val is None:
                        self.errorAdreca.emit(dict(row))
                        num += 1
                    # Escritura de fila con campos
                    else:
                        for campZona in self.campsZones:
                            campSortida = self.prefixe + campZona
                            campNou = (campSortida not in row.keys())
                            if campNou or self.substituir or row[campSortida] is None or row[campSortida] == '':
                                row.update([(campSortida, val[campZona])])

                    # if campoNuevo or self.substituir or row[self.campZona] is None or row[self.campZona] == '':
                    #     val = self.db.geoCampCarrerNum(self.valZona[0],
                    #           self.valorCampAdreca(row, 0), self.valorCampAdreca(row, 1), self.valorCampAdreca(row, 2),
                    #           self.valorCampAdreca(row, 3), self.valorCampAdreca(row, 4), self.valorCampAdreca(row, 5))
                    #     # Error en geocodificación
                    #     if val is None:
                    #         self.errorAdreca.emit(dict(row))
                    #         num += 1
                    #     # Escritura de fila con campo
                    #     row.update([(self.campZona, val)])
                    
                    writer.writerow(row)
                    # Informe de progreso cada 1% o cada fila si hay menos de 100
                    if self.rows > 0 and tot % nSignal == 0:
                        self.percentatgeProces.emit(int(round(tot * 100 / self.rows)))

                    # Cancelación del proceso via slot -- SIN PROBAR
                    if self.cancel:
                        break

            fin = time.time()
            self.rows = tot
            self.errors = num

            # Informe de fin de proceso y segundos transcurridos
            if not self.cancel:
                self.percentatgeProces.emit(100)
            self.procesAcabat.emit(fin - ini)
            return True

    def calcSelect(self, llistaCamps: List[str] = []) -> str:
        # Calculamos filtro
        if self.filtre is None or self.filtre == '':
            filtre = ''
        else:
            filtre = ' WHERE ' + self.filtre
        # Calculamos lista de campos de la zona
        camps = ''
        if llistaCamps is not None and len(llistaCamps) > 0:
            for item in llistaCamps:
                camps += ", Z." + item
        camps += ', Z.GEOMETRY as GEOM'
        # Calculamos SELECT comlpeto de agrupación
        select = "select round(I.AGREGAT " + self.tipusDistribucio + ", " + str(self.numDecimals) + ") AS " + self.campCalculat + \
                 camps + " from Zona AS Z, " + \
                 "(SELECT " + self.tipusAgregacio + " AS AGREGAT, " + self.campZona + " AS CODI " + \
                 "FROM Info" + filtre + " GROUP BY " + self.campZona + ") AS I WHERE Z.CODI = I.CODI"
        return select

    def netejaString(self, txt: str) -> str:
        s = txt.strip()
        s = s.replace(' ', '_')
        s = s.translate(_TRANS)
        return s

    def agregacio(self, llegenda, nomCapa: str, tipusAgregacio: str,
        campCalculat: str = 'RESULTAT', campAgregat: str = '', tipusDistribucio: str = "Total", filtre: str = '', numDecimals: int = -1,
        numCategories: int = 4, modeCategories: str = "Endreçat", colorBase: str ='Blau', format: str = '%1 - %2',
        veure: bool = True) -> bool:
        """ ***********************************************************************************************************
            EN DESARROLLO *********************************************************************************************
            ***********************************************************************************************************
        
        Arguments:
            llegenda {[type]} -- [description]
            nomCapa {str} -- [description]
            tipusAgregacio {str} -- [description]
        
        Keyword Arguments:
            campCalculat {str} -- [description] (default: {'RESULTAT'})
            campAgregat {str} -- [description] (default: {''})
            tipusDistribucio {str} -- [description] (default: {"Total"})
            filtre {str} -- [description] (default: {''})
            numDecimals {int} -- [description] (default: {-1})
            numCategories {int} -- [description] (default: {4})
            modeCategories {str} -- [description] (default: {"Endreçat"})
            colorBase {str} -- [description] (default: {'Blau'})
            format {str} -- [description] (default: {'%1 - %2'})
            veure {bool} -- [description] (default: {True})
        
        Returns:
            bool -- [description]
        """

        self.fMapa = ''
        self.capaMapa = None
        self.fSQL = ''
        self.llegenda = llegenda
        self.msgError = ''

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
        self.modeCategories = MAP_METODES[modeCategories]

        if colorBase is None or colorBase not in MAP_COLORS.keys():
            self.msgError = "Error en colorBase"
            return False
        self.colorBase = MAP_COLORS[colorBase]

        if numDecimals >= 0:
            self.numDecimals = numDecimals
        elif self.tipusAgregacio.startswith('COUNT'):
            self.numDecimals = 0
        else:
            self.numDecimals = 2

        self.numCategories = numCategories
        self.filtre = filtre
        self.campCalculat = campCalculat
        self.nomCapa = self.netejaString(nomCapa)

        # Carga de capa de datos geocodificados
        infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
        infoLyr.setProviderEncoding(self.code)
        if not infoLyr.isValid():
            self.msgError = "No s'ha pogut carregar capa de dades: " + self.fZones
            return False

        # Carga de capa base de zona
        self.fBase = RUTA_DADES + self.valZona[1]
        zonaLyr = QgsVectorLayer(self.fBase, 'Zona', 'ogr')
        zonaLyr.setProviderEncoding("UTF-8")
        if not zonaLyr.isValid():
            self.msgError = "No s'ha pogut carregar capa de zones: " + self.fBase
            return False

        # Añadimos capas auxiliares a la leyenda (de forma no visible) para procesarlas
        self.llegenda.project.addMapLayer(infoLyr, False)
        self.llegenda.project.addMapLayer(zonaLyr, False)

        # Lista de campos de zona que se incluirán en la mapificación
        zonaCamps = []
        for field in zonaLyr.fields():
            name = field.name().upper()
            if not name.startswith('QVISTA_') and not name.startswith('OGC_'):
                zonaCamps.append(name)

        # Creación de capa virtual que construye la agregación
        select = self.calcSelect(zonaCamps)
        virtLyr = QgsVectorLayer("?query=" + select, nomCapa, "virtual")
        virtLyr.setProviderEncoding("UTF-8")            

        if not virtLyr.isValid():
            self.llegenda.project.removeMapLayer(zonaLyr.id())
            self.llegenda.project.removeMapLayer(infoLyr.id())
            self.msgError = "No s'ha pogut generar capa de agregació"
            return False

        # Guarda capa de agregación en SQLite
        self.fSQL = RUTA_LOCAL + self.nomCapa + ".sqlite"
        ret, msg = QgsVectorFileWriter.writeAsVectorFormat(virtLyr, self.fSQL, "UTF-8", zonaLyr.crs(), "SQLite")
        if ret != QgsVectorFileWriter.NoError:
            self.llegenda.project.removeMapLayer(zonaLyr.id())
            self.llegenda.project.removeMapLayer(infoLyr.id())
            self.msgError = "No s'ha pogut desar capa de agregació: " + self.fSQL + " (Error - " + msg + ")"
            return False

        # Elimina capas de base y datos
        self.llegenda.project.removeMapLayer(zonaLyr.id())
        self.llegenda.project.removeMapLayer(infoLyr.id())

        # Carga capa SQLite de agregación
        mapLyr = QgsVectorLayer(self.fSQL, nomCapa , "ogr")
        mapLyr.setProviderEncoding("UTF-8")
        if not mapLyr.isValid():
            self.msgError = "No s'ha pogut carregar capa de agregació: " + self.fSQL
            return False

        # Renderer para mapificar
        self.renderer = self.llegenda.mapRenderer.calcRender(mapLyr, self.campCalculat, self.numDecimals,
            self.colorBase, self.numCategories, self.modeCategories)
        if self.renderer is None:
            self.msgError = "No s'ha pogut elaborar el mapa"
            return False
        else:
            mapLyr.setRenderer(self.renderer)

        # Guarda capa qlr con agregación + mapificación
        self.fMapa = RUTA_LOCAL + self.nomCapa + '.qlr'

        # Tipo de capa para qVista
        QgsExpressionContextUtils.setLayerVariable(mapLyr, 'qV_tipusCapa', 'MAPIFICACIÓ')

        try:
            # Leer DOM, eliminar path local y guardar en fichero
            domDoc = QgsLayerDefinition.exportLayerDefinitionLayers([mapLyr], QgsReadWriteContext())
            txt = domDoc.toString()
            txt = txt.replace(RUTA_LOCAL, './')
            with open(self.fMapa, "w+", encoding="UTF-8") as qlr:
                qlr.write(txt)
        except Exception as e:
            fich = self.fMapa
            self.fMapa = ''
            print(e)
            self.msgError = "No s'ha pogut desar capa mapificació: " + fich
            return False

        # Mostar qlr de mapificación, si es el caso
        if veure and self.fMapa != '':
            # Cargar qlr
            ok, txt = QgsLayerDefinition.loadLayerDefinition(self.fMapa,
                self.llegenda.project, self.llegenda.root)
            if not ok:
                self.msgError = "No s'ha pogut carregar capa mapificació: " + self.fMapa
                return False
            QgsApplication.processEvents()

        return True

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()

        z = QvMapificacio('CarrecsANSI.csv')
        print(z.rows, 'filas en', z.fDades)
        print('Campos:', z.fields)
        print('Muestra:', z.mostra)

        camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
        zones = ('Coordenada', 'Barri')
        ok = z.geocodificacio(camps, zones,
            percentatgeProces=lambda n: print('... Procesado', str(n), '% ...'),
            errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            procesAcabat=lambda n: print('Zonas', z.zones, 'procesadas en', str(n), 'segs. en ' + z.fZones + ' -', str(z.rows), 'registros,', str(z.errors), 'errores'))
        if not ok:
            print('ERROR:', z.msgError)
