# -*- coding: utf-8 -*-

import configuracioQvista
from qgis.core import QgsRectangle
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit, QApplication, QHBoxLayout,QColorDialog
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QSize, QTimer
from time import sleep
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDockWidget, QTreeView

import win32api
import sys
import os
from moduls.QvImports  import *
import math


class QvcapturesMapeta(QWidget):
    '''
    
    '''
    def showDialogColor(self):
        d_color= QColorDialog()
        
        col = d_color.getColor()
        if col.isValid():
            self.color=col

    def tamanyoLadoCirculo(self):
        '''
        lado me gusta mas que spinB...value
        '''
        self.lado= self.spinBox.value()             

    def __init__(self, canvas,pare=None):
        '''
        '''
        self.canvas=canvas
        if self.canvas.rotation() != 0:
            self.canvas.setRotation(0)

        self.color= QColor(121,144,155)

        self.tempdir=configuracioQvista.tempdir 
        QWidget.__init__(self)
        # self.dadesdir=configuracioQvista.dadesdir
        self.setParent(pare)
        self.pare = pare

        #defino botones y las funciones de su click
        self.botonEjecutar = QPushButton("Ejecutar")
        self.botonEjecutar.setToolTip('Ejecutar')
        self.botonEjecutar.clicked.connect(self.ejecutar)
        self.botonEjecutar.setFixedWidth(120) 

        self.botoColor = QPushButton('Sel·lecc. color')
        self.botoColor.setToolTip('Color perimetre')
        self.botoColor.clicked.connect(self.showDialogColor)
        self.botoColor.setFixedWidth(120) 


        self.layH1=QHBoxLayout()
        self.layH1.addWidget(self.botonEjecutar)
        self.layH1.addWidget(self.botoColor)
        self.spinBox = QSpinBox(self)
        self.spinBox.setFixedWidth(60)
        self.spinBox.setRange(50, 4000)  #600
        self.spinBox.setSingleStep(20)
        self.spinBox.setValue(200)
        self.lado=self.spinBox.value()
        self.spinBox.valueChanged.connect(self.tamanyoLadoCirculo)
        

        self.layV1=QVBoxLayout()
        self.layV1.addLayout(self.layH1) 
        self.layV1.addWidget(self.spinBox) 
        self.setLayout(self.layV1)
    def ejecutar(self):
        """accion correspondiente a la pulsacion del boton
        """
        
        #Carregar layers de districtes i barris
        zones = ["districtes", "barris"]
        for zona in zones:
            pathBoxes = "Dades\\Zones.gpkg|layername=" + zona
            layerBoxes = QgsVectorLayer(pathBoxes, 'ogr')        

            if not layerBoxes.isValid():
                print ("Layer failed to load!")
            
            
            vlayer = QgsProject.instance().mapLayers().values()

            #Propietats imatge del mapeta
            settings = QgsMapSettings()
            # settings.setLayers(vlayer)
            settings.setLayers(self.canvas.layers())
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(self.lado, self.lado))
            
            features = layerBoxes.getFeatures()  
            kk = layerBoxes.featureCount()
            nn=0 
            for feature in features:
                if zona=='districtes' and feature[1] != '10':
                    continue
                if zona=='barris' and ( feature[3] != '10' ):
                    continue

                if zona=='barris' :
                    continue


                # pretendo: toda la geometria a una convex hull
                geoHull= feature.geometry().convexHull()
                polHull= geoHull.asPolygon()

                try:
                    for ring in polHull:
                        convexHull=[]
                        for v in ring:
                            xx=(v.x()); yy=(v.y())

                            pnt=QPointF(xx,yy)  
                            convexHull.append(pnt)
                except Exception as ee:
                    print(str(ee))


                centro,radio= FindMinimalBoundingCircle(convexHull)
                nn+=1
                print("zona:{} nº {} centro: {},{} radio:{}"  \
                    .format(zona,nn,round(centro.x(),3),round(centro.y(),3),round(radio,3)))
                # print("zona:{zona} nº {nn} centro: {centro.x()}{centro.y()} radio{radio}")

                nom = feature[2]
                if nom == "Les Corts" or nom == "les Corts":
                    a = "a"

                x1 = centro.x() + radio #xmax
                x2 = centro.x() - radio #xmin
                y1 = centro.y() + radio #ymax
                y2 = centro.y() - radio #xmin

                settings.setExtent(QgsRectangle(x2,y2,x1,y1))
                ira= settings.hasValidSettings()
                if ira==False:
                    print("mal")
                render = QgsMapRendererSequentialJob(settings)
                
                
                # #Renderitzar imatge PNG
                render.start()
                render.waitForFinished()
                errors= render.errors() 
                img = render.renderedImage()
                
                img = img.convertToFormat(QImage.Format_ARGB32)

                # Preparació per convertir img quadrada a out_img circular
                out_img = QImage(img.width(), img.width(), QImage.Format_ARGB32)
                out_img.fill(Qt.transparent)

                # #Pinzell i pintar imatge
                brush = QBrush(img)       
                painter = QPainter(out_img) 
                painter.setBrush(brush)      
                pen= QPen(self.color,  1, Qt.SolidLine)    #qVista claro         
                # pen= QPen(self.parent.color,  1, Qt.SolidLine)    #qVista claro         
                painter.setPen(pen)
                painter.setRenderHint(QPainter.Antialiasing, True)  
                painter.drawEllipse(0, 0, img.width(), img.width())  
                painter.end()                

                # #Guardar imatge
                scaled_pixmap = QPixmap.fromImage(out_img)
                # scaled_pixmap = QPixmap.fromImage(img)
                image_location = os.path.join("Imatges\\capturesMapeta\\", nom + "_" + zona[0] + ".png")
                scaled_pixmap.save(image_location, "png")

                ##Crear arxiu de metadades PGW
                #Nom fitzer PGW
                split_nombre=os.path.splitext(image_location)
                filenamePgw = split_nombre[0] + ".pgw"
                wld = open(filenamePgw, "w")   

                # #Rang mapeta
                xdist = x1 - x2 
                ydist = y1 - y2
                iheight = self.lado   #tamany imatge
                iwidth =  self.lado
                xmin = x2
                ymin = y2


                # #Escriure PGW
                wld.writelines("%s\n" % (xdist/iwidth))
                wld.writelines("0.0\n")
                wld.writelines("0.0\n")
                wld.writelines("%s\n" % (ydist/iheight))
                wld.writelines("%s\n" % xmin)
                wld.writelines("%s\n" % ymin)
                wld.close        
