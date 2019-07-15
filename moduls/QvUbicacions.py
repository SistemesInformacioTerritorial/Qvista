# from moduls.QvImports import *
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap

from qgis.core import QgsRectangle,   QgsProject, QgsVectorLayer, QgsLayoutExporter, QgsPointXY, QgsGeometry, QgsVector, QgsLayout, QgsReadWriteContext
from qgis.gui import QgsMapCanvas,QgsLayerTreeMapCanvasBridge,  QgsVertexMarker
import sys
# from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDockWidget, QTreeView, QAction, QVBoxLayout, QHBoxLayout ,QAbstractItemView, QLabel, QWidget, QLineEdit, QPushButton

import pickle
from collections import deque
import os.path
from qgis.core.contextmanagers import qgisapp

from PyQt5.QtGui import QPainter, QColor, QPen



projecteInicial='../dades/projectes/BCN11.qgs'
fic_guardar_arbre='C:/Temp/QvUbicacions.p'  #Fichero para la lectura/escritura de ubicaciones (serializadas)

class StandardItemModel_mio(QStandardItemModel):
    """ Subclase de QStandardItemModel en el que implemento metodos de importacion de datos y de 
        exportacion de datos
    """
    def __init__(self, data, parent=None, ubicacions = None):
        """ En la inicialización se importan los datos de un fichero de objetos serializados con pickle
        """
        super(StandardItemModel_mio, self).__init__(parent)
        self.importData(data)    
        self.ubicacions = ubicacions   

    def exportData(self):
        """ Las ubicaciones se guardan  serializadas en fichero
        """
        # import os
        # os.system('D:/projectes_py/qVista/kk.chm')

        def crear__listaDatos(self, parent = QModelIndex()):
            """ Creamos array de diccionarios que es un objeto serializable
            """
            datos=[]
            n_linea= -1
            raiz=0
            
            def itemList_2(self, n_linea,datos,raiz, parent = QModelIndex()):
                """ Función recursiva para la lectura de todos los nodos del arbol. Una vez obtenidos se
                    formatean adecuadamente y se añaden a la lista
                """
                n_linea += 1
                if n_linea==0:
                    raiz=int(str(parent)[38:-1],16)

                for row in range(self.ubicacions.model.rowCount(parent)):
                    idx = self.ubicacions.model.index(row, 0, parent)
                    i_xxmin = self.ubicacions.model.index(row, 1, parent)
                    i_yymin = self.ubicacions.model.index(row, 2, parent)
                    i_xxmax = self.ubicacions.model.index(row, 3, parent)
                    i_yymax = self.ubicacions.model.index(row, 4, parent)
                    i_proy = self.ubicacions.model.index(row, 5, parent)
                    
                    nn=int(str(idx)[38:-1],16)
                    par=int(str(parent)[38:-1],16)

                    try:
                        xmin_i = int(self.ubicacions.model.data(i_xxmin))
                        ymin_i = int(self.ubicacions.model.data(i_yymin))
                        xmax_i = int(self.ubicacions.model.data(i_xxmax))
                        ymax_i = int(self.ubicacions.model.data(i_yymax))
                    except :
                        xmin_i= 0            
                        ymin_i= 0            
                        xmax_i= 0
                        ymax_i= 0                

                    subdatos={'level' :0, 'id_': nn, 'parent_id': par, 'mi_ubi' : self.ubicacions.model.data(idx),'xmin' : xmin_i, 'ymin' : ymin_i, 'xmax' : xmax_i, 'ymax' : ymax_i}
                    datos.append(subdatos)
                    
                    if self.ubicacions.model.hasChildren(idx):
                        itemList_2(self,n_linea,datos,raiz,idx)

                return raiz

            # invocamos la función para obtener la lista
            raiz=itemList_2(self,n_linea,datos,raiz)
        
            # Bucle para hacer tunning de datos
            for ii in range(len(datos)):
                if datos[ii]['parent_id'] != raiz:
                    datos[ii]['level']=1        

            return (datos)

        datos=crear__listaDatos(self)

        try:
            # if os.path.exists(fic_guardar_arbre):
            #     os.remove(fic_guardar_arbre)

            with open(fic_guardar_arbre,'wb') as fga:
                pickle.dump(datos, fga)
                datos.clear()
                fga.close()
                # msg = QMessageBox()

                # msg.setIcon(QMessageBox.Information)
                # literal= "Ubicacions desades"
                # msg.setText(literal)
                # # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
                # msg.setWindowTitle("QvUbicacions")
               
                # retval = msg.exec_()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            literal= "Error en escriure el fitxer: "+  fic_guardar_arbre 
            msg.setText(literal)
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("QvUbicacions ERROR")
            msg.setDetailedText("Comprovar que existeix i es pot escriure en: " + os.path.dirname(fic_guardar_arbre))
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()
            # if retval== 1024:
            #     print('Implementer salida')
            # else:
            #     print ('No salimos')     


    def importData(self, data, root=None):
        """ Los datos se cargan desde un fichero 
        """
        self.removeRows( 0, self.rowCount() )
        self.setRowCount(0)
        if root is None:
            root = self.invisibleRootItem()
        seen = {}
        values = deque(data)
        while values:
            value = values.popleft()
            if value['level'] == 0:
                parent = root
            else:
                pid = value['parent_id']
                if pid not in seen:
                    values.append(value)
                    continue
                parent = seen[pid]
            xmin = value['xmin']
            ymin = value['ymin']
            xmax = value['xmax']
            ymax = value['ymax']
            visto = value['id_']

            item1= QStandardItem(value['mi_ubi'])
            item1.setToolTip('')

            parent.appendRow([
                item1,
                QStandardItem(str(xmin)),
                QStandardItem(str(ymin)),
                QStandardItem(str(xmax)),
                QStandardItem(str(ymax)),
                ])
            seen[visto] = parent.child(parent.rowCount() - 1)



