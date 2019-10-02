# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsVectorLayerCache
from qgis.PyQt import QtWidgets  # , uic
from qgis.PyQt.QtCore import Qt, pyqtSignal, QSize
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QTabWidget, QVBoxLayout, QAction, QMenuBar, QWidget, QHBoxLayout, QLabel
from qgis.gui import (QgsGui,
                      QgsAttributeTableModel,
                      QgsAttributeTableView,
                      QgsAttributeTableFilterModel,
                      QgsAttributeForm,
                      QgsSearchQueryBuilder,
                      QgsActionMenu)
from moduls.QvAccions import QvAccions
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton
# import images_rc  # NOQA
# import recursos
import csv
# import xlwt - .xls
from PyQt5.QtWidgets import QDialog

from moduls.Ui_AtributsForm import Ui_AtributsForm


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
        self.title = self.windowTitle()
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


class QvAtributs(QTabWidget):

    clicatMenuContexte = pyqtSignal('PyQt_PyObject')
    modificatFiltreCapa = pyqtSignal('PyQt_PyObject')

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        # self.layout = QVBoxLayout(self)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tancarTab)

        self.setWhatsThis(QvApp().carregaAjuda(self))

        # Conjunto de acciones de usuario
        self.accions = QvAccions()
        # Lista de acciones en el menú de contexto
        self.menuAccions = []
        self.cwidget=QWidget(self) #Corner Widget
        clayout=QHBoxLayout()
        clayout.setContentsMargins(10,0,0,0)
        self.cwidget.setLayout(clayout)
        self.setCornerWidget(self.cwidget,Qt.TopLeftCorner)
        self.desaCsv=QvPushButton(flat=True,parent=self)
        self.desaCsv.setIcon(QIcon('Imatges/file-delimited.png'))
        self.desaCsv.setIconSize(QSize(24,24))
        self.desaCsv.setToolTip('Desar taula com a csv')
        self.filtra=QvPushButton(flat=True,parent=self)
        self.filtra.setIcon(QIcon('Imatges/filter.png'))
        self.filtra.setIconSize(QSize(24,24))
        self.filtra.setToolTip('Filtrar/modificar filtre')
        self.eliminaFiltre=QvPushButton(flat=True,parent=self)
        self.eliminaFiltre.setIcon(QIcon('Imatges/filter-remove.png'))
        self.eliminaFiltre.setIconSize(QSize(24,24))
        self.eliminaFiltre.setToolTip('Eliminar filtre')
        self.eliminaFiltre.hide()
        clayout.addWidget(self.desaCsv,Qt.AlignCenter)
        clayout.addWidget(self.filtra,Qt.AlignCenter)
        clayout.addWidget(self.eliminaFiltre,Qt.AlignCenter)
        # self.filtra.clicked.connect(self.filterElements)


    def setMenuAccions(self, layer):
        self.menuAccions = ['showFeature', 'selectElement', 'selectAll']
        if layer.selectedFeatureCount() > 0:
            self.menuAccions += [
                'separator',
                'flashSelection', 'zoomToSelection', 'showSelection',
                'invertSelection', 'removeSelection']
        self.menuAccions += [
            'separator',
            'filterElements']
        if layer.subsetString() != '':
            self.menuAccions += ['removeFilter']
        self.menuAccions += ['saveToCSV']

    def tabTaula(self, layer, current=False):
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
        self.filtra.disconnect()
        self.desaCsv.disconnect()
        self.eliminaFiltre.disconnect()
        self.filtra.clicked.connect(taula.filterElements)
        self.desaCsv.clicked.connect(taula.saveToCSV)
        self.eliminaFiltre.clicked.connect(taula.removeFilter)
        i = self.addTab(taula, taula.layerNom())
        taula.canviNomTaula.connect(self.setTabText)
        self.setCurrentIndex(i)
        self.setTabText(i,self.tabText(i))
    def setTabText(self,i,text):
        super().setTabText(i,text+' (%i)'%len(self.widget(i)))

    def tancarTab(self, i):
        # Cerrar tabla por número de tab
        num = self.count()
        if i in range(0, num):
            taula = self.widget(i)
            if taula is not None:
                taula.deleteLater()
                self.removeTab(i)

    def tancarTaula(self, layer): #???
        # Cerrar tabla por layer
        if layer is None:
            return
        num = self.count()
        for i in range(0, num):
            taula = self.widget(i)
            if taula is not None and taula.layer.id() == layer.id():
                taula.deleteLater()
                self.removeTab(i)
                return

    def tancarTaules(self, layers):
        # Cerrar tablas de un conjunto de layers
        if layers is None:
            return
        ids = []
        for layer in layers:
            ids.append(layer.id())
        num = self.count()
        if num > 0:
            for i in range(num-1, -1, -1):
                taula = self.widget(i)
                if taula is not None and taula.layer.id() in ids:
                    taula.deleteLater()
                    self.removeTab(i)

    def deleteTabs(self):
        # Cerrar todas las tablas
        num = self.count()
        if num > 0:
            for i in range(num-1, -1, -1):
                taula = self.widget(i)
                if taula is not None:
                    taula.deleteLater()
                self.removeTab(i)

    def filtrarCapa(self, layer, on=True):
        try:
            filtro = layer.subsetString()
            if on:
                dlgFiltre = QgsSearchQueryBuilder(layer)
                dlgFiltre.setSearchString(filtro)
                ok = dlgFiltre.exec_()
                if ok != 1:
                    return
                nuevoFiltro = dlgFiltre.searchString()     
            else:
                nuevoFiltro = ''
            
            #Podria semblar que podem aprofitar l'if-else anterior. Però si ho féssim no estaríem tenint en compte el cas d'aplicar un filtre buit
            if nuevoFiltro=='':
                self.eliminaFiltre.hide()
            else:              
                self.eliminaFiltre.show()

            if nuevoFiltro != filtro:
                layer.setSubsetString(nuevoFiltro)
                self.modificatFiltreCapa.emit(layer)

        except Exception as e:
            print(str(e))

    def desarCSV(self, layer, selected=False):
        try:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Desa dades a arxiu', '', 'CSV (*.csv)')
            if path is not None:
                with open(path, 'w', newline='') as stream:
                    writer = csv.writer(
                        stream, delimiter=';', quotechar='¨',
                        quoting=csv.QUOTE_MINIMAL)
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
            return None
    # def setCurrentIndex(self,i):
    #     super().setCurrentIndex(i)
    #     self.lblCount.setText(str(len(self.currentWidget()))+' ')


