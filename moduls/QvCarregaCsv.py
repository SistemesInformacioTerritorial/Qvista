from moduls.QvImports import *
from enum import IntEnum
from moduls.QvLectorCsv import QvLectorCsv
#import qVista
import tempfile
from moduls.QvGeocod import QvGeocod
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
import re
from csv import DictReader
import io
import chardet
import time
from pathlib import Path
from typing import Callable

class QvCarregaCsv(QWizard):
    finestres = IntEnum(
        'finestres', 'Precalculat TriaSep           TriaGeom CampsXY Adreca GeneraCoords Personalitza')
                             #TriaSepDec

    def __init__(self, csv: str, carregar: Callable[[str,str,str,str],None], parent: QWidget = None):
        '''Crea un assistent de càrrega de csv
        Arguments:
            csv{str} -- Nom de l'arxiu a carregar
            carregar{ (str,str,str,str,nomCapa: str) -> None } -- Funció que rep, per ordre, nom del csv, nom del separador, nom de la coordenada X, nom de la coordenada Y i nom de la capa, i carrega l'arxiu
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.carregar = carregar
        self.nomCapa = csv[:-4]
        self.nomCapa = self.nomCapa.split('\\')[-1].split('/')[-1]
        # self.csv = csv
        self.resultatsMostrats = False  #
        self.readerTmp = False          # Serveixen pel tema de cancel·lar el procés de calcular coordenades i que no peti a les segones voltes
        self.numeroLinies = -1          #
        self.setNomCsv(csv)
        self.color = 'red'
        self.symbol = 'circle'
        self.aprofitar = False #per defecte no aprofitarà les coordenades precalculades
        self.formata()
        self.camps = DictReader(self.getCsv(), delimiter=';').fieldnames
        if 'XCalculadaqVista' in self.camps and 'YCalculadaqVista' in self.camps:
            self.setPage(QvCarregaCsv.finestres.Precalculat,QvCarregaCsvPrecalculat(self))

        self.setPage(QvCarregaCsv.finestres.TriaSep, QvCarregaCsvTriaSep(self))
        #self.setPage(QvCarregaCsv.finestres.TriaSepDec,QvCarregaCsvTriaSepDec(self))
        self.setPage(QvCarregaCsv.finestres.TriaGeom,
                    QvCarregaCsvTriaGeom(self))
        self.setPage(QvCarregaCsv.finestres.CampsXY, QvCarregaCsvXY(self))
        self.setPage(QvCarregaCsv.finestres.Adreca, QvCarregaCsvAdreca(self))
        self.setPage(QvCarregaCsv.finestres.GeneraCoords,
                    QvCarregaCsvGeneraCoords(self))
        self.setPage(QvCarregaCsv.finestres.Personalitza,
                    QvCarregaCsvPersonalitza(self))

    def formata(self):
        '''Dóna format a l'assistent'''
        self.setOptions(QWizard.NoBackButtonOnStartPage)
        self.segButton = QvPushButton('Següent', destacat=True)
        self.backButton = QvPushButton('Enrere', destacat=False)
        self.finishButton = QvPushButton('Finalitzar', destacat=True)
        self.cancelButton = QvPushButton('Cancel·lar', destacat=False)
        self.commitButton = QvPushButton('Geocodifica', destacat=True)

        self.setButton(QvCarregaCsv.NextButton, self.segButton)
        self.setButton(QvCarregaCsv.BackButton, self.backButton)
        self.setButton(QvCarregaCsv.FinishButton, self.finishButton)
        self.setButton(QvCarregaCsv.CancelButton, self.cancelButton)
        self.setButton(QvCarregaCsv.CommitButton, self.commitButton)

        self.setFixedWidth(500)
        self.setFixedHeight(460)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setStyleSheet('''
            background-color: %s;
            color: %s;
            /*QWidget {border: 0px} 
            QFrame {border: 0px} 
            QLabel {border: 0px}*/
            QRadioButton {background-color: transparent}
            ''' % (QvConstants.COLORBLANCHTML, QvConstants.COLORFOSCHTML))
        self.setPixmap(QWizard.LogoPixmap, QPixmap(imatgesDir+'layers.png'))
        self.setFont(QvConstants.FONTTEXT)
        self.oldPos = self.pos()

    def prefab (self):
        self.coordX = 'XCalculadaqVista'
        self.coordY = 'YCalculadaqVista'
        self.separador = ';'
        self.proj = 25831

    def accept(self):
        super().accept()

        self.carregar(self.csv, self.separador, self.coordX, self.coordY,
                      self.proj, self.nomCapa, color=self.color, symbol=self.symbol)

    # Aquestes funcions seran cridades NOMÉS des de les pàgines
    def setSeparador(self, sep: str):
        self.separador = sep

    def setSeparadorDec(self, sepD: str): #Teòricament no es cridarà
        self.separadorDec = sepD

    def setCoordX(self, coordX: str):
        self.coordX = coordX

    def setCoordY(self, coordY: str):
        self.coordY = coordY

    def setProjecció(self, proj: int):
        self.proj = proj

    def setNomCapa(self, nomCapa: str):
        self.nomCapa = nomCapa

    def setNomCsv(self, csv: str):
        if not hasattr(self,'csv'):
            self.csv=csv
        #Si fem setNomCsv d'un nom que ja tenim, no repetirem càlculs
        elif self.csv==csv: return
        
        if not hasattr(self, 'csvOrig'):
            self.csvOrig = self.csv
        self.csv = csv
        #Detecció de la codificació
        with open(self.csv,'rb') as f:
            string=b''
            i=0
            while i<112:
                if i!=0: string+=f.readline() #???
                i+=1
            self.csvEncoding=chardet.detect(string)['encoding']
        #Obertura
        self.arxiuCsv=open(self.csv,'r',errors='ignore',encoding=self.csvEncoding)
    def getCsvName(self):
        return self.csv
    def getCsv(self):
        #Anem al principi de l'arxiu, per si en algun moment ens havíem desplaçat
        self.arxiuCsv.seek(0)
        return self.arxiuCsv

    def setDadesAdreca(self, tipusVia: str, via: str, numIni: str, lletraIni: str, numFi: str, lletraFi: str):
        self.dadesAdreca = (tipusVia, via, numIni, lletraIni, numFi, lletraFi)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.segButton.isEnabled():
                self.next()

    def show(self):
        super().show()
        self.activateWindow()  # Que el carregador aparegui per sobre de tot


