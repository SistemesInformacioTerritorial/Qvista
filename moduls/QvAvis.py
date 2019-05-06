from QvNews import QvNewsFinestra
from PyQt5 import QtCore, QtWidgets
import tempfile
import os
from moduls.QvConstants import QvConstants

class QvAvis(QvNewsFinestra):
    def __init__(self,parent=None):
        super().__init__(QvConstants.ARXIUAVIS,parent)
        if self.calAvis():
            self.exec_()
    def calAvis(self):
        if not os.path.isfile(QvConstants.ARXIUAVIS):
            return False
        if not os.path.isfile(QvConstants.ARXIUTMPAVIS):
            return True
        return os.path.getmtime(QvConstants.ARXIUTMPAVIS)<os.path.getmtime(QvConstants.ARXIUAVIS)
    def exec_(self):
        super().exec_()
        with open(QvConstants.ARXIUTMPAVIS,'w') as arxiu:
            #Escrivim alguna cosa. Realment no caldria que fos el temps
            import time
            arxiu.write(str(time.time()))

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    avis=QvAvis()
    #avis.show()
    sys.exit(app.exec_())