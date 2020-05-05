from qgis.core import *
from qgis.gui import *
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QMainWindow, QDockWidget

from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
from moduls.QvCanvas import QvCanvas

projecteInicial = 'MapesOffline/qVista default map.qgs'

with qgisapp() as app:
    win = QMainWindow()

    llistaBotons = ['streetview','apuntar', 'zoomIn', 'zoomOut', 'panning', 'centrar', 'enrere', 'endavant', 'maximitza']
        
    # canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True)
    canvas = QgsMapCanvas()
    canvas.show()
    win.setCentralWidget(canvas)
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root,canvas)

    tablaAtributos = QvAtributs(canvas)
    # leyenda = QvLlegenda(canvas, tablaAtributos)
    leyenda = QgsMapCanvas()
    leyenda.show()
    dw = QDockWidget("hola", win)
    dw.setWidget(leyenda)
    win.addDockWidget(Qt.LeftDockWidgetArea, dw)
    win.show()
    project.read(projecteInicial)




