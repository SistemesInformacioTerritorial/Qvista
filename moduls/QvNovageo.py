# -*- coding: utf-8 -*-

from moduls.QvApp import QvApp
from moduls.QvSingleton import Singleton
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
import os

_DB_NOVAGEO = dict()

_DB_NOVAGEO['DSV'] = {
    'Database': 'QOCISPATIAL',
    'HostName': 'corpp1.imi.bcn',
    'Port': 1541,
    'DatabaseName': 'CORPP1',
    'UserName': 'SDR_GEOCOD_CONS',
    'Password': 'SDR_GEOCOD_CONS'
}

# _DB_NOVAGEO['PRO'] = {
#     'Database': 'QOCISPATIAL',
#     'HostName': 'corp1.imi.bcn',
#     'Port': 1521,
#     'DatabaseName': 'CORPR1',
#     'UserName': 'SDR_GEOCOD_CONS',
#     'Password': 'SDR_GEOCOD_CONS'
# }

class QvNovageo:

    app = QvApp()
    db = None
    
    @staticmethod
    def dbConnect(name='NOVAGEO'):
        if not QvNovageo.app.intranet:
            return False
        try:
            dbParams = _DB_NOVAGEO[QvNovageo.app.entorn]
            db = QSqlDatabase.addDatabase(dbParams['Database'], name)
            if db.isValid():
                db.setHostName(dbParams['HostName'])
                db.setPort(dbParams['Port'])
                db.setDatabaseName(dbParams['DatabaseName'])
                db.setUserName(dbParams['UserName'])
                db.setPassword(dbParams['Password'])
                if db.open():
                    QvNovageo.db = db
                    return True
            return False
        except Exception:
            QvNovageo.db = None
            return False

    @staticmethod
    def dbDisconnect():
        if not QvNovageo.app.intranet:
            return
        try:
            if QvNovageo.db is not None:
                name = QvNovageo.db.connectionName()
                QvNovageo.db.close()
                QvNovageo.db = None
                QSqlDatabase.removeDatabase(name)
        except Exception:
            QvNovageo.db = None


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp

    gui = False

    with qgisapp(guienabled=gui) as app:

        if QvNovageo.dbConnect():
            print(QvNovageo.db.connectionName())
            QvNovageo.dbDisconnect()
        else:
            print('No connection')

