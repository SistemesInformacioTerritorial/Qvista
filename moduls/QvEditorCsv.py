from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QDesktopServices
from moduls.QvPushButton import QvPushButton
from moduls.QvConstants import QvConstants
import csv
import chardet
import time
from typing import List, Tuple, Iterable
from moduls.QvImports import *
from moduls.QvFuncioFil import QvFuncioFil


class ModelCsv(QAbstractTableModel):
    ROW_BATCH_COUNT = 15

    def __init__(self):
        super().__init__()
        self.headers = []
        self.persons = []
        self.rowsLoaded = ModelCsv.ROW_BATCH_COUNT

    def setHeaders(self, headers):
        self.headers = headers

    def setErrors(self, errors):
        self.errors = errors

    def addRow(self, row):
        self.beginResetModel()
        self.persons.append(row)
        self.endResetModel()

    def setArxiu(self, arxiu, cod, sep):
        # self.func=QvFuncioFil(lambda: self._setArxiu(arxiu, cod, sep))
        # self.func.start()
        # time.sleep(5)
        self._setArxiu(arxiu, cod, sep)

    def _setArxiu(self, arxiu, cod, sep):
        with open(arxiu, 'r', encoding=cod) as f:
            lector = csv.reader(f, delimiter=sep)
            f0 = next(lector)
            self._capcalera = list(f0)
            self.setHeaders(self._capcalera)
            self.addRows(lector)

    def addRows(self, rows):
        self.persons.extend(list(rows))

    def rowCount(self, index=QModelIndex()):
        if not self.persons:
            return 0

        if len(self.persons) <= self.rowsLoaded:
            return len(self.persons)
        else:
            return self.rowsLoaded

    def canFetchMore(self, index=QModelIndex()):
        if len(self.persons) > self.rowsLoaded:
            return True
        else:
            return False

    def fetchMore(self, index=QModelIndex()):
        reminder = len(self.persons) - self.rowsLoaded
        itemsToFetch = min(reminder, ModelCsv.ROW_BATCH_COUNT)
        self.beginInsertRows(QModelIndex(), self.rowsLoaded,
                             self.rowsLoaded+itemsToFetch-1)
        self.rowsLoaded += itemsToFetch
        self.endInsertRows()

    # def addPerson(self,person):
    #     self.beginResetModel()
    #     self.persons.append(person)
    #     self.endResetModel()
    def estaCarregat(self, fila):
        return fila <= self.rowsLoaded

    def columnCount(self, index=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        col = index.column()
        person = self.persons[index.row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col < len(person):
                return QVariant(person[col])
            return QVariant()
        if role == Qt.BackgroundRole:
            return QBrush(QvConstants.COLORDESTACAT) if index.row()+1 in self.errors else QBrush(QvConstants.COLORBLANC)

    def setData(self, index, value, role):
        if index.isValid and role == Qt.EditRole:
            self.persons[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return super().flags(index) | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return QVariant(self.headers[section])
        return QVariant(int(section + 1))

    def desar(self, arxiu):
        with open(arxiu, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self._capcalera)
            writer.writerows(self.persons)


class QvEditorCsv(QDialog):
    rutaCanviada = pyqtSignal(str)
    modificat = pyqtSignal()

    def __init__(self, arxiu: str, errors: Iterable[int], codificacio: str, separador: str, parent: QWidget = None):
        super().__init__(parent, Qt.WindowSystemMenuHint |
                         Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.resize(800, 600)
        # Declaració d'atributs de l'objecte
        self._arxiu = arxiu
        self._codificacio = codificacio
        self._errors = sorted(errors)
        self._separador = separador
        self._i = 0
        self._teErrors = len(self._errors) != 0

        # Definició gràfica
        self._lay = QVBoxLayout()
        self.setLayout(self._lay)
        # Definim el widget per moure'ns entre els errors
        if self._teErrors:
            self._layErrors = QHBoxLayout()
            self._spinErrors = QSpinBox(self)
            self._spinErrors.setStyleSheet('border: 1px solid #38474F')
            self._spinErrors.setPrefix('Error ')
            self._spinErrors.setSuffix(' de %i' % len(self._errors))
            self._spinErrors.setRange(1, len(self._errors))
            self._spinErrors.setEnabled(False)
            # self._spinErrors.valueChanged.connect(lambda x: self._setError(x-1))
            self._spinErrors.lineEdit().setReadOnly(True)
            # No volem permetre seleccionar el lineedit
            self._spinErrors.lineEdit().selectionChanged.connect(
                lambda: self._spinErrors.lineEdit().setSelection(0, 0))
            # self._layErrors.addWidget(self._spinErrors)
            # self._layErrors.addStretch()
            self._lay.addLayout(self._layErrors)
        # Declarem la taula
        self._taula = QTableView()
        self._lay.addWidget(self._taula)

        self._layBotons = QHBoxLayout()
        self._lay.addLayout(self._layBotons)
        self._defBotons()
        self._carregaTaula()
        if self._teErrors:
            self._mostraErrorActual()

    def _defBotons(self):
        self._bFullCalcul = QvPushButton('Obre com a full de càlcul', discret=True)
        self._bFullCalcul.clicked.connect(self._obreFullCalcul)
        self._bDesar = QvPushButton('Desar', destacat=True)
        self._bDesar.clicked.connect(self._desar)
        self._bCancelar = QvPushButton('Cancel·lar')
        self._bCancelar.clicked.connect(self.close)
        if self._teErrors:
            self._bAnt = QvPushButton('Error anterior')
            self._bAnt.clicked.connect(self._errorAnt)
            self._bSeg = QvPushButton('Error següent')
            self._bSeg.clicked.connect(self._errorSeg)
            self._layErrors.addStretch()
            self._layErrors.addWidget(self._bAnt)
            self._layErrors.addWidget(self._spinErrors)
            self._layErrors.addWidget(self._bSeg)
            self._layErrors.addStretch()
        self._layBotons.addWidget(self._bFullCalcul)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bDesar)
        self._layBotons.addWidget(self._bCancelar)

    def _obreFullCalcul(self):
        QDesktopServices.openUrl(QUrl(self._arxiu))
        self.close()

    def _carregaTaula(self):
        self._taula.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._model = ModelCsv()
        self._model.setErrors(self._errors)
        self._model.setArxiu(self._arxiu, self._codificacio, self._separador)
        self._taula.setModel(self._model)
        self._taula.resizeColumnsToContents()

    def _mostraErrorActual(self, click=False):
        if not self._teErrors:
            return  # si no hi ha errors no farem res
        if not click:
            fila = self._errors[self._i]-1
            while not self._model.estaCarregat(fila):
                self._model.fetchMore()
            index = self._model.index(fila, 0)
            self._taula.scrollTo(index)
            # encara que ho sembli, no, no és repetitiu. Cal fer-ho dues vegades
            self._taula.scrollTo(index)
        self._spinErrors.setValue(self._i+1)

    def _setError(self, i, click=False):
        if i < 0:
            self._i = 0
        elif i >= len(self._errors):
            self._i = len(self._errors)-1
        else:
            self._i = i
        self._mostraErrorActual(click)

    def _errorAnt(self):
        self._setError(self._i-1)

    def _errorSeg(self):
        self._setError(self._i+1)

    def _desar(self):
        nfile, _ = QFileDialog.getSaveFileName(
            None, "Desar taula", self._arxiu, "Arxius csv (*.csv)")
        if nfile != '':
            self._model.desar(nfile)
            if nfile != self._arxiu:
                self.rutaCanviada.emit(nfile)
            # Assumim que si el desem és que s'ha modificat
            self.modificat.emit()
            self.close()

    def _errorProper(self, x, y):
        if self._teErrors:
            if x+1 in self._errors:
                self._setError(self._errors.index(x+1), True)
            else:
                return
                distancies = enumerate(map(lambda xx: abs(xx-x), self._errors))
                index = sorted(distancies, key=lambda x: x[1])[0][0]
                self._setError(index, True)

    def showEvent(self, e):
        super().showEvent(e)
        if self._teErrors:
            self._mostraErrorActual()


if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp

    gui = True

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()
        arxiu = 'C:/Users/omarti/Documents/Random/CarrecsUTF8.csv'
        with open(arxiu, 'rb') as f:
            val = chardet.detect(b''.join(f.readlines(5000)))
        taula = QvEditorCsv(
            arxiu, [10, 20, 30, 40, 50, 60, 70, 1000, 10000, 100000, 1000000], val['encoding'], ';')
        taula.rutaCanviada.connect(print)
        # Posem el stylesheet de qVista. Així forcem a que es vegi com es veurà a qVista
        with open('style.qss') as f:
            taula.setStyleSheet(f.read())
        taula.show()
