from moduls.QvImports import *
from PyQt5.QtWidgets import *
from typing import Type
from moduls.QvMapificacio import QvMapificacio
from moduls.QvPushButton import QvPushButton
from moduls.QvEditorCsv import QvEditorCsv

#Còpia de la funció definida dins de qVista.py. Millor aquí???
def nivellCsv(fitxer: str,delimitador: str,campX: str,campY: str, projeccio: int = 23031, nomCapa: str = 'Capa sense nom', color = 'red', symbol = 'circle'):
    uri = "file:///"+fitxer+"?type=csv&delimiter=%s&xField=%s&yField=%s" % (delimitador,campX,campY)
    layer = QgsVectorLayer(uri, nomCapa, 'delimitedtext')
    layer.setCrs(QgsCoordinateReferenceSystem(projeccio, QgsCoordinateReferenceSystem.EpsgCrsId))
    if layer is not None or layer is not NoneType:
        symbol = QgsMarkerSymbol.createSimple({'name': symbol, 'color': color})
        if layer.renderer() is not None: 
            layer.renderer().setSymbol(symbol)
        qV.project.addMapLayer(layer)
        # print("add layer")
        qV.setDirtyBit(True)
    else: print ("no s'ha pogut afegir la nova layer")

def esCoordAux(coord,rangs):
    try:
        coord=float(coord)
    except ValueError as e:
        return False
    return any(map(lambda x: coord>x[0] and coord<x[1], rangs))


def esCoordX(coord):
    rangs=((420762.,435606.),(2.0513,2.2279))
    return esCoordAux(coord,rangs)

def esCoordY(coord):
    rangs=((4574135.,4591086.),(41.3162,41.4691))
    return esCoordAux(coord,rangs)

def campsCoords(csvPath, sep, cod):
    #TODO: mirar si comencen o acaben amb X
    nomsCampsX=('X89AB','XTRETRS89A','COORDX','COORD_X', 'XUTM', 'X_UTM','XETRS89','X_ETRS89','ETRS89_X','ETRS89X','X','LONG','LONGITUD')
    # nomsCampsX=(':D')
    nomsCampsY=('Y89AB','YTRETRS89A','COORDY','COORD_Y', 'YUTM', 'Y_UTM','YETRS89','Y_ETRS89','ETRS89_Y','ETRS89Y','Y','LAT','LATITUD')
    with open(csvPath) as f:
        reader=csv.DictReader(f,delimiter=sep)

        #INTENT 1: comprovem si els camps encaixen amb els noms que tenim predefinits
        aux=list(zip(reader.fieldnames,map(lambda x: x in nomsCampsX, reader.fieldnames),map(lambda y: y in nomsCampsY, reader.fieldnames)))
        encaixenX=filter(lambda x: x[1], aux)
        encaixenY=filter(lambda x: x[2], aux)
        try:
            return next(encaixenX)[0], next(encaixenY)[0]
        except StopIteration:
            #Si un dels dos és buit, no hi haurà return. Tocarà buscar dins del seu contingut
            pass
        #INTENT 2: comprovem si hi ha algun camp que comenci o acabi per X i un altre per Y
        aux = list(zip(reader.fieldnames,map(lambda x: x.startswith('X') or x.startswith('LONG') or x.endswith('X') or x.endswith('LONG'),reader.fieldnames),map(lambda x: x.startswith('Y') or x.startswith('LAT') or x.endswith('Y') or x.endswith('LAT'),reader.fieldnames)))
        encaixenX=filter(lambda x: x[1],aux)
        encaixenY=filter(lambda x: x[2],aux)
        try:
            return next(encaixenX)[0], next(encaixenY)[0]
        except StopIteration:
            pass
        #INTENT 3: comprovem si la primera fila té camps que encaixin com a coordenades
        fila1=next(reader)
        aux=list(zip(fila1.keys(),map(esCoordX,fila1.values()),map(esCoordY,fila1.values())))
        encaixenX=filter(lambda x: x[1],aux)
        encaixenY=filter(lambda x: x[2],aux)
        try:
            return next(encaixenX)[0],next(encaixenY)[0]
        except StopIteration:
            return None, None

class QvCarregaCsv(QDialog):
    def __init__(self,rutaCsv: str, qV=None):
        super().__init__(qV)
        self.setMinimumSize(300,100)
        if qV is not None:
            self._qV=qV
        self._mapificador=QvMapificacio(rutaCsv)
        self._separador=self._mapificador.separador
        self._codificacio=self._mapificador.codi
        self._csv=rutaCsv
        self._widgetSup = QWidget(objectName='layout')
        self._layoutGran=QVBoxLayout()
        self.setLayout(self._layoutGran)
        self._layout=QVBoxLayout()
        self._layoutGran.addWidget(self._widgetSup)
        self._layoutGran.addLayout(self._layout)
        self._layoutGran.setContentsMargins(0,0,0,0)
        self._layoutGran.setSpacing(0)

        #TODO: REVISAR
        # self._finestres=[x(self) for x in (CsvPrefab,CsvTriaSeparador, CsvTriaGeom ,CsvXY, CsvAdreca, CsvGeneraCoords, CsvPersonalitza)]
        # for x in self.finestres: x.hide() #Ocultem totes les finestres que no volem mostrar
        # self.widgetActual=self.finestres[1]
        campX, campY = campsCoords(rutaCsv,self._separador, self._codificacio)
        if campX is not None and campY is not None:
            self._widgetActual = CsvCoords(self,campX,campY)
            self._widgetActual.salta.connect(self.salta)
        else:
            pass
            # self._widgetActual = CsvAdreca()
        self.formata()
        self.oldPos=self.pos()
    def formata(self):
        self._layoutGran.addWidget(self._widgetActual)
        pass
    def salta(self,nouW):
        self._widgetActual.hide()
        self._layoutGran.replaceWidget(self._widgetActual,nouW)
        self._widgetActual=nouW
        self._widgetActual.salta.connect(self.salta)

