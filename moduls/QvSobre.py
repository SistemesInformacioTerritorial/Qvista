from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QSizePolicy
from qgis.PyQt.QtGui import QFont, QIcon
from qgis.PyQt.QtCore import Qt
import os
from moduls.QvApp import QvApp
from moduls.QvConstants import QvConstants
from moduls.QvReports import QvReports
import configuracioQvista

class QvSobre(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent,Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        # self.setMinimumWidth(600)
        self.setWindowTitle('Sobre qVista')
        self.setWindowIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'QVistaLogo_256.png')))

        self._lay=QGridLayout()
        self._i=0

        # lay.setSpacing(0)
        self.setLayout(self._lay)

        self._creaFila('Versió de qVista:',configuracioQvista.versio)

        self._creaFila('Versió de QGIS:',QvApp().versioQgis())

        if QvReports.DataPlotlyVersion is not None:
            self._creaFila('Versió de DataPlotly:', QvReports.DataPlotlyVersion)

        self._creaFila('Desenvolupat per:',"Sistemes d'Informació Territorial\n Institut Municipal d'Informàtica\n Ajuntament de Barcelona")

        # self._creaFila('Llicència:','<a href="https://www.gnu.org/licenses/gpl-3.0.ca.html">GNU GPLv3</a>')

    def _creaFila(self, text1, text2):
        lbl1=QLabel(text1)
        lbl2=QLabel(text2)

        # Per si hi ha algun enllaç
        lbl1.setOpenExternalLinks(True)
        lbl2.setOpenExternalLinks(True)

        # SizePolicy
        lbl1.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        lbl2.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)

        # Fonts
        # Fem una còpia de la font dels textos per posar-la en negreta
        fontNoms = QFont(QvConstants.FONTTEXT)
        fontNoms.setBold(True)
        lbl1.setFont(fontNoms)
        lbl2.setFont(QvConstants.FONTTEXT)

        self._lay.addWidget(lbl1,self._i,0,Qt.AlignTop|Qt.AlignRight)
        self._lay.addWidget(lbl2,self._i,1,Qt.AlignTop)
        
        self._i+=1

if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp
    with qgisapp(guienabled=True):
        about = QvSobre()
        about.exec_()