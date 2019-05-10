import sys
from PyQt5.QtSql import *
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, \
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLineEdit, QLabel, QGridLayout



if __name__ == '__main__':
    app = QApplication(sys.argv) # Creamos una instancia de "QApplication"

    db = QSqlDatabase.addDatabase('QSQLITE') # Creamos la base de datos
    db.setDatabaseName('CarrersNums.db') # Le asignamos un nombre
    db.setConnectOptions("QSQLITE_OPEN_READONLY")
    
    if not db.open(): # En caso de que no se abra
        QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                "Click para cancelar y salir.", QMessageBox.Cancel)

    index = 0
    query = QSqlQuery() # Intancia del Query
    query.exec_("select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros where codi = '000102'") 

    while query.next():
        codi = query.value(0) # Codigo calle
        num_lletra_post = query.value(1) # Numero y Letra
        etrs89_coord_x = query.value(2) # coor x
        etrs89_coord_y = query.value(3) # coor y
        num_oficial = query.value(4) # numero oficial
        print(codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial )
        index += 1

    db.close()
    sys.exit(app.exec_()) # Cerramos el proceso