class QvTaulaAtributs(QgsAttributeTableView):

    canviNomTaula = pyqtSignal(int, str)

    def __init__(self, parent=None, layer=None, canvas=None, numCache=10000):
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

    def init(self, layer, canvas, numCache=10000):
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
            menu = self.accions.menuAccions(self.parent.menuAccions,
                                            self.parent.accions.accions,
                                            self.featureActions())
            if menu is not None:
                menu.exec_(QCursor.pos())

    def crearDialog(self):
        dialog = None
        try:
            modelIndex = self.currentIndex()
            if modelIndex is not None and modelIndex.isValid():
                self.feature = self.model.feature(modelIndex)
                if self.feature is not None and self.feature.isValid():
                    num = self.layer.selectedFeatureCount()
                    dialog = QvFitxesAtributs(self.layer, [self.feature], num == 0)
                #     dialog = QgsAttributeDialog(
                #         self.layer, self.feature, False)
                #     # dialog = QgsAttributeForm(self.layer, self.feature)
                #     if filtre:
                #         dialog.setWindowTitle(self.layer.name() + ' - Filtres')
                #         dialog.setMode(QgsAttributeForm.SearchMode)
                #     else:
                #         dialog.setWindowTitle(
                #             self.layer.name() +
                #             ' - Element ' + str(self.feature.id()))
                #         dialog.setMode(QgsAttributeForm.SingleEditMode)
        except Exception:
            pass
        return dialog

    def featureActions(self):
        try:
            modelIndex = self.currentIndex()
            if modelIndex is not None and modelIndex.isValid():
                self.feature = self.model.feature(modelIndex)
                if self.feature is not None and self.feature.isValid():
                    menuExtra = QgsActionMenu(
                        self.layer, self.feature, 'Feature', self.canvas)
                    if menuExtra is not None and not menuExtra.isEmpty():
                        return menuExtra
            return None
        except Exception:
            return None

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

    def toggleSelection(self, check=True):
        if check:
            self.filter.setFilterMode(
                QgsAttributeTableFilterModel.ShowSelected)
        else:
            self.filter.setFilterMode(QgsAttributeTableFilterModel.ShowAll)
        self.accions.accio('showSelection').setChecked(check)
        self.layerTab()

    def showSelection(self):
        if (self.layer.selectedFeatureCount() > 0 and
                self.filter.filterMode() ==
                QgsAttributeTableFilterModel.ShowAll):
            self.toggleSelection(True)
        else:
            self.toggleSelection(False)

    def layerSelection(self):
        if self.layer.selectedFeatureCount() == 0:
            self.toggleSelection(False)
        else:
            self.layerTab()

    def saveToCSV(self):
        self.parent.desarCSV(
            self.layer,
            self.filter.filterMode() ==
            QgsAttributeTableFilterModel.ShowSelected)
    def __len__(self):
        return self.layer.featureCount()


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsMapCanvas
    from qgis.PyQt.QtWidgets import QMessageBox, QWhatsThis
    from moduls.QvLlegenda import QvLlegenda

    from moduls.QvPlotly import QvChart

    with qgisapp() as app:

        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        # win = uic.loadUi('moduls/Dialog.ui')  # specify the location of your .ui file
        # win.buttonBox.accepted.connect(win.accept)
        # result = win.exec_()
        # if result == QDialog.Accepted:
        #     print('OK')

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

        # Creación dinamica de objeto por nombre
        # mod = sys.modules['moduls.QvPlotly']
        # cls = getattr(mod, 'QvChart')
        # chart = cls()
        # print(type(chart))
        # print(vars(chart))

        chart = QvChart()
        chart.setGeometry(50, 50, 1200, 700)
        chart.setWindowTitle('Gràfics')

        def salutacions(txt):
            if txt == '':
                txt = 'Salutacions'
            QMessageBox().information(None, txt, 'qVista - Menú QvAtributs ')

        # Acciones personalizadas para menú contextual de la leyenda:
        #
        # - Definición de la acción y del metodo asociado
        # - Se añade la acción a la lista de acciones disponibles
        #   (llegenda.accions)
        # - Se redefine la lista de acciones que apareceran en el menú
        #   (llegenda.menuAccions) mediante la señal clicatMenuContexte
        #   según el tipo de nodo clicado
        #   (Tipos: none, group, layer, symb)

        # Accines de usuario para el menú
        act = QAction()
        act.setText("Salutacions")
        act.triggered.connect(lambda: salutacions(capa.name()))
        atributs.accions.afegirAccio('salutacions', act)

        act = QAction()
        act.setText("Help mode")
        act.triggered.connect(QWhatsThis.enterWhatsThisMode)
        atributs.accions.afegirAccio('helpmode', act)

        act = QAction()
        act.setText("Gràfic població")
        act.triggered.connect(lambda: poblacioBarChart(capa))
        atributs.accions.afegirAccio('chartpoblacio', act)

        act = QAction()
        act.setText("Gràfic densitat")
        act.triggered.connect(lambda: densitatBarChart(capa))
        atributs.accions.afegirAccio('chartdensitat', act)

        capa = None

        def poblacioBarChart(capa):
            chart.showNormal()
            chart.activateWindow()
            chart.poblacioBarChart(capa)

        def densitatBarChart(capa):
            chart.showNormal()
            chart.activateWindow()
            chart.densitatBarChart(capa)

        def menuContexte(layer):
            global capa
            capa = layer
            atributs.menuAccions.append('separator')
            atributs.menuAccions.append('salutacions')
            atributs.menuAccions.append('helpmode')
            if 'DISTRICTE' in capa.name().upper():
                atributs.menuAccions.append('separator')
                atributs.menuAccions.append('chartpoblacio')
                atributs.menuAccions.append('chartdensitat')

        atributs.clicatMenuContexte.connect(menuContexte)

        # QWhatsThis.enterWhatsThisMode()
