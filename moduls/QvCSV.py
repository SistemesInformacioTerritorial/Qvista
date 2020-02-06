from moduls.QvImports import *
from PyQt5.QtWidgets import *
from typing import Type
from moduls.QvMapificacio import QvMapificacio
from moduls.QvPushButton import QvPushButton
from moduls.QvEditorCsv import QvEditorCsv
from moduls.QvMapForms import QvFormNovaMapificacio
from moduls.QvConstants import QvConstants
from moduls.QvApp import QvApp
from moduls.QvFuncioFil import QvFuncioFil

# Còpia de la funció definida dins de qVista.py. Millor aquí???


def nivellCsv(qV, fitxer: str, delimitador: str, campX: str, campY: str, projeccio: int = 23031, nomCapa: str = 'Capa sense nom', color='red', symbol='circle'):
    uri = "file:///"+fitxer + \
        "?type=csv&delimiter=%s&xField=%s&yField=%s" % (
            delimitador, campX, campY)
    layer = QgsVectorLayer(uri, nomCapa, 'delimitedtext')
    layer.setCrs(QgsCoordinateReferenceSystem(
        projeccio, QgsCoordinateReferenceSystem.EpsgCrsId))
    if layer is not None or layer is not NoneType:
        symbol = QgsMarkerSymbol.createSimple({'name': symbol, 'color': color})
        if layer.renderer() is not None:
            layer.renderer().setSymbol(symbol)
        qV.project.addMapLayer(layer)
        # print("add layer")
        qV.setDirtyBit(True)
    else:
        print("no s'ha pogut afegir la nova layer")


def esCoordAux(coord, rangs):
    try:
        coord = float(coord)
    except ValueError as e:
        return False
    return any(map(lambda x: coord > x[0] and coord < x[1], rangs))


def esCoordX(coord):
    rangs = ((420762., 435606.), (2.0513, 2.2279))
    return esCoordAux(coord, rangs)


def esCoordY(coord):
    rangs = ((4574135., 4591086.), (41.3162, 41.4691))
    return esCoordAux(coord, rangs)


def campsCoords(csvPath, sep, cod):
    # TODO: mirar si comencen o acaben amb X
    nomsCampsX = ('X89AB', 'XTRETRS89A', 'COORDX', 'COORD_X', 'XUTM', 'X_UTM',
                  'XETRS89', 'X_ETRS89', 'ETRS89_X', 'ETRS89X', 'X', 'LONG', 'LONGITUD')
    # nomsCampsX=(':D')
    nomsCampsY = ('Y89AB', 'YTRETRS89A', 'COORDY', 'COORD_Y', 'YUTM', 'Y_UTM',
                  'YETRS89', 'Y_ETRS89', 'ETRS89_Y', 'ETRS89Y', 'Y', 'LAT', 'LATITUD')
    with open(csvPath) as f:
        reader = csv.DictReader(f, delimiter=sep)

        # INTENT 1: comprovem si els camps encaixen amb els noms que tenim predefinits
        aux = list(zip(reader.fieldnames, map(lambda x: x in nomsCampsX, reader.fieldnames), map(
            lambda y: y in nomsCampsY, reader.fieldnames)))
        encaixenX = filter(lambda x: x[1], aux)
        encaixenY = filter(lambda x: x[2], aux)
        try:
            return next(encaixenX)[0], next(encaixenY)[0]
        except StopIteration:
            # Si un dels dos és buit, no hi haurà return. Tocarà buscar dins del seu contingut
            pass
        # INTENT 2: comprovem si hi ha algun camp que comenci o acabi per X i un altre per Y
        aux = list(zip(reader.fieldnames, map(lambda x: x.startswith('X') or x.startswith('LONG') or x.endswith('X') or x.endswith(
            'LONG'), reader.fieldnames), map(lambda x: x.startswith('Y') or x.startswith('LAT') or x.endswith('Y') or x.endswith('LAT'), reader.fieldnames)))
        encaixenX = filter(lambda x: x[1], aux)
        encaixenY = filter(lambda x: x[2], aux)
        try:
            return next(encaixenX)[0], next(encaixenY)[0]
        except StopIteration:
            pass
        # INTENT 3: comprovem si la primera fila té camps que encaixin com a coordenades
        fila1 = next(reader)
        aux = list(zip(fila1.keys(), map(esCoordX, fila1.values()),
                       map(esCoordY, fila1.values())))
        encaixenX = filter(lambda x: x[1], aux)
        encaixenY = filter(lambda x: x[2], aux)
        try:
            return next(encaixenX)[0], next(encaixenY)[0]
        except StopIteration:
            return None, None

