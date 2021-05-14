from moduls.QvImports import *
from qgis.PyQt.QtWidgets import *
import itertools
import shutil
from moduls.QvMapificacio import QvMapificacio
from moduls.QvPushButton import QvPushButton
from moduls.QvEditorCsv import QvEditorCsv
from moduls.QvMapForms import QvFormNovaMapificacio
from moduls.QvConstants import QvConstants
from moduls.QvFuncioFil import QvFuncioFil
from moduls.QvMemoria import QvMemoria

# Còpia de la funció definida dins de qVista.py. Millor aquí???


def nivellCsv(projecte, llegenda, fitxer: str, delimitador: str, campX: str, campY: str, projeccio: int = 25831, nomCapa: str = 'Capa sense nom', color='red', symbol='circle', separadorDec='.'):
    if projeccio<0:
        try:
            import pandas as pd
        except ModuleNotFoundError:
            return False

        # si és -X, serà que són coordenades reduïdes en format X.
        df = pd.read_csv(fitxer, engine='python', sep=delimitador)
        nouCampX = f'{campX}_COMPLET'
        nouCampY = f'{campY}_COMPLET'
        nouFitxer = str(Path(fitxer).with_suffix('.coordenades_completes.csv')).replace('.coordenades_completes','_coordenades_completes')
        df[nouCampX]=df[campX]/1000+400000
        df[nouCampY]=df[campY]/1000+4500000
        df.to_csv(nouFitxer, sep=delimitador)
        
        campX, campY = nouCampX, nouCampY
        fitxer = nouFitxer
        projeccio = -projeccio
        
    # uri = "file:///"+fitxer + "?type=csv&delimiter=%s&xField=%s&yField=%s" % (delimitador, campX, campY)
    uri = fr'file:///{fitxer}?type=csv&delimiter={delimitador}&xField={campX}&yField={campY}&decimalPoint={separadorDec}'
    layer = QgsVectorLayer(uri, nomCapa, 'delimitedtext')
    layer.setCrs(QgsCoordinateReferenceSystem(
        projeccio, QgsCoordinateReferenceSystem.EpsgCrsId))
    if layer is not None or layer is not NoneType:
        symbol = QgsMarkerSymbol.createSimple({'name': symbol, 'color': color, 'outline_width':'0.05'})
        # if layer.renderer() is not None:
        #     layer.renderer().setSymbol(symbol)
        pr=layer.dataProvider()
        writer=QgsVectorFileWriter.writeAsVectorFormat(layer,fitxer[:-4],pr.encoding(),pr.crs(),symbologyExport=QgsVectorFileWriter.SymbolLayerSymbology)
        capaGpkg=QgsVectorLayer(fitxer[:-4]+'.gpkg',nomCapa,'ogr')
        # capaGpkg.renderer().setSymbol(symbol)
        projecte.addMapLayer(capaGpkg)
        llegenda.saveStyleToGeoPackage(capaGpkg)
        # qV.project.addMapLayer(layer)
        # qV.setDirtyBit(True)
        return True
    else:
        print("no s'ha pogut afegir la nova layer")
        return False


def esCoordAux(coord, rangs):
    try:
        coord = float(coord)
    except Exception as e:
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
                  'XETRS89', 'X_ETRS89', 'ETRS89_X', 'ETRS89X', 'X', 'LAT', 'LATITUD')
    # nomsCampsX=(':D')
    nomsCampsY = ('Y89AB', 'YTRETRS89A', 'COORDY', 'COORD_Y', 'YUTM', 'Y_UTM',
                  'YETRS89', 'Y_ETRS89', 'ETRS89_Y', 'ETRS89Y', 'Y', 'LON', 'LONGITUD')
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

def creaCsvAmbNums(ruta, sep, cod, campAdreca):
    nom_res = str(Path(tempdir,Path(ruta).name))
    # nom_res = f'{tempdir}/{Path(ruta).name}'
    with open(ruta, encoding=cod) as f, open(nom_res,'w', encoding=cod) as ff:
        read = csv.DictReader(f, delimiter=sep)
        writ = csv.DictWriter(ff, delimiter=sep, fieldnames=read.fieldnames+['NUM_INFERIT_QVISTA'])
        writ.writeheader()
        for row in read:
            adreca = row[campAdreca].split(',')
            row[campAdreca], row['NUM_INFERIT_QVISTA'] = ','.join(adreca[:-1]), adreca[-1]
            writ.writerow(row)
    return nom_res

