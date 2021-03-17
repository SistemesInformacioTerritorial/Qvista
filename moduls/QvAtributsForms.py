# -*- coding: utf-8 -*-

from qgis.gui import QgsAttributeForm, QgsAttributeDialog, QgsActionMenu, QgsAttributeEditorContext, QgsGui
from qgis.PyQt.QtWidgets import QDialog, QMenuBar, QDialogButtonBox, QPushButton

from moduls.Ui_AtributsForm import Ui_AtributsForm
from moduls.QvDigitizeContext import QvDigitizeContext

class QvFormAtributs:

    @staticmethod
    def create(layer, features, parent=None, attributes=None, new=False):
        """Crea un formulario para dar de alta, modificar o consultar datos alfanuméricos de un elemento.
           Cuando se trata de una consulta, puede mostrar una lista de elementos.

        Args:
            layer (QgsVectorLayer): Capa vectorial
            features (QgsFeature o [QgsFeature]): Elemento o lista de elementos
            parent (QWidget, optional): Widget padre del formulario creado. Defaults to None.
            attributes (QvAtributs, optional): Widget con las tablas de atributos. Defaults to None.
            new (bool, optional): Indica que se trata de un alta cuando se está en modo edición.
                                  Defaults to False.
        Returns:
            QDialog: Formulario de alta / modificación / consulta de elemento(s)
        """
        return QvFitxesAtributs(layer, features, parent, attributes, new)

    @staticmethod
    def toList(var):
        if var is None:
            return None, 0
        if isinstance(var, list):
            return var, len(var)
        else:
            return [var], 1


class QvFitxesAtributs(QDialog):

    def __init__(self, layer, features, parent=None, attributes=None, new=False):
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
        QDialog.__init__(self, parent)
        self.initUI()
        self.layer = layer
        self.features, self.total = QvFormAtributs.toList(features)
        self.attributes = attributes
        self.mode = None
        # self.selectFeature = self.layer.selectedFeatureCount() == 0
        if self.attributes is not None and self.attributes.llegenda is not None and self.attributes.llegenda.editing(layer):
            self.edicion(new)
        else:
            self.consulta()
        self.go(0)

    def initUI(self):
        self.ui = Ui_AtributsForm()
        self.ui.setupUi(self)
        self.finished.connect(self.finish)
        self.ui.buttonBox.accepted.connect(self.accept)

    def consulta(self):
        for feature in self.features:
            form = QgsAttributeForm(self.layer, feature)
            # form.setMode(QgsAttributeEditorContext.IdentifyMode)
            self.ui.stackedWidget.addWidget(form)
        if self.total > 1:
            self.title = self.layer.name() + " - Consulta fitxa elements"
            self.ui.bPrev.clicked.connect(lambda: self.move(-1))
            self.ui.bNext.clicked.connect(lambda: self.move(1))
            self.ui.groupBox.setVisible(True)
        else:
            self.title = self.layer.name() + " - Consulta fitxa element"
            self.ui.groupBox.setVisible(False)

    def setDefaultValues(self, feature):
        for idx in self.layer.attributeList():
            vDef = self.layer.defaultValue(idx, feature)
            feature.setAttribute(idx, vDef)

    def addRemoveButton(self, form):
        bDel = QPushButton("Esborra element")
        bDel.clicked.connect(lambda: self.remove(form.feature()))
        buttonBox = form.findChild(QDialogButtonBox)
        buttonBox.addButton(bDel, QDialogButtonBox.ResetRole)

    def edicion(self, new):
        self.newFeature = None
        self.total = 1
        feature = self.features[0]
        if new:
            self.mode = QgsAttributeEditorContext.AddFeatureMode 
            self.title = self.layer.name() + " - Fitxa nou element"
            self.setDefaultValues(feature)
            form = QgsAttributeDialog(self.layer, feature, False)
        else:
            self.mode = QgsAttributeEditorContext.SingleEditMode
            self.title = self.layer.name() + " - Edició fitxa element"
            form = QgsAttributeDialog(self.layer, feature, False)
            self.addRemoveButton(form)
        form.setMode(self.mode)
        form.attributeForm().featureSaved.connect(self.featureSaved)
        form.accepted.connect(self.formAccepted)
        form.rejected.connect(self.close)
        self.ui.stackedWidget.addWidget(form)
        self.ui.groupBox.setVisible(False)
        self.ui.buttonBox.setVisible(False)

    def featureSaved(self, feature):
        self.newFeature = feature

    def formAccepted(self):
        if self.newFeature is not None:
            self.attributes.tabTaula(self.layer, True, self.newFeature.id())
        self.close()

    def remove(self, feature):
        taula = self.attributes.tabTaula(self.layer)
        if taula is not None:
            taula.removeFeature(feature)
        self.close()

    def setTitle(self, n):
        if self.total > 1:
            self.setWindowTitle(self.title + ' (' + str(n+1) + ' de ' + str(self.total) + ')')
        else:
            self.setWindowTitle(self.title)

    def setMenu(self, n):
        if self.mode is None: # Consulta
            self.menuBar = QMenuBar()
            self.menu = QgsActionMenu(self.layer, self.features[n], 'Feature')
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
            self.layer.removeSelection()
        else:
            QvDigitizeContext.selectAndScrollFeature(self.features[n].id(), self.layer, self.attributes)

    def go(self, n):
        if n >= 0 and n < self.total:
            self.select(n)
            self.setTitle(n)
            self.setMenu(n)
            self.ui.stackedWidget.setCurrentIndex(n)

    def move(self, inc):
        n = (self.ui.stackedWidget.currentIndex() + inc) % self.total
        self.go(n)

    def finish(self, int):
        self.select(None)