def FindCircle( a,  b,  c):
    """Calcula circunferencia dados tres puntos

    Arguments:
        a QPointF -- primer punto
        b QPointF -- segundo punto
        c QPointF -- tercer punto

    Returns:
        center QPointF -- Centro de la circunferencia
        radius float -- Radio de la circunferencia
    
    http://csharphelper.com/blog/2016/09/draw-a-circle-through-three-points-in-c/
    """
    #  Get the perpendicular bisector of (x1, y1) and (x2, y2).
    x1 = (b.x() + a.x()) / 2
    y1 = (b.y() + a.y()) / 2
    dy1 = b.x() - a.x()
    dx1 = -(b.y() - a.y())

    # Get the perpendicular bisector of (x2, y2) and (x3, y3).
    x2 = (c.x() + b.x()) / 2
    y2 = (c.y() + b.y()) / 2
    dy2 = c.x() - b.x()
    dx2 = -(c.y() - b.y())
    #     // See where the lines intersect.
    #     bool lines_intersect, segments_intersect;
    #     PointF intersection, close1, close2;

    p1 =    QPointF(x1, y1)
    p2=     QPointF(x2, y2)
    p1Inc1= QPointF(x1 + dx1, y1 + dy1)
    p2Inc2= QPointF(x2 + dx2, y2 + dy2)
    lines_intersect, segments_intersect, intersection, close1, close2=FindIntersection( p1,p1Inc1, p2, p2Inc2)
        
    if (not lines_intersect):
        # print("The points are colinear")
        center = QPointF(0, 0)
        radius = 0;
    else:
        center = intersection
        dx = center.x() - a.x()
        dy = center.y() - a.y()
        radius = math.sqrt(dx * dx + dy * dy)
    return  center, radius