class QvCarregaCsv(QDialog):
    def __init__(self, rutaCsv: str, projecte, llegenda, parent=None):
        super().__init__(parent,Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle('Carregador d\'arxius CSV')
        self.setMinimumWidth(750)
        self._llegenda=llegenda
        self._projecte=projecte
        self._csv = self._primerCsv = rutaCsv
        self.loadMap()
        # self._mapificador = QvMapificacio(rutaCsv)
        self._widgetSup = QWidget(objectName='layout')
        self._layoutGran = QVBoxLayout()
        self.setLayout(self._layoutGran)
        self._layout = QVBoxLayout()
        self._layoutGran.addWidget(self._widgetSup)
        self._layoutGran.addLayout(self._layout)
        self._layoutGran.setContentsMargins(20, 20, 20, 20)
        # self._layoutGran.setSpacing(0)
        self._layout.setContentsMargins(0,0,0,0)
        # self._layout.setSpacing(0)
        self.triaPrimeraPantalla()
        #TODO: REVISAR
        # self._finestres=[x(self) for x in (CsvPrefab,CsvTriaSeparador, CsvTriaGeom ,CsvXY, CsvAdreca, CsvGeneraCoords, CsvPersonalitza)]
        # for x in self.finestres: x.hide() #Ocultem totes les finestres que no volem mostrar
        # self.widgetActual=self.finestres[1]

        self.formata()
        self.oldPos = self.pos()
    def loadMap(self):
        self._mapificador = QvMapificacio(self._csv)
        self._codificacio = self._mapificador.codi
        self.setSeparador()
    def setSeparador(self):
        self._separador = self._mapificador.separador
    def getPrimeraPantalla(self):
        aux=QvMemoria().getCampsGeocod(self.parentWidget()._primerCsv)
        if aux is not None:
            if aux['teCoords']:
                return CsvCoords(self,self,**aux['camps'])
            else:
                return CsvAdreca(self,self,**aux['camps'])
        campX, campY = campsCoords(
            self._csv, self._separador, self._codificacio)
        if campX is not None and campY is not None:
            return CsvCoords(self, self, campX, campY)
        else:
            return CsvAdreca(self, self)

    def triaPrimeraPantalla(self):
        # self._widgetActual=self.getPrimeraPantalla()
        self._widgetActual=CsvTab(self)
        self._widgetActual.salta.connect(self.salta)

    def formata(self):
        self._layoutGran.addWidget(self._widgetActual)

    def salta(self, nouW):
        self._widgetActual.hide()
        self._layoutGran.replaceWidget(self._widgetActual, nouW)
        self._widgetActual = nouW
        try:
            self._widgetActual.salta.disconnect()
        except:
            pass
        self._widgetActual.salta.connect(self.salta)

    def setCsv(self, csv):
        self._csv = csv


class CsvPagina(QWidget):
    salta = pyqtSignal(QWidget)

    def __init__(self, carregador, parent=None):
        super().__init__(parent)
        self._carregador=carregador
        self._lay = QVBoxLayout(self)
        # self._lay.setContentsMargins(0,0,0,0)
        # self._lay.setSpacing(0)
        self.setLayout(self._lay)
        self._lblTitol = QLabel()  # falta posar-li l'estil i tal
        self._lblTitol.setFont(QvConstants.FONTTITOLS)
        self._lay.addWidget(self._lblTitol)

    def _mostraTaula(self, errors=[], modal=False):
        # La senyal clicked dels botons passa un booleà que indica si està checked o no
        # Si ens demana veure-ho des d'un botó directament, vol dir que no hi ha errors. Per tant, ignorem el booleà
        if isinstance(errors, bool):
            errors = []
        # TODO: Invocar QvEditorCsv per mostrar la taula
        self._wid = QvEditorCsv(self._carregador._csv, errors, self._carregador._codificacio, self._carregador._separador,parent=self)
        
        
        if modal:
            self._wid.setWindowTitle("Veure i arreglar errors")
            self._canviat = False
            self._wid.rutaCanviada.connect(self._carregador.setCsv)

            def setCanviat():  # Una lambda no pot tenir assignacions :(
                self._canviat = True
            self._wid.modificat.connect(setCanviat)
            self._wid.exec()
            return self._canviat
        else:
            self._wid.setWindowTitle("Veure taula completa")
            self._wid.setReadOnly(True)
            self._wid.show()

    def getCamps(self):
        with open(self._carregador._csv, encoding=self._carregador._codificacio) as f:
            reader = csv.DictReader(
                f, delimiter=self._carregador._separador)
            return reader.fieldnames

    def _setTitol(self, titol):
        self._lblTitol.setText(titol)

    def _mapifica(self):
        # fMap = QvFormNovaMapificacio(
        #     self._carregador._llegenda, mapificacio=self._carregador._mapificador)
        # if fMap.exec()==QDialog.Accepted:
        #     self._carregador.close()
        if QvFormNovaMapificacio.executa(self._carregador._llegenda,
            mapificacio=self._carregador._mapificador) == QDialog.Accepted:
            self._carregador.close()

class CsvTab(QTabWidget):
    salta = pyqtSignal(QWidget)
    def __init__(self,parent=None):
        super().__init__(parent)
        
        aux=QvMemoria().getCampsGeocod(self.parentWidget()._primerCsv)
        if aux is not None:
            if aux['teCoords']:
                primer=0
                self._coords=CsvCoords(self.parentWidget(),self.parentWidget(),**aux['camps'])
                self._adreca=CsvAdreca(self.parentWidget(),self.parentWidget())
            else:
                primer=1
                self._coords=CsvCoords(self.parentWidget(),self.parentWidget())
                self._adreca=CsvAdreca(self.parentWidget(),self.parentWidget(),**aux['camps'])
        else:
            campX, campY = campsCoords(
                self.parentWidget()._csv, self.parentWidget()._separador, self.parentWidget()._codificacio)
            self._coords=CsvCoords(self.parentWidget(),self.parentWidget(), campX, campY)
            self._adreca=CsvAdreca(self.parentWidget(),self.parentWidget())
            primer=0 if campX is not None else 1
        with open(parent._mapificador.fDades,encoding=parent._mapificador.codi) as f:
            reader=csv.DictReader(f,delimiter=parent._mapificador.separador)
            numFiles=300
            self._coords._taulaPreview.setRowCount(numFiles)
            self._coords._taulaPreview.setColumnCount(len(reader.fieldnames))
            self._coords._taulaPreview.setHorizontalHeaderLabels(reader.fieldnames)
            self._adreca._taulaPreview.setRowCount(numFiles)
            self._adreca._taulaPreview.setColumnCount(len(reader.fieldnames))
            self._adreca._taulaPreview.setHorizontalHeaderLabels(reader.fieldnames)

            files=0
            for i, fila in itertools.islice(enumerate(reader),numFiles):
                files+=1
                for j, x in enumerate(reader.fieldnames):
                    self._coords._taulaPreview.setItem(i,j,QTableWidgetItem(fila[x]))
                    self._adreca._taulaPreview.setItem(i,j,QTableWidgetItem(fila[x]))
            #Actualitzem les files. Per les taules petites
            self._coords._taulaPreview.setRowCount(files)
            self._adreca._taulaPreview.setRowCount(files)
        self._coords.salta.connect(lambda x: self.salta.emit(x))
        self._adreca.salta.connect(lambda x: self.salta.emit(x))
        self.addTab(self._coords,'Coordenades')
        self.addTab(self._adreca,'Adreces')
        self.setCurrentIndex(primer)

class CsvCoords(CsvPagina):
    def __init__(self, carregador, parent=None, campX=None, campY=None, proj=None):
        super().__init__(carregador,parent)
        self._setTitol('El CSV ja conté coordenades?')
        lbl=QLabel("Seleccioneu quins són els camps de coordenades i el seu sistema de referència geogràfic.\n\nDepenent del sistema podran ser coordenades (X,Y) en metres o (Latitud,Longitud) en graus")
        lbl.setWordWrap(True)
        self._lay.addWidget(lbl)
        self._lay.addStretch()
        # Creem una groupbox per triar els paràmetres de les coordenades
        self._gbCoords = QGroupBox(self)
        self._layCamps = QVBoxLayout(self._gbCoords)
        self._gbCoords.setLayout(self._layCamps)
        camps = self.getCamps()
        if campX is None:
            campX, campY = campsCoords(self._carregador._csv, self._carregador._separador, self._carregador._codificacio)
        self._proj = {'EPSG:25831 UTM 31N ETRS89': 25831,
                      'EPSG:3857 Pseudo Mercator (Google)': 3857,
                      'EPSG:4326 WGS 84': 4326,
                      'EPSG:23031 UTM 31N ED50': 23031,
                      'EPSG:23031 UTM 31N ED50 Reduïdes': -23031}
        if proj is None:
            proj='EPSG:25831 UTM ETRS89 31N'
        layX = QHBoxLayout()
        lblX = QLabel('Coordenada X:')
        lblX.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layX.addWidget(lblX)
        self._cbX = QComboBox()
        self._cbX.addItems(camps)
        self._cbX.setCurrentText(campX)
        layX.addWidget(self._cbX)

        layY = QHBoxLayout()
        lblY = QLabel('Coordenada Y:')
        lblY.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layY.addWidget(lblY)
        self._cbY = QComboBox()
        self._cbY.addItems(camps)
        self._cbY.setCurrentText(campY)
        layY.addWidget(self._cbY)

        def canviaLbls(x):
            if x in (0,3,4):
                lblX.setText('Coordenada X:')
                lblY.setText('Coordenada Y:')
            else:
                lblX.setText('Latitud:')
                lblY.setText('Longitud:')

        layProj = QHBoxLayout()
        lblProj = QLabel('Projecció:')
        lblProj.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layProj.addWidget(lblProj)
        self._cbProj = QComboBox()
        self._cbProj.addItems(self._proj.keys())
        self._cbProj.setCurrentText(proj)
        self._cbProj.currentIndexChanged.connect(canviaLbls)
        layProj.addWidget(self._cbProj)

        self._layCamps.addLayout(layX)
        self._layCamps.addLayout(layY)
        self._layCamps.addLayout(layProj)
        self._lay.addWidget(self._gbCoords)

        
        self._lay.addStretch()
        self._taulaPreview = QTableWidget()
        self._lay.addWidget(self._taulaPreview)
        self._lay.addStretch()

        # Botons per fer coses
        self._layBotons = QHBoxLayout()
        self._bVeure = QvPushButton("Veure taula completa",discret=True)
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bAfegir = QvPushButton('Afegir com a capa de punts')
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(self.afegir)
        self._bMapifica = QvPushButton('Mapificar')
        self._bMapifica.setToolTip('Crea una mapificació a partir de la taula per visualitzar-la sobre el mapa')
        self._bMapifica.clicked.connect(self._mapifica)
        with open(self._carregador._csv) as f:
            self._bMapifica.setEnabled('QVISTA_' in f.readline())
        #TODO: comprovar si hi ha camps de zona
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bAfegir)
        self._layBotons.addWidget(self._bMapifica)
        self._lay.addLayout(self._layBotons)

    def afegir(self):
        QvMemoria().setCampsGeocod(self._carregador._csv,{'teCoords':True,'camps':{'campX':self._cbX.currentText(),'campY':self._cbY.currentText(),'proj':self._cbProj.currentText()}})
        self.salta.emit(CsvAfegir(self._cbX.currentText(), self._cbY.currentText(
        ), self._proj[self._cbProj.currentText()], self._carregador))


