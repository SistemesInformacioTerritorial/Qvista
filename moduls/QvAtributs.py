# -*- coding: utf-8 -*-

from qgis.core import QgsMapLayer, QgsVectorLayerCache
from qgis.PyQt import QtWidgets  # , uic
from qgis.PyQt.QtCore import Qt, pyqtSignal, QSize, pyqtSlot
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QAction, QHBoxLayout, QTabWidget, QWidget, QMenu, QMessageBox, QAbstractItemView

from qgis.gui import (QgsGui,
                      QgsAttributeTableModel,
                      QgsAttributeTableView,
                      QgsAttributeTableFilterModel,
                      QgsSearchQueryBuilder,
                      QgsActionMenu)
from moduls.QvAccions import QvAccions
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton
from moduls.QvDiagrama import QvDiagrama
from moduls.QvAtributsForms import QvFormAtributs

# import images_rc  # NOQA
# import recursos
import os
import csv
import functools
# import xlwt - .xls

from configuracioQvista import imatgesDir

class QvAtributs(QTabWidget):

    clicatMenuContexte = pyqtSignal('PyQt_PyObject')
    modificatFiltreCapa = pyqtSignal('PyQt_PyObject')

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.llegenda = None
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
        self.desaCsv.setIcon(QIcon(os.path.join(imatgesDir,'file-delimited.png')))
        self.desaCsv.setIconSize(QSize(24,24))
        self.desaCsv.setToolTip('Desar taula com a csv')
        self.filtra=QvPushButton(flat=True,parent=self)
        self.filtra.setIcon(QIcon(os.path.join(imatgesDir,'filter.png')))
        self.filtra.setIconSize(QSize(24,24))
        self.filtra.setToolTip('Filtrar/modificar filtre')
        self.eliminaFiltre=QvPushButton(flat=True,parent=self)
        self.eliminaFiltre.setIcon(QIcon(os.path.join(imatgesDir,'filter-remove.png')))
        self.eliminaFiltre.setIconSize(QSize(24,24))
        self.eliminaFiltre.setToolTip('Eliminar filtre')
        self.eliminaFiltre.hide()
        clayout.addWidget(self.desaCsv,Qt.AlignCenter)
        clayout.addWidget(self.filtra,Qt.AlignCenter)
        clayout.addWidget(self.eliminaFiltre,Qt.AlignCenter)
        self.currentChanged.connect(self.setCurrentIndex)
        # self.filtra.clicked.connect(self.filterElements)

    def setMenuAccions(self, layer):
        self.menuAccions = []
        self.menuAccions += ['showFeature', 'selectElement', 'selectAll']
        if layer.selectedFeatureCount() > 0:
            self.menuAccions += [
                'separator',
                'flashSelection', 'zoomToSelection', 'showSelection',
                'invertSelection', 'removeSelection']
        self.menuAccions += ['separator']
        if QvDiagrama.capaAmbDiagrama(layer) != '':
            self.menuAccions += ['showBarChart']
        self.menuAccions += ['updateData', 'filterElements']
        if layer.subsetString() != '':
            self.menuAccions += ['removeFilter']
        self.menuAccions += ['saveToCSV']

    def numTaula(self, layer):
        if layer is not None:
            num = self.count()
            for i in range(0, num):
                taula = self.widget(i)
                if taula.layer.id() == layer.id():
                    return i
        return -1

    def tabTaula(self, layer, current=False, fid=None):
        # Ver si la tabla ya está abierta y, eventualmente, activar la pestaña y mostrar registro
        i = self.numTaula(layer)
        if i >= 0:
            taula = self.widget(i)
            txt = taula.layerNom()
            self.setTabText(i, txt)
            if current:
                self.setCurrentIndex(i)
                if fid is not None:
                    taula.scrollToFid(fid)
            return taula
        return None

    def obrirTaula(self, layer):
        # Abrir tabla por layer
        if layer is None:
            return
        # Si la tabla está abierta, mostrarla y actualizar nomnbre
        if self.tabTaula(layer, True) is not None:
            return
        
        # per assegurar que només es fa el connect una vegada, posem aquesta variable
        # la següent vegada que s'entri a aquesta funció, com que la variable ja tindrà valor, no tornarà a connectar-la
        if not hasattr(layer, '_subsetStringConnectat'):
            # Equivalent a la crida següent
            #  layer.subsetStringChanged.connect(lambda: self.actualitzaBoto(layer))
            # En bucles i altres àmbits utilitzar el mètode de la lambda pot fallar. Aquí no, però per si de cas...
            layer.subsetStringChanged.connect(functools.partial(self.actualitzaBoto,layer))
            layer._subsetStringConnectat = True
        # Si no se ha encontrado la tabla, añadirla
        taula = QvTaulaAtributs(self, layer, self.canvas)

        # self.filtra.disconnect()
        # self.desaCsv.disconnect()
        # self.eliminaFiltre.disconnect()
        # self.filtra.clicked.connect(taula.filterElements)
        # self.desaCsv.clicked.connect(taula.saveToCSV)
        # self.eliminaFiltre.clicked.connect(taula.removeFilter)
        i = self.addTab(taula, taula.layerNom())
        taula.canviNomTaula.connect(self.setTabText)
        self.setCurrentIndex(i)
        self.setTabText(i,self.tabText(i))

    def setTabText(self,i,text):
        l=len(self.widget(i))
        super().setTabText(i,text+(' (%i)'%l if l!=0 else ''))

    def removeTab(self, i):
        super().removeTab(i)
        if self.count() == 0:
            dw = self.parent()
            if dw is None:
                self.hide()
            else:
                dw.hide()

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
    
    @pyqtSlot('PyQt_PyObject')
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
            if self.llegenda is not None and self.llegenda.editing(layer):
                QMessageBox.information(self, "Atenció", "No es pot modificar el filtre d'una capa mentre s'està editant")
                return
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
                self.tabTaula(layer)
                self.modificatFiltreCapa.emit(layer)

        except Exception as e:
            print(str(e))

    def formatAttributes(self, feature):
        # Hay que tratar de forma especial los campos de tipo fecha

        def removeSuffix(s, suffix):
            if suffix and s.endswith(suffix):
                return s[:-len(suffix)]
            return s

        row = feature.attributes()
        for i, field in enumerate(feature.fields()):
            if field.isDateOrTime():
                data = row[i]
                if not data.isNull():
                    # Si llega fecha con hora a 0, dejamos solo la fecha
                    row[i] = removeSuffix(data.toString(Qt.ISODate), 'T00:00:00')
        return row

    def desarCSV(self, layer, selected=False):        
        try:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Desa dades a arxiu', '', 'CSV (*.csv)')
            if path is not None:
                with open(path, 'w', encoding="utf-8", newline='') as stream:
                    writer = csv.writer(
                        stream, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(layer.fields().names())
                    if selected:
                        iterator = layer.getSelectedFeatures
                    else:
                        iterator = layer.getFeatures
                    for feature in iterator():
                        writer.writerow(self.formatAttributes(feature))
            return path
        except Exception as e:
            QMessageBox.warning(self, "Error al desar l'arxiu CSV", f"No s'ha pogut desar correctament l'arxiu {path}")
            print(str(e))
            return None

    def setCurrentIndex(self,i):
        super().setCurrentIndex(i)
        try:
            taula=self.currentWidget()
            try:
                self.filtra.disconnect()
                self.desaCsv.disconnect()
                self.eliminaFiltre.disconnect()
            except:
                pass
            self.filtra.clicked.connect(taula.filterElements)
            self.desaCsv.clicked.connect(taula.saveToCSV)
            self.eliminaFiltre.clicked.connect(taula.removeFilter)
        except:
            pass
        #Mirar si està filtrat

    def actualitzaBoto(self, layer=None):
        if layer is None:
            taula=self.currentWidget()
            layer=taula.layer
            if layer is None: return
        filtre=layer.subsetString()
        if filtre=='':
            self.eliminaFiltre.hide()
        else:
            self.eliminaFiltre.show()

class QvTaulaAtributs(QgsAttributeTableView):

    canviNomTaula = pyqtSignal(int, str)

    def __init__(self, parent=None, layer=None, canvas=None, numCache=10000, readOnly=True):
        if len(QgsGui.editorWidgetRegistry().factories()) == 0:
            QgsGui.editorWidgetRegistry().initEditors()
        super().__init__(parent)
        self.parent = parent
        self.init(layer, canvas, numCache, readOnly)

        # Conjunto de acciones predefinidas
        self.accions = QvAccions()
        self.setAccions()

        # Lista de acciones (de las predefinidas) que apareceran en el menú
        # self.menuAccions = []
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        
        self.layer.selectionChanged.connect(self.layerSelection)

    def init(self, layer, canvas, numCache, readOnly):
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

        # Edition
        if readOnly:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # def setHidenColumns(self, prefijo='__'):
    #     changed = False
    #     config = self.layer.attributeTableConfig()
    #     columns = config.columns()
    #     for column in columns:
    #         if column.name.startswith("__"):
    #             column.hidden = True
    #             changed = True
    #     if changed:
    #         config.setColumns(columns)
    #         self.layer.setAttributeTableConfig(config)
    #         self.filter.setAttributeTableConfig(config)
    #         self.setAttributeTableConfig(config)

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
        act.setText("Suprimeix selecció")
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
        act.setText("Mostra diagrama barres")
        act.triggered.connect(self.showBarChart)
        self.accions.afegirAccio('showBarChart', act)

        act = QAction()
        act.setText("Mostra fitxa")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.showFeature)
        self.accions.afegirAccio('showFeature', act)

        act = QAction()
        act.setText("Esborra element")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.removeFeature)
        self.accions.afegirAccio('removeFeature', act)

        act = QAction()
        act.setText("Filtra elements")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.filterElements)
        self.accions.afegirAccio('filterElements', act)

        act = QAction()
        act.setText("Actualitza dades")
        # act.setIcon(QIcon(':/Icones/ic_file_upload_black_48dp.png'))
        act.triggered.connect(self.updateData)
        self.accions.afegirAccio('updateData', act)

        act = QAction()
        act.setText("Suprimeix filtre")
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
            act = self.accions.accio('showFeature')
            if act is not None and self.parent.llegenda is not None:
                if self.parent.llegenda.editing(self.layer):
                    act.setText("Modifica fitxa")
                else:
                    act.setText("Mostra fitxa")
            menu = self.accions.menuAccions(self.parent.menuAccions,
                                            self.parent.accions.accions,
                                            self.featureActions())
            if menu is not None:
                menu.exec_(QCursor.pos())

    def scrollToFid(self, fid):
        index = self.filter.fidToIndex(fid)
        if index.isValid():
            self.scrollTo(index)

    def currentFeature(self):
        feature = None
        modelIndex = self.currentIndex()
        if modelIndex is not None and modelIndex.isValid():
            modelIndex = self.filter.mapToMaster(modelIndex)
            if modelIndex is not None and modelIndex.isValid():
                feature = self.model.feature(modelIndex)
        return feature

    def crearDialog(self):
        try:
            self.feature = self.currentFeature()
            if self.feature is not None and self.feature.isValid():
                return QvFormAtributs.create(self.layer, self.feature, self.parent, self.parent)                
        except Exception as e:
            print(str(e))
        return None

    def featureActions(self):
        try:
            self.feature = self.currentFeature()
            if self.feature is not None and self.feature.isValid():
                menuExtra = QgsActionMenu(self.layer, self.feature, 'Feature', self.canvas)
                if menuExtra is not None and not menuExtra.isEmpty():
                    return menuExtra
            return None
        except Exception:
            return None

    def showBarChart(self):
        self.diagrama = QvDiagrama.barres(self.layer)
        if self.diagrama is not None:
            self.diagrama.show()

    def showFeature(self):
        dlgFitxa = self.crearDialog()
        if dlgFitxa is not None:
            dlgFitxa.exec_()

    def removeFeature(self, feature=None):
        if feature == None:
            self.feature = self.currentFeature()
        else:
            self.feature = feature
        if self.feature is not None and self.feature.isValid():
            self.layer.deleteFeature(self.feature.id())
            self.parent.tabTaula(self.layer)
            self.layer.repaintRequested.emit()

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

    def updateData(self):
        try:
            self.layer.dataProvider().reloadData()
        except Exception as e:
            print(str(e))

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
        i = self.parent.numTaula(self.layer)
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
        return max(0,self.layer.featureCount())

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
        llegenda.project.read("D:/qVista/Codi/mapesOffline/qVista default map.qgs")

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

        chart = QvChart('C:/temp/qVista/dades/provaAtrs.html','Gràfic de prova atributs')
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
