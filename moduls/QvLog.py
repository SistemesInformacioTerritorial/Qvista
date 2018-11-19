# -*- coding: utf-8 -*-

from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from moduls.QvSingleton import Singleton
import getpass
import uuid

_DB_QVISTA = {
    'Database': 'QOCISPATIAL',
    'HostName': 'GEOPR1.imi.bcn',
    'Port': 1551,
    'DatabaseName': 'GEOPR1',
    'UserName': 'QVISTA_CONS',
    'Password': 'QVISTA_CONS'
}

class QvLog(Singleton):

    def __init__(self, family = 'QVISTA', logname = 'DESKTOP', dbLog = _DB_QVISTA):
        if hasattr(self, 'db'): # Solo se inicializa una vez
            return
        self.family = family.upper()
        self.logname = logname.upper()
        self.usuari = getpass.getuser().upper()
        self.db = self.connexio(dbLog)
        self.sessio = str(uuid.uuid1())
        self.query = QSqlQuery()

    def connexio(self, dbLog):
        db = QSqlDatabase.addDatabase(dbLog['Database'])
        if db.isValid():
            db.setHostName(dbLog['HostName'])
            db.setPort(dbLog['Port'])
            db.setDatabaseName(dbLog['DatabaseName'])
            db.setUserName(dbLog['UserName'])
            db.setPassword(dbLog['Password'])
            if db.open(): 
                return db
        return None

    def desconnexio(self):
        if self.db is None:
            return
        conName = self.db.connectionName()
        self.db.close()
        self.db = None
        QSqlDatabase.removeDatabase(conName)

    def registre(self, topic, params = None):
        if self.db is None or self.query is None:
            return False
        self.query.prepare("CALL QV_LOG_WRITE(:IDUSER, :IDSESSION, :FAMILY, :LOGNAME, :TOPIC, :PARAMS)")
        self.query.bindValue(':IDUSER', self.usuari)
        self.query.bindValue(':IDSESSION', self.sessio)
        self.query.bindValue(':FAMILY', self.family)
        self.query.bindValue(':LOGNAME', self.logname)
        self.query.bindValue(':TOPIC', topic)
        self.query.bindValue(':PARAMS', params)
        ok = self.query.exec_()
        return ok

    def inici(self):
        ok = self.registre('LOG_INICI')
        return ok

    def fi(self):
        ok = self.registre('LOG_FI')
        self.desconnexio()
        return ok

    def error(self):
        if self.db is None or self.query is None:
            return None
        else:
            return self.query.lastError().text()

if __name__ == "__main__":
    
    log = QvLog()   # Singleton
    ok = log.inici()
    if not ok:
        print('ERROR LOG >>', log.error())

    ok = log.registre('Capa1')
    ok = log.registre('Atributs')

    ###########

    log2 = QvLog()  # log2 equivale a log
    ok = log2.registre('Print', 'B/N;1:5000')
    ok = log2.registre('PDF', 'Color;1:1000')

    ###########

    ok = log.registre('Capa2')

    ok = log.fi()