def campsPref(csvPath,sep,cod,nomCamps):
    with open(csvPath) as f:
        reader=csv.DictReader(f,delimiter=sep)
        comencen=filter(lambda x: any(map(lambda y: x.lower().startswith(y),nomCamps)),reader.fieldnames)
        try:
            return next(comencen)
        except StopIteration:
            return None

def campsAdreces(csvPath,sep,cod):
    nomCamps = ('nom','via','carr')
    return campsPref(csvPath,sep,cod,nomCamps)
def campsNum(csvPath,sep,cod):
    nomCamps = ('num','npost','n_post','n post','núm')
    return campsPref(csvPath,sep,cod,nomCamps)

class QvCarregaCsv(QDialog):
    def __init__(self, rutaCsv: str, qV=None):
        super().__init__(qV,Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle('Carregador d\'arxius CSV')
        self.setFixedSize(QvApp().zoomFactor()*700, QvApp().zoomFactor()*450)
        if qV is not None:
            self._qV = qV
        self._csv = rutaCsv
        self.loadMap()
        # self._mapificador = QvMapificacio(rutaCsv)
        self.setSeparador()
        self._codificacio = self._mapificador.codi
        self._widgetSup = QWidget(objectName='layout')
        self._layoutGran = QVBoxLayout()
        self.setLayout(self._layoutGran)
        self._layout = QVBoxLayout()
        self._layoutGran.addWidget(self._widgetSup)
        self._layoutGran.addLayout(self._layout)
        self._layoutGran.setContentsMargins(0, 0, 0, 0)
        self._layoutGran.setSpacing(0)
        self.triaPrimeraPantalla()
        #TODO: REVISAR
        # self._finestres=[x(self) for x in (CsvPrefab,CsvTriaSeparador, CsvTriaGeom ,CsvXY, CsvAdreca, CsvGeneraCoords, CsvPersonalitza)]
        # for x in self.finestres: x.hide() #Ocultem totes les finestres que no volem mostrar
        # self.widgetActual=self.finestres[1]

        self.formata()
        self.oldPos = self.pos()
    def loadMap(self):
        self._mapificador = QvMapificacio(self._csv)
    def setSeparador(self):
        self._separador = self._mapificador.separador
    def getPrimeraPantalla(self):
        campX, campY = campsCoords(
            self._csv, self._separador, self._codificacio)
        if campX is not None and campY is not None:
            return CsvCoords(self, campX, campY)
        else:
            return CsvAdreca(self)

    def triaPrimeraPantalla(self):
        self._widgetActual=self.getPrimeraPantalla()
        self._widgetActual.salta.connect(self.salta)

    def formata(self):
        self._layoutGran.addWidget(self._widgetActual)
        pass

    def salta(self, nouW):
        self._widgetActual.hide()
        self._layoutGran.replaceWidget(self._widgetActual, nouW)
        self._widgetActual = nouW
        self._widgetActual.salta.connect(self.salta)

    def setCsv(self, csv):
        self._csv = csv


class CsvPagina(QWidget):
    salta = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lay = QVBoxLayout(self)
        self.setLayout(self._lay)
        self._lblTitol = QLabel()  # falta posar-li l'estil i tal
        self._lblTitol.setFont(QvConstants.FONTTITOLS)
        self._lay.addWidget(self._lblTitol)

    def _mostraTaula(self, errors=[]):
        # La senyal clicked dels botons passa un booleà que indica si està checked o no
        # Si ens demana veure-ho des d'un botó directament, vol dir que no hi ha errors. Per tant, ignorem el booleà
        if isinstance(errors, bool):
            errors = []
        # TODO: Invocar QvEditorCsv per mostrar la taula
        print(self.parentWidget()._csv)
        wid = QvEditorCsv(self.parentWidget()._csv, errors, self.parentWidget(
        )._codificacio, self.parentWidget()._separador)
        wid.setWindowTitle("Vista prèvia de l'arxiu csv")
        self._canviat = False
        wid.rutaCanviada.connect(self.parentWidget().setCsv)

        def setCanviat():  # Una lambda no pot tenir assignacions :(
            self._canviat = True
        wid.modificat.connect(setCanviat)
        wid.exec()
        return self._canviat
        pass

    def getCamps(self):
        with open(self.parentWidget()._csv, encoding=self.parentWidget()._codificacio) as f:
            reader = csv.DictReader(
                f, delimiter=self.parentWidget()._separador)
            return reader.fieldnames

    def _setTitol(self, titol):
        self._lblTitol.setText(titol)

    def _mapifica(self):
        fMap = QvFormNovaMapificacio(
            self.parentWidget()._qV.llegenda, mapificacio=self.parentWidget()._mapificador)
        fMap.exec()
        self.parentWidget().close()


class CsvCoords(CsvPagina):
    def __init__(self, parent=None, campX=None, campY=None):
        super().__init__(parent)
        self._setTitol('Sel·leccioneu dels camps de coordenades')
        self._lay.addWidget(
            QLabel("Introduiu els camps que defineixen les coordenades"))
        self._lay.addStretch()
        # Creem una groupbox per triar els paràmetres de les coordenades
        self._gbCoords = QGroupBox(self)
        self._layCamps = QVBoxLayout(self._gbCoords)
        self._gbCoords.setLayout(self._layCamps)
        camps = self.getCamps()
        if campX is None:
            campX, campY = campsCoords(self.parentWidget()._csv, self.parentWidget()._separador, self.parentWidget()._codificacio)
        self._proj = {'EPSG:25831 UTM ETRS89 31N': 25831,
                      'EPSG:3857 Pseudo Mercator (Google)': 3857,
                      'EPSG:4326 WGS 84': 4326,
                      'EPSG:23031 ED50 31N': 23031}
        layX = QHBoxLayout()
        lblX = QLabel('Coordenades X:')
        lblX.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layX.addWidget(lblX)
        self._cbX = QComboBox()
        self._cbX.addItems(camps)
        self._cbX.setCurrentText(campX)
        layX.addWidget(self._cbX)

        layY = QHBoxLayout()
        lblY = QLabel('Coordenades Y:')
        lblY.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layY.addWidget(lblY)
        self._cbY = QComboBox()
        self._cbY.addItems(camps)
        self._cbY.setCurrentText(campY)
        layY.addWidget(self._cbY)

        layProj = QHBoxLayout()
        lblProj = QLabel('Projecció:')
        lblProj.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layProj.addWidget(lblProj)
        self._cbProj = QComboBox()
        self._cbProj.addItems(self._proj.keys())
        layProj.addWidget(self._cbProj)

        self._layCamps.addLayout(layX)
        self._layCamps.addLayout(layY)
        self._layCamps.addLayout(layProj)
        self._lay.addWidget(self._gbCoords)

        # Botó per anar a la pantalla de les adreces
        self._bAdreces = QvPushButton("Hi ha camps d'adreces?")
        self._bAdreces.setToolTip("Si no disposeu de camps de coordenades, premeu aquí per geocodificar-les a partir d'adreces")
        self._bAdreces.clicked.connect(
            lambda: self.salta.emit(CsvAdreca(self.parentWidget())))
        self._lay.addWidget(self._bAdreces)
        self._lay.addStretch()

        # Botons per fer coses
        self._layBotons = QHBoxLayout()
        self._bVeure = QvPushButton("Vista prèvia de l'arxiu csv")
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bAfegir = QvPushButton('Afegir com a capa de punts')
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(self.afegir)
        self._bMapifica = QvPushButton('Mapificar')
        self._bMapifica.setToolTip('Crea una mapificació a partir de la taula per visualitzar-la sobre el mapa')
        self._bMapifica.clicked.connect(self._mapifica)
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bAfegir)
        self._layBotons.addWidget(self._bMapifica)
        self._lay.addLayout(self._layBotons)

    def afegir(self):
        self.salta.emit(CsvAfegir(self._cbX.currentText(), self._cbY.currentText(
        ), self._proj[self._cbProj.currentText()], self.parentWidget()))


