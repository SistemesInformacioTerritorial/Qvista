
# from qgis.PyQt.QtCore import QObject, QModelIndex
# 

# import sys




# from  moduls.QvImports import *
from qgis.core import QgsRectangle
from qgis.PyQt.QtCore import QObject, QModelIndex, Qt
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QTreeView, QAction, QApplication
import sys, csv

from moduls.QvImports  import *

class QVDistrictesBarris(QObject):

    __distBarrisCSV = r'Dades\DIST_BARRIS.csv'
    __zones = r'Dades\Zones.gpkg'

    def __init__(self):
        super().__init__()
        self.labels = []
        self.registre = {}

        # Model
        self.model = QStandardItemModel()
        self.llegirZonesGPKG()
        #self.llegirDistrictesBarrisCSV()

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
        self.expand_all()

    def llegirZonesGPKG(self):
        try:
            pathDistrictes = self.__zones + '|layername=districtes'
            layerDistrictes = QgsVectorLayer(pathDistrictes, 'ogr')
            pathBarris = self.__zones + '|layername=barris'
            layerBarris = QgsVectorLayer(pathBarris, 'ogr')
            
            rowsDistrictes = layerDistrictes.getFeatures()
            llistaDistrictes = []
            for rowD in rowsDistrictes: 
                #print(rowD.attributes())
                #zona = ""
                num_districte = rowD.attributes()[1]
                nom_districte = rowD.attributes()[2]
                num_barri = ""
                
                nom_barri = ""
                geometria = rowD.geometry().boundingBox()
                x_min = str(geometria.xMinimum())
                y_min = str(geometria.yMinimum())
                x_max = str(geometria.xMaximum())
                y_max = str(geometria.yMaximum())
                item = [num_districte,nom_districte,num_barri,nom_barri,x_min,y_min,x_max,y_max]
                llistaDistrictes.append(item)

            def ordenaPerNumDistricte(elem):
                return elem[0]
            llistaDistrictes.sort(key=ordenaPerNumDistricte)
            #print(llistaDistrictes)

            rowsBarris = layerBarris.getFeatures()
            llistaBarris = []
            for rowB in rowsBarris:
                #print(rowB.attributes())
                #zona = ""
                num_districte = rowB.attributes()[3]
                nom_districte = llistaDistrictes[int(num_districte)-1][1]
                num_barri = rowB.attributes()[1]
                nom_barri = rowB.attributes()[2]
                geometria = rowB.geometry().boundingBox()
                x_min = str(geometria.xMinimum())
                y_min = str(geometria.yMinimum())
                x_max = str(geometria.xMaximum())
                y_max = str(geometria.yMaximum())
                item = [num_districte,nom_districte,num_barri,nom_barri,x_min,y_min,x_max,y_max]
                llistaBarris.append(item)

            def ordenaPerNumBarri(elem):
                return elem[2]
            llistaBarris.sort(key=ordenaPerNumBarri)
            #print(llistaBarris)

            self.labels = ["ZONA", "DISTRICTE", "NOM_DISTRICTE", "BARRI", "NOM_BARRI", "X_MIN", "Y_MIN", "X_MAX", "Y_MAX"]
            root = self.model.invisibleRootItem()
            self.model.setColumnCount(len(self.labels))
            self.model.setHorizontalHeaderLabels(self.labels)

            #Afegir Barcelona com a arrel de l'arbre
            bcn_dades = ["00","Barcelona", "00", "Barcelona", "419710.0553820258", "4573818.80776309", "436533.35", "4591775.02"]
            bcn = [QStandardItem("Barcelona")]
            for item in bcn_dades:
                bcn.append(QStandardItem(item))
            root.appendRow(bcn)

            ultimaDistr = -1
            itDist = 0
            for b in llistaBarris:
                if ultimaDistr != int(b[0]):  #Afegir següent districte 
                    dist = [QStandardItem(llistaDistrictes[itDist][1])]
                    for i in range (0, len(llistaDistrictes[itDist])):
                        dist.append(QStandardItem(llistaDistrictes[itDist][i]))  
                    bcn[0].appendRow(dist)
                    
                    itDist = itDist + 1
                                        #Afegir següent Barri
                barri = [QStandardItem(b[3])]
                for item in b:
                    barri.append(QStandardItem(item))
                dist[0].appendRow(barri)
                ultimaDistr = int(b[0])
            return True     
        except:
            print("Error en construcció de l'arbre de zones")
            return False

    # def llegirDistrictesBarrisCSV(self):
    #     try:
    #         first = True
    #         with open(self.__distBarrisCSV, newline='') as csvFile:
    #             reader = csv.DictReader(csvFile, delimiter=';')
    #             root = self.model.invisibleRootItem()
    #             for row in reader:
    #                 if first: # Primer registro
    #                     self.labels = ['ZONA']
    #                     for item in row:
    #                         self.labels.append(item)
    #                     self.model.setColumnCount(len(self.labels))
    #                     self.model.setHorizontalHeaderLabels(self.labels)
    #                     first = False
    #                 if row['BARRI'] == '': # Registro de distrito
    #                     dist = [QStandardItem(row['NOM_DISTRICTE'])]
    #                     for item in row.values():
    #                         dist.append(QStandardItem(item))  
    #                     root.appendRow(dist)
    #                 else: # Registro de barrio
    #                     barri = [QStandardItem(row['NOM_BARRI'])]
    #                     for item in row.values():
    #                         barri.append(QStandardItem(item))
    #                     dist[0].appendRow(barri)
    #         return True
    #     except:
    #         print('QDistrictesBarris.llegirDistrictesBarrisCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
    #         return False
    
    def llegirRegistre(self):
        try:
            click = self.view.currentIndex()
            #Controlarem si s'ha canviat d'índex o no
            if hasattr(self,'ultimIndex') and self.ultimIndex==click:
                return self.registre
            self.ultimIndex=click
            self.registre = {}
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
    
    def esDistricte(self):
        return self.llegirRegistre()['BARRI']==''
    
    def esBarri(self):
        return not self.esDistricte()
    
    def llegirNom(self):
        if self.esDistricte():
            distr = self.llegirRegistre()["NOM_DISTRICTE"]
            distr_d = distr + "_d"
            return distr_d
        else:
            barri = self.llegirRegistre()["NOM_BARRI"]
            if barri == "Barcelona":
                return barri
            else:
                barri_b = barri + "_b"
                return barri_b


    def llegirID(self):
        if self.esDistricte():
            return self.llegirRegistre()['DISTRICTE']
        return self.llegirRegistre()['BARRI']

        

if __name__ == "__main__":
    with qgisapp() as app:

        distBarris = QVDistrictesBarris()

