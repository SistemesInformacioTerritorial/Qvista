from qgis.PyQt.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLabel, QFrame, QScrollArea
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsVectorLayer

import os

class QvCarregadorGPKG(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent,Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self._layoutGran = QVBoxLayout()
        lblExplicacio=QLabel('Trieu quines capes voleu carregar sobre el mapa')
        self._layoutGran.addWidget(lblExplicacio)
        fr=QFrame()
        sc=QScrollArea()
        sc.setWidget(fr)
        sc.setWidgetResizable(True)
        fr.setFrameShape(QFrame.Box)
        fr.setStyleSheet('background: white')
        self._layout = QVBoxLayout()
        fr.setLayout(self._layout)
        self._layoutGran.addWidget(sc)
        bAcceptar = QPushButton('Acceptar')
        bAcceptar.clicked.connect(self.accept)
        bCancelar = QPushButton('Cancelar')
        bCancelar.clicked.connect(self.reject)
        layBotons = QHBoxLayout()
        layBotons.addStretch()
        layBotons.addWidget(bAcceptar)
        layBotons.addWidget(bCancelar)
        self._layoutGran.addLayout(layBotons)
        self.setLayout(self._layoutGran)
        self.setWindowTitle('Tria de les subcapes a carregar')
    def setCapes(self,capes):
        self._combos=[QCheckBox(x) for x in capes]
        for x in self._combos:
            self._layout.addWidget(x)
    def exec_(self):
        if super().exec_() == QDialog.Accepted:
            return [x.text() for x in filter(lambda x: x.isChecked(),self._combos)]
        else:
            return []
    @classmethod
    def triaCapes(cls,nfile, parent=None):
        layer = QgsVectorLayer(nfile, os.path.basename(nfile), "ogr")
        subLayers = [x.split('!!::!!')[1] for x in layer.dataProvider().subLayers()]
        dial=cls(parent)
        dial.setCapes(subLayers)
        return dial.exec_()