class CsvPagina(QWidget):
    salta=pyqtSignal(QWidget)
    def __init__(self,parent=None):
        super().__init__(parent)
        self._lay=QVBoxLayout(self)
        self.setLayout(self._lay)
    def _mostraTaula(self):
        #TODO: Invocar QvEditorCsv per mostrar la taula 
        wid=QvEditorCsv(self.parentWidget()._csv,[],self.parentWidget()._codificacio,self.parentWidget()._separador)
        wid.exec()
        pass
    def getCamps(self):
        with open(self.parentWidget()._csv,encoding=self.parentWidget()._codificacio) as f:
            reader=csv.DictReader(f,delimiter=self.parentWidget()._separador)
            return reader.fieldnames

class CsvCoords(CsvPagina):
    def __init__(self, parent=None, campX=None, campY=None):
        super().__init__(parent)
        #Creem una groupbox per triar els paràmetres de les coordenades
        self._gbCoords=QGroupBox(self)
        self._layCamps=QVBoxLayout(self._gbCoords)
        self._gbCoords.setLayout(self._layCamps)
        camps=self.getCamps()
        self._proj={'EPSG:25831 UTM ETRS89 31N': 25831,
                   'EPSG:3857 Pseudo Mercator (Google)': 3857,
                   'EPSG:4326 WGS 84': 4326,
                   'EPSG:23031 ED50 31N': 23031}
        self._cbX=QComboBox()
        self._cbX.addItems(camps)
        self._cbX.setCurrentText(campX)
        self._cbY=QComboBox()
        self._cbY.addItems(camps)
        self._cbY.setCurrentText(campY)
        self._cbProj=QComboBox()
        self._cbProj.addItems(self._proj.keys())
        self._layCamps.addWidget(self._cbX)
        self._layCamps.addWidget(self._cbY)
        self._layCamps.addWidget(self._cbProj)
        self._lay.addWidget(self._gbCoords)

        #Botó per anar a la pantalla de les adreces
        self._bAdreces=QvPushButton('No. Té adreces')
        self._bAdreces.clicked.connect(lambda: self.salta.emit(CsvAdreca(self.parentWidget())))
        self._lay.addWidget(self._bAdreces)

        #Botons per fer coses
        self._layBotons=QHBoxLayout()
        self._bVeure=QvPushButton('Veure')
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bAfegir=QvPushButton('Afegir')
        self._bMapifica=QvPushButton('Mapificar')
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bAfegir)
        self._layBotons.addWidget(self._bMapifica)
        self._lay.addLayout(self._layBotons)

class CsvAdreca(CsvPagina):
    def __init__(self,parent=None, **camps):
        super().__init__(parent)
        self._gbCamps=QGroupBox(self)
        self._layCamps=QGridLayout(self._gbCamps)
        self._gbCamps.setLayout(self._layCamps)
        camps=self.getCamps()
        self._cbTipusVia=QComboBox()
        self._cbTipusVia.addItems(['']+camps)
        self._cbVia=QComboBox()
        self._cbVia.addItems(camps)
        self._cbNumI=QComboBox()
        self._cbNumI.addItems(camps)
        self._cbNumF=QComboBox()
        self._cbNumF.addItems(['']+camps)
        self._cbLletraI=QComboBox()
        self._cbLletraI.addItems(['']+camps)
        self._cbLletraF=QComboBox()
        self._cbLletraF.addItems(['']+camps)
        self._layCamps.addWidget(self._cbTipusVia,0,0)
        self._layCamps.addWidget(self._cbVia,0,1)
        self._layCamps.addWidget(self._cbNumI,1,0)
        self._layCamps.addWidget(self._cbNumF,1,1)
        self._layCamps.addWidget(self._cbLletraI,2,0)
        self._layCamps.addWidget(self._cbLletraF,2,1)
        self._lay.addWidget(self._gbCamps)

        self._bCoords=QvPushButton('No. Té coordenades')
        self._bCoords.clicked.connect(lambda: self.salta.emit(CsvCoords(self.parentWidget())))
        self._lay.addWidget(self._bCoords)

        self._layBotons=QHBoxLayout()
        self._bVeure=QvPushButton('Veure')
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bGeocod=QvPushButton('Geocodificar')
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bGeocod)
        self._lay.addLayout(self._layBotons)

if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp

    gui = True

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        app = QvApp()
        arxiu = 'U:/QUOTA/Comu_imi/Becaris/gossos.csv'
        wiz=QvCarregaCsv(arxiu)
        with open('style.qss') as f:
            wiz.setStyleSheet(f.read())
        wiz.show()