import sys
from PyQt5.QtSql import *
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, \
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLineEdit, QLabel, QGridLayout

# Creamos la clase que heredara métodos y componentes de QWidget
class PYQT_BD(QWidget):
    def __init__(self, parent=None):
        super(PYQT_BD, self).__init__(parent)

        # Creamos una tabla en donde organizaremos los datos
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['codi', 'num_letra_post', 'etrs89_coord_x','etrs89_coord_y','num_oficial']) # Tabla con 5 columnas
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        self.lblCodi = QLabel("CODI:") # Campo de texto para 
        self.txtCodi = QLineEdit()
        self.txtCodi.setPlaceholderText("-----")

        self.lblNum_Lletra_Post = QLabel("NUM_LLETRA_POST:") # Campo de texto 
        self.txtNum_Lletra_Post = QLineEdit()
        self.txtNum_Lletra_Post.setPlaceholderText("-----")

        self.lblEtrs89_Coord_X = QLabel("ETRS89_COORD_X:") # Campo de texto 
        self.txtEtrs89_Coord_X = QLineEdit()
        self.txtEtrs89_Coord_X.setPlaceholderText("-----")

        self.lblEtrs89_Coord_Y = QLabel("ETRS89_COORD_Y:") # Campo de texto 
        self.txtEtrs89_Coord_Y = QLineEdit()
        self.txtEtrs89_Coord_Y.setPlaceholderText("-----")

        self.lblNum_Oficial = QLabel("NUM_OFICIAL:") # Campo de texto 
        self.txtNum_Oficial = QLineEdit()
        self.txtNum_Oficial.setPlaceholderText("-----")

        

        grid = QGridLayout() # Declaramo sun gridlayout en donde ingresaremos todos los widget
        grid.addWidget(self.lblCodi, 0, 0)
        grid.addWidget(self.txtCodi, 0, 1)

        grid.addWidget(self.lblNum_Lletra_Post, 1, 0)
        grid.addWidget(self.txtNum_Lletra_Post, 1, 1)
        
        grid.addWidget(self.lblEtrs89_Coord_X, 2, 0)
        grid.addWidget(self.txtEtrs89_Coord_X, 2, 1)

        grid.addWidget(self.lblEtrs89_Coord_Y, 3, 0)
        grid.addWidget(self.txtEtrs89_Coord_Y, 3, 1)

        grid.addWidget(self.lblNum_Oficial, 4, 0)
        grid.addWidget(self.txtNum_Oficial, 4, 1)        

        btnCargar = QPushButton('Cargar Datos') # Boton para cargar y mostrar los datos
        btnCargar.clicked.connect(self.cargarDatos) # función al hacer click sobre el boton

        btnInsertar = QPushButton('Insertar') # Boton agregar datos
        btnInsertar.clicked.connect(self.insertarDatos) # función al hacer click sobre el boton

        btnEliminar = QPushButton('Eliminar') # Boton para eliminar datos
        btnEliminar.clicked.connect(self.eliminarDatos)

        hbx = QHBoxLayout() # Declaramos un QHBoxLayout
        # Agregamos los elementos al layout
        hbx.addWidget(btnCargar)
        hbx.addWidget(btnInsertar)
        hbx.addWidget(btnEliminar)

        vbx = QVBoxLayout()
        vbx.addLayout(grid)
        vbx.addLayout(hbx)
        vbx.setAlignment(Qt.AlignTop)
        vbx.addWidget(self.table)

        self.setWindowTitle("PyQT - Base de datos (SQLite)") # Titulo de la ventana
        self.resize(600, 1000) # Tamaño de la ventana
        self.setLayout(vbx) # Layout de la ventana

        # Método para agregar datos a la base de datos
    def cargarDatos(self, event):
        index = 0
        query = QSqlQuery() # Intancia del Query
        # Ejecutamos el query "select * from personas"
        # El cual nos devolvera todos los datos d ela tabla "personas"
        query.exec_("select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros where codi = '000102'") 
        # query.exec_("select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros") 

        # Iteramos los datos recividos
        while query.next():
            codi = query.value(0) # Codigo calle
            num_lletra_post = query.value(1) # Numero y Letra
            etrs89_coord_x = query.value(2) # coor x
            etrs89_coord_y = query.value(3) # coor y
            num_oficial = query.value(4) # numero oficial


            # Ahora organizamos los datos en la tabla creada anteriormente
            self.table.setRowCount(index + 1)
            self.table.setItem(index, 0, QTableWidgetItem(str(codi)))
            self.table.setItem(index, 1, QTableWidgetItem(num_lletra_post))
            self.table.setItem(index, 2, QTableWidgetItem(etrs89_coord_x))
            self.table.setItem(index, 3, QTableWidgetItem(etrs89_coord_y))
            self.table.setItem(index, 4, QTableWidgetItem(num_oficial))            

            index += 1

    # Método para insertar datos en la base de datos
    def insertarDatos(self, event): 
        # Obtenemos los valores de los campos de texto

        # codi  = int(self.txtCodi.text())
        codi  = self.txtCodi.text()
        num_lletra_post = self.txtNum_Lletra_Post.text()
        etrs89_coord_x =  self.txtEtrs89_Coord_X.text()
        etrs89_coord_y =  self.txtEtrs89_Coord_Y.text()
        num_oficial    =  self.txtNum_Oficial.text()



        query = QSqlQuery() # Instancia de Query
        # Ejecutamos una sentencia para insertar los datos 
        # De los campos de texto
        try:
            query.exec_("insert into Numeros values('{0}', '{1}', '{2}','{3}','{4}')".format(codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial))
        except Exception as ee:

            print(str(ee))

   

        # Mpetodo para eliminar datos d ela base de datos
    def eliminarDatos(self, event):
        # select = fila seleccionada en la tabla
        selected = self.table.currentIndex()
        if not selected.isValid() or len(self.table.selectedItems()) < 1:
            return

        ids = self.table.selectedItems()[0] # valor de tabla
        query = QSqlQuery() # instancia de Query
        # Ejecutamos una sentencia. Eliminara toda fila cuyo
        # Valor de id sea igual al seleccionado
        linea= "delete from Numeros where codi = '" + self.txtCodi.text() +"'"
        query.exec_(linea)

        self.table.removeRow(selected.row()) # Removemos la fila
        self.table.setCurrentIndex(QModelIndex())

        # Método para crear la base de datos
    def db_connect(self, filename, server): # Recibe dos parametros: nombre de la base de datos, y el tipo.
        db = QSqlDatabase.addDatabase(server) # Creamos la base de datos
        db.setDatabaseName(filename) # Le asignamos un nombre
        db.setConnectOptions("QSQLITE_OPEN_READONLY")
        
        if not db.open(): # En caso de que no se abra
            QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                    "Click para cancelar y salir.", QMessageBox.Cancel)
            return False
        return True

        # Método para crear la tabla personas
    def db_create(self):
        query = QSqlQuery() # Instancia de Query
        #Ejecutamos la sentencia para crear la tabla personas con 3 columnas
        query.exec_("create table personas(id int primary key, "
                    "firstname varchar(20), lastname varchar(20))")
        # Agregamos algunos datos de prueba
        query.exec_("insert into personas values(101, 'Danny', 'Young')")
        query.exec_("insert into personas values(102, 'Christine', 'Holand')")
        query.exec_("insert into personas values(103, 'Lars', 'Gordon')")
        query.exec_("insert into personas values(104, 'Roberto', 'Robitaille')")
        query.exec_("insert into personas values(105, 'Maria', 'Papadopoulos')")

        # Método para ejecutar la base de datos
    def init(self, filename, server):
        import os # Importamos os
        if not os.path.exists(filename):
            self.db_connect(filename, server) # Llamamos a "db_connect"
            self.db_create() # Llamamis a "db_create"
        else:
            self.db_connect(filename, server)

if __name__ == '__main__':
    app = QApplication(sys.argv) # Creamos una instancia de "QApplication"
    ejm = PYQT_BD() # Instancia de nuestra clase "PYQT_DB"
    # Llamamos al metodo "iinit"
    # La base de datos se llamara 'personas' y sera 'SQLite'
    ejm.init('CarrersNums.db', 'QSQLITE') 
    ejm.show() # Ejecutamos la ventana
    sys.exit(app.exec_()) # Cerramos el proceso