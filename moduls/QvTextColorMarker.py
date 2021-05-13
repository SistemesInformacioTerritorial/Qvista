"""
Mòdul per crear un punt al canvas que tingui un color determinat i estigui numerat. Codi d'exemple:
color = QColor(255, 0, 0)
location = QGSPointXY(-1,-1)
number = 47

punt = QvTextColorMarker(canvas,location,number,color)
punt.show()
punt.hide()

"""

#imports
import xml.etree.ElementTree as ET
import requests
from moduls.QvImports import *
from qgis.core import QgsPointXY
from qgis.gui import QgsMapCanvas, QgsRubberBand

class QvTextColorMarker:
    #canvas
    #location
    #number
    #color

    #annotation
    #annotationItem

    colorlist = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#000000", 
        "800000", "#008000", "#000080", "#808000", "#800080", "#008080", "#808080", 
        "C00000", "#00C000", "#0000C0", "#C0C000", "#C000C0", "#00C0C0", "#C0C0C0", 
        "400000", "#004000", "#000040", "#404000", "#400040", "#004040", "#404040", 
        "200000", "#002000", "#000020", "#202000", "#200020", "#002020", "#202020", 
        "600000", "#006000", "#000060", "#606000", "#600060", "#006060", "#606060", 
        "A00000", "#00A000", "#0000A0", "#A0A000", "#A000A0", "#00A0A0", "#A0A0A0", 
        "E00000", "#00E000", "#0000E0", "#E0E000", "#E000E0", "#00E0E0", "#E0E0E0"]

    def __init__(self, canvas, location, number):
        self.canvas = canvas 
        self.location = location
        self.number = number+1
        self.color = QColor(self.colorlist[self.number % len(self.colorlist)])

        self.annotation = QgsTextAnnotation(self.canvas)
        text = QTextDocument()
        text.setHtml("<span style=\" text-align: center; font-weight:600; color:#ffffff;\" >" + str(self.number) + "</span")
        font = QFont()
        if (self.number >= 10):
            font.setPointSize(8)
        else:
            font.setPointSize(12)        
        text.setDefaultStyleSheet("color: rgb(100,0,0)")
        text.setDefaultFont(font)

        self.annotation.setDocument(text)
        self.annotation.setMapPosition(self.location)

        # Create SVG marker symbol
        self.svgStyle = {
            "name": "Imatges/pointMap.svg",
            "size": "5",
            "fill": self.color.name(),
        }
        svgLayer = QgsSvgMarkerSymbolLayer.create(self.svgStyle)
        svgSymbol = QgsMarkerSymbol()
        svgSymbol.changeSymbolLayer(0, svgLayer)

        self.annotation.setMarkerSymbol(svgSymbol)
        self.annotation.setFillSymbol(None)
        
        self.annotation.setFrameOffsetFromReferencePointMm(QPointF(-2.5, -7.5))
        self.annotationItem = QgsMapCanvasAnnotationItem(self.annotation, self.canvas)

    def hide(self):
        self.canvas.scene().removeItem(self.annotationItem)

    def setCenter(self, location):
        self.location = location
        self.annotation.setMapPosition(self.location)

    def setColor(self, color):
        self.svgStyle["fill"] = color.name()
        svgLayer = QgsSvgMarkerSymbolLayer.create(self.svgStyle)
        svgSymbol = QgsMarkerSymbol()
        svgSymbol.changeSymbolLayer(0, svgLayer)

        self.annotation.setMarkerSymbol(svgSymbol)

    def refresh(self, number):
        self.number = number+1
        self.color = QColor(self.colorlist[self.number % len(self.colorlist)])
        

        self.svgStyle["fill"] = self.color.name()
        svgLayer = QgsSvgMarkerSymbolLayer.create(self.svgStyle)
        svgSymbol = QgsMarkerSymbol()
        svgSymbol.changeSymbolLayer(0, svgLayer)

        text = QTextDocument()
        text.setHtml("<span style=\" text-align: center; font-weight:600; color:#ffffff;\" >" + str(self.number) + "</span")
        font = QFont()
        if (self.number >= 10):
            font.setPointSize(8)
        else:
            font.setPointSize(12)
        text.setDefaultStyleSheet("color: rgb(100,0,0)")
        text.setDefaultFont(font)

        self.annotation.setDocument(text)
        self.annotation.setMarkerSymbol(svgSymbol)
