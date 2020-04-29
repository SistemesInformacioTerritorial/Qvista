# -*- coding: utf-8 -*-

from qgis.core import QgsExpressionContextUtils
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication

import moduls.QvMapVars as mv

from collections import OrderedDict


class QvDiagrama:

    @staticmethod
    def capaAmbMapificacio(capa):
        var = QgsExpressionContextUtils.layerScope(capa).variable(mv.MAP_ID)
        return var

    @staticmethod
    def capaAmbDiagrama(capa, zones=('Districte', 'Barri')):
        var = QvDiagrama.capaAmbMapificacio(capa)
        if var is None:
            return ''
        for zona in zones:
            if f'Zona: {zona}\n' in var:
                return zona
        return ''

    @staticmethod
    def barres(capa):
        try:
            QApplication.instance().setOverrideCursor(Qt.WaitCursor)
            from moduls.QvPlotly import QvPlot, QvChart
            regs = dict()
            for f in capa.getFeatures():
                regs[f['CODI'] + '-' + f['DESCRIPCIO']] = f['RESULTAT']
            lista = OrderedDict(sorted(regs.items()))
            pl = QvPlot.barres(
                    list(lista.keys()), list(lista.values()),
                    titol='Capa ' + capa.name() + ' - Diagrama de barres per ' +
                          QvDiagrama.capaAmbDiagrama(capa).lower())
            return QvChart.visorGrafic(pl)
        except Exception as e:
            print(str(e))
            return None
        finally:
            QApplication.instance().restoreOverrideCursor()
