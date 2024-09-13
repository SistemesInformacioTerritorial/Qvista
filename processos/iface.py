# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsVectorLayer
from moduls.QvApp import QvApp

class iface:

    def addVectorLayer(path, baseName, providerLib, options=QgsVectorLayer.LayerOptions(), addToLegend=True):
        vLayer = QgsVectorLayer(path, baseName, providerLib, options)
        if vLayer.isValid():
            mLayer = QgsProject.instance().addMapLayer(vLayer, addToLegend)
            return mLayer
        else:
            return None
