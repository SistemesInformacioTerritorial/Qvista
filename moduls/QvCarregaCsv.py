from moduls.QvImports import *
from enum import IntEnum
from moduls.QvLectorCsv import QvLectorCsv
import qVista
import tempfile
from QvGeocod import QvGeocod
from QvConstants import QvConstants
from QvPushButton import QvPushButton
import re


class QvCarregaCsv(QWizard):
    finestres = IntEnum(
        'finestres', 'TriaSep TriaSepDec TriaGeom CampsXY Adreca GeneraCoords')

    def __init__(self, csv: str, carregar, parent: QWidget = None):
        '''Crea un assistent de càrrega de csv
        Arguments:
            csv{str} -- Nom de l'arxiu a carregar
            carregar{ (str,str,str,str,nomCapa: str) -> None } -- Funció que rep, per ordre, nom del csv, nom del separador, nom de la coordenada X, nom de la coordenada Y i nom de la capa, i carrega l'arxiu
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.carregar = carregar
        self.csv = csv
        self.formata()
        self.setPage(QvCarregaCsv.finestres.TriaSep, QvCarregaCsvTriaSep(self))
        self.setPage(QvCarregaCsv.finestres.TriaSepDec,
                     QvCarregaCsvTriaSepDec(self))
        self.setPage(QvCarregaCsv.finestres.TriaGeom,
                     QvCarregaCsvTriaGeom(self))
        self.setPage(QvCarregaCsv.finestres.CampsXY, QvCarregaCsvXY(self))
        self.setPage(QvCarregaCsv.finestres.Adreca, QvCarregaCsvAdreca(self))
        self.setPage(QvCarregaCsv.finestres.GeneraCoords,
                     QvCarregaCsvGeneraCoords(self))

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
        self.setButton(QvCarregaCsv.CommitButton,self.commitButton)

        self.setFixedWidth(500)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setStyleSheet('''
            background-color: %s;
            color: %s;
            QWidget {border: 0px} 
            QFrame {border: 0px} 
            QLabel {border: 0px}
            QRadioButton {background-color: transparent}
            ''' % (QvConstants.COLORBLANCHTML, QvConstants.COLORFOSCHTML))
        self.setPixmap(QWizard.LogoPixmap, QPixmap('imatges/layers.png'))
        self.oldPos = self.pos()
        self.setFont(QvConstants.FONTTEXT)

    def accept(self):
        super().accept()
        self.carregar(self.csv, self.separador,
                      self.coordX, self.coordY, 'Hola')

    # Aquestes funcions seran cridades NOMÉS des de les pàgines
    def setSeparador(self, sep):
        self.separador = sep

    def setCoordX(self, coordX):
        self.coordX = coordX

    def setCoordY(self, coordY):
        self.coordY = coordY

    def setProjecció(self, proj):
        self.proj = proj

    def setNomCapa(self, nomCapa):
        self.nomCapa = nomCapa

    def setNomCsv(self, csv):
        if not hasattr(self, 'csv'):
            self.csvOrig = self.csv
        self.csv = csv

    def setDadesAdreca(self, tipusVia, via, numIni, lletraIni, numFi, lletraFi):
        self.dadesAdreca = (tipusVia, via, numIni, lletraIni, numFi, lletraFi)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        # print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.segButton.isEnabled():
                self.next()


class QvCarregaCsvPage(QWizardPage):
    def __init__(self, parent: QWidget = None):
        '''Crea una pàgina de l'assistent de càrrega de csv
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.parent = parent
        self.setTitle('Assistent de càrrega de csv')
        self.setSubTitle('Subtítol de prova)')
        self.formata()

    def formata(self):
        self.setStyleSheet('''background-color: %s; 
                              QFrame {border: 0px} 
                              QLabel {border: 0px}
                              ''' % QvConstants.COLORBLANCHTML)

        self.setContentsMargins(0, 0, 0, 0)

    def mostraTaula(self, completa=False):
        '''Mostra la taula provisional que està carregant
        Keyword Arguments:
            completa{bool} -- Indica si volem mostrar la taula completa.
                Si és false, mostra una previsualització de 10 elements 
                (default: {False})
        '''
        self.table = QvtLectorCsv(
            self.parent.csv, self.parent.separador, completa, self)
        self.table.verticalScrollBar().setStyleSheet(QvConstants.SCROLLBARSTYLESHEET)
        self.table.horizontalScrollBar().setStyleSheet(QvConstants.SCROLLBARSTYLESHEET)
        self.layoutTable = QVBoxLayout()
        self.layout.addLayout(self.layoutTable)
        self.layoutTable.addWidget(self.table)

    def recarregaTaula(self, completa=False):
        self.table = QvtLectorCsv(
            self.parent.csv, self.parent.separador, completa, self)

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'table'):
            self.table.recarrega(self.parent.separador)

    def obteCamps(self):
        return csv.DictReader(open(self.parent.csv), delimiter=self.parent.separador).fieldnames
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

    def setTitle(self, title):
        s = '<p><span style="color: #38474f;"><strong><span style="font-family: arial, helvetica, sans-serif; font-size: 12pt;">%s</span></strong></span></p>' % title
        super().setTitle(s)

    def setSubTitle(self, subtitle):
        s = '<p><span style="color: #38474f; font-size: 10pt;"><strong><span style="font-family: arial, helvetica, sans-serif;">%s</span></strong></span></p>' % subtitle
        super().setSubTitle(s)


