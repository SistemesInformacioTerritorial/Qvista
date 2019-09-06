# from moduls.QvImports import *

from qgis.core import QgsRectangle, QgsVectorLayer, QgsLayoutExporter, QgsPointXY, QgsGeometry, QgsVector, QgsLayout, QgsReadWriteContext
from qgis.gui import QgsMapTool, QgsRubberBand

from qgis.PyQt.QtCore import Qt, QFile, QUrl
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QCheckBox, QLineEdit, QRadioButton
from qgis.PyQt.QtGui import QFont, QColor,QStandardItemModel, QStandardItem, QDesktopServices
from PyQt5.QtWebKitWidgets import QWebView , QWebPage #???
from PyQt5.QtWebKit import QWebSettings

from moduls.QvImports import *
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton

import time
import math
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
        xMon = self.point.x() #???
        yMon = self.point.y() #???

        self.parent.pucMoure = False
        
class QvPrint(QWidget):
    """Una classe del tipus QWidget que servirà per imprimir un area determinada.
    El widget conté un botó per imprimir, un per tornar a posicionar l'area d'impresió, i un comboBox per escollir l'escala.
    """
    
    def __init__(self, project, canvas, poligon,parent=None):
        """Inicialització de la clase:
            Arguments:
                project {QgsProject().instance()} -- El projecte actiu
                canvas {QgsVectorLayer} -- El canvas sobre el que es coloca la rubberband.   
                poligon {QgsPoligon} -- Poligon inicial. A revisar.
        """
        # We inherit our parent's properties and methods.
        QWidget.__init__(self, parent)
        self.parent = parent
        # Creating a memory layer to draw later the rubberband.
        estatDirtybit = self.parent.canvisPendents

        self.layer = QgsVectorLayer('Point?crs=epsg:23031', "Capa temporal d'impressió","memory")
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
        self.dictEscales = {'100':20, '200':40, '250':45, '500':100, '1000':200, '2000':400, '2500':450, '5000':1000, '10000':2000, '20000':4000, '25000':4500, '50000':10000}

        # We instanciate de PointTool tool, to wait for clicks
        # After that, we assign the tool to the canvas.
        rp = PointTool(self, self.canvas)
        canvas.setMapTool(rp)

        self.setupUI()

        self.rubberband = QgsRubberBand(self.canvas)
        self.rubberband.setColor(QColor(0,0,0,50))
        self.rubberband.setWidth(4)

        self.canvas.xyCoordinates.connect(self.mocMouse)
        self.pintarRectangle(self.poligon)
        
        self.parent.setDirtyBit(estatDirtybit)

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10,20,10,20)
        self.layout.setSpacing(14)
        # self.layout.setAlignment(Qt.AlignTop)

        self.layoutTitol = QHBoxLayout()
        self.lblTitol = QLabel("Títol: ")
        self.leTitol = QLineEdit(self)
        self.leTitol.setText(self.parent.titolProjecte)
        self.layoutTitol.addWidget(self.lblTitol)
        self.layoutTitol.addWidget(self.leTitol)

        self.cbOrientacio=QComboBox(self)
        self.cbOrientacio.addItems(['Vertical', 'Horitzontal'])
        self.cbOrientacio.SelectedItem = "Vertical"
        self.cbOrientacio.setCurrentIndex(1)
        self.cbOrientacio.currentTextChanged.connect(self.canviOrientacio)
        self.lblCBOrientacio = QLabel("Orientació: ")
        self.layoutCBOrientacio = QHBoxLayout()
        self.layoutCBOrientacio.addWidget(self.lblCBOrientacio)
        self.layoutCBOrientacio.addWidget(self.cbOrientacio)

        self.combo = QComboBox(self)
        llistaEscales = [key for key in self.dictEscales]
        self.combo.addItems(llistaEscales)
        self.combo.currentTextChanged.connect(self.canviEscala)
        self.lblEscales = QLabel("Escales")
        self.layEscales = QHBoxLayout()
        self.layEscales.addWidget(self.lblEscales)
        self.layEscales.addWidget(self.combo)

        self.cbMida=QComboBox(self)
        self.cbMida.addItems(['A0','A1','A2','A3','A4'])
        self.cbMida.currentTextChanged.connect(self.canviEscala)
        self.cbMida.setCurrentIndex(4)
        self.lblCBmida = QLabel("Paper: ")
        self.layoutCBmida = QHBoxLayout()
        self.layoutCBmida.addWidget(self.lblCBmida)
        self.layoutCBmida.addWidget(self.cbMida)

        self.boto = QvPushButton(text='Generar PDF',destacat=True, parent=self)
        self.boto.clicked.connect(self.printPlanol)
        self.boto.setFixedWidth(220)
        self.boto2 = QvPushButton(text='Emmarcar zona a imprimir',parent=self)
        self.boto2.clicked.connect(self.potsMoure)
        self.boto2.setFixedWidth(220)

        self.nota = QLabel("NOTA: Alguns navegadors web alteren l'escala d'impressió dels PDFs. Per màxima exactitud imprimiu des de l'Adobe Acrobat.")
        styleheetLabel='''
            QLabel {
                color: grey;
            }'''
        self.nota.setStyleSheet(styleheetLabel)
        self.nota.setMaximumWidth(200)
        self.nota.setWordWrap(True)


        self.layout.addLayout(self.layoutTitol)
        self.layout.addLayout(self.layEscales)
        self.layout.addLayout(self.layoutCBmida)
        self.layout.addLayout(self.layoutCBOrientacio)
        self.layout.addWidget(self.boto2)
        self.layout.addWidget(self.boto)
        self.layout.addWidget(self.nota)
        # self.layout.addWidget(self.wFormat)
        # self.layout.addWidget(self.rbVertical)
        # self.layout.addWidget(self.rbHoritzontal)
        self.layout.addStretch()

    def potsMoure(self):
        # self.canvas.scene().removeItem(self.rubberband)
        self.pucMoure = True

    def canviEscala(self):
        self.pucMoure = True
        escala = int(self.dictEscales[self.combo.currentText()])
        mida=self.cbMida.currentText()
        if mida=='A3':
            escala*=math.sqrt(2)
        elif mida=='A2':
            escala*=math.sqrt(2)*2
        elif mida=='A1':
            escala*=math.sqrt(2)*3
        elif mida=='A0':
            escala*=math.sqrt(2)*4


        if self.cbOrientacio.SelectedItem == "Horitzontal":
            self.incX = escala
            self.incY = escala * 1.5
        else:
            self.incX = escala * 1.5
            self.incY = escala

    def canviOrientacio(self):
        self.pucMoure = True
        if self.cbOrientacio.SelectedItem == "Vertical":
            self.cbOrientacio.SelectedItem = "Horitzontal"
        else:
            self.cbOrientacio.SelectedItem = "Vertical"
        self.incX, self.incY = self.incY, self.incX

    def canvasClickat(self): #???
        print ('Clickat, si')

    def mocMouse(self,p):
        if not self.isVisible():
            self.rubberband.hide()
            self.pucMoure

        elif self.pucMoure:
            if self.canvas.rotation()==0:
                self.posXY = [p.x()+self.incX/2, p.y()+self.incY/2]
                self.rubberband.movePoint(0,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
                self.rubberband.movePoint(1,QgsPointXY(p.x()+self.incX,p.y()),0)
                self.rubberband.movePoint(2,QgsPointXY(p.x(),p.y()),0)
                self.rubberband.movePoint(3,QgsPointXY(p.x(),p.y()+self.incY),0)
                self.rubberband.movePoint(4,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
            else:
                alpha=math.radians(self.canvas.rotation())
                beta=math.atan(self.incY/self.incX)
                d=math.sqrt(self.incX**2+self.incY**2)
                self.posXY = [(2*p.x()+d*math.cos(alpha+beta))/2,(2*p.y()+d*math.sin(alpha+beta))/2]
                self.rubberband.movePoint(0,QgsPointXY(p.x()+d*math.cos(alpha+beta),p.y()+d*math.sin(alpha+beta)),0)
                self.rubberband.movePoint(1,QgsPointXY(p.x()+self.incX*math.cos(alpha),p.y()+self.incX*math.sin(alpha)),0)
                self.rubberband.movePoint(2,QgsPointXY(p.x(),p.y()),0)
                self.rubberband.movePoint(3,QgsPointXY(p.x()+self.incY*math.cos(math.radians(90+45)),p.y()+self.incY*math.sin(math.radians(90+45))),0)
                self.rubberband.movePoint(4,QgsPointXY(p.x()+d*math.cos(alpha+beta),p.y()+d*math.sin(alpha+beta)),0)
            


    def pintarRectangle(self,poligon):
        points=[QgsPointXY(0,0),QgsPointXY(0,10),QgsPointXY(10,10),QgsPointXY(0,10),QgsPointXY(0,0)]
        listaPoligonos=[points]
        poligono=QgsGeometry.fromRect(self.poligon)
        self.rubberband.setToGeometry(poligono,self.layer)
        self.rubberband.show()

    def printPlanol(self):
        #
        # if self.checkRotacio.checkState():
        #     rotacio=44.75
        # else:
        #     rotacio=0
        rotacio=self.canvas.rotation()
        if self.cbOrientacio.currentText() == "Vertical":
            if self.cbMida.currentText() == "A4":
                self.plantillaMapa = 'plantillaMapa.qpt'
            elif self.cbMida.currentText() == "A3":
                self.plantillaMapa = 'plantillaMapaA3.qpt'
            elif self.cbMida.currentText() == "A2":
                self.plantillaMapa = 'plantillaMapaA2.qpt'
            elif self.cbMida.currentText() == "A1":
                self.plantillaMapa = 'plantillaMapaA1.qpt'
            elif self.cbMida.currentText() == "A0":
                self.plantillaMapa = 'plantillaMapaA0.qpt'
            
        else:
            if self.cbMida.currentText() == "A4":
                self.plantillaMapa = 'plantillaMapaH.qpt'
            elif self.cbMida.currentText() == "A3":
                self.plantillaMapa = 'plantillaMapaA3H.qpt'
            elif self.cbMida.currentText() == "A2":
                self.plantillaMapa = 'plantillaMapaA2H.qpt'
            elif self.cbMida.currentText() == "A1":
                self.plantillaMapa = 'plantillaMapaA1H.qpt'
            elif self.cbMida.currentText() == "A0":
                self.plantillaMapa = 'plantillaMapaA0H.qpt'  

        t = time.localtime()
        timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
        sortida=tempdir+'sortida_'+timestamp
        
        self.imprimirPlanol(self.posXY[0], self.posXY[1], int(self.combo.currentText()), rotacio, self.cbMida.currentText(), self.plantillaMapa , sortida, 'PDF')
       
        QvApp().logRegistre('Impressió: '+self.combo.currentText() )
    
    def imprimirPlanol(self,x, y, escala, rotacion, midaPagina, templateFile, fitxerSortida, tipusSortida):
        tInicial=time.time()


        template = QFile(templateFile)
        doc = QDomDocument()
        doc.setContent(template, False)

        layout = QgsLayout(self.project)
        # page=QgsLayoutItemPage(layout)
        # page.setPageSize(midaPagina)
        # layout.pageCollection().addPage(page)

        # layout.initializeDefaults()
        # p=layout.pageCollection().pages()[0]
        # p.setPageSize(midaPagina)

        context = QgsReadWriteContext()
        [items, ok] = layout.loadFromTemplate(doc, context)
        # p=layout.pageCollection().pages()[0]
        # p.setPageSize(midaPagina)
   
        if ok:
            refMap = layout.referenceMap()

            titol=layout.itemById('idNomMapa')
            # if self.leTitol.text()!='':
            #     titol.setText(self.leTitol.text()) #comentat pk peta
            # else:
            #     titol.setText('')
            
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
            
            if tipusSortida=='PDF':
                settings = QgsLayoutExporter.PdfExportSettings()
                settings.dpi=300
                settings.exportMetadata=False
                
                # fitxerSortida='d:/sortida_'+timestamp+'.PDF'
                fitxerSortida+='.PDF'
                result = exporter.exportToPdf(fitxerSortida, settings) #Cal desar el resultat (???)

                print (fitxerSortida)

            if tipusSortida=='PNG':
                settings = QgsLayoutExporter.ImageExportSettings()
                settings.dpi = 300

                # fitxerSortida='d:/sortida_'+timestamp+'.PNG'
                fitxerSortida+='.PNG'
                result = exporter.exportToImage(fitxerSortida, settings) #Cal desar el resultat (???)
        
            #Obra el document si està marcat checkObrirResultat
            QDesktopServices().openUrl(QUrl(fitxerSortida))
            
            segonsEmprats=round(time.time()-tInicial,1) #???
            layersTemporals = self.project.mapLayersByName("Capa temporal d'impressió")

            estatDirtybit = self.parent.canvisPendents
            for layer in layersTemporals:
                self.project.removeMapLayer(layer.id())
            self.parent.setDirtyBit(estatDirtybit)

    def oculta(self):
        #Eliminem la capa temporal
        estatDirtybit = self.parent.canvisPendents
        layersTemporals = self.project.mapLayersByName("Capa temporal d'impressió")
        for layer in layersTemporals:
            self.project.removeMapLayer(layer.id())
        self.parent.setDirtyBit(estatDirtybit)
        #Falta posar el ratolí anterior


if __name__ == "__main__":
    with qgisapp() as app:
        # app.setStyle(QStyleFactory.create('fusion'))
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
        windowTest = QMainWindow()
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
