# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsEditorWidgetSetup, QgsExpressionContextUtils
from qgis.gui import QgsAttributeForm, QgsAttributeDialog, QgsActionMenu, QgsAttributeEditorContext, QgsGui
from qgis.PyQt.QtWidgets import QWidget, QDialog, QMenuBar, QDialogButtonBox, QPushButton, QMessageBox, QScrollArea, QFrame
from qgis.PyQt.QtCore import QVariant

from moduls.Ui_AtributsForm import Ui_AtributsForm
from moduls.QvDigitizeContext import QvDigitizeContext
from moduls import QvFuncions
from moduls.QvApp import QvApp

class QvFormAtributs:

    @staticmethod
    def create(layer, features, parent=None, attributes=None, new=False):
        """Crea un formulario para dar de alta, modificar o consultar datos alfanuméricos de un elemento.
           Cuando se trata de una consulta, puede mostrar una lista de elementos.

        Args:
            layer (QgsVectorLayer): Capa vectorial
            features (QgsFeature o [QgsFeature]): Elemento o lista de elementos. Tambien puede contener, en lugar
                                                  de elementos, duplas compuestas de elemento y su capa correspondiente
                                                  (para consultas multicapa -> MABIM)
            parent (QWidget, optional): Widget padre del formulario creado. Defaults to None.
            attributes (QvAtributs, optional): Widget con las tablas de atributos. Defaults to None.
            new (bool, optional): Indica que se trata de un alta cuando se está en modo edición.
                                  Defaults to False.
        Returns:
            QDialog: Formulario de alta / modificación / consulta de elemento(s)
        """
        try:
            return QvFitxesAtributs(layer, features, parent, attributes, new)
        except Exception as e:
            QMessageBox.warning(parent, "Error al crear formulari",
                f"No s'ha pogut mostrar la fitxa del element seleccionat\n\nError intern: {e}")
            print(str(e))
            return None


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
        # Inicialización de editores para formularios
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
        # Borrado de las relaciones para mantener formularios simples
        # relManager = QgsProject().instance().relationManager()
        # relManager.clear()
        # Pruebas con proyecto TestRelaciones.qgs
        # - Generado con versión 3.16 LTR
        # - Capas GPKG marcadas como solo lectura
        # - Relaciones de 1 y 2 niveles
        # - Editados expresión de muestra y campo invisible
        QDialog.__init__(self, parent)
        self.initUI()
        self.layer = layer
        featuresList, self.total = QvFormAtributs.toList(features)
        # Donat que fer un if-else en una dict comprehension és molt estrany, fem primer un generador amb el contingut, i després ho passem al diccionari
        capesAux = ((feat[0],feat[1]) if isinstance(feat, tuple) else (feat,layer) for feat in featuresList)
        self.capesCorresponents = {x[0]:x[1] for x in capesAux}
        self.features = list(self.capesCorresponents.keys())
        self.attributes = attributes
        self.mode = -1
        self.autoCommit = False
        # self.selectFeature = self.layer.selectedFeatureCount() == 0
        self.paramsFormulari = QgsExpressionContextUtils.layerScope(layer).variable('qV_formulari')
        if QvFuncions.debugging() and self.paramsFormulari is not None: print(f'qV_formulari de capa {layer.name()}: {self.paramsFormulari}')
        if any([isinstance(feat, tuple) for feat in featuresList]) or self.attributes is None or self.attributes.llegenda is None:
            self.consulta()
        elif self.attributes.llegenda.editing(self.layer):
            self.edicion(new) # Altas, bajas y modificaciones
        elif self.attributes.llegenda.isLayerEditForm(self.layer):
            self.edicionForm() # Solo modificaciones
        else:
            self.consulta()
        self.go(0)

    def initUI(self):
        self.ui = Ui_AtributsForm()
        self.ui.setupUi(self)
        self.finished.connect(self.finish)
        self.ui.buttonBox.accepted.connect(self.accept)

    def getLayerFromFeature(self, feature):
        return self.capesCorresponents[feature]

    def layerRelations(self, layer):
        relManager = QgsProject().instance().relationManager()        
        return relManager.referencedRelations(layer)

    def formResize(self, layer):
        numRelations = len(self.layerRelations(layer))
        if numRelations == 0: w = 700
        elif numRelations == 1: w = 900
        else: w = 1100
        self.resize(w, 800)

    def setMenuBar(self, feature):
        # Al añadir el menú, cambia el tamaño del form.
        # Hay que guardarlo y restaurarlo
        size = self.size()
        if hasattr(self, 'menuBar'):
            self.menuBar.deleteLater()
        self.menuBar = QMenuBar()
        self.menu = QgsActionMenu(self.layer, feature, 'Feature')
        if self.menu is not None and not self.menu.isEmpty():
            self.menuBar.addMenu(self.menu)
            self.menuBar.setVisible(True)
        else:
            self.menuBar.setVisible(False)
        self.layout().setMenuBar(self.menuBar)
        self.resize(size)

    def noNullValues(self, layer, feature):
        # Esconde los campos del formulario cuando tienen valor NULL (si la variable de capa 'qV_formulari' tiene el valor 'nonull')
        listHidden = []
        if self.paramsFormulari == 'nonull':
            for idx, value in enumerate(feature):
                # int, float, str, QVariant
                if isinstance(value, QVariant) and value.isNull():
                    # nom = layer.fields()[idx].name()
                    listHidden.append((idx, layer.editorWidgetSetup(idx)))
                    layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup('Hidden', {}))
                    # layer.setEditorWidgetSetup(idx, QgsEditorWidgetSetup('TextEdit', {'IsMultiline': False, 'UseHtml': False}))
        return listHidden

    def emptyNullValues(self, layer):
        # Vacía los campos del formulario cuando tienen valor NULL (si la variable de capa 'qV_formulari' tiene el valor 'emptynull')
        nullStr = None
        if self.paramsFormulari == 'emptynull':
            nullStr = QvApp().appQgis.nullRepresentation()
            QvApp().appQgis.setNullRepresentation('')
        return nullStr

    def hideNullValues(self, layer, feature):
        # Tratamiento de campos a NULL del formulario segun variable de capa 'qV_formulari'
        listHidden = self.noNullValues(layer, feature)
        nullStr = self.emptyNullValues(layer)
        return listHidden, nullStr

    def showNullValues(self, layer, listHidden, nullStr):
        # Restaura los campos a NULL escondidos del formulario segun variable de capa 'qV_formulari'
        for item in listHidden:
            idx = item[0]
            setup = item[1]
            layer.setEditorWidgetSetup(idx, setup)
        if nullStr is not None:
            QvApp().appQgis.setNullRepresentation(nullStr)

    def consulta(self):
        self.autoCommit = False
        first = True
        layers = set(self.getLayerFromFeature(feature) for feature in self.features)
        for feature in self.features:
            layer = self.getLayerFromFeature(feature)
            if first:
                self.formResize(layer)
                first = False
            listHidden, nullStr = self.hideNullValues(layer, feature)
            form = QgsAttributeForm(layer, feature)
            # form.setMode(QgsAttributeEditorContext.IdentifyMode)
            self.showNullValues(layer, listHidden, nullStr)
            if len(layers)>1:
                scroll = QScrollArea()
                scroll.setWidget(form)
                scroll.setWidgetResizable(True)
                scroll.setFrameStyle(QFrame.NoFrame)
                self.ui.stackedWidget.addWidget(scroll)
            else:
                self.ui.stackedWidget.addWidget(form)
        baseTitol = '{}'
        if self.total > 1:
            self.title = baseTitol + " - Consulta fitxa elements"
            self.ui.bPrev.clicked.connect(lambda: self.moveIndex(-1))
            self.ui.bNext.clicked.connect(lambda: self.moveIndex(1))
            self.ui.groupBox.setVisible(True)
        else:
            self.title = baseTitol + " - Consulta fitxa element"
            self.ui.groupBox.setVisible(False)
        self.setMenuBar(feature)

    def setDefaultValues(self, feature):
        layer = self.getLayerFromFeature(feature)
        for idx in layer.attributeList():
            vDef = layer.defaultValue(idx, feature)
            feature.setAttribute(idx, vDef)

    def addRemoveButton(self, form):
        bDel = QPushButton("Esborra element")
        bDel.clicked.connect(lambda: self.remove(form.feature()))
        buttonBox = form.findChild(QDialogButtonBox)
        buttonBox.addButton(bDel, QDialogButtonBox.ResetRole)

    def removeMenuBar(self, form):
        menu = form.layout().menuBar()
        if menu is not None: menu.setVisible(False)

    def edicion(self, new):
        self.autoCommit = False
        self.newFeature = None
        self.total = 1
        feature = self.features[0]
        layer = self.getLayerFromFeature(feature)
        if new:
            self.mode = QgsAttributeEditorContext.AddFeatureMode 
            self.title = layer.name() + " - Fitxa nou element"
            self.setDefaultValues(feature)
            form = QgsAttributeDialog(layer, feature, False)
            self.removeMenuBar(form)
        else:
            self.mode = QgsAttributeEditorContext.SingleEditMode
            self.title = layer.name() + " - Edició fitxa element"
            form = QgsAttributeDialog(layer, feature, False)
            self.removeMenuBar(form)
            self.setMenuBar(feature)
            self.addRemoveButton(form)
        form.setMode(self.mode)
        form.attributeForm().featureSaved.connect(self.featureSaved)
        form.accepted.connect(self.formAccepted)
        form.rejected.connect(self.formRejected)
        self.ui.stackedWidget.addWidget(form)
        self.ui.groupBox.setVisible(False)
        self.ui.buttonBox.setVisible(False)
    
    def commit(self, ok):
        # Para cerrar los auto-commits y controlar los errores (ok a True, commit; a False, rollback)
        if not self.autoCommit: return
        if ok and not self.layer.commitChanges():
            QMessageBox.warning(self, "Error al modificar fitxa d'element", "\n".join(self.layer.commitErrors()))
        self.layer.rollBack()
        self.autoCommit = False

    def hideEvent(self, event):
        # Para capturar las salidas del formulario con tecla ESC o pulsando la cruz de cerrar ventana
        self.commit(False)
        QWidget.hideEvent(self, event)

    def featureSaved(self, feature):
        self.newFeature = feature

    def formAccepted(self):
        if self.newFeature is not None:
            self.attributes.tabTaula(self.layer, True, self.newFeature.id())
        self.commit(True)
        self.close()

    def formRejected(self):
        self.commit(False)
        self.close()
        
    def remove(self, feature):
        taula = self.attributes.tabTaula(self.layer)
        if taula is not None:
            taula.removeFeature(feature)
        self.close()

    def edicionForm(self):
        if self.layer.startEditing():
            self.autoCommit = True
            self.newFeature = None
            self.total = 1
            feature = self.features[0]
            layer = self.getLayerFromFeature(feature)
            self.mode = QgsAttributeEditorContext.SingleEditMode
            self.title = layer.name() + " - Modificació fitxa element"
            form = QgsAttributeDialog(layer, feature, False)
            self.removeMenuBar(form)
            self.setMenuBar(feature)
            form.setMode(self.mode)
            form.attributeForm().featureSaved.connect(self.featureSaved)
            form.accepted.connect(self.formAccepted)
            form.rejected.connect(self.formRejected)
            self.ui.stackedWidget.addWidget(form)
            self.ui.groupBox.setVisible(False)
            self.ui.buttonBox.setVisible(False)
        else:
            self.consulta()

    def setTitle(self, n):
        titolAct = self.title.format(self.getLayerFromFeature(self.features[n]).name())
        if self.total > 1:
            self.setWindowTitle(titolAct + ' (' + str(n+1) + ' de ' + str(self.total) + ')')
        else:
            self.setWindowTitle(titolAct)

    def select(self, n=None):
        # if not self.selectFeature:
        #     return
        if n is None:
            for layer in self.capesCorresponents.values():
                layer.removeSelection()
        else:
            layer = self.getLayerFromFeature(self.features[n])
            QvDigitizeContext.selectAndScrollFeature(self.features[n].id(), layer, self.attributes)
    
    def deselect(self,n):
        layer = self.getLayerFromFeature(self.features[n])
        layer.removeSelection()

    def go(self, n):
        if n >= 0 and n < self.total:
            self.deselect(self.ui.stackedWidget.currentIndex())
            self.select(n)
            self.setTitle(n)
            self.ui.stackedWidget.setCurrentIndex(n)

    def moveIndex(self, inc):
        n = (self.ui.stackedWidget.currentIndex() + inc) % self.total
        self.go(n)

    def finish(self, int):
        self.select(None)