class CsvAdreca(CsvPagina):
    def __init__(self, parent=None, **camps):
        super().__init__(parent)
        self._setTitol("Sel·leccioneu els camps d'adreça")
        self._lay.addWidget(QLabel(
            "Trieu els camps que defineixen l'adreça.\nNomés són obligatoris el nom de la via i el número inicial"))
        self._lay.addStretch()
        self._gbCamps = QGroupBox(self)
        self._layCamps = QGridLayout(self._gbCamps)
        self._gbCamps.setLayout(self._layCamps)
        camps = self.getCamps()
        self._cbTipusVia = QComboBox()
        self._cbTipusVia.addItems(['']+camps)
        layTipusVia = QHBoxLayout()
        lblTipusVia = QLabel('Tipus via (carrer, avinguda...):')
        lblTipusVia.setAlignment(Qt.AlignRight | Qt.AlignVCenter) #Cal alinear a la dreta i al centre, ja que si no, queda mal alineat respecte la combobox
        layTipusVia.addWidget(lblTipusVia)
        layTipusVia.addWidget(self._cbTipusVia)

        self._cbVia = QComboBox()
        self._cbVia.addItems(camps)
        layVia = QHBoxLayout()
        lblVia = QLabel('Via:')
        lblVia.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layVia.addWidget(lblVia)
        layVia.addWidget(self._cbVia)
        c=campsAdreces(self.parentWidget()._csv,self.parentWidget()._separador, self.parentWidget()._codificacio)
        if c is not None:
            i=self._cbVia.findText(c)
            self._cbVia.setCurrentIndex(i)

        self._cbNumI = QComboBox()
        self._cbNumI.addItems(camps)
        layNumI = QHBoxLayout()
        lblNumI = QLabel('Número postal inicial:')
        lblNumI.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layNumI.addWidget(lblNumI)
        layNumI.addWidget(self._cbNumI)
        c=campsNum(self.parentWidget()._csv,self.parentWidget()._separador, self.parentWidget()._codificacio)
        if c is not None:
            i=self._cbNumI.findText(c)
            self._cbNumI.setCurrentIndex(i)

        self._cbNumF = QComboBox()
        self._cbNumF.addItems(['']+camps)
        layNumF = QHBoxLayout()
        lblNumF = QLabel('Número postal final:')
        lblNumF.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layNumF.addWidget(lblNumF)
        layNumF.addWidget(self._cbNumF)

        self._cbLletraI = QComboBox()
        self._cbLletraI.addItems(['']+camps)
        layLletraI = QHBoxLayout()
        lblLletraI = QLabel('Lletra inicial:')
        lblLletraI.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layLletraI.addWidget(lblLletraI)
        layLletraI.addWidget(self._cbLletraI)

        self._cbLletraF = QComboBox()
        self._cbLletraF.addItems(['']+camps)
        layLletraF = QHBoxLayout()
        lblLletraF = QLabel('Lletra final:')
        lblLletraF.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layLletraF.addWidget(lblLletraF)
        layLletraF.addWidget(self._cbLletraF)
        self._layCamps.addLayout(layTipusVia, 0, 0)
        self._layCamps.addLayout(layVia, 0, 1)
        self._layCamps.addLayout(layNumI, 1, 0)
        self._layCamps.addLayout(layNumF, 1, 1)
        self._layCamps.addLayout(layLletraI, 2, 0)
        self._layCamps.addLayout(layLletraF, 2, 1)
        self._lay.addWidget(self._gbCamps)

        self._bCoords = QvPushButton('Hi ha camps de coordenades?')
        self._bCoords.setToolTip('Si ja es disposa de camps de coordenades, premeu aquí per carregar-les directament')
        self._bCoords.clicked.connect(
            lambda: self.salta.emit(CsvCoords(self.parentWidget())))
        self._lay.addWidget(self._bCoords)
        self._lay.addStretch()

        self._layBotons = QHBoxLayout()
        self._bVeure = QvPushButton("Vista prèvia de l'arxiu csv")
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bGeocod = QvPushButton('Geocodificar')
        self._bGeocod.setToolTip("Obté les coordenades a partir d'adreces postals")
        self._bGeocod.clicked.connect(self.geocodifica)
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bGeocod)
        self._lay.addLayout(self._layBotons)

    def geocodifica(self):
        self.salta.emit(CsvGeocod([x.currentText() for x in (self._cbTipusVia, self._cbVia,
                                                             self._cbNumI, self._cbLletraI, self._cbNumF, self._cbLletraF)], self.parentWidget()))


