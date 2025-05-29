from qgis.core import *
from qgis.gui import *
from qgis.core.contextmanagers import qgisapp
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from moduls.QvApp import QvApp
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
# from moduls.QvCanvas import QvCanvas

projecteInicial = 'MapesOffline/qVista default map.qgs'

with qgisapp() as app:

    canvas = QgsMapCanvas()
    canvas.show()
    QvApp().mainApp = canvas
    atributos = QvAtributs(canvas)
    proyecto = QgsProject.instance()
    root = proyecto.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root,canvas)
    proyecto.read(projecteInicial)
    leyenda = QvLlegenda(canvas, atributos)
    leyenda.show()




