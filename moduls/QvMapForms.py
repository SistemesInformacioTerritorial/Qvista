# -*- coding: utf-8 -*-

from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSize
from qgis.PyQt.QtGui import QColor, QValidator, QIcon, QDoubleValidator, QPixmap
from qgis.PyQt.QtWidgets import (QFileDialog, QWidget, QPushButton, QFormLayout, QVBoxLayout, QHBoxLayout, QSplitter,
                                 QComboBox, QLabel, QLineEdit, QSpinBox, QGroupBox, QFrame, QGridLayout, QDialog, QSizePolicy,
                                 QTableWidget, QTableWidgetItem, QMessageBox, QDialogButtonBox, QApplication)

from qgis.core import QgsApplication, QgsGraduatedSymbolRenderer, QgsExpressionContextUtils

from moduls.QvMapVars import *
from moduls.QvMapificacio import *
from moduls.QvSqlite import QvSqlite

import os
import sqlite3

class QvFormBaseMapificacio(QDialog):
    def __init__(self, llegenda, amplada=None, parent=None, modal=True):
        super().__init__(parent, modal=modal)
        self.llegenda = llegenda
        if amplada is not None:
            self.setMinimumWidth(amplada)
            self.setMaximumWidth(amplada)
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)

    def msgInfo(self, txt):
        QMessageBox.information(self, 'Informació', txt)

    def msgAvis(self, txt):
        QMessageBox.warning(self, 'Avís', txt)

    def msgError(self, txt):
        QMessageBox.critical(self, 'Error', txt)

    def msgSobreescriure(self, arxiu):
        if os.path.isfile(arxiu):
            res = QMessageBox.question(self, 'Atenció',
                arxiu + " ja existeix.\nVol sobreescriure aquest arxiu?")
            return res == QMessageBox.Yes
        else:
            return True

    def pause(self):
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        self.setDisabled(True)

    def play(self):
        self.setDisabled(False)
        QApplication.instance().restoreOverrideCursor()

    def comboColors(self, combo, llista=MAP_COLORS, colorBase=None, mantenirIndex=False):
        idx = -1
        if mantenirIndex:
            idx = combo.currentIndex()
        combo.clear()
        for nom, col in llista.items():
            if col is None:
                if colorBase is None:
                    col = MAP_COLORS[self.renderParams.colorBase]
                else:
                    col = colorBase
            pixmap = QPixmap(80, 45)
            pixmap.fill(col)
            icon = QIcon(pixmap)
            combo.addItem(icon, nom)
        if mantenirIndex:
            combo.setCurrentIndex(idx)

    def valida(self):
        return True

    def procesa(self):
        return ''

    @pyqtSlot()
    def accept(self):
        if self.valida():
            self.pause()
            msg = self.procesa()
            if msg == '':
                self.play()
                super().accept()
            else:
                self.play()
                self.msgError(msg)

    @pyqtSlot()
    def cancel(self):
        self.close()

class QvVerifNumero(QValidator):

    def verifCharsNumero(self, string):
        for char in string:
            if char.isdigit() or char in ('.', ',', '-'):
                pass
            else:
                return False
        return True

    def validate(self, string, index):
        txt = string.strip()
        num, ok = MAP_LOCALE.toFloat(txt)
        if ok:
            state = QValidator.Acceptable
        elif self.verifCharsNumero(txt):
            state = QValidator.Intermediate
        else:
            state = QValidator.Invalid
        return (state, string, index)

class QvComboBoxCamps(QComboBox):
    def __init__(self, parent, multiple=False):
        super().__init__(parent)
        self.multiple = multiple
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.oldText = ''
        self.newText = ''
        if self.multiple:
            self.setEditable(True)
            self.editTextChanged.connect(self.copyText)
            self.activated.connect(self.copyItem)

    def wheelEvent(self, event):
        if self.multiple:
            event.ignore()
        
    def clear(self):
        super().clear()
        self.oldText = ''
        self.newText = ''

    def setItems(self, items):
        self.addItems(items)
        self.setCurrentIndex(-1)
        self.setCurrentText('')

    @pyqtSlot(str)
    def copyText(self, txt):
        self.oldText = self.newText
        self.newText = txt

    @pyqtSlot(int)
    def copyItem(self, i):
        if i == -1:
            return
        txt = self.oldText
        self.item = self.currentText()
        lenItem = len(self.item)
        if txt.rstrip().upper().endswith(self.item.upper()):
            txt = txt.rstrip()
            txt = txt[0:len(txt)-lenItem] + self.item
        else:
            if txt != '' and txt[-1] != ' ':
                txt += ' '
            txt += self.item
        self.setCurrentText(txt)
        self.lineEdit().setSelection(len(txt) - lenItem, lenItem)

