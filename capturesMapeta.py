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
        projecteInicial='C:/qVista/Qvista/mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)      

        else:
            print("error en carga del proyecto qgis")
     
        zones = ["districtes", "barris"]
        for zona in zones:
            pathBoxes = "C:\\qVista\\Qvista\\Dades\\Zones.gpkg|layername=" + zona
            layerBoxes = QgsVectorLayer(pathBoxes, 'ogr')
            
            vlayer = QgsProject.instance().mapLayers().values()

            settings = QgsMapSettings()
            settings.setLayers(vlayer)
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(250, 250))
            
            i = 0 
            features = layerBoxes.getFeatures()   
            for feature in features:
                geometria = feature.geometry().boundingBox()
                print(feature.attributes())
                nom = feature[2]
                settings.setExtent(geometria)
                render = QgsMapRendererSequentialJob(settings)
                image_location = os.path.join("C:\\qVista\\Qvista\\Imatges\\capturesMapeta\\", nom +".png")
                
                render.start()
                render.waitForFinished()
                img = render.renderedImage()
                img.save(image_location, "png")
                i = i + 1
            
        
# https://gis.stackexchange.com/questions/138266/getting-a-layer-that-is-not-active-with-pyqgis
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/cheat_sheet.html
# https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/composer.html#simple-rendering
# https://gis.stackexchange.com/questions/189735/iterating-over-layers-and-export-them-as-png-images-with-pyqgis-in-a-standalone           
