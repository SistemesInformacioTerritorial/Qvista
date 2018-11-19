from qgis.core import QgsPointXY
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter
import sys
import csv
import collections

class QvCercadorJCA(QObject):

    __carrersCSV = 'moduls\DadesBCN\CARRERER.csv'
    __numerosCSV = 'moduls\DadesBCN\TAULA_DIRELE.csv'
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

    def trobatCarrer(self):
        txt = self.leCarrer.text()
        if txt != '' and txt != self.nomCarrer:
            self.iniAdreca()
            if txt in self.dictCarrers:
                self.nomCarrer = txt
                self.codiCarrer = self.dictCarrers[self.nomCarrer]
                self.completarNumero()
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
        completer = QCompleter(self.dictCarrers, self.leCarrer)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leCarrer.setCompleter(completer)   

    def completarNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        completer = QCompleter(self.dictNumerosFiltre, self.leNumero)
        completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(completer)  

    def trobatNumero(self):
        txt = self.leNumero.text()
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


from importaciones import *


def completarNumero():
    global codiCarrer

    dictNumerosFiltre = dictNumeros[codiCarrer]
    completer = QCompleter(dictNumerosFiltre, le1)
    completer.setFilterMode(QtCore.Qt.MatchStartsWith)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    le1.setCompleter(completer)  
    completer.setWidget(le1)
    print(dictNumerosFiltre)

def llegirAdrecesCSV():
    try:
        with open(carrersCSV, encoding='utf-8', newline='') as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                dictCarrers[row['NOM_OFICIAL']] = row['CODI_VIA']

        with open(numerosCSV, encoding='utf-8', newline='') as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row
        return True
    except:
        print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
        return False


def trobatCarrer():
    global carrerTrobat
    global completer
    global longi
    global segueixo
    global textTallat
    global actualCandidat
    global textPrevi
    global codiCarrer

    segueixo = False
    carrerTrobat = False
    print ('He trobat: '+actualCandidat)
    le1.setText(textPrevi+" "+actualCandidat)
    textPrevi = le1.text()
    txt = le1.text()
    longi = len(txt)

    if actualCandidat in dictCarrers:
        nomCarrer = actualCandidat
        codiCarrer = dictCarrers[nomCarrer]
        print ('codi carrer: '+codiCarrer)
        # completarNumero()

    print("Trobat: "+txt)
    # print("Trobat: "+txt, completer.currentIndex(), completer.currentRow())
    carrerTrobat = True
    segueixo = True

def textTipat():
    global longi
    global completer
    global carrerTrobat
    global segueixo
    global textTallat
    global textPrevi
    global actualCandidat

    print ("prefijo actual: "+completer.completionPrefix())

    # if carrerTrobat:
    #     # le1.setCompleter(None)
    #     # completer = QCompleter(dictCarrers, le1)
    #     # completer.setFilterMode(QtCore.Qt.MatchContains)
    #     # completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
    #     # completer.setCompletionMode(QCompleter.PopupCompletion)
    #     # completer.setWrapAround(True)
    #     # completer.setWidget(le1)
    #     # le1.setCompleter(completer) 
    #     carrerTrobat = False

    if segueixo:
        print(longi)
        posi = longi +1
        textTallat = le1.text()[posi:]
        print("Text que cerquem:"+textTallat)
        completer.setCompletionPrefix(textTallat)
        cr=QRect(QPoint(1, 1), QSize(100, 100))
        le1.completer().complete(cr)

    completer.setCompletionPrefix(le1.text()[10:])
    print ("Actual candidat:"+completer.currentCompletion())
    actualCandidat = completer.currentCompletion()
    

carrersCSV = 'moduls\DadesBCN\CARRERER.csv'
numerosCSV = 'moduls\DadesBCN\TAULA_DIRELE.csv'
dictCarrers = {}
dictNumeros = collections.defaultdict(dict)

global carrerTrobat
carrerTrobat = False

global segueixo
segueixo = False

global longi
longi = 0

global textTallat 
textTallat= ''

global completer

global textPrevi
textPrevi = ''

global actualCandidat
actualCandidat = ''

global codiCarrer
codiCarrer=''

if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        le1 = QLineEdit()
        llegirAdrecesCSV()

        # le2 = QLineEdit()

        completer = QCompleter(dictCarrers, le1)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setWrapAround(True)
        completer.setWidget(le1)

        le1.setCompleter(completer) 
        le1.textChanged.connect(textTipat)
        le1.returnPressed.connect(trobatCarrer)
        le1.show()
        # le2.show()