class CsvAdreca(CsvPagina):
    def __init__(self, carregador, parent=None, **campsAdreca):
        super().__init__(carregador,parent)
        self._setTitol("El CSV conté adreces postals?")
        lblExpl = QLabel("Seleccioneu el camp o camps que contenen l'adreça.\n\nEspecifiqueu com a mínim el nom de la via i el número inicial. La resta de camps, si els teniu, serviran per accelerar i optimitzar la geocodificació.")
        lblExpl.setWordWrap(True)
        self._lay.addWidget(lblExpl)
        self._lay.addStretch()
        self._gbCamps = QGroupBox(self)
        self._layCamps = QGridLayout(self._gbCamps)
        self._gbCamps.setLayout(self._layCamps)
        camps = self.getCamps()
        self._cbTipusVia = QComboBox()
        self._cbTipusVia.addItems(['']+camps)
        layTipusVia = QHBoxLayout()
        lblTipusVia = QLabel('Tipus de via (carrer, plaça...):')
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
        

        self._cbNumI = QComboBox()
        self._cbNumI.addItems(['']+camps)
        layNumI = QHBoxLayout()
        lblNumI = QLabel('Número postal inicial:')
        lblNumI.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layNumI.addWidget(lblNumI)
        layNumI.addWidget(self._cbNumI)
        

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

        if len(campsAdreca)!=0:
            self._cbTipusVia.setCurrentText(campsAdreca['tipusVia'])
            self._cbVia.setCurrentText(campsAdreca['via'])
            self._cbNumI.setCurrentText(campsAdreca['numI'])
            self._cbNumF.setCurrentText(campsAdreca['numF'])
            self._cbLletraI.setCurrentText(campsAdreca['lletraI'])
            self._cbLletraF.setCurrentText(campsAdreca['lletraF'])
        else:
            self.campsDefecte()

        self._lay.addStretch()
        self._taulaPreview = QTableWidget()
        self._lay.addWidget(self._taulaPreview)
        self._lay.addStretch()

        self._layBotons = QHBoxLayout()
        self._bVeure = QvPushButton("Veure taula completa",discret=True)
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bGeocod = QvPushButton('Geocodificar')
        self._bGeocod.setToolTip("Obté les coordenades a partir d'adreces postals")
        self._bGeocod.clicked.connect(self.geocodifica)
        self._layBotons.addWidget(self._bVeure)
        self._layBotons.addStretch()
        self._layBotons.addWidget(self._bGeocod)
        self._lay.addLayout(self._layBotons)
    def campsDefecte(self):
        c=campsAdreces(self._carregador._csv,self._carregador._separador, self._carregador._codificacio)
        if c is not None:
            i=self._cbVia.findText(c)
            self._cbVia.setCurrentIndex(i)
        c=campsNum(self._carregador._csv,self._carregador._separador, self._carregador._codificacio)
        if c is not None:
            i=self._cbNumI.findText(c)
            self._cbNumI.setCurrentIndex(i)
    def geocodifica(self):
        arxiuNet=str(Path(self._carregador._csv).parent)+'\\'+self._carregador._mapificador.netejaString(Path(self._carregador._csv).stem,True)+'.csv'
        geocod=QvMemoria().getGeocodificat(self._carregador._csv, arxiuNet)
        if geocod is not None:
            #Preguntar si volem carregar directament el geocodificat
            resposta=QMessageBox.question(self,"Aquest arxiu ja ha sigut geocodificat prèviament", \
                "Aquest arxiu ja ha sigut geocodificat prèviament. Vol carregar-lo directament, estalviant així repetir la geocodificació?",QMessageBox.Yes|QMessageBox.No)
            if resposta==QMessageBox.Yes:
                self._carregador.setCsv(geocod)
                self._carregador._codificacio='utf-8'
                self._carregador._mapificador=QvMapificacio(geocod)
                self.salta.emit(CsvGeocodificat(None,0, self._carregador))
                return
        camps = [x.currentText() for x in (self._cbTipusVia, self._cbVia,
                 self._cbNumI, self._cbLletraI, self._cbNumF, self._cbLletraF)]
            
        QvMemoria().setCampsGeocod(self._carregador._csv,{'teCoords':False,'camps':{'tipusVia':camps[0],'via':camps[1],'numI':camps[2],
                'lletraI':camps[3],'numF':camps[4],'lletraF':camps[5]}})
        if camps[2]=='':
            nouCsv = creaCsvAmbNums(self._carregador._csv, self._carregador._separador, self._carregador._codificacio, self._cbVia.currentText())
            self._carregador._csv = nouCsv
            camps[2]='NUM_INFERIT_QVISTA'
            self._carregador.loadMap()
        self.salta.emit(CsvGeocod(camps, self._carregador))


