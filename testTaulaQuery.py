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
    if self.layerActiu.type() == QgsMapLayer.VectorLayer:
        fields = self.layerActiu.fields()
        for field in fields:
            # print(field.typeName())
            # if (field.typeName()!='String' and field.typeName()!='Date' and field.typeName()!='Date'):
            if (field.typeName()=='Real' or field.typeName()=='Integer64'):
                self.lwFieldsSelect.addItem(field.name())
    expressioCerca="NOM LIKE '%"+leEdit.text()+"'"
    if layer:
        layer.setSubsetString(expressioCerca)
        # expr = QgsExpression(expressioCerca)
        # it = layer.getFeatures( QgsFeatureRequest( expr ) )
        # ids = [i.id() for i in it]
def nouQuery():
    queryFile2=queryFile.format(param=leEdit.text())
    taula.setQuery(queryFile2)
with qgisapp() as app:
    projecteInicial = 'L:\DADES\SIT\PyQgis\Apl\MaSIP\QGIS\Finques de titularitat publica.qgs'
    canvas=QgsMapCanvas()
    canvas.show()
    leEdit = QLineEdit()
    leEdit.setText('ciutad')
    leEdit.show()
    leEdit.textChanged.connect(nouQuery)
    project = QgsProject().instance()
    root = project.layerTreeRoot()
    bridge =QgsLayerTreeMapCanvasBridge(root,canvas)
    canvas.show()

    # llegim un projecte de demo
    project.read(projecteInicial)
    canvas.zoomToFullExtent()
    db = connexio(dbConnexio)

    with open('d:/RECERCA_GENERAL.sql', 'r') as myfile:
        queryFile=myfile.read()
    queryFile2=queryFile.format(param=leEdit.text())
    print(queryFile2)
    taula = QvTaulaQuery(canvas, db, queryFile2)
    taula.show()    
    llegenda= QvLlegenda(canvas)
    llegenda.show()
    # boto.clicked.connect(redueix)
