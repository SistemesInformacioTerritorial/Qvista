# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsVectorLayerCache, QgsFeature

import plotly as py
import plotly.graph_objs as go

def testBarChart():
    trace1 = go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[20, 14, 23],
        name='SF Zoo'
    )
    trace2 = go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[12, 18, 29],
        name='LA Zoo'
    )

    data = [trace1, trace2]
    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)
    py.offline.plot(fig,  auto_open=True)

def layerBarChart(layer, selected=False):
    if selected:
        iterator = layer.getSelectedFeatures
    else:
        iterator = layer.getFeatures

    x = []
    y1 = []
    y2 = []
    for feature in iterator():
        x.append(feature['C_Distri'])
        y1.append(feature['Dones'])
        y2.append(feature['Homes'])

    trace1 = go.Bar(x, y1, name='Dones')
    trace2 = go.Bar(x, y2, name='Homes')

    data = [trace1, trace2]
    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)
    py.offline.plot(fig,  auto_open=True)