class CsvGeocod(CsvPagina):
    def __init__(self, campsAdreca, parent=None):
        super().__init__(parent)
        self._setTitol('Geocodificació')
        # self._lay.addWidget(QLabel('GEOCODIFICACIÓ'))
        self._lblNumErrors = QLabel("Número d'errors: 0")
        self._lay.addWidget(self._lblNumErrors)
        self._numErr = 0
        self._errors = []
        self._modificaLblErr()
        self._progress = QProgressBar()
        self._progress.setMaximum(100)
        self._lay.addWidget(self._progress)
        self._lay.addStretch()
        self._lblExplicativa=QLabel('Aquest procés pot trigar uns minuts. Espereu, si us plau...')
        self._lblExplicativa.setAlignment(Qt.AlignCenter)
        self._lay.addWidget(self._lblExplicativa)
        self._lay.addStretch()
        self._lblExplicativa.hide()
        self._lay.addStretch()
        layH=QHBoxLayout()
        self._bCancelar=QvPushButton('Cancel·lar')
        self._bCancelar.clicked.connect(self.cancela)
        layH.addWidget(self._bCancelar)
        self._lay.addLayout(layH)
        self._camps = campsAdreca
        self._cancelat=False

    def cancela(self):
        self.parentWidget()._mapificador.cancelProces()
        

    def showEvent(self, e):
        super().showEvent(e)
        # Falta mirar què fem amb els errors
        self.setCursor(QvConstants.CURSOROCUPAT)
        if self.parentWidget()._mapificador.files>50000:
            self._lblExplicativa.show()
        # if self._cancelat:
        #     self.parentWidget().loadMap()
        fil=QvFuncioFil(lambda: self.parentWidget()._mapificador.geocodificacio(self._camps, ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica",
                                                                      "Secció censal"), percentatgeProces=self._canviPercentatge, procesAcabat=self.acabat))
        fil.start()
        # self.parentWidget()._mapificador.geocodificacio(self._camps, ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica",
        #                                                               "Secció censal"), percentatgeProces=self._canviPercentatge, procesAcabat=self.acabat)
        qApp.processEvents()
    def _canviPercentatge(self,p):
        self._progress.setValue(p)
        # qApp.processEvents()
    def _unErrorMes(self, err):
        self._errors.append(err)
        self._numErr += 1
        self._modificaLblErr()

    def _modificaLblErr(self):
        self._lblNumErrors.setText("Número d'errors: %i" % self._numErr)
        # qApp.processEvents()

    def acabat(self, n):
        if self.parentWidget()._mapificador.cancel:
            self.salta.emit(self.parentWidget().getPrimeraPantalla())
        else:
            # Aquí saltar al resultat
            self.parentWidget().setCsv(self.parentWidget()._mapificador.fZones)
            # self.parentWidget()._csv=self.parentWidget()._mapificador.fDades
            self.salta.emit(CsvGeocodificat(self._errors, self.parentWidget()))
            print(n)
        pass


