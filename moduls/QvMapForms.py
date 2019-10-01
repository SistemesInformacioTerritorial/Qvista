# -*- coding: utf-8 -*-

from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor, QValidator, QIcon
from qgis.PyQt.QtWidgets import (QFileDialog, QWidget, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout,
                                 QComboBox, QLabel, QLineEdit, QSpinBox, QGroupBox, QGridLayout,
                                 QMessageBox, QDialogButtonBox)

from qgis.core import QgsApplication, QgsGraduatedSymbolRenderer, QgsExpressionContextUtils

from moduls.QvMapVars import *
from moduls.QvMapificacio import QvMapificacio

# class verifNumero(QValidator):
#     def validate(self, string, index):
#         txt = string.strip()
#         if txt == '':
#             state = QValidator.Intermediate
#         elif txt.isnumeric():
#             state = QValidator.Acceptable
#         else:
#             state = QValidator.Invalid
#         return (state, string, index)

class QvFormNovaMapificacio(QWidget):
    def __init__(self, llegenda):

        super().__init__(minimumWidth=360)
        self.llegenda = llegenda

        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle('Afegir capa de mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.arxiu = QgsFileWidget()
        self.arxiu.setStorageMode(QgsFileWidget.GetFile)
        self.arxiu.setDialogTitle('Selecciona fitxer de dades…')
        self.arxiu.setDefaultRoot(_RUTA_LOCAL)
        self.arxiu.setFilter('Arxius CSV (*.csv)')
        self.arxiu.setSelectedFilter('Arxius CSV (*.csv)')
        self.arxiu.lineEdit().setReadOnly(True)
        self.arxiu.fileChanged.connect(self.arxiuSeleccionat)

        self.zona = QComboBox(self)
        self.zona.setEditable(False)
        self.zona.addItem('Selecciona zona…')
        self.zona.addItems(_ZONES.keys())
        # self.zona.model().item(0).setEnabled(False)

        self.capa = QLineEdit(self)
        self.capa.setMaxLength(40)

        self.tipus = QComboBox(self)
        self.tipus.setEditable(False)
        self.tipus.addItem('Selecciona tipus…')
        self.tipus.addItems(_AGREGACIO.keys())

        self.distribucio = QComboBox(self)
        self.distribucio.setEditable(False)
        self.distribucio.addItems(_DISTRIBUCIO.keys())

        self.calcul = QLineEdit(self)

        self.filtre = QLineEdit(self)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItems(MAP_COLORS.keys())

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(_METODES.keys())

        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(9)
        self.intervals.setSingleStep(1)
        self.intervals.setValue(4)
        self.intervals.setSuffix("  (depèn del mètode)")
        # self.intervals.valueChanged.connect(self.deselectValue)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.gZona = QGroupBox('Definició zona')
        self.lZona = QFormLayout()
        self.lZona.setSpacing(10)
        self.gZona.setLayout(self.lZona)

        self.lZona.addRow('Arxiu dades:', self.arxiu)
        self.lZona.addRow('Zona:', self.zona)
        self.lZona.addRow('Nom capa:', self.capa)

        self.gDades = QGroupBox('Dades agregació')
        self.lDades = QFormLayout()
        self.lDades.setSpacing(10)
        self.gDades.setLayout(self.lDades)

        self.lDades.addRow('Tipus agregació:', self.tipus)
        self.lDades.addRow('Camp o fòrmula càlcul:', self.calcul)
        self.lDades.addRow('Filtre:', self.filtre) 
        self.lDades.addRow('Distribució:', self.distribucio)

        self.gSimb = QGroupBox('Simbologia mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(10)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color mapa:', self.color)
        self.lSimb.addRow('Mètode classificació:', self.metode)
        self.lSimb.addRow('Nombre intervals:', self.intervals)

        self.layout.addWidget(self.gZona)
        self.layout.addWidget(self.gDades)
        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.buttons)

    def nouArxiu(self, nItem):
        self.zona.setCurrentIndex(nItem)
        self.tipus.setCurrentIndex(0)

    @pyqtSlot(str)
    def arxiuSeleccionat(self, nom):
        n = 0
        if nom != '':
            fNom = os.path.splitext(os.path.basename(nom))[0]
            nItems = self.zona.count()
            for i in range(1, nItems):
                item = self.zona.itemText(i)
                if fNom.upper().endswith('_' + item.upper()):
                    n = i
                    break
        self.nouArxiu(n)

    def msgInfo(self, txt):
        QMessageBox.information(self, 'Informació', txt)

    def msgAvis(self, txt):
        QMessageBox.warning(self, 'Avís', txt)

    def msgError(self, txt):
        QMessageBox.critical(self, 'Error', txt)

    def valida(self):
        ok = False
        if self.arxiu.filePath() == '':
            self.msgInfo("S'ha de seleccionar un arxiu de dades")
            self.arxiu.setFocus()
        elif self.zona.currentIndex() <= 0:
            self.msgInfo("S'ha de seleccionar una zona")
            self.zona.setFocus()
        elif self.capa.text().strip() == '':
            self.msgInfo("S'ha de introduir un nom de capa")
            self.capa.setFocus()
        elif self.tipus.currentIndex() <= 0:
            self.msgInfo("S'ha de seleccionar un tipus d'agregació")
            self.tipus.setFocus()
        elif self.calcul.text().strip() == '' and self.tipus.currentText() != 'Recompte':
            self.msgInfo("S'ha de introduir un cálcul per fer l'agregació")
            self.calcul.setFocus()
        else:
            ok = True
        return ok

    def mapifica(self):
        z = QvMapificacio(self.arxiu.filePath(), self.zona.currentText(), numMostra=0)
        ok, err = z.agregacio(self.llegenda, self.capa.text().strip(), self.tipus.currentText(), campAgregat=self.calcul.text().strip(),
                              filtre=self.filtre.text().strip(), tipusDistribucio=self.distribucio.currentText(),
                              modeCategories=self.metode.currentText(), numCategories=self.intervals.value(),
                              colorBase=self.color.currentText())
        if ok:
            return ''
        else: 
            return err

    @pyqtSlot()
    def ok(self):
        if self.valida():
            self.setDisabled(True)
            msg = self.mapifica()
            if msg == '':
                self.close()
            else:
                self.msgError(msg)
                self.setDisabled(False)
    
    @pyqtSlot()
    def cancel(self):
        self.close()

