# -*- coding: utf-8 -*-

# def stackedBarChart(layer, selected=False):
# try:
#     path, _ = QtWidgets.QFileDialog.getSaveFileName(
#         self, 'Desa dades a arxiu', '', 'CSV (*.csv)')
#     if path is not None:
#         with open(path, 'w', newline='') as stream:
#             writer = csv.writer(
#                 stream, delimiter=';', quotechar='¨',
#                 quoting=csv.QUOTE_MINIMAL)
#             writer.writerow(layer.fields().names())
#             if selected:
#                 iterator = layer.getSelectedFeatures
#             else:
#                 iterator = layer.getFeatures
#             for feature in iterator():
#                 writer.writerow(feature.attributes())
#     return path
# except Exception as e:
#     print(str(e))
#     return None

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
