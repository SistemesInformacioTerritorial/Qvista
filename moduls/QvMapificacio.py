# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal

from moduls.QvSqlite import QvSqlite

import os
import sys
import csv
import time

_ZONES = {
    "Codi postal": "DIST_POST",
    "Districte": "DISTRICTE",
    "Illa": "ILLA",
    "Solar": "SOLAR",
    "Barri": "BARRI",
    "Àrea estadística bàsica": "AEB",
    "Secció censal": "SECC_CENS",
    "Sector policial operatiu": "SPO"
}

class QvZonificacio(QObject):
    progres = pyqtSignal(int)

    def __init__(self, input, code='ANSI', delimiter=';'):
        super().__init__()
        self.input = input
        self.code = code
        self.delimiter = delimiter
        self.rows = 0
        self.fields = []
        self.inicio()

    def inicio(self):
        if not os.path.isfile(self.input):
            return
        with open(self.input, encoding=self.code) as csvInput:
            data = csv.DictReader(csvInput, delimiter=self.delimiter)
            self.fields = data.fieldnames
            tot = num = 0
            size = os.path.getsize(self.input)
            for row in data:
                num += 1
                tot += sys.getsizeof(row)
                if num == 10:
                    self.rows = (size * num) // tot
                    return

            # TODO: Método de cálculo de zonas de Geocod
            # TODO: Probar la geocodificación en una layer directamente

            # ini = time.time()

            # # Fichero de salida de errores
            # # sys.stdout = open(ruta + fich + '_ERR.txt', 'w')
            # print('*** FICHERO:', fich)

            # # Fichero CSV de entrada
            # with open(ruta + fich + '.csv', encoding=code) as csvInput:

            #     # Fichero CSV de salida con columna extra
            #     with open(ruta + fich + '_' + camp + '.csv', 'w', encoding=code) as csvOutput:

            #         # Cabeceras
            #         data = csv.DictReader(csvInput, delimiter=';')
            #         fields = data.fieldnames
            #         fields.append('QVISTA_' + camp)

            #         writer = csv.DictWriter(csvOutput, fieldnames=fields, lineterminator='\n')
            #         writer.writeheader()

            #         # Lectura de filas y geocodificación
            #         tot = num = 0
            #         dbgeo = QvSqlite()
            #         for row in data:
            #             tot += 1
            #             val = dbgeo.geoCampCarrerNum(camp, '', row['NOM_CARRER_GPL'], row['NUM_I_GPL'], '', row['NUM_F_GPL'], '')
            #             # Error en geocodificación
            #             if val is None:
            #                 num += 1
            #                 print('- ERROR', '|', row['NFIXE'], row['NOM_CARRER_GPL'], row['NUM_I_GPL'], '', row['NUM_F_GPL'])

            #             # Escritura de fila con X e Y
            #             row.update([('QVISTA_' + camp, val)])
            #             writer.writerow(row)

            #     fin = time.time()
            #     print('==> REGISTROS:', str(tot), '- ERRORES:', str(num))
            #     print('==> TIEMPO:', str(fin - ini), 'segundos')

            # print(QgsVectorDataProvider.availableEncodings())
            # ANSI / ISO-8859-1 / latin1
            # CP1252 /  windows-1252
            # UTF-8

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        z = QvZonificacio('D:/qVista/CarrecsANSI.csv')
        print(z.rows, 'filas en ', z.input)