class CsvGeocod(CsvPagina):
    def __init__(self, campsAdreca, carregador, parent=None):
        super().__init__(carregador, parent)
        self._setTitol('Geocodificació')
        # self._lay.addWidget(QLabel('GEOCODIFICACIÓ'))
        self._lblNumErrors = QLabel("Número d'errors: 0")
        self._lay.addWidget(self._lblNumErrors)
        self._lblFilesGeocod = QLabel("Files geocodificades: 0")
        self._lay.addWidget(self._lblFilesGeocod)
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
        self._carregador._mapificador.cancelProces()
        

    def showEvent(self, e):
        super().showEvent(e)
        # Falta mirar què fem amb els errors
        self.setCursor(QvConstants.CURSOROCUPAT)
        if self._carregador._mapificador.files>50000:
            self._lblExplicativa.show()
        # if self._cancelat:
        #     self._carregador.loadMap()
        self.fil=QvFuncioFil(lambda: self._carregador._mapificador.geocodificacio(self._camps, ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica",
                                                                      "Secció censal"), percentatgeProces=self._canviPercentatge, procesAcabat=self.acabat, errorAdreca=self._unErrorMes, filesGeocodificades=self._filesGeocod))
        self.fil.funcioAcabada.connect(lambda: self.acabat(-1))
        self.fil.start()
        # self._carregador._mapificador.geocodificacio(self._camps, ('Coordenada', 'Districte', 'Barri', 'Codi postal', "Illa", "Solar", "Àrea estadística bàsica",
        #                                                               "Secció censal"), percentatgeProces=self._canviPercentatge, procesAcabat=self.acabat)
        qApp.processEvents()
    def _canviPercentatge(self,p):
        self._progress.setValue(p)
        # qApp.processEvents()
    def _unErrorMes(self, err):
        self._errors.append(err)
        self._numErr += 1
        self._modificaLblErr()
    def _filesGeocod(self,f,files):
        # actualitzem la label cada 10 files. Això permet que es vegi més fluid
        if f%10==0 or f==files:
            self._lblFilesGeocod.setText("Files geocodificades: %i d'aproximadament %i"%(f,files))

    def _modificaLblErr(self):
        self._lblNumErrors.setText("Número d'errors: %i" % self._numErr)
        # qApp.processEvents()

    def acabat(self, n):
        if self._carregador._mapificador.cancel:
            self.salta.emit(self._carregador.getPrimeraPantalla())
        elif self.fil.resultat==False: # no podem posar "not self.fil.resultat", perquè el cas "None" s'avaluaria també
            QMessageBox.critical(self,'Error de geocodificació',f'Hi ha hagut un error durant la geocodificació:\n{self._carregador._mapificador.msgError}')
            self._carregador._mapificador.cancel = True
            self.acabat(n)
        else:
            # Aquí saltar al resultat
            arxiuNet=str(Path(self._carregador._csv).parent)+'\\'+self._carregador._mapificador.netejaString(Path(self._carregador._csv).stem,True)+'.csv'
            QvMemoria().setGeocodificat(self._carregador._csv, arxiuNet)
            self._carregador.setCsv(self._carregador._mapificador.fZones)
            # self._carregador._csv=self._carregador._mapificador.fDades
            self.salta.emit(CsvGeocodificat(self._errors, n, self._carregador,self._carregador))


