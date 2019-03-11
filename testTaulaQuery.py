from moduls.QvImports import *
from moduls.QvTaulaQuery import QvTaulaQuery
from moduls.QvLlegenda import QvLlegenda
import qgis.PyQt.QtSql
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery

dbConnexio = {
    'Database': 'QOCISPATIAL',
    'HostName': 'GEOPR1.imi.bcn',
    'Port': 1551,
    'DatabaseName': 'GEOPR1',
    'UserName': 'QVISTA_CONS',
    'Password': 'QVISTA_CONS'
}


def connexio(dbConnexio):
    db = QSqlDatabase.addDatabase(dbConnexio['Database'])
    if db.isValid():
        db.setHostName(dbConnexio['HostName'])
        db.setPort(dbConnexio['Port'])
        db.setDatabaseName(dbConnexio['DatabaseName'])
        db.setUserName(dbConnexio['UserName'])
        db.setPassword(dbConnexio['Password'])
        if db.open(): 
            return db
    return None

def redueix():
    layer=llegenda.currentLayer()
    expressioCerca="NOM LIKE '%"+leEdit.text()+"%'"
    if layer:
        layer.setSubsetString(expressioCerca)
        expr = QgsExpression(expressioCerca)
        it = layer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [i.id() for i in it]
with qgisapp():
    projecteInicial = 'n:/siteb/apl/vistamecano/bimap/obres/mapaobres.qgs'
    canvas=QgsMapCanvas()
    canvas.show()
    leEdit = QLineEdit()
    leEdit.show()
    leEdit.editingFinished.connect(redueix)
    project = QgsProject().instance()
    root = project.layerTreeRoot()
    bridge =QgsLayerTreeMapCanvasBridge(root,canvas)
    canvas.show()

    # llegim un projecte de demo
    project.read(projecteInicial)
    db = connexio(dbConnexio)
    expWhere = "where ESTAT='PROJECTE'"
    taula = QvTaulaQuery(canvas, db, 'select * from obr_natura_obres'+' '+expWhere)
    taula.show()    
    llegenda= QvLlegenda(canvas)
    llegenda.show()
    # boto.clicked.connect(redueix)
