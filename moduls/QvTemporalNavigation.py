# -*- coding: utf-8 -*-

# from qgis.core import QgsProject, QgsLayoutExporter, QgsReport, QgsFeedback

from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsTemporalControllerWidget

from moduls.QvFuncions import debugging
import os 

def navegacioTemporal(qV, docked=True):

    from qgis.gui import QgsTemporalControllerWidget
    from qVista import QvDockWidget
    from moduls.QvApp import QvApp

    if docked:
        wController = QgsTemporalControllerWidget() 
        tempControler = wController.temporalController()
        qV.canvas.setTemporalController(tempControler)

        qV.dwNavegacioTemporal = QvDockWidget('Navegació temporal')
        qV.dwNavegacioTemporal.setContextMenuPolicy(Qt.PreventContextMenu)
        qV.dwNavegacioTemporal.setObjectName("temporal")
        qV.dwNavegacioTemporal.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        qV.dwNavegacioTemporal.setContentsMargins(0, 0, 0, 0)

        qV.dwNavegacioTemporal.setMinimumHeight(round(150*QvApp().zoomFactor()))
        qV.dwNavegacioTemporal.setMaximumHeight(round(150*QvApp().zoomFactor()))
        qV.addDockWidget(Qt.BottomDockWidgetArea, qV.dwNavegacioTemporal)

        qV.dwNavegacioTemporal.setWidget(wController)
        qV.dwNavegacioTemporal.setWindowFlag(Qt.Window)
        qV.dwNavegacioTemporal.show()

    else:
        qV.dwNavegacioTemporal = QgsTemporalControllerWidget() 
        tempControler =  qV.dwNavegacioTemporal.temporalController()
        qV.canvas.setTemporalController(tempControler)
        qV.dwNavegacioTemporal.setWindowTitle('Navegació temporal')
        qV.dwNavegacioTemporal.setGeometry(100, 500, 1000, 150)
        qV.dwNavegacioTemporal.setWindowFlags(Qt.WindowStaysOnTopHint)
        qV.dwNavegacioTemporal.show()


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.core import QgsLayoutExporter, QgsReport, QgsApplication
    from qgis.gui import QgsMapCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvApp import QvApp
    from moduls.QvAtributs import QvAtributs
    from DataPlotly.QvDataPlotly import QvDataPlotly
    from qgis.analysis import QgsNativeAlgorithms
    from qgis.PyQt.QtWidgets import QWidget, QHBoxLayout, QPushButton
    
    import sys

    with qgisapp() as app:

        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        canvas = QgsMapCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        # sys.path.append(r'C:\OSGeo4W\apps\qgis-ltr\python\plugins')
        # import processing

        # nAlgs = QgsNativeAlgorithms()
        # nAlgs.loadAlgorithms()
        # QgsApplication.processingRegistry().addProvider(nAlgs) 

        # llegenda.project.read('projectes/Illes.qgs')
        llegenda.project.read("D:/qVista/EndrecaSoroll/sorollEndreca.qgs")

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()
        
        # Abrimos una tabla de atributos
        # layer = llegenda.capaPerNom('Illes')
        # atributs.obrirTaula(layer)

        # atributs.setWindowTitle('Atributs')
        # atributs.setGeometry(50, 500, 1050, 250)
        # llegenda.obertaTaulaAtributs.connect(atributs.show)


