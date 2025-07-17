# -*- coding: utf-8 -*-

import os
_subdirPlugins = r"\QGIS\QGIS3\profiles\default\python\plugins"
_dirPlugins = os.environ.get('APPDATA') + _subdirPlugins
os.sys.path.insert(0, _dirPlugins)
from DataPlotly.data_plotly import DataPlotly
from _qgis.utils import iface
from moduls.QvSingleton import singleton

@singleton
class QvDataPlotly(DataPlotly):
    """_Clase para inicializar DataPlotly desde qVista.
    Se usa el código instalado por el plugin DataPlotly en QGIS.
    Mejor crearla desde QvLlegenda.
    """
    def __init__(self, docWidgets=False):
        iface.docWidgets = docWidgets  # Si es True, se muestran los docks de DataPlotly
        DataPlotly.__init__(self, iface)
        self.initGui()
        self.versio = self.dataPlotlyVersion()

    def dataPlotlyVersion(self):
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(_dirPlugins + r"\DataPlotly\metadata.txt")
            return config.get('general', 'version')
        except Exception as e:
            print(str(e))
            return self.VERSION
