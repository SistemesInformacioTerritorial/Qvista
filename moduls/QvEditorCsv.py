from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem
from moduls.QvPushButton import QvPushButton
from moduls.QvConstants import QvConstants
import csv
import chardet
from typing import List, Tuple, Iterable
from moduls.QvImports import *


class QvEditorCsv(QDialog):
    rutaCanviada = pyqtSignal(str)
    modificat = pyqtSignal()

    def __init__(self, arxiu: str, errors: Iterable[int], codificacio: str, separador: str, parent: QWidget = None):
        super().__init__(parent)
        # self.setMinimumWidth(800)
        # self.setMinimumHeight(600)
        self.resize(800,600)
        # Declaració d'atributs de l'objecte
        self._arxiu = arxiu
        self._codificacio = codificacio
        self._errors = sorted(errors)
        self._separador = separador
        self._i = 0
        self._teErrors=len(self._errors)!=0

        # Definició gràfica
        self._lay = QVBoxLayout()
        self.setLayout(self._lay)
        # Definim el widget per moure'ns entre els errors
        if self._teErrors:
            self._layErrors = QHBoxLayout()
            self._spinErrors = QSpinBox(self)
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
        self._taula = QTableWidget()
        self._taula.currentCellChanged.connect(self._errorProper)
        self._lay.addWidget(self._taula)
        self._layBotons = QHBoxLayout()
        self._lay.addLayout(self._layBotons)
        self._defBotons()
        self._carregaTaula()
        if self._teErrors:
            self._mostraErrorActual()

    def _defBotons(self):
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
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bDesar)
        self._layBotons.addWidget(self._bCancelar)

    def _carregaTaula(self):
        self._taula.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        with open(self._arxiu, 'r', encoding=self._codificacio) as f:
            lector = csv.reader(f, delimiter=self._separador)
            for i, row in enumerate(lector):
                if i == 0:
                    self._capcalera = list(row)
                    self._taula.setColumnCount(len(self._capcalera))
                    self._taula.setHorizontalHeaderLabels(self._capcalera)
                else:
                    self._taula.setRowCount(i)
                    for j, x in enumerate(row):
                        item = QTableWidgetItem(x)
                        # if i in self._errors:
                        #     item.setBackground(QvConstants.COLORDESTACAT)
                        self._taula.setItem(i-1, j, item)
            for i in range(self._taula.rowCount()):
                item = QTableWidgetItem(str(i+1))
                if self._teErrors and i+1 in self._errors:
                    item.setBackground(QBrush(QvConstants.COLORDESTACAT))
                    item.setForeground(QBrush(QvConstants.COLORDESTACAT))
                    font=item.font()
                    font.setBold(True)
                    item.setFont(font)
                self._taula.setVerticalHeaderItem(i,item)
    def exec(self):
        self._mostraErrorActual()
        return super().exec()
    def _mostraErrorActual(self, click=False):
        if not self._teErrors: return # si no hi ha errors no farem res
        if not click: self._taula.scrollToItem(self._taula.item(self._errors[self._i]-1, 0))
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
            with open(nfile, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self._capcalera)
                files = ((self._taula.item(i, j).data(Qt.DisplayRole) for j in range(
                    self._taula.columnCount())) for i in range(self._taula.rowCount()))
                writer.writerows(files)
            if nfile!=self._arxiu:
                self.rutaCanviada.emit(nfile)
            #Assumim que si el desem és que s'ha modificat
            self.modificat.emit()
            self.close()
    def _errorProper(self,x,y):
        if self._teErrors:
            if x+1 in self._errors:
                self._setError(self._errors.index(x+1), True)
            else:
                return
                distancies=enumerate(map(lambda xx: abs(xx-x),self._errors))
                index=sorted(distancies,key=lambda x:x[1])[0][0]
                self._setError(index, True)
    def show(self):
        super().show()
        if self._teErrors:
            self._mostraErrorActual()


if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp

    gui = True

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()
        arxiu = 'U:/QUOTA/Comu_imi/Becaris/CarrecsAnsi100.csv'
        with open(arxiu, 'rb') as f:
            val = chardet.detect(f.read())
        taula = QvEditorCsv(
            arxiu, [10, 20, 30, 40, 50, 60, 70], val['encoding'], ';')
        taula.rutaCanviada.connect(print)
        #Posem el stylesheet de qVista. Així forcem a que es vegi com es veurà a qVista
        with open('style.qss') as f:
            taula.setStyleSheet(f.read())
        taula.show()
