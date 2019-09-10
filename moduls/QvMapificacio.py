# -*- coding: utf-8 -*-

from qgis.core import (QgsProject, QgsVectorLayer, QgsLayerDefinition, QgsVectorFileWriter,
                       QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange, QgsAggregateCalculator,
                       QgsGradientColorRamp, QgsRendererRangeLabelFormat, QgsReadWriteContext)
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtXml import QDomDocument

from moduls.QvSqlite import QvSqlite

import os
import sys
import csv
import time
import unicodedata

_ZONES = {
    # Nom: (Camp, Taula, Arxiu)
    "Codi postal": "CODI_POSTAL",
    "Districte": "DISTRICTE",
    "Illa": "ILLA",
    "Solar": "SOLAR",
    "Barri": ("BARRI", "Barris", "Barris.sqlite"),
    "Àrea estadística bàsica": "AEB",
    "Secció censal": "SECCIO_CENSAL",
    "Sector policial operatiu": "SPO"
}

_AGREGACIO = {
    "Nombre": "COUNT({})",
    "Nombre diferents": "COUNT(DISTINCT {})",
    "Suma": "SUM({})",
    "Mitjana": "AVG({})"
}

_DISTRIBUCIO = {
    "Total": "",
    "Per m2": "/ Z.AREA",
    "Per habitant": "/ Z.POBLACIO"
}

# _COLORS = {
#     "Blau": QColor(0, 128, 255),
#     "Taronja": QColor(255, 128, 0),
#     "Gris": QColor(128, 128, 128),
#     "Vermell" : QColor(255, 32, 32),
#     "Verd" : QColor(32, 160, 32),
#     "Groc" : QColor(255, 192, 0)
# }