class QvVeureMostra(QTableWidget):
    def __init__(self, map):
        super().__init__(None)
        self.map = map
        self.setRowCount(self.map.numMostra)
        self.setColumnCount(len(self.map.camps))
        self.setHorizontalHeaderLabels(self.map.camps)
        for fila, reg in enumerate(self.map.mostra):
            cols = reg.split(self.map.separador)
            for col, val in enumerate(cols):
                item = QTableWidgetItem(val)
                self.setItem(fila, col, item)
        self.resizeColumnsToContents()

class QvFormMostra(QDialog):
    def __init__(self, map, amplada=800, alcada=500, parent=None, modal=False):
        super().__init__(parent, modal=modal)
        self.taula = QvVeureMostra(map)
        self.resize(amplada, alcada)
        self.setWindowTitle("Mostra de " + map.fZones)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.taula)

class QvFormNovaMapificacio(QvFormBaseMapificacio):
    def __init__(self, llegenda, amplada=500, mapificacio=None):
        super().__init__(llegenda, amplada)

        self.fCSV = mapificacio
        self.taulaMostra = None

        self.setWindowTitle('Afegir capa de mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(14)
        self.setLayout(self.layout)

        if self.fCSV is None:
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
        self.zona.currentIndexChanged.connect(self.canviaZona)

        self.capa = QLineEdit(self)
        self.capa.setMaxLength(40)

        self.tipus = QComboBox(self)
        self.tipus.setEditable(False)
        self.tipus.addItem('Selecciona tipus…')
        self.tipus.addItems(MAP_AGREGACIO.keys())

        self.distribucio = QComboBox(self)
        self.distribucio.setEditable(False)
        self.distribucio.addItem(next(iter(MAP_DISTRIBUCIO.keys())))

        self.calcul = QvComboBoxCamps(self)
        # self.filtre = QvComboBoxCamps(self)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.comboColors(self.color)

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

        self.bTaula = QPushButton('Veure arxiu')
        self.bTaula.setEnabled(False)
        self.bTaula.clicked.connect(self.veureArxiu)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)
        self.buttons.addButton(self.bTaula, QDialogButtonBox.ResetRole)

        self.gZona = QGroupBox('Definició de zona')
        self.lZona = QFormLayout()
        self.lZona.setSpacing(14)
        self.gZona.setLayout(self.lZona)

        if self.fCSV is None:
            self.lZona.addRow('Arxiu de dades:', self.arxiu)
        self.lZona.addRow('Zona:', self.zona)
        self.lZona.addRow('Nom de capa:', self.capa)

        self.gDades = QGroupBox('Agregació de dades')
        self.lDades = QFormLayout()
        self.lDades.setSpacing(14)
        self.gDades.setLayout(self.lDades)

        self.lDades.addRow("Tipus d'agregació:", self.tipus)
        self.lDades.addRow('Camp de càlcul:', self.calcul)
        # self.lDades.addRow('Filtre:', self.filtre) 
        self.lDades.addRow('Distribució:', self.distribucio)

        self.gSimb = QGroupBox('Simbologia de mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(14)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color base:', self.color)
        self.lSimb.addRow('Mètode de classificació:', self.metode)
        self.lSimb.addRow("Nombre d'intervals:", self.intervals)

        self.layout.addWidget(self.gZona)
        self.layout.addWidget(self.gDades)
        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.buttons)

        self.adjustSize()

        self.nouArxiu()

    @pyqtSlot()
    def veureArxiu(self):
        if self.taulaMostra is not None:
            self.taulaMostra.show()
            self.taulaMostra.activateWindow()

    def campsDB(self, nom):
        res = []
        if nom != '':
            fich = RUTA_DADES + MAP_ZONES_DB
            if os.path.isfile(fich):
                conn = sqlite3.connect('file:' + fich + '?mode=ro', uri=True)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('select * from ' + nom)   # nom.split('.')[0])
                row = c.fetchone()
                # res = [i[0].upper() for i in c.description]
                res = [i.upper() for i in row.keys()]
                conn.close()
        return res

    def soloPrimerItem(self, combo):
        combo.setCurrentIndex(0)
        ultimo = combo.count() - 1
        for n in range(ultimo, 0, -1):
            combo.removeItem(n)

    @pyqtSlot()
    def canviaZona(self):
        self.distribucio.setCurrentIndex(0)
        self.soloPrimerItem(self.distribucio)
        if self.zona.currentIndex() > 0:
            z = self.zona.currentText()
            campsZona = self.campsDB(MAP_ZONES[z][1])
            # Carga combo con distribuciones si el campo correspondiente está en la BBDD
            for dist, campo in MAP_DISTRIBUCIO.items():
                if campo != '' and campo in campsZona:
                    self.distribucio.addItem(dist)

    def borrarArxiu(self):
        if self.taulaMostra is not None:
            self.taulaMostra.hide()
            self.taulaMostra = None
        self.bTaula.setEnabled(False)
        self.tipus.setCurrentIndex(0)
        self.soloPrimerItem(self.zona)
        self.calcul.clear()
        # self.filtre.clear()

    def nouArxiu(self):
        if self.fCSV is None:
            return
        # Carga combo con zonas si el campo correspondiente está en el fichero CSV
        num = 0
        for zona, val in MAP_ZONES.items():
            if val[1] != '' and self.fCSV.prefixe + QvSqlite.getAlias(val[0]) in self.fCSV.camps:
                self.zona.addItem(zona)
                num = num + 1
        if num == 0:
            self.msgInfo("El fitxer " + self.fCSV.fZones + " no té cap camp de zona")
            if hasattr(self, 'arxiu'):
                self.arxiu.lineEdit().clear()
                self.arxiu.setFocus()
            return
        if num == 1:
            self.zona.setCurrentIndex(1)
            self.capa.setFocus()
        else:
            self.zona.setFocus()
        self.taulaMostra = QvFormMostra(self.fCSV, parent=self)
        self.bTaula.setEnabled(True)
        self.calcul.setItems(self.fCSV.camps)
        # self.filtre.setItems(self.fCSV.camps)

    @pyqtSlot(str)
    def arxiuSeleccionat(self, nom):
        if nom == '':
            return
        self.borrarArxiu()
        self.fCSV = QvMapificacio(nom)
        self.nouArxiu()

    def validaSortida(self, nom):
        fSalida = self.fCSV.nomArxiuSortida(self.fCSV.netejaString(nom))
        return self.msgSobreescriure(fSalida)
        
    def valida(self):
        ok = False
        if hasattr(self, 'arxiu') and self.arxiu.filePath() == '':
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
        elif self.calcul.currentText().strip() == '' and self.tipus.currentText() != 'Recompte':
            self.msgInfo("S'ha de introduir un cálcul per fer l'agregació")
            self.calcul.setFocus()
        elif self.fCSV is None:
            return self.msgInfo("No hi ha cap fitxer seleccionat")
        elif not self.validaSortida(self.capa.text().strip()):
            self.capa.setFocus()
        else:
            ok = True
        return ok

    def procesa(self):
        if self.taulaMostra is not None:
            self.taulaMostra.hide()
        ok = self.fCSV.agregacio(self.llegenda, self.capa.text().strip(), self.zona.currentText(), self.tipus.currentText(),
                                 campAgregat=self.calcul.currentText().strip(), # filtre=self.filtre.currentText().strip(),
                                 tipusDistribucio=self.distribucio.currentText(), modeCategories=self.metode.currentText(),
                                 numCategories=self.intervals.value(), colorBase=self.color.currentText())
        if ok:
            return ''
        else: 
            return self.fCSV.msgError

