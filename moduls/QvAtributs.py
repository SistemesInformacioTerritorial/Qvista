# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsVectorLayerCache, QgsFeature
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt, QObject, QPoint, QModelIndex, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QTabWidget, QVBoxLayout, QMenu, QAction
from qgis.gui import (QgsGui,
                      QgsAttributeTableModel,
                      QgsAttributeTableView,
                      QgsAttributeTableFilterModel,
                      QgsAttributeDialog,
                      QgsAttributeForm,
                      QgsAttributeEditorContext,
                      QgsLayerTreeMapCanvasBridge,
                      QgsSearchQueryBuilder,
                      QgsBusyIndicatorDialog)
from moduls.QvAccions import QvAccions
from moduls.QvApp import QvApp
# import images_rc
# import recursos
import csv
# import xlwt - .xls

class QvAtributs(QTabWidget):

    clicatMenuContexte = pyqtSignal('PyQt_PyObject')
    modificatFiltreCapa = pyqtSignal('PyQt_PyObject')

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.layout = QVBoxLayout(self)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tancarTab)

        self.setWhatsThis(QvApp().carregaAjuda(self))

        # Conjunto de acciones de usuario
        self.accions = QvAccions()
        # Lista de acciones en el menú de contexto
        self.menuAccions = []

    def setMenuAccions(self, layer):
        self.menuAccions = ['showFeature', 'selectElement', 'selectAll']
        if layer.selectedFeatureCount() > 0:
            self.menuAccions +=['separator',
                                'flashSelection', 'zoomToSelection', 'showSelection',
                                'invertSelection', 'removeSelection']
        self.menuAccions += ['separator', 
                            'filterElements']
        if layer.subsetString() != '':
            self.menuAccions += ['removeFilter']
        self.menuAccions += ['saveToCSV']
  
    def tabTaula(self, layer, current = False):
    # Ver si la tabla ya está abierta y, eventualmente, activar la pestaña
        if layer is None:
            return False
        num = self.count()
        for i in range(0, num):
            taula = self.widget(i)
            if taula.layer.id() == layer.id():
                txt = taula.layerNom()
                self.setTabText(i, txt)
                print('tabTaula:', txt)
                if current:
                    self.setCurrentIndex(i)
                return True
        return False
    
    def obrirTaula(self, layer):
    # Abrir tabla por layer
        if layer is None:
            return
        # Si la tabla está abierta, mostrarla y actualizar nomnbre
        if self.tabTaula(layer, True):
            return
        # Si no se ha encontrado la tabla, añadirla
        taula = QvTaulaAtributs(self, layer, self.canvas)
        i = self.addTab(taula, taula.layerNom())
        taula.canviNomTaula.connect(self.setTabText)
        self.setCurrentIndex(i)
    
    def tancarTab(self, i):
    # Cerrar tabla por número de tab
        num = self.count()
        if i in range(0, num):
            taula = self.widget(i)
            taula.deleteLater()

    def tancarTaula(self, layer):
    # Cerrar tabla por layer
        if layer is None:
            return
        num = self.count()
        for i in range(0, num):
            taula = self.widget(i)
            if taula.layer.id() == layer.id():
                taula.deleteLater()
    
    def deleteTabs(self):
    # Cerrar todas las tablas
        num = self.count()
        for i in range(0, num):
            taula = self.widget(i)
            taula.deleteLater()
            self.removeTab(i)

    def filtrarCapa(self, layer, on = True):
        try:
            if on:
                dlgFiltre = QgsSearchQueryBuilder(layer)
                dlgFiltre.setSearchString(layer.subsetString())
                dlgFiltre.exec_()
                layer.setSubsetString(dlgFiltre.searchString())
            else:
                layer.setSubsetString('')
            self.modificatFiltreCapa.emit(layer)
        except Exception as e:
            print(str(e))

    def desarCSV(self, layer, selected = False):
        try:
            path,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Desa dades a arxiu', '', 'CSV (*.csv)')
            if path is not None:
                with open(path, 'w', newline='') as stream:
                    writer = csv.writer(stream, delimiter=';', quotechar='¨', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(layer.fields().names())
                    if selected:
                        iterator = layer.getSelectedFeatures
                    else:
                        iterator = layer.getFeatures
                    for feature in iterator():
                        writer.writerow(feature.attributes())
            return path                        
        except Exception as e:
            print(str(e))

class QvTaulaAtributs(QgsAttributeTableView):

    canviNomTaula = pyqtSignal(int, str)

    def __init__(self, parent = None, layer = None, canvas = None, numCache = 10000):
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
        super().__init__()
        self.parent = parent
        self.init(layer, canvas, numCache)

        # Conjunto de acciones predefinidas
        self.accions = QvAccions()
        self.setAccions()

        # Lista de acciones (de las predefinidas) que apareceran en el menú
        # self.menuAccions = []
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.layer.selectionChanged.connect(self.layerSelection)

    def init(self, layer, canvas, numCache = 10000):
        if not layer or not canvas:
            return
        if layer.type() != QgsMapLayer.VectorLayer:
            return
        self.layer = layer
        self.canvas = canvas

        # Model y caché
        self.cache = QgsVectorLayerCache(self.layer, numCache)
        self.model = QgsAttributeTableModel(self.cache)
        self.model.loadLayer()

        # Filter y view
        self.filter = QgsAttributeTableFilterModel(self.canvas, self.model)
        self.filter.setFilterMode(QgsAttributeTableFilterModel.ShowAll)
        self.setModel(self.filter)

    def setAccions(self):
        act = QAction()
        act.setText("Selecciona element")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.selectElement)
        self.accions.afegirAccio('selectElement', act)

        act = QAction()
        act.setText("Selecciona-ho tot")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.selectAll)
        self.accions.afegirAccio('selectAll', act)

        act = QAction()
        act.setText("Esborra selecció")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.removeSelection)
        self.accions.afegirAccio('removeSelection', act)

        act = QAction()
        act.setText("Inverteix selecció")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.invertSelection)
        self.accions.afegirAccio('invertSelection', act)

        act = QAction()
        act.setText("Enquadra selecció")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.zoomToSelection)
        self.accions.afegirAccio('zoomToSelection', act)

        act = QAction()
        act.setText("Flash selecció")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.flashSelection)
        self.accions.afegirAccio('flashSelection', act)

        act = QAction()
        act.setText("Mostra fitxa")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.showFeature)
        self.accions.afegirAccio('showFeature', act)

        act = QAction()
        act.setText("Filtra elements")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.filterElements)
        self.accions.afegirAccio('filterElements', act)

        act = QAction()
        act.setText("Esborra filtre")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.removeFilter)
        self.accions.afegirAccio('removeFilter', act)

        act = QAction()
        act.setText("Només seleccionats")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.showSelection)
        act.setCheckable(True)
        act.setChecked(False)
        self.accions.afegirAccio('showSelection', act)

        act = QAction()
        act.setText("Desa a CSV")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.saveToCSV)
        self.accions.afegirAccio('saveToCSV', act)

    def contextMenu(self, pos):
        if self.layer is not None and self.parent is not None:
            self.parent.setMenuAccions(self.layer)
            self.parent.clicatMenuContexte.emit(self.layer)
            menu = self.accions.menuAccions(self.parent.menuAccions, self.parent.accions.accions)
            if menu is not None:
                menu.exec_(QCursor.pos())

    def crearDialog(self, filtre = False):
        dialog = None
        try:
            modelIndex = self.currentIndex()
            if modelIndex is not None and modelIndex.isValid():
                self.feature = self.model.feature(modelIndex)
                if self.feature is not None and self.feature.isValid():
                    dialog = QgsAttributeDialog(self.layer, self.feature, False) # , self)
                    # dialog = QgsAttributeForm(self.layer, self.feature)
                    if filtre:
                        dialog.setWindowTitle(self.layer.name() + ' - Filtres')
                        dialog.setMode(QgsAttributeForm.SearchMode)
                    else:
                        dialog.setWindowTitle(self.layer.name() + ' - Element ' + str(self.feature.id() + 1))
                        dialog.setMode(QgsAttributeForm.SingleEditMode)
        except:
            pass
        return dialog

    def showFeature(self):
        dlgFitxa = self.crearDialog()
        if dlgFitxa is not None:
            dlgFitxa.exec_()

    def flashSelection(self):
        features = self.layer.selectedFeatureIds()
        self.canvas.flashFeatureIds(self.layer, features)
         
    def zoomToSelection(self):
        # box = self.layer.boundingBoxOfSelected()
        # self.canvas.setExtent(box)
        # self.canvas.refresh()
        self.canvas.zoomToSelected(self.layer)

    def filterElements(self):
        self.parent.filtrarCapa(self.layer, True)
        # global llegenda
        # llegenda.actIconaFiltre(self.layer)

        # # self.dlgFiltre = self.crearDialog(True)
        # try:
        #     self.dlgFiltre = QgsSearchQueryBuilder(self.layer)
        #     self.dlgFiltre.setSearchString(self.layer.subsetString())
        #     self.dlgFiltre.exec_()
        #     self.layer.setSubsetString(self.dlgFiltre.searchString())
        #     self.parent.modificatFiltreCapa.emit(self.layer)
        # except Exception as e:
        #     print(str(e))

    def removeFilter(self):
        self.parent.filtrarCapa(self.layer, False)
        # global llegenda
        # llegenda.actIconaFiltre(self.layer)
        # self.layer.setSubsetString('')
        # self.parent.modificatFiltreCapa.emit(self.layer)

    def selectElement(self):
        modelIndex = self.currentIndex()
        if modelIndex is not None and modelIndex.isValid():
            self.selectRow(modelIndex.row())

    def removeSelection(self):
        self.layer.removeSelection()

    def invertSelection(self):
        self.layer.invertSelection()

    def layerNom(self):
        num = self.layer.selectedFeatureCount()
        if num == 0:
            txt = self.layer.name()
        else:
            txt = self.layer.name() + ' [' + str(num) + ']'
        return txt

    def layerTab(self):
        tab = self.parentWidget()
        i = tab.currentIndex()
        txt = self.layerNom()
        self.canviNomTaula.emit(i, txt)

    def toggleSelection(self, check = True):
        if check:
            self.filter.setFilterMode(QgsAttributeTableFilterModel.ShowSelected)
        else:
            self.filter.setFilterMode(QgsAttributeTableFilterModel.ShowAll)
        self.accions.accio('showSelection').setChecked(check)
        self.layerTab()

    def showSelection(self):        
        if (self.layer.selectedFeatureCount() > 0 and
            self.filter.filterMode() == QgsAttributeTableFilterModel.ShowAll):
            self.toggleSelection(True)
        else:
            self.toggleSelection(False)

    def layerSelection(self):
        if self.layer.selectedFeatureCount() == 0:
            self.toggleSelection(False)
        else:
            self.layerTab()

    def saveToCSV(self):
        self.parent.desarCSV(self.layer, self.filter.filterMode() == QgsAttributeTableFilterModel.ShowSelected)

        # print('Num features/selected:', self.layer.featureCount(), self.layer.selectedFeatureCount())
        # try:
        #     path,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Desa dades a arxiu', '', 'CSV (*.csv)')
        #     if path is not None:
        #         with open(path, 'w', newline='') as stream:
        #             writer = csv.writer(stream, delimiter=';', quotechar='¨', quoting=csv.QUOTE_MINIMAL)
        #             writer.writerow(self.layer.fields().names())
        #             if  self.filter.filterMode() == QgsAttributeTableFilterModel.ShowSelected:
        #                 iterator = self.layer.getSelectedFeatures
        #             else:
        #                 iterator = self.layer.getFeatures
        #             for feature in iterator():
        #                 writer.writerow(feature.attributes())                        
        # except Exception as e:
        #     print(str(e))

