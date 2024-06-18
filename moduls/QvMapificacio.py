# -*- coding: utf-8 -*-

from qgis.core import QgsVectorLayer, QgsExpressionContextUtils
from qgis.PyQt.QtCore import QDate, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QMessageBox

import os
import csv
import time
import chardet
import collections
import re
from typing import List, Callable

from moduls.QvApp import QvApp
from moduls.QvSqlite import QvSqlite
from moduls.QvMapRenderer import QvMapRendererParams
import moduls.QvMapVars as mv
from moduls import QvNumPostal

from configuracioQvista import dadesdir

# Verifica si está disponible pandas, necesario para mapificar
import importlib

_np_spec = importlib.util.find_spec("numpy")
_pd_spec = importlib.util.find_spec("pandas")
_gpd_spec = importlib.util.find_spec("geopandas")

PANDAS_ENABLED = _np_spec is not None and _pd_spec is not None and _gpd_spec is not None
PANDAS_ERROR = "No es pot mapificar perquè no s'ha instal·lat el mòdul pandas." + \
               "\n\nContacti amb el personal informàtic de suport."

# from typing import List
# from moduls.QvPlotly import QvPlot

_TRANS_ALL = str.maketrans("ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöüºª€$çÇñÑ ·.,;:()[]¡!¿?|%&*/\\\'\"@#",
                           "AEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouoaEDcCnN______________________aN")

_TRANS_MINI = str.maketrans(" \'\"",
                            "___")

RUTA_LOCAL = dadesdir + '/'
RUTA_DADES = os.path.abspath('Dades').replace('\\', '/') + '/'
CAMP_QVISTA = 'QVISTA_'

# def creaPlot(out, fRes):
#     pl = QvPlot.barres(out['RESULTAT'],out['DESCRIPCIO'],arxiu=fRes,horitzontal=True)
#     pl.write()