def FindIntersection(p1,p2,p3,p4):
    """Busca punto de interseccion entre dos lineas

    Arguments:
        p1 QPointF -- primer punto de primera linea
        p2 QPointF -- segundo punto de primera linea
        p3 QPointF -- primer punto de segunda linea
        p4 QPointF -- segundo punto de segunda linea

    Returns:
        lines_intersect     Bool    -- True si hay interseccion False lo contrario
        segments_intersect  Bool    -- True si los segmentos intersectan False lo contario
        intersection        QPointF -- Punto interseccion
        close_p1            --   el punto en el primer segmento que está más cerca del punto de intersección
        close_p2            --    el punto en el segundo segmento que está más cerca del punto de intersección

        http://csharphelper.com/blog/2014/08/determine-where-two-lines-intersect-in-c/
    """

    # Find the point of intersection between
    #  the lines p1 --> p2 and p3 --> p4.
    # Get the segments' parameters.
    dx12 = p2.x() - p1.x()
    dy12 = p2.y() - p1.y()
    dx34 = p4.x() - p3.x()
    dy34 = p4.y() - p3.y()
    #  Solve for t1 and t2

    denominator = (dy12 * dx34 - dx12 * dy34)
    try:
        t1 = ((p1.x() - p3.x()) * dy34 + (p3.y() - p1.y()) * dx34) / denominator
    except Exception as ee:
        # print(str(ee))  #jnb
        lines_intersect = False
        segments_intersect = False
        intersection = QPointF(float('nan'), float('nan'))
        close_p1 = QPointF(float('nan'), float('nan'))
        close_p2 = QPointF(float('nan'), float('nan'))
        return lines_intersect, segments_intersect, intersection, close_p1, close_p2
    
    if (math.isinf(t1)):
        # The lines are parallel (or close enough to it).
        lines_intersect = False
        segments_intersect = False
        intersection = QPointF(float('nan'), float('nan'))
        close_p1 = QPointF(float('nan'), float('nan'))
        close_p2 = QPointF(float('nan'), float('nan'))
        return lines_intersect, segments_intersect, intersection, close_p1, close_p2
    lines_intersect = True
    t2 = ((p3.x() - p1.x()) * dy12 + (p1.y() - p3.y()) * dx12)  / -denominator
    # Find the point of intersection.
    intersection = QPointF(p1.x() + dx12 * t1, p1.y() + dy12 * t1)

    # The segments intersect if t1 and t2 are between 0 and 1.
    segments_intersect = ((t1 >= 0) and (t1 <= 1) and (t2 >= 0) and (t2 <= 1))

    # Find the closest points on the segments.
    if (t1 < 0):
        t1 = 0
    elif (t1 > 1):
        t1 = 1

    if (t2 < 0):
        t2 = 0
    elif (t2 > 1):
        t2 = 1

    close_p1 = QPointF(p1.x() + dx12 * t1, p1.y() + dy12 * t1)
    close_p2 = QPointF(p3.x() + dx34 * t2, p3.y() + dy34 * t2)

    return lines_intersect, segments_intersect, intersection, close_p1, close_p2
