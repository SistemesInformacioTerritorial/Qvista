# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.PyQt.QtCore as qtCor
from qgis.core.contextmanagers import qgisapp
from moduls.QvApp import QvApp
from moduls.QvCanvas import QvCanvas
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
import configuracioQvista as cfg

canvas = None
atributs = None
llegenda = None

def action(msg, qOutput):
    global canvas
    global atributs
    global llegenda

    try:
        linea = msg.split('&')

        if linea[0] == 'SHOW':
            # llegenda.show()
            canvas.setWindowFlags(qtCor.Qt.FramelessWindowHint) #  and qtCor.Qt.WindowStaysOnTopHint)
            canvas.setGeometry(int(linea[1]), int(linea[2]), int(linea[3]), int(linea[4]))
            canvas.setFocus()
            canvas.show()

        elif linea[0] == 'HIDE':
            llegenda.hide()
            canvas.hide()  
            atributs.hide()

        elif linea[0] == "CENTER":
            s = float(linea[1])
            p = qgCor.QgsPointXY(float(linea[2]), float(linea[3]))
            canvas.setCenter(p)
            canvas.zoomScale(s)

        elif linea[0] == "ZONES":
            llegenda.project.read('C:/temp/qVista/Dades Usuari/TestZones.qgs')
            qOutput.put("NAME&" + llegenda.project.title())

        elif linea[0] == "NAME":
            qOutput.put("NAME&" + llegenda.project.title())

    except Exception as e:
        print(str(e))


def listenMsg(app, qInput, qOutput):
    while True:
        if not qInput.empty():
            action(qInput.get(), qOutput)
        app.processEvents()

def test(qInput=None, qOutput=None, project=None):
    global canvas
    global atributs
    global llegenda

    with qgisapp() as app:

        if project is None:
            project = cfg.projecteInicial
            main = True
            inc = 0
        else:
            main = False
            inc = 500

        qapp = QvApp()
        qapp.carregaIdioma(app, 'ca')

        canvas = QvCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        llegenda.project.read(project)

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50+inc, 300, 400)

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50+inc, 700, 400)

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(50, 300+inc, 1050, 250)

        if main:
            llegenda.show()
            canvas.show()  
        else:
            if qInput and qOutput:
                listenMsg(app, qInput, qOutput)

if __name__ == "__main__":

    test()