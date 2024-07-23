from moduls.QvVisorHTML import QvVisorHTML
from qgis.PyQt import QtWidgets
import os
import configuracioQvista
from moduls.QvMemoria import QvMemoria
from qgis.PyQt.QtWidgets import QMessageBox

class QvAvis(QvVisorHTML):
    '''Crea un diàleg d'avisos i, si n'hi ha algun de nou, el mostra
    '''
    def __init__(self, errors, parent: QtWidgets.QWidget=None):
        super().__init__(configuracioQvista.arxiuAvis, 'Atenció',parent)
        self.errors = errors
        for capa in self.errors.values():
            for error_type, error_message in capa.items():
                self.afegirError(error_type, error_message)
        if self.calAvis():
            self.exec_()

    def calAvis(self):
        if not os.path.isfile(configuracioQvista.arxiuAvis):
            return False
        
        return QvMemoria().getUltimAvis()<os.path.getmtime(configuracioQvista.arxiuAvis)

    def exec_(self):
        super().exec_()
        QvMemoria().setUltimAvis()

    def afegirError(self, error_type, error_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Atenció")
        msg.setText(f"{error_type}: {error_message}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__=='__main__':
    import sys
    app=QtWidgets.QApplication(sys.argv)
    avis=QvAvis()
    avis.show()
    sys.exit(app.exec_())