# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsVectorLayerCache, QgsFeature
from qgis.PyQt import QtWebKitWidgets
from qgis.PyQt.QtCore import QUrl

import plotly as py
import plotly.graph_objs as go


class QvChart(QtWebKitWidgets.QWebView):
    def __init__(self, ruta=None):
        super(QvChart, self).__init__()
        if ruta is not None:
            self.load(QUrl(ruta))

    def densitatBarChart(self, layer, orientation='v', selected=False):
        if selected:
            iterator = layer.getSelectedFeatures
        else:
            iterator = layer.getFeatures

        x = []
        y = []
        for feature in iterator():
            x.append(feature['N_Distri'])
            y.append(round(
                (feature['Dones'] + feature['Homes']) /
                (feature['Area'] / 1000000), 2))

        if orientation == 'v':
            trace = go.Bar(x=x, y=y, name='Habitants/km2', orientation=orientation)
        else:
            trace = go.Bar(x=y, y=x, name='Habitants/mm2', orientation=orientation)

        data = [trace]
        layout = go.Layout(
            title='Densitat de població per districte<br />(Habitants per km2)',
            barmode='stack'
        )

        fig = go.Figure(data=data, layout=layout)
        fname = 'D:/Temp/den_temp.html'
        py.offline.plot(fig,  filename=fname, auto_open=False)
        self.load(QUrl('file:///'+fname))

    def poblacioBarChart(self, layer, orientation='v', selected=False):
        if selected:
            iterator = layer.getSelectedFeatures
        else:
            iterator = layer.getFeatures

        x = []
        y1 = []
        y2 = []
        for feature in iterator():
            x.append(feature['N_Distri'])
            y1.append(feature['Dones'])
            y2.append(feature['Homes'])

        if orientation == 'v':
            trace1 = go.Bar(x=x, y=y1, name='Dones', orientation=orientation)
            trace2 = go.Bar(x=x, y=y2, name='Homes', orientation=orientation)
        else:   
            trace1 = go.Bar(x=y1, y=x, name='Dones', orientation=orientation)
            trace2 = go.Bar(x=y2, y=x, name='Homes', orientation=orientation)

        data = [trace1, trace2]
        layout = go.Layout(
            title='Població per districte',
            barmode='stack'
        )

        fig = go.Figure(data=data, layout=layout)
        fname = 'D:/Temp/pob_temp.html'
        py.offline.plot(fig,  filename=fname, auto_open=False)
        self.load(QUrl('file:///'+fname))