class QvMapificacio(QObject):

    afegintZona = pyqtSignal(int)  # Porcentaje cubierto (0 - 100)
    zonaAfegida = pyqtSignal(int)  # Tiempo transcurrido (segundos)
    errorAdreca = pyqtSignal(dict) # Registro que no se pudo geocodificar

    def __init__(self, fDades, zona, campZona='', code='ANSI', delimiter=';', prefixe='QVISTA_', numMostra=60):
        super().__init__()
        self.fDades = fDades
        self.fZones = fDades
        self.zona = zona
        self.campZona = campZona
        self.code = code
        self.delimiter = delimiter
        self.prefixe = prefixe
        self.numMostra = numMostra
        self.mostra = []
        self.fields = []
        self.rows = 0
        self.errors = 0
        self.iniDades()
        self.db = QvSqlite()

    def iniDades(self):
        if not os.path.isfile(self.fDades):
            return

        if self.zona is None or self.zona not in _ZONES.keys():
            return
        else:
            self.valZona = _ZONES[self.zona]

        if self.campZona is None or self.campZona == '':
            self.campZona = self.prefixe + self.valZona[0]

        with open(self.fDades, "r", encoding=self.code) as csvInput:
            lenFile = os.path.getsize(self.fDades)
            data = csvInput.readline()
            self.fields = data.rstrip(csvInput.newlines).split(self.delimiter)
            lenMuestra = 0
            maxMuestra = self.numMostra
            self.mostra = []
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

    def verifCampsAdreca(self, camps):
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
    
    def valorCampAdreca(self, fila, num):
        try:
            camp = self.campsAdreca[num]
            if camp is None or camp == '':
                return ''
            else:
                return fila[camp]
        except Exception:
            return ''

    def zonificacio(self, campsAdreca=(), fZones='', substituir=True, afegintZona=None, zonaAfegida=None, errorAdreca=None):

        if self.verifCampsAdreca(campsAdreca):
            self.campsAdreca = campsAdreca
        else:
            return

        if fZones is None or fZones == '':
            splitFile = os.path.splitext(self.fDades)
            self.fZones = splitFile[0] + '_' + self.valZona[0] + splitFile[1]
        else:
            self.fZones = fZones

        self.substituir = substituir

        if self.rows >= 100:
            nSignal = int(round(self.rows / 100))
        else:
            nSignal = 1

        if afegintZona is not None:
            self.afegintZona.connect(afegintZona)
        if zonaAfegida is not None:
            self.zonaAfegida.connect(zonaAfegida)
        if errorAdreca is not None:
            self.errorAdreca.connect(errorAdreca)

        ini = time.time()

        # Fichero CSV de entrada
        with open(self.fDades, "r", encoding=self.code) as csvInput:

            # Fichero CSV de salida zonificado
            with open(self.fZones, "w", encoding=self.code) as csvOutput:

                # Cabeceras
                campoNuevo = False
                data = csv.DictReader(csvInput, delimiter=self.delimiter)
                if self.campZona not in self.fields:
                    self.fields.append(self.campZona)
                    campoNuevo = True

                writer = csv.DictWriter(csvOutput, delimiter=self.delimiter, fieldnames=self.fields, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y zonificación
                tot = num = 0
                for row in data:
                    tot += 1

                    if campoNuevo or self.substituir or row[self.campZona] is None or row[self.campZona] == '':
                        val = self.db.geoCampCarrerNum(self.valZona[0],
                              self.valorCampAdreca(row, 0), self.valorCampAdreca(row, 1), self.valorCampAdreca(row, 2),
                              self.valorCampAdreca(row, 3), self.valorCampAdreca(row, 4), self.valorCampAdreca(row, 5))
                        # Error en zonificación
                        if val is None:
                            self.errorAdreca.emit(dict(row))
                            num += 1
                        # Escritura de fila con campo
                        row.update([(self.campZona, val)])
                    
                    writer.writerow(row)
                    # Informe de progreso cada 1% o cada fila si hay menos de 100
                    if tot % nSignal == 0:
                        self.afegintZona.emit(int(round(tot * 100 / self.rows)))

            fin = time.time()
            self.rows = tot
            self.errors = num

            # Informe de fin de proceso y segundos transcurridos
            self.afegintZona.emit(100)
            self.zonaAfegida.emit(fin - ini)

    def prueba(self, ruta='D:/qVista/'):
        # Cargamos capa base de zona
        zonaLyr = QgsVectorLayer(ruta + 'Barris.sqlite', 'Zona', 'ogr')
        zonaLyr.setProviderEncoding("UTF-8")
        if zonaLyr.isValid():
            QgsProject.instance().addMapLayer(zonaLyr, False)

        # layers = QgsLayerDefinition.loadLayerDefinitionLayers(ruta + self.valZona + '.qlr')
        # QgsProject.instance().addMapLayers(layers, False)
        # zonaLyr = layers[0]

        # Cargamos capa de datos zonificados
        infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
        infoLyr.setProviderEncoding(self.code)
        if infoLyr.isValid():
            QgsProject.instance().addMapLayer(infoLyr, False)

        # mapLayer = QgsVectorLayer( "?query=select * from Zona Z, Info I where Z.codi = I." + self.campZona, "Mapificacio", "virtual" )

        vlayer = QgsVectorLayer("?query=select A.NOMBRE, Z.CODI, Z.DESCRIPCIO, Z.GEOMETRY as GEOM from Zona AS Z, "
            "(SELECT COUNT(*) AS NOMBRE, QVISTA_BARRI AS CODI FROM INFO GROUP BY QVISTA_BARRI) AS A "
            "WHERE Z.CODI = A.CODI",
            "Mapificacio", "virtual" )
        vlayer.setProviderEncoding("UTF-8")            

        if vlayer.isValid():
            QgsVectorFileWriter.writeAsVectorFormat(vlayer, ruta + "Mapificacio.sqlite", "UTF-8", zonaLyr.crs(), "SQLite")

            QgsProject.instance().removeMapLayer(zonaLyr.id())
            QgsProject.instance().removeMapLayer(infoLyr.id())

            mapLayer = QgsVectorLayer(ruta + "Mapificacio.sqlite", 'Mapificacio' , "ogr")
            mapLayer.setProviderEncoding("UTF-8")
            if mapLayer.isValid():

                numItems = 5
                numDecimals = 0
                iniAlpha = 8

                symbol = QgsSymbol.defaultSymbol(mapLayer.geometryType())
                colorRamp = QgsGradientColorRamp(QColor(0, 128, 255, iniAlpha),
                                                QColor(0, 128, 255, 255 - iniAlpha))
                format = QgsRendererRangeLabelFormat('%1 - %2', numDecimals)
                renderer = QgsGraduatedSymbolRenderer.createRenderer(mapLayer, "NOMBRE", numItems, 
                    QgsGraduatedSymbolRenderer.Pretty, symbol, colorRamp, format)

                mapLayer.setRenderer(renderer)
                domDoc = QgsLayerDefinition.exportLayerDefinitionLayers([mapLayer], QgsReadWriteContext())

                with open(ruta + 'Mapificacio.qlr', "w+", encoding="UTF-8") as qlr:
                    qlr.write(domDoc.toString())

                # layers = QgsLayerDefinition.loadLayerDefinitionLayers(ruta + self.valZona + '.qlr')
                # QgsProject.instance().addMapLayers(layers, True)
                layers = QgsLayerDefinition.loadLayerDefinitionLayers(ruta + 'Mapificacio.qlr')
                QgsProject.instance().addMapLayers(layers, True)

    def calcColors(self, colorBase, iniAlpha):
        colorIni = QColor(colorBase)
        colorIni.setAlpha(iniAlpha)
        colorFi = QColor(colorBase)
        colorFi.setAlpha(255 - iniAlpha)
        return colorIni, colorFi

    def calcRenderer(self, mapLyr, numCategories, format, colorBase, iniAlpha=8):
        colorIni, colorFi = self.calcColors(colorBase, iniAlpha)
        colorRamp = QgsGradientColorRamp(colorIni, colorFi)
        labelFormat = QgsRendererRangeLabelFormat(format, self.numDecimals)
        symbol = QgsSymbol.defaultSymbol(mapLyr.geometryType())
        renderer = QgsGraduatedSymbolRenderer.createRenderer(mapLyr, self.campCalculat, numCategories, 
            QgsGraduatedSymbolRenderer.Pretty, symbol, colorRamp, labelFormat)
        return renderer

    def calcSelect(self):
        select = "select round(I.AGREGAT " + self.tipusDistribucio + ", " + str(self.numDecimals) + ") AS " + self.campCalculat + ", " + \
                 "Z.CODI, Z.DESCRIPCIO, Z.AREA, Z.GEOMETRY as GEOM from Zona AS Z, " + \
                 "(SELECT " + self.tipusAgregacio + " AS AGREGAT, " + self.campZona + " AS CODI " + \
                 "FROM Info GROUP BY " + self.campZona + ") AS I WHERE Z.CODI = I.CODI"
        return select

    def agregacio(self, nomCapa, tipusAgregacio, campCalculat='RESULTAT', campAgregat='', tipusDistribucio="Total",
                  numDecimals=0, numCategories=5, colorBase=QColor(0, 128, 255), format='%1 - %2', veure=True):

        self.fMapa = ''

        if campAgregat is not None and campAgregat != '':
            self.campAgregat = campAgregat
        elif tipusAgregacio == 'Nombre' and campAgregat == '':
            self.campAgregat = '*'
        else:
            return

        if tipusAgregacio is None or tipusAgregacio not in _AGREGACIO.keys():
            return
        self.tipusAgregacio = _AGREGACIO[tipusAgregacio].format(self.campAgregat)

        if tipusDistribucio is None or tipusDistribucio not in _DISTRIBUCIO.keys():
            return
        self.tipusDistribucio = _DISTRIBUCIO[tipusDistribucio]

        self.campCalculat = campCalculat
        self.numDecimals = numDecimals
        nom = nomCapa.strip()
        nom = nom.replace(' ', '_')
        # nom = unicodedata.normalize('NFKD', nom) # .encode('UTF-8', 'ignore')
        self.nomCapa = nom
        rutaDades = 'Dades/'
        rutaMapes = 'C:/temp/qVista/temp/'

        # Carga de capa base de zona
        zonaLyr = QgsVectorLayer(rutaDades + self.valZona[2], 'Zona', 'ogr')
        zonaLyr.setProviderEncoding("UTF-8")
        if zonaLyr.isValid():
            QgsProject.instance().addMapLayer(zonaLyr, False)

        # Carga de capa de datos zonificados
        infoLyr = QgsVectorLayer(self.fZones, 'Info', 'ogr')
        infoLyr.setProviderEncoding(self.code)
        if infoLyr.isValid():
            QgsProject.instance().addMapLayer(infoLyr, False)

        # Creación de capa virtual que construye la agregación
        select = self.calcSelect()
        virtLyr = QgsVectorLayer("?query=" + select, self.nomCapa, "virtual")
        virtLyr.setProviderEncoding("UTF-8")            

        if virtLyr.isValid():
            # Guarda capa de agregación en SQLite
            QgsVectorFileWriter.writeAsVectorFormat(virtLyr, rutaMapes + self.nomCapa + ".sqlite", "UTF-8", zonaLyr.crs(), "SQLite")

            # Elimina capas de base y datos
            QgsProject.instance().removeMapLayer(zonaLyr.id())
            QgsProject.instance().removeMapLayer(infoLyr.id())

            # Carga capa SQLite de agregación
            mapLyr = QgsVectorLayer(rutaMapes + self.nomCapa + ".sqlite", nomCapa , "ogr")
            mapLyr.setProviderEncoding("UTF-8")
            if mapLyr.isValid():

                # Renderer para mapificar
                renderer = self.calcRenderer(mapLyr, numCategories, format, colorBase)
                mapLyr.setRenderer(renderer)

                # Guarda capa qlr con agregación + mapificación
                self.fMapa = rutaMapes + self.nomCapa + '.qlr'
                try:
                    domDoc = QgsLayerDefinition.exportLayerDefinitionLayers([mapLyr], QgsReadWriteContext())
                    with open(self.fMapa, "w+", encoding="UTF-8") as qlr:
                        qlr.write(domDoc.toString())
                except Exception:
                    self.fMapa = ''

                # Mostar qlr de mapificación, si es el caso
                if veure and self.fMapa != '':
                    layers = QgsLayerDefinition.loadLayerDefinitionLayers(self.fMapa)
                    QgsProject.instance().addMapLayers(layers, True)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()

        z = QvMapificacio('D:/qVista/CarrecsANSI.csv', 'Barri')
        print(z.rows, 'filas en', z.fDades)
        print('Muestra:', z.mostra)

        camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
        z.zonificacio(camps,
            afegintZona=lambda n: print('... Procesado', str(n), '% ...'),
            errorAdreca=lambda f: print('Fila sin geocodificar -', f),
            zonaAfegida=lambda n: print('Zona', z.zona, 'procesada en', str(n), 'segs. en ' + z.fZones + ' -', str(z.rows), 'registros,', str(z.errors), 'errores'))

        # zona = 'Barri'
        # camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL', '')
        # z.zonificacio(zona, camps)

        # exit(0)

        # z = QvZonificacio('D:/qVista/CarrecsUTF8.csv', 'UTF-8')
        # print(z.rows, 'filas en', z.fDades)

        # z = QvZonificacio('D:/qVista/GossosBCN.csv')
        # print(z.rows, 'filas en', z.fDades)
