# coding:utf-8

from moduls.QvImports import *
from moduls.QvPushButton import QvPushButton


projecteInicial='../dades/projectes/BCN11_nord.qgs'

class PointTool(QgsMapTool):
    def __init__(self, parent, canvas):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent
        self.moureBoto = False
        self.canvas = canvas
        self.a = QgsTextAnnotation()
        self.c = QTextDocument()
        self.puntOriginal = QgsPointXY()
        self.xInici = 0
        self.yInici = 0
    
    def canvasPressEvent(self,event):
        self.puntOriginal = self.toMapCoordinates(event.pos())
        self.pOriginal = event.pos()
        self.xInici = self.pOriginal.x()
        self.yInici = self.pOriginal.y()
        # print (self.xInici, self.yInici)
                    
        self.a = QgsTextAnnotation()
        self.c = QTextDocument()
        
        self.c.setHtml(self.parent.entradaText.toPlainText())
        self.a.setDocument(self.c)

        
        self.layer = QgsVectorLayer('Point?crs=epsg:25831', "RectanglePrint","memory")
        QgsProject().instance().addMapLayer(self.layer)
        self.a.setFrameSize(QSizeF(100, 50))
        self.a.setMapLayer(self.layer)
        self.a.setFrameOffsetFromReferencePoint(QtCore.QPointF(30, 30))
        self.a.setMapPosition(self.puntOriginal)
        self.a.setMapPositionCrs(QgsCoordinateReferenceSystem(25831))
       
        self.i = QgsMapCanvasAnnotationItem(self.a, self.canvas) #???
        # print ('press')

    def canvasMoveEvent(self, event):
        self.puntFinal = event.pos()

        xFinal = self.puntFinal.x()
        yFinal = self.puntFinal.y()

        self.deltaX = xFinal - self.xInici
        self.deltaY = yFinal - self.yInici

        self.a.setFrameOffsetFromReferencePoint(QtCore.QPointF(self.deltaX, self.deltaY))

    def canvasReleaseEvent(self, event):
        self.point = self.toMapCoordinates(event.pos())

        xMon = self.point.x() #???
        yMon = self.point.y() #???

        self.a = QgsTextAnnotation()
        self.c = QTextDocument()
        
        self.c.setHtml(self.parent.entradaText.toPlainText())
        self.a.setDocument(self.c)



class QvAnotacions(QWidget):
    def __init__(self, canvas):
        QWidget.__init__(self)
        self.layout = QVBoxLayout(self)
        self.setLayout = self.layout

        self.setWindowTitle('Anotacions')
        self.canvas = canvas
        self.pt = PointTool(self, self.canvas)
        self.canvas.setMapTool(self.pt)
        self.entradaText = QTextEdit()
        self.entradaText.show()
        self.botoBorrar = QvPushButton('Esborrar anotacions')
        self.botoBorrar.clicked.connect(self.esborrarAnotacions)
        self.layout.addWidget(self.entradaText)
        self.layout.addWidget(self.botoBorrar)

    def esborrarAnotacions(self):
        pass
       

if __name__ == "__main__":
    with qgisapp():
        canvas=QgsMapCanvas()
        canvas.setContentsMargins(0,0,0,0)
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo

        project.read(projecteInicial)
        
        anotacions = QvAnotacions(canvas)
        anotacions.show()

        canvas.show()

