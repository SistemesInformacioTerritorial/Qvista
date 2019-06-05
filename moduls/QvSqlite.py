# -*- coding: utf-8 -*-

from moduls.QvSingleton import Singleton
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery, QSql
import os


class QvSqlite(Singleton):

    def __init__(self):
        if hasattr(self, 'db'):  # Se inicializa una vez
            return
        self.db = None
        self.query = None
        self.dbFile = r'Dades\Geocod.db'
        self.trans = str.maketrans('ÁÉÍÓÚáéíóúÀÈÌÒÙàèìòùÂÊÎÔÛâêîôûÄËÏÖÜäëïöü·ºª.',
                                   'AEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOUAEIOU.   ')

    def dbGeoConnexio(self):
        try:
            if self.db is None:
                if not os.path.exists(self.dbFile):
                    return None
                db = QSqlDatabase.addDatabase('QSQLITE', 'GEO')
                db.setDatabaseName(self.dbFile)
                db.setConnectOptions("QSQLITE_OPEN_READONLY")
                if db.isValid() and db.open():
                    self.db = db
                    self.query = QSqlQuery(self.db)
                    # ok = self.query.exec_("PRAGMA cache_size = 32768")
                    # ok = self.query.exec_("PRAGMA temp_store = MEMORY")
                else:
                    self.db = None
                    self.query = None
                return db
        except Exception:
            self.db = None
            self.query = None
            return None

    def dbGeoDesconnexio(self):
        try:
            if self.db is not None:
                if self.db.isOpen():
                    self.db.close()
                self.db = None
                self.query = None
        except Exception:
            self.db = None
            self.query = None

    def dbSelectValue(self, select, param):
        if self.db is None or param == '' or param is None:
            return ''
        try:
            select = select.format(param)
            if self.query.exec_(select) and self.query.next():
                txt = self.query.value(0)
                self.query.finish()
                return txt
            else:
                err = self.query.lastError().databaseText()
                self.query.finish()
                if err is not None and err != '':
                    print(err)
                return ''
        except Exception:
            err = self.query.lastError().databaseText()
            if err is not None and err != '':
                print(err)
            return ''

    def dbTipusVia(self, variant):
        select = "SELECT TIPUS_VIA FROM TipusVia WHERE VARIANT='{}'"
        return self.dbSelectValue(select, variant.strip().replace("'", "''"))

    def dbVariant(self, variant):
        select = "SELECT CODI FROM Variants WHERE VARIANT='{}'"
        return self.dbSelectValue(select, variant.strip().replace("'", "''"))

    def codiCarrerVariant(self, variant):
        if variant == '' or variant is None:
            return ''

        # Pasar a mayúsculas, eliminar acentos y otros caracteres, trim
        variant = variant.upper()
        variant = variant.translate(self.trans)
        variant = variant.strip()

        # Si no quedan caracteres, hemos terminado
        if variant == '':
            return ''

        # Eliminar espacions en blanco redundantes
        tmp = variant.replace('  ', ' ')
        while tmp != variant:
            variant = tmp
            tmp = variant.replace('  ', ' ')

        # Las variantes tienen como máximo 30 caracteres
        variant30 = variant[:30]

        # Si se encuentra la variante exacta, hemos terminado
        codi = self.dbVariant(variant30)
        if codi != '':
            return codi

        # Dividimos la variante en primera palabra y resto
        parte = variant.split(' ', 1)
        num = len(parte)

        if num > 1:
            tipus = self.dbTipusVia(parte[0])
            variant = parte[1]
        else:
            tipus = ''
            variant = parte[0]

        # Dividimos la variante en primera palabra, segunda y resto
        parte = variant.split(' ', 2)
        num = len(parte)

        # Busqueda y eliminación de partículas:
        # "DE", "DEL", "DELS", "D'EN", "D'", "DE L'", "DE LA", "DE LES", "DE LOS", "DE LAS"
        if num > 1:
            if parte[0] in ("DE", "DEL", "DELS", "D'EN", "D'"):
                if num == 3:
                    if parte[0] == "DE" and parte[1] in ("L'", "LA", "LES", "LOS", "LAS"):
                        variant = parte[2]
                    else:
                        variant = parte[1] + ' ' + parte[2]
                else:
                    variant = parte[1]

        # Búsqueda de tipo y variante, si hay tipo
        if tipus != '':
            tVariant = tipus.upper() + ' ' + variant
            tVariant = tVariant.strip()
            variant30 = tVariant[:30]
            codi = self.dbVariant(variant30)
            if codi != '':
                return codi

        # Búsqueda de variante limpia
        variant = variant.strip()
        variant30 = variant[:30]
        codi = self.dbVariant(variant30)
        if codi != '':
            return codi

    def formatNum(self, num):
        if num is None:
            return '0'
        num = num.strip()
        num = num.lstrip('0')
        if num == '':
            return '0'
        else:
            return num

    def coordsCarrerNum(self, codiCarrer, num):
        if self.db is None or num == '' or num is None or codiCarrer == '' or codiCarrer is None:
            return None, None
        try:
            select = "SELECT ETRS89_COORD_X, ETRS89_COORD_Y FROM Numeros WHERE \
                CODI = '{}' AND NUM_LLETRA_POST = '{}'"
            select = select.format(codiCarrer.strip(), num.strip())
            if self.query.exec_(select) and self.query.next():
                x = float(self.query.value(0))
                y = float(self.query.value(1))
                self.query.finish()
                return x, y
            else:
                err = self.query.lastError().databaseText()
                self.query.finish()
                if err is not None and err != '':
                    print(err)
                return None, None
        except Exception:
            err = self.query.lastError().databaseText()
            if err is not None and err != '':
                print(err)
            return None, None

    def coordsAdreca(self, variant, num=''):
        if variant == '' or variant is None:
            return None, None
        try:
            codi = self.codiCarrerVariant(variant)
            if codi == '':
                return None, None
            nums = num.split('-')
            nNums = len(nums)
            if nNums == 0:
                num = '0'
            else:
                num = self.formatNum(nums[0])
            x, y = self.coordsCarrerNum(codi, num)
            if x is not None and y is not None:
                return x, y
            if nNums > 1:
                num = self.formatNum(nums[1])
                return self.coordsCarrerNum(codi, num)
            else:
                return None, None
        except Exception:
            return None, None


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        sqlite = QvSqlite()

        sqlite.dbGeoConnexio()

        x, y = sqlite.coordsAdreca('C BAC DE RODA', '20')
        x, y = sqlite.coordsAdreca('Pg DEL TAULAT', '216')
        x, y = sqlite.coordsAdreca('Pg DE GARCIA FARIA', '77')
        x, y = sqlite.coordsAdreca('Pg DEL TAULAT', '238')

        x, y = sqlite.coordsAdreca('Carrer de Mallorca', '0025')
        x, y = sqlite.coordsAdreca('Calle Numancia', '0085 - 00089')
        x, y = sqlite.coordsAdreca('000180', 'kk-')

        txt = sqlite.codiCarrerVariant('Carrer de Mallorca')
        txt = sqlite.codiCarrerVariant('Carrer   Mallorca')
        txt = sqlite.codiCarrerVariant('DE MALLORCA')
        txt = sqlite.codiCarrerVariant('DE BALMES')
        txt = sqlite.codiCarrerVariant('BALMES')
        txt = sqlite.codiCarrerVariant(' Gran.     vía. de     les corts    catalanes  ')
        txt = sqlite.codiCarrerVariant('avda. dIAgONAL.')
        txt = sqlite.codiCarrerVariant('avenida diagonal')
        txt = sqlite.codiCarrerVariant('PALAU DE LA VIRREINA')
        txt = sqlite.codiCarrerVariant('191204')

        txt = sqlite.dbTipusVia('CALLE')
        txt = sqlite.dbTipusVia()
        txt = sqlite.dbTipusVia('AVENIDA')
        txt = sqlite.dbTipusVia('JARDIN')
        txt = sqlite.dbTipusVia('PLAZA')
        txt = sqlite.dbTipusVia('CALLEJON')

        sqlite.dbGeoDesconnexio()
