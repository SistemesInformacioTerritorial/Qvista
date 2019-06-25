# -*- coding: utf-8 -*-
"""
Módulo de funciones de goecodificación de Oracle / SQLite
"""
from moduls.QvApp import QvApp
from moduls.QvSqlite import QvSqlite


class QvGeocod:
    """Clase con métodos estáticos para uso de la geocodificación con Oracle o SQLite
    """

    @staticmethod
    def coordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas de una dirección postal

        Arguments:
            tipusVia {str} -- Tipo de vía
            nomCarrer {str} -- Nombre o variante de la calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
        if QvApp().dbGeo is None:
            # LLamamos a rutinas GEOCOD de Oracle
            return QvApp().geocod(tipusVia, nomCarrer, '', numIni, lletraIni, numFi, lletraFi)
        else:
            # LLamamos a rutinas GEOCOD de SQLite
            return QvSqlite().geoCoordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni, numFi, lletraFi)

            # Comparativa Oracle / SQLite
            # x1, y1 = QvSqlite().geoCoordsCarrerNum(tipusVia, nomCarrer, numIni, lletraIni, numFi, lletraFi)
            # x2, y2 = QvApp().geocod(tipusVia, nomCarrer, '', numIni, lletraIni, numFi, lletraFi)
            # if x1 is None and x2 is not None:
            #     print('GEO - ORA =>', tipusVia, nomCarrer, numIni, lletraIni, numFi, lletraFi, x2, y2)
            # if x1 is not None and x2 is None:
            #     print('GEO - SLT =>', tipusVia, nomCarrer, numIni, lletraIni, numFi, lletraFi, x1, y1)
            # if x1 is not None and x2 is not None and (round(x1, 3) != round(x2, 3) or round(y1, 3) != round(y2, 3)):
            #     print('GEO - DIF =>', tipusVia, nomCarrer, numIni, lletraIni, numFi, lletraFi, x1, y1, x2, y2)
            # return x1, y1

    @staticmethod
    def coordsCodiNum(codiCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        """Retorna las coordenadas a partir de código de calle y número postal

        Arguments:
            codiCarrer {str} -- Código de calle
            numIni {str} -- Número postal (primero)

        Keyword Arguments:
            lletraIni {str} -- Letra del primer número postal (default: {''})
            numFi {str} -- Segundo número postal (default: {''})
            lletraFi {str} -- Letra del segundo número postal (default: {''})

        Returns:
            x, y -- Coordenadas en formato ETRS89, o None si no se encuentra
        """
        if QvApp().dbGeo is None:
            # LLamamos a rutinas GEOCOD de Oracle
            return QvApp().geocod('', '', codiCarrer, numIni, lletraIni, numFi, lletraFi)
        else:
            # LLamamos a rutinas GEOCOD de SQLite
            return QvSqlite().geoCoordsCodiNum(codiCarrer, numIni, lletraIni, numFi, lletraFi)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        import sys
        import csv
        import time
        # import locale

        # print(locale.getpreferredencoding())

# ************************** PRUEBA GOSSOS

        ini = time.time()

        ruta = '../'
        fich = 'GossosBCN'
        code = 'cp1252'
        tipo = 'NOM'

        # Fichero de salida de errores
        sys.stdout = open(ruta + fich + tipo + '_ERR.txt', 'w')
        print('*** FICHERO:', fich, 'por', tipo)

        # Fichero CSV de entrada
        with open(ruta + fich + '.csv', encoding=code) as csvInput:

            # Fichero CSV de salida con columnas X, Y extras
            with open(ruta + fich + tipo + '.csv', 'w', encoding=code) as csvOutput:

                # Cabeceras
                data = csv.DictReader(csvInput, delimiter=';')
                fields = data.fieldnames
                fields.append('X')
                fields.append('Y')

                writer = csv.DictWriter(csvOutput, fieldnames=fields, lineterminator='\n')
                writer.writeheader()

                # Lectura de filas y geocodificación
                tot = num = 0
                for row in data:
                    tot += 1
                    x, y = QvGeocod().coordsCarrerNum(row['Tipus de via'],
                                                      row['Via'],
                                                      row['Número'])
                    # Error en geocodificación
                    if x is None or y is None:
                        num += 1
                        print('- ERROR', '|', row['Identificador gos'],
                              row['Tipus de via'], row['Via'], row['Número'])

                    # Escritura de fila con X e Y
                    row.update([('X', x), ('Y', y)])
                    writer.writerow(row)

            fin = time.time()
            print('==> REGISTROS:', str(tot), '- ERRORES:', str(num))
            print('==> TIEMPO:', str(fin - ini), 'segundos')

        sys.exit(0)

# ************************** PRUEBA IMH

        # fich = 'CarrecsUTF8-100'
        # fich = 'CarrecsUTF8-100MIL'
        fich = 'CarrecsUTF8'

        tipo = 'CODI'
        # tipo = 'NOM'

        sys.stdout = open('../' + fich + tipo + '.txt', 'w')
        print('*** FICHERO:', fich, 'por', tipo)

        with open('../' + fich + '.csv', encoding='utf-8') as csvInput:

            data = csv.DictReader(csvInput, delimiter=';')
            tot = num = 0
            for row in data:
                tot += 1
                if tipo == 'CODI':
                    x, y = QvGeocod().coordsCodiNum(row['CODI_CARRER_GPL'],
                                                    row['NUM_I_GPL'], '',
                                                    row['NUM_F_GPL'], '')
                else:
                    x, y = QvGeocod().coordsCarrerNum('', row['NOM_CARRER_GPL'],
                                                      row['NUM_I_GPL'], '',
                                                      row['NUM_F_GPL'], '')
                if x is None or y is None:
                    num += 1
                    print('- ERROR', end='')
                else:
                    print('- COORDS x:', x, 'y:', y, end='')

                print(' |', row['NFIXE'], '-',
                      row['NOM_CARRER_GPL'], row['CODI_CARRER_GPL'],
                      row['NUM_I_GPL'], '-', row['NUM_F_GPL'])

            fin = time.time()
            print('==> REGISTROS:', str(tot), '- ERRORES:', str(num))
            print('==> TIEMPO:', str(fin - ini), 'segundos')

        sys.exit(0)

# *******************************************************************************

        x, y = QvGeocod().coordsCarrerNum('Av', 'BALMES', '61')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'BALMES', '61', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('C', 'BOLIVIA', '0')
        if x is None or y is None:
            print('No coords')
        else:
            print('C', 'BOLIVIA', '0', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('', 'Av. Xile', '')
        if x is None or y is None:
            print('No coords')
        else:
            print('', 'Av. Xile', '', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('Av', 'DE LES CORTS', '304')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'DE LES CORTS', '304', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('C', "D'EIXIMENIS", "28")
        if x is None or y is None:
            print('No coords')
        else:
            print('C', "D'EIXIMENIS", "28", str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum("Pg", "FONT D'EN FARGUES", "9")
        if x is None or y is None:
            print('No coords')
        else:
            print("Pg", "FONT D'EN FARGUES", "9", str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum("Pl", "DE L'AIRE", "6")
        if x is None or y is None:
            print('No coords')
        else:
            print("Pl", "DE L'AIRE", "6", str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum("Ptge", "d'Artemis", "15")
        if x is None or y is None:
            print('No coords')
        else:
            print("Ptge", "d'Artemis", "15", str(x), str(y))

#####################

        x, y = QvGeocod().coordsCarrerNum('Camí', 'ANGELS', '13')
        if x is None or y is None:
            print('No coords')
        else:
            print('Camí', 'ANGELS', '13', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('', 'Camí ANGELS', '13')
        if x is None or y is None:
            print('No coords')
        else:
            print('', 'Camí ANGELS', '13', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('C', 'Trav DE SANT ANTONI', '8')
        if x is None or y is None:
            print('No coords')
        else:
            print('C', 'Trav DE SANT ANTONI', '8', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('Av', 'JORDA', '12')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'JORDA', '12', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('Av', 'VALLCARCA', '159')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'VALLCARCA', '159', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('Camí', 'CAL NOTARI', '7')
        if x is None or y is None:
            print('No coords')
        else:
            print('Camí', 'CAL NOTARI', '7', str(x), str(y))

        x, y = QvGeocod().coordsCarrerNum('Can', 'ENRIC GRANADOS', '19')
        if x is None or y is None:
            print('No coords')
        else:
            print('Can', 'ENRIC GRANADOS', '19', str(x), str(y))

        x, y = QvApp().geocod('Pl', 'TIRANT LO BLANC', '',  '2')
        if x is None or y is None:
            print('No coords')
        else:
            print('ORACLE', 'Pl', 'TIRANT LO BLANC', '2', str(x), str(y))

        x, y = QvSqlite().geoCoordsCarrerNum('Pl', 'TIRANT LO BLANC', '2')
        if x is None or y is None:
            print('No coords')
        else:
            print('SQLite', 'Pl', 'TIRANT LO BLANC', '2', str(x), str(y))

        x, y = QvGeocod.coordsCodiNum('001808', '23', '', '25')
        if x is None or y is None:
            print('No coords')
        else:
            print('001808', '23', '25', str(x), str(y))

        x, y = QvGeocod.coordsCodiNum('003406', '132', 'B')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvGeocod.coordsCodiNum('dfadfadfadfadf', 'asdfadfad')
        if x is None or y is None:
            print('No coords')
        else:
            print('003406', '132', 'B', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('C', 'Mallorca', '100')
        if x is None or y is None:
            print('No coords')
        else:
            print('C', 'Mallorca', '100', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('', 'Balmes', '150')
        if x is None or y is None:
            print('No coords')
        else:
            print('Balmes', '150', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('Av', 'Diagonal', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '220', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('Av', 'Diagonal', '45', 'X')
        if x is None or y is None:
            print('No coords')
        else:
            print('Av', 'Diagonal', '45', 'X', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('', 'Msakjdaskjdlasdj', '220')
        if x is None or y is None:
            print('No coords')
        else:
            print('Msakjdaskjdlasdj', '220', str(x), str(y))

        x, y = QvGeocod.coordsCarrerNum('', 'Numancia', 'aa-87')
        if x is None or y is None:
            print('No coords')
        else:
            print('Numancia', 'aa-87', str(x), str(y))
