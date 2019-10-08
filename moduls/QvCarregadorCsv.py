from moduls.QvImports import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from typing import Callable
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvLectorCsv import QvLectorCsv
from moduls.QvGeocod import QvGeocod
from enum import IntEnum
import csv
import io
import chardet
import tempfile
from pathlib import Path

finestres = IntEnum('finestres', 'Precalculat TriaSep TriaGeom CampsXY Adreca GeneraCoords Personalitza')

class QvCarregaCsv(QDialog):
    def __init__(self,rutaCsv: str, funcioCarregar: Callable[[str,str,str,str],None],parent:QWidget= None):
        super().__init__(parent)
        self._separador=';'
        self.numeroLinies=-1
        self.setWindowFlag(Qt.FramelessWindowHint)

        #Si geocodifiquem tindrem dos csv. L'original, que és el primer que ens han passat, i el geocodificat
        self.setCsv(rutaCsv)
        self._csvOrig=self._csv
        self.funcioCarregar=funcioCarregar
        self.widgetSup = QWidget(objectName='layout')
        self.layoutGran=QVBoxLayout()
        self.setLayout(self.layoutGran)
        self.layout=QVBoxLayout()
        self.layoutGran.addWidget(self.widgetSup)
        self.layoutGran.addLayout(self.layout)
        self.layoutGran.setContentsMargins(0,0,0,0)
        self.layoutGran.setSpacing(0)

        self.finestres=[x(self) for x in (CsvPrefab,CsvTriaSeparador, CsvTriaGeom ,CsvXY, CsvAdreca, CsvGeneraCoords, CsvPersonalitza)]
        for x in self.finestres: x.hide() #Ocultem totes les finestres que no volem mostrar
        self.widgetActual=self.finestres[1]
        self.formata()
        self.oldPos=self.pos()
    def formata(self):
        self.setMinimumSize(640,400)
        # self.setStyleSheet('QWidget{background: solid white}')

        #Capçalera
        self.layoutCapcalera = QHBoxLayout()
        self.widgetSup.setLayout(self.layoutCapcalera)
        self.layout.addWidget(self.widgetSup)
        self.lblCapcalera = QLabel(objectName='Fosca')
        self.lblCapcalera.setText('  Carregador de csv')
        self.lblLogo = QLabel()
        self.lblLogo.setPixmap(
            QPixmap('imatges/QVistaLogo_40_32.png'))
        self.layoutCapcalera.addWidget(self.lblLogo)
        self.layoutCapcalera.addWidget(self.lblCapcalera)
        self.lblLogo.setFixedSize(40,40)
        self.lblCapcalera.setStyleSheet('background-color: %s; color: %s; border: 0px' % (
            QvConstants.COLORFOSCHTML, QvConstants.COLORBLANCHTML))
        self.lblCapcalera.setFont(QvConstants.FONTCAPCALERES)
        self.lblCapcalera.setFixedHeight(40)
        self.layoutCapcalera.setContentsMargins(0, 0, 0, 0)
        self.layoutCapcalera.setSpacing(0)


        # self.layout.addWidget(QLabel('Carregador de csv'))
        self.layout.addWidget(self.widgetActual)
        self.widgetActual.show()

        self.taula=QvtLectorCsv(self.rutaCsv(),self.csv(),separador=self.separador(),parent=self)
        self.layout.addWidget(self.taula)

        layoutBotons=QHBoxLayout()
        self.next=QvPushButton('Següent',destacat=True,parent=self)
        self.next.clicked.connect(self.seguent)
        self.finalitzar=QvPushButton('Finalitzar',destacat=True,parent=self)
        self.finalitzar.clicked.connect(self.finalitza)
        #TODO: posar-li la funció de finalitzar al botó
        self.ant=QvPushButton('Anterior',parent=self)
        self.ant.clicked.connect(self.anterior)
        self.cancelar=QvPushButton('Cancel·lar',parent=self)
        self.cancelar.clicked.connect(self.close)
        layoutBotons.addWidget(self.ant)
        layoutBotons.addWidget(self.next)
        layoutBotons.addWidget(self.finalitzar)
        layoutBotons.addWidget(self.cancelar)
        self.layout.addLayout(layoutBotons)
        self.actualitzaBotons()
    def recarrega(self):
        '''Diuen que un informàtic és aquella persona que mira als dos costats abans de creuar per un carrer d'un sol sentit
        La comprovació no caldria, però la fem per si de cas'''
        if not hasattr(self,'taula'): return
        self.taula.recarrega(self.separador())
    def actualitzaBotons(self):
        self.ant.setEnabled(self.widgetActual.teAnterior())
        self.next.setEnabled(self.widgetActual.teSeguent())
        self.next.setVisible(not self.widgetActual.esFinal())
        self.finalitzar.setVisible(self.widgetActual.esFinal())
        #TODO: Hauríem de posar un botó de Finalitzar
    
    def salta(self,seg):
        wid=self.widgetActual
        self.widgetActual=self.finestres[seg-1]
        self.layout.replaceWidget(wid,self.widgetActual)
        wid.hide()
        self.actualitzaBotons()
        self.widgetActual.show()
        self.update()
    def seguent(self):
        #TODO: Posar comprovacions prèvies al pas a la següent pantalla
        self.salta(self.widgetActual.seguent())
    def finalitza(self):
        self.funcioCarregar(self.rutaCsv(),self.separador(),self.coordX,self.coordY,self.proj,self.titol,self.color,self.forma)
        self.close()
    def anterior(self):
        self.salta(self.widgetActual.anterior())
    def rutaCsv(self):
        return self._rutaCsv
    def csv(self):
        self._csv.seek(0)
        return self._csv
    def rutaCsvOrig(self):
        return self._rutaCsvOrig
    def csvOrig(self):
        self._csvOrig.seek(0)
        return self._csvOrig
    def setCsv(self,ruta):
        self._rutaCsv=ruta
        encoding=self.getCodificacio(ruta)
        self._csv=io.open(self._rutaCsv,encoding=encoding)
        if hasattr(self,'taula'): self.taula.carregaCsv(self.rutaCsv(),self.csv(),separador=self.separador())
        self.recarrega()
    def setSeparador(self,sep):
        self._separador=sep
        self.recarrega()
    def setDadesAdreca(self,tipusVia,via,numI,numF,lletraI,lletraF):
        if tipusVia=='': tipusVia=None
        if via=='': via=None
        if numI=='': numI=None 
        if numF=='': numF=None 
        if lletraI=='': lletraI=None 
        if lletraF=='': lletraF=None
        self.dades=(tipusVia,via,numI,numF,lletraI,lletraF)
        print(self.dades)
    def getDadesAdreca(self):
        return self.dades
    def separador(self):
        return self._separador
    def setCoordenades(self,x,y,proj):
        print(x,y,proj)
        self.coordX=x
        self.coordY=y
        self.proj=proj

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
                self.seguent()
    def close(self):
        self.funcioCarregar(self.coordX,self.coordY,self.proj,'Hola')
        super().close()
    def obteCamps(self):
        return csv.DictReader(self.csv(),delimiter=self.separador()).fieldnames
    def getCodificacio(self,path):
        with open(path,'rb') as f:
            string=b''
            i=0
            for line in f.readlines():
                string+=line
                i+=1
                if i==100: break
            return chardet.detect(string)['encoding']
    def setAspecte(self,titol,color,forma):
        self.titol=titol
        self.color=color
        self.forma=forma

        