class QvUbicacions(QWidget):
    """Una classe del tipus QWidget que mostra i gestiona un arbre d'ubicacions.
    Poden afegir-se noves ubicacions i guardar-hi una descripció. 
    Un click sobre una ubicació ens situa en el rang guardat previament.
    """
    
    def __init__(self, canvas, pare = None):
        """[summary]
        Arguments:
            canvas {[QgsMapCanvas]} -- [El canvas que es vol gestionar]


        """
        self.pare= pare
        self.canvas = canvas
        QWidget.__init__(self)

        
        # Leemos un fichero serializado para cargar sus ubicaciones en data
        try:
            with open(fic_guardar_arbre,'rb') as fga:
                data=pickle.load(fga)
                fga.close()
        except:
            data=[]
  
        # Instanciamos ARBOL ************************************************************+*****
        self.arbre = QTreeView()

        # Ponemos menu contextual l arbol
        self.arbre.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.actEsborrar = QAction("Esborrar branca", self)
        self.actEsborrar.setStatusTip("Esborrar")
        self.actEsborrar.triggered.connect(self.esborrarNode)
        self.arbre.addAction(self.actEsborrar)

        self.actExpand = QAction("Expandeix/Contreu Tot", self)
        self.actExpand.setStatusTip("Expand")
        self.actExpand.triggered.connect(self.expand_all)
        self.arbre.addAction(self.actExpand)
       

        self.actClear = QAction("Esborrar arbre", self)
        self.actClear.setStatusTip("Clear")
        self.actClear.triggered.connect(self.clear_all)
        self.arbre.addAction(self.actClear)

        # Permitimos arrastre de ramas en arbol  
        self.arbre.setDragDropMode(QAbstractItemView.InternalMove)  #  4atencion  internal
        # Amaguem (o no) les capçaleres. False és que no s'amaguen.
        # self.arbre.setHeaderHidden(True)  #aqui
        # self.arbre.setColumnWidth(0,8000)
        # self.arbre.setHorizontalScrollBarPolicy(1)        

        self.arbre.clicked.connect(self._clickArbre)

        # Fem visible l'arbre
        self.arbre.show()

        # Instanciamos MODELO *********************************************************************
        self.model = StandardItemModel_mio(data, ubicacions = self)

        # asignamos al arbol el modelo
        self.arbre.setModel(self.model)

        #Amaguem totes les columnes menys la primera
        for i in range(self.model.columnCount()):
            if i!=0:
                self.arbre.setColumnHidden(i,False)   # atencion, si oculto columnas no puedo ver coordenadas de los hijos

        # Connectem el click de l'arbre a la funció _clickArbre
        
        # no_se
        self.selectionModel = self.arbre.selectionModel()  

        # Cal un invisibleRootItem  qu eés la arrel del arbre d'on penjen els elements de la base.
        self.arrelModel = self.model.invisibleRootItem()
        
        # Definim els labels del arbre. 
        self.labels=['Ubicació', 'xMin', 'yMin', 'xMax', 'yMax', 'Projecte']
        # En funció  d'aquests labels s'estableix el numero de columnes que tindrà el model (i l'arbre)
        self.model.setColumnCount(len(self.labels))
        # Coloquem els labels com a headers del model (i l'arbre)
        self.model.setHorizontalHeaderLabels(self.labels)

 
        # ELEMENTOS GRAFICOS DE LA CLASE
        # Definim un lineEdit, li afegim un tooltip i el connectem a una funció quan es premi Return   
        self.leUbicacions = QLineEdit()
        self.leUbicacions.setToolTip('Escriu el nom de la ubicació i prem Return')
        self.leUbicacions.returnPressed.connect(self._novaUbicacio)

       
        #Definimos un boton para guardar las ubicaciones
        icon = QIcon()
        fichero= './imatges/guardar.png'
        icon.addPixmap(QPixmap(fichero))  
        # icon.addPixmap(QPixmap("D:/projectes_py/qVista/imatges/guardar.png"))  

        # self.boton_1 = QPushButton(icon,'')       
        # self.boton_1.setToolTip("Desar ubicacions")
        # self.boton_1.setMaximumSize(QSize(20,20))
        # self.boton_1.show()
        # self.boton_1.clicked.connect(self.model.exportData)

        self.lblubicacio = QLabel('Ubicació:') 

        # Creamos un caja de diseño vertical que s'aplica al widget QvUbicacions
        self.layVUbicacions = QVBoxLayout(self)
        # Creamos una caja de diseño horizontal
        self.layHUbicacions = QHBoxLayout()
        # incluimos en la caja horizontal el line edit y el boton (entran de izquierda a derecha)
        self.layHUbicacions.addWidget(self.lblubicacio)
        self.layHUbicacions.addWidget(self.leUbicacions)
        # self.layHUbicacions.addWidget(self.boton_1)  # y colocacion en contenidor horizontal   

        # incluimos en caja vertical el la caja horizontal y el arbol  (entran desde abajo) 
        self.layVUbicacions.addLayout(self.layHUbicacions)
        self.layVUbicacions.addWidget(self.arbre)

        # Podriem afegir un frame (fBotonera), sobre el que carregar botons
        # self.layUbicacions.addWidget(self.fBotonera)

        # PARA QUE HAGA CASO HA DE PONERSE ESTAS LINEAS POST .SETMODEL
        self.arbre.setHeaderHidden(True)  #aqui
        self.arbre.setColumnWidth(0,8000)
        self.arbre.setHorizontalScrollBarPolicy(1)  


       
    def ubicacionsFi(self):
        self.model.exportData()   
       
       
    def esborrarNode(self):
        """ Eliminar rama del arbol
        """
        self.model.removeRow(self.arbre.currentIndex().row(), self.arbre.currentIndex().parent())
        pass


    def expand_all(self):
        """Expandir o contraer todo el arbol, dependiendo de si detecta que esta extendido o contraido
        """
        if self.arbre.isExpanded(self.model.index(0, 0, QModelIndex())):
            self.arbre.collapseAll()
        else:
            self.arbre.expandAll()
        pass


    def clear_all(self):
        """ Eliminar el arbol completo
        """
        self.model.removeRows( 0, self.model.rowCount() )
        self.model.setRowCount(0)

        


    def _novaUbicacio(self):
        """Es dona d'alta una ubicació al arbre.
        """
        # Treiem el focus del lineEdit
        self.leUbicacions.clearFocus()

        # El text descriptiu de la ubicació entrat al lineEdit
        descripcioUbicacio = self.leUbicacions.text()
        
        # Llegim les coordenades màximes i mínimes a partir del rang del canvas
        rang = self.canvas.extent()
        xmax=int(rang.xMaximum())
        ymax=int(rang.yMaximum())
        xmin=int(rang.xMinimum())
        ymin=int(rang.yMinimum())

        # Només donem l'alta la ubicació si en tenim una descripció
        if descripcioUbicacio == '':
            pass
        else:
            # filaItems contindrà objectes del tipus QStandarItem per a carregar-los al model
            filaItems=[]

            # Construim la llista d'elements que formen la ubicació
            itemsFila=[descripcioUbicacio,xmin,ymin,xmax,ymax, QgsProject().instance().fileName()]

            # Convertim la llista d'elements a llista de QStandarItem's, construint filaItems.
            for item in itemsFila:
                item_Qs=QStandardItem(str(item))
                item_Qs.setToolTip('')
                filaItems.append(item_Qs)


            #Añadir en raiz 
            try:
                self.arrelModel.appendRow(filaItems)
            except:
                pass               

        self.leUbicacions.clear()
        # try:
        #     self.model.exportData()
        # except Exception  as ee:
        #     print(str(ee))
        
        

    def _clickArbre(self):
        """Es gestiona el dobleclick sobre una ubicació.
           El canvas gestionat es visualitzarà segons el rang de la ubicació.        
        """

        # La següent linia carrega les variables de x,y màximes i mínimes, segons el currentIndex del model clickat.
        try:
            xxmin  = float(self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 0+1)).text())
            yymin  = float(self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 1+1)).text())
            xxmax  = float(self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 2+1)).text())
            yymax  = float(self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 3+1)).text())

            # self.model.itemFromIndex(self.arbre.currentIndex().sibling(0, 0)).text()  para debugar contenidos
            # Construim un rang del tipus QgsRectangle
            # rang = QgsRectangle(xmin, ymin, xmax, ymax)
            rang = QgsRectangle(xxmin, yymin, xxmax, yymax)
            # Canviem l'extensió del canvas segons el rang recien calculat.
            self.canvas.zoomToFeatureExtent(rang)


            if self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 0)).text()[0] == chr(45): # "-" :
                if self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), 0)).text()[1] ==chr(62): #">" :

                    self.canvas.scene().removeItem(self.pare.marcaLloc)
                    self.pare.marcaLloc = QgsVertexMarker(self.pare.canvas)
                    self.pare.marcaLloc.setCenter( QgsPointXY(float((xxmin+xxmax)/2),  float((yymin+yymax)/2)) )
                    self.pare.marcaLloc.setColor(QColor(255, 0, 0))
                    self.pare.marcaLloc.setIconSize(15)
                    self.pare.marcaLloc.setIconType(QgsVertexMarker.ICON_CIRCLE) # or  ICON_NONE, ICON_CROSS, ICON_X, ICON_BOX, ICON_CIRCLE, ICON_DOUBLE_TRIANGLE 
                    self.pare.marcaLloc.setPenWidth(3)
                    self.pare.marcaLloc.show()
                    self.pare.marcaLlocPosada = True
        except :
            pass
        



    def _prepararBotonera(self):
        """Funció reservada per a la gestió de la botonera de ubicacions. En aquest moment no s'utilitza.
        """
        self.botoneraArbre = ['Nou']
        for text in self.botoneraArbre:
            boto = QtWidgets.QPushButton()
            boto.setText(text)
            boto.setMaximumWidth(50)
            boto.clicked.connect(self.novaUbicacio)
            self.layBotonera.addWidget(boto)
        self.fBotonera.show()
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layBotonera.addSpacerItem(spacer)



