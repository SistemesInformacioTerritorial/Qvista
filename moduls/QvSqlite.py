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
        variant = variant.strip().upper().replace("'", "''")
        return self.dbSelectValue(select, variant)

    def dbVariant(self, variant):
        select = "SELECT CODI FROM Variants WHERE VARIANT='{}'"
        variant = variant.strip().upper().replace("'", "''")
        variant = variant[:30]
        return self.dbSelectValue(select, variant)

    def dbTipusVariant(self, tipusVia, variant):
        tipusVia = tipusVia.strip().upper()
        if tipusVia == '':
            codi = self.dbVariant(variant)
        else:
            if tipusVia == 'C':
                codi = self.dbVariant(variant)
            else:
                codi = self.dbVariant(self.netejaString(tipusVia) + ' ' + variant)
        return codi

    def netejaString(self, txt):
        # Pasar a mayúsculas, eliminar acentos y otros caracteres, trim
        txt = txt.upper()
        txt = txt.translate(self.trans)
        txt = txt.strip()

        # Eliminar espacios en blanco redundantes
        tmp = txt.replace('  ', ' ')
        while tmp != txt:
            txt = tmp
            tmp = txt.replace('  ', ' ')

        return txt

    def senseParticules(self, txt):
        # Busqueda y eliminación de partículas (prefijos)
        lista = ("DE L'", "DE LA ", "DE LES ", "DE LOS ", "DE LAS ", "DE ", "DEL ", "DELS ", "D'EN ", "D'")
        for particula in lista:
            n = len(particula)
            if particula == txt[:n]:
                txt = txt[n:]
                return txt.lstrip()
        return txt

    def codiCarrerVariant(self, tipusVia, variant):
        if variant == '' or variant is None:
            return ''

        variant = self.netejaString(variant)
        if variant == '':
            return ''

        if tipusVia == '' or tipusVia is None:
            tipusVia = ''
        else:
            tipusVia = self.dbTipusVia(tipusVia)

        codi = self.dbTipusVariant(tipusVia, variant)
        if codi == '':
            v = self.senseParticules(variant)
            if v != variant:
                variant = v
                codi = self.dbTipusVariant(tipusVia, variant)
            if codi == '':
                parte = variant.split(' ', 1)
                num = len(parte)
                if num > 1:
                    tipus = self.dbTipusVia(parte[0])
                    if tipus != '':
                        variant = self.senseParticules(parte[1])
                        codi = self.dbTipusVariant(tipus, variant)
                        if codi == '':
                            codi = self.dbTipusVariant(tipusVia, parte[0] + ' ' + variant)
                        if codi == '' and tipusVia != tipus:
                            codi = self.dbTipusVariant(tipusVia, variant)
                else:
                    if tipusVia != 'C':
                        codi = self.dbTipusVariant('', variant)

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
        if self.db is None or codiCarrer is None or codiCarrer == '' or num is None or num == '' or num == '0':
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

    def coordsAdreca(self, tipusVia, variant, num=''):
        if variant == '' or variant is None:
            return None, None
        try:
            codi = self.codiCarrerVariant(tipusVia, variant)
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

    def geoCoordsCarrerNum(self, tipusVia, variant, numIni, lletraIni='', numFi='', lletraFi=''):
        # Verificamos si hay número final / letra final para añadirlos
        if numFi == '' and lletraFi == '':
            num2 = ''
        else:
            num2 = '-' + numFi + lletraFi
        return self.coordsAdreca(tipusVia, variant, numIni + lletraIni + num2)

    def geoCoordsCodiNum(self, codiCarrer, numIni, lletraIni='', numFi='', lletraFi=''):
        # Buscamos número / letra inicial en Ge<ocod de SQLite
        num1 = self.formatNum(numIni) + lletraIni.strip().upper()
        x, y = self.coordsCarrerNum(codiCarrer, num1)
        if x is not None and y is not None:
            return x, y
        else:
            # Si no, buscamos número / letra finales en  Geocod de SQLite
            num2 = self.formatNum(numFi) + lletraFi.strip().upper()
            if num2 != num1:
                return self.coordsCarrerNum(codiCarrer, num2)
            else:
                return None, None


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        sqlite = QvSqlite()

        sqlite.dbGeoConnexio()

        x, y = sqlite.coordsAdreca('', 'C RIBAS', '19')
        x, y = sqlite.coordsAdreca('C', 'RIBAS', '19')

        x, y = sqlite.coordsAdreca('', 'C BAC DE RODA', '20')
        x, y = sqlite.coordsAdreca('', 'Pg DEL TAULAT', '216')
        x, y = sqlite.coordsAdreca('', 'Pg DE GARCIA FARIA', '77')
        x, y = sqlite.coordsAdreca('', 'Pg DEL TAULAT', '238')

        x, y = sqlite.coordsAdreca('', 'Carrer de Mallorca', '0025')
        x, y = sqlite.coordsAdreca('', 'Calle Numancia', '0085 - 00089')
        x, y = sqlite.coordsAdreca('', '000180', 'kk-')

        txt = sqlite.codiCarrerVariant('', 'Carrer de Mallorca')
        txt = sqlite.codiCarrerVariant('', 'Carrer   Mallorca')
        txt = sqlite.codiCarrerVariant('', 'DE MALLORCA')
        txt = sqlite.codiCarrerVariant('', 'DE BALMES')
        txt = sqlite.codiCarrerVariant('', 'BALMES')
        txt = sqlite.codiCarrerVariant('', ' Gran.     vía. de     les corts    catalanes  ')
        txt = sqlite.codiCarrerVariant('', 'avda. dIAgONAL.')
        txt = sqlite.codiCarrerVariant('', 'avenida diagonal')
        txt = sqlite.codiCarrerVariant('', 'PALAU DE LA VIRREINA')
        txt = sqlite.codiCarrerVariant('', '191204')

        txt = sqlite.dbTipusVia('CALLE')
        txt = sqlite.dbTipusVia('AVENIDA')
        txt = sqlite.dbTipusVia('JARDIN')
        txt = sqlite.dbTipusVia('PLAZA')
        txt = sqlite.dbTipusVia('CALLEJON')

        sqlite.dbGeoDesconnexio()
