# -*- coding: utf-8 -*-

from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor, QValidator, QIcon, QDoubleValidator
from qgis.PyQt.QtWidgets import (QFileDialog, QWidget, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout,
                                 QComboBox, QLabel, QLineEdit, QSpinBox, QGroupBox, QGridLayout,
                                 QMessageBox, QDialogButtonBox)

from qgis.core import QgsApplication, QgsGraduatedSymbolRenderer, QgsExpressionContextUtils

from moduls.QvMapVars import *
from moduls.QvMapificacio import *

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
        self.arxiu.setDefaultRoot(RUTA_LOCAL)
        self.arxiu.setFilter('Arxius CSV (*.csv)')
        self.arxiu.setSelectedFilter('Arxius CSV (*.csv)')
        self.arxiu.lineEdit().setReadOnly(True)
        self.arxiu.fileChanged.connect(self.arxiuSeleccionat)

        self.zona = QComboBox(self)
        self.zona.setEditable(False)
        self.zona.addItem('Selecciona zona…')
        self.zona.addItems(MAP_ZONES.keys())
        # self.zona.model().item(0).setEnabled(False)

        self.capa = QLineEdit(self)
        self.capa.setMaxLength(40)

        self.tipus = QComboBox(self)
        self.tipus.setEditable(False)
        self.tipus.addItem('Selecciona tipus…')
        self.tipus.addItems(MAP_AGREGACIO.keys())

        self.distribucio = QComboBox(self)
        self.distribucio.setEditable(False)
        self.distribucio.addItems(MAP_DISTRIBUCIO.keys())

        self.calcul = QLineEdit(self)

        self.filtre = QLineEdit(self)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.color.addItems(MAP_COLORS.keys())

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(MAP_METODES.keys())

        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(MAP_MAX_CATEGORIES)
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
        z = QvMapificacio(self.arxiu.filePath(), numMostra=0)
        ok = z.agregacio(self.llegenda, self.capa.text().strip(), self.zona.currentText(), self.tipus.currentText(),
                         campAgregat=self.calcul.text().strip(), filtre=self.filtre.text().strip(),
                         tipusDistribucio=self.distribucio.currentText(), modeCategories=self.metode.currentText(),
                         numCategories=self.intervals.value(), colorBase=self.color.currentText())
        if ok:
            return ''
        else: 
            return z.msgError

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

        super().__init__()
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
        self.intervals.setMaximum(MAP_MAX_CATEGORIES)
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
        self.gSimb.setMinimumWidth(400)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color mapa:', self.color)
        self.lSimb.addRow('Mètode classificació:', self.metode)
        self.lSimb.addRow(self.nomIntervals, self.intervals)

        self.wInterval = []
        for w in self.iniIntervals():
            self.wInterval.append(w)
        self.gInter = self.grupIntervals()

        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.gInter)
        self.layout.addWidget(self.buttons)

        self.valorsInicials()

    def txtRang(self, num):
        if type(num) == str:
            return num
        v = round(num, self.numDecimals)
        if self.numDecimals == 0:
            v = int(v)
        return str(v)

    def iniFilaInterval(self, iniValor, finValor):
        maxSizeB = 27
        validator = QDoubleValidator(self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        validator.setDecimals(5)
        ini = QLineEdit(self)
        ini.setText(self.txtRang(iniValor))
        ini.setValidator(validator)
        sep = QLabel('-', self)
        fin = QLineEdit(self)
        fin.setText(self.txtRang(finValor))
        fin.setValidator(validator)
        fin.editingFinished.connect(self.nouTall)
        add = QPushButton('+', self)
        add.setMaximumSize(maxSizeB, maxSizeB)
        add.clicked.connect(self.afegirFila)
        # add.setFocusPolicy(Qt.NoFocus)
        rem = QPushButton('-', self)
        rem.setMaximumSize(maxSizeB, maxSizeB)
        rem.clicked.connect(self.eliminarFila)
        # rem.setFocusPolicy(Qt.NoFocus)
        return [ini, sep, fin, add, rem]

    def iniIntervals(self):
        for cat in self.rangsCategories:
            yield self.iniFilaInterval(cat.lowerValue(), cat.upperValue())

    def grupIntervals(self):
        group = QGroupBox('Definició intervals')
        group.setMinimumWidth(400)
        layout = QGridLayout()
        layout.setSpacing(8)
        # layout.setColumnMinimumWidth(4, 40)
        numFilas = len(self.wInterval)
        for fila, widgets in enumerate(self.wInterval):
            for col, w in enumerate(widgets):
                # Primera fila: solo +
                if fila == 0 and col > 3:
                    w.setVisible(False)
                # # Ultima fila: no hay + ni -
                elif fila == (numFilas - 1) and col > 2:
                    w.setVisible(False)
                else:
                    w.setVisible(True)
                # Valor inicial deshabilitado (menos 1a fila)
                if col == 0 and fila != 0:
                    w.setDisabled(True)
                w.setProperty('Fila', fila)
                layout.addWidget(w, fila, col)
        group.setLayout(layout)
        return group

    def actGrupIntervals(self):
        self.intervals.setValue(len(self.wInterval))

        self.setUpdatesEnabled(False)
        self.buttons.setVisible(False)
        self.gInter.setVisible(False)

        self.layout.removeWidget(self.buttons)
        self.layout.removeWidget(self.gInter)

        self.gInter.deleteLater()
        self.gInter = self.grupIntervals()

        self.layout.addWidget(self.gInter)
        self.layout.addWidget(self.buttons)

        self.gInter.setVisible(True)
        self.buttons.setVisible(True)

        self.adjustSize()
        self.setUpdatesEnabled(True)

    @pyqtSlot()
    def afegirFila(self):
        masFilas = (len(self.wInterval) < MAP_MAX_CATEGORIES)
        if masFilas:
            f = self.sender().property('Fila') + 1
            ini = self.wInterval[f][0]
            val = ini.text()
            ini.setText('')
            w = self.iniFilaInterval(val, '')
            self.wInterval.insert(f, w)
            self.actGrupIntervals()
            self.wInterval[f][2].setFocus()
        else:
            self.msgInfo("S'ha arribat al màxim d'intervals possibles")

    @pyqtSlot()
    def eliminarFila(self):
        f = self.sender().property('Fila')
        ini = self.wInterval[f][0]
        val = ini.text()
        del self.wInterval[f]
        ini = self.wInterval[f][0]
        ini.setText(val)
        self.actGrupIntervals()

    @pyqtSlot()
    def nouTall(self):
        w = self.sender()
        if w.isModified():
            f = w.property('Fila') + 1
            if f < len(self.wInterval):
                ini = self.wInterval[f][0]
                ini.setText(w.text())
            w.setModified(False)

    def iniParams(self):
        tipus = QgsExpressionContextUtils.layerScope(self.capa).variable('qV_tipusCapa')
        if tipus != 'MAPIFICACIÓ':
            return False
        self.campCalculat, self.numDecimals, self.colorBase, self.numCategories, \
            self.modeCategories, self.rangsCategories = self.llegenda.mapRenderer.paramsRender(self.capa)
        self.custom = (self.modeCategories == 'Personalitzat')
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
        try:
            if self.custom:
                self.renderer = self.llegenda.mapRenderer.customRender(self.capa, self.campCalculat, self.numDecimals,
                    MAP_COLORS[self.colorBase], self.rangs)
            else:
                self.renderer = self.llegenda.mapRenderer.calcRender(self.capa, self.campCalculat, self.numDecimals,
                    MAP_COLORS[self.colorBase], self.numCategories, MAP_METODES_MODIF[self.modeCategories])
        except Exception as e:
            return "No s'ha pogut modificar la simbologia\n ({})".format(str(e))
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
        self.custom = (self.metode.currentText() == 'Personalitzat')
        self.nomIntervals.setVisible(not self.custom)
        self.intervals.setVisible(not self.custom)
        self.gSimb.adjustSize()
        self.gInter.setVisible(self.custom)
        self.adjustSize()

