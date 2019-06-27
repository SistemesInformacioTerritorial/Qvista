
# from qgis.PyQt.QtCore import QObject, QModelIndex
# 

# import sys




# from  moduls.QvImports import *
from qgis.core import QgsRectangle
from qgis.PyQt.QtCore import QObject, QModelIndex, Qt
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QTreeView, QAction
import sys, csv

class QVDistrictesBarris(QObject):

    __distBarrisCSV = 'Dades\DIST_BARRIS.csv'

    def __init__(self):
        super().__init__()
        self.labels = []
        self.registre = {}

        # Model
        self.model = QStandardItemModel()
        self.llegirDistrictesBarrisCSV()

        # View
        self.view = QTreeView()




        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.actExpand = QAction("Expandeix/Contreu Tot", self)
        self.actExpand.setStatusTip("Expand")
        self.actExpand.triggered.connect(self.expand_all)
        self.view.addAction(self.actExpand)






        self.view.setModel(self.model)
        self.iniView()



    def expand_all(self):
        """Expandir o contraer todo el arbol, dependiendo de si detecta que esta extendido o contraido
        """
        if self.view.isExpanded(self.model.index(0, 0, QModelIndex())):
            self.view.collapseAll()
        else:
            self.view.expandAll()
        pass        

    def iniView(self):
        self.view.setHeaderHidden(True)
        for i in range(self.model.columnCount()):
            if i == 0:
                self.view.setColumnHidden(i, False)
                self.view.resizeColumnToContents(i)
                self.view.resizeColumnToContents(i)
            else:
                self.view.setColumnHidden(i, True)
        self.view.setEditTriggers(QTreeView.NoEditTriggers)

    def llegirDistrictesBarrisCSV(self):
        try:
            first = True
            with open(self.__distBarrisCSV, newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=';')
                root = self.model.invisibleRootItem()
                for row in reader:
                    if first: # Primer registro
                        self.labels = ['ZONA']
                        for item in row:
                            self.labels.append(item)
                        self.model.setColumnCount(len(self.labels))
                        self.model.setHorizontalHeaderLabels(self.labels)
                        first = False
                    if row['BARRI'] == '': # Registro de distrito
                        dist = [QStandardItem(row['NOM_DISTRICTE'])]
                        for item in row.values():
                            dist.append(QStandardItem(item))  
                        root.appendRow(dist)
                    else: # Registro de barrio
                        barri = [QStandardItem(row['NOM_BARRI'])]
                        for item in row.values():
                            barri.append(QStandardItem(item))
                        dist[0].appendRow(barri)
            return True
        except:
            print('QDistrictesBarris.llegirDistrictesBarrisCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
            return False
    
    def llegirRegistre(self):
        try:
            self.registre = {}
            click = self.view.currentIndex()
            for i in range(self.model.columnCount()):
                index = click.sibling(click.row(), i)
                item = self.model.itemFromIndex(index)
                self.registre[self.labels[i]] = item.text()
            self.registre['RANG'] = QgsRectangle(float(self.registre['X_MIN']), \
                                                 float(self.registre['Y_MIN']), \
                                                 float(self.registre['X_MAX']), \
                                                 float(self.registre['Y_MAX']))
        except:
            print('QDistrictesBarris.llegirRegistre(): ', sys.exc_info()[0], sys.exc_info()[1])
        finally:
            return self.registre

    def llegirRang(self):
        return self.llegirRegistre()['RANG']

        