class QvCarregaCsvTriaSep(QvCarregaCsvPage):
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar el separador d'aquest
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.setSubTitle('Tria del separador de camps')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio1 = QLabel(
            "Escull quin separador fa servir l'arxiu CVS que vols carregar:")
        self.layout.addWidget(self.lblExplicacio1)
        self.setLayout(self.layout)
        self.layoutCheckButton = QHBoxLayout(self)
        self.layout.addLayout(self.layoutCheckButton)
        self.lblSep = QLabel()
        self.lblSep.setText("Separador:")
        self.cbSep = QComboBox()
        QvConstants.formataScrollbar(self.cbSep.view().verticalScrollBar())
        llistaSeparadors = [';', ',', '.', ':', '|']
        self.cbSep.addItems(llistaSeparadors)
        self.layoutCheckButton.addWidget(self.lblSep)
        self.layoutCheckButton.addWidget(self.cbSep)
        print(parent.csv)
        self.parent.setSeparador(infereixSeparadorRegex(open(parent.csv)))
        self.mostraTaula()

        def botoClickat(boto):
            self.parent.setSeparador(self.cbSep.currentText())
            self.table.recarrega(self.parent.separador)
        self.cbSep.activated.connect(botoClickat)
        index = llistaSeparadors.index(self.parent.separador)
        self.cbSep.setCurrentIndex(index)


class QvCarregaCsvTriaSepDec(QvCarregaCsvPage):
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar el separador decimal
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.setSubTitle('Tria del separador dels decimals')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio2 = QLabel(
            "Escull quin separador es fa servir per als decimals:")
        self.layout.addWidget(self.lblExplicacio2)
        self.layoutCheckButton = QHBoxLayout()
        self.layout.addLayout(self.layoutCheckButton)
        self.lblSepDec = QLabel()
        self.lblSepDec.setText("Separador Decimal:")
        self.cbSepDec = QComboBox()
        QvConstants.formataScrollbar(self.cbSepDec.view().verticalScrollBar())
        llistaSeparadorsDecimals = ['.', ',']
        self.cbSepDec.addItems(llistaSeparadorsDecimals)
        self.layoutCheckButton.addWidget(self.lblSepDec)
        self.layoutCheckButton.addWidget(self.cbSepDec)
        self.mostraTaula()

    pass

