# -*- coding: utf-8 -*-

# from qgis.core import QgsProject, QgsLayoutExporter, QgsReport, QgsFeedback

from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsTemporalControllerWidget

from moduls.QvFuncions import debugging
import os 

def navegacioTemporal(parent):

    from qgis.gui import QgsTemporalControllerWidget

    # Como widget
    parent.wNavegacioTemporal = QgsTemporalControllerWidget() 
    tempControler =  parent.wNavegacioTemporal.temporalController()
    parent.canvas.setTemporalController(tempControler)
    parent.wNavegacioTemporal.setWindowTitle('Navegació temporal')
    parent.wNavegacioTemporal.setGeometry(50, 500, 1050, 150)
    parent.wNavegacioTemporal.show()

    # Como dock widget
    # wController = QgsTemporalControllerWidget() 
    # tempControler = wController.temporalController()
    # self.canvas.setTemporalController(tempControler)
    # wController.resize(1000, 150)
    # self.dwNavegacioTemporal = QvDockWidget()
    # self.dwNavegacioTemporal.setWidget(wController)
    # self.dwNavegacioTemporal.setWindowTitle('Navegació temporal')
    # self.addDockWidget(Qt.BottomDockWidgetArea, self.dwNavegacioTemporal)
    # self.dwNavegacioTemporal.show()    

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

