# -*- coding: utf-8 -*-

from qgis.core import QgsRectangle
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit, QApplication, QHBoxLayout,QColorDialog
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QSize
from time import sleep

import sys
import os
from moduls.QvImports  import *


if __name__ == "__main__":

    with qgisapp() as app:

        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.utils import iface
     
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='D:/qVista/Qvista/mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)      

        else:
            print("error en carga del proyecto qgis")

        #Carregar layers de districtes i barris
        zones = ["districtes", "barris"]
        for zona in zones:
            pathBoxes = "D:\\qVista\\Qvista\\Dades\\Zones.gpkg|layername=" + zona
            layerBoxes = QgsVectorLayer(pathBoxes, 'ogr')
            
            vlayer = QgsProject.instance().mapLayers().values()

            #Propietats imatge del mapeta
            settings = QgsMapSettings()
            settings.setLayers(vlayer)
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(200, 200))
            
            features = layerBoxes.getFeatures()   
            for feature in features:
                geometria = feature.geometry().boundingBox()
                #print(feature.attributes())
                nom = feature[2]
                settings.setExtent(geometria)
                render = QgsMapRendererSequentialJob(settings)
                
                
                #Renderitzar imatge PNG
                render.start()
                render.waitForFinished()
                img = render.renderedImage()
                img = img.convertToFormat(QImage.Format_ARGB32)

                #Preparació per convertir img quadrada a out_img circular
                out_img = QImage(img.width(), img.width(), QImage.Format_ARGB32)
                out_img.fill(Qt.transparent)

                #Pinzell i pintar imatge
                brush = QBrush(img)       
                painter = QPainter(out_img) 
                painter.setBrush(brush)      
                pen= QPen(QColor(121,144,155),  1, Qt.SolidLine)    #qVista claro         
                # pen= QPen(self.parent.color,  1, Qt.SolidLine)    #qVista claro         
                painter.setPen(pen)
                painter.setRenderHint(QPainter.Antialiasing, True)  
                painter.drawEllipse(0, 0, img.width(), img.width())  
                painter.end()                

                #Guardar imatge
                scaled_pixmap = QPixmap.fromImage(out_img)
                image_location = os.path.join("D:\\qVista\\Qvista\\Imatges\\capturesMapeta\\", nom +".png")
                scaled_pixmap.save(image_location, "png")

                ##Crear arxiu de metadades PGW
                #Nom fitzer PGW
                split_nombre=os.path.splitext(image_location)
                filenamePgw = split_nombre[0] + ".pgw"
                wld = open(filenamePgw, "w")   

                #Rang mapeta
                xdist = geometria.xMaximum()- geometria.xMinimum()   
                ydist = geometria.yMaximum()- geometria.yMinimum() 
                iheight = 200 
                iwidth =  200

                if ydist > xdist:
                    dist = ydist
                    offset = (ydist - xdist) / 2
                    xmin = geometria.xMinimum() - offset
                    ymin = geometria.yMinimum()
                else:
                    dist = xdist
                    offset = (xdist - ydist) / 2
                    xmin = geometria.xMinimum() 
                    ymin = geometria.yMinimum() - offset

                #Escriure PGW
                wld.writelines("%s\n" % (dist/iwidth))
                wld.writelines("0.0\n")
                wld.writelines("0.0\n")
                wld.writelines("%s\n" % (dist/iheight))
                wld.writelines("%s\n" % xmin)
                wld.writelines("%s\n" % ymin)
                wld.close

            
        
# https://gis.stackexchange.com/questions/138266/getting-a-layer-that-is-not-active-with-pyqgis
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/cheat_sheet.html
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/composer.html#simple-rendering
# https://gis.stackexchange.com/questions/189735/iterating-over-layers-and-export-them-as-png-images-with-pyqgis-in-a-standalone           
