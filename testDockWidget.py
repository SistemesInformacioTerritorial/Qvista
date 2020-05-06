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

# QTBUG-65592
# -----------
# QDockWidget split position "jumps" when QMainWindow resized
#
# Comment:
#
# When I encountered this bug it seemed that anything which sets QDockAreaLayoutItem::KeepSize
# avoided the error. This includes things like undocking and re-docking widgets.
#
# My own terribly hacky workaround was thus:
#
#     QByteArray temp = saveState();
#     restoreState(temp);
#
# since restoreState sets the flag.
#

    win = QMainWindow()
    temp = win.saveState()  # Añadido para evitar bug

    canvas = QgsMapCanvas()
    
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

    win.setCentralWidget(canvas)
    
    boton = QPushButton('Botón de prueba')
    dw = QDockWidget("Dock Widget de prueba ", win)
    dw.setWidget(boton)
    win.addDockWidget(Qt.LeftDockWidgetArea, dw)
    
    win.restoreState(temp)  # Añadido para evitar bug
    win.show()

    project.read(projecteInicial)




