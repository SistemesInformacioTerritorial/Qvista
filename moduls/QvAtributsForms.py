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
        # Donat que fer un if-else en una dict comprehension és molt estrany, fem primer un generador amb el contingut, i després ho passem al diccionari
        capesAux = ((feat[0],feat[1]) if isinstance(feat, tuple) else (feat,layer) for feat in self.features)
        self.capesCorresponents = {x[0]:x[1] for x in capesAux}
        self.features = list(self.capesCorresponents.keys())
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
        layersDiferents = set()
        for feature in self.features:
            layer = self.capesCorresponents[feature]
            form = QgsAttributeForm(layer, feature)
            layersDiferents.add(layer)
            # form.setMode(QgsAttributeEditorContext.IdentifyMode)
            self.ui.stackedWidget.addWidget(form)
        # baseTitol = self.layer.name() if len(layersDiferents)==1 else 'Consulta multicapa'
        baseTitol = '{}'
        if self.total > 1:
            self.title = baseTitol + " - Consulta fitxa elements"
            self.ui.bPrev.clicked.connect(lambda: self.move(-1))
            self.ui.bNext.clicked.connect(lambda: self.move(1))
            self.ui.groupBox.setVisible(True)
        else:
            self.title = baseTitol + " - Consulta fitxa element"
            self.ui.groupBox.setVisible(False)

    def setDefaultValues(self, feature):
        layer = self.capesCorresponents[feature]
        for idx in layer.attributeList():
            vDef = layer.defaultValue(idx, feature)
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
        layer = self.capesCorresponents[feature]
        if new:
            self.mode = QgsAttributeEditorContext.AddFeatureMode 
            self.title = layer.name() + " - Fitxa nou element"
            self.setDefaultValues(feature)
            form = QgsAttributeDialog(layer, feature, False)
        else:
            self.mode = QgsAttributeEditorContext.SingleEditMode
            self.title = layer.name() + " - Edició fitxa element"
            form = QgsAttributeDialog(layer, feature, False)
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
        titolAct = self.title.format(self.capesCorresponents[self.features[n]].name())
        if self.total > 1:
            self.setWindowTitle(titolAct + ' (' + str(n+1) + ' de ' + str(self.total) + ')')
        else:
            self.setWindowTitle(titolAct)

    def setMenu(self, n):
        if self.mode is None: # Consulta
            # Al añadir el menú, cambia el tamaño del form.
            # Hay que guardarlo y restaurarlo
            size = self.size()
            self.menuBar = QMenuBar()
            self.menu = QgsActionMenu(self.layer, self.features[n], 'Feature')
            if self.menu is not None and not self.menu.isEmpty():
                self.menuBar.addMenu(self.menu)
                self.menuBar.setVisible(True)
            else:
                self.menuBar.setVisible(False)
            self.layout().setMenuBar(self.menuBar)
            self.resize(size)

    def select(self, n=None):
        # if not self.selectFeature:
        #     return
        if n is None:
            self.layer.removeSelection()
        else:
            layer = self.capesCorresponents[self.features[n]]
            QvDigitizeContext.selectAndScrollFeature(self.features[n].id(), layer, self.attributes)
    
    def deselect(self,n):
        layer = self.capesCorresponents[self.features[n]]
        layer.removeSelection()

    def go(self, n):
        if n >= 0 and n < self.total:
            self.deselect(self.ui.stackedWidget.currentIndex())
            self.select(n)
            self.setTitle(n)
            self.setMenu(n)
            self.ui.stackedWidget.setCurrentIndex(n)

    def move(self, inc):
        n = (self.ui.stackedWidget.currentIndex() + inc) % self.total
        self.go(n)
    def moveWid(self,x,y):
        # En general, els QWidgets tenen una funció move, que serveix per moure el widget de posició
        # En aquest cas, donat que hem fet una funció "move" que feia una altra cosa (canviar la pantalla),
        #  necessitem una altra funció move per fer el move normal
        # més info: https://doc.qt.io/qt-5/qwidget.html#pos-prop
        # Nota: potser calgui fer-ne una altra per fer el move(QPoint)
        super().move(x,y)

    def finish(self, int):
        self.select(None)