# La classe per triar si definim la geometria amb coordenades X Y, o bé amb una adreça


class QvCarregaCsvTriaGeom(QvCarregaCsvPage):
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar-ne la geometria
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.setSubTitle('Tria del tipus de la geometria')
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio3 = QLabel(
            "Hi ha 2 camps del CSV que contenen les coordenades X i Y a processar \no s'han d'inferir a partir d'una adreça?")
        self.layout.addWidget(self.lblExplicacio3)
        self.botoXY = QRadioButton('Coordenades X Y')
        self.botoAdreca = QRadioButton('Adreça')
        self.layoutBotons = QHBoxLayout()
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
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar els camps de les coordenades X Y
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layoutCoord = QHBoxLayout()
        self.layout.addLayout(self.layoutCoord)
        self.parent.llistaCamps = self.obteCamps()
        print(self.parent.llistaCamps)
        self.cbX = QComboBox()
        QvConstants.formataScrollbar(self.cbX.view().verticalScrollBar())
        self.cbX.addItems(self.parent.llistaCamps)
        self.cbY = QComboBox()
        QvConstants.formataScrollbar(self.cbY.view().verticalScrollBar())
        self.cbY.addItems(self.parent.llistaCamps)
        self.layoutCoord.addWidget(self.cbX)
        self.layoutCoord.addWidget(self.cbY)
        self.cbProj = QComboBox()
        QvConstants.formataScrollbar(self.cbProj.view().verticalScrollBar())
        projeccions = [25831, 1, 2, 3]
        self.cbProj.clear()
        self.cbProj.addItems([str(x) for x in projeccions])
        self.layout.addWidget(self.cbProj)

        def xChanged():
            self.parent.setCoordX(self.cbX.currentText())

        def yChanged():
            self.parent.setCoordY(self.cbY.currentText())

        def projChanged():
            self.parent.setProjeccio(self.cbProj.currentText())
        self.cbX.currentIndexChanged.connect(xChanged)
        self.cbY.currentIndexChanged.connect(yChanged)
        self.cbProj.currentIndexChanged.connect(projChanged)

        self.setFinalPage(True)
        self.mostraTaula()

    def nextId(self):
        return -1  # No hi ha pàgina següent


class QvCarregaCsvAdreca(QvCarregaCsvPage):
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que permet triar els camps de l'adreça
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.setSubTitle('Tria dels components de la geometria')
        self.layout = QVBoxLayout(self)
        self.layoutAdreca = QVBoxLayout()
        self.layout.addLayout(self.layoutAdreca)
        camps = self.obteCamps()
        self.lblTipus = QLabel('Tipus Via')
        self.cbTipus = QComboBox()
        QvConstants.formataScrollbar(self.cbTipus.view().verticalScrollBar())
        self.cbTipus.addItems(['']+camps)
        self.lblCarrer = QLabel('Via')
        self.cbCarrer = QComboBox()
        QvConstants.formataScrollbar(self.cbCarrer.view().verticalScrollBar())
        self.cbCarrer.addItems(camps)
        self.lblNumIni = QLabel('Nº post. inicial')
        self.cbNumIni = QComboBox()
        QvConstants.formataScrollbar(self.cbNumIni.view().verticalScrollBar())
        self.cbNumIni.addItems(['']+camps)
        self.lblLletraIni = QLabel('Lletra inicial')
        self.cbLletraIni = QComboBox()
        QvConstants.formataScrollbar(
            self.cbLletraIni.view().verticalScrollBar())
        self.cbLletraIni.addItems(['']+camps)
        self.lblNumFi = QLabel('Nº post. final  ')
        self.cbNumFi = QComboBox()
        QvConstants.formataScrollbar(self.cbNumFi.view().verticalScrollBar())
        self.cbNumFi.addItems(['']+camps)
        self.lblLletraFi = QLabel('Lletra final  ')
        self.cbLletraFi = QComboBox()
        QvConstants.formataScrollbar(
            self.cbLletraFi.view().verticalScrollBar())
        self.cbLletraFi.addItems(['']+camps)

        self.layoutCarrer = QHBoxLayout()
        self.layoutTipus = QHBoxLayout()
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

        self.layoutAdreca.addLayout(self.layoutTipus)
        self.layoutAdreca.addLayout(self.layoutCarrer)
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
        self.setCommitPage(True)

        self.mostraTaula()

    def nextId(self):
        return QvCarregaCsv.finestres.GeneraCoords


