from moduls.QvVisorHTML import QvVisorHTML
from qgis.PyQt import QtWidgets
import os
from configuracioQvista import *
from moduls.QvMemoria import QvMemoria

class QvAvis(QvVisorHTML):
    '''Crea un diàleg d'avisos i, si n'hi ha algun de nou, el mostra
    '''
    def __init__(self,parent: QtWidgets.QWidget=None):
        super().__init__(arxiuAvis, 'Atenció',parent)
        if self.calAvis():
            self.exec_()
    def calAvis(self):
        if not os.path.isfile(arxiuAvis):
            return False
        
        return QvMemoria().getUltimAvis()<os.path.getmtime(arxiuAvis)
    def exec_(self):
        super().exec_()
        QvMemoria().setUltimAvis()

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    avis=QvAvis()
    avis.show()
    sys.exit(app.exec_())