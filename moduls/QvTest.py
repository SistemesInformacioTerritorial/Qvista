# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor
from qgis.core.contextmanagers import qgisapp

from moduls.QvApp import QvApp
from moduls.QvCanvas import QvCanvas
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs
import configuracioQvista as cfg

import multiprocessing as mp
import win32gui
import win32con


class QvProcess(mp.Process):

    @staticmethod
    def listenMsg(app, qInput, getMsg):
        while True:
            if not qInput.empty():
                getMsg(qInput.get())
            app.processEvents()

    def __init__(self, project=None):
        self.qInput = mp.Queue()
        self.qOutput = mp.Queue()
        self.project = project
        super().__init__(target=self.go)

    def go(self):
        with qgisapp() as app:

            self.qapp = QvApp()
            self.qapp.carregaIdioma(app, 'ca')

            self.canvas = QvCanvas()
            self.atributs = QvAtributs(self.canvas)
            self.llegenda = QvLlegenda(self.canvas, self.atributs)

            if self.project: self.llegenda.project.read(self.project)

            QvProcess.listenMsg(app, self.qInput, self.getMsg)

    def getMsg(self, msg):
        try:
            linea = msg.split('=')
            if len(linea) == 0:
                return
            self.command = linea[0].lower() + 'Get'
            if len(linea) == 1:
                self.params = None
            else:
                self.params = linea[1]
            cmd = getattr(self, self.command, None)
            if cmd is not None:
                cmd()
        except Exception as e:
            print(str(e))

    def showGet(self):
        params = self.params.split('&')
        self.canvas.setWindowFlags(qtCor.Qt.FramelessWindowHint) #  and qtCor.Qt.WindowStaysOnTopHint)
        self.canvas.setGeometry(int(params[0]), int(params[1]), int(params[2]), int(params[3]))
        win32gui.SetWindowPos(self.canvas.winId().__int__(), win32con.HWND_TOPMOST,
                              int(params[0]), int(params[1]), int(params[2]), int(params[3]), 0)
        self.canvas.show()

    def hideGet(self):
        self.llegenda.hide()
        self.canvas.hide()  
        self.atributs.hide()

    def centerGet(self):
        params = self.params.split('&')
        self.canvas.setCenter(qgCor.QgsPointXY(float(params[1]), float(params[2])))
        self.canvas.zoomScale(float(params[0]))

    def readGet(self):
        params = self.params.split('&')
        self.llegenda.project.read(params[0])
        self.namePut()

    def nameGet(self):
        self.namePut()

    def namePut(self):
        self.qOutput.put("NAME=" + self.llegenda.project.title())

if __name__ == "__main__":

    # proc = QvProcess(cfg.projecteInicial)
    # proc.start()
    # exit(0)

    def action(msg):
        try:
            linea = msg.split('=')

            if linea[0] == "NAME":
                mapes.setTabText(1, linea[1])

        except Exception as e:
            print(str(e))

    proc = QvProcess('D:/Temp/Test_edició.qgs')
    proc.start()

    with qgisapp() as app:

        qapp = QvApp()
        qapp.carregaIdioma(app, 'ca')

        canvas = QvCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        llegenda.project.read(cfg.projecteInicial)

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(50, 300, 1050, 250)

        mapes = qtWdg.QTabWidget()
        mapes.setWindowTitle('Mapes')
        mapes.setGeometry(400, 50, 900, 600)
        mapes.addTab(canvas, llegenda.project.title())
        canvas2 = qtWdg.QWidget()
        mapes.addTab(canvas2, '')
        mapes.show()
        proc.qInput.put("NAME")

        llegenda.show()
        canvas.show()

        # id = queue.get()
        # print(id)
        # win = qtGui.QWindow.fromWinId(id)

        # Acciones de usuario para el menú

        def putCenter():
            linea = f"CENTER={canvas.scale()}&{canvas.center().x()}&{canvas.center().y()}"
            proc.qInput.put(linea)

        def putShow():
            g = canvas.geometry()
            p1 = canvas.mapToGlobal(qtCor.QPoint(0, 0))
            p2 = canvas.mapToGlobal(qtCor.QPoint(g.width(), g.height()))
            # hwnd = canvas2.winId().__int__() 
            # linea = f"SHOW&{p1.x()}&{p1.y()}&{p2.x()-p1.x()}&{p2.y()-p1.y()}&{hwnd}"
            linea = f"SHOW={p1.x()}&{p1.y()}&{p2.x()-p1.x()}&{p2.y()-p1.y()}"
            proc.qInput.put(linea)

        def putRead():
            mapa = 'C:/temp/qVista/Dades Usuari/TestZones.qgs'
            linea = f"READ={mapa}"
            proc.qInput.put(linea)

        act = qtWdg.QAction()
        act.setText("SHOW")
        act.triggered.connect(putShow)
        llegenda.accions.afegirAccio("SHOW", act)

        act = qtWdg.QAction()
        act.setText("HIDE")
        act.triggered.connect(lambda: proc.qInput.put("HIDE"))
        llegenda.accions.afegirAccio("HIDE", act)

        act = qtWdg.QAction()
        act.setText("CENTER")
        act.triggered.connect(putCenter)
        llegenda.accions.afegirAccio("CENTER", act)

        act = qtWdg.QAction()
        act.setText("READ")
        act.triggered.connect(putRead)
        llegenda.accions.afegirAccio("READ", act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'none':
                llegenda.menuAccions.append('separator')
                llegenda.menuAccions.append('SHOW')
                llegenda.menuAccions.append('CENTER')
                llegenda.menuAccions.append('HIDE')
                llegenda.menuAccions.append('READ')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        llegenda.clicatMenuContexte.connect(menuContexte)

        QvProcess.listenMsg(app, proc.qOutput, action)

    # import multiprocessing as mp
    # from moduls.QvTest import test

    # q = mp.Queue()

    # p1 = mp.Process(target=test, args=(q,))
    # p1.start()
    # print('Start 1')

    # p2 = mp.Process(target=test, args=(q, 'C:/temp/qVista/Dades Usuari/PruebaPuntosPoligonos.qgs',))
    # p2.daemon = True
    # p2.start()
    # print('Start 2')

    # q.put('SHOW')
    
    # p1.join()
    # # p2.join()
    # print('Join')
