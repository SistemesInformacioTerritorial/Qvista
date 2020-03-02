# -*- coding: utf-8 -*-

from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery, QSql
from qgis.PyQt.QtCore import QTranslator, QLibraryInfo, QLocale
from qgis.PyQt.QtNetwork import QNetworkProxy
from qgis.core import QgsPythonRunner
from moduls.QvSingleton import Singleton
from moduls.QvPythonRunner import QvPythonRunner
from moduls.QvGithub import QvGithub
from moduls.QvSqlite import QvSqlite
from PyQt5.QtWidgets import QApplication
from pathlib import Path
import sys
import getpass
import uuid
import os
import json


_PATH_PRO = 'N:\\SITEB\\APL\\PYQGIS\\QVISTA\\CODI\\'

_PATH_HELP = 'help/'

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

_PROXY = {
    'HostName': 'iprx.imi.bcn',
    'Port': 8080
}


def _fatalError(type, value, tb):
    QvApp().bugFatalError(type, value, tb)

#     error = repr(traceback.format_tb(tb))
#     error = error[-1000:]
#     print('ERROR -', error)
#     QvApp().logRegistre('LOG_ERROR', error[-1000:])


class QvApp(Singleton):

    def __init__(self):
        if hasattr(self, 'gh'):                     # Se inicializa una vez
            return

        self.gh = None
        self.ruta, self.rutaBase = self.calcRuta()  # Path de la aplicación
        self.cfg = self.readCfg()                   # Config de instalación
        val = self.paramCfg("Debug", "False")       # Errores no controlados
        if val != "True":
            sys.excepthook = _fatalError

        self.entorn = self.calcEntorn()             # 'DSV' o 'PRO'

        self.usuari = getpass.getuser().upper()     # Id de usuario
        self.sessio = str(uuid.uuid1())             # Id único de sesión

        self.intranet = self.calcIntranet()         # True si en la intranet
        self.dbQvista = _DB_QVISTA[self.entorn]     # Conexión Oracle entorno
        self.dbGeo = QvSqlite().dbGeoConnexio()     # Conexión Geocod SQlite

        self.proxy = self.setProxy()                # Establecer proxy

        val = self.paramCfg('Log', 'False')         # Activación log
        if val == 'True':
            self.log = True
        else:
            self.log = False

        val = self.paramCfg('Github', 'False')      # Establecer rama Github
        if val == 'False':
            self.github = None
        elif val == 'True':
            self.github = 'master'
        else:
            self.github = val

        if self.github is None:
            self.gh = None
        else:
            val = self.paramCfg('Id', '')
            self.gh = QvGithub(self.data(), self.github, val)

        val = self.paramCfg('Stdout', 'False')      # Activación fichero salida
        if val == 'True':
            try:
                # print(os.getcwd())
                sys.stdout = open('../Salida.txt', 'w')
            except Exception:
                print('Error al redirigir stdout')

        self.dbLog = None
        self.queryLog = None
        self.familyLog = None
        self.nameLog = None
        self.queryGeo = None
        self.appQgis = None
        self.idioma = None
        self.qtTranslator = None
        self.qgisTranslator = None
        self.locale = QLocale("ca-ES")

        QgsPythonRunner.setInstance(QvPythonRunner())   # Ejecuciones Python

    def data(self):
        txt = ''
        txt += 'Nom: ' + self.paramCfg('Nom', '???') + '\n'
        txt += 'Entorn: ' + self.entorn + '\n'
        txt += 'Branca: ' + self.github + '\n'
        txt += 'Intranet: ' + str(self.intranet) + '\n'
        txt += 'Usuari: ' + self.usuari + '\n'
        txt += 'Sessió: ' + self.sessio + '\n'
        txt += '___' + '\n'
        return txt

    def calcRuta(self):
        try:
            q1 = 'qVista/'
            q2 = 'Codi/'
            f = sys.argv[0]
            f = f.replace('\\', '/')
            fUp = f.upper()
            q = q1 + q2
            qUp = q.upper()
            n = fUp.find(qUp)
            if n >= 0:
                ruta = f[:n+len(q)]
                rutaBase = f[:n+len(q1)]
                return ruta, rutaBase
            else:
                return '', ''
        except Exception as err:
            self.bugException(err)
            return '', ''

    def readCfg(self):
        try:
            nom = 'install.cfg'
            fich = self.rutaBase + nom
            if not os.path.isfile(fich):
                fich = self.ruta + nom
            fp = open(fich, 'r', encoding='utf-8-sig')
            cfg = json.load(fp)
            fp.close()
            return cfg
        except Exception as err:
            self.bugException(err)
            return dict()

    def paramCfg(self, name, default):
        if hasattr(self, 'cfg') and self.cfg is not None:
            return self.cfg.get(name, default)
        else:
            return default

    def setProxy(self):
        try:
            val = self.paramCfg('Proxy', 'False')
            if self.intranet and val == 'True':
                proxy = QNetworkProxy()
                proxy.setType(QNetworkProxy.DefaultProxy)
                proxy.setHostName = _PROXY['HostName']
                proxy.setPort = _PROXY['Port']
                proxy.setApplicationProxy(proxy)
                return proxy
            else:
                return None
        except Exception as err:
            self.bugException(err)
            return None

    def calcEntorn(self):
        val = self.paramCfg('Producció', 'False')
        if val == 'True':
            return 'PRO'
        else:
            return 'DSV'

    def calcIntranet(self):
        return os.path.isdir(_PATH_PRO)

    def carregaIdioma(self, app, idioma='ca'):
        if app is None:
            return
        self.appQgis = app
        self.idioma = self.paramCfg('Idioma', idioma)
        self.qtTranslator = QTranslator()
        self.qgisTranslator = QTranslator()

        path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        self.qtTranslator.load("qt_" + idioma, path)
        app.installTranslator(self.qtTranslator)

        path = app.i18nPath()
        path = path.replace('/./', '/')
        self.qgisTranslator.load("qgis_" + idioma, path)
        app.installTranslator(self.qgisTranslator)

        self.locale = QLocale(self.idioma + "-ES")

    def llegirFitxerText(self, nomFich):
        try:
            txt = ''
            file = Path(nomFich)
            if file.is_file():
                #file.open()
                with file.open():
                    txt = file.read_text()
            return txt
        except Exception:
            return ''

    def carregaAjuda(self, objecte):
        try:
            nom = type(objecte).__name__
            if self.idioma is not None and self.idioma != '':
                nomFich = nom + '_' + self.idioma + '.html'
            else:
                nomFich = nom + '.html'
            txt = self.llegirFitxerText(_PATH_HELP + nomFich)
            if txt == '':
                txt = self.llegirFitxerText(_PATH_HELP + 'WorkInProgress.html')
            return txt
        except Exception as e:
            print(str(e))
            return ''
    def zoomFactor(self):
        #Windows per defecte utilitza un dpi de 96. Si hem aplicat un factor de zoom, serà més
        #Per tant, dividint entre 96 tindrem l'escalat en tant per 1
        return 1
        # zoomFactor=QApplication.desktop().screen().logicalDpiX()/96
        # return zoomFactor
    def nomUsuari(self):
        try:
            #Copia-pega de https://sjohannes.wordpress.com/2010/06/19/win32-python-getting-users-display-name-using-ctypes/
            #No sé per què va, però va
            import ctypes
            GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
            NameDisplay = 3

            size = ctypes.pointer(ctypes.c_ulong(0))
            GetUserNameEx(NameDisplay, None, size)

            nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
            GetUserNameEx(NameDisplay, nameBuffer, size)
            return nameBuffer.value
        except:
            print('Sembla que no estàs a Windows :D')
            #Si no funciona l'anterior, posem l'usuari del login
            return self.usuari
    # Metodos db QVISTA

    def dbLogConnexio(self):
        if not self.intranet:
            return
        try:
            if self.dbLog is None:
                db = QSqlDatabase.addDatabase(self.dbQvista['Database'], 'LOG')
                if db.isValid():
                    db.setHostName(self.dbQvista['HostName'])
                    db.setPort(self.dbQvista['Port'])
                    db.setDatabaseName(self.dbQvista['DatabaseName'])
                    db.setUserName(self.dbQvista['UserName'])
                    db.setPassword(self.dbQvista['Password'])
                    if db.open():
                        self.dbLog = db
        except Exception:
            self.dbLog = None

    def dbLogDesconnexio(self):
        if not self.intranet:
            return
        try:
            if self.dbLog is not None:
                conName = self.dbLog.connectionName()
                self.dbLog.close()
                self.dbLog = None
                QSqlDatabase.removeDatabase(conName)
        except Exception:
            self.dbLog = None

    # Metodos de LOG en Oracle

    def logInici(self, family='QVISTA', logname='DESKTOP', params=None):
        if not self.log:
            return False
        self.dbLogConnexio()
        if self.dbLog is None:
            return False
        self.familyLog = family.upper()
        self.nameLog = logname.upper()
        self.queryLog = QSqlQuery(self.dbLog)
        return self.logRegistre('LOG_INICI', params)

    def logRegistre(self, topic, params=None):
        if not self.log or self.dbLog is None or self.queryLog is None:
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
        except Exception:
            return False

    def logFi(self, params=None):
        ok = self.logRegistre('LOG_FI', params)
        self.dbLogDesconnexio()
        return ok

    def logError(self):
        if not self.log or self.dbLog is None or self.queryLog is None:
            return 'Log no actiu'
        try:
            return self.queryLog.lastError().text()
        except Exception:
            return None

    # Metodos de geocodificación

    def geocod(self, tipusVia, variant, codi, numIni, lletraIni='', numFi='', lletraFi=''):
        self.dbLogConnexio()
        if self.dbLog is None:
            return None, None
        if self.queryGeo is None:
            self.queryGeo = QSqlQuery(self.dbLog)
        try:
            self.queryGeo.prepare("CALL QV_GEOCOD(:TIPUSVIA, :VARIANTE, :CODIGO, " +
                                  ":NUMINI, :LETRAINI, :NUMFIN, :LETRAFIN, :X, :Y)")
            self.queryGeo.bindValue(':TIPUSVIA', tipusVia)
            self.queryGeo.bindValue(':VARIANTE', variant)
            self.queryGeo.bindValue(':CODIGO', codi)
            self.queryGeo.bindValue(':NUMINI', numIni)
            self.queryGeo.bindValue(':LETRAINI', lletraIni)
            self.queryGeo.bindValue(':NUMFIN', numFi)
            self.queryGeo.bindValue(':LETRAFIN', lletraFi)
            self.queryGeo.bindValue(':X', 0.0, QSql.Out)
            self.queryGeo.bindValue(':Y', 0.0, QSql.Out)
            ok = self.queryGeo.exec_()
            if ok:
                x = self.queryGeo.boundValue(':X')
                if not isinstance(x, float):
                    x = None
                y = self.queryGeo.boundValue(':Y')
                if not isinstance(y, float):
                    y = None
            return x, y
        except Exception:
            return None, None

    # Métodos de reporte de bugs con Github

    def bugUser(self, tit, desc):
        if self.gh is not None:
            return self.gh.postUser(tit, desc)
        else:
            return False

    def bugException(self, err):
        ok = False
        if self.gh is not None:
            ok = self.gh.reportBug()
        val = self.paramCfg('Debug', 'False')
        if val == 'True':
            raise err
        return ok

    def bugFatalError(self, type, value, tb):
        if self.gh is not None:
            return self.gh.reportBug(type, value, tb)
        else:
            return False


if __name__ == "__main__":

    print(sys.argv[0])

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        # print(QSqlDatabase.drivers())

        qApp = QvApp()                  # Singleton

        qApp.carregaIdioma(app, 'ca')   # Traductor

        x, y = qApp.geocod('C', 'Mallorca', None, '100')
        if x is not None:
            print('C', 'Mallorca', '100', str(x), str(y))
        x, y = qApp.geocod('Av', 'Diagonal', None, '220')
        if x is not None:
            print('Av', 'Diagonal', '220', str(x), str(y))
        x, y = qApp.geocod('', 'Msakjdaskjdlasdj', None, '220')
        if x is not None:
            print(str(x), str(y))

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

        aux = 3 / 0

        #
        # FIN LOG: Por evento si es un programa online, o por método si es un batch
        #
        if gui:
            app.aboutToQuit.connect(QvApp().logFi)
        else:
            QvApp().logFi()
