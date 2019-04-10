# -*- coding: utf-8 -*-

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
        habs = 0
        area = 0
        primero = True
        for feature in iterator():
            if primero:
                nDist = feature.fieldNameIndex('N_Distri')
                nDones = feature.fieldNameIndex('Dones')
                nHomes = feature.fieldNameIndex('Homes')
                nArea = feature.fieldNameIndex('Area')
                primero = False

            habs += feature[nDones] + feature[nHomes]
            area += feature[nArea]

            x.append(feature[nDist])
            y.append(round(
                (feature[nDones] + feature[nHomes]) /
                (feature[nArea] / 1000000), 2))

        media = round(habs / (area / 1000000), 2)
        if orientation == 'v':
            trace = go.Bar(x=x, y=y,
                           name='Habitants/Km2', orientation=orientation)
        else:
            trace = go.Bar(x=y, y=x,
                           name='Habitants/Km2', orientation=orientation)

        data = [trace]
        layout = go.Layout(
            title='Densitat de població per districte<br />Habitants per Km<sup>2</sup>',
            titlefont=dict(
                color='green'
            ),
            barmode='stack',
            separators=',.',
            xaxis=dict(
                title='DISTRICTES',
                titlefont=dict(
                    # family='Arial, sans-serif',
                    size=18,
                    color='grey'
                ),
                showticklabels=True,
                tickangle=0,
                ticks=''
                # tickfont=dict(
                #     family='Arial, sans-serif',
                #     size=10,
                #     color='black'
                # ),
            ),
            yaxis=dict(
                exponentformat='none',
                hoverformat=',.0f',
                ticks=''
            ),
            shapes=[
                dict(
                    type='line',
                    x0=-0.5,
                    y0=media,
                    x1=10,
                    y1=media,
                    line=dict(
                        color=('rgb(50, 171, 96)'),
                        width=2,
                        dash='dash'
                    )
                )
            ],
            annotations=[
                dict(
                    x=10,
                    y=media+100,
                    xref='x',
                    yref='y',
                    text='Mitjana<br /><b>'+"{:,}".format(round(media)).replace(',', '.')+'</b>',
                    font=dict(
                        size=12,
                        color='gray'
                    ),
                    showarrow=True,
                    arrowhead=7,
                    arrowcolor=('rgb(50, 171, 96)'),
                    ax=0,
                    ay=-40
                )
            ]
        )

        fig = go.Figure(data=data, layout=layout)
        fname = 'C:/temp/den_chart.html'
        py.offline.plot(fig, filename=fname, auto_open=False)
        self.load(QUrl('file:///' + fname))

    def poblacioBarChart(self, layer, orientation='v', selected=False):
        if selected:
            iterator = layer.getSelectedFeatures
        else:
            iterator = layer.getFeatures

        x = []
        y1 = []
        y2 = []
        primero = True
        for feature in iterator():
            if primero:
                nDist = feature.fieldNameIndex('N_Distri')
                nDones = feature.fieldNameIndex('Dones')
                nHomes = feature.fieldNameIndex('Homes')
                primero = False

            x.append(feature[nDist])
            y1.append(feature[nDones])
            y2.append(feature[nHomes])

        if orientation == 'v':
            trace1 = go.Bar(x=x, y=y1, name='Dones', orientation=orientation)
            trace2 = go.Bar(x=x, y=y2, name='Homes', orientation=orientation)
        else:
            trace1 = go.Bar(x=y1, y=x, name='Dones', orientation=orientation)
            trace2 = go.Bar(x=y2, y=x, name='Homes', orientation=orientation)

        data = [trace1, trace2]
        layout = go.Layout(
            title='Població per districte',
            barmode='stack',
            separators=',.',
            xaxis=dict(
                title='DISTRICTES',
                titlefont=dict(
                    # family='Arial, sans-serif',
                    size=18,
                    color='grey'
                ),
            ),
            yaxis=dict(
                exponentformat='none',
                showexponent='none'
            )
        )

        fig = go.Figure(data=data, layout=layout)
        fname = 'C:/temp/pob_chart.html'
        py.offline.plot(fig, filename=fname, auto_open=False)
        self.load(QUrl('file:///' + fname))