class WindowProgressBar(QWidget):
    def __init__(self, mida, parent=None):
        super().__init__(parent)
        self.progress = QProgressBar()
        self.progress.setGeometry(0, 0, 300, 25)
        self.mida = mida
        self.progress.setMaximum(mida)
        self.count = 0  # necessari per a la progress bar
        self.progress.setValue(self.count)
        self.layProgressW = QVBoxLayout()
        self.lblAdrInfo = QLabel()
        self.lblAdrInfo.setText("Adreces Processades: 0")
        self.layProgressW.addWidget(self.progress)
        self.layProgressW.addWidget(self.lblAdrInfo)
        self.setLayout(self.layProgressW)

    def actualitzaLBL(self):
        self.lblAdrInfo.setText(
            "Adreces Processades: %i de %i" % (self.count, self.mida))


class QvCarregaCsvGeneraCoords(QvCarregaCsvPage):
    def __init__(self, parent=None):
        '''Crea una pàgina de l'assistent de càrrega de csv que genera les coordenades a partir d'una adreça
        Keyword Arguments:
            parent{QWidget} -- Pare de l'assistent (default{None})
        '''
        super().__init__(parent)
        self.parent.coordX = 'XCalculadaqVista'
        self.parent.coordY = 'YCalculadaqVista'
        self.lblAdrecesError = QLabel()
        self.lblAdrecesError.setText("")
        self.lblAdrecesError.setStyleSheet('color: red')
        # self.lblAdrecesError.setFixedHeight(100)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.lblExplicacio4 = QLabel()
        self.lblExplicacio4.setText(
            "Aquestes són les adreces que no s'han pogut geolocalitzar:")
        self.layout.addWidget(self.lblExplicacio4)
        self.scrollErrors = QScrollArea()
        self.scrollErrors.setWidgetResizable(True)
        self.scrollErrors.verticalScrollBar().setStyleSheet(
            QvConstants.SCROLLBARSTYLESHEET)
        self.lblAdrecesError.setContentsMargins(10, 5, 10, 5)
        self.scrollErrors.setWidget(self.lblAdrecesError)
        self.layout.addWidget(self.scrollErrors)
        # Després de generar el csv amb coordenades no hi ha volta enrere
        self.setCommitPage(True)
        self.showed = False

    #def showEvent(self, event):
    def initializePage(self):
        def splitCarrer(nomComplet):
            if not hasattr(self, 'TIPUSVIES'):
                with open('U:/QUOTA/Comu_imi/Becaris/Tipusvia.csv') as csvfile:
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

        #if not self.showed:
        self.showed = True
        self.mostraTaula(completa=True)
        fileCsv = open(self.parent.csv)
        reader = csv.DictReader(fileCsv, delimiter=self.parent.separador)
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', delete=False) as arxiuNouCsv:
            self.parent.setNomCsv(arxiuNouCsv.name)
            mida = len(list(reader))-1
            fileCsv.seek(0)

            wpg = WindowProgressBar(mida=mida)
            wpg.show()

            self.names = self.parent.llistaCamps + \
                [self.parent.coordX, self.parent.coordY]
            writer = csv.DictWriter(
                arxiuNouCsv, fieldnames=self.names, delimiter=self.parent.separador)
            writer.writeheader()
            i = -1
            for row in reader:
                i += 1
                if i == 0:
                    continue
                print(wpg.count)
                d = {**row}
                d[''] = ''
                if self.parent.dadesAdreca[0] == "":
                    tipusVia, nomVia, num = splitCarrer(
                        row[self.parent.dadesAdreca[1]])

                else:
                    tipusVia = row[self.parent.dadesAdreca[0]]
                    nomVia = row[self.parent.dadesAdreca[1]]
                    num = row[self.parent.dadesAdreca[2]]
                    num = re.sub('[^0-9][0-9]*', '', num)

                if num != '':
                    x, y = QvGeocod.coordsCarrerNum(tipusVia, nomVia, num)
                else:
                    x, y = QvGeocod.coordsCarrerNum(
                        tipusVia, nomVia, d[self.parent.dadesAdreca[2]], d[self.parent.dadesAdreca[3]], d[self.parent.dadesAdreca[4]], d[self.parent.dadesAdreca[5]])

                wpg.count = wpg.count + 1
                wpg.actualitzaLBL()
                print(wpg.count)
                wpg.progress.setValue(wpg.count)
                app.processEvents()
                if x is None or y is None:
                    aux = self.lblAdrecesError.text()
                    if aux != "":
                        self.lblAdrecesError.setText(
                            aux + "\n" + tipusVia + " " + nomVia + " " + num)
                    else:
                        self.lblAdrecesError.setText(
                            tipusVia + " " + nomVia + " " + num)
                    print(tipusVia, nomVia, num)
                    d[self.parent.coordX] = ""
                    d[self.parent.coordY] = ""
                    del d[""]
                    writer.writerow(d)
                    continue

                d[self.parent.coordX] = x
                d[self.parent.coordY] = y
                # print(d)
                del d[""]
                writer.writerow(d)
        self.recarregaTaula(completa=True)
        app.processEvents()
    def nextId(self):
        return -1


