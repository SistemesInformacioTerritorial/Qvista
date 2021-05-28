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
import inspect

class QvQueueCmds:
    def __init__(self, app, queue, cmds, prefijo='do'):
        self.app = app
        self.qInput = queue
        self.cmds = cmds
        self.prefijo = prefijo

    def listenMsg(self):
        while True:
            if not self.qInput.empty():
                self.readMsg(self.qInput.get())
            self.app.processEvents()

    def readMsg(self, msg):
        print('QvQueueCmds', msg)
        try:
            linea = msg.split('=')
            if len(linea) == 0:
                return
            command = self.prefijo + linea[0].capitalize()
            if len(linea) == 1:
                params = None
            else:
                params = linea[1].split('&')
            if inspect.ismethod(self.cmds) or inspect.isfunction(self.cmds):
                doCommand = self.cmds
            else:
                doCommand = getattr(self.cmds, command, None)
            if doCommand is None:
                print('No existe función', command)
            else:
                if params is None:
                    doCommand()
                else:
                    doCommand(params)
        except Exception as e:
            print(str(e))

class QvProcess(mp.Process):

    def __init__(self, project=None):
        self.qInput = mp.Queue()
        self.qOutput = mp.Queue()

        self.app = None
        self.qapp = None
        self.canvas = None
        self.atributs = None
        self.llegenda = None
        self.project = project
        super().__init__(target=self.go)

        self.mainCanvas = None
        self.outCanvas = None
        self.paramsShow = []
        self.input = None

    def go(self):
        with qgisapp() as app:

            self.app = app
            self.qapp = QvApp()
            self.qapp.carregaIdioma(app, 'ca')

            self.canvas = QvCanvas()
            self.atributs = QvAtributs(self.canvas)
            self.llegenda = QvLlegenda(self.canvas, self.atributs)

            if self.project:
                self.llegenda.project.read(self.project)
                self.outName()
            
            self.input = QvQueueCmds(self.app, self.qInput, self)
            self.input.listenMsg()

    def newShow(self, params):
        if len(self.paramsShow) == 0:
            return True
        for i in range(4):
            if self.paramsShow[i] != params[i]:
                return True
        return False

    def saveShow(self, params):
        self.paramsShow.clear()
        for i in range(4):
            self.paramsShow.append(params[i])

    def doShow(self, params):
        self.canvas.setWindowFlags(qtCor.Qt.FramelessWindowHint) #  and qtCor.Qt.WindowStaysOnTopHint)
        self.canvas.setGeometry(int(params[0]), int(params[1]), int(params[2]), int(params[3]))
        win32gui.SetWindowPos(self.canvas.winId().__int__(), win32con.HWND_TOPMOST,
                              int(params[0]), int(params[1]), int(params[2]), int(params[3]), 0)
        self.canvas.show()
        self.saveShow(params)

    def doRefresh(self, params):
        if not self.newShow(params):
            return
        self.doShow(params)

    def doHide(self):
        self.llegenda.hide()
        self.canvas.hide()  
        self.atributs.hide()

    def doCenter(self, params):
        self.canvas.setCenter(qgCor.QgsPointXY(float(params[1]), float(params[2])))
        self.canvas.zoomScale(float(params[0]))

    def doRead(self, params):
        self.llegenda.project.read(params[0])
        self.outName()

    def doName(self):
        self.outName()

    def outName(self):
        self.qOutput.put("NAME=" + self.llegenda.project.title())

    def connectCanvas(self, mainCanvas, outCanvas):
        self.mainCanvas = mainCanvas
        self.outCanvas = outCanvas

    def resizeCanvas(self, resizeEvent):
        pass

    def noCanvas(self):
        return self.mainCanvas is None or self.outCanvas is None

    def sendMsg(self, command, *params):
        linea = command
        sep = '='
        for p in params:
            linea += sep + str(p)
            if sep == '=': sep = '&'
        self.qInput.put(linea)

    def sendCenter(self):
        if self.noCanvas(): return
        self.sendMsg('center', self.mainCanvas.scale(), self.mainCanvas.center().x(), self.mainCanvas.center().y())

    def sendRange(self, cmd):
        if self.noCanvas(): return
        g = self.outCanvas.geometry()
        p1 = self.outCanvas.mapToGlobal(qtCor.QPoint(0, 0))
        p2 = self.outCanvas.mapToGlobal(qtCor.QPoint(g.width(), g.height()))
        self.sendMsg(cmd, p1.x(), p1.y(), p2.x()-p1.x(), p2.y()-p1.y())

    def sendShow(self):
        self.sendRange('show')

    def sendRefresh(self):
        self.sendRange('refresh')

    def sendRead(self):
        self.sendMsg('read', 'C:/temp/qVista/Dades Usuari/TestZones.qgs')

    def sendHide(self):
        self.sendMsg('hide')

    def sendName(self):
        self.sendMsg('name')


if __name__ == "__main__":

    # proc = QvProcess(cfg.projecteInicial)
    # proc.start()
    # exit(0)

    class QvWidget(qtWdg.QWidget):

        refresh = qtCor.pyqtSignal()

        def __init__(self, ms=300):
            super().__init__()
            self.ms = ms
            self.timer = qtCor.QTimer()
            self.timer.timeout.connect(self.sendRefresh)
            self.timer.setSingleShot(True)
            self.installEventFilter(self)

        def eventFilter(self, obj, event):
            # print(event.type())
            # 12 - Paint
            # 13 - Move
            # 14 - Resize
            # 17 - Show
            # 18 - Hide
            # 24 - Window Activate 
            # 25 - Window Deactivate
            # 126 - Z-order change
            # if event.type() == qtCor.QEvent.Paint or event.type() == qtCor.QEvent.Move or event.type() == qtCor.QEvent.Resize:
            if event.type() == qtCor.QEvent.Move or event.type() == qtCor.QEvent.Resize:
                self.timer.start(self.ms)
                return True
            return False

        def sendRefresh(self):
            self.refresh.emit()

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

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(50, 300, 1050, 250)

        mapes = qtWdg.QTabWidget()
        mapes.setWindowTitle('Mapes')
        mapes.setGeometry(400, 50, 900, 600)
        mapes.addTab(canvas, llegenda.project.title())
        # canvas2 = qtWdg.QWidget()
        canvas2 = QvWidget()
        mapes.addTab(canvas2, '')

        llegenda.show()
        canvas.show()
        mapes.show()

        def getName(params):
            mapes.setTabText(1, params[0])

        def tabChanged(index):
            if index == 1:
                proc.sendShow()
            else:
                proc.sendHide()

        proc.connectCanvas(canvas, canvas2)
        mapes.currentChanged.connect(tabChanged)
        canvas2.refresh.connect(proc.sendRefresh)

        # id = queue.get()
        # print(id)
        # win = qtGui.QWindow.fromWinId(id)

        # Acciones de usuario para el menú

        act = qtWdg.QAction()
        act.setText("SHOW")
        act.triggered.connect(proc.sendShow)
        llegenda.accions.afegirAccio("SHOW", act)

        act = qtWdg.QAction()
        act.setText("HIDE")
        act.triggered.connect(proc.sendHide)
        llegenda.accions.afegirAccio("HIDE", act)

        act = qtWdg.QAction()
        act.setText("CENTER")
        act.triggered.connect(proc.sendCenter)
        llegenda.accions.afegirAccio("CENTER", act)

        act = qtWdg.QAction()
        act.setText("READ")
        act.triggered.connect(proc.sendRead)
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

        input = QvQueueCmds(app, proc.qOutput, getName)
        input.listenMsg()


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
