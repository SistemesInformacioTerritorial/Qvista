# -*- coding: utf-8 -*-

from qgis.gui import QgsMapCanvas

class QvEscala():
    def __init__(self, canvas, escalas=None):
        self.canvas = canvas
        if escalas is None:
            self.escalas = [500, 1000, 2500, 5000, 10000,
                            25000, 50000, 100000, 250000, 500000]
        else:
            self.escalas = escalas
        self.selec = False
        self.canvas.scaleChanged.connect(self.selecEscala)  

    def selecEscala(self, escala):
        if self.selec:
            return
        # print ("initial scale: %s" % escala)
        
        nuevaEscala = min(
            self.escalas, key=lambda x:abs(x - escala)
        )
        if nuevaEscala == escala:
            return
        
        self.selec = True
        # print("zoom to %s" % nuevaEscala)
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

        escala = QvEscala(canvas)

        # llegenda.project.read('projectes/Illes.qgs')
        llegenda.project.read('../Dades/Projectes/BCN11.qgs')

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()

