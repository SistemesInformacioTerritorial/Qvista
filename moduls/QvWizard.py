from qvistawizard import Ui_Wizard

from moduls.QvImports import *

class QvWizard(QWizard, Ui_Wizard):
    def __init__(self):
        QWizard.__init__(self)
        self.setupUi(self)



if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        wiz = QvWizard()
        wiz.show()