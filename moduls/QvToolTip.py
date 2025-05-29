# -*- coding: utf-8 -*-

from qgis.PyQt import QtCore
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
        self.layer = None
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

    def clear(self):
        """Necesario para que los MapTips no se queden en la pantalla en la versión 3.40"""
        self.canvas.setCenter(self.canvas.center())

    def toggleMapTips(self, enabled):
        self.mapTipsVisible = enabled
        if not self.mapTipsVisible:
            self.mapTipsTimer.stop()
            self.mapTip.clear(self.canvas)
            if QvApp().testVersioQgis(3, 40): self.clear()

    def checkCurrentLayer(self):
        self.layer = self.canvas.currentLayer()
        return self.layer is not None and (not QvApp().testVersioQgis(3, 40) or self.layer.hasMapTips())

    def checkMapTip(self):
        return self.mapTipsVisible and self.canvas.underMouse() and self.checkCurrentLayer()

    def showMapTip(self):
        """ SLOT. Show MapTips on the map """
        if self.checkMapTip():
            self.mapTip.showMapTip(self.layer, self.lastMapPosition, self.canvas.mouseLastXY(), self.canvas)

    def saveLastMousePosition(self, p):
        """ SLOT. Initialize the Timer to show MapTips on the map """
        if self.checkMapTip():
            self.lastMapPosition = p
            if QvApp().testVersioQgis(3, 40):
                interval = min(300, self.mapTipsTimer.interval())
                self.mapTip.clear(self.canvas, interval)
                self.clear()
            else:
                self.mapTip.clear(self.canvas)
            self.mapTipsTimer.start()

      