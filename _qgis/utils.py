# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsVectorLayer
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtCore import Qt, QPoint, QSize
from qgis.PyQt.QtWidgets import QMenu, QWidget
from moduls.QvFuncions import debugging
from moduls.QvApp import QvApp
from moduls.QvSingleton import singleton

@singleton
class QvIface:

    def __init__(self):
        self.init()
        self.inc = QPoint(120, 80)
        self.size = QSize(550, 500)
        QgsProject.instance().readProject.connect(self.init)

    def init(self):
        self.origin = QPoint(0, 0)

    # ************************ Funciones de iface recubiertas ************************

    def addVectorLayer(self, path, baseName, providerLib, options=QgsVectorLayer.LayerOptions(), addToLegend=True):
        vLayer = QgsVectorLayer(path, baseName, providerLib, options)
        if vLayer.isValid():
            mLayer = QgsProject.instance().addMapLayer(vLayer, addToLegend)
            return mLayer
        else:
            return None
        
    def mainWindow(self):
        return QvApp().mainApp

    def mapCanvas(self):
        mainW = self.mainWindow()
        if hasattr(mainW, 'canvas'):
            return mainW.canvas
        else:
            return mainW

    def iconSize(self, dockedToolbar=False):
        if dockedToolbar:
            return QSize(16, 16)
        else:
            return QSize(24, 24)

    def addDockWidget(self, area, dock):
        # self.mainWindow().addDockWidget(area, dock)
        if debugging():
            self.origin += self.inc
            dock.setGeometry(self.origin.x(), self.origin.y(), 
                            round(self.size.width() * QvApp().zoomFactor()),
                            round(self.size.height() * QvApp().zoomFactor()))
            # En Qt 6, se podría poner en la misma pantalla que qVista:
            # dock.setScreen(self.mainWindow().screen())
            dock.show()

    def removeDockWidget(self, dock):
        # self.mainWindow().removeDockWidget(dock)
        if debugging():  
            dock.hide()

    # ************************ Funciones no operativas ************************

    def messageBar(self):
        return QgsMessageBar()

    def addToolBarWidget(self, widget):
        return None

    def addToolBarIcon(self, action):
        return 0

    def pluginHelpMenu(self):
        return QMenu()

    def pluginMenu(self):
        return QMenu()

iface = QvIface()