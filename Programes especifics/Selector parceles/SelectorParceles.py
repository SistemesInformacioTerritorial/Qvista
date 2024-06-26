from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge, QgsMapToolPan, QgsMapTool
from qgis.core import QgsProject, QgsRectangle, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QMainWindow, QTextEdit, QDialog, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QMessageBox,  QListWidget, QWidget, QDockWidget, QLabel
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import Qt
import os
from os import path
import json
import SelectorParcelesUi

capaParceles = 'PARCELARI_SIMPLE POLIGONS_PARCELA'

#Aquesta variable conté el path on es guardarà la llista (.txt) de les parcel·les seleccionades
pathGuardarSeleccio = "\\Programes especifics\\Selector parceles\\seleccio_parceles.txt"

pathImatges = "\\Programes especifics\\Selector parceles\\Imatges"

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
        self.listSel.itemDoubleClicked.connect(self.clickLlista)
        self.llista_catastral = [] #contingut llista catastral
        self.llista_ids = [] #per pintar les parcel·les

        if path.exists(os.path.abspath(os.getcwd()) + pathGuardarSeleccio):
            with open(os.path.abspath(os.getcwd()) + pathGuardarSeleccio) as f:
                self.llista_catastral = [x.replace('\n','') for x in f.readlines()]
            self.llista_ids=[x.id() for x in self.layer.getFeatures() if x.attribute(self.config['campReferencia']) in self.llista_catastral]
            self.layer.selectByIds(self.llista_ids)
            for i in self.llista_catastral:
                self.listSel.addItem(str(i))

        pa = os.path.join(os.path.abspath(os.getcwd()) + pathImatges)
        print(pa)
        self.bPanning.setIcon(QIcon(pa,'pan_tool_black_24x24.png'))
        self.bSeleccio.setIcon(QIcon(pa,'apuntar.png'))
        
        self.bPanning.clicked.connect(self.mouCanvas)
        self.bSeleccio.clicked.connect(self.selecciona)

        self.actionNova_seleccio.triggered.connect(self.novaSeleccio)
        self.actionNova_configuracio.triggered.connect(self.novaConfig)
        self.actionObrir_configuracio.triggered.connect(self.obrirConfig)
        self.actionDesar_configuracio.triggered.connect(self.desarConfig)
        self.actionObrir_seleccio.triggered.connect(self.obrirSeleccio)
        self.actionDesar_seleccio.triggered.connect(self.desarResultat)

        self.bCancelar.clicked.connect(self.close)
        self.bConfirmar.clicked.connect(self.desarResultat)

        self.carregaConfig()

    def clickLlista(self,item):
        ref_catastral = item.text()
        index = self.llista_catastral.index(str(ref_catastral))
        idx = self.llista_ids[index]
        feature = self.layer.getFeature(idx)
        rect = feature.geometry().boundingBox()
        self.canvas.setExtent(rect)
        self.canvas.zoomScale(500)
    
    def mouCanvas(self):
        self.tool = QgsMapToolPan(self.canvas)
        self.canvas.setMapTool(self.tool)
    
    def selecciona(self):
        self.tool = EinaSeleccio(self.canvas)
        self.canvas.setMapTool(self.tool)
        self.tool.featsSeleccionades.connect(self.seleccionaFeats)

    def seleccionaFeats(self,feats):
        ids=[x.id() for x in feats]
        refs_catastre = [x[self.config['campReferencia']] for x in feats]
        
        for idx in ids:
            if idx in self.llista_ids:
                self.llista_ids.remove(idx)
            else:
                self.llista_ids.append(idx)
        self.layer.selectByIds(self.llista_ids)
        #print(self.layer.selectedFeatureIds())

        for ref in refs_catastre:
            if str(ref) in self.llista_catastral:
                self.llista_catastral.remove(ref)
                self.listSel.clear()
                for i in self.llista_catastral:
                    self.listSel.addItem(str(i))
            else:
                self.llista_catastral.append(ref)
                self.listSel.addItem(str(ref))

    def novaSeleccio(self):
        #self.novaConfig()
        self.llista_catastral = []
        self.llista_ids = []
        self.listSel.clear()
        self.layer.selectByIds([])

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

        self.carregaConfig()
    
    def obrirConfig(self):
        nfile,_ = QFileDialog.getOpenFileName(None, "Obrir fitxer JSON", ".", "JSON (*.json)")
        if nfile=='': return
        try:
            with open(nfile) as f:
                self.config = json.loads(f.read())
            self.config["campReferencia"]
            self.config["colHex"]
        except:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Error)
            msgBox.setText("No s ha pogut obrir correctament la configuracio.")
            msgBox.exec()
            pass
        self.carregaConfig()
    
    def desarConfig(self):
        nfile, _ = QFileDialog.getSaveFileName(None, "Desar fitxer JSON", ".", "JSON (*.json)")
        if nfile=='': return
        try:
            with open(nfile,'w') as f:
                f.write(json.dumps(self.config))
        except:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Error)
            msgBox.setText("No s ha pogut desar correctament la configuracio.")
            msgBox.exec()
            pass

    def obrirSeleccio(self):
        nfile, _ = QFileDialog.getOpenFileName(None, "Obrir fitxer de text", ".", "Arxiu de text (*.txt)")
        if nfile=='': return
        try:
            with open(nfile) as f:
                self.llista_catastral = [x.replace('\n','') for x in f.readlines()]
        except:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Error)
            msgBox.setText("No s ha pogut obrir correctament la seleccio.")
            msgBox.exec()
            pass

        self.novaConfig()
        self.listSel.clear()
        self.listSel.addItems(self.llista_catastral)
        self.llista_ids=[x.id() for x in self.layer.getFeatures() if x.attribute(self.config['campReferencia']) in self.llista_catastral]
        self.layer.selectByIds(self.llista_ids)

    def carregaConfig(self):
        self.canvas.setSelectionColor(QColor(self.config['colHex']))

    def desarResultat(self):
        #nfile, _ = QFileDialog.getSaveFileName(None, "Desar fitxer de text", ".", "Arxiu de text (*.txt)")
        nfile = os.path.abspath(os.getcwd()) + pathGuardarSeleccio
        if nfile=='': return
        try:
            with open(nfile,'w') as f:
                f.writelines([x+'\n' for x in self.llista_catastral])
            # msgBox = QMessageBox()
            # msgBox.setIcon(QMessageBox.Information)
            # msgBox.setText("La selecció s'ha guardat correctament.")
            # msgBox.exec()
        except:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Error)
            msgBox.setText("La selecció no s'ha pogut guardat correctament.")
            msgBox.exec()
            pass

        self.close()


if __name__=='__main__':
    #from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        sel = SelectorParceles()

        widgetSel = QWidget()
        layV = QVBoxLayout() 
        layV.addWidget(sel.listSel)
        widgetSel.setLayout(layV)
        dwLlista = QDockWidget()
        dwLlista.setWindowTitle("Parcel·les seleccionades")
        sel.addDockWidget(Qt.RightDockWidgetArea, dwLlista)
        dwLlista.setWidget(widgetSel)

        sel.showMaximized()