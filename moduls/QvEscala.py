# -*- coding: utf-8 -*-

from qgis.core import QgsExpressionContextUtils


class QvEscala():
    def __init__(self, canvas):
        self.canvas = canvas
        self.llista = None
        self.selec = True

    def nouProjecte(self, projecte):
        self.lliure()
        llista = self.varEscales(projecte)
        if llista is not None:
            self.fixe(llista)

    def netejaEscales(self, var):
        if var is not None:
            # Eliminar separadores y convertirlos en blancos
            for c in "\"'’,;":
                var = var.replace(c, " ")
            # Sustituir grupos de blancos por uno
            var = " ".join(var.split())
        return var

    def varEscales(self, projecte):
        try:
            var = QgsExpressionContextUtils.projectScope(projecte).variable('qV_escales')
            var = self.netejaEscales(var)
            if var is not None:
                llista = list(map(int, var.split(' ')))
                if llista is not None and (len(llista) > 0):
                    return llista
            return None
        except Exception as e:
            print(str(e))
            return None

    def fixe(self, llista=None):
        if llista is None:
            self.llista = [500, 1000, 2500,
                           5000, 10000, 25000,
                           50000, 100000, 250000]
        else:
            self.llista = llista
        self.selec = False
        self.canvas.scaleChanged.connect(self.selecEscala)

    def lliure(self):
        if self.llista is not None:
            self.canvas.scaleChanged.disconnect(self.selecEscala)
        self.llista = None
        self.selec = True

    def selecEscala(self, escala):
        if self.selec:
            return
        # print ("initial scale: %s" % escala)

        nuevaEscala = min(
            self.llista, key=lambda x: abs(x - escala)
        )
        if nuevaEscala == escala:
            return

        # print("zoom to %s" % nuevaEscala)
        self.selec = True
        self.canvas.zoomScale(nuevaEscala)
        self.selec = False


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvApp import QvApp

    with qgisapp(sysexit=False) as app:

        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        canvas = QgsMapCanvas()

        llegenda = QvLlegenda(canvas)

        # llegenda.escales.fixe()
        # llegenda.escales.fixe([500, 1000, 5000, 10000, 50000])

        path = "D:/qVista/Mapas/Publicacions/Mapa Topogràfic Municipal/Qgs/"
        llegenda.project.read(path + '00 Mapa TM - Situació rr QPKG.qgs')

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()
