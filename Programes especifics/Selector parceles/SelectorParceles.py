from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge, QgsMapToolPan, QgsMapTool
from qgis.core import QgsProject, QgsRectangle, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QMainWindow, QTextEdit, QDialog, QVBoxLayout
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import pyqtSignal
import configuracioQvista
import os
import json
import SelectorParcelesUi

capaParceles = 'PARCELARI_SIMPLE POLIGONS_PARCELA'

class EinaSeleccio(QgsMapTool):
    featsSeleccionades = pyqtSignal(list)
    def __init__(self, canvas, radi=1):
        super().__init__(canvas)
        self.canvas = canvas
        self.radi = radi
    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        layer = QgsProject.instance().mapLayersByName(capaParceles)[0]
        esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x - self.radi, y-self.radi)
        dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x + self.radi, y+self.radi)
        rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())

        it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))

        features = []
        for feature in it:
            # ids.append(feature.id())
            features.append(feature)
        
        self.featsSeleccionades.emit(features)

class SelectorParceles(QMainWindow,SelectorParcelesUi.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.config = None
        projecte = QgsProject.instance()
        # projecte.read('MapesOffline/parcel·lari simple.qgs')
        projecte.read('MapesOffline/parcel·lari simple gpkg.qgs') # el correcte és l'anterior, però sense POVI millor aquest
        self.canvas = QgsMapCanvas(self)
        bridge = QgsLayerTreeMapCanvasBridge(projecte.layerTreeRoot(), self.canvas)
        self.layer = QgsProject.instance().mapLayersByName(capaParceles)[0]
        self.layCanvas.addWidget(self.canvas)

        self.bPanning.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'pan_tool_black_24x24.png')))
        self.bSeleccio.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'apuntar.png')))
        
        self.bPanning.clicked.connect(self.mouCanvas)
        self.bSeleccio.clicked.connect(self.selecciona)

        self.actionNova_sel_lecci.triggered.connect(self.novaSeleccio)
    
    def mouCanvas(self):
        self.tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.tool)
    def selecciona(self):
        self.tool = EinaSeleccio(self.canvas)
        self.canvas.setMapTool(self.tool)

        
        self.tool.featsSeleccionades.connect(self.seleccionaFeats)
    def seleccionaFeats(self,feats):
        ids=[x.id() for x in feats]
        self.layer.selectByIds(ids)
        print(self.layer.selectedFeatureIds())
    
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

        self.canvas.setSelectionColor(QColor(self.config['colHex']))

if __name__=='__main__':
    with qgisapp() as app:
        sel = SelectorParceles()
        sel.show()