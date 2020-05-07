# -*- coding: utf-8 -*-

from qgis.core import QgsRectangle
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit, QApplication, QHBoxLayout,QColorDialog
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QSize
from time import sleep

import win32api
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
        projecteInicial='./mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)      

        else:
            print("error en carga del proyecto qgis")

        #win32api.SetFileAttributes(".\\Dades\\Zones.gpkg",win32con.FILE_ATTRIBUTE_READONLY)

        #Carregar layers de districtes i barris
        zones = ["districtes", "barris"]
        for zona in zones:
            pathBoxes = "Dades\\Zones.gpkg|layername=" + zona
            layerBoxes = QgsVectorLayer(pathBoxes, 'ogr')
            
            vlayer = QgsProject.instance().mapLayers().values()

            #Propietats imatge del mapeta
            settings = QgsMapSettings()
            settings.setLayers(vlayer)
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(200, 200))
            
            features = layerBoxes.getFeatures()   
            for feature in features:
                #Nom zona
                nom = feature[2]
                if nom == "Les Corts" or nom == "les Corts":
                    a = "a"
                #Rectangle zona
                marge = 0.41
                offset_marge = marge/2 
                geometria = feature.geometry().boundingBox()
                xdist = geometria.xMaximum()- geometria.xMinimum()   
                ydist = geometria.yMaximum()- geometria.yMinimum() 
                x1 = geometria.xMaximum() + xdist * offset_marge
                x2 = geometria.xMinimum() - xdist * offset_marge
                y1 = geometria.yMaximum() + ydist * offset_marge
                y2 = geometria.yMinimum() - ydist * offset_marge

                if y1 - y2 > x1 - x2:
                    offset = ((y1 - y2) - (x1 - x2)) / 2
                    x1 = x1 + offset
                    x2 = x2 - offset
                else:
                    offset = ((x1 - x2) - (y1 - y2)) / 2
                    y1 = y1 + offset
                    y2 = y2 - offset

                settings.setExtent(QgsRectangle(x2,y2,x1,y1))
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
                image_location = os.path.join("Imatges\\capturesMapeta\\", nom + "_" + zona[0] + ".png")
                scaled_pixmap.save(image_location, "png")

                ##Crear arxiu de metadades PGW
                #Nom fitzer PGW
                split_nombre=os.path.splitext(image_location)
                filenamePgw = split_nombre[0] + ".pgw"
                wld = open(filenamePgw, "w")   

                #Rang mapeta
                xdist = x1 - x2 
                ydist = y1 - y2
                iheight = 200   #tamany imatge
                iwidth =  200

                if ydist > xdist:
                    dist = ydist
                    offset = (ydist - xdist) / 2
                    xmin = x2 - offset
                    ymin = y2
                else:
                    dist = xdist
                    offset = (xdist - ydist) / 2
                    xmin = x2
                    ymin = y2 - offset

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
