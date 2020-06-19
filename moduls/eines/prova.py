from moduls import QvFuncions
from moduls.QvImports import *

class ElMeuWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.lay=QVBoxLayout()
        self.lay.addWidget(QLabel('Hola :D'))
        self.lay.addWidget(QPushButton('No faig res'))
        self.lay.addWidget(QLabel("Adéu :'("))
        self.setLayout(self.lay)

prova = QvFuncions.creaEntorn(ElMeuWidget(),titol="Prova del generador d'entorns",
                              esEinaGlobal=True,apareixDockat=False)