# https://www.qtcentre.org/threads/53745-QPixmap-as-background-of-QWidget
from moduls.QvImports  import *

from qgis.core import QgsRectangle, QgsPointXY
from qgis.gui import QgsMapTool
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout 
from PyQt5.QtWidgets import QHBoxLayout, QFrame
from PyQt5.QtWidgets import  QApplication
from moduls import QvFuncions


# import time

@QvFuncions.creaEina(titol="Eina Coordenades", esEinaGlobal = True, apareixDockat = False)
class EinaCoordenades(QWidget):

    def __init__(self, pare):
        
        QWidget.__init__(self)
        if isinstance(pare, QgsMapCanvas):
            self.canvas = pare
        else: 
            self.canvas = pare.canvas
        self.setParent(pare)
        self.pare = pare
        self.nova = True

        lay = QVBoxLayout()
        self.setLayout(lay)

        def novaCoordenada():
            self.nova = True

        nou = QPushButton()
        nou.pressed.connect(novaCoordenada)
        nou.setText("Nou punt")
        lay.addWidget(nou)

        lay1 = QHBoxLayout()
        lay2 = QHBoxLayout()

        try:
            self.sistemaCoords = self.canvas.mapSettings().destinationCrs().authid()
        except:
            print("coords malament")

        lblnom1 = QLabel()
        lblnom1.setMinimumWidth(75)
        lblnom1.setText(self.sistemaCoords)
        lblnom2 = QComboBox()
        lblnom2.setMinimumWidth(75)
        lblnom2.addItem("Lat/Long")
        lblnom2.addItem("ETRS89")
        lblnom2.addItem("TRESOR")
        lblnom2.addItem("ETRS3857")

        self.leXcoord1 = QLineEdit()
        self.leYcoord1 = QLineEdit()

        def is_number(s):
            try:
                float(s)
                return True
            except ValueError:
                return False

        def transformaPunt():
            if is_number(self.leXcoord1.text()) and is_number(self.leYcoord1.text()):
                x = float(self.leXcoord1.text())
                y = float(self.leYcoord1.text())
                p = QgsPointXY(x,y)
                estat_nova = self.nova 
                self.nova = True
                showXY(p)
                self.nova = estat_nova
                
        self.leXcoord1.returnPressed.connect(transformaPunt)
        self.leYcoord1.returnPressed.connect(transformaPunt)

        self.leXcoord2 = QLineEdit()
        self.leYcoord2 = QLineEdit()

        def f1():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text1)
        
        def f2():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text2)

        icona_copiar = QIcon('Imatges/file-document.png')
        b1 = QPushButton()
        b1.pressed.connect(f1)
        b1.setIcon(icona_copiar)
        b1.setToolTip("Copia al portaretalls")
        b2 = QPushButton()
        b2.pressed.connect(f2)
        b2.setIcon(icona_copiar)
        b2.setToolTip("Copia al portaretalls")

        lay1.addWidget(lblnom1)
        lay1.addWidget(self.leXcoord1)
        lay1.addWidget(self.leYcoord1)
        lay1.addWidget(b1)
        lay2.addWidget(lblnom2)
        lay2.addWidget(self.leXcoord2)
        lay2.addWidget(self.leYcoord2)
        lay2.addWidget(b2)

        lay.addLayout(lay1)
        lay.addLayout(lay2)

        def showXY(p): 
            if self.nova:
                x1=str("%.3f" % p.x())
                y1=str("%.3f" % p.y())
                self.leXcoord1.setText(x1)
                self.leYcoord1.setText(y1)
                self.text1 = x1 + ", " + y1

                if lblnom2.currentText() == "Lat/Long": #WGS84
                    if self.sistemaCoords != "EPSG:4326":
                        self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.sistemaCoords), 
                                QgsCoordinateReferenceSystem("EPSG:4326"), 
                                QgsProject.instance())
                        p=self.transformacio.transform(p)
                    y2 = str("%.7f" % p.x())
                    x2 = str("%.7f" % p.y())

                elif lblnom2.currentText() == "TRESOR": #ETRS89
                    self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.sistemaCoords), 
                            QgsCoordinateReferenceSystem("EPSG:25831"), 
                            QgsProject.instance())
                    p=self.transformacio.transform(p)
                    x2= str(int((float(p.x()) - 400000) * 1000))
                    y2= str(int((float(p.y()) - 4500000) * 1000))

                #TRESOR  ED50
                
                elif lblnom2.currentText() == "ETRS89":
                    if self.sistemaCoords != "EPSG:25831":
                        self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.sistemaCoords), 
                                QgsCoordinateReferenceSystem("EPSG:25831"), 
                                QgsProject.instance())
                        p=self.transformacio.transform(p)
                    x2 = str("%.3f" % p.x())
                    y2 = str("%.3f" % p.y())

                elif lblnom2.currentText() == "ETRS3857": #pseudomercator
                    if self.sistemaCoords != "EPSG:3857":
                        self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.sistemaCoords), 
                                QgsCoordinateReferenceSystem("EPSG:3857"), 
                                QgsProject.instance())
                        p=self.transformacio.transform(p)
                    x2 = str("%.3f" % p.x())
                    y2 = str("%.3f" % p.y())

                self.leXcoord2.setText(x2)
                self.leYcoord2.setText(y2)
                self.text2 = x2 + ", " + y2
        
        self.canvas.xyCoordinates.connect(showXY)

        class PointTool(QgsMapTool):   
            def __init__(self, canvas, parent):
                QgsMapTool.__init__(self, canvas)
                self.canvas = canvas  
                self.parent = parent
                self.m1 = QgsVertexMarker(canvas)
                self.m1.setColor(QColor(255,0, 0)) #(R,G,B)
                self.m1.setIconSize(12)
                self.m1.setIconType(QgsVertexMarker.ICON_CROSS)
                self.m1.setPenWidth(3)

            def canvasPressEvent(self, event):
                self.parent.nova = False
                x = self.parent.leXcoord1.text()
                y = self.parent.leYcoord1.text()
                self.m1.setCenter(QgsPointXY(float(x),float(y)))
                self.m1.show()

        self.tool = PointTool(self.canvas, self)
        self.canvas.setMapTool(self.tool)

    def hideEvent(self,event):
        super().hideEvent(event)
        self.canvas.unsetMapTool(self.tool)
        self.canvas.scene().removeItem(self.tool.m1)

    def showEvent(self,event):
        super().showEvent(event)
        self.canvas.setMapTool(self.tool)

        
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
            qvEinaCoords = EinaCoordenades(pare=canvas)
            #dwLay = QVBoxLayout()
            dwEC = QDockWidget()
            dwEC.setWidget(qvEinaCoords)
            dwEC.show()
            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")