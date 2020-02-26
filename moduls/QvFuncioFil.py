from PyQt5.QtCore import QThread

class QvFuncioFil(QThread):
    '''Classe per executar una funció (sense paràmetres) en un fil. Si volem passar-hi paràmetres, haurem de fer una nova funció sense paràmetres que ho gestioni
Per fer-la servir només cal fer una cosa així:
def funcio_molt_costosa(arg1,arg2):
    ...
ff = QvFuncioFil(lambda: funcio_molt_costosa(a1,a2))
ff.start()

El codi serà executat en un fil a part, permetent no bloquejar la interfície gràfica.

Per comunicar aquest codi amb altres widgets ho haurem de fer utilitzant signals i slots. Qualsevol altra cosa pot no funcionar

IMPORTANT: no cridar directament la funció run. Sempre invocar amb start
'''
    def __init__(self,f):
        super().__init__()
        self._f=f
    def __del__(self):
        self.wait()
    def run(self):
        self._f()