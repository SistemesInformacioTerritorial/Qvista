from moduls.QvImports import * 
from enum import IntEnum
from moduls.QvLectorCsv import QvLectorCsv
import qVista
import tempfile
from QvGeocod import QvGeocod
import re

class QvCarregaCsv(QWizard):
    finestres=IntEnum('finestres','TriaSep TriaSepDec TriaGeom CampsXY Adreca GeneraCoords')
    def __init__(self,csv,parent=None):
        super().__init__(parent)
        #self.separador
        #self.coordX
        #self.coordY
        #self.proj
        #self.nomCapa
        self.csv=csv
        self.setPage(QvCarregaCsv.finestres.TriaSep, QvCarregaCsvTriaSep(self))
        self.setPage(QvCarregaCsv.finestres.TriaSepDec, QvCarregaCsvTriaSepDec(self))
        self.setPage(QvCarregaCsv.finestres.TriaGeom, QvCarregaCsvTriaGeom(self))
        self.setPage(QvCarregaCsv.finestres.CampsXY, QvCarregaCsvXY(self))
        self.setPage(QvCarregaCsv.finestres.Adreca, QvCarregaCsvAdreca(self))
        self.setPage(QvCarregaCsv.finestres.GeneraCoords, QvCarregaCsvGeneraCoords(self))
    def accept(self):
        super().accept()
        qVista.nivellCsv(self.csv, self.separador, self.coordX,self.coordY, nomCapa='Hola')

    
    #Aquestes funcions seran cridades NOMÉS des de les pàgines
    def setSeparador(self,sep):
        self.separador=sep
    def setCoordX(self,coordX):
        self.coordX=coordX
    def setCoordY(self,coordY):
        self.coordY=coordY
    
    def setProjecció(self,proj):
        self.proj=proj
    def setNomCapa(self,nomCapa):
        self.nomCapa=nomCapa
    def setNomCsv(self,csv):
        if not hasattr(self,'csv'):
            self.csvOrig=self.csv
        self.csv=csv
    def setDadesAdreca(self,tipusVia, via, numIni, lletraIni, numFi, lletraFi):
        self.dadesAdreca=(tipusVia, via, numIni, lletraIni, numFi, lletraFi)


        

class QvCarregaCsvPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.setTitle('Assistent de càrrega de CSV')
    def mostraTaula(self, completa=False):
        self.table=QvtLectorCsv(self.parent.csv,self.parent.separador,completa,self)
        self.layoutTable=QVBoxLayout()
        self.layout.addLayout(self.layoutTable)
        self.layoutTable.addWidget(self.table)
    def recarregaTaula(self, completa=False):
        self.table=QvtLectorCsv(self.parent.csv,self.parent.separador,completa,self)
    def showEvent(self,event):
        super().showEvent(event)
        self.table.recarrega(self.parent.separador)
    def obteCamps(self):
        return csv.DictReader(open(self.parent.csv),delimiter=self.parent.separador).fieldnames
        
    #Aquí posarem formats i coses perquè totes les pàgines siguin iguals

class QvCarregaCsvTriaSep(QvCarregaCsvPage):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setSubTitle('Tria del separador de camps')
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layoutCheckButton=QVBoxLayout(self)
        self.layout.addLayout(self.layoutCheckButton)
        self.botons={x:QRadioButton(x) for x in (';',',','.',':','|')}
        for x, y in self.botons.items(): self.layoutCheckButton.addWidget(y)
        print(parent.csv)
        self.parent.setSeparador(infereixSeparadorRegex(open(parent.csv)))
        self.mostraTaula()
        def botoClickat(boto):
            def botoClickatAux():
                self.parent.setSeparador(boto)
                self.table.recarrega(self.parent.separador)
            return botoClickatAux
        for x, y in self.botons.items(): y.toggled.connect(botoClickat(x))
        self.botons[self.parent.separador].setChecked(True)

