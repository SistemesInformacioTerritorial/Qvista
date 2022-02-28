# -*- coding: utf-8 -*-

from qgis.PyQt import QtWidgets

class QvFormMapesGPKG(QtWidgets.QDialog):
    def __init__(self, mapes):
        super(QvFormMapesGPKG, self).__init__()
        self.setWindowTitle("Obrir mapa d'arxiu geopackage")
        self.setMinimumSize(400, 100)
        self.layout = QtWidgets.QFormLayout()
        self.layout.setVerticalSpacing(20)
        self.setLayout(self.layout)

        self.mapa = None
        self.mapes = QtWidgets.QComboBox()
        self.mapes.setEditable(False)
        self.mapes.addItems(mapes)

        self.buttons = QtWidgets.QDialogButtonBox(self)
        self.buttons.addButton(QtWidgets.QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.addButton(QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.layout.addRow("Selecciona mapa:", self.mapes)
        self.layout.addRow(self.buttons)

    def accept(self):
        self.mapa = self.mapes.currentText()
        self.hide()

    def cancel(self):
        self.mapa = None
        self.hide()

    @classmethod
    def executa(cls, mapes):
        fMap = cls(mapes)
        fMap.exec()
        return fMap.mapa