# Demo d'ús quan es crida el fitxer de la classe per separat
if __name__ == "__main__":
    
    with qgisapp() as app:
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        # canvas.show()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)

        # Instanciem la classe QvUbicacions
        ubicacions = QvUbicacions(canvas)

        """
        Amb aquesta linia:
        ubicacions.show()
        es veuria el widget suelto, separat del canvas.

        Les següents línies mostren com integrar el widget 'ubicacions' com a dockWidget.
        """
        
        windowTest = QMainWindow()

        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)

        # Creem un dockWdget i definim les característiques
        dwUbicacions = QDockWidget( "Ubicacions", windowTest )
        dwUbicacions.setContextMenuPolicy(Qt.PreventContextMenu)
        dwUbicacions.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwUbicacions.setContentsMargins ( 1, 1, 1, 1 )

        # Afegim el widget ubicacions al dockWidget
        dwUbicacions.setWidget(ubicacions)

        # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwUbicacions)

        # Fem visible el dockWidget
        dwUbicacions.show()  #atencion

        # Botón para gestionar el guardado del contenido del arbol
        # boto = QtWidgets.QPushButton('Guardar')
        # boto.show()
        # boto.clicked.connect(ubicacions.guardarArbre)

        # Fem visible la finestra principal
        canvas.show()
        windowTest.show()


        pass  




        