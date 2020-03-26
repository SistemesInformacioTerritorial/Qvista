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
        if self.llegenda.editable:
            self.llegenda.editarLlegenda(False)
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
    from configuracioQvista import projecteInicial

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = qgGui.QgsMapCanvas()
        atribs = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atribs)
        leyenda.project.read(projecteInicial)

        canvas.setWindowTitle('Mapa')
        leyenda.setWindowTitle('Llegenda')
        atribs.setWindowTitle('Taules')

        canvas.show()
        leyenda.show()

        # Generación de botoneras de leyenda
        botonera = None
        rangos = None

        def filtroBotonera(item):
            return item.tipus in ('layer', 'group')

        def filtroRangos(item):
            return item.tipus == 'symb'

        def modifBoton(boton):
            boton.setFlat(True)

        botonera = QvLlegendaBotonera(leyenda, 'Botonera')
        botonera.afegirBotonera(filtroBotonera, modifBoton)
        botonera.show()

        # Falta comprobar checks
        botoneraRangos = QvLlegendaBotonera(leyenda, 'Rangos', False)
        botoneraRangos.afegirBotonera(filtroRangos, modifBoton)
        botoneraRangos.show()

