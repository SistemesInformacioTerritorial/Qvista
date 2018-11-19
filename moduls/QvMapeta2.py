
from importaciones import *

from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.core import QgsRectangle

from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebKit import QWebSettings
projecteInicial='../dades/projectes/BCN11_nord.qgs'


class QvMapeta(QtWidgets.QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        # self.setStyleSheet('background-image: url("d:/dropbox/repsqv/qvista/MAPETA_SITUACIO_267x284.bmp");');
        # self.setStyleSheet('background: yellow;')
        self.setGeometry(30,30,600,400)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.gvMapeta = QtWidgets.QGraphicsView(self)
        self.escena = QtWidgets.QGraphicsScene()
        self.gvMapeta.setScene(self.escena)
        self.escena.addText('hola mon')
        self.gvMapeta.setGeometry(0,0,300,300)
        self.imatge = QPixmap('MAPETA_SITUACIO_267x284.bmp')
        self.gvMapeta.show()
        self.escena.addPixmap(self.imatge)
        # self.frame = QtWidgets.QFrame(self)
        # self.frame.setGeometry(0,0,267,284)
        # self.frame.show()
        self.show()

    def paintEvent(self, event):
        
        qp = QtGui.QPainter(self.gvMapeta)
       
 
        # qp.drawRect(QtCore.QRect(self.begin, self.end))       
        #self.gvMapeta.setPixmap(self.imatge)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos() 
        self.br = QtGui.QBrush(QtGui.QColor(100, 210, 10, 40))   

        # brush.setStyle(QtCore.Qt.Dense2Pattern)
        dx = self.end.x()-self.begin.x()
        dy = self.end.y()-self.begin.y()
        print (dx,dy)
        self.escena.addRect(self.begin.x(), self.begin.y(), dx, dy, brush = self.br)

      
        self.gvMapeta.update()
        self.update()

    def mouseReleaseEvent(self, event): 

        self.begin = event.pos()
        self.end = event.pos() 
       
        self.update()


if __name__ == "__main__":
    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
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


        qvMapeta = QvMapeta(canvas)
        qvMapeta.show()

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

