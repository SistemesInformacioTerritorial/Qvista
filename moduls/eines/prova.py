from moduls import QvFuncions
from moduls.QvImports import *

@QvFuncions.creaEina(titol="Prova del generador d'entorns",esEinaGlobal=True,apareixDockat=False)
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