class QvFormSimbMapificacio(QWidget):
    def __init__(self, llegenda, capa):

        super().__init__(minimumWidth=400)
        self.llegenda = llegenda
        self.capa = capa
        if not self.iniParams():
            return

        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle('Modificar categories de mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItems(MAP_COLORS.keys())

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(MAP_METODES_MODIF.keys())
        self.metode.currentIndexChanged.connect(self.canviaMetode)

        self.nomIntervals = QLabel('Nombre intervals:', self)
        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(9)
        self.intervals.setSingleStep(1)
        self.intervals.setValue(4)
        self.intervals.setSuffix("  (depèn del mètode)")
        # self.intervals.valueChanged.connect(self.deselectValue)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)

        self.gSimb = QGroupBox('Simbologia mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(10)
        self.gSimb.setMinimumWidth(378)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color mapa:', self.color)
        self.lSimb.addRow('Mètode classificació:', self.metode)
        self.lSimb.addRow(self.nomIntervals, self.intervals)

        self.gInter = QGroupBox('Definició intervals')
        self.lInter = QGridLayout()
        self.lInter.setSpacing(10)
        self.gInter.setLayout(self.lInter)

        self.wInterval = []
        self.iniIntervals()

        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.gInter)
        self.layout.addWidget(self.buttons)

        self.valorsInicials()

    @pyqtSlot()
    def afegirFila(self):
        f = self.sender().property('Fila')
        print('afegirFila', f)

    @pyqtSlot()
    def eliminarFila(self):
        f = self.sender().property('Fila')
        print('eliminarFila', f)

    @pyqtSlot()
    def nouTall(self):
        w = self.sender()
        if w.isModified():
            f = w.property('Fila')
            ini = self.wInterval[f+1][0]
            ini.setText(w.text())
            w.setModified(False)

    def txtRang(self, num):
        v = round(num, self.numDecimals)
        if self.numDecimals == 0:
            v = int(v)
        return str(v)

    def iniIntervals(self):
        maxSizeE = 130
        maxSizeB = 27
        renderer = self.capa.renderer()
        cats = renderer.ranges()
        numCats = len(cats)
        for fila, cat in enumerate(cats):
            ini = QLineEdit(self)
            ini.setText(self.txtRang(cat.lowerValue()))
            ini.setMaximumWidth(maxSizeE)
            if fila != 0:
                ini.setDisabled(True)
            sep = QLabel('-', self)
            fin = QLineEdit(self)
            fin.setText(self.txtRang(cat.upperValue()))
            fin.setMaximumWidth(maxSizeE)
            # Ultima fila: no hay + ni -
            if fila == (numCats - 1):
                widgets = (ini, sep, fin)
            else:
                fin.setProperty('Fila', fila)
                fin.editingFinished.connect(self.nouTall)
                add = QPushButton('+', self)
                add.setMaximumSize(maxSizeB, maxSizeB)
                add.setProperty('Fila', fila)
                add.clicked.connect(self.afegirFila)
                add.setFocusPolicy(Qt.NoFocus)
                # Primera fila: solo +
                if fila == 0:
                    widgets = (ini, sep, fin, add)
                # Resto de filas: + y -
                else:
                    rem = QPushButton('-', self)
                    rem.setMaximumSize(maxSizeB, maxSizeB)
                    rem.setProperty('Fila', fila)
                    rem.clicked.connect(self.eliminarFila)
                    rem.setFocusPolicy(Qt.NoFocus)
                    widgets = (ini, sep, fin, add, rem)
            # Añadir widgets a la fila
            for col, w in enumerate(widgets):
                self.lInter.addWidget(w, fila, col)
            # Guardar widgets
            self.wInterval.append(widgets)

    def iniParams(self):
        tipus = QgsExpressionContextUtils.layerScope(self.capa).variable('qV_tipusCapa')
        if tipus != 'MAPIFICACIÓ':
            return False
        self.campCalculat, self.numDecimals, self.colorBase, self.numCategories, \
            self.modeCategories, self.format = self.llegenda.mapRenderer.paramsRender(self.capa)
        return True

    def valorsInicials(self):        
        self.color.setCurrentIndex(self.color.findText(self.colorBase))
        self.metode.setCurrentIndex(self.metode.findText(self.modeCategories))
        self.intervals.setValue(self.numCategories)
        self.canviaMetode()

    def valorsFinals(self):
        self.colorBase = self.color.currentText()
        self.modeCategories = self.metode.currentText()
        self.numCategories = self.intervals.value()
        if self.custom:
            self.rangs = []
            for fila in self.wInterval:
                self.rangs.append((fila[0].text(), fila[2].text()))

    def msgInfo(self, txt):
        QMessageBox.information(self, 'Informació', txt)

    def msgAvis(self, txt):
        QMessageBox.warning(self, 'Avís', txt)

    def msgError(self, txt):
        QMessageBox.critical(self, 'Error', txt)

    def mapifica(self):
        self.valorsFinals()
        if self.custom:
            self.renderer = self.llegenda.mapRenderer.customRender(self.capa, self.campCalculat, self.numDecimals,
                MAP_COLORS[self.colorBase], self.rangs, self.format)
        else:
            self.renderer = self.llegenda.mapRenderer.calcRender(self.capa, self.campCalculat, self.numDecimals,
                MAP_COLORS[self.colorBase], self.numCategories, MAP_METODES_MODIF[self.modeCategories], self.format)
        if self.renderer is None:
            return "No s'ha pogut modificar la simbologia"
        self.capa.setRenderer(self.renderer)
        self.capa.triggerRepaint()
        self.llegenda.modificacioProjecte('mapModified')
        return ''

    @pyqtSlot()
    def ok(self):
        self.setDisabled(True)
        msg = self.mapifica()
        if msg == '':
            self.close()
        else:
            self.msgError(msg)
            self.setDisabled(False)

    @pyqtSlot()
    def cancel(self):
        self.close()

    @pyqtSlot()
    def canviaMetode(self):
        self.custom = (self.metode.currentIndex() == QgsGraduatedSymbolRenderer.Custom)
        self.nomIntervals.setVisible(not self.custom)
        self.intervals.setVisible(not self.custom)
        self.gSimb.adjustSize()
        # if self.custom: 
        #     self.intervals.setValue(self.numCategories)
        self.gInter.setVisible(self.custom)
        self.adjustSize()

        # label = self.lParms.labelForField(self.intervals)
        # if label is not None:
        #     label.setVisible(ok)

