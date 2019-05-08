from moduls.QvImports import * 
from enum import IntEnum
from moduls.QvLectorCsv import QvLectorCsv

class QvCarregaCsv(QWizard):
    finestres=IntEnum('finestres','TriaSep TriaSepDec TriaGeom CampsXY Adreca')
    def __init__(self,csv,parent=None):
        super().__init__(parent)
        self.csv=csv
        self.setPage(QvCarregaCsv.finestres.TriaSep, QvCarregaCsvTriaSep(self))
        self.setPage(QvCarregaCsv.finestres.TriaSepDec, QvCarregaCsvTriaSepDec(self))
        self.setPage(QvCarregaCsv.finestres.TriaGeom, QvCarregaCsvTriaGeom(self))
        self.setPage(QvCarregaCsv.finestres.CampsXY, QvCarregaCsvXY(self))
        self.setPage(QvCarregaCsv.finestres.Adreca, QvCarregaCsvAdreca(self))
    def exec_(self):
        super().exec_()
        return self.csv,self.separador, self.coordX, self.coordY, self.nomCapa

        

class QvCarregaCsvPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent=parent
        self.setTitle('Assistent de càrrega de CSV')
    def mostraTaula(self):
        self.table=QvtLectorCsv(self.parent.csv,self.parent.separador,self)
        self.layoutTable=QVBoxLayout()
        self.layout.addLayout(self.layoutTable)
        self.layoutTable.addWidget(self.table)
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
        self.parent.separador=infereixSeparadorRegex(open(parent.csv))
        self.mostraTaula()
        def botoClickat(boto):
            def botoClickatAux():
                self.parent.separador=boto
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
        self.llistaCamps=self.obteCamps()
        print(self.llistaCamps)
        self.cbX=QComboBox()
        self.cbX.addItems(self.llistaCamps)
        self.cbY=QComboBox()
        self.cbY.addItems(self.llistaCamps)
        self.layoutCoord.addWidget(self.cbX)
        self.layoutCoord.addWidget(self.cbY)
        self.cbProj=QComboBox()
        projeccions = [25831, 1 , 2 , 3]
        self.cbProj.clear()
        self.cbProj.addItems([str(x) for x in projeccions])
        self.layout.addWidget(self.cbProj)
        def xChanged():
            self.parent.coordX=self.cbX.currentText()
        def yChanged():
            self.parent.coordY=self.cbY.currentText()
        def projChanged():
            self.parent.proj=self.cbProj.currentText()
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
            self.parent.tipusVia
            self.parent.tipusVia
            self.parent.tipusVia
            self.parent.tipusVia
            self.parent.tipusVia
            

        self.mostraTaula()




class QvtLectorCsv(QvLectorCsv):
        def __init__(self, fileName='', separador=None, parent=None):
                #QvLectorCsv.__init__(self, fileName)
                super().__init__(fileName)
                self.separador=separador
                if self.separador is not None:
                        self.carregaCsv(self.fileName,self.separador)
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