if __name__ == "__main__":

    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox, QWhatsThis
    from moduls.QvLlegenda import QvLlegenda
    from qgis.PyQt.QtCore import QTranslator, QLocale, QLibraryInfo
    
    with qgisapp() as app:
 
        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        canvas = QgsMapCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        # llegenda.project.read('projectes/Illes.qgs')
        llegenda.project.read('../Dades/Projectes/BCN11.qgs')

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()

        # Abrimos una tabla de atributos
        # layer = llegenda.capaPerNom('Illes')
        # atributs.obrirTaula(layer)

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(50, 500, 1050, 250)
        llegenda.obertaTaulaAtributs.connect(atributs.show)

        def salutacions(txt):
            if txt == '':
                txt = 'Salutacions'
            QMessageBox().information(None, txt, 'qVista - Menú QvAtributs ')


        # Acciones personalizadas para menú contextual de la leyenda:
        #
        # - Definición de la acción y del metodo asociado
        # - Se añade la acción a la lista de acciones disponibles (llegenda.accions)
        # - Se redefine la lista de acciones que apareceran en el menú (llegenda.menuAccions)
        #   mediante la señal clicatMenuContexte según el tipo de nodo clicado
        #   (Tipos: none, group, layer, symb)

        # Accines de usuario para el menú
        act = QAction()
        act.setText("Salutacions")
        act.triggered.connect(lambda: salutacions(capa))
        atributs.accions.afegirAccio('salutacions', act)

        act = QAction()
        act.setText("Help mode")
        act.triggered.connect(QWhatsThis.enterWhatsThisMode)
        atributs.accions.afegirAccio('helpmode', act)

        capa = ''

        def menuContexte(layer):
            global capa
            capa = layer.name()
            atributs.menuAccions.append('separator')
            atributs.menuAccions.append('salutacions')
            atributs.menuAccions.append('helpmode')

        atributs.clicatMenuContexte.connect(menuContexte)

        # QWhatsThis.enterWhatsThisMode()


