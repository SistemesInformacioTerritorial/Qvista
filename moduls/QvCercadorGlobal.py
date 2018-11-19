from qgis.core import QgsProject

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter, QWidget, QStyleFactory, QLineEdit, QVBoxLayout
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
import sys
import csv
import collections
from qgis.core.contextmanagers import qgisapp

class QvCercadorGlobal(QWidget):

    __carrersCSV = 'moduls\DadesBCN\CARRERER.csv'
    __numerosCSV = 'moduls\DadesBCN\TAULA_DIRELE.csv'
    sHanTrobatCoordenades = pyqtSignal()

    def __init__(self):
        # Inicialitcem la classe pare
        super().__init__()

        # Instanciem, preparem i mostrem la linia d'edicó del carcador
        self.liniaCercador = QLineEdit()
        self.liniaCercador.textChanged.connect(self.textCanviat)
        self.liniaCercador.setPlaceholderText('Escriu aquí el terme de cerca')
        self.liniaCercador.show()

        # Coloquem la linia d'edició al layout del widget
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.liniaCercador)
    
    def textCanviat(self):
        print('Text canviat: {}'.format(self.liniaCercador.text()))
        

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
        completer = QCompleter(self.dictCarrers, self.leCarrer)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leCarrer.setCompleter(completer)   

    def trobatCarrer(self):
        txt = self.leCarrer.text()
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


if __name__ == "__main__":
    
    projecteInicial='../dades/../dades/projectes/BCN11_nord.qgs'
    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))
        # Canvas, projecte i bridge
        #canvas=QvCanvas()
        canvas=QgsMapCanvas()
        # canvas.xyCoordinates.connect(mocMouse)
        # canvas.show()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo
        project.read(projecteInicial)
        canvas.setGeometry(100,150,400,400)
        canvas.show()
        

 
        #layer = project.instance().mapLayersByName('BCN_Districte_ETRS89_SHP')[0]

        cercador = QvCercadorGlobal()
        cercador.setGeometry(100,100,400,20)
        cercador.show()