class QvCarregaCsvTriaSepDec(QvCarregaCsvPage):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setSubTitle('Tria del separador dels decimals')
        self.layout=QVBoxLayout(self)
        textBase='Els nombres tenen aquest aspecte: '
        textPunt=textBase+'105.23  221.5  10000  10003.4'
        textComa=textPunt.replace('.',',')
        self.layoutCheckButton=QVBoxLayout()
        self.layout.addLayout(self.layoutCheckButton)
        self.botoPunt=QRadioButton('.')
        self.botoComa=QRadioButton(',')
        self.layoutCheckButton.addWidget(self.botoPunt)
        self.layoutCheckButton.addWidget(self.botoComa)

        self.label=QLabel()
        self.layout.addWidget(self.label)

        self.botoPunt.toggled.connect(lambda: self.label.setText(textPunt))
        self.botoComa.toggled.connect(lambda: self.label.setText(textComa))
        self.botoPunt.setChecked(True)
        self.mostraTaula()
        

    pass

#La classe per triar si definim la geometria amb coordenades X Y, o bé amb una adreça
class QvCarregaCsvTriaGeom(QvCarregaCsvPage):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout=QVBoxLayout(self)
        self.botoXY=QRadioButton('Coordenades X Y')
        self.botoAdreca=QRadioButton('Adreça')
        self.layout.addWidget(self.botoXY)
        self.layout.addWidget(self.botoAdreca)
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
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout=QVBoxLayout(self)
        self.layoutCoord=QHBoxLayout()
        self.layout.addLayout(self.layoutCoord)
        self.parent.llistaCamps=self.obteCamps()
        print(self.parent.llistaCamps)
        self.cbX=QComboBox()
        self.cbX.addItems(self.parent.llistaCamps)
        self.cbY=QComboBox()
        self.cbY.addItems(self.parent.llistaCamps)
        self.layoutCoord.addWidget(self.cbX)
        self.layoutCoord.addWidget(self.cbY)
        self.cbProj=QComboBox()
        projeccions = [25831, 1 , 2 , 3]
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
        
        self.mostraTaula()

class QvCarregaCsvAdreca(QvCarregaCsvPage):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout=QVBoxLayout(self)
        self.layoutAdreca=QVBoxLayout()
        self.layout.addLayout(self.layoutAdreca)
        camps=self.obteCamps()

        self.layoutTipus=QHBoxLayout()
        self.lblTipus=QLabel('Tipus Via')
        self.cbTipus=QComboBox()
        self.cbTipus.addItems(['']+camps)
        self.layoutTipus.addWidget(self.lblTipus)
        self.layoutTipus.addWidget(self.cbTipus)

        self.layoutCarrer=QHBoxLayout()
        self.lblCarrer=QLabel('Via')
        self.cbCarrer=QComboBox()
        self.cbCarrer.addItems(camps)
        self.layoutCarrer.addWidget(self.lblCarrer)
        self.layoutCarrer.addWidget(self.cbCarrer)

        self.layoutIni=QHBoxLayout()
        self.lblNumIni=QLabel('Número postal inicial')
        self.cbNumIni=QComboBox()
        self.cbNumIni.addItems(['']+camps)
        self.lblLletraIni=QLabel('Lletra Inicial')
        self.cbLletraIni=QComboBox()
        self.cbLletraIni.addItems(['']+camps)
        self.layoutIni.addWidget(self.lblNumIni)
        self.layoutIni.addWidget(self.cbNumIni)
        self.layoutIni.addWidget(self.lblLletraIni)
        self.layoutIni.addWidget(self.cbLletraIni)

        self.layoutFi=QHBoxLayout()
        self.lblNumFi=QLabel('Número postal final')
        self.cbNumFi=QComboBox()
        self.cbNumFi.addItems(['']+camps)
        self.lblLletraFi=QLabel('Lletra final')
        self.cbLletraFi=QComboBox()
        self.cbLletraFi.addItems(['']+camps)
        self.layoutFi.addWidget(self.lblNumFi)
        self.layoutFi.addWidget(self.cbNumFi)
        self.layoutFi.addWidget(self.lblLletraFi)
        self.layoutFi.addWidget(self.cbLletraFi)

        
        

        self.layoutAdreca.addLayout(self.layoutTipus)
        self.layoutAdreca.addLayout(self.layoutCarrer)
        self.layoutAdreca.addLayout(self.layoutIni)
        self.layoutAdreca.addLayout(self.layoutFi)
        def guardaDades():
            #self.parent.setDadesAdreca(self.cbTipus.currentText(), self.cbCarrer.currentText(), self.cbNumIni.currentText(), self.cbLletraIni.currentText(), self.cbNumFi.currentText(), self.cbLletraFi.currentText())
            self.parent.setDadesAdreca(*[x.currentText() for x in (self.cbTipus, self.cbCarrer,self.cbNumIni,self.cbLletraIni, self.cbNumFi, self.cbLletraFi)])
        
        self.cbTipus.currentIndexChanged.connect(guardaDades)
        self.cbCarrer.currentIndexChanged.connect(guardaDades)
        self.cbNumIni.currentIndexChanged.connect(guardaDades)
        self.cbLletraIni.currentIndexChanged.connect(guardaDades)
        self.cbNumFi.currentIndexChanged.connect(guardaDades)
        self.cbLletraFi.currentIndexChanged.connect(guardaDades)
        guardaDades()

        self.mostraTaula()
    def nextId(self):
        return QvCarregaCsv.finestres.GeneraCoords

