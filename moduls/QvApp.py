# -*- coding: utf-8 -*-

from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from qgis.PyQt.QtCore import QTranslator, QLibraryInfo
from qgis.PyQt.QtNetwork import QNetworkProxy
from moduls.QvSingleton import Singleton
from pathlib import Path
import sys
import getpass
import uuid
import lib
import os

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

_PATH_PRO = ['N:\\SITEB\\APL\\PYQGIS\\']

_PATH_HELP = 'help/'

_PROXY = {
    'HostName': 'iprx.imi.bcn',
    'Port': 8080
}

def _fatalError(type, value, tb):    
    # QvApp().logRegistre('LOG_ERROR', traceback.print_tb(tb, limit=1000))
    print('Error:', type, value)

sys.excepthook = _fatalError

class QvApp(Singleton):

    def __init__(self):
        if hasattr(self, 'entorn'): # Solo se inicializa una vez
            return
        
        self.entorn = self.calcEntorn()         # 'DSV' o 'PRO'
        self.dbQvista = _DB_QVISTA[self.entorn] # Conexión a Oracle según entorno
        self.usuari = getpass.getuser().upper() # Usuario de red
        self.sessio = str(uuid.uuid1())         # Id único de sesión
        self.proxy = self.setProxy()
        self.dbLog = None
        self.queryLog = None
        self.familyLog = None
        self.nameLog = None
        self.appQgis = None
        self.idioma = None
        self.qtTranslator = None
        self.qgisTranslator = None

    def setProxy(self):
        try:
            if self.usuari is not None and len(self.usuari) > 0:
                proxy = QNetworkProxy()
                proxy.setType(QNetworkProxy.DefaultProxy)
                proxy.setHostName = _PROXY['HostName']
                proxy.setPort = _PROXY['Port']
                proxy.setApplicationProxy(proxy)
                return proxy
            else:
                return None
        except Exception as e:
            print(str(e))
            return None
        
    def calcEntorn(self):
        entorn = 'DSV'
        if len(sys.argv) > 0:
            for pathPro in _PATH_PRO:
                prog = sys.argv[0].upper()
                progL = len(sys.argv[0])
                path = pathPro.upper()
                pathL = len(pathPro)
                if progL > pathL:
                    pref = prog[:pathL]
                    if pref == path:
                        entorn = 'PRO'
                        break
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

    def llegirFitxerText(self, nomFich):
        try:
            txt = ''
            file = Path(nomFich)
            if file.is_file():
                file.open() 
                txt = file.read_text() 
            return txt
        except:
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

    # for param in os.environ.keys():
    #     print(param, '->', os.environ[param])

# ALLUSERSPROFILE -> C:\ProgramData
# APPDATA -> C:\Users\cpret\AppData\Roaming
# COMMONPROGRAMFILES -> C:\Program Files\Common Files
# COMMONPROGRAMFILES(X86) -> C:\Program Files (x86)\Common Files
# COMMONPROGRAMW6432 -> C:\Program Files\Common Files
# COMPUTERNAME -> DELL-CARLOS
# COMSPEC -> C:\WINDOWS\system32\cmd.exe
# DRIVERDATA -> C:\Windows\System32\Drivers\DriverData
# GDAL_DATA -> D:\QGIS34\share\gdal
# GDAL_DRIVER_PATH -> D:\QGIS34\bin\gdalplugins
# GDAL_FILENAME_IS_UTF8 -> YES
# GEOTIFF_CSV -> D:\QGIS34\share\epsg_csv
# HOMEDRIVE -> C:
# HOMEPATH -> \Users\cpret
# JAVA_HOME -> C:\Program Files (x86)\Java\jre1.8.0_91
# JPEGMEM -> 1000000
# LOCALAPPDATA -> C:\Users\cpret\AppData\Local
# LOGONSERVER -> \\DELL-CARLOS
# NUMBER_OF_PROCESSORS -> 4
# O4W_QT_BINARIES -> D:/QGIS34/apps/Qt5/bin
# O4W_QT_DOC -> D:/QGIS34/apps/Qt5/doc
# O4W_QT_HEADERS -> D:/QGIS34/apps/Qt5/include
# O4W_QT_LIBRARIES -> D:/QGIS34/apps/Qt5/lib
# O4W_QT_PLUGINS -> D:/QGIS34/apps/Qt5/plugins
# O4W_QT_PREFIX -> D:/QGIS34/apps/Qt5
# O4W_QT_TRANSLATIONS -> D:/QGIS34/apps/Qt5/translations
# ONEDRIVE -> C:\Users\cpret\OneDrive
# OS -> Windows_NT
# OSGEO4W_ROOT -> D:\QGIS34
# PATH -> D:\QGIS34\apps\qgis\bin;D:\QGIS34\apps\Python37;D:\QGIS34\apps\Python37\Scripts;D:\QGIS34\apps\qt5\bin;D:\QGIS34\apps\Python27\Scripts;D:\QGIS34\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\system32\WBem;D:\QGIS34\apps\Python37\lib\site-packages\pywin32_system32
# PATHEXT -> .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.CPL
# PROCESSOR_ARCHITECTURE -> AMD64
# PROCESSOR_IDENTIFIER -> Intel64 Family 6 Model 78 Stepping 3, GenuineIntel
# PROCESSOR_LEVEL -> 6
# PROCESSOR_REVISION -> 4e03
# PROGRAMDATA -> C:\ProgramData
# PROGRAMFILES -> C:\Program Files
# PROGRAMFILES(X86) -> C:\Program Files (x86)
# PROGRAMW6432 -> C:\Program Files
# PROJ_LIB -> D:\QGIS34\share\proj
# PROMPT -> $P$G
# PSMODULEPATH -> C:\Users\cpret\Documents\WindowsPowerShell\Modules;C:\Program Files\WindowsPowerShell\Modules;C:\WINDOWS\system32\WindowsPowerShell\v1.0\Modules
# PUBLIC -> C:\Users\Public
# PYTHONHOME -> D:\QGIS34\apps\Python37
# PYTHONIOENCODING -> UTF-8
# PYTHONPATH -> D:\QGIS34\apps\qgis\python;
# PYTHONUNBUFFERED -> 1
# QGIS_PREFIX_PATH -> D:/QGIS34/apps/qgis
# QT_PLUGIN_PATH -> D:\QGIS34\apps\qgis\qtplugins;D:\QGIS34\apps\qt5\plugins
# SESSIONNAME -> Console
# SYSTEMDRIVE -> C:
# SYSTEMROOT -> C:\WINDOWS
# TEMP -> C:\Users\cpret\AppData\Local\Temp
# TMP -> C:\Users\cpret\AppData\Local\Temp
# USERDOMAIN -> DELL-CARLOS
# USERDOMAIN_ROAMINGPROFILE -> DELL-CARLOS
# USERNAME -> cpret
# USERPROFILE -> C:\Users\cpret
# VSCODE_CWD -> C:\Program Files\Microsoft VS Code
# VSCODE_NODE_CACHED_DATA_DIR_14248 -> C:\Users\cpret\AppData\Roaming\Code\CachedData\1dfc5e557209371715f655691b1235b6b26a06be
# VSI_CACHE -> TRUE
# VSI_CACHE_SIZE -> 1000000
# WINDIR -> C:\WINDOWS
# TERM_PROGRAM -> vscode
# TERM_PROGRAM_VERSION -> 1.29.1
# LANG -> en_US.UTF-8

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


        
