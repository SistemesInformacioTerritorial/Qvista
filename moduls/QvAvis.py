from moduls.QvVisorHTML import QvVisorHTML
from PyQt5 import QtCore, QtWidgets
import tempfile
import os
from moduls.QvConstants import QvConstants
from configuracioQvista import *

class QvAvis(QvVisorHTML):
    '''Crea un diàleg d'avisos i, si n'hi ha algun de nou, el mostra
    '''
    def __init__(self,parent=None):
        super().__init__(arxiuAvis, 'Avisos qVista',parent)
        if self.calAvis():
            self.exec_()
    def calAvis(self):
        if not os.path.isfile(arxiuAvis):
            return False
        if not os.path.isfile(arxiuTmpAvis):
            return True
        return os.path.getmtime(arxiuTmpAvis)<os.path.getmtime(arxiuAvis)
    def exec_(self):
        super().exec_()
        with open(arxiuTmpAvis,'w') as arxiu:
            #Escrivim alguna cosa. Realment no caldria que fos el temps
            import time
            arxiu.write(str(time.time()))

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    avis=QvAvis()
    avis.show()
    sys.exit(app.exec_())