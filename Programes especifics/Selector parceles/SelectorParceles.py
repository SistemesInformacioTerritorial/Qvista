from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QMainWindow, QTextEdit, QDialog, QVBoxLayout
from moduls.QvImports  import *
import os
import json
import SelectorParcelesUi

class SelectorParceles(QMainWindow,SelectorParcelesUi.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.config = None
        print(os.getcwd())
        projecte = QgsProject.instance()
        # projecte.read('MapesOffline/parcel·lari simple.qgs')
        projecte.read('MapesOffline/parcel·lari simple gpkg.qgs') # el correcte és l'anterior, però sense POVI millor aquest
        canvas = QgsMapCanvas(self)
        bridge = QgsLayerTreeMapCanvasBridge(projecte.layerTreeRoot(), canvas)
        self.layCanvas.addWidget(canvas)

        self.actionNova_sel_lecci.triggered.connect(self.novaSeleccio)
    
    def novaSeleccio(self):
        dial = QDialog(self)
        lay = QVBoxLayout(dial)
        tedit = QTextEdit()
        tedit.setPlainText('{\n'
            '    "campReferencia":"REF_CDS",\n'
            '    "colHex":"#FF6215"\n'
            '}')
        lay.addWidget(tedit)
        dial.exec()
        try:
            self.config = json.loads(tedit.toPlainText())
        except:
            # Queixar-nos de que la configuració no està ben escrita
            pass
        self.habilitaBotons()

    def habilitaBotons(self):
        habilitats = self.config is not None
        self.bPanning.setEnabled(habilitats)
        self.bSeleccio.setEnabled(habilitats)


if __name__=='__main__':
    from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        sel = SelectorParceles()

        llegenda = QvLlegenda()
        dwLlegenda = QDockWidget("Dockable")
        dwLlegenda.setWindowTitle("Llegenda")
        sel.addDockWidget(Qt.LeftDockWidgetArea, dwLlegenda)
        dwLlegenda.setWidget(llegenda)

        widgetSel = QWidget()
        layV = QVBoxLayout()
        listSel = QListWidget()
        layV.addWidget(listSel)
        widgetSel.setLayout(layV)
        dwLlista = QDockWidget("Dockable")
        dwLlista.setWindowTitle("Selecció")
        sel.addDockWidget(Qt.RightDockWidgetArea, dwLlista)
        dwLlista.setWidget(widgetSel)

        sel.showMaximized()