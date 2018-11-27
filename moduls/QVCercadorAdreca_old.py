from qgis.core import QgsPointXY
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter
import sys
import csv
import collections

class QCercadorAdreca(QObject):

    __carrersCSV = '..\dades\dadesBcn\CARRERER.csv'
    __numerosCSV = '..\dades\dadesBcn\TAULA_DIRELE.csv'
    sHanTrobatCoordenades = pyqtSignal()

    def __init__(self, lineEditCarrer, lineEditNumero, origen = 'CSV'):
        super().__init__()
        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        self.connectarLineEdits()

        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)

        self.iniAdreca()
        if self.llegirAdreces():
            self.completarCarrer()

    def iniAdreca(self):
        self.iniAdrecaCarrer()
        self.iniAdrecaNumero()

    def iniAdrecaCarrer(self):
        self.nomCarrer = ''
        self.codiCarrer = ''

    def iniAdrecaNumero(self):
        self.numeroCarrer = ''
        self.coordAdreca = None
        self.infoAdreca = None

    def connectarLineEdits(self):
        self.leCarrer.editingFinished.connect(self.trobatCarrer)
        self.leCarrer.returnPressed.connect(self.focusANumero)
        self.leCarrer.textChanged.connect(self.esborrarNumero)
        self.leNumero.editingFinished.connect(self.trobatNumero)

    def llegirAdreces(self):
        if self.origen == 'CSV':
            ok = self.llegirAdrecesCSV()
        elif self.origen == 'ORACLE':
            ok = self.llegirAdrecesOracle()
        else:
            ok = False
        return ok

    def llegirAdrecesOracle(self):
        #
        # TODO - Lectura datos de direcciones de Oracle
        #
        return False

    def llegirAdrecesCSV(self):
        try:
            with open(self.__carrersCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictCarrers[row['NOM_OFICIAL']] = row['CODI_VIA']

            with open(self.__numerosCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row
            return True
        except:
            print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
            return False

    def completarCarrer(self):
        self.completer = QCompleter(self.dictCarrers, self.leCarrer)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leCarrer.setCompleter(self.completer)   

    def completarNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        self.completer = QCompleter(self.dictNumerosFiltre, self.leNumero)
        self.completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(self.completer)  

    def trobatCarrer(self):
        print (self.completer.currentCompletion())
        # txt = self.leCarrer.text()
        txt = self.completer.currentCompletion()
        self.leCarrer.setText(txt)
        if txt != '' and txt != self.nomCarrer:
            self.iniAdreca()
            if txt in self.dictCarrers:
                self.nomCarrer = txt
                self.codiCarrer = self.dictCarrers[self.nomCarrer]
                self.completarNumero()

    def completarNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        completer = QCompleter(self.dictNumerosFiltre, self.leNumero)
        completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(completer)  

    def trobatNumero(self):
        txt = self.completer.currentCompletion()
        self.leNumero.setText(txt)
        if txt != '': # and txt != self.numeroCarrer:
            self.iniAdrecaNumero()
            if self.nomCarrer != '' and txt in self.dictNumerosFiltre:
                self.numeroCarrer = txt
                self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), \
                                            float(self.infoAdreca['ETRS89_COORD_Y']))
                self.leNumero.clearFocus()
                self.sHanTrobatCoordenades.emit()

    def focusANumero(self):
        self.leNumero.setFocus()

    def esborrarNumero(self):
        self.leNumero.clear()
        self.leNumero.setCompleter(None)

