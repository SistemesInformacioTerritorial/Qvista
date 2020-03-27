# -*- coding: utf-8 -*-

import qgis.PyQt.QtWidgets as qgWdg
import qgis.PyQt.QtCore as qgCor


class QvLlegendaBotonera(qgWdg.QWidget):

    clicatBoto = qgCor.pyqtSignal(int)

    def __init__(self, llegenda, nom='Llegenda', vertical=True):
        super().__init__()
        self.llegenda = llegenda
        self.items = dict()
        self.botons = dict()
        self.setWindowTitle(nom)
        if vertical:
            self.setLayout(qgWdg.QVBoxLayout())
        else:
            self.setLayout(qgWdg.QHBoxLayout())
        self.funcioFiltre = None
        self.funcioBoto = None

    def afegirBoto(self, item):
        boto = qgWdg.QPushButton(item.nom())
        boto.setCheckable(True)
        boto.setChecked(item.esVisible())
        self.layout().addWidget(boto)
        i = self.layout().indexOf(boto)
        self.items[i] = item
        self.botons[i] = boto
        boto.clicked.connect(self.clickBoto)
        return boto

    def esborrarBotonera(self):
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeItem(layout.itemAt(i))
        self.repaint()
        self.items = dict()
        self.botons = dict()

    def afegirBotonera(self, funcioFiltre=None, funcioBoto=None):
        # Filtro de usuario del itema a añadir a botonera
        if funcioFiltre is not None:
            self.funcioFiltre = funcioFiltre
        # Modificación de usuario del boton generado
        if funcioBoto is not None:
            self.funcioBoto = funcioBoto
        self.esborrarBotonera()
        for item in self.llegenda.items():
            if self.funcioFiltre is None or self.funcioFiltre(item):
                boto = self.afegirBoto(item)
                if self.funcioBoto is not None:
                    self.funcioBoto(boto)

    def actBotons(self):
        for i in range(len(self.botons)):
            self.botons[i].setChecked(self.items[i].esVisible())

    def clickBoto(self):
        boto = self.sender()
        i = self.layout().indexOf(boto)
        item = self.items[i]
        item.veure(not item.esVisible())
        self.actBotons()
        self.clicatBoto.emit(i)


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    import qgis.gui as qgGui

    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvAtributs import QvAtributs
    from moduls.QvApp import QvApp
    # from configuracioQvista import projecteInicial

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = qgGui.QgsMapCanvas()
        canvas.setWindowTitle('Mapa')

        atribs = QvAtributs(canvas)
        atribs.setWindowTitle('Taules')

        leyenda = QvLlegenda(canvas, atribs, editable=False)
        leyenda.project.read('D:/qVista/EjemploMapTestMask.qgs')
        leyenda.setWindowTitle('Llegenda')
        leyenda.move(0, 0)
        leyenda.show()

        canvas.move(leyenda.width(), 0)
        canvas.show()

        # Generación de botoneras de leyenda
        botonera = None
        clases = None

        def modifBoton(boton):
            boton.setFlat(True)

        def filtroBotonera(item):
            if item.tipus == 'layer':
                return item.nom() != "Màscara"
            elif item.tipus == 'group':
                return True
            else:
                return False

        def filtroClases(item):
            return item.tipus == 'symb'

        def verClases(i):
            boto = botonera.botons[i]
            if boto.text() == "Cadires Terrasses":
                botoneraClases.setVisible(boto.isChecked())

        botonera = QvLlegendaBotonera(leyenda, 'Botonera')
        botonera.afegirBotonera(filtroBotonera, modifBoton)
        botonera.clicatBoto.connect(verClases)
        botonera.setMinimumSize(200, 100)
        botonera.move(0, canvas.height() + 20)
        botonera.show()

        botoneraClases = QvLlegendaBotonera(leyenda, 'Clases', False)
        botoneraClases.afegirBotonera(filtroClases, modifBoton)
        botoneraClases.move(botonera.width(), canvas.height() + 20)
        botoneraClases.show()
