from qgis.core import *
from qgis.gui import *
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QMainWindow, QDockWidget, QPushButton

from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvCanvas import QvCanvas

projecteInicial = 'MapesOffline/qVista default map.qgs'

with qgisapp() as app:
    win = QMainWindow()


    # canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True)
    canvas = QgsMapCanvas()
    win.setCentralWidget(canvas)
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root,canvas)

    tablaAtributos = QvAtributs(canvas)
    # leyenda = QvLlegenda(canvas, tablaAtributos)
    boton = QPushButton('Botón de prueba')
    dw = QDockWidget("Dock Widget de prueba ", win)
    dw.setWidget(boton)
    win.addDockWidget(Qt.LeftDockWidgetArea, dw)
    win.show()
    project.read(projecteInicial)




