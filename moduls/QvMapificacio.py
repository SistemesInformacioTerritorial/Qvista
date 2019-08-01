# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtGui import QColor

from moduls.QvSqlite import QvSqlite

import os
import sys
import csv
import time

_ZONES = {
    "Codi postal": "CODI_POSTAL",
    "Districte": "DISTRICTE",
    "Illa": "ILLA",
    "Solar": "SOLAR",
    "Barri": "BARRI",
    "Àrea estadística bàsica": "AEB",
    "Secció censal": "SECCIO_CENSAL",
    "Sector policial operatiu": "SPO"
}

_TIPUS = {
    "Nombre": "COUNT({})",
    "Nombre diferents": "COUNT(DISTINCT {})",
    "Suma": "SUM({})",
    "Mitjana": "AVG({})"
}

class QvMapificacio(QObject):

    afegintZona = pyqtSignal(int) # Porcentaje cubierto (0 - 100)
    zonaAfegida = pyqtSignal(int) # Tiempo transcurrido (segundos)

    def __init__(self, fDades, code='ANSI', delimiter=';'):
        super().__init__()
        self.fDades = fDades
        self.code = code
        self.delimiter = delimiter
        self.fields = []
        self.rows = 0
        self.iniDades()
        self.db = QvSqlite()
        self.zonificat = False

    def iniDades(self):
        if not os.path.isfile(self.fDades):
            return
        with open(self.fDades, "r", encoding=self.code) as csvInput:
            lenFile = os.path.getsize(self.fDades)
            data = csvInput.readline()
            self.fields = data.rstrip(csvInput.newlines).split(self.delimiter)
            lenMuestra = 0
            maxMuestra = 60
            num = 0
            for data in csvInput:
                num += 1
                data = data.encode(self.code)
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

    def zonificacio(self, zona, campsAdreca=(), fZones='', prefijo='QVISTA_', afegintZona=None, zonaAfegida=None):

        if zona is None or zona not in _ZONES.keys():
            return
        self.zona = _ZONES[zona]

        if not self.verifCampsAdreca(campsAdreca):
            return
        self.campsAdreca = campsAdreca

        if fZones is None or fZones == '':
            splitFile = os.path.splitext(self.fDades)
            self.fZones = splitFile[0] + '_' + self.zona + splitFile[1]
        else:
            self.fZones = fZones

        if self.rows >= 100:
            nSignal = int(round(self.rows / 100))
        else:
            nSignal = 1

        if afegintZona is not None:
            self.afegintZona.connect(afegintZona)
        if zonaAfegida is not None:
            self.zonaAfegida.connect(zonaAfegida)

        camp = prefijo + self.zona
        ini = time.time()

        # Fichero CSV de entrada
        with open(self.fDades, "r", encoding=self.code) as csvInput:

            # Fichero CSV de salida con columna extra
            with open(self.fZones, "w", encoding=self.code) as csvOutput:

                # Cabeceras
                data = csv.DictReader(csvInput, delimiter=self.delimiter)
                if camp not in self.fields:
                    self.fields.append(camp)

                writer = csv.DictWriter(csvOutput, delimiter=self.delimiter, fieldnames=self.fields, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y zonificación
                tot = num = 0
                for row in data:
                    tot += 1
                    val = self.db.geoCampCarrerNum(self.zona,
                        self.valorCampAdreca(row, 0), self.valorCampAdreca(row, 1), self.valorCampAdreca(row, 2),
                        self.valorCampAdreca(row, 3), self.valorCampAdreca(row, 4), self.valorCampAdreca(row, 5))
                    # Error en zonificación
                    if val is None:
                        num += 1
                    # Escritura de fila con campo
                    row.update([(camp, val)])
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
            self.zonificat = True

    def agregacio(self, tipus, camp, nomCapa, colorBase=QColor(0, 128, 255), numCategories=5):
        if not self.zonificat:
            return

        if tipus is None or tipus not in _TIPUS.keys():
            return
        self.tipus = _TIPUS[self.tipus].format(self.zona)

        if camp is not None and camp in self.fields:
            self.camp = camp


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()

        z = QvMapificacio('D:/qVista/CarrecsANSI.csv')
        print(z.rows, 'filas en', z.fDades)

        zona = 'Districte'
        camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL')
        z.zonificacio(zona, camps,
            afegintZona=lambda n: print('... Procesado', str(n), '% ...'),
            zonaAfegida=lambda n: print('Zona', zona, 'añadida en', str(n), 'segs. -', str(z.rows), 'registros,', str(z.errors), 'errores'))

        zona = 'Barri'
        camps = ('', 'NOM_CARRER_GPL', 'NUM_I_GPL', '', 'NUM_F_GPL', '')
        z.zonificacio(zona, camps)

        # exit(0)

        # z = QvZonificacio('D:/qVista/CarrecsUTF8.csv', 'UTF-8')
        # print(z.rows, 'filas en', z.fDades)

        # z = QvZonificacio('D:/qVista/GossosBCN.csv')
        # print(z.rows, 'filas en', z.fDades)