class QvCarregaCsvPage(QWizardPage):
    def __init__(self, parent: QWidget = None):
        '''Crea una pàgina de l'assistent de càrrega de csv
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.parent = parent
        self.setTitle('Assistent de càrrega de csv')
        self.setSubTitle('')
        self.formata()

    def formata(self):
        # self.setStyleSheet('QFrame {border: 0px}')
        self.setStyleSheet('''background-color: %s; 
                              QFrame {border: 0px} 
                              QLabel {border: 0px}
                              ''' % QvConstants.COLORBLANCHTML)
        self.setFont(QvConstants.FONTTITOLS)
        self.setContentsMargins(0, 0, 0, 0)

    def mostraTaula(self, completa: bool=False, guardar: bool = False):
        '''Mostra la taula provisional que està carregant
        Keyword Arguments:
            completa{bool} -- Indica si volem mostrar la taula completa.
                Si és false, mostra una previsualització de 10 elements 
                (default: {False})
        '''
        self.table = QvLectorCsv(self.parent.nomCapa, self.parent.getCsv(), self.parent.separador, completa, guardar, self)
        self.layoutTable = QVBoxLayout()
        self.layout.addLayout(self.layoutTable)
        self.layoutTable.addWidget(self.table)
        if guardar:
            self.table.setMinimumHeight(120)
            self.bGuardar = QvPushButton("Guardar CSV")
            self.bGuardar.clicked.connect(lambda: self.table.writeCsv(self.parent.getCsv()))
            self.layoutB = QVBoxLayout()
            self.lblOff = QLabel()
            self.lblOff.setFixedHeight(0)
            self.lblOff.setFixedWidth(0)
            self.layoutB.setAlignment(Qt.AlignCenter)
            self.layoutTable.addWidget(self.lblOff)
            self.layoutB.addWidget(self.bGuardar)
            self.layoutTable.addLayout(self.layoutB)
            

    def recarregaTaula(self, completa: bool=False):
        self.table = QvtLectorCsv(
            self.parent.getCsv(), self.parent.separador, completa, self)

    def showEvent(self, event):
        super().showEvent(event)
        # qApp.processEvents()
        if hasattr(self, 'table'):
            self.table.recarrega(self.parent.separador)

    def obteCamps(self):
        return csv.DictReader(self.parent.getCsv(), delimiter=self.parent.separador).fieldnames
    #  PROBLEMA: Les línies separadores es dibuixen dins d'una funció d'una classe inaccessible, que es diu QWizardHeader
    #            No podem aplicar-hi una stylesheet ni una paleta de colors, ja que no podem accedir a la instància de la classe
    #            La única solució que he pogut trobar és canviar la paleta de colors de la app, posant el color Mid del mateix
    #            color que la base de manera que la línia hi sigui, però invisible
    # "SOLUCIÓ": Modificar la paleta de colors de l'aplicació perquè el color Mid sigui igual que el color Base, pintar, i
    #            tornar a posar la paleta com al principi, de manera que teòricament el canvi no es noti
    #      TODO: Trobar alguna manera de fer-ho que no vulneri totes les regles no escrites de la programació

    def paintEvent(self, event):
        pal = QPalette(self.palette())
        colorMidAnt = qApp.palette().color(QPalette.Mid)
        pal.setColor(QPalette.Mid, pal.color(QPalette.Base))
        qApp.setPalette(pal)
        super().paintEvent(event)
        pal.setColor(QPalette.Mid, colorMidAnt)
        qApp.setPalette(pal)

    def setTitle(self, title: str):
        s = '<p><span style="color: #38474f;"><strong><span style="font-family: arial, helvetica, sans-serif; font-size: 12pt;">%s</span></strong></span></p>' % title
        super().setTitle(s)

    def setSubTitle(self, subtitle: str):
        s = '<p><span style="color: #38474f; font-size: 10pt;"><strong><span style="font-family: arial, helvetica, sans-serif;">%s</span></strong></span></p>' % subtitle
        super().setSubTitle(s)

class QvCarregaCsvPrecalculat(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet escollir entre el procediment normal o saltar-se'l 
            en cas que trobi els camps XCalculadaqVista i YCalculadaqVista.
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.parent = parent
        self.setSubTitle("Procediment a seguir")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio0 = QLabel(
            """Hem detectat que l'arxiu .CSV que vols carregar ja ha estat tractat per aquest programa. Vols que es carregui directament o vols continuar amb el procediment normal?""")
        self.lblExplicacio0.setWordWrap(True)
        self.layout.addWidget(self.lblExplicacio0)
        self.setLayout(self.layout)
        self.botoA = QRadioButton('Carregar directament')
        self.botoB = QRadioButton('Procediment normal aprofitant coordenades calculades')
        self.botoC = QRadioButton('Procediment normal recalculant totes les coordenades')
        self.layoutBotons = QVBoxLayout()
        self.layoutBotons.setSpacing(20)
        self.layoutBotons.addWidget(self.botoA)
        self.layoutBotons.addWidget(self.botoB)
        self.layoutBotons.addWidget(self.botoC)
        self.layout.addLayout(self.layoutBotons)

        def activaBoto():
            self.completeChanged.emit()
        self.botoA.toggled.connect(activaBoto)
        self.botoB.toggled.connect(activaBoto)
        self.botoC.toggled.connect(activaBoto)

    def isComplete(self):
        return self.botoA.isChecked() or self.botoB.isChecked() or self.botoC.isChecked()

    def nextId(self):
        if self.botoA.isChecked():
            self.parent.prefab()
            return QvCarregaCsv.finestres.Personalitza
        if self.botoB.isChecked():
            self.parent.aprofitar = True
        return QvCarregaCsv.finestres.Adreca

class QvCarregaCsvTriaSep(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar el separador d'aquest
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        # self.setSubTitle('Tria del separador de camps')
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio1 = QLabel(
            "Escolliu quin separador fa servir l'arxiu CSV que voleu carregar:")
        self.layout.addWidget(self.lblExplicacio1)
        self.setLayout(self.layout)
        self.layoutCheckButton = QHBoxLayout(self)
        self.layout.addLayout(self.layoutCheckButton)
        self.lblSep = QLabel()
        self.lblSep.setText("Separador:")
        self.cbSep = QComboBox()
        self.cbSep.setFixedWidth(60)
        llistaSeparadors = [';', ',', '.', ':', '|']
        self.cbSep.addItems(llistaSeparadors)
        self.layoutCheckButton.addWidget(self.lblSep)
        self.layoutCheckButton.addWidget(self.cbSep)
        self.layoutCheckButton.addStretch(1)
        self.parent.setSeparador(infereixSeparadorRegex(parent.getCsv()))
        if not isinstance(self.parent.setSeparador, str):
            self.parent.setSeparador(';')
        self.mostraTaula()

        def botoClickat(boto):
            self.parent.setSeparador(self.cbSep.currentText())
            self.table.recarrega(self.parent.separador)
        self.cbSep.activated.connect(botoClickat)
        index = llistaSeparadors.index(self.parent.separador)
        self.cbSep.setCurrentIndex(index)

        def nextId(self):
            return QvCarregaCsv.finestres.TriaGeom


class QvCarregaCsvTriaSepDec(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar el separador decimal
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.setSubTitle('Tria del separador dels decimals')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio2 = QLabel(
            "Escolliu quin separador es fa servir per als decimals:")
        self.layout.addWidget(self.lblExplicacio2)
        self.layoutCheckButton = QHBoxLayout()
        self.layout.addLayout(self.layoutCheckButton)
        self.lblSepDec = QLabel()
        self.lblSepDec.setText("Separador Decimal:")
        self.cbSepDec = QComboBox()
        self.cbSepDec.setFixedWidth(60)
        llistaSeparadorsDecimals = ['.', ',']
        self.cbSepDec.addItems(llistaSeparadorsDecimals)
        self.layoutCheckButton.addWidget(self.lblSepDec)
        self.layoutCheckButton.addWidget(self.cbSepDec)
        self.parent.setSeparadorDec('.')

        def botoClickatDec(boto):
            self.parent.setSeparadorDec(self.cbSepDec.currentText())
        self.cbSepDec.activated.connect(botoClickatDec)
        self.layoutCheckButton.addStretch(1)
        self.mostraTaula()


# La classe per triar si definim la geometria amb coordenades X Y, o bé amb una adreça


class QvCarregaCsvTriaGeom(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar-ne la geometria
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        # self.setSubTitle('Tria del tipus de la geometria')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio3 = QLabel(
            "De quins camps obtenim les coordenades?")
        self.layout.addWidget(self.lblExplicacio3)
        self.botoXY = QRadioButton('Camps de coordenades X Y')
        self.botoAdreca = QRadioButton(
            'Cal geocodificar-los a partir d\'una adreça postal')
        self.layoutBotons = QVBoxLayout()
        self.layoutBotons.setSpacing(0)
        self.layoutBotons.addWidget(self.botoXY)
        self.layoutBotons.addWidget(self.botoAdreca)
        self.layout.addLayout(self.layoutBotons)

        def activaBoto():
            self.completeChanged.emit()
        self.botoXY.toggled.connect(activaBoto)
        self.botoAdreca.toggled.connect(activaBoto)
        self.setLayout(self.layout)
        self.mostraTaula()

    def isComplete(self):
        return self.botoXY.isChecked() or self.botoAdreca.isChecked()

    def nextId(self):
        if self.botoXY.isChecked():
            return QvCarregaCsv.finestres.CampsXY
        return QvCarregaCsv.finestres.Adreca


class QvCarregaCsvXY(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar els camps de les coordenades X Y
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # self.setSubTitle('Tria dels camps de les coordenades')
        self.layoutCoordX = QHBoxLayout()
        self.layoutCoordY = QHBoxLayout()
        self.layoutCoordP = QHBoxLayout()
        self.lblCoordX = QLabel()
        self.lblCoordX.setText("Camp Coordenada X:")
        self.lblCoordY = QLabel()
        self.lblCoordY.setText("Camp Coordenada Y:")
        self.lblProj = QLabel()
        self.lblProj.setText("Projecció usada:")
        self.layout.addLayout(self.layoutCoordX)
        self.layout.addLayout(self.layoutCoordY)
        self.layout.addLayout(self.layoutCoordP)
        self.parent.llistaCamps = self.obteCamps()
        self.cbX = QComboBox()
        self.cbX.addItems(self.parent.llistaCamps)
        self.cbY = QComboBox()
        self.cbY.addItems(self.parent.llistaCamps)
        self.layoutCoordX.addWidget(self.lblCoordX)
        self.layoutCoordX.addWidget(self.cbX)
        self.layoutCoordY.addWidget(self.lblCoordY)
        self.layoutCoordY.addWidget(self.cbY)
        self.cbProj = QComboBox()
        projeccionsDict = {'EPSG:25831 UTM ETRS89 31N': 25831,
                           'EPSG:3857 Pseudo Mercator (Google)': 3857,
                           'EPSG:4326 WGS 84': 4326,
                           'EPSG:23031 ED50 31N': 23031}
        self.cbProj.clear()
        self.cbProj.addItems([str(x) for x, y in projeccionsDict.items()])
        self.layoutCoordP.addWidget(self.lblProj)
        self.layoutCoordP.addWidget(self.cbProj)

        def xChanged():
            self.parent.setCoordX(self.cbX.currentText())

        def yChanged():
            self.parent.setCoordY(self.cbY.currentText())

        def projChanged():
            self.parent.setProjecció(
                projeccionsDict[self.cbProj.currentText()])
        self.cbX.currentIndexChanged.connect(xChanged)
        self.cbY.currentIndexChanged.connect(yChanged)
        self.cbProj.currentIndexChanged.connect(projChanged)
        xChanged()
        yChanged()
        projChanged()
        self.mostraTaula()


    def nextId(self):
        self.parent.setCoordX(self.cbX.currentText())
        self.parent.setCoordY(self.cbY.currentText())
        # if self.parent.separadorDec == ',':
        #     self.replaceComa()
        return QvCarregaCsv.finestres.Personalitza


class QvCarregaCsvAdreca(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar els camps de l'adreça
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        MIDACOMBOBOX = 100  # Perquè totes les combobox tinguin la mateixa mida
        # self.setSubTitle('Tria dels components de la geometria')
        self.layout = QVBoxLayout(self)
        self.lblExplicacio6 = QLabel()
        self.lblExplicacio6.setText(
            "Indiqueu el(s) camp(s) de les adreces que voleu geocodificar.\nNomés és obligatori el camp de la via")
        self.layout.addWidget(self.lblExplicacio6)
        self.layoutAdreca = QVBoxLayout()
        self.layout.addLayout(self.layoutAdreca)

        camps = self.obteCamps()
        def actualitzaUI(self):
            qApp.processEvents()
        self.lblTipus = QLabel('Tipus Via')
        self.cbTipus = QComboBox()
        self.cbTipus.setFixedWidth(MIDACOMBOBOX)
        self.cbTipus.addItems(['']+camps)
        self.cbTipus.currentIndexChanged.connect(actualitzaUI)
        self.lblCarrer = QLabel('Via o adreça')
        self.cbCarrer = QComboBox()
        self.cbCarrer.addItems(camps)
        self.cbCarrer.setFixedWidth(MIDACOMBOBOX)
        self.lblNumIni = QLabel('Nº post. inicial')
        self.cbNumIni = QComboBox()
        self.cbNumIni.addItems(['']+camps)
        self.cbNumIni.setFixedWidth(MIDACOMBOBOX)
        self.lblLletraIni = QLabel('Lletra inicial')
        self.cbLletraIni = QComboBox()
        self.cbLletraIni.setFixedWidth(MIDACOMBOBOX)
        self.cbLletraIni.addItems(['']+camps)
        self.lblNumFi = QLabel('Nº post. final  ')
        self.cbNumFi = QComboBox()
        self.cbNumFi.setFixedWidth(MIDACOMBOBOX)
        self.cbNumFi.addItems(['']+camps)
        self.lblLletraFi = QLabel('Lletra final  ')
        self.cbLletraFi = QComboBox()
        self.cbLletraFi.setFixedWidth(MIDACOMBOBOX)
        self.cbLletraFi.addItems(['']+camps)

        self.layoutCarrer = QHBoxLayout()
        self.layoutCarrer.addStretch(1)
        self.layoutTipus = QHBoxLayout()
        self.layoutTipus.addStretch(1)
        self.layoutNumLletraAux = QHBoxLayout()
        self.layoutNumero = QVBoxLayout()
        self.layoutLletra = QVBoxLayout()

        self.layoutTipus.addWidget(self.lblTipus)
        self.layoutTipus.addWidget(self.cbTipus)
        self.layoutCarrer.addWidget(self.lblCarrer)
        self.layoutCarrer.addWidget(self.cbCarrer)

        lay1 = QHBoxLayout()
        lay2 = QHBoxLayout()
        lay3 = QHBoxLayout()
        lay4 = QHBoxLayout()

        lay1.addStretch(1)
        lay2.addStretch(1)
        lay3.addStretch(1)
        lay4.addStretch(1)

        lay1.addWidget(self.lblNumIni)
        lay1.addWidget(self.cbNumIni)
        lay2.addWidget(self.lblLletraIni)
        lay2.addWidget(self.cbLletraIni)
        lay3.addWidget(self.lblNumFi)
        lay3.addWidget(self.cbNumFi)
        lay4.addWidget(self.lblLletraFi)
        lay4.addWidget(self.cbLletraFi)

        self.layoutNumero.addLayout(lay1)
        self.layoutNumero.addLayout(lay3)
        self.layoutLletra.addLayout(lay2)
        self.layoutLletra.addLayout(lay4)
        self.layoutNumLletraAux.addLayout(self.layoutNumero)
        self.layoutNumLletraAux.addLayout(self.layoutLletra)

        layAdrecaTipus = QHBoxLayout()
        layAdrecaTipus.addLayout(self.layoutTipus)
        layAdrecaTipus.addLayout(self.layoutCarrer)
        self.layoutAdreca.addLayout(layAdrecaTipus)
        self.layoutAdreca.addLayout(self.layoutNumLletraAux)

        def guardaDades():
            self.parent.setDadesAdreca(*[x.currentText() for x in (
                self.cbTipus, self.cbCarrer, self.cbNumIni, self.cbLletraIni, self.cbNumFi, self.cbLletraFi)])

        self.cbTipus.currentIndexChanged.connect(guardaDades)
        self.cbCarrer.currentIndexChanged.connect(guardaDades)
        self.cbNumIni.currentIndexChanged.connect(guardaDades)
        self.cbLletraIni.currentIndexChanged.connect(guardaDades)
        self.cbNumFi.currentIndexChanged.connect(guardaDades)
        self.cbLletraFi.currentIndexChanged.connect(guardaDades)
        guardaDades()
        # self.setCommitPage(True)

        self.mostraTaula()

    def nextId(self):
        return QvCarregaCsv.finestres.GeneraCoords


class WindowProgressBar(QWidget):
    def __init__(self, mida: int, parent: QWidget=None):
        super().__init__(parent)
        self.setWindowTitle("Progrés")
        self.progress = QProgressBar()
        self.progress.setGeometry(0, 0, 300, 25)
        self.mida = mida + 1
        self.progress.setMaximum(mida)
        self.count = 0  # necessari per a la progress bar
        self.errors = 0
        self.progress.setValue(self.count)
        self.layProgressW = QVBoxLayout()
        self.lblAdrInfo = QLabel()
        self.lblAdrInfo.setText("Adreces Processades: 0")
        self.lblAdrErrors = QLabel()
        self.lblAdrErrors.setText("Adreces no geolocalitzades: 0")
        self.layProgressW.addWidget(self.progress)
        self.layProgressW.addWidget(self.lblAdrInfo)
        self.layProgressW.addWidget(self.lblAdrErrors)
        self.setLayout(self.layProgressW)

        self.timeB=time.time()
        self.lblTempsRestant=QLabel()
        self.layProgressW.addWidget(self.lblTempsRestant)
        self.bCancelar = QvPushButton('Cancel·lar', destacat = False)
        self.layCancelar = QHBoxLayout()
        self.layCancelar.setAlignment(Qt.AlignRight)
        self.layProgressW.addLayout(self.layCancelar)
        self.layCancelar.addWidget(self.bCancelar)
        self.bCancelar.clicked.connect(self.cancelar)
        self.cancelat = False

    def actualitzaLBL(self):
        self.lblAdrInfo.setText(
            "Adreces Processades: %i d'aproximadament %i" % (self.count, self.mida))
        self.lblAdrErrors.setText(
            "Adreces no geolocalitzades: %i" % (self.errors))
        if self.count>=self.mida:
            tempsR=0
        else:
            tempsR=(time.time()-self.timeB)*max(self.mida/self.count,1)*(1-self.count/self.mida)
        tempsTxt=time.strftime("%H:%M:%S", time.gmtime(tempsR))
        self.lblTempsRestant.setText('Temps restant: %s'%tempsTxt)
    
    def cancelar(self):
        self.cancelat = True
       


class QvCarregaCsvGeneraCoords(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que genera les coordenades a partir d'una adreça
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        # self.setSubTitle("Gestió d'errors i finalitzar procés")
        self.parent = parent
        self.lblAdrecesError = QLabel()
        self.lblAdrecesError.setText("")
        self.lblAdrecesError.setStyleSheet('color: red')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20,0,20,0)
        self.lblExplicacio4 = QLabel()
        self.lblExplicacio4.setText("Aquestes són les adreces que no s'han pogut geolocalitzar:")
        self.layout.addWidget(self.lblExplicacio4)
        self.lblExplicacio4.hide()
        self.scrollErrors = QScrollArea()
        self.scrollErrors.setFixedHeight(75)
        self.scrollErrors.setWidgetResizable(True)
        self.lblAdrecesError.setContentsMargins(10, 5, 10, 5)
        self.scrollErrors.setWidget(self.lblAdrecesError)
        self.scrollErrors.hide()
        self.layout.addWidget(self.scrollErrors)
        self.showed = False


    def initializePage(self):
        self.parent.coordX = 'XCalculadaqVista'
        self.parent.coordY = 'YCalculadaqVista'
        self.cancelat = False

        def splitCarrer(nomComplet: str):
            if not hasattr(self, 'TIPUSVIES'):
                with open('dades/Tipusvia.csv') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    self.TIPUSVIES = [y+' ' for x in reader for y in x]
                    self.TIPUSVIES = list(set(self.TIPUSVIES))
            tipusVia = ''
            nomVia = ''
            num = ''
            for x in self.TIPUSVIES:
                if nomComplet.startswith(x):
                    tipusVia = x
                    # Eliminem el tipus de via i l'espai
                    nomComplet = nomComplet[len(x):]
            if ',' in nomComplet:
                subs = nomComplet.split(', ')
                nomVia = subs[0]
                num = re.findall('^[0-9]*', subs[1])[0]
            return tipusVia[:-1], nomVia, num

        self.showed = True
        self.parent.setProjecció(25831)
        fileCsv = self.parent.getCsv()
        reader = csv.DictReader(fileCsv, delimiter=self.parent.separador)
        nom=tempdir+Path(self.parent.getCsvName()).stem+str(int(time.time()))+'.csv'
        # with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', delete=False, newline='', encoding=self.parent.csvEncoding) as arxiuNouCsv:
        with open(nom,'w+', newline='') as arxiuNouCsv:
            self.parent.setNomCsv(nom)
            if not self.parent.readerTmp:
                try:
                    # mida = len(list(reader))-1
                    with tempfile.NamedTemporaryFile(suffix='.csv',mode='w',delete=True) as jajasalu2:
                        i=0
                        linies_a_mirar=500
                        wrt=csv.DictWriter(jajasalu2,fieldnames=reader.fieldnames)
                        wrt.writeheader()
                        self.parent.readerTmp = reader
                        for x in reader:
                            if i>=linies_a_mirar: break
                            wrt.writerow(x)
                            i+=1
                        jajasalu2.flush()
                        midalinia=os.path.getsize(jajasalu2.name)/linies_a_mirar
                        jajasalu2.seek(0)
                    mida=os.path.getsize(fileCsv.name)
                    #for _ in reader: mida+=1
                except:
                    mida=-1
                fileCsv.seek(0)
            if self.parent.numeroLinies == -1:
                numLinies=mida/midalinia
                self.parent.numeroLinies = numLinies
            else:
                numLinies = self.parent.numeroLinies

            wpg = WindowProgressBar(mida=numLinies)
            wpg.setWindowFlag(Qt.WindowStaysOnTopHint)
            wpg.setWindowFlag(Qt.WindowMinimizeButtonHint,False)
            wpg.setWindowFlag(Qt.WindowMaximizeButtonHint,False)
            wpg.setWindowModality(Qt.WindowModal)
            wpg.show()

            if 'XCalculadaqVista' not in self.parent.llistaCamps:
                self.names = self.parent.llistaCamps + [self.parent.coordX, self.parent.coordY]
            else: 
                self.names = self.parent.llistaCamps
            writer = csv.DictWriter(
                arxiuNouCsv, fieldnames=self.names, delimiter=self.parent.separador)
            #writer.writeheader()
            i = -1

            if self.parent.readerTmp:
                reader = self.parent.readerTmp

            for row in reader:
                i += 1

                if i == 0:
                    row[self.parent.coordX] = self.parent.coordX
                    row[self.parent.coordY] = self.parent.coordY
                    writer.writerow(row)
                    self.lblAdrecesError.setText("")

                    continue

                if numLinies > 1000:
                    if i%int(numLinies/1000)==0:
                        wpg.count = i
                        wpg.actualitzaLBL()
                        wpg.progress.setValue(wpg.count)
                    qApp.processEvents()
                else:
                    wpg.count = i
                    wpg.actualitzaLBL()
                    wpg.progress.setValue(wpg.count)

                if self.parent.aprofitar:
                    if row['XCalculadaqVista'] != '':
                        writer.writerow(row)
                        continue

                row[''] = ''

                if self.parent.dadesAdreca[0] == "": 
                    tipusVia = ""
                else:
                    tipusVia = row[self.parent.dadesAdreca[0]]
                nomVia = row[self.parent.dadesAdreca[1]]
                if self.parent.dadesAdreca[2] == "": 
                    numI = "" 
                else:
                    numI = row[self.parent.dadesAdreca[2]]
                    numI = re.sub('[^0-9][0-9]*', '', numI)
                if self.parent.dadesAdreca[3] == "":
                    lletraI = ""
                else:
                    lletraI = row[self.parent.dadesAdreca[3]]
                if self.parent.dadesAdreca[4] == "": 
                    numF = "" 
                else:
                    numF = row[self.parent.dadesAdreca[4]]
                    numF = re.sub('[^0-9][0-9]*', '', numF)
                if self.parent.dadesAdreca[5] == "":
                    lletraF = ""
                else:
                    lletraF = row[self.parent.dadesAdreca[5]]


                if self.parent.dadesAdreca[0] == "" and self.parent.dadesAdreca[2] == "":
                    try:
                        tipusVia, nomVia, numI = splitCarrer(row[self.parent.dadesAdreca[1]])
                    except:
                        pass


                elif self.parent.dadesAdreca[0] == "" and self.parent.dadesAdreca[2] != "":
                    try:
                        tipusVia, nomVia, _ = splitCarrer(row[self.parent.dadesAdreca[1]]) 
                    except:
                        pass

                elif self.parent.dadesAdreca[0] != "" and self.parent.dadesAdreca[2] == "":
                    try:
                        _, nomVia, numI = splitCarrer(row[self.parent.dadesAdreca[1]])
                    except:
                        pass

                if nomVia == "":
                    nomVia = row[self.parent.dadesAdreca[1]]  
                x, y = QvGeocod.coordsCarrerNum(tipusVia, nomVia, numI, lletraI, numF, lletraF)


                # wpg.count = wpg.count + 1
                if wpg.cancelat:
                    self.cancelat = True
                    del wpg
                    self.parent.backButton.click()
                    self.parent.segButton.click()
                    self.lblAdrecesError.setText("")
                    qApp.processEvents()
                    return
                    # return QvCarregaCsvGeneraCoords #Adreca #3
                    # self.initializePage()
                    # self.lblAdrecesError.setText("")
                    # return
                
                if x is None or y is None:
                    aux = self.lblAdrecesError.text()
                    wpg.errors = wpg.errors + 1
                    if aux != "":
                        self.lblAdrecesError.setText(
                            aux + "\n" + tipusVia + " " + nomVia + " " + numI + ' - Fila ' + str(i))
                    else:
                        self.lblAdrecesError.setText(
                            tipusVia + " " + nomVia + " " + numI + ' - Fila ' + str(i))
                    row[self.parent.coordX] = ""
                    row[self.parent.coordY] = ""
                    del row[""]
                    writer.writerow(row)
                    continue

                row[self.parent.coordX] = x
                row[self.parent.coordY] = y
                del row[""]
                writer.writerow(row)
                
            if not self.cancelat:
                self.lblExplicacio4.show()
                self.scrollErrors.show()
                self.lblExplicacio4.setText(
                "Aquestes són les adreces que no s'han pogut geolocalitzar: (%i)" %wpg.errors)
                if not self.parent.resultatsMostrats:
                    self.mostraTaula(completa=False, guardar = True)
                    self.parent.resultatsMostrats = True
        #self.recarregaTaula(completa=False)
        qApp.processEvents()
        # self.layout.addWidget(self.lblExplicacio5)

    def nextId(self):
        self.resize(500,500)
        return QvCarregaCsv.finestres.Personalitza


class QvCarregaCsvPersonalitza(QvCarregaCsvPage):
    def __init__(self, parent: QWidget=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet personalitzar la nova capa
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        # self.setSubTitle("Personalització de la nova capa")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(40)
        self.layout.setAlignment(Qt.AlignTop)
        self.layNom = QHBoxLayout()
        self.lblNom = QLabel()
        self.lblNom.setText("Nom de la capa:")
        self.leNom = QLineEdit()
        self.leNom.setText(parent.nomCapa)
        self.leNom.textChanged.connect(
            lambda: self.parent.setNomCapa(self.leNom.text()))
        self.layNom.addWidget(self.lblNom)
        self.layNom.addWidget(self.leNom)
        self.layout.addLayout(self.layNom)
        self.leColor = QLabel()
        self.leColor.setText("Trieu el color:")
        self.layColor = QHBoxLayout()
        self.layColor.addWidget(self.leColor)

        bColor = QPushButton()

        def canvicolor(self, dcolor):
            bColor.setStyleSheet("background-color: %s;" % dcolor.name())

        def openColorDialog(self):
            dcolor = QColorDialog().getColor()
            parent.color = dcolor.name()
            canvicolor(self, dcolor)
        bColor.clicked.connect(openColorDialog)
        bColor.setFixedWidth(322)
        #bColor.setText("Escull Color")
        self.layColor.addWidget(bColor)
        self.layout.addLayout(self.layColor)

        self.lblSimbol = QLabel()
        self.lblSimbol.setText("Amb quin símbol voleu representar els punts?")
        self.layout.addWidget(self.lblSimbol)

        self.groupBox = QGroupBox("")
        self.layIMGS1 = QHBoxLayout()
        radio1 = QRadioButton()

        def fradio1():
            parent.symbol = 'square'
        radio1.toggled.connect(fradio1)
        self.layIMGS1.addWidget(radio1)
        self.img1 = QLabel()
        self.img1.setPixmap(QPixmap(imatgesDir+'squareW.png'))
        self.layIMGS1.addWidget(self.img1)
        radio2 = QRadioButton()

        def fradio2():
            parent.symbol = 'diamond'
        radio2.toggled.connect(fradio2)
        self.layIMGS1.addWidget(radio2)
        self.img2 = QLabel()
        self.img2.setPixmap(QPixmap(imatgesDir+'rhombusW.png'))
        self.layIMGS1.addWidget(self.img2)
        radio3 = QRadioButton()

        def fradio3():
            parent.symbol = 'pentagon'
        radio3.toggled.connect(fradio3)
        self.layIMGS1.addWidget(radio3)
        self.img3 = QLabel()
        self.img3.setPixmap(QPixmap(imatgesDir+'pentagonW.png'))
        self.layIMGS1.addWidget(self.img3)
        # self.layout.addLayout(self.layIMGS1)
        radio7 = QRadioButton()

        def fradio7():
            parent.symbol = 'star'
        radio7.toggled.connect(fradio7)
        self.layIMGS1.addWidget(radio7)
        self.img7 = QLabel()
        self.img7.setPixmap(QPixmap(imatgesDir+'starW.png'))
        self.layIMGS1.addWidget(self.img7)
        self.layIMGS2 = QHBoxLayout()
        radio4 = QRadioButton()

        def fradio4():
            parent.symbol = 'triangle'
        radio4.toggled.connect(fradio4)
        self.layIMGS2.addWidget(radio4)
        self.img4 = QLabel()
        self.img4.setPixmap(QPixmap(imatgesDir+'triangleW.png'))
        self.layIMGS2.addWidget(self.img4)
        radio5 = QRadioButton()

        def fradio5():
            parent.symbol = 'circle'
        radio5.toggled.connect(fradio5)
        self.layIMGS2.addWidget(radio5)
        self.img5 = QLabel()
        self.img5.setPixmap(QPixmap(imatgesDir+'circleW.png'))
        self.layIMGS2.addWidget(self.img5)
        radio6 = QRadioButton()

        def fradio6():
            parent.symbol = 'hexagon'
        radio6.toggled.connect(fradio6)
        self.layIMGS2.addWidget(radio6)
        self.img6 = QLabel()
        self.img6.setPixmap(QPixmap(imatgesDir+'hexagonW.png'))
        self.layIMGS2.addWidget(self.img6)
        radio8 = QRadioButton()

        def fradio8():
            parent.symbol = 'cross'
        radio8.toggled.connect(fradio8)
        self.layIMGS2.addWidget(radio8)
        self.img8 = QLabel()
        self.img8.setPixmap(QPixmap(imatgesDir+'crossW.png'))
        self.layIMGS2.addWidget(self.img8)
        self.layIMGS1.setSpacing(25)
        self.layIMGS2.setSpacing(25)
        layoutGB = QVBoxLayout()
        layoutGB.addLayout(self.layIMGS1)
        layoutGB.addLayout(self.layIMGS2)
        self.groupBox.setLayout(layoutGB)
        self.layCB = QVBoxLayout()
        self.layCB.addWidget(self.lblSimbol)
        self.layCB.addWidget(self.groupBox)
        self.layCB.setSpacing(8)
        self.layout.addLayout(self.layCB)

        #symbol = QgsMarkerSymbol.createSimple({'name': 'square', 'color': 'red'})
        # layer.renderer().setSymbol(symbol)
        # https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#modify-features

    def nextId(self):
        return -1


class QvtLectorCsv(QvLectorCsv):
    def __init__(self, csvName: str, csv: io.TextIOBase=None, separador: str=None, completa: bool=False, guardar: bool=False, parent: QWidget=None):
        super().__init__(csvName, guardar)
        self.separador = separador
        self.fname=csvName
        if self.separador is not None:
            if csv is None: #És el nom de l'arxiu
                self.carregaCsv(csvName, self.separador, completa)
            else: #És l'arxiu
                self.carregaCsvFile(csv, csvName,self.separador,completa)
    
    

    


def infereixSeparadorRegex(arxiu):
    '''Infereix el separador d'un arxiu csv
    Arguments:
        arxiu{str} -- El nom de l'arxiu del qual volem inferir el separador
    Returns:
        separador{str} -- El separador inferit
    '''
    import re

    def eliminaRep(lst):
        '''Rep una llista i la retorna sense repeticions'''
        return list(set(lst))

    def eliminaRepOrd(lst):
        '''Rep una llista i la retorna sense repeticions i ordenada'''
        return sorted(set(lst))

    # Utilitzant expressions regulars
    # Un substring serà tot allò que comenci per ", i acabi amb ", sense contenir-ne cap a dins, de manera que ens ho carreguem
    # Un nombre serà [0-9]+, cosa que també ens carreguem

    def infereixSeparadorLinia(line):
        aux = re.sub('"[^"]*"', '', line)
        aux = re.sub('[0-9]+', '', aux)
        aux = re.sub('[a-zA-Z]*', '', aux)
        aux = aux.replace('\n', '')  # Per si tenim salt de línia al final
        auxSenseRep = eliminaRepOrd(aux)  # Eliminem repeticions
        if len(auxSenseRep) == 1:
            return aux[0]
        # Creem una llista de tuples ordenada, on cada tupla conté el nombre d'aparicions del caracter i el caracter
        lst = sorted(map(lambda x: (aux.count(x), x), auxSenseRep))
        return lst

    def uneixLlistesAp(lst1, lst2):
        return list(set(lst1) & set(lst2))
    lst = []
    for x in arxiu.readlines(1000):
        act = infereixSeparadorLinia(x)
        if isinstance(act, str):
            arxiu.seek(0)
            return act
        if len(lst) == 0:
            lst = act  # Primera iteració
        else:
            lst = uneixLlistesAp(lst, act)
        if len(lst) == 1:
            arxiu.seek(0)
            return lst[0][1]
    arxiu.seek(0)
    return [y for x, y in lst]


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setFont(QvConstants.FONTTEXT)
    wizard = QvCarregaCsv(
        'U:\\QUOTA\\Comu_imi\\Becaris\\XX22 per geocodificar correcció.csv', print)
    #wizard = QvCarregaCsv('U:\\QUOTA\\Comu_imi\\Becaris\\gossos.csv', print)
    wizard.show()
    sys.exit(app.exec_())
