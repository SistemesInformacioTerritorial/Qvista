
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from qgis.core import *
from qgis.core.contextmanagers import qgisapp
from qgis.gui import *
class QMaBIM(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('exemples/qtExemple.ui',self)
 
        self.bSelecciona.clicked.connect(self.prova)

    def prova(self):
        self.l_label.setText('sdf')
           

def main():
    with qgisapp(sysexit=False) as app:

        # app.setWindowIcon(QtGui.QIcon('imatges/MaBIM/MaBIM vermell.png'))
        # splash = splashScreen()
        # app.processEvents()
        main = QMaBIM()
        # splash.finish(main)
        main.showMaximized()

if __name__ == '__main__':
    main()
 