class CsvGeocodificat(CsvPagina):
    def __init__(self, errors, parent=None):
        super().__init__(parent)
        self._setTitol('Geocodificat')
        self._errors = [x['_fila'] for x in errors]
        self._textEditErrors = QTextEdit()
        self._lay.addWidget(self._textEditErrors)
        self._definirErrors(self._errors)
        self._layBotons = QHBoxLayout()
        # Definició de la botonera
        self._bEnrere= QvPushButton('Enrere')
        self._bEnrere.clicked.connect(self._enrere)
        self._bVeure = QvPushButton("Vista prèvia de l'arxiu csv")
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bAfegir = QvPushButton('Afegir com a capa de punts')
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(lambda: self.salta.emit(CsvAfegir(
            'QVISTA_ETRS89_COORD_X', 'QVISTA_ETRS89_COORD_Y', 25831, self.parentWidget())))
        # self._bAfegir.clicked.connect()
        self._bMapifica = QvPushButton('Mapificar')
        self._bMapifica.setToolTip('Crea una mapificació a partir de la taula per visualitzar-la sobre el mapa')
        self._bMapifica.clicked.connect(self._mapifica)
        # self._bMapifica.clicked.connect()
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addWidget(self._bEnrere)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bAfegir)
        self._layBotons.addWidget(self._bMapifica)
        self._lay.addLayout(self._layBotons)
    def _enrere(self):
        self.salta.emit(self.parentWidget().getPrimeraPantalla())
        
    def _definirErrors(self, errors):
        errorsStr = ''
        for x in errors:
            errorsStr = errorsStr+'\nFila %i' % x
        self._textEditErrors.setText(
            'Files amb errors (click sobre "Veure" per veure i editar la taula):%s' % errorsStr)
        pass

    def _mostraTaula(self):
        if super()._mostraTaula(self._errors):
            # Si retorna true vol dir que hem fet algun canvi
            self.parentWidget()._mapificador = QvMapificacio(self.parentWidget()._csv)
            self.parentWidget().setSeparador()
            self.salta.emit(CsvAdreca(self.parentWidget()))


