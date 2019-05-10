from moduls.QvImports import *
import  qgis.PyQt.QtSql
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery

projecteInicial='../dades/projectes/BCN11_nord.qgs'

class QvTaulaQuery(QWidget):
    """Un widget que mostra una taula generada a partir d'un query. 
    Si el resultat conté els camps qv_Xmin, qv_Ymin, qv_Xmax, qv_Ymax, un doble click situa el canvas sobre el rang.
        
        Arguments de creació:
            canvas {[QgsMapCanvas]} -- [el canvas associat]
            baseDeDades {[type]} -- [la connexió de base de dades]
            strQuery {[string]} -- [el query aplicat inicialment]
    """

    def __init__(self, canvas, baseDeDades, strQuery, amagarCoordenades = True):
        """Inicialització de la QvTaulaQuery
        
        Arguments:
            canvas {[QgsMapCanvas]} -- [el canvas associat]
            baseDeDades {[type]} -- [la connexió de base de dades]
            strQuery {[string]} -- [el query aplicat inicialment]
        """

        QWidget.__init__(self)
        
        self.setWindowTitle("Prueba SQLITE para Cercador")

        # Convertim els parametres del constructor en variable de la clase. Així ho fem accesible a la resta de funcions de la clase.
        self.canvas = canvas
        self.baseDeDades = baseDeDades
        self.strQuery = strQuery

        self.baseDeDades.open()

        # Instanciem el model sobre el que carreguerem el resultat del query (self.strQuery)
        self.model = QtSql.QSqlQueryModel()
        self.model.setQuery(self.strQuery)
        
        # Instanciem una TableView, li assignem el model i connectem el doble click a self.ajustarMapa
        self.taula = QTableView()
        self.taula.setModel(self.model)


        # # Amaguem les columnes amb camps qv_ (Poc pitonic, right now...)
        # for column in range(0,self.model.columnCount()):
        #     titol = self.model.record().fieldName(column)
        #     # print(column, titol, titol[0:3])
        #     if titol[0:3] == 'qv_':
        #         self.taula.setColumnHidden(column,amagarCoordenades)
        
        # Reajustem el tamany de la taula i la fem visible
        self.taula.resizeColumnsToContents()

        # Coloquem la taula sobre el layout del widget i la fem visible
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.taula)
        
        self.taula.show()

                      


        # Exemple d'extracció de les dades a partir del index que s'obte de la fila columna
        # fila = index.row()
        # columna = index.columna()
        # index = self.model.index(fila, columna)
        # print("Contingut de fila: {} columna: {} : {}".format(fila, columna, self.model.data(index))
  

        # Definim rectange de rang a partir de les coordenades llegides 
        # xMin = self.model.record(index.row()).value("qv_Xmin")
        # yMin = self.model.record(index.row()).value("qv_Ymin")
        # xMax = self.model.record(index.row()).value("qv_Xmax")
        # yMax = self.model.record(index.row()).value("qv_Ymax")
        # rang = QgsRectangle(xMin, yMin, xMax, yMax)

        # Canviem l'extensió del canvas segons el rang recien calculat.
        # self.canvas.zoomToFeatureExtent(rang)

    def setQuery(self,strQuery):
        """Assigna a la clase un nou query
        
        Arguments:
            strQuery {[string]} -- [El query assignat a la taula]
        """

        self.model.setQuery(strQuery)


# El que continua és un exemple d'ús de la classe QvTaulaQuery

# dbConnexio = {
#     'Database': 'QOCISPATIAL',
#     'HostName': 'GEOPR1.imi.bcn',
#     'Port': 1551,
#     'DatabaseName': 'GEOPR1',
#     'UserName': 'SIU_CONS',
#     'Password': 'SIU_CONS'
# }

# def connexio(dbConnexio):
#     db = QSqlDatabase.addDatabase(dbConnexio['Database'])
#     if db.isValid():
#         db.setHostName(dbConnexio['HostName'])
#         db.setPort(dbConnexio['Port'])
#         db.setDatabaseName(dbConnexio['DatabaseName'])
#         db.setUserName(dbConnexio['UserName'])
#         db.setPassword(dbConnexio['Password'])
#         if db.open(): 
#             return db
#     return None

if __name__ == "__main__":
    with qgisapp():
        canvas = QgsMapCanvas()

        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge  =QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
 
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('U:/QUOTA/Comu_imi/-JNB/para_qVista/buenas/prueba.db')
        db.open()
        codigo= "'000102'"
        mi_query= "select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros where codi =" + codigo
        taulaQuery = QvTaulaQuery(canvas, db, mi_query)

        taulaQuery.setGeometry(100,100, 450, 250)
        taulaQuery.show()
        canvas.setGeometry(100,400,450,400)
        canvas.show()


   