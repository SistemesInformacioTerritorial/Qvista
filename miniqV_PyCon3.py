from qgis.core import *
from qgis.gui import *
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *

from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs

projecteInicial = 'MapesOffline/qVista default map.qgs'

with qgisapp() as app:
    canvas = QgsMapCanvas()
    canvas.show()

    project = QgsProject.instance()
    root = project.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root,canvas)

    tablaAtributos = QvAtributs(canvas)
    leyenda = QvLlegenda(canvas, tablaAtributos)
    leyenda.show()
    project.read(projecteInicial)