def CircleEnclosesPoints(center,  radius2, points, skip1,  skip2,  skip3):
    """Testea si un conjunto de puntos está dentro de circunferencia

    Arguments:
        center {QPointF} -- Centro de circunferencia
        radius2 {Float} -- Radio circunferencia
        points {[type]} -- Conjunto de puntos a comprobar
        skip1 {int} -- punto a descartar
        skip2 {int} -- punto a descartar
        skip3 {int} -- punto a descartar

    Returns:
        [Bool] -- [True todos los puntos estan incluidos False lo contrario]
    """
    total_pnt= len(points)
    for ii in  range(0,total_pnt):
        if ((ii != skip1) and (ii != skip2) and (ii != skip3)):
            point = points[ii]
            dx = center.x() - point.x()
            dy = center.y() - point.y()

            test_radius2 = dx * dx + dy * dy
            if (round(test_radius2,4) > round(radius2,4)):
                return False

    return True
def FindMinimalBoundingCircle(convexHull):
    """Busca la circunferencia minima que rodea una convexHull

    Arguments:
        convexHull  -- poligono convexHull

    http://csharphelper.com/blog/2014/08/find-a-minimal-bounding-circle-of-a-set-of-points-in-c/
    """
    # La mejor solución hasta ahora.
    best_center = convexHull[0]
    # best_radius2  = float('inf')
    best_radius2 = sys.maxsize * 2 + 1
    total_pnt= len(convexHull)
    """
    Luego recorre cada par de puntos en conex para ver si se encuentran en un 
    círculo delimitador. Para cada par de puntos, el programa prueba el círculo con 
    el centro exactamente a medio camino entre los dos puntos y pasando por los puntos. 
    Si el radio del círculo al cuadrado es más pequeño que el mejor valor encontrado 
    hasta ahora, el programa llama al método CircleEnclosesPoints (descrito brevemente) 
    para ver si el círculo encierra todos los puntos. Si el círculo encierra los puntos, 
    el programa actualiza su mejor centro y radio del círculo.
    """
    #  Mira pares de puntos de la convex
    for ii in  range(0,total_pnt):
        # print(ii,convexHull[ii])
        for jj in range(total_pnt-1,-1,-1):
        
            xx= (convexHull[ii].x() + convexHull[jj].x()) / 2
            yy= (convexHull[ii].y() + convexHull[jj].y()) / 2
            # Encuentra el círculo a través de estos dos puntos: centro y radio
            test_center = QPointF(xx,yy)
            dx = test_center.x() - convexHull[ii].x()
            dy = test_center.y() - convexHull[ii].y()
            test_radius2 = dx * dx + dy * dy  #radio al cuadrado

            # Vea si este círculo sería una mejora
            if (test_radius2 < best_radius2):
                #  Vea si este círculo encierra todos los puntos.
                if test_radius2 == 0:
                    continue

                if (CircleEnclosesPoints(test_center, test_radius2, convexHull, ii, jj, -1)):
                    # Save this solution.
                    best_center = test_center
                    best_radius2 = test_radius2

                xx=test_center.x(); yy=test_center.y();
                test_radius=math.sqrt(test_radius2)
    
    xx=best_center.x(); yy=best_center.y(); best_radius= math.sqrt(best_radius2)
    '''
    Después de verificar todos los pares de puntos, el programa recorre todos los 
    triples puntos. Para cada triple, el programa utiliza la técnica descrita en la 
    publicación Dibuje un círculo a través de tres puntos en C # para obtener un 
    círculo que pase por los tres puntos. Compara el radio del círculo al cuadrado 
    con el mejor hasta ahora y llama a CircleEnclosesPoints como antes para ver si 
    debe actualizar el mejor círculo.
    '''
    # Mira triples de puntos de la convex
    for ii in  range(0,total_pnt-2):
        for jj in range(ii+1,total_pnt-1):
            for kk in range(jj+1,total_pnt):
                test_center, test_radius= FindCircle(convexHull[ii], convexHull[jj], convexHull[kk])
                test_radius2= test_radius * test_radius
                
                # Vea si este círculo sería una mejora.
                if (test_radius2 < best_radius2):
                    #  Vea si este círculo encierra todos los puntos.
                    encontrado=False
                    if (CircleEnclosesPoints(test_center, test_radius2, convexHull, ii, jj, kk)):
                        # Guarda esta solución
                        best_center = test_center
                        best_radius2 = test_radius2
                        encontrado=True

    '''
    Cuando ha terminado de verificar todos los triples puntos, el código compara 
    best_radius2 con float.MaxValue para ver si encontró un círculo. Si los valores 
    son los mismos, eso significa que la matriz de puntos tiene un solo punto. 
    En ese caso, el programa establece el radio en 0 para que devuelva un círculo 
    centrado en el punto único con radio 0.

    Si best_radius2 no es igual a float.MaxValue , el programa establece el resultado 
    del radio de retorno y finaliza.
    '''
    center = best_center
    if (best_radius2 == sys.maxsize * 2 + 1):
        radius = 0
    else:
        radius = math.sqrt(best_radius2)
    return center,radius




