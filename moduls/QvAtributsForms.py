# -*- coding: utf-8 -*-

from qgis.gui import QgsAttributeForm, QgsAttributeDialog, QgsActionMenu, QgsAttributeEditorContext
from qgis.PyQt.QtWidgets import QDialog, QMenuBar

from moduls.Ui_AtributsForm import Ui_AtributsForm

class QvFormAtributs:
    @staticmethod
    def create(layer, features, parent=None, digitize=None, new=False):
        """Crea un formulario para dar de alta, modificar o consultar datos alfanuméricos de un elemento.
           Cuando se trata de una consulta, puede tratarse de una lista de elementos.

        Args:
            layer (QgsVectorLayer): Capa
            features (QgsFeature o [QgsFeature]): Elemento o lista de elementos
            parent (QWidget, optional): Widget padre del formulario creado. Defaults to None.
            digitize (QvDigitize, optional): Información del estado de digitalización de la capa.
                                             Necesario si no se trata de un alta. Defaults to None.
            new (bool, optional): Si es True se trata de un alta. Defaults to False.

        Returns:
            QgsAttributeDialog o QDialog: Formulario de alta / edición o formulario de consulta de elemento(s)
        """
        # Alta de elemento
        if new:
            if features is not None and isinstance(features, list): features = features[0]
            return QvFitxaAtributs(layer, features, parent, QgsAttributeEditorContext.AddFeatureMode)
        # Modificación de elemento
        if digitize is not None and digitize.editing(layer):
            if features is not None and isinstance(features, list): features = features[0]
            return QvFitxaAtributs(layer, features, parent, QgsAttributeEditorContext.SingleEditMode)
        # Consulta de elemento(s)
        if features is not None and not isinstance(features, list): features = [features]
        return QvFitxesAtributs(layer, features, layer.selectedFeatureCount() == 0)


class QvFitxaAtributs(QgsAttributeDialog):
    def __init__(self, layer, feature, parent=None, mode=None, selectFeature=True):
        super().__init__(layer, feature, False, parent)
        self.layer = layer
        self.selectFeature = selectFeature
        self.resize(600, 650)
        if mode is not None:
            self.setMode(mode)
        if self.selectFeature:
            self.layer.selectByIds([feature.id()])
            self.finished.connect(self.finish)

    def finish(self, int):
        if self.selectFeature:
            self.layer.selectByIds([])


class QvFitxesAtributs(QDialog):
    def __init__(self, layer, features, selectFeature=True):
        QDialog.__init__(self)
        self.ui = Ui_AtributsForm()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.finished.connect(self.finish)
        self.layer = layer
        self.features = features
        self.selectFeature = selectFeature
        self.title = self.layer.name() + " - Atributs d'objecte"
        self.total = len(self.features)
        if self.total > 0:
            for feature in self.features:
                form = QgsAttributeForm(self.layer, feature)
                self.ui.stackedWidget.addWidget(form)
            self.visibleButtons()
            self.go(0)

    def setTitle(self, n):
        if self.total > 1:
            self.setWindowTitle(self.title + ' (' + str(n+1) + ' de ' + str(self.total) + ')')
        else:
            self.setWindowTitle(self.title)

    def setMenu(self, n):
        self.menuBar = QMenuBar()
        self.menu = QgsActionMenu(self.layer, self.features[n], 'Feature')
        if self.menu is not None and not self.menu.isEmpty():
            self.menuBar.addMenu(self.menu)
            self.menuBar.setVisible(True)
        else:
            self.menuBar.setVisible(False)
        self.layout().setMenuBar(self.menuBar)

    def select(self, n=None):
        if not self.selectFeature:
            return
        if n is None:
            self.layer.selectByIds([])  
        else:
            self.layer.selectByIds([self.features[n].id()])

    def go(self, n):
        if n >= 0 and n < self.total:
            self.select(n)
            self.setTitle(n)
            self.setMenu(n)
            self.ui.stackedWidget.setCurrentIndex(n)

    def move(self, inc):
        n = (self.ui.stackedWidget.currentIndex() + inc) % self.total
        self.go(n)

    def visibleButtons(self):
        if self.total > 1:
            self.ui.bPrev.clicked.connect(lambda: self.move(-1))
            self.ui.bNext.clicked.connect(lambda: self.move(1))
            self.ui.groupBox.setVisible(True)
        else:
            self.ui.groupBox.setVisible(False)

    def finish(self, int):
        self.select(None)

