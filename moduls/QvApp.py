# -*- coding: utf-8 -*-

from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from qgis.PyQt.QtCore import QTranslator, QLibraryInfo
from moduls.QvSingleton import Singleton
import sys
import getpass
import uuid

_DB_QVISTA = dict()

_DB_QVISTA['DSV'] = {
    'Database': 'QOCISPATIAL',
    'HostName': 'GEOPP1.imi.bcn',
    'Port': 1551,
    'DatabaseName': 'GEOPP1',
    'UserName': 'QVISTA_CONS',
    'Password': 'QVISTA_CONS'
}

_DB_QVISTA['PRO'] = {
    'Database': 'QOCISPATIAL',
    'HostName': 'GEOPR1.imi.bcn',
    'Port': 1551,
    'DatabaseName': 'GEOPR1',
    'UserName': 'QVISTA_CONS',
    'Password': 'QVISTA_CONS'
}

_PATH_PRO = 'N:\\SITEB\\APL\\PYQGIS\\'

class QvApp(Singleton):

    def __init__(self):
        if hasattr(self, 'entorn'): # Solo se inicializa una vez
            return
        self.entorn = self.calcEntorn()         # 'DSV' o 'PRO'
        self.dbQvista = _DB_QVISTA[self.entorn] # Conexión a Oracle según entorno
        self.usuari = getpass.getuser().upper() # Usuario de red
        self.sessio = str(uuid.uuid1())         # Id único de sesión
        self.dbLog = None
        self.queryLog = None
        self.familyLog = None
        self.nameLog = None
        self.appQgis = None
        self.idioma = None
        self.qtTranslator = None
        self.qgisTranslator = None

    def calcEntorn(self):
        entorn = 'DSV'
        if len(sys.argv) > 0:
            prog = sys.argv[0].upper()
            progL = len(sys.argv[0])
            path = _PATH_PRO.upper()
            pathL = len(_PATH_PRO)
            if progL > pathL:
                pref = prog[:pathL]
                if pref == path:
                    entorn = 'PRO'
        return entorn

    def carregaIdioma(self, app, idioma = 'ca'):
        if app is None:
            return
        self.appQgis = app
        self.idioma = idioma
        self.qtTranslator = QTranslator()
        self.qgisTranslator = QTranslator()

        path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        self.qtTranslator.load("qt_" + idioma, path)
        app.installTranslator(self.qtTranslator)

        path = app.i18nPath()
        path = path.replace('/./', '/')
        self.qgisTranslator.load("qgis_" + idioma, path)
        app.installTranslator(self.qgisTranslator)

    def logConnexio(self):
        try:
            db = QSqlDatabase.addDatabase(self.dbQvista['Database'])
            if db.isValid():
                db.setHostName(self.dbQvista['HostName'])
                db.setPort(self.dbQvista['Port'])
                db.setDatabaseName(self.dbQvista['DatabaseName'])
                db.setUserName(self.dbQvista['UserName'])
                db.setPassword(self.dbQvista['Password'])
                if db.open():
                    return db
            return None
        except:
            return None

    def logDesconnexio(self):
        if self.dbLog is None:
            return
        try:
            conName = self.dbLog.connectionName()
            self.dbLog.close()
            self.dbLog = None
            QSqlDatabase.removeDatabase(conName)
        except:
            return

    def logRegistre(self, topic, params = None):
        if self.dbLog is None or self.queryLog is None:
            return False
        try:
            self.queryLog.prepare("CALL QV_LOG_WRITE(:IDUSER, :IDSESSION, :FAMILY, :LOGNAME, :TOPIC, :PARAMS)")
            self.queryLog.bindValue(':IDUSER', self.usuari)
            self.queryLog.bindValue(':IDSESSION', self.sessio)
            self.queryLog.bindValue(':FAMILY', self.familyLog)
            self.queryLog.bindValue(':LOGNAME', self.nameLog)
            self.queryLog.bindValue(':TOPIC', topic)
            self.queryLog.bindValue(':PARAMS', params)
            ok = self.queryLog.exec_()
            return ok
        except:
            return False

    def logInici(self, family = 'QVISTA', logname = 'DESKTOP'):
        self.familyLog = family.upper()
        self.nameLog = logname.upper()
        self.dbLog = self.logConnexio()
        if self.dbLog is None:
            return False
        else:
            self.queryLog = QSqlQuery()
            return self.logRegistre('LOG_INICI')

    def logFi(self):
        ok = self.logRegistre('LOG_FI')
        self.logDesconnexio()
        return ok

    def logError(self):
        if self.dbLog is None or self.queryLog is None:
            return None
        try:
            return self.queryLog.lastError().text()
        except:
            return None

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled = gui) as app:

        print(QSqlDatabase.drivers())

        qApp = QvApp()                  # Singleton
        
        qApp.carregaIdioma(app, 'ca')   # Traductor

        #
        # INICIO LOG: Si logInici() retorna False, el resto de funciones de log no hacen nada
        #
        ok = qApp.logInici()            # Por defecto: family='QVISTA', logname='DESKTOP'
        if not ok:
            print('ERROR LOG >>', qApp.logError())

        ok = qApp.logRegistre('Capa1')
        ok = qApp.logRegistre('Atributs')

        ###########

        qApp2 = QvApp()  # qApp2 equivale a qApp
        ok = qApp2.logRegistre('Print', 'B/N;1:5000')
        ok = qApp2.logRegistre('PDF', 'Color;1:1000')

        ###########

        ok = QvApp().logRegistre('Capa2')

        #
        # FIN LOG: Por evento si es un programa online, o por método si es un batch
        #
        if gui:
            app.aboutToQuit.connect(QvApp().logFi)
        else:
            QvApp().logFi()


        