class QvMapificacio(QObject):
    """Clase que, a partir de un CSV con campos de dirección postal es capaz de:
       - Añadir a cada registro del CSV coordenadas y códigos de zona (distrito, barrio...)
         correspondientes a la dirección
       - Calcular una agregación a partir del código de zona para una posterior mapificación
    """

    def __init__(self, fDades: str, codi: str = '', separador: str = '',
                 prefixe: str = CAMP_QVISTA, numMostra: int = 60):
        """Abre y prepara el fichero CSV para la mapificación

        Arguments:
            fDades {str} -- Nombre del fichero CSV a tratar

        Keyword Arguments:
            codi {str} -- Codificación de los caracteres del CSV. Por defecto,
                          se infiere del fichero (default: {''})
            separador {str} -- Caracter separador de campos en el CSV. Por defecto,
                               se infiere del fichero (default: {''})
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
        self.direccionUnida = False
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
            items = self.mostraCols.split(self.separador)
            self.camps = [item.strip('"') for item in items]

    def infereixCodi(self) -> str:
        '''Infereix la codificació d'un arxiu csv
        Returns:
            codi{str} -- El codi inferit
        '''
        with open(self.fDades, "rb") as csvInput:
            buf = csvInput.read(10000)
        val = chardet.detect(buf)
        if val['encoding']=='ascii':
            # tant utf-8 com iso-8859-1 són compatibles amb ascii (és a dir, els primers 127 caràcters són els mateixos)
            # si detecta que utilitzem ascii, volem comprovar que realment és ascii i no un dels altres
            # Per comprovar-ho, iterem totes les línies, mirem si es pot convertir al format, i si no es pot l'eliminem de la llista
            with open(self.fDades,'rb') as csvInput:
                possibilitats=[
                    'ascii',
                    # la codificació que s'hauria d'utilitzar per tot
                    'utf-8',
                    # per defecte, quan s'importa d'excel a csv es desen en aquesta codificació
                    'iso-8859-1',
                    # superconjunt de l'iso-8859-1, afegint alguns caràcters com el €
                    'cp1252'
                ]
                for l in csvInput.readlines():
                    for p in possibilitats:
                        try:
                            l.decode(p)
                        except UnicodeDecodeError:
                            possibilitats.remove(p)
                    if len(possibilitats)==1:
                        return possibilitats[0]
                
                # si totes les línies es poden convertir a més d'una codificació, agafem la primera
                return possibilitats[0]
        return val['encoding']

    def infereixSeparador(self) -> str:
        '''Infereix el separador d'un arxiu csv
        Returns:
            separador{str} -- El separador inferit
        '''
        cont = collections.Counter()
        for linia in self.mostra:
            aux = linia.strip()
            aux = re.sub('"[^"]*"', '', aux)  # Elimina strings entre comillas dobles
            # aux = ''.join([i for i in aux if not i.isalnum()])  # Elimina caracteres alfanuméricos
            aux = ''.join([i for i in aux if i in (',',';','|','\t')])
            cont.update(aux)
        # Retornamos el caracter con más apariciones en total
        elems = cont.most_common(1)
        if len(elems) > 0:
            return elems[0][0]
        else:
            return ';'

    def verifCampsAdreca(self, camps: List[str]) -> bool:
        """ Verifica la lista de campos de dirección postal. Han de venir en este orden:
            (Tipus_via, *Nombre_via, *Número_inicial, Letra_inicial, Número_final, Letra_final)
            Los 2 campos precedidos por * son obligatorios, aunque el 2º es calculable desde el 1º
            
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
                if num == 2:  # Obligatorio
                    if camp is None or camp not in self.camps:
                        return False
                if num == 3:  # Obligatorio pero calculable
                    if camp is None or camp == '':
                        self.direccionUnida = True
                    elif camp is not None and camp != '' and camp not in self.camps:
                        return False
                else:  # Opcional
                    if camp is not None and camp != '' and camp not in self.camps:
                        return False
            return True
        except Exception:
            return False

    def valorCampAdreca(self, fila: dict, num: int) -> str:
        """ Retorna el valor de uno de los campos de la lista que componen la dirección postal.
        
        Arguments:
            fila {dict} -- Fila leída del CSV
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

    def calcValorsAdreca(self, fila: dict) -> List[str]:
        """ Retorna la lista de 6 valores que componen la dirección postal.
        
        Arguments:
            fila {dict} -- Fila leída del CSV
        
        Returns:
            List -- Valores de la dirección postal
        """
        try:
            valors = []
            for num in range(6): 
                if self.direccionUnida:
                    if num == 1: # Calcular calle por un lado y números por otro
                        calle, nums = QvNumPostal.separaDireccion(self.valorCampAdreca(fila, num))
                        valors.append(calle)
                        valors.append(nums)
                    elif num != 2:
                        valors.append(self.valorCampAdreca(fila, num))
                else:
                    valors.append(self.valorCampAdreca(fila, num))
            return valors
        except Exception:
            return []

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
            if zona not in mv.MAP_ZONES_COORD.keys():
                return False
            else:
                self.valZones.append(mv.MAP_ZONES_COORD[zona])
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
    errorAdreca = pyqtSignal(dict)  # Registro que no se pudo geocodificar
    filesGeocodificades = pyqtSignal(int, int)  # Número de líneas geocodificadas y número total

    # def asincGeocodificacio(self, campsAdreca: List[str], zones: List[str], fZones: str = '',
    #                         substituir: bool = True,
    #     percentatgeProces: pyqtSignal = None, procesAcabat: pyqtSignal = None,
    #                         errorAdreca: pyqtSignal = None) -> bool:
    #     """ Versión asíncrona de la función geocodificacio, con los mismos parámetros
    #     """
    #     from multiprocessing.pool import ThreadPool
    #     pool = ThreadPool(processes=1)

    #     async_result = pool.apply_async(self.geocodificacio, (campsAdreca, zones,
    #         fZones, substituir, percentatgeProces, procesAcabat, errorAdreca))
    #     return async_result.get()


    # def prueba_regex(self, txt, f=None):
    #     import re
    #     nombre = txt = txt.strip()
    #     nums = ''
    #     r = r"[0-9]+\s*[a-z|A-Z]?\s*\-+\s*[0-9]+\s*[a-z|A-Z]?$" # 2 nums. (con letra o no) separados por un guión
    #     s = re.search(r, txt)
    #     if s is None:
    #         r = r"[0-9]+\s*[a-z|A-Z]?$" # 1 número (con letra o no)
    #         s = re.search(r, txt)
    #     if s is not None:
    #         nombre = txt[0:s.span()[0]].strip()
    #         if nombre != '' and nombre[-1] == ',': # Eliminar coma separadora si la hay
    #             nombre = nombre[:-1].strip()
    #         nums = txt[s.span()[0]:].strip()
    #     if f:
    #         f.write(nombre + ' | ' + nums + '\n')
    #     else:
    #         print('*', nombre, '|' , nums)


    def geocodificacio(self, campsAdreca: List[str], zones: List[str], fZones: str = '',
                       substituir: bool = True, percentatgeProces: pyqtSignal = None,
                       procesAcabat: pyqtSignal = None, errorAdreca: pyqtSignal = None,
                       filesGeocodificades: pyqtSignal = None,
                       fCalcValorsAdreca: Callable[[dict], List[str]] = None) -> bool:
        """Añade coordenadas y códigos de zona a cada uno de los registros del CSV,
           a partir de los campos de dirección postal

        Arguments:
            campsAdreca {List[str]} -- Nombre de los campos que definen la dirección postal,
                                       en este orden: TipusVia, Variant, NumIni, LletraIni,
                                       NumFi, LletraFi (obligatorios 2º y 3º)
                                       (actúa junto a la función self.calcValorsAdreca siempre
                                       que no se suministre el parámetro fCalcValorsAdreca)
            zones List[str] -- Nombre de las zonas a añadir (ver MAP_ZONES_COORD en QvMapVars.py)
        
        Keyword Arguments:
            fZones {str} -- Nombre del fichero CSV de salida. Si no se indica, se usa el nombre
                            del fichero de entrada añadiendo el sufijo '_Geo' (default: {''})
            substituir {bool} -- En el caso de que el campo de código de zona ya exista y tenga 
                                 un valor, indica si se ha de sobreescribir o no (default: {True})
            percentatgeProces {pyqtSignal} -- Señal de progreso con el porcentaje transcurrido
                                              (default: {None})
            procesAcabat {pyqtSignal} -- Señal de finalización con tiempo transcurrido
                                         (default: {None})
            errorAdreca {pyqtSignal} -- Señal con registro erróneo (default: {None})
            filesGeocodificades {pyqtSignal} -- Señal de progreso con número de filas procesadas
                                                sobre el total (default: {None})
            fCalcValorsAdreca {Callable[[dict], List[str]]} -- función de cálculo de los 6 valores que
                                                               definen la dirección postal a partir de
                                                               cada fila del fichero CSV (default: {None})

        Returns:
            bool -- True si ha ido bien, False si hay errores o se canceló el proceso
                    (mensaje en self.msgError)

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

        # Se puede definir la dirección postal con los campos del csv indicados en el parámetro campsAdreca
        # o bien con los 6 valores calculados por la función fCalcValorsAdreca pasada como parámetro
        self.campsAdreca = campsAdreca
        self.direccionUnida = False
        if fCalcValorsAdreca is not None:
            self.fCalcValorsAdreca = fCalcValorsAdreca
        else:
            if not self.verifCampsAdreca(self.campsAdreca):
                self.msgError = "Error als camps d'adreça"
                return False
            self.fCalcValorsAdreca = self.calcValorsAdreca

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

        try:

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
                        campZona = QvSqlite().getAlias(campZona)
                        campSortida = self.prefixe + campZona
                        if campSortida not in self.camps:
                            self.camps.append(campSortida)
                            self.mostraCols += self.separador + campSortida
                    
                    writer = csv.DictWriter(csvOutput, delimiter=self.separador,
                                            fieldnames=self.camps, lineterminator='\n')
                    writer.writeheader()

                    # Lectura de filas y geocodificación
                    tot = num = 0
                    self.mostra = []

                    # f = open('D:/qVista/prueba_regex.txt', 'w')

                    for rowOrig in data:
                        tot += 1
                        # Normaliza nombres de campos
                        row = {self.netejaString(k): v for k, v in rowOrig.items()}
                        # Geocodificación
                        valors = self.fCalcValorsAdreca(rowOrig)

                        # self.prueba_regex(valors[1], f)

                        val = self.db.geoCampsCarrerNum(
                            self.campsZones,
                            valors[0], valors[1], valors[2], valors[3], valors[4], valors[5])
                        if val is None:
                            # Error en geocodificación
                            self.errorAdreca.emit(dict(rowOrig, **{'_fila': tot}))
                            num += 1
                        else:
                            # Resultado en campos
                            for campZona in self.campsZones:
                                campZona = QvSqlite().getAlias(campZona)
                                campSortida = self.prefixe + campZona
                                campNou = (campSortida not in row.keys())
                                if (campNou or self.substituir or
                                    row[campSortida] is None or row[campSortida] == ''):
                                    row.update([(campSortida, val[campZona])])
                        # Escritura de fila con campos
                        writer.writerow(row)

                        if self.numMostra >= tot:
                            self.mostra.append(self.separador.join(row.values()))

                        # Informe de progreso: filas y porcentaje
                        # (cada 1% o cada fila si hay menos de 100)
                        self.filesGeocodificades.emit(tot, self.files)
                        if self.files > 0 and tot % nSignal == 0:
                            self.percentatgeProces.emit(int(round(tot * 100 / self.files)))

                        # Cancelación del proceso via slot
                        if self.cancel:
                            break

                # f.close()

                fin = time.time()
                self.errors = num

                # Informe de fin de proceso y segundos transcurridos
                if self.cancel:
                    self.msgError = "Procés geocodificació cancel·lat"
                else:
                    self.files = tot
                    self.filesGeocodificades.emit(tot, self.files)
                    self.percentatgeProces.emit(100)
                self.procesAcabat.emit(round(fin - ini))

                return not self.cancel
                
        except Exception as e:
            self.msgError = "Error al geocodificar: " + str(e)
            return False

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
    #     select = "select round(I.AGREGAT " + dist + ", " + str(self.renderParams.numDecimals) + ")
    #        AS " + self.renderParams.campCalculat + \
    #        camps + " from Zona AS Z, " + \
    #       "(SELECT " + self.tipusAgregacio + " AS AGREGAT, " + self.campZona + " AS CODI " + \
    #       "FROM Info" + filtre + " GROUP BY " + self.campZona + ") AS I WHERE Z.CODI = I.CODI"
    #     return select

    def netejaString(self, txt: str, all: bool = False) -> str:
        """ Sustituye ciertos caracteres (de control, con acentos, etc) en un string.
        
        Arguments:
            txt {str} -- String a tratar
        
        Keyword Arguments:
            all {bool} -- Si es True, sustituye segín _TRANS_ALL; si no, utiliza _TRANS_MIN
                (default: {False})
        
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
        if self.zona is None or self.zona not in mv.MAP_ZONES.keys():
            return False
        else:
            self.valZona = mv.MAP_ZONES[self.zona]
        self.campZona = self.prefixe + QvSqlite().getAlias(self.valZona[0])
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

    def testExtensioArxiu(self, campExtensio):
        if PANDAS_ENABLED:
            import numpy as np
            import pandas as pd
        else:
            self.msgError = PANDAS_ERROR
            return False
        
        if campExtensio == '' or (campExtensio[0] == '<'):
            return False

        try:
            # El campo de extensión se carga como string
            campExt = CAMP_QVISTA + campExtensio
            dtypes = {campExt: np.string_}

            # Carga de capa de datos geocodificados
            csv = pd.read_csv(self.fZones, sep=self.separador, encoding='utf-8',
                              decimal=QvApp().locale.decimalPoint(), dtype=dtypes)
            cnt = csv[campExt].value_counts(normalize=True)
            if cnt.iloc[0] >= mv.MAP_FEQ_EXTENSIO:
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False

    def generaCapaGpd(self, nomCapa: str, tipusAgregacio: str, tipusDistribucio: str,
                      renderParams: QvMapRendererParams, campExtensio: str = '') -> bool:
        """ Calcula la agregación de datos, los cruza con el geopackage de zonas y genera la capa del mapa de coropletas.
        
        Arguments:
            nomCapa {str} -- Nombre de la capa del mapa
            tipusAgregacio {str} -- Tipo de agregación a aplicar
            tipusDistribucio {str} -- Tipo de distribución a aplicar
            renderParams {QvMapRendererParams} -- Parámetros de simbología

        Keyword Arguments:
            campExtensio {str} -- Nombre del campo que indica la extensión del mapa (default: {''})
        
        Returns:
            bool -- True si se generó la capa con el  mapa correctamente
        """
        if PANDAS_ENABLED:
            import numpy as np
            import pandas as pd
            import geopandas as gpd
        else:
            self.msgError = PANDAS_ERROR
            return False

        try:
            # Los campos de zona y extensión se cargan como string, y el de agregacion como float si hay acumulados
            dtypes = {self.campZona: np.string_}
            valExtensio = ''
            if campExtensio == '' or (campExtensio[0] == '<'):
                campExt = ''
                valExtensio = campExtensio
            else:
                campExt = CAMP_QVISTA + campExtensio
                if campExt != self.campZona:
                    dtypes.update({campExt: np.string_})
            if tipusAgregacio in ("Suma", "Mitjana"):
                if self.campAgregat == self.campZona or (campExt != '' and self.campAgregat == campExt):
                    self.msgError = "No és possible calcular aquesta agregació de dades.\n\nRevisi els paràmetres especificats."
                    return False
                dtypes.update({self.campAgregat: np.float_})

            # Carga de capa de datos geocodificados
            csv = pd.read_csv(self.fZones, sep=self.separador, encoding='utf-8',
                              decimal=QvApp().locale.decimalPoint(), dtype=dtypes)
            csv = csv[csv[self.campZona].notnull()]

            # Los campos de zona y extensión se cargan como string, y el de agregacion como float si hay acumulados
            dtypes = {self.campZona: np.string_}
            valExtensio = ''
            if campExtensio == '' or (campExtensio[0] == '<'):
                campExt = ''
                valExtensio = campExtensio
            else:
                campExt = CAMP_QVISTA + campExtensio
                if campExt != self.campZona:
                    dtypes.update({campExt: np.string_})
            if tipusAgregacio in ("Suma", "Mitjana"):
                if self.campAgregat == self.campZona or (campExt != '' and self.campAgregat == campExt):
                    self.msgError = "No és possible calcular aquesta agregació de dades.\n\nRevisi els paràmetres especificats."
                    return False
                dtypes.update({self.campAgregat: np.float_})

            # Carga de capa de datos geocodificados
            csv = pd.read_csv(self.fZones, sep=self.separador, encoding='utf-8',
                              decimal=QvApp().locale.decimalPoint(), dtype=dtypes)
            csv = csv[csv[self.campZona].notnull()]

            # Aplicar filtro
            try:
                if self.filtre != '':
                    csv.query(self.filtre, inplace=True)
            except Exception as err:
                self.msgError = "Error a l'expressió de filtre\n\n" + str(err)
                return False

            # Cálculo de la agreagación de datos
            if tipusAgregacio == "Cap":
                agreg = pd.Series(csv[self.campAgregat].values.round(renderParams.numDecimals), index=csv[self.campZona])
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
                agreg = csv.groupby(self.campZona)[self.campAgregat].sum().round(renderParams.numDecimals)
            elif tipusAgregacio == "Mitjana":
                agreg = csv.groupby(self.campZona)[self.campAgregat].mean().round(renderParams.numDecimals)
            else:
                self.msgError = "Tipus de agregació '{}' incorrecte.".format(tipusAgregacio)
                return False
            agreg.index.names = ['CODI']
            res = agreg.to_frame(name='RESULTAT')

            # Carga de capa base de zona
            self.fBase = RUTA_DADES + mv.MAP_ZONES_DB
            pols = gpd.read_file(self.fBase, driver="GPKG", layer=self.valZona[1], mode='r')
            if "AREA" in pols.columns:
                pols["AREA"] = pd.to_numeric(pols["AREA"]).round(3)
            if "POBLACIO" in pols.columns:
                pols["POBLACIO"] = pd.to_numeric(pols["POBLACIO"], downcast='integer', errors='coerce')

            # Aplicamos la extensión cuando el campo indicado contiene un valor predominante
            if campExt != '':
                cnt = csv[campExt].value_counts(normalize=True)
                if cnt.iloc[0] >= mv.MAP_FEQ_EXTENSIO:
                    if campExtensio == QvSqlite().getAlias(self.valZona[0]):
                        campExtensio = 'CODI'
                    valExtensio = cnt.index[0]
                    listExtensions = cnt.index.tolist()
                    pols = pols[pols[campExtensio].isin(listExtensions)]

            # Join
            join = pols.merge(res, on='CODI', how='left')
            if valExtensio == '' or valExtensio == '<ALL>':
                # Extension ciudad: ponemos a 0 todos los polígonos sin datos
                join['RESULTAT'].fillna(0, inplace=True)
            elif valExtensio == '<DATA>':
                # Extensión datos: solo poligonos con datos
                join = join[join['RESULTAT'].notnull()]
            else:
                # Extensión limitada: ponemos a 0 solo los polígonos de la zona predominante
                ext = join[join[campExtensio] == valExtensio]
                ext['RESULTAT'].fillna(0, inplace=True)
                resto = join[join[campExtensio] != valExtensio]
                resto = resto[resto['RESULTAT'].notnull()]
                join = pd.concat([ext, resto])

            # Aplicar distribución
            if self.tipusDistribucio == '':
                out = join
            else:
                # Filtrar elementos para evitar division por 0
                out = join[join[self.tipusDistribucio].notnull() & (join[self.tipusDistribucio] > 0)]
                out["RESULTAT"] = (out["RESULTAT"] / out[self.tipusDistribucio]).round(renderParams.numDecimals)
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
            out.to_file(self.fSQL, driver="GPKG", layer=nomCapa, overwrite=True)
            # gràfic
            # Aquí caldria comprovar si la regió utilitzada és un districte o un barri
            # if 'DESCRIPCIO' in out:
            #     creaPlot(out,self.fSQL)
            return True
        except Exception as err:
            self.msgError = "Error al calcular l'agregació de dades.\n\n" + str(err)
            return False

    def agregacio(self, llegenda, nomCapa: str, zona: str, tipusAgregacio: str,
                  renderParams: QvMapRendererParams, campAgregat: str = '', 
                  simple=True, tipusDistribucio: str = "Total",
                  campExtensio: str = mv.MAP_EXTENSIO, filtre: str = '',
                  veure: bool = True, form: QDialog = None) -> bool:
        """ Realiza la agragación de los datos por zona, la generación del mapa y su simbología.
        
        Arguments:
            llegenda {QvLlegenda} -- Leyenda
            nomCapa {str} -- Nombre de la capa del mapa a generar
            zona {str} -- Zona de agregación
            tipusAgregacio {str} -- Tipo de agregación
            renderParams {QvMapRendererParams} -- Parámetros de simbología
        
        Keyword Arguments:
            campAgregat {str} -- Campo que se utiliza en el cálculo de la agragación (default: {''})
            tipusDistribucio {str} -- Tipo de distribución (default: {"Total"})
            campExtensio {str} -- Nombre del campo que indica la extensión del mapa (default: {''})
            filtre {str} -- Expresión para filtrar los datos (default: {''})
            veure {bool} -- Si es True, añade la nueva capa con el mapa en la leyenda (default: {True})
            form {QDialog} -- Formulario desde donde se invoca la función (default: {None})
        
        Returns:
            bool -- False si hubo errores (mensaje de error en self.msgError)
        """

        if not PANDAS_ENABLED:
            self.msgError = PANDAS_ERROR
            return False

        self.fMapa = ''
        self.fSQL = ''
        self.llegenda = llegenda
        self.msgError = ''
        self.form = form
        self.descripcio = "Arxiu de dades: " + self.fZones + '\n' + \
            "Data: " +  QDate.currentDate().toString(QvApp().locale.dateFormat(QvApp().locale.ShortFormat)) + '\n' + \
            "Zona: " + zona + '\n' + \
            "Tipus d'agregació: " + tipusAgregacio + '\n' + \
            "Camp de càlcul: " + campAgregat
        if not simple:
            self.descripcio += '\n' + \
                "Filtre: " + filtre + '\n' + \
                "Distribució: " + tipusDistribucio

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

        if tipusAgregacio is None or tipusAgregacio not in mv.MAP_AGREGACIO.keys():
            self.msgError = "Error en tipusAgregacio"
            return False
        self.tipusAgregacio = mv.MAP_AGREGACIO[tipusAgregacio].format(self.campAgregat)

        if tipusDistribucio is None or tipusDistribucio not in mv.MAP_DISTRIBUCIO.keys():
            self.msgError = "Error en tipusDistribucio"
            return False
        self.tipusDistribucio = mv.MAP_DISTRIBUCIO[tipusDistribucio]

        self.filtre = filtre
        self.nomCapa = self.netejaString(nomCapa, True)

        # if not self.generaCapaQgis(nomCapa):
        #     return False

        if not self.generaCapaGpd(self.nomCapa, tipusAgregacio, tipusDistribucio,
                                  renderParams, campExtensio):
            return False

        # Carga capa de agregación
        mapLyr = QgsVectorLayer(self.fSQL, nomCapa, "ogr")
        mapLyr.setProviderEncoding("UTF-8")
        if not mapLyr.isValid():
            self.msgError = "No s'ha pogut carregar capa de agregació: " + self.fSQL
            return False

        # Renderer para mapificar
        mapRenderer = renderParams.mapRenderer(self.llegenda)
        self.renderer = mapRenderer.calcRender(mapLyr)
        if self.renderer is None:
            self.msgError = "No s'ha pogut elaborar el mapa"
            return False
        else:
            mapLyr.setRenderer(self.renderer)

        # Identificador de mapificación para qVista
        QgsExpressionContextUtils.setLayerVariable(mapLyr, mv.MAP_ID, self.descripcio)
        mapLyr.setDisplayExpression(renderParams.campCalculat)

        # Guarda simbología en GPKG
        err = self.llegenda.saveStyleToGeoPackage(mapLyr, mv.MAP_ID)
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

    class Test:
        def __init__(self):
            self.campsAdreca = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')

        def valorCampAdreca(self, fila: dict, num: int) -> str:
            try:
                camp = self.campsAdreca[num]
                if camp is None or camp == '':
                    return ''
                else:
                    return fila[camp]
            except Exception:
                return ''

        def userCalcValorsAdreca(self, fila: dict) -> List[str]:
            try:
                valors = []
                for num in range(6): 
                    valors.append(self.valorCampAdreca(fila, num))
                return valors
            except Exception:
                return []

        # def __init__(self, mapificacio):
        #     self.mapificacio = mapificacio

        # def userCalcValorsAdreca(self, fila: dict) -> List[str]:
        #     return self.mapificacio.calcValorsAdreca(fila)

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp
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

        # fCSV = 'D:/qVista/FME/CarrecsUTF8.csv'
        # fCSV = r"D:\qVista\F5_BCNPIC_LOG.csv"
        fCSV = r"D:\qVista\Geocod\mostra_dades_radars_ZBE_K.csv"

        z = QvMapificacio(fCSV)

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
        # campsAdreca = ('Tipus via', 'Carrer', 'Numero')
        # campsAdreca = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', '')
        # campsAdreca = ('', 'ADDRESS', '', '', '')
        # campsAdreca = ('', 'Codi carrer infracció', 'Num carrer infracció', '', '')
        campsAdreca = ('', 'Nom dispositiu', '', '', '')

        # zones = ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica", "Secció censal")
        zones = ('Coordenada', 'Districte')
        test = Test()
        ok = z.geocodificacio(campsAdreca, zones,
            percentatgeProces=lambda n: print('... Procesado', str(n), '% ...'),
            errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            procesAcabat=lambda n: print('Zonas', z.zones, 'procesadas en', str(n), 'segs. en ' + z.fZones + ' -', str(z.files), 'registros,', str(z.errors), 'errores')
            # ,fCalcValorsAdreca=test.userCalcValorsAdreca
        )
            
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



