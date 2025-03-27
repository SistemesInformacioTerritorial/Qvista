from qgis.PyQt import QtCore
from qgis.core import QgsSettings
from qgis.gui import QgsMapTip
from moduls.QvApp import QvApp
from moduls.QvFuncions import debugging
import os

class QvToolTip:
    """ Class to show MapTips on the map
        (Código tomado de qgisapp.cpp - varía según la version de QGIS)
    """
    def __init__(self, canvas):
        self.canvas = canvas
        self.settings = QvApp().settings
        self.mapTipsVisible = self.settings.value("qgis/enableMapTips", defaultValue=True, type=bool)
        if debugging(): print("qgis/enableMapTips:", self.mapTipsVisible)
        self.createMapTips()
        self.lastMapPosition = None
        self.canvas.xyCoordinates.connect(self.saveLastMousePosition)

    def createMapTips(self):
        self.mapTipsTimer = QtCore.QTimer(self.canvas)
        self.mapTipsTimer.timeout.connect(self.showMapTip)
        self.mapTipsTimer.setInterval(self.settings.value("qgis/mapTipsDelay", defaultValue=850, type=int))
        self.mapTipsTimer.setSingleShot(True)
        self.mapTip = QgsMapTip()

    def toggleMapTips(self, enabled):
        self.mapTipsVisible = enabled
        if not self.mapTipsVisible:
            self.mapTipsTimer.stop()
            self.mapTip.clear(self.canvas)
            if QvApp().testVersioQgis(3, 40): self.clear()

    def showMapTip(self):
        """ SLOT. Show MapTips on the map """
        if self.mapTipsVisible and self.canvas.underMouse():
            pointerPos = self.canvas.mouseLastXY()
            layer = self.canvas.currentLayer()
            if layer is not None and (not QvApp().testVersioQgis(3, 40) or layer.hasMapTips()):
                self.mapTip.showMapTip(layer, self.lastMapPosition, pointerPos, self.canvas)

    def clear(self):
        """Necesario para que los MapTips no se queden en la pantalla en la versión 3.40"""
        self.canvas.setCenter(self.canvas.center())

    def saveLastMousePosition(self, p):
        """ SLOT. Initialize the Timer to show MapTips on the map """
        if self.mapTipsVisible:
            self.lastMapPosition = p
            if self.canvas.underMouse():
                if QvApp().testVersioQgis(3, 40):
                    interval = min(300, self.mapTipsTimer.interval())
                    self.mapTip.clear(self.canvas, interval)
                    self.clear()
                else:
                    self.mapTip.clear(self.canvas)
                self.mapTipsTimer.start()

      