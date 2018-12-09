# coding:utf-8

from moduls.QvImports import *
import math

from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.core import QgsRectangle
from qgis.PyQt.QtCore import pyqtSignal, Qt

from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings
projecteInicial='../dades/projectes/BCN11_nord.qgs'


class PointTool(QgsMapTool):
    
    line_complete = pyqtSignal(QgsPointXY, QgsPointXY)
    start_point = None
    end_point = None
    rubberband = None


    def __init__(self, canvas):
        self.canvas = canvas
        self.punts = []
        QgsMapTool.__init__(self, canvas)

    def canvasPressEvent(self, event):
        print ('press')
        if self.start_point is None:
            self.start_point = self.toMapCoordinates(event.pos())
            self.punts.append(self.start_point)
            # self.label = QtWidgets.QLabel(self.canvas)
            # self.label.move(event.pos())
            # self.label.setText('hola')
            # self.label.show()
        else:
            self.end_point = self.toMapCoordinates(event.pos())
            self.punts.append(self.end_point)
            # kill the rubberband
            self.rubberband.setToGeometry(QgsGeometry.fromPolylineXY(self.points),None)
            self.rubberband.reset()
            # line is done, emit a signal
            self.line_complete.emit(self.start_point, self.end_point)
            # reset the points
            # self.start_point = None
            self.end_point = None

    def canvasMoveEvent(self, event):
        if self.start_point:
            self.point = self.toMapCoordinates(event.pos())
            # print (math.sqrt((self.start_point.x() - point.x())**2 + (self.start_point.y()-point.y())**2))
            if self.rubberband:
                a = None
                # self.rubberband.reset()
            else:
                self.rubberband = QgsRubberBand(self.canvas)
                self.rubberband.setColor(QColor(0,0,0,50))
                self.rubberband.setWidth(4)

                # self.rubberband.setColor(QColor(Qt.red))
                # set the geometry for the rubberband
            self.points = [self.start_point, self.point]
            self.rubberband.setToGeometry(QgsGeometry.fromPolylineXY(self.points),None)
            # self.label.move(event.pos())
            # self.label.adjustSize()
            # self.label.setText(str(math.sqrt((self.start_point.x() - point.x())**2 + (self.start_point.y()-point.y())**2)))
            # self.a.setMapPosition(point)
            # self.a.setMapPositionCrs(QgsCoordinateReferenceSystem(25831))
            # # self.a.setMapPositionCrs(QgsCoordinateReferenceSystem(25831))
       
            # self.i = QgsMapCanvasAnnotationItem(self.a, self.canvas)
        
    def canvasReleaseEvent(self, event):    
        try:
            self.rubberband.addPoint(self.point)
        except:
            print ('release')
        pass
    #     if self.rubberband:
    #         self.end_point = self.toMapCoordinates(event.pos())
    #         # # kill the rubberband
    #         # self.rubberband.reset()
    #         # line is done, emit a signal
    #         self.line_complete.emit(self.start_point, self.end_point)
    #         # reset the points
    #         self.start_point = None
    #         self.end_point = None
            

class QvMedicions(QWidget):
    """Una classe del tipus QWidget 
    """
    def __init__(self, canvas, parent = None):
        """Inicialització de la clase:
            Arguments:
                canvas {QgsVectorLayer} -- El canvas sobre el que es clicka   
        """
        # We inherit our parent's properties and methods.
        QWidget.__init__(self)

        self.canvas = canvas
        self.parent = parent
        self.rp = PointTool(self.canvas)
        self.canvas.setMapTool(self.rp)
        
        self.setupUI()
        # self.canvas.xyCoordinates.connect(self.mocMouse)

    def setupUI(self):
        self.boto = QPushButton(self)


if __name__ == "__main__":
    with qgisapp():
        canvas=QgsMapCanvas()
        label = QLabel()
        canvas.setContentsMargins(0,0,0,0)
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo

        project.read(projecteInicial)
        
        qvSv = QvMedicions(canvas)
        qvSv.setContentsMargins(0,0,0,0)

        canvas.show()
        label.show()

