from importaciones import *

from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.core import QgsRectangle

projecteInicial='../dades/projectes/BCN11_nord.qgs'


class PointTool(QgsMapTool):
    def __init__(self, parent, canvas):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent

    
    def canvasMoveEvent(self, event):
        self.parent.dockX = event.pos().x()
        self.parent.dockY = event.pos().y()
        # print (x, y)
        # self.parent.move(x, y)

        # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        
        self.point = self.toMapCoordinates(event.pos())
        print (self.point)
        print (event.x())
        self.parent.pucMoure = False

class QvPrint(QtWidgets.QWidget):
    """Una classe del tipus QWidget que servirà per imprimir un area determinada.

    El widget conté un botó per imprimir, un per tornar a posicionar l'area d'impresió, i un comboBox per escollir l'escala.
    """
    
    def __init__(self, project, canvas, poligon):
        """Inicialització de la clase:
            Arguments:
                project {QgsProject().instance()} -- El projecte actiu
                canvas {QgsVectorLayer} -- El canvas sobre el que es coloca la rubberband.   
                poligon {QgsPoligon} -- Poligon inicial. A revisar.
        """
        # We inherit our parent's properties and methods.
        QtWidgets.QWidget.__init__(self)

        # Creating a memory layer to draw later the rubberband.
        self.layer = QgsVectorLayer('Point?crs=epsg:25831', "RectanglePrint","memory")
        project.addMapLayer(self.layer)

        # We store safely the parameters as class variables.
        self.canvas = canvas
        self.project = project
        self.poligon = poligon

        # Offset inicial del rectangle d'impressió- TODO
        self.incX = 100
        self.incY = 150

        # Semafor per deixar fix el rectangle un cop fet click.
        self.pucMoure = True

        # Diccionari d'escales i proporcions que fixen el tamany del rectangle en pantalla.
        # Podria fer-se millor, pero Practicality beats Purity...
        self.dictEscales = {'500':100, '1000':200, '2000':400, '5000':1000, '10000':2000, '20000':4000,'50000':10000}

        # We instanciate de PointTool tool, to wait for clicks
        # After that, we assign the tool to the canvas.
        rp = PointTool(self, self.canvas)
        canvas.setMapTool(rp)

        self.setupUI()

        self.rubberband = QgsRubberBand(self.canvas)
        self.rubberband.setColor(QtGui.QColor(0,0,0,50))
        self.rubberband.setWidth(4)

        self.canvas.xyCoordinates.connect(self.mocMouse)
        self.pintarRectangle(self.poligon)

    def setupUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)


        self.combo = QtWidgets.QComboBox(self)
        # self.combo.move(5,100)
        llistaEscales = [key for key in self.dictEscales]
        self.combo.addItems(llistaEscales)
        self.combo.currentTextChanged.connect(self.canviEscala)
        self.combo.show()

        
        self.comboOrientacio = QtWidgets.QComboBox(self)
        # self.combo.move(5,100)
        orientacions = ['Vertical', 'Horitzontal']
        self.comboOrientacio.addItems(orientacions)
        self.comboOrientacio.currentTextChanged.connect(self.canviOrientacio)
        self.comboOrientacio.show()

        self.font = QFont()
        self.font.setPointSize(20)
        self.boto = QtWidgets.QPushButton(self)
        self.boto.setText('Plot')
        self.boto.setFont(self.font)
        self.boto.setMinimumHeight(self.boto.height()*2)
        
        self.boto.clicked.connect(self.printPlanol)
        self.boto2 = QtWidgets.QPushButton(self)
        self.boto2.setText('Reposicionar')
        self.boto2.clicked.connect(self.potsMoure)

        self.checkRotacio = QtWidgets.QCheckBox('Planol rotat')
        self.checkRotacio.show()

        self.layout.addWidget(self.boto)
        self.layout.addWidget(self.boto2)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.checkRotacio)
        self.layout.addWidget(self.comboOrientacio)


    def potsMoure(self):
        # self.canvas.scene().removeItem(self.rubberband)
        self.pucMoure = True

    def canviEscala(self):
        self.pucMoure = True
        escala = int(self.dictEscales[self.combo.currentText()])

        if self.comboOrientacio.currentText() == 'Vertical':
            self.incX = escala
            self.incY = escala * 1.5
        else:
            self.incX = escala * 1.5
            self.incY = escala

    def canviOrientacio(self):
        self.pucMoure = True
        self.incX, self.incY = self.incY, self.incX

    def canvasClickat(self):
        print ('Clickat, si')

    def mocMouse(self,p):
        if not self.isVisible():
            self.rubberband.hide()
            self.pucMoure

        elif self.pucMoure:
            self.posXY = [p.x()+self.incX/2, p.y()+self.incY/2]
            self.rubberband.movePoint(0,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
            self.rubberband.movePoint(1,QgsPointXY(p.x()+self.incX,p.y()),0)
            self.rubberband.movePoint(2,QgsPointXY(p.x(),p.y()),0)
            self.rubberband.movePoint(3,QgsPointXY(p.x(),p.y()+self.incY),0)
            self.rubberband.movePoint(4,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
            


    def pintarRectangle(self,poligon):
        points=[QgsPointXY(0,0),QgsPointXY(0,10),QgsPointXY(10,10),QgsPointXY(0,10),QgsPointXY(0,0)]
        listaPoligonos=[points]
        poligono=QgsGeometry.fromRect(self.poligon)
        self.rubberband.setToGeometry(poligono,self.layer)
        self.rubberband.show()

    def printPlanol(self):
        if self.checkRotacio.checkState():
            rotacio=44.75
        else:
            rotacio=0
        orientacio = self.comboOrientacio.currentText()
        if orientacio == 'Vertical':
            self.plantillaMapa = 'plantillaMapa.qpt'
        else:
            self.plantillaMapa = 'plantillaMapaH.qpt'
        self.imprimirPlanol(self.posXY[0], self.posXY[1], int(self.combo.currentText()), rotacio, self.plantillaMapa , 'd:/EUREKA.pdf', 'PDF')

    def imprimirPlanol(self,x, y, escala, rotacion, templateFile, fitxerSortida, tipusSortida):
        tInicial=time.time()

        template = QtCore.QFile(templateFile)
        doc = QDomDocument()
        doc.setContent(template, False)

        layout = QgsLayout(self.project)
        context = QgsReadWriteContext()
        [items, ok] = layout.loadFromTemplate(doc, context)
   
        if ok:
            refMap = layout.referenceMap()
            
            rect = refMap.extent()
            vector = QgsVector(x - rect.center().x(), y - rect.center().y())
            rect += vector
            refMap.setExtent(rect)
            refMap.setScale(escala)
            refMap.setMapRotation(rotacion)
            #Depenent del tipus de sortida...
            
            exporter = QgsLayoutExporter(layout) 
            # image_settings = exporter.ImageExportSettings()
            # image_settings.dpi = 30
                
            # result = exporter.exportToImage('d:/dropbox/qpic/preview.png',  image_settings)
            # imatge = QPixmap('d:/dropbox/qpic/preview.png')
            # self.ui.lblImatgeResultat.setPixmap(imatge)
            t = time.localtime()

            timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
            if tipusSortida=='PDF':
                settings = QgsLayoutExporter.PdfExportSettings()
                settings.dpi=300
                settings.exportMetadata=False
                
                fitxerSortida='d:/dropbox/qpic/sortida_'+timestamp+'.PDF'
                result = exporter.exportToPdf(fitxerSortida, settings)

                print (fitxerSortida)

            if tipusSortida=='PNG':
                settings = QgsLayoutExporter.ImageExportSettings()
                settings.dpi = 300

                fitxerSortida='d:/dropbox/qpic/sortida_'+timestamp+'.PNG'
                result = exporter.exportToImage(fitxerSortida, settings)
        
            #Obra el document si està marcat checkObrirResultat
            QDesktopServices().openUrl(QUrl(fitxerSortida))
            
            segonsEmprats=round(time.time()-tInicial,1)


if __name__ == "__main__":
    with qgisapp():
        # Canvas, projecte i bridge
        #canvas=QvCanvas()
        canvas=QgsMapCanvas()
        # canvas.xyCoordinates.connect(mocMouse)
        # canvas.show()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo
        project.read(projecteInicial)
        

 
        #layer = project.instance().mapLayersByName('BCN_Districte_ETRS89_SHP')[0]


        qvPrint = QvPrint(project, canvas, canvas.extent())
        qvPrint.show()

        """
        Amb aquesta linia:
        qvPrint.show()
        es veuria el widget suelto, separat del canvas.

        Les següents línies mostren com integrar el widget 'ubicacions' com a dockWidget.
        """
        # Definim una finestra QMainWindow
        """ 
        windowTest = QtWidgets.QMainWindow()

        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)

        # Creem un dockWdget i definim les característiques
        dwPrint = QDockWidget( "qV Print", windowTest )
        dwPrint.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwPrint.setContentsMargins ( 1, 1, 1, 1 )
        dwPrint.setMaximumHeight(200)

        # Afegim el widget ubicacions al dockWidget
        dwPrint.setWidget(qvPrint)

        # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwPrint)

        # Fem visible el dockWidget
        # dwPrint.show()

        # Fem visible la finestra principal

        windowTest.show() """

        canvas.show()

