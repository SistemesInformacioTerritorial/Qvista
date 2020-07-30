from qgis.gui import QgsMapToolPan, QgsMapTool, QgsMapCanvas
from qgis.core import QgsProject, QgsRectangle, QgsFeatureRequest
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon
from moduls import QvFuncions
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QFileDialog
import os
import configuracioQvista


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

@QvFuncions.creaEina(titol="Selector de Parcel·les", esEinaGlobal = False, apareixDockat = True)
class SelectorParceles(QWidget):
    def __init__(self,pare):
        super().__init__(pare)
        if isinstance(pare,QgsMapCanvas):
            self.canvas = pare
        else:
            try:
                self.canvas = pare.canvas
            except:
                # Queixar-nos
                pass
        lay = QVBoxLayout(self)
        
        self.llista = QListWidget(self)
        self.llista.itemClicked.connect(self.centraItem)
        self.llista.itemDoubleClicked.connect(self.eliminaItem)
        lay.addWidget(self.llista)

        layBotons = QHBoxLayout()
        lay.addLayout(layBotons)

        bSeleccio = QPushButton()
        bConfirmar = QPushButton('Confirmar')
        bNetejar = QPushButton('Netejar')
        layBotons.addWidget(bSeleccio)
        layBotons.addStretch()
        layBotons.addWidget(bConfirmar)
        layBotons.addWidget(bNetejar)

        bSeleccio.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'apuntar.png')))

        einaSel = EinaSeleccio(self.canvas)
        bSeleccio.clicked.connect(lambda: self.canvas.setMapTool(einaSel))
        einaSel.featsSeleccionades.connect(self.seleccionaFeats)

        bConfirmar.clicked.connect(self.desar)
        bNetejar.clicked.connect(self.netejar)

        self.featsSeleccionades = []

        self.layer = QgsProject.instance().mapLayersByName(capaParceles)[0]
    def desar(self):
        nfile, _ = QFileDialog.getSaveFileName(None, "Desar fitxer de text", ".", "Arxius de text (*.txt)")
        if nfile!='':
            try:
                with open(nfile,'w') as f:
                    f.writelines([feat['REF_CDS']+'\n' for feat in self.featsSeleccionades])
            except:
                pass
                # Queixar-nos
    def netejar(self):
        self.featsSeleccionades = []
        self.layer.selectByIds([])
        self.llista.clear()
    
    def centraItem(self,item):
        feat = [feat for feat in self.featsSeleccionades if feat['REF_CDS']==item.text()][0]
        self.canvas.setExtent(feat.geometry().boundingBox())
        #self.update()
        self.canvas.zoomScale(500)

    def eliminaItem(self,item):
        self.featsSeleccionades = [feat for feat in self.featsSeleccionades if feat['REF_CDS']!=item.text()]
        self.layer.selectByIds([feat.id() for feat in self.featsSeleccionades])
        self.llista.clear()
        self.llista.addItems([feat['REF_CDS'] for feat in self.featsSeleccionades])

    def seleccionaFeats(self, feats):
        ids = [feat.id() for feat in self.featsSeleccionades]
        for x in feats:
            if x.id() in ids:
                element = [feat for feat in self.featsSeleccionades if feat.id()==x.id()][0]
                self.featsSeleccionades.remove(element)
            else:
                self.featsSeleccionades.append(x)
        self.layer.selectByIds([feat.id() for feat in self.featsSeleccionades])
        
        self.llista.clear()
        self.llista.addItems([feat['REF_CDS'] for feat in self.featsSeleccionades])