class QvFormSimbMapificacio(QvFormBaseMapificacio):
    def __init__(self, llegenda, capa, amplada=500):
        super().__init__(llegenda, amplada)
        self.capa = capa
        self.info = None
        if not self.iniParams():
            return

        self.setWindowTitle('Modificar mapificació')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(14)
        self.setLayout(self.layout)

        self.color = QComboBox(self)
        self.color.setEditable(False)
        self.comboColors(self.color)

        self.contorn = QComboBox(self)
        self.contorn.setEditable(False)
        self.comboColors(self.contorn, MAP_CONTORNS)

        self.color.currentIndexChanged.connect(self.canviaContorns)

        self.metode = QComboBox(self)
        self.metode.setEditable(False)
        self.metode.addItems(MAP_METODES_MODIF.keys())
        self.metode.setCurrentIndex(-1)
        self.metode.currentIndexChanged.connect(self.canviaMetode)

        self.nomIntervals = QLabel("Nombre d'intervals:", self)
        self.intervals = QSpinBox(self)
        self.intervals.setMinimum(2)
        self.intervals.setMaximum(max(MAP_MAX_CATEGORIES, self.renderParams.numCategories))
        self.intervals.setSingleStep(1)
        self.intervals.setValue(4)
        self.intervals.setSuffix("  (depèn del mètode)")
        # self.intervals.valueChanged.connect(self.deselectValue)

        self.bInfo = QPushButton('Info')
        self.bInfo.clicked.connect(self.veureInfo)

        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.cancel)
        self.buttons.addButton(self.bInfo, QDialogButtonBox.ResetRole)

        self.gSimb = QGroupBox('Simbologia de mapificació')
        self.lSimb = QFormLayout()
        self.lSimb.setSpacing(14)
        self.gSimb.setLayout(self.lSimb)

        self.lSimb.addRow('Color base:', self.color)
        self.lSimb.addRow('Color contorn:', self.contorn)
        self.lSimb.addRow('Mètode de classificació:', self.metode)
        self.lSimb.addRow(self.nomIntervals, self.intervals)

        self.wInterval = []
        for w in self.iniIntervals():
            self.wInterval.append(w)
        self.gInter = self.grupIntervals()

        self.layout.addWidget(self.gSimb)
        self.layout.addWidget(self.gInter)
        self.layout.addWidget(self.buttons)

        self.valorsInicials()

    def iniParams(self):
        self.info = QgsExpressionContextUtils.layerScope(self.capa).variable(MAP_ID)
        if self.info is None:
            return False
        # ok, (self.campCalculat, self.numDecimals, self.colorBase, self.iniColorContorn, self.numCategories, self.modeCategories,
        #     self.rangsCategories, self.sourceSymbol) = self.llegenda.mapRenderer.paramsRender(self.capa)
        self.renderParams = self.llegenda.mapRenderer.paramsRender(self.capa)
        self.custom = (self.renderParams.modeCategories == 'Personalitzat')
        if self.renderParams.msgError != '':
            self.msgInfo("No s'han pogut recuperar els paràmetres de mapificació\n" + self.renderParams.msgError)
            self.renderParams.msgError = ''
        return True

    @pyqtSlot()
    def veureInfo(self):
        if self.info is not None:
            box = QMessageBox(self)
            box.setWindowTitle('Info de mapificació')
            txt = '<table width="500">'
            params = self.info.split('\n')
            for param in params:
                linea = param.strip()
                if linea.endswith(':'):
                    linea += ' ---'
                txt += '<tr><td><nobr>&middot;&nbsp;{}</nobr></td></tr>'.format(linea)
            txt += '</table>'
            box.setTextFormat(Qt.RichText)
            box.setText("Paràmetres d'agregació de dades:")
            box.setInformativeText(txt)
            box.setIcon(QMessageBox.Information)
            box.setStandardButtons(QMessageBox.Ok)
            box.setDefaultButton(QMessageBox.Ok)
            box.exec()

    def valorsInicials(self):        
        self.color.setCurrentIndex(self.color.findText(self.renderParams.colorBase))
        self.contorn.setCurrentIndex(self.contorn.findText(self.renderParams.colorContorn))
        self.intervals.setValue(self.renderParams.numCategories)
        self.metode.setCurrentIndex(self.metode.findText(self.renderParams.modeCategories))

    def valorsFinals(self):
        self.renderParams.colorBase = self.color.currentText()
        self.renderParams.colorContorn = self.contorn.currentText()
        self.renderParams.modeCategories = self.metode.currentText()
        self.renderParams.numCategories = self.intervals.value()
        if self.custom:
            self.renderParams.rangsCategories = []
            for fila in self.wInterval:
                self.renderParams.rangsCategories.append((fila[0].text(), fila[2].text()))
            self.renderParams.numCategories = len(self.renderParams.rangsCategories)

    def txtRang(self, num):
        if type(num) == str:
            return num
        return MAP_LOCALE.toString(num, 'f', self.renderParams.numDecimals)

    def iniFilaInterval(self, iniValor, finValor):
        maxSizeB = 27
        # validator = QDoubleValidator(self)
        # validator.setLocale(MAP_LOCALE)
        # validator.setNotation(QDoubleValidator.StandardNotation)
        # validator.setDecimals(5)
        validator = QvVerifNumero(self)
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
        add.setToolTip('Afegeix nou interval')
        add.clicked.connect(self.afegirFila)
        add.setFocusPolicy(Qt.NoFocus)
        rem = QPushButton('-', self)
        rem.setMaximumSize(maxSizeB, maxSizeB)
        rem.setToolTip('Esborra interval')
        rem.clicked.connect(self.eliminarFila)
        rem.setFocusPolicy(Qt.NoFocus)
        return [ini, sep, fin, add, rem]

    def iniIntervals(self):
        for cat in self.renderParams.rangsCategories:
            yield self.iniFilaInterval(cat.lowerValue(), cat.upperValue())

    def grupIntervals(self):
        group = QGroupBox('Definició dels intervals')
        # group.setMinimumWidth(400)
        layout = QGridLayout()
        layout.setSpacing(10)
        # layout.setColumnMinimumWidth(4, 40)
        numFilas = len(self.wInterval)
        for fila, widgets in enumerate(self.wInterval):
            for col, w in enumerate(widgets):
                # Primera fila: solo +
                if fila == 0 and col > 3:
                    w.setVisible(False)
                # # Ultima fila: no hay + ni -
                elif fila > 0 and fila == (numFilas - 1) and col > 2:
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

    @pyqtSlot()
    def canviaMetode(self):
        self.custom = (self.metode.currentText() == 'Personalitzat')
        if self.custom:
            self.intervals.setValue(len(self.wInterval))
        self.intervals.setEnabled(not self.custom)
        self.gInter.setVisible(self.custom)
        self.adjustSize()
        # print('GSIMB -> Ancho:', self.gSimb.size().width(), '- Alto:', self.gSimb.size().height())
        # print('FORM -> Ancho:', self.size().width(), '- Alto:', self.size().height())

    @pyqtSlot()
    def canviaContorns(self):        
        self.comboColors(self.contorn, MAP_CONTORNS, MAP_COLORS[self.color.currentText()], True)

    def leSelectFocus(self, wLineEdit):
        lon = len(wLineEdit.text())
        if lon > 0:
            wLineEdit.setSelection(0, lon)
        wLineEdit.setFocus()

    def validaNum(self, wLineEdit):
        val = wLineEdit.validator()
        if val is None:
            return True
        res = val.validate(wLineEdit.text(), 0)
        if res[0] == QValidator.Acceptable:
            return True
        else:
            self.msgInfo("Cal introduir un nombre enter o amb decimals.\n"
                "Es farà servir la coma (,) per separar els decimals.\n"
                "I pels milers, opcionalment, el punt (.)")
            self.leSelectFocus(wLineEdit)
            return False

    def validaInterval(self, wLineEdit1, wLineEdit2):
        num1, _ = MAP_LOCALE.toFloat(wLineEdit1.text())
        num2, _ = MAP_LOCALE.toFloat(wLineEdit2.text())
        if num2 > num1:
            return True
        else:
            self.msgInfo("El segon nombre de l'interval ha de ser major que el primer")
            self.leSelectFocus(wLineEdit2)
            return False

    def validaFila(self, fila):
        wLineEdit1 = fila[0]
        wLineEdit2 = fila[2]
        if not self.validaNum(wLineEdit1):
            return False
        if not self.validaNum(wLineEdit2):
            return False
        if not self.validaInterval(wLineEdit1, wLineEdit2):
            return False
        return True

    def valida(self):
        if self.custom:
            for fila in self.wInterval:
                if not self.validaFila(fila):
                    return False
        return True

    def procesa(self):
        self.valorsFinals()
        try:
            if self.custom:
                self.renderParams.colorBase = MAP_COLORS[self.renderParams.colorBase]
                self.renderParams.colorContorn = MAP_CONTORNS[self.renderParams.colorContorn]
                self.renderer = self.llegenda.mapRenderer.customRender(self.capa, self.renderParams)
            else:
                self.renderParams.colorBase = MAP_COLORS[self.renderParams.colorBase]
                self.renderParams.colorContorn = MAP_CONTORNS[self.renderParams.colorContorn]
                self.renderParams.modeCategories = MAP_METODES_MODIF[self.renderParams.modeCategories]
                self.renderer = self.llegenda.mapRenderer.calcRender(self.capa, self.renderParams)
            if self.renderer is None:
                return "No s'ha pogut elaborar el mapa"
            err = self.llegenda.saveStyleToGeoPackage(self.capa, MAP_ID)
            if err != '':
                return "Hi ha hagut problemes al desar la simbologia\n({})".format(err)
            # self.llegenda.modificacioProjecte('mapModified')
            return ''
        except Exception as e:
            return "No s'ha pogut modificar el mapa\n({})".format(str(e))