class QvCarregaCsvGeneraCoords(QvCarregaCsvPage):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.progress=QProgressBar()
        self.parent.coordX='XCalculadaqVista'
        self.parent.coordY='YCalculadaqVista'
        self.lblAdrecesError = QLabel()
        self.lblAdrecesError.setText("")
        self.lblAdrecesError.setStyleSheet('color: red')
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.lblAdrecesError)
        self.lblAdrecesError.setText('Hola')
        self.mostraTaula()


    def splitCarrer(nomComplet):
        if not hasattr(QvCarregaCsvGeneraCoords.splitCarrer,'TIPUSVIES'):
            with open('U:/QUOTA/Comu_imi/Becaris/Tipusvia.csv') as csvfile:
                    reader=csv.reader(csvfile, delimiter=';')
                    QvCarregaCsvGeneraCoords.splitCarrer.TIPUSVIES=[y+' ' for x in reader for y in x]
                    QvCarregaCsvGeneraCoords.splitCarrer.TIPUSVIES=list(set(QvCarregaCsvGeneraCoords.splitCarrer.TIPUSVIES))
        tipusVia=''
        nomVia=''
        num=''
        for x in QvCarregaCsvGeneraCoords.splitCarrer.TIPUSVIES:
            if nomComplet.startswith(x):
                tipusVia=x
                #Eliminem el tipus de via i l'espai
                nomComplet=nomComplet[len(x):]
        if ','  in nomComplet:
            subs=nomComplet.split(', ')
            nomVia=subs[0]
            #num=re.findall('^[0-9]*((\-[0-9]*)|)',subs[1])[0]
            print(subs)
            num=re.findall('^[0-9]*',subs[1])[0]
        return tipusVia[:-1], nomVia, num

    #def showEvent(self,event):
    #    super().showEvent(event)
    def show(self):
        super().show()
        self.mostraTaula()
        fileCsv=open(self.parent.csv)
        reader=csv.DictReader(fileCsv, delimiter=self.parent.separador)
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+',delete=False) as arxiuNouCsv:
            self.parent.setNomCsv(arxiuNouCsv.name)
            mida=len(list(reader))-1
            fileCsv.seek(0)
            self.progress.setMaximum(mida)
            count=0
            self.progress.setValue(count)

            self.names=self.parent.llistaCamps+[self.parent.coordX,self.parent.coordY]
            writer=csv.DictWriter(arxiuNouCsv,fieldnames=self.names, delimiter=self.parent.separador)
            writer.writeheader()
            i=-1
            for row in reader:
                i+=1
                if i==0: continue
                print(count)
                d={**row}
                d['']=''
                #index=tabs.currentIndex()
                if d[self.parent.dadesAdreca[0]] == "":
                    tipusVia, nomVia, num = QvCarregaCsvGeneraCoords.splitCarrer(d[self.parent.dadesAdreca[1]])
                    
                elif d[self.parent.dadesAdreca[0]] != "" and d[self.parent.dadesAdreca[1]] != "":
                    tipusVia, nomVia, num = QvCarregaCsvGeneraCoords.splitCarrer(d[self.parent.dadesAdreca[0]] + ' ' + d[self.parent.dadesAdreca[1]])

                x, y = QvGeocod.coordsCarrerNum(tipusVia, nomVia, num if num!='' else d[self.parent.dadesAdreca[2]],d[self.parent.dadesAdreca[3]],d[self.parent.dadesAdreca[4]],d[self.parent.dadesAdreca[5]])
                d.pop('')
                count = count + 1
                self.progress.setValue(count)
                #app.processEvents() 
                if x is None or y is None:
                    aux = self.lblAdrecesError.text()
                    self.lblAdrecesError.setText(aux + "\n"+ tipusVia + " " + nomVia + " " + num)
                    print(tipusVia, nomVia, num)
                    d[self.parent.coordX]=""
                    d[self.parent.coordY]=""
                    writer.writerow(d)
                    continue

                d[self.parent.coordX]=x
                d[self.parent.coordY]=y
                writer.writerow(d)
        self.recarregaTaula(completa=True)
                