class QvtLectorCsv(QvLectorCsv):
    def __init__(self, fileName='', separador=None, completa=False, parent=None):
        super().__init__(fileName)
        self.separador = separador
        if self.separador is not None:
            self.carregaCsv(self.fileName, self.separador, completa)

    def carregaCsv(self, fileName, separador=None, completa=False):
        from PyQt5 import QtGui
        if separador is None:
            super().carregaCsv(fileName)
            return
        if fileName:
            f = open(fileName, 'r')
            with f:
                self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
                self.setWindowTitle(self.fname)
                reader = csv.reader(f, delimiter=separador)
                self.model.clear()
                i = 0
                for row in reader:
                    if not completa and i > 9:
                        break  # Per agilitzar la càrrega, només ens cal una preview petita
                    items = [QtGui.QStandardItem(field) for field in row]
                    self.model.appendRow(items)
                    i += 1
                self.tableView.resizeColumnsToContents()

    def recarrega(self, separador):
        self.separador = separador
        self.carregaCsv(self.fileName, self.separador)

    def verticalScrollBar(self):
        return self.tableView.verticalScrollBar()

    def horizontalScrollBar(self):
        return self.tableView.horizontalScrollBar()


def infereixSeparadorRegex(arxiu):
    '''Infereix el separador d'un arxiu csv
    Arguments:
        arxiu{str} -- El nom de l'arxiu del qual volem inferir el separador
    Returns:
        separador{str} -- El separador inferit
    '''
    import re
    # Rep una llista i la retorna sense repeticions

    def eliminaRep(lst):
        return list(set(lst))
    # Rep una llista i la retorna sense repeticions i ordenada

    def eliminaRepOrd(lst):
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
    for x in arxiu.readlines():
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
    wizard=QvCarregaCsv('U:\\QUOTA\\Comu_imi\\Becaris\\XX22 per geocodificar correcció.csv',print)
    #wizard = QvCarregaCsv('U:\\QUOTA\\Comu_imi\\Becaris\\gossos.csv', print)
    wizard.show()
    sys.exit(app.exec_())
