import time

from qgis.core import (QgsFeature, QgsField, QgsGeometry, QgsProject,
                       QgsVectorLayer)
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsMapTool
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import (QComboBox, QHBoxLayout, QLineEdit,
                                 QPushButton, QSizePolicy, QTableWidget,
                                 QTableWidgetItem, QVBoxLayout, QWidget)

from moduls import QvFuncions


@QvFuncions.creaEina(titol="Creador de capes puntuals", esEinaGlobal = False, apareixDockat = False)
class CreadorCapesPuntuals(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.pare = parent
        if isinstance(parent,QgsMapCanvas):
            self.canvas = parent
        else:
            possiblesCanvas = parent.findChildren(QgsMapCanvas)
            if len(possiblesCanvas)==1:
                self.canvas = possiblesCanvas[0]
            else:
                # Això s'ha de canviar per detectar quin és el canvas principal
                self.canvas = possiblesCanvas[0]
        
        lay = QVBoxLayout()
        self.setLayout(lay)

        self.leNomCapa = QLineEdit()
        self.leNomCapa.textChanged.connect(self.canviaNomCapa)
        lay.addWidget(self.leNomCapa)

        self.taula = QTableWidget(2,0)
        self.taula.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum)
        lay.addWidget(self.taula)

        layH = QHBoxLayout()
        lay.addLayout(layH)

        self.leNomCamp = QLineEdit()
        self.leNomCamp.setEnabled(False)
        self.cbTipus = QComboBox()
        layH.addWidget(self.leNomCamp)
        layH.addWidget(self.cbTipus)

        self.cbTipus.addItems(['Int','String'])

        self.leNomCamp.returnPressed.connect(self.afegirCamp)

        layB = QHBoxLayout()
        lay.addLayout(layB)
        self.bCrearCapa = QPushButton('Afegir elements')
        self.bCrearCapa.clicked.connect(self.switchBoto)
        self.bCrearCapa.setCheckable(True)
        layB.addWidget(self.bCrearCapa)

        self.bDesar = QPushButton('Desar capa')
        self.bDesar.clicked.connect(self.desar)
        self.bDesar.setEnabled(False)
        layB.addWidget(self.bDesar)

        self.capa = self.novaCapa()
    
    def switchBoto(self):
        if self.bCrearCapa.isChecked():
            # Crear maptool
            class EinaCrearCapa(QgsMapTool):
                def __init__(self, parent):
                    super().__init__(parent.canvas)
                    self.pare = parent
                    self.canvas = parent.canvas
                    pass
                def canvasPressEvent(self,e):
                    super().canvasPressEvent(e)
                    feat = QgsFeature(self.pare.capa.fields())
                    feat.setGeometry(QgsGeometry.fromPointXY(self.canvas.getCoordinateTransform().toMapCoordinates(e.pos())))
                    # Faltaria fer el diàleg per afegir la informació
                    
                    self.pare.afegirFeature(feat)
            self.eina = EinaCrearCapa(self)
            self.canvas.setMapTool(self.eina)
        else:
            self.canvas.refresh()
            self.canvas.unsetMapTool(self.eina)
    def desar(self):
        self.taula.clear()
        self.taula.setColumnCount(0)
        self.capa = self.novaCapa()
        self.leNomCapa.clear()
        self.bDesar.setEnabled(False)
        self.leNomCamp.setEnabled(True)
    def afegirCamp(self):
        dictTipus = {'Int':QVariant.Int, 'String':QVariant.String}
        pr = self.capa.dataProvider()
        pr.addAttributes([QgsField(self.leNomCamp.text(),dictTipus[self.cbTipus.currentText()])])
        self.capa.updateFields()

        self.taula.setColumnCount(self.taula.columnCount()+1)
        self.taula.setItem(0,self.taula.columnCount()-1,QTableWidgetItem(self.leNomCamp.text()))
        self.taula.setItem(1,self.taula.columnCount()-1,QTableWidgetItem(self.cbTipus.currentText()))

        self.leNomCamp.clear()
    def novaCapa(self):
        self.afegida = False
        capa = QgsVectorLayer('Point?crs=EPSG:25831','','memory')
        return capa
    def afegirFeature(self,feat):
        if not self.afegida:
            QgsProject.instance().addMapLayer(self.capa)
            self.afegida = True
            self.canvas.refresh()
            self.bDesar.setEnabled(True)
            self.leNomCamp.setEnabled(False)
        self.capa.dataProvider().addFeature(feat)
        self.capa.triggerRepaint()
    def canviaNomCapa(self):
        self.capa.setName(self.leNomCapa.text())
        self.leNomCamp.setEnabled(self.leNomCapa.text()!='')


if __name__ == "__main__":
       
    with qgisapp() as app:
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas

        from moduls.QvLlegenda import QvLlegenda

        # Canvas, projecte i bridge
        start1 = time.time()
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

            eina = CreadorCapesPuntuals(canvas)

            eina.show()