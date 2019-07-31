# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, pyqtSignal

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

class QvZonificacio(QObject):
    progres = pyqtSignal(int)

    def __init__(self, input, code='ANSI', delimiter=';'):
        super().__init__()
        self.input = input
        self.code = code
        self.delimiter = delimiter
        self.fields = []
        self.rows = 0
        self.inicio()

    def inicio(self):
        if not os.path.isfile(self.input):
            return
        with open(self.input, "r", encoding=self.code) as csvInput:
            lenFile = os.path.getsize(self.input)
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
            self.rows = int(lenFile // lenRow)

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
        print(z.rows, 'filas en', z.input)

        z = QvZonificacio('D:/qVista/CarrecsUTF8.csv', 'UTF-8')
        print(z.rows, 'filas en', z.input)

        z = QvZonificacio('D:/qVista/GossosBCN.csv')
        print(z.rows, 'filas en', z.input)