if __name__ == "__main__":

    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.utils import iface
        from moduls.QvAtributs import QvAtributs
     
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)

        atributos = QvAtributs(canvas)
        project = QgsProject.instance()
        # projecteInicial='./mapesOffline/qVista default map.qgs'
        projecteInicial = os.path.abspath('mapesOffline/00 Mapa TM - Situació rr QPKG.qgs')

        if project.read(projecteInicial):
            root = project.layerTreeRoot()

            bool = True # or False
            # root = QgsProject.instance().layerTreeRoot()
            allLayers = root.layerOrder()

            # for layer in allLayers:
            #     root.findLayer(layer.id()).setItemVisibilityChecked(True)                        


            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)   

            windowTest = QMainWindow()
            windowTest.setCentralWidget(canvas)

            leyenda = QvLlegenda(canvas, atributos)
            leyenda.show()
            dwleyenda = QDockWidget( "Leyenda", windowTest )
            dwleyenda.setContextMenuPolicy(Qt.PreventContextMenu)
            dwleyenda.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwleyenda.setContentsMargins ( 1, 1, 1, 1 )
            
            # AÑADIMOS  nuestra instancia al dockwidget
            dwleyenda.setWidget(leyenda)
            # Coloquem el dockWidget al costat esquerra de la finestra
            # windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwleyenda)
            windowTest.addDockWidget( Qt.RightDockWidgetArea, dwleyenda)
            # Fem visible el dockWidget
            dwleyenda.show()  #atencion

            # Instanciamos la classe QvcrearMapetaConBotones
            capturesMapeta = QvcapturesMapeta(canvas)
            capturesMapeta.show()

            """
            Amb aquesta linia:
            crearMapeta.show()
            es veuria el widget suelto, separat del canvas.
            Les següents línies mostren com integrar el widget 'crearMapeta' com a dockWidget.
            """
            # Creem un dockWdget i definim les característiques
            dwcapturesMapeta = QDockWidget( "Captures Mapeta", windowTest )
            dwcapturesMapeta.setContextMenuPolicy(Qt.PreventContextMenu)
            dwcapturesMapeta.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
            dwcapturesMapeta.setContentsMargins ( 1, 1, 1, 1 )
            
            # AÑADIMOS  nuestra instancia al dockwidget
            dwcapturesMapeta.setWidget(capturesMapeta)

            # Coloquem el dockWidget al costat esquerra de la finestra
            windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwcapturesMapeta)

            # Fem visible el dockWidget
            dwcapturesMapeta.show()  #atencion

            # Fem visible la finestra principal
            canvas.show()
            windowTest.show()
        else:
            print("error en carga del proyecto qgis")



       


        
# https://gis.stackexchange.com/questions/138266/getting-a-layer-that-is-not-active-with-pyqgis
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/cheat_sheet.html
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/composer.html#simple-rendering
# https://gis.stackexchange.com/questions/189735/iterating-over-layers-and-export-them-as-png-images-with-pyqgis-in-a-standalone           
