# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from moduls.QvApp import QvApp

class QvNavegacioTemporal:

    @staticmethod
    def widget():
        qV = QvApp().mainApp
        if qV is None: return None
        return qV.dwNavegacioTemporal

    @staticmethod
    def switch():
        widget = QvNavegacioTemporal.widget()
        if widget is None: return
        widget.setVisible(not widget.isVisible())

    @staticmethod
    def hide():
        widget = QvNavegacioTemporal.widget()
        if widget is None: return
        widget.hide()

    @staticmethod
    def show():
        widget = QvNavegacioTemporal.widget()
        if widget is None: return
        widget.show()

    @staticmethod
    def isActive(layer):
        tempProps = layer.temporalProperties()
        if tempProps is None: return False
        return tempProps.isActive()


# def navegacioTemporal(docked=False):

#     qV = QvApp().mainApp
#     if qV is None: return

#     if docked:
#         wController = QgsTemporalControllerWidget() 
#         tempControler = wController.temporalController()
#         qV.canvas.setTemporalController(tempControler)

#         qV.dwNavegacioTemporal = QvDockWidget('Navegació temporal')
#         qV.dwNavegacioTemporal.setContextMenuPolicy(Qt.PreventContextMenu)
#         qV.dwNavegacioTemporal.setObjectName("temporal")
#         qV.dwNavegacioTemporal.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
#         qV.dwNavegacioTemporal.setContentsMargins(0, 0, 0, 0)

#         qV.dwNavegacioTemporal.setMinimumHeight(round(150*QvApp().zoomFactor()))
#         qV.dwNavegacioTemporal.setMaximumWidth(round(150*QvApp().zoomFactor()))
#         qV.addDockWidget(Qt.BottomDockWidgetArea, qV.dwNavegacioTemporal)

#         qV.dwNavegacioTemporal.setWidget(wController)
#         qV.dwNavegacioTemporal.setWindowFlag(Qt.Window)
#         qV.dwNavegacioTemporal.show()

#     else:
#         qV.dwNavegacioTemporal = QgsTemporalControllerWidget() 
#         tempControler =  qV.dwNavegacioTemporal.temporalController()
#         qV.canvas.setTemporalController(tempControler)
#         qV.dwNavegacioTemporal.setWindowTitle('Navegació temporal')
#         qV.dwNavegacioTemporal.setGeometry(100, 500, 1000, 150)
#         qV.dwNavegacioTemporal.setWindowFlags(Qt.WindowStaysOnTopHint)
#         qV.dwNavegacioTemporal.show()
