from importaciones import *

from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.core import QgsRectangle

projecteInicial='../dades/projectes/bcn11.qgs'


# Cambios de CPC
# Cambios JNB
# Cambios de CPC por error en master

class QvUbicacions(QtWidgets.QWidget):
    """Una classe del tipus QWidget que mostra i gestiona un arbre d'ubicacions.

    Poden afegir-se noves ubicacions i guardar-hi una descripció. 

    Un click sobre una ubicació ens situa en el rang guardat previament.
    """
    def __init__(self, canvas):
        """[summary]
        Arguments:
            canvas {[QgsMapCanvas]} -- [El canvas que es vol gestionar]
        """

        self.canvas = canvas
        QtWidgets.QWidget.__init__(self)

        # Creem un layout que s'aplica al widget QvUbicacions
        self.layUbicacions = QVBoxLayout(self)
        
        # El model i l'arbre que omplira s'omplirà amb aquest model. 
        self.model = QStandardItemModel()
        self.arbre = QTreeView()
        self.arbre.setModel(self.model)

        # Cal un invisibleRootItem  qu eés la arrel del arbre d'on penjen els elements de la base.
        self.arrelModel = self.model.invisibleRootItem()
        
        # Definim els labels del arbre. 
        self.labels=['Ubicació', 'xMin', 'yMin', 'xMax', 'yMax', 'Projecte']

        # En funció  d'aquests labels s'estableix el numero de columnes que tindrà el model (i l'arbre)
        self.model.setColumnCount(len(self.labels))

        # Coloquem els labels com a headers del model (i l'arbre)
        self.model.setHorizontalHeaderLabels(self.labels)
        
        # Amaguem (o no) les capçaleres. False és que no s'amaguen.
        self.arbre.setHeaderHidden(False)

        #Amaguem totes les columnes menys la primera
        for i in range(self.model.columnCount()):
            if i!=0:
                self.arbre.setColumnHidden(i,True)

        # Connectem el click de l'arbre a la funció _clickArbre
        self.arbre.clicked.connect(self._clickArbre)

        # Fem visible l'arbre
        self.arbre.show()

        # Definim un lineEdit, li afegim un tooltip i el connectem a una funció quan es premi Return        
        self.leUbicacions = QtWidgets.QLineEdit()
        self.leUbicacions.setToolTip('Escriu el nom de la ubicació i prem Return')
        self.leUbicacions.returnPressed.connect(self._novaUbicacio)

        # Afegim el lineEdit i l'arbre al widget QvUbicacions (Afegint els widgets al seu layout.)
        self.layUbicacions.addWidget(self.leUbicacions)
        self.layUbicacions.addWidget(self.arbre)

        # Podriem afegir un frame (fBotonera), sobre el que carregar botons
        # self.layUbicacions.addWidget(self.fBotonera)
 
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
            print('no')
        else:
            # filaItems contindrà objectes del tipus QStandarItem per a carregar-los al model
            filaItems=[]

            # Construim la llista d'elements que formen la ubicació
            itemsFila=[descripcioUbicacio,xmin,ymin,xmax,ymax, QgsProject().instance().fileName()]

            # Convertim la llista d'elements a llista de QStandarItem's, construint filaItems.
            for item in itemsFila:
                filaItems.append(QStandardItem(str(item)))

            # Afegim la fila de items a la arrel del model 
            self.arrelModel.appendRow(filaItems)

            # Redimensionem la columna de descripció (la única visible) segons el contingut
            self.arbre.resizeColumnToContents(0)
        
    def _clickArbre(self):

        """Es gestiona el click sobre una ubicació.
           El canvas gestionat es visualitzarà segons el rang de la ubicació.        

        """
        # La següent linia carrega les variables de x,y màximes i mínimes, segons el currentIndex del model clickat.
        xmin, ymin, xmax, ymax = (float(self.model.itemFromIndex(self.arbre.currentIndex().sibling(self.arbre.currentIndex().row(), i+1)).text()) for i in range(4))
        
        # Construim un rang del tipus QgsRectangle
        rang = QgsRectangle(xmin, ymin, xmax, ymax)

        # Canviem l'extensió del canvas segons el rang recien calculat.
        self.canvas.zoomToFeatureExtent(rang)

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
    with qgisapp():
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
        # Definim una finestra QMainWindow
        windowTest = QtWidgets.QMainWindow()

        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)

        # Creem un dockWdget i definim les característiques
        dwUbicacions = QDockWidget( "Ubicacions", windowTest )
        dwUbicacions.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwUbicacions.setContentsMargins ( 1, 1, 1, 1 )

        # Afegim el widget ubicacions al dockWidget
        dwUbicacions.setWidget(ubicacions)

        # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwUbicacions)

        # Fem visible el dockWidget
        # dwUbicacions.show()

        # Fem visible la finestra principal
        canvas.show()
        windowTest.show()