# -*- coding: utf-8 -*-

from qgis.gui import QgsAttributeForm, QgsAttributeDialog, QgsActionMenu, QgsAttributeEditorContext
from qgis.PyQt.QtWidgets import QDialog, QMenuBar

from moduls.Ui_AtributsForm import Ui_AtributsForm

class QvFormAtributs:

    @staticmethod
    def create(layer, features, parent=None, attributes=None, new=False):
        """Crea un formulario para dar de alta, modificar o consultar datos alfanuméricos de un elemento.
           Cuando se trata de una consulta, puede mostrar una lista de elementos.

        Args:
            layer (QgsVectorLayer): Capa
            features (QgsFeature o [QgsFeature]): Elemento o lista de elementos
            parent (QWidget, optional): Widget padre del formulario creado. Defaults to None.
            attributes (QvAtributs, optional): Widget con las tablas de atributos para mostrar el
                                               registro seleccionado. Defaults to None.
            new (bool, optional): Si es True se trata de un alta. Defaults to False.

        Returns:
            QgsAttributeDialog o QDialog: Formulario de alta / edición o formulario de consulta de elemento(s)
        """
        # Alta de elemento
        if new:
            return QvFitxaAtributs(layer, features, parent, attributes, new)
        # Modificación de elemento
        if attributes is not None and attributes.llegenda is not None and attributes.llegenda.editing(layer):
            return QvFitxaAtributs(layer, features, parent, attributes)
        # Consulta de elemento(s)
        return QvFitxesAtributs(layer, features, parent, attributes)


class QvFitxaAtributs(QgsAttributeDialog):

    def __init__(self, layer, features, parent=None, attributes=None, new=False):
        self.reg = self.oneFeature(features)
        super().__init__(layer, self.reg, False, parent)
        self.resize(600, 650)
        self.layer = layer
        self.attributes = attributes
        self.new = new
        if self.new:
            self.setMode(QgsAttributeEditorContext.AddFeatureMode)
        else:
            self.setMode(QgsAttributeEditorContext.SingleEditMode)
            self.select(self.reg.id())
            self.finished.connect(self.finish)

    def oneFeature(self, features):
        if features is not None and isinstance(features, list):
            features = features[0]
        return features

    def select(self, fid):
        # Importante: Primero poner tab de capa y luego seleccionar feature
        if self.attributes is not None:
            self.attributes.tabTaula(self.layer, True, fid)
        self.layer.selectByIds([fid])

    def finish(self):
        self.layer.selectByIds([])


class QvFitxesAtributs(QDialog):

    def __init__(self, layer, features, parent=None, attributes=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_AtributsForm()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.finished.connect(self.finish)
        self.layer = layer
        self.regs = self.listFeatures(features)
        self.attributes = attributes
        # self.selectFeature = self.layer.selectedFeatureCount() == 0
        self.title = self.layer.name() + " - Atributs d'objecte"
        self.total = len(self.regs)
        if self.total > 0:
            for feature in self.regs:
                form = QgsAttributeForm(self.layer, feature)
                self.ui.stackedWidget.addWidget(form)
            self.visibleButtons()
            self.go(0)

    def listFeatures(self, features):
        if features is not None and not isinstance(features, list):
            features = [features]
        return features

    def setTitle(self, n):
        if self.total > 1:
            self.setWindowTitle(self.title + ' (' + str(n+1) + ' de ' + str(self.total) + ')')
        else:
            self.setWindowTitle(self.title)

    def setMenu(self, n):
        self.menuBar = QMenuBar()
        self.menu = QgsActionMenu(self.layer, self.regs[n], 'Feature')
        if self.menu is not None and not self.menu.isEmpty():
            self.menuBar.addMenu(self.menu)
            self.menuBar.setVisible(True)
        else:
            self.menuBar.setVisible(False)
        self.layout().setMenuBar(self.menuBar)

    def select(self, n=None):
        # if not self.selectFeature:
        #     return
        if n is None:
            self.layer.selectByIds([])  
        else:
            fid = self.regs[n].id()
            # Importante: Primero poner tab de capa y luego seleccionar feature
            if self.attributes is not None:
                self.attributes.tabTaula(self.layer, True, fid)
            self.layer.selectByIds([fid])

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

