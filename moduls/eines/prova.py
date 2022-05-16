from moduls import QvFuncions
from moduls.QvImports import *

# Exemple de com es pot crear una eina a partir d'un QWidget i el generador d'eines
# Posem esEinaGlobal a False perquè no aparegui dins del qVista
# Canviant-lo a True apareixeria dins del qVista sense fer res més
@QvFuncions.creaEina(titol="Prova del generador d'entorns",esEinaGlobal=False,apareixDockat=False)
class prova(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.lay=QVBoxLayout()
        self.lay.addWidget(QLabel('Hola :D'))
        self.lay.addWidget(QPushButton('No faig res'))
        self.lay.addWidget(QLabel("Adéu :'("))
        self.setLayout(self.lay)

if __name__=='__main__':
    import sys
    with qgisapp() as app:
        wid = prova()
        wid.show()
        sys.exit(app.exec())