class CsvPagina(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.layout=QVBoxLayout()
        self.setLayout(self.layout)
    #Les subclasses tindran les següents funcions
    #def teSeguent(self):
    #def seguent(self):
    #def teAnterior(self):
    #def anterior(self):
    def esFinal(self):
        return False
    def rutaCsv(self):
        return self.parentWidget().rutaCsv()
    def csv(self):
        return self.parentWidget().csv()
    def rutaCsvOrig(self):
        return self.parentWidget().rutaCsvOrig()
    def csvOrig(self):
        return self.parentWidget().csvOrig()
    pass

class CsvPrefab(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        lbl=QLabel(type(self).__name__)
        self.layout.addWidget(lbl)


class CsvTriaSeparador(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        #self.layout.addWidget(QLabel('Tria del separador'))
        descripcio=QLabel("Trieu quin és el separador utilitzat per l'arxiu que voleu carregar")
        descripcio.setWordWrap(True)
        self.layout.addWidget(descripcio)

        laySep=QHBoxLayout()
        laySep.addWidget(QLabel('Introdueixi el separador utilitzat '))
        self.cbSeparadors=QComboBox(self)
        laySep.addWidget(self.cbSeparadors)
        self.layout.addLayout(laySep)
        self.cbSeparadors.addItems([';',',','.',':','|'])
        separadors={';':0,',':1,'.':2,':':3,'|':4}
        self.cbSeparadors.currentTextChanged.connect(self.parentWidget().setSeparador)
        self.cbSeparadors.setCurrentIndex(separadors[self.infereixSeparadorRegex(self.csv())])
        self.parentWidget().setSeparador(self.cbSeparadors.currentText())
    def teSeguent(self):
        return True
    def seguent(self):
        return finestres.TriaGeom
    def teAnterior(self):
        return False
    def anterior(self):
        #Es retorna a ell mateix, ja que no hi ha finestra anterior
        return finestres.TriaSep
    def infereixSeparadorRegex(self,arxiu):
        '''Infereix el separador d'un arxiu csv
        Arguments:
            arxiu{File} -- L'arxiu del qual volem inferir el separador
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

class CsvTriaGeom(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        lbl=QLabel('De quins camps obtenim les coordenades?')
        self.cbXY=QRadioButton('Camps de coordenades X Y')
        self.cbXY.toggled.connect(self.parentWidget().actualitzaBotons)
        self.cbAdreca=QRadioButton('Adreces postals')
        self.cbAdreca.toggled.connect(self.parentWidget().actualitzaBotons)
        self.layout.addWidget(lbl)
        self.layout.addWidget(self.cbXY)
        self.layout.addWidget(self.cbAdreca)
    def teSeguent(self):
        #Mirar si ha seleccionat alguna cosa
        return self.cbXY.isChecked() or self.cbAdreca.isChecked()
    def seguent(self):
        return finestres.CampsXY if self.cbXY.isChecked() else finestres.Adreca
    def teAnterior(self):
        return True
    def anterior(self):
        return finestres.TriaSep

class CsvXY(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        lay1=QHBoxLayout()
        lay1.addWidget(QLabel('Camp de coordenada X'))
        self.cbX=QComboBox()#camps
        lay1.addWidget(self.cbX)
        lay2=QHBoxLayout()
        lay2.addWidget(QLabel('Camp de coordenada Y'))
        self.cbY=QComboBox()#camps
        lay2.addWidget(self.cbY)
        lay3=QHBoxLayout()
        lay3.addWidget(QLabel('Projecció usada:'))
        self.proj={'EPSG:25831 UTM ETRS89 31N': 25831,
                   'EPSG:3857 Pseudo Mercator (Google)': 3857,
                   'EPSG:4326 WGS 84': 4326,
                   'EPSG:23031 ED50 31N': 23031}
        self.cbProj=QComboBox()
        self.cbProj.addItems(self.proj.keys())
        lay3.addWidget(self.cbProj)
        
        self.layout.addLayout(lay1)
        self.layout.addLayout(lay2)
        self.layout.addLayout(lay3)
    def show(self):
        camps=self.parentWidget().obteCamps()
        self.cbX.clear()
        self.cbY.clear()
        self.cbX.addItems(camps)
        self.cbY.addItems(camps)
        super().show()
    def hide(self):
        super().hide()
        self.parentWidget().setCoordenades(self.cbX.currentText(),self.cbY.currentText(),self.proj[self.cbProj.currentText()])
    def teSeguent(self):
        return True
    def seguent(self):
        return finestres.Personalitza
    def teAnterior(self):
        return True
    def anterior(self):
        return finestres.TriaGeom
    pass

class CsvAdreca(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        MIDACOMBOBOX=100
        camps=self.parentWidget().obteCamps()
        self.lblTipus = QLabel('Tipus Via')
        self.cbTipus = QComboBox()
        self.cbTipus.setFixedWidth(MIDACOMBOBOX)
        self.cbTipus.addItems(['']+camps)
        # self.cbTipus.currentIndexChanged.connect(actualitzaUI)
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
        self.layout.addLayout(layAdrecaTipus)
        self.layout.addLayout(self.layoutNumLletraAux)
    def teSeguent(self):
        return True
    def seguent(self):
        self.parentWidget().setDadesAdreca(*[x.currentText() for x in (self.cbTipus,self.cbCarrer,self.cbNumIni,self.cbNumFi,self.cbLletraIni,self.cbLletraFi)])
        return finestres.GeneraCoords
    def teAnterior(self):
        return True
    def anterior(self):
        return finestres.TriaGeom
    

class CsvGeneraCoords(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        lbl=QLabel(type(self).__name__)
        self.layout.addWidget(lbl)
        self.seg=False
    def teAnterior(self):
        return True
    def anterior(self):
        pass
    def teSeguent(self):
        return self.seg
    def seguent(self):
        self.parentWidget().setCsv(self.nouCsv)
        return finestres.Personalitza
    def show(self):
        super().show()
        self.parentWidget().setCoordenades('XCalculadaqVista','YCalculadaqVista',25831)
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
            else:
                nomVia=nomComplet
            return tipusVia[:-1], nomVia, num

        def calculaNumLinies(arxiu):
            with tempfile.NamedTemporaryFile(mode='w') as auxiliar:
                count=0
                for x in arxiu.readlines():
                    if count!=0:
                        if count>=100: break
                        auxiliar.write(x)
                    count+=1
                if count<100: return count-1
                auxiliar.flush()
                return 100*os.path.getsize(arxiu.name)/os.path.getsize(auxiliar.name) 
        def adreca(fila):
            tipusVia, via, numI, numF, lletraI, lletraF=self.parentWidget().getDadesAdreca()
            if tipusVia is None or numI is None:
                tv, via, num = splitCarrer(fila[via])
                tpv=fila[tipusVia] if tipusVia is not None else tv
                numIni=fila[numI] if numI is not None else num
            else:
                tpv=fila[tipusVia]
                via=fila[via]
                numIni=fila[numI]
            numFi=fila[numF] if numF is not None else ''
            lletraIni=fila[lletraI] if lletraI is not None else ''
            lletraFi=fila[lletraF] if lletraF is not None else ''
            return tpv,via,numIni,lletraIni,numFi,lletraFi

        mida=calculaNumLinies(self.parentWidget().csv())
        wpb=WindowProgressBar(mida,self)
        self.layout.addWidget(wpb)
        arxiuCsv=self.parentWidget().csv()
        reader=csv.DictReader(arxiuCsv,delimiter=self.parentWidget().separador())
        with open(tempdir+str(time.time())+'.csv','w',newline='') as nouCsv:
            writer=csv.DictWriter(nouCsv,fieldnames=reader.fieldnames+['XCalculadaqVista','YCalculadaqVista'],delimiter=self.parentWidget().separador())
            writer.writeheader()
            for row in reader:
                x, y = QvGeocod.coordsCarrerNum(*adreca(row))
                row['XCalculadaqVista']=x
                row['YCalculadaqVista']=y
                writer.writerow(row)
                wpb.seg()
                qApp.processEvents()
            wpb.fi()
            self.nouCsv=nouCsv.name
            self.seg=True
            self.parentWidget().actualitzaBotons()

    pass

class CsvPersonalitza(CsvPagina):
    def __init__(self,parent):
        super().__init__(parent)
        layNom=QHBoxLayout()
        layNom.addWidget(QLabel('Nom de la capa: '))
        self.leNom=QLineEdit(self)
        self.leNom.textChanged.connect(self.actualitzaDades)
        layNom.addWidget(self.leNom)
        self.layout.addLayout(layNom)
        layColor=QHBoxLayout()
        layColor.addWidget(QLabel('Trieu el color'))
        bColor = QPushButton()
        def canvicolor(dcolor):
            self.color = dcolor.name()
            bColor.setStyleSheet("background-color: %s;" % self.color)
            self.actualitzaDades()
        def openColorDialog():
            dcolor = QColorDialog().getColor()
            canvicolor(dcolor)
        self.color='white'
        bColor.clicked.connect(openColorDialog)
        layColor.addWidget(bColor)
        self.layout.addLayout(layColor)
        #la resta del codi
        self.actualitzaDades()

    def teAnterior(self):
        return False
    def anterior(self):
        return finestres.Personalitza
    def teSeguent(self):
        return False
    def seguent(self):
        return finestres.Personalitza
    def esFinal(self):
        return True
    def actualitzaDades(self):
        self.parentWidget().setAspecte(self.leNom.text(),self.color,'circle')
    pass

class QvtLectorCsv(QvLectorCsv):
    def __init__(self, csvName: str, csv: io.TextIOBase=None, separador: str=';', completa: bool=False, guardar: bool=False, parent: QWidget=None):
        super().__init__(csvName, guardar=guardar)
        self.separador = separador
        self.fname=csvName
        if self.separador is not None:
            if csv is None: #És el nom de l'arxiu
                self.carregaCsv(csvName, self.separador, completa)
            else: #És l'arxiu
                self.carregaCsvFile(csv, csvName,self.separador,completa)

class WindowProgressBar(QWidget):
    def __init__(self, mida: int, parent: QWidget=None):
        super().__init__(parent)
        self.setWindowTitle("Progrés")
        self.progress = QProgressBar()
        self.progress.setGeometry(0, 0, 300, 25)
        self.mida = mida
        self.salt = int(self.mida/20) if self.mida>100 else 1 #Saltarem cada 1%
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
        # self.bCancelar = QvPushButton('Cancel·lar', destacat = False)
        # self.layCancelar = QHBoxLayout()
        # self.layCancelar.setAlignment(Qt.AlignRight)
        # self.layProgressW.addLayout(self.layCancelar)
        # self.layCancelar.addWidget(self.bCancelar)
        # self.bCancelar.clicked.connect(self.cancelar)
        # self.cancelat = False

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
    def seg(self):
        self.count+=1
        print(self.count, self.mida)
        if self.count%self.salt==0:
            self.progress.setValue(self.count)
            self.actualitzaLBL()
            self.update()
            qApp.processEvents()
    def fi(self):
        self.count=self.mida
        self.actualitzaLBL()
        self.progress.setValue(self.count)
        qApp.processEvents()
    def cancelar(self):
        self.cancelat = True
 

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setFont(QvConstants.FONTTEXT)
    wizard = QvCarregaCsv(
        'C:\\Users\\omarti\\Documents\\qVista\\codi\\Dades\\Tipusvia.csv', print)
    #wizard = QvCarregaCsv('U:\\QUOTA\\Comu_imi\\Becaris\\gossos.csv', print)
    wizard.show()
    sys.exit(app.exec_())