# TODO Com fer invisible columna a partir de nom. Sabem: taula.setColumnHidden(column, True)
from importaciones import *
import  qgis.PyQt.QtSql

projecteInicial='../dades/projectes/BCN11_nord.qgs'

class QvTaulaQuery(QtWidgets.QWidget):

    def __init__(self, canvas, baseDeDades, strQuery):
        QtWidgets.QWidget.__init__(self)

        # Convertim els parametres del constructor en variable de la clase. Així ho fem accesible a la resta de funcions de la clase.
        
        self.canvas = canvas
        self.baseDeDades = baseDeDades
        self.strQuery = strQuery

        self.preparacio()

    def preparacio(self):    
        # db.open()
        self.baseDeDades.open()
        self.model = QtSql.QSqlQueryModel()
        self.model.setQuery(self.strQuery)
        
        titol = "Taula de prova"
        self.taula = QtWidgets.QTableView()
        self.taula.setModel(self.model)
        self.taula.setWindowTitle(titol)
        self.taula.doubleClicked.connect(self.pinta)

        for column in range(0,6):
            titol = self.model.record().fieldName(column)
            print(column, titol, titol[0:3])
            if titol[0:3] == 'qv_':
                self.view2.setColumnHidden(column,True)

        self.taula.show()

        # Exemple d'extracció de les dades a partir del index que s'obte de la fila columna
        # index = self.model.index(1, 1)
        # print(self.model.data(index))

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.taula)

        self.setWindowTitle("MeGAtAULOdON")
                      
    def setQuery(strQuery):
        self.model.setQuery(strQuery)

    def pinta(self,index):
        print(index.row(), index.column())
        # for idx in view2.selectionModel().selectedIndexes():
        #     index = model2.index(idx.row(), idx.column())
        #     print(idx.row(), idx.column())
        print(self.model.data(index))
        print(self.model.record(index.row()).fieldName(index.column()))
        print(self.model.record(index.row()).value("qv_X"), self.model2.record(index.row()).value("qv_Y"))
        x = float(self.model.record(index.row()).value("qv_X"))
        y = float(self.model.record(index.row()).value("qv_Y"))
        rang = QgsRectangle(qv_Xmin, qv_Ymin, qv_Xmax, qv_Ymax)

        # Canviem l'extensió del canvas segons el rang recien calculat.
        self.canvas.zoomToFeatureExtent(rang)


    
if __name__ == "__main__":
    with qgisapp():
        canvas = QgsMapCanvas()

        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge  =QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
        
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('sports6.db')
        db.open()
        query = QtSql.QSqlQuery()
        query.exec_("create table sportsmen(id int primary key, " "firstname varchar(20), lastname varchar(20))")
        query.exec_("insert into sportsmen values(1013, 'fRoger', 'Federer')")
        query.exec_("insert into sportsmen values(1023, 'fChristiano', 'Ronaldo')")
        query.exec_("insert into sportsmen values(1033, 'fUssain', 'Bolt')")
        query.exec_("insert into sportsmen values(1043, 'fSachin', 'Tendulkar')")
        query.exec_("insert into sportsmen values(1053, 'fSaina', 'Nehwal')")
        db.close()

        qvSv = QvTaulaQuery(canvas, db, "select * , 'hola' from sportsmen")
        qvSv.show()

        canvas.show()



   