class CsvAfegir(CsvPagina):
    def __init__(self, campCoordX, campCoordY, projeccio, parent=None):
        super().__init__(parent)
        self._setTitol('Afegir com a capa de punts')
        self._campCoordX = campCoordX
        self._campCoordY = campCoordY
        self._projeccio = projeccio
        # Nom de la capa
        layNom = QHBoxLayout()
        layNom.addWidget(QLabel('Nom de la capa: '))
        self._leNomCapa = QLineEdit()
        self._leNomCapa.setText(Path(self.parentWidget()._csv).stem)
        layNom.addWidget(self._leNomCapa)
        self._lay.addLayout(layNom)
        # Color de la representació
        self._color = 'red'
        layColor = QHBoxLayout()
        layColor.addWidget(QLabel('Color: '))

        def setColorBoto():
            self._bColor.setStyleSheet(
                'color: %s; background-color: %s' % (self._color, self._color))

        def obrirDialegColor():
            color = QColorDialog.getColor(
                QColor(self._color), self, 'Tria del color de la representació')
            self._color = color.name()
            setColorBoto()

        self._bColor = QvPushButton(flat=True)
        self._bColor.setIcon(QIcon('Imatges/da_color.png'))
        self._bColor.setStyleSheet('background: solid %s; border: none'%self._color)
        self._bColor.setIconSize(QSize(25,25))
        self._bColor.setFixedSize(25,25)
        QvConstants.afegeixOmbraWidget(self._bColor)
        self._bColor.clicked.connect(obrirDialegColor)
        layColor.addWidget(self._bColor)
        layColor.addStretch()
        setColorBoto()
        self._lay.addLayout(layColor)
        self._lay.addStretch()
        # Forma

        def setForma(imatge):
            self._forma = imatge
        gbForma = QGroupBox()
        self._lay.addWidget(gbForma)
        layForma = QGridLayout()
        gbForma.setLayout(layForma)
        rbCreu = QRadioButton()
        rbCreu.setIcon(QIcon(imatgesDir+'crossW.png'))
        rbCreu.toggled.connect(lambda x: setForma(
            'cross') if x else print(':D'))
        layForma.addWidget(rbCreu, 1, 2)

        rbQuadrat = QRadioButton()
        rbQuadrat.setIcon(QIcon(imatgesDir+'squareW.png'))
        rbQuadrat.toggled.connect(lambda x: setForma(
            'square') if x else print(':D'))
        layForma.addWidget(rbQuadrat, 0, 1)

        rbRombe = QRadioButton()
        rbRombe.setIcon(QIcon(imatgesDir+'rhombusW.png'))
        rbRombe.toggled.connect(lambda x: setForma(
            'diamond') if x else print(':D'))
        layForma.addWidget(rbRombe, 0, 2)

        rbPentagon = QRadioButton()
        rbPentagon.setIcon(QIcon(imatgesDir+'pentagonW.png'))
        rbPentagon.toggled.connect(lambda x: setForma(
            'pentagon') if x else print(':D'))
        layForma.addWidget(rbPentagon, 0, 3)

        rbEstrella = QRadioButton()
        rbEstrella.setIcon(QIcon(imatgesDir+'starW.png'))
        rbEstrella.toggled.connect(lambda x: setForma(
            'star') if x else print(':D'))
        layForma.addWidget(rbEstrella, 1, 0)

        rbTriangle = QRadioButton()
        rbTriangle.setIcon(QIcon(imatgesDir+'triangleW.png'))
        rbTriangle.toggled.connect(lambda x: setForma(
            'triangle') if x else print(':D'))
        layForma.addWidget(rbTriangle, 1, 1)

        rbCercle = QRadioButton()
        rbCercle.setIcon(QIcon(imatgesDir+'circleW.png'))
        rbCercle.toggled.connect(lambda x: setForma(
            'circle') if x else print(':D'))
        rbCercle.click()
        layForma.addWidget(rbCercle, 0, 0)

        rbHexagon = QRadioButton()
        rbHexagon.setIcon(QIcon(imatgesDir+'hexagonW.png'))
        rbHexagon.toggled.connect(lambda x: setForma(
            'hexagon') if x else print(':D'))
        layForma.addWidget(rbHexagon, 1, 3)
        # Afegim els botons
        layBotons = QHBoxLayout()
        layBotons.addStretch()
        self._bAfegir = QvPushButton('Afegir com a capa de punts', destacat=True)
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(self.afegir)
        self._leNomCapa.textChanged.connect(
            lambda x: self._bAfegir.setEnabled(x != ''))
        layBotons.addWidget(self._bAfegir)
        self._lay.addLayout(layBotons)
    def showEvent(self, e):
        super().showEvent(e)
        self._leNomCapa.setFocus()
        self._leNomCapa.selectAll()
    def afegir(self):
        nivellCsv(self.parentWidget()._qV, self.parentWidget()._csv, self.parentWidget()._separador,
                  self._campCoordX, self._campCoordY, self._projeccio, self._leNomCapa.text(), self._color, symbol=self._forma)
        self.parentWidget().close()


if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp

    gui = True

    with qgisapp(guienabled=gui) as app:

        from moduls.QvApp import QvApp

        qApp = QvApp()
        arxiu = 'C:/Users/omarti/Documents/Random/gossos.csv'
        wiz = QvCarregaCsv(arxiu)
        with open('style.qss') as f:
            app.setStyleSheet(f.read())
            # wiz.setStyleSheet(f.read())
        wiz.show()
