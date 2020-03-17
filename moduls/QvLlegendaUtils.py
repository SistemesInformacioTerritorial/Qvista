""" Modulo QvLlegendaUtils

Contiene clases que complementan QvLlegenda

"""
from qgis.PyQt.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from qgis.PyQt.QtCore import Qt, pyqtSignal
from moduls.QvLlegenda import QvLlegenda

class QvBotoneraLlegenda(QWidget):

    clicatBoto = pyqtSignal(int)

    def __init__(self, llegenda, nom='Llegenda', vertical=True):
        super().__init__()
        self.llegenda = llegenda
        self.items = dict()
        self.botons = dict()
        self.setWindowTitle(nom)
        if vertical:
            self.setLayout(QVBoxLayout())
        else:
            self.setLayout(QHBoxLayout())
        self.funcioFiltre = None
        self.funcioBoto = None

    def afegirBoto(self, item):
        if self.llegenda.editable:
            self.llegenda.editarLlegenda(False)
        boto = QPushButton(item.nom())
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

    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvApp import QvApp
    from configuracioQvista import projecteInicial

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = QvCanvas()
        atribs = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atribs)
        leyenda.project.read(projecteInicial)

        canvas.setWindowTitle('Mapa')
        canvas.show()
        leyenda.setWindowTitle('Llegenda')
        leyenda.show()
        atribs.setWindowTitle('Taules')