class CsvGeocodificat(CsvPagina):
    def __init__(self, errors, temps, carregador, parent=None):
        super().__init__(carregador, parent)
        self._setTitol('Geocodificat')
        if temps!=0: 
            self._lay.addWidget(QLabel('Temps requerit per la geocodificació: %i segons'%temps))
            self._lay.addWidget(QLabel('Geocodificat a una velocitat de %.2f files per segon'%(self._carregador._mapificador.files/temps)))
        self._textEditErrors = QTextEdit()
        self._textEditErrors.setReadOnly(True)
        self._textEditErrors.setStyleSheet('background: white')
        self._lay.addWidget(self._textEditErrors)
        if errors is not None:
            self._errors = [x['_fila'] for x in errors]
            if len(self._errors)>0:
                self._definirErrors(self._errors)
            else:
                pass
        else:
            self._errors=[]
            self._textEditErrors.setText('Aquest arxiu ha sigut carregat directament des de la memòria cau.\nPer tant, no hi ha errors a mostrar.')
        # self._lay.addStretch()
        self._layBotons = QHBoxLayout()
        # Definició de la botonera
        self._bEnrere= QvPushButton('Enrere')
        self._bEnrere.clicked.connect(self._enrere)
        self._bVeure = QvPushButton("Veure i arreglar errors",discret=True)
        self._bVeure.setToolTip("Premeu aquest botó per visualitzar l'arxiu csv")
        self._bVeure.clicked.connect(self._mostraTaula)
        self._bAfegir = QvPushButton('Afegir com a capa de punts')
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(lambda: self.salta.emit(CsvAfegir(
            'QVISTA_ETRS89_COORD_X', 'QVISTA_ETRS89_COORD_Y', 25831, self._carregador)))
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
        self._carregador._csv = self._carregador._primerCsv
        self._carregador.loadMap()
        self.salta.emit(CsvTab(self._carregador))
        
    def _definirErrors(self, errors):
        errorsStr = ''
        for x in errors:
            errorsStr = errorsStr+'\nFila %i' % x
        self._textEditErrors.setText(
            'Files amb errors (click sobre "Veure i arreglar errors" per veure i editar la taula):%s' % errorsStr)

    def _mostraTaula(self):
        if super()._mostraTaula(self._errors, modal=True):
            # Si retorna true vol dir que hem fet algun canvi
            self._carregador._mapificador = QvMapificacio(self._carregador._csv)
            self._carregador.setSeparador()
            self.salta.emit(CsvAdreca(self._carregador,self._carregador))