class QvtLectorCsv(QvLectorCsv):
        def __init__(self, fileName='', separador=None, completa=False, parent=None):
                #QvLectorCsv.__init__(self, fileName)
                super().__init__(fileName)
                self.separador=separador
                if self.separador is not None:
                        self.carregaCsv(self.fileName,self.separador, completa)
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
                                reader=csv.reader(f,delimiter=separador)
                                self.model.clear()
                                i=0
                                for row in reader:
                                        if not completa and i>9: break #Per agilitzar la càrrega, només ens cal una preview petita
                                        items=[QtGui.QStandardItem(field) for field in row]
                                        self.model.appendRow(items)
                                        i+=1
                                self.tableView.resizeColumnsToContents()
        def recarrega(self,separador):
                self.separador=separador
                self.carregaCsv(self.fileName,self.separador)


def infereixSeparadorRegex(arxiu):
    import re
    #Rep una llista i la retorna sense repeticions
    def eliminaRep(lst):
        return list(set(lst))
    #Rep una llista i la retorna sense repeticions i ordenada
    def eliminaRepOrd(lst):
        return sorted(set(lst))

    '''
    Utilitzant expressions regulars
    Un substring serà tot allò que comenci per ", i acabi amb ", sense contenir-ne cap a dins, de manera que ens ho carreguem
    Un nombre serà [0-9]+, cosa que també ens carreguem
    '''
    def infereixSeparadorLinia(line):
        aux=re.sub('"[^"]*"','',line)
        aux=re.sub('[0-9]+','',aux)
        aux=re.sub('[a-zA-Z]*','',aux)
        aux=aux.replace('\n','')#Per si tenim salt de línia al final
        auxSenseRep=eliminaRepOrd(aux) #Eliminem repeticions
        if len(auxSenseRep)==1: return aux[0] 
        #Creem una llista de tuples ordenada, on cada tupla conté el nombre d'aparicions del caracter i el caracter
        #lst=[(aux.count(x),x) for x in auxSenseRep]
        lst=sorted(map(lambda x: (aux.count(x),x),auxSenseRep))
        return lst
    def uneixLlistesAp(lst1, lst2):
        return list(set(lst1)&set(lst2))
    lst=[]
    for x in arxiu.readlines():
        act=infereixSeparadorLinia(x)
        if isinstance(act,str):
            arxiu.seek(0)
            return act
        if len(lst)==0: lst=act #Primera iteració
        else: lst=uneixLlistesAp(lst,act)
        if len(lst)==1:
            arxiu.seek(0)
            return lst[0][1]
    arxiu.seek(0)
    return [y for x,y in lst]


if __name__=='__main__':
    import sys
    app=QApplication(sys.argv)
    wizard=QvCarregaCsv('U:\\QUOTA\\Comu_imi\\Becaris\\gossos.csv')
    wizard.show()
    sys.exit(app.exec_())
