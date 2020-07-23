from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge, QgsMapToolPan, QgsMapTool
from qgis.core import QgsProject, QgsRectangle, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QMainWindow, QTextEdit, QDialog, QVBoxLayout, QFileDialog, QComboBox
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import Qt
import configuracioQvista
from moduls.QvImports  import *
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
        self.canvas = QgsMapCanvas(self)
        self.config = {"campReferencia": "REF_CDS", "colHex": "#FF6215"}
        projecte = QgsProject.instance()
        projecte.read('MapesOffline/parcel·lari simple gpkg.qgs') # el correcte és l'anterior, però sense POVI millor aquest
        root = projecte.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, self.canvas)
        # projecte.read('MapesOffline/parcel·lari simple.qgs')

        self.layer = QgsProject.instance().mapLayersByName(capaParceles)[0]
        self.layCanvas.addWidget(self.canvas)
        self.listSel = QListWidget()
        self.llista_catastral = [] #contingut llista catastral
        self.llista_ids = []

        self.bPanning.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'pan_tool_black_24x24.png')))
        self.bSeleccio.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'apuntar.png')))
        
        self.bPanning.clicked.connect(self.mouCanvas)
        self.bSeleccio.clicked.connect(self.selecciona)

        self.actionNova_sel_lecci.triggered.connect(self.novaConfig)
        self.actionObrir_sel_lecci.triggered.connect(self.obrirConfig)
        self.actionDesar.triggered.connect(self.desarConfig)

        self.bCancelar.clicked.connect(self.close)
        # self.bAcceptar.clicked.connect(self.desarResultat) # No implementada

        self.habilitaBotons()
    
    def mouCanvas(self):
        self.tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.tool)
    
    def selecciona(self):
        self.tool = EinaSeleccio(self.canvas)
        self.canvas.setMapTool(self.tool)
        self.tool.featsSeleccionades.connect(self.seleccionaFeats)

    def seleccionaFeats(self,feats):
        ids=[x.id() for x in feats]
        ref_catastre = [x[self.config['campReferencia']] for x in feats]
        
        for idx in ids:
            if idx in self.llista_ids:
                self.llista_ids.remove(idx)
            else:
                self.llista_ids.append(idx)
        self.layer.selectByIds(self.llista_ids)
        #print(self.layer.selectedFeatureIds())

        for ref in ref_catastre:
            if str(ref) in self.llista_catastral:
                self.llista_catastral.remove(ref)
                self.listSel.clear()
                for i in self.llista_catastral:
                    self.listSel.addItem(str(i))
            else:
                self.llista_catastral.append(ref)
                self.listSel.addItem(str(ref))
    
    def novaConfig(self):
        dial = QDialog(self,Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        dial.setWindowTitle('Nova configuració')
        lay = QVBoxLayout(dial)

        layCol = QHBoxLayout()
        layCol.addWidget(QLabel('Color de la selecció:'))
        layCol.addStretch()
        lay.addLayout(layCol)
        color = self.config['colHex']
        STYLESHEET = 'background-color: %s'
        def obrirDialegColor():
            nonlocal color
            c = QColorDialog.getColor(QColor(color),dial,'Tria del color')
            color = c.name()
            bColor.setStyleSheet(STYLESHEET%color)
        bColor = QPushButton()
        bColor.setStyleSheet(STYLESHEET%color)
        bColor.clicked.connect(obrirDialegColor)
        layCol.addWidget(bColor)

        layCamp = QHBoxLayout()
        layCamp.addWidget(QLabel('Camp de les referències cadastrals:'))
        layCamp.addStretch()
        lay.addLayout(layCamp)

        cbCamps = QComboBox()
        camps = [x.name() for x in self.layer.fields()]
        cbCamps.addItems(camps)
        layCamp.addWidget(cbCamps)
        if self.config['campReferencia'] in camps:
            cbCamps.setCurrentIndex(camps.index(self.config['campReferencia']))

        lay.addStretch()
        bAcceptar = QPushButton('Acceptar')
        bAcceptar.clicked.connect(dial.close)
        lay.addWidget(bAcceptar, alignment=Qt.AlignRight)

        dial.exec_()

        self.config = {'campReferencia':cbCamps.currentText(), 'colHex': color}

        self.habilitaBotons()
    
    def obrirConfig(self):
        nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer JSON", ".", "JSON (*.json)")
        try:
            with open(nfile) as f:
                self.config = json.loads(f.read())
            self.config["campReferencia"]
            self.config["colHex"]
        except:
            # Queixar-nos
            pass
        self.habilitaBotons()
    
    def desarConfig(self):
        nfile, _ = QFileDialog.getSaveFileName(None, "Desar fitxer JSON", ".", "JSON (*.json)")
        try:
            with open(nfile,'w') as f:
                f.write(json.dumps(self.config))
        except:
            pass
            # Queixar-nos
    def habilitaBotons(self):
        habilitats = self.config is not None
        self.bPanning.setEnabled(habilitats)
        self.bSeleccio.setEnabled(habilitats)

        self.canvas.setSelectionColor(QColor(self.config['colHex']))

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
        layV.addWidget(sel.listSel)
        widgetSel.setLayout(layV)
        dwLlista = QDockWidget("Dockable")
        dwLlista.setWindowTitle("Selecció")
        sel.addDockWidget(Qt.RightDockWidgetArea, dwLlista)
        dwLlista.setWidget(widgetSel)

        sel.showMaximized()