class CsvAfegir(CsvPagina):
    def __init__(self, campCoordX, campCoordY, projeccio, carregador, parent=None):
        super().__init__(carregador, parent)
        self._setTitol('Afegir com a capa de punts')
        self._campCoordX = campCoordX
        self._campCoordY = campCoordY
        self._projeccio = projeccio
        # Nom de la capa
        layLbls = QVBoxLayout()
        layTries = QVBoxLayout()
        layGrup = QHBoxLayout()
        layGrup.addLayout(layLbls)
        layGrup.addLayout(layTries)
        self._lay.addLayout(layGrup)
        # layNom = QHBoxLayout()
        layLbls.addWidget(QLabel('Nom de la capa: '))
        self._leNomCapa = QLineEdit()
        self._leNomCapa.setText(Path(self._carregador._csv).stem)
        layTries.addWidget(self._leNomCapa)
        # self._lay.addLayout(layNom)
        # Color de la representació
        self._color = 'red'
        # layColor = QHBoxLayout()
        lblColor = QLabel('Color: ')
        lblColor.setAlignment(Qt.AlignRight)
        layLbls.addWidget(lblColor)

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
        layTries.addWidget(self._bColor)
        # layColor.addStretch()
        setColorBoto()
        self.cbDesaCsv = QCheckBox('Desar CSV geocodificat')
        self.cbDesaGpkg = QCheckBox('Desar capa resultant en arxiu GPKG')
        layTries.addWidget(self.cbDesaCsv)
        layTries.addWidget(self.cbDesaGpkg)
        # self._lay.addLayout(layColor)
        self._lay.addStretch()
        # Forma

        def setForma(imatge):
            self._forma = imatge
        gbForma = QGroupBox()
        self._lay.addWidget(gbForma)
        layForma = QGridLayout()
        gbForma.setLayout(layForma)
        rbCreu = QRadioButton()
        rbCreu.setIcon(QIcon(os.path.join(imatgesDir,'crossW.png')))
        rbCreu.toggled.connect(lambda x: setForma(
            'cross_fill') if x else print(':D'))
        layForma.addWidget(rbCreu, 1, 2)

        rbQuadrat = QRadioButton()
        rbQuadrat.setIcon(QIcon(os.path.join(imatgesDir,'squareW.png')))
        rbQuadrat.toggled.connect(lambda x: setForma(
            'square') if x else print(':D'))
        layForma.addWidget(rbQuadrat, 0, 1)

        rbRombe = QRadioButton()
        rbRombe.setIcon(QIcon(os.path.join(imatgesDir,'rhombusW.png')))
        rbRombe.toggled.connect(lambda x: setForma(
            'diamond') if x else print(':D'))
        layForma.addWidget(rbRombe, 0, 2)

        rbPentagon = QRadioButton()
        rbPentagon.setIcon(QIcon(os.path.join(imatgesDir,'pentagonW.png')))
        rbPentagon.toggled.connect(lambda x: setForma(
            'pentagon') if x else print(':D'))
        layForma.addWidget(rbPentagon, 0, 3)

        rbEstrella = QRadioButton()
        rbEstrella.setIcon(QIcon(os.path.join(imatgesDir,'starW.png')))
        rbEstrella.toggled.connect(lambda x: setForma(
            'star') if x else print(':D'))
        layForma.addWidget(rbEstrella, 1, 0)

        rbTriangle = QRadioButton()
        rbTriangle.setIcon(QIcon(os.path.join(imatgesDir,'triangleW.png')))
        rbTriangle.toggled.connect(lambda x: setForma(
            'triangle') if x else print(':D'))
        layForma.addWidget(rbTriangle, 1, 1)

        rbCercle = QRadioButton()
        rbCercle.setIcon(QIcon(os.path.join(imatgesDir,'circleW.png')))
        rbCercle.toggled.connect(lambda x: setForma(
            'circle') if x else print(':D'))
        rbCercle.click()
        layForma.addWidget(rbCercle, 0, 0)

        rbHexagon = QRadioButton()
        rbHexagon.setIcon(QIcon(os.path.join(imatgesDir,'hexagonW.png')))
        rbHexagon.toggled.connect(lambda x: setForma(
            'hexagon') if x else print(':D'))
        layForma.addWidget(rbHexagon, 1, 3)
        # Afegim els botons
        layBotons = QHBoxLayout()
        layBotons.addStretch()
        self._bAfegir = QvPushButton('Afegir com a capa de punts', destacat=True)
        self._bAfegir.setToolTip('Afegeix al mapa com a capa de punts')
        self._bAfegir.clicked.connect(self.afegir)
        self._bEnrere = QvPushButton('Enrere')
        self._bEnrere.setToolTip('Retrocedeix a la pantalla anterior')
        self._bEnrere.clicked.connect(self._enrere)
        self._leNomCapa.textChanged.connect(
            lambda x: self._bAfegir.setEnabled(x != ''))
        layBotons.addWidget(self._bEnrere)
        layBotons.addWidget(self._bAfegir)
        self._lay.addLayout(layBotons)
    def showEvent(self, e):
        super().showEvent(e)
        self._leNomCapa.setFocus()
        self._leNomCapa.selectAll()
    def _enrere(self):
        self.salta.emit(CsvGeocodificat([],0,self._carregador))
    def calculaSeparadorDec(self):
        def conteComa(x):
            return ',' in x[self._campCoordX] or ',' in x[self._campCoordY]
        def contePunt(x):
            return '.' in x[self._campCoordX] or '.' in x[self._campCoordY]

        with open(self._carregador._csv) as f:
            reader = csv.DictReader(f, delimiter=self._carregador._separador)
            ambDecimals = filter(lambda x: conteComa(x) or contePunt(x), reader)
            try:
                primer = next(ambDecimals)
                if contePunt(primer):
                    return '.'
                return ','
            except:
                return ''
    def afegir(self):
        if not nivellCsv(self._carregador._projecte, self._carregador._llegenda, self._carregador._csv, self._carregador._separador, self._campCoordX, self._campCoordY, self._projeccio, self._leNomCapa.text(), self._color, symbol=self._forma, separadorDec=self.calculaSeparadorDec()):
            QMessageBox.warning(self,"No s'ha pogut afegir la capa","No s'ha pogut afegir aquest arxiu. Contacteu amb la persona de referència")
        nomBase = str(Path(self._carregador._csv).stem)
        if self.cbDesaCsv.isChecked():
            nom, _ = QFileDialog.getSaveFileName(self,'Desar csv',f'{QvMemoria().getDirectoriDesar()}/{nomBase}.csv',"(*.csv)")
            if nom!='':
                shutil.copyfile(self._carregador._csv,nom)
        if self.cbDesaGpkg.isChecked():
            nom, _ = QFileDialog.getSaveFileName(self,'Desar GPKG',f'{QvMemoria().getDirectoriDesar()}/{nomBase}.gpkg',"(*.gpkg)")
            if nom!='':
                shutil.copyfile(self._carregador._csv.replace('.csv','.gpkg'), nom)
        self._carregador.close()


if __name__ == '__main__':
    from qgis.core.contextmanagers import qgisapp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvDropFiles import QvDropFiles

    gui = True

    with qgisapp(guienabled=gui) as app:
        with open('style.qss') as f:
            app.setStyleSheet(f.read())
        canvas = QvCanvas(llistaBotons=["panning","zoomIn","zoomOut"])
        project = QgsProject.instance()
        projecteInicial = './mapesOffline/qVista default map.qgs'
        project.read(projecteInicial)
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        llegenda = QvLlegenda()
        llegenda.show()
        canvas.show()

        def obreGeocod(files):
            for x in files:
                if not x.lower().endswith('.csv'): continue #Si no és un csv ens el saltem
                carregador=QvCarregaCsv(x,project,llegenda)
                carregador.show()
        dropCanvas = QvDropFiles(canvas,['.csv'])
        dropCanvas.arxiusPerProcessar.connect(obreGeocod)