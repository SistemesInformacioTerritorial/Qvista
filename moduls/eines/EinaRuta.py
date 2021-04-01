# https://www.qtcentre.org/threads/53745-QPixmap-as-background-of-QWidget
from moduls.QvImports  import *

from qgis.core import QgsRectangle, QgsPointXY
from qgis.gui import QgsMapTool
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout 
from PyQt5.QtWidgets import QHBoxLayout, QFrame
from PyQt5.QtWidgets import  QApplication, QMessageBox
from moduls import QvFuncions
from moduls.QvRuta import *

@QvFuncions.creaEina(titol="Eina Ruta", esEinaGlobal = True, apareixDockat = False)
class EinaRuta(QWidget):
    getPoint = 1
    """
    Valors del getPoint:
        0 - no seleccionar un punt
        1 - seleccionar punt inicial
        2 - seleccionar punt final
    """
    # canvas = None
    tool = None

    pGirs = [] #punts de gir

    startPoint = QgsPointXY(float(0),float(0))
    endPoint = QgsPointXY(float(0),float(0))

    mStart = None
    mEnd = None

    ruta = Ruta(None,None)

    def __init__(self, pare):
        def getCoordInici():
            self.getPoint = 1

        def getCoordFi():
            self.getPoint = 2

        def calcularRuta():
            self.ruta.ocultarRuta()
            self.ruta.ocultarPuntsGir()
            self.ruta = Ruta(self.startPoint,self.endPoint)
            self.ruta.calculaRuta()
            if (self.ruta.ruta_calculada == False):
                print("error calculant la ruta")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error calculant la ruta")
                msg.setInformativeText("La ruta no s'ha pogut calcular. Provi amb uns altres punts")
                msg.setWindowTitle("Error")
                msg.exec_()
            else:
                self.ruta.pintarRuta(self.canvas)
                self.ruta.pintarPuntsGir(self.canvas)
   
        QWidget.__init__(self)

        if isinstance(pare, QgsMapCanvas):
            self.canvas = pare
        else: 
            self.canvas = pare.canvas
        
        lay = QVBoxLayout()
        self.setLayout(lay)

        startButton = QPushButton()
        startButton.pressed.connect(getCoordInici)
        startButton.setText("Punt inici")
        lay.addWidget(startButton)

        endButton = QPushButton()
        endButton.pressed.connect(getCoordFi)
        endButton.setText("Punt final")
        lay.addWidget(endButton)

        calcRouteButton = QPushButton()
        calcRouteButton.pressed.connect(calcularRuta)
        calcRouteButton.setText("Calcular ruta")
        lay.addWidget(calcRouteButton)

        self.initMarkers()
        class PointTool(QgsMapTool):  
            def __init__(self, canvas, parent):
                QgsMapTool.__init__(self, canvas)
                self.canvas = canvas  
                self.parent = parent

            def canvasPressEvent(self, event):
                if self.parent.getPoint == 1:
                    """
                    Pre: -
                    Post: el següent click és per seleccionar el punt final. Estableix un marker
                    """
                    startPoint = QgsPointXY(event.mapPoint())
                    print("Start Point is " + str(startPoint))
                    self.parent.startPoint = startPoint
                    self.parent.getPoint = 2 
                    self.parent.mStart.setCenter(startPoint)

                elif self.parent.getPoint == 2:
                    endPoint = QgsPointXY(event.mapPoint())
                    print("End Point is " + str(endPoint))
                    self.parent.endPoint = endPoint
                    self.parent.getPoint = 0
                    self.parent.mEnd.setCenter(endPoint)
    
        self.tool = PointTool(self.canvas, self)
        self.canvas.setMapTool(self.tool)

    def initMarkers(self):
        self.mStart = QgsVertexMarker(self.canvas)
        self.mStart.setColor(QColor(255,0, 0)) #(R,G,B)
        self.mStart.setIconSize(12)
        self.mStart.setIconType(QgsVertexMarker.ICON_CROSS)
        self.mStart.setPenWidth(3)

        self.mEnd = QgsVertexMarker(self.canvas)
        self.mEnd.setColor(QColor(0,0, 255)) #(R,G,B)
        self.mEnd.setIconSize(12)
        self.mEnd.setIconType(QgsVertexMarker.ICON_CROSS)
        self.mEnd.setPenWidth(3)

    def hideEvent(self,event):
        super().hideEvent(event)
        self.canvas.unsetMapTool(self.tool)
        self.canvas.scene().removeItem(self.mStart)
        self.canvas.scene().removeItem(self.mEnd)
        self.ruta.ocultarRuta()
        self.ruta.ocultarPuntsGir()

    def showEvent(self,event):
        super().showEvent(event)
        self.canvas.setMapTool(self.tool)
        self.initMarkers()
        self.getPoint = 1

if __name__ == "__main__":
    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
     
        # Canvas, projecte i bridge
        start1 = time.time()
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
            qvEinaRuta = EinaRuta(canvas)
            dwEC = QDockWidget()
            dwEC.setWidget(qvEinaRuta)
            dwEC.show()
            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")