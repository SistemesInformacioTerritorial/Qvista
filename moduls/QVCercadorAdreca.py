from qgis.core import QgsPointXY
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter
import sys
import csv
import collections





class QCercadorAdreca(QObject):

    __carrersCSV = '..\dades\dadesBcn\CARRERER.csv'
    __numerosCSV = '..\dades\dadesBcn\TAULA_DIRELE.csv'
    sHanTrobatCoordenades = pyqtSignal(int, 'QString')  # atencion

    def __init__(self, lineEditCarrer, lineEditNumero, origen = 'CSV'):
        super().__init__()
        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        self.connectarLineEdits()
        self.carrerActivat = False

        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)

        self.iniAdreca()
        if self.llegirAdreces():
            self.prepararCompleterCarrer()

    def prepararCompleterCarrer(self):
        self.completerCarrer = QCompleter(self.dictCarrers, self.leCarrer)
        self.completerCarrer.setFilterMode(QtCore.Qt.MatchContains)
        self.completerCarrer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completerCarrer.activated.connect(self.activatCarrer)
        self.leCarrer.setCompleter(self.completerCarrer)   

    def prepararCompleterNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        self.completerNumero = QCompleter(self.dictNumerosFiltre, self.leNumero)
        self.completerNumero.activated.connect(self.activatNumero)
        self.completerNumero.setFilterMode(QtCore.Qt.MatchStartsWith)
        self.completerNumero.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(self.completerNumero)  


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
        self.leCarrer.returnPressed.connect(self.trobatCarrer)
        self.leCarrer.textChanged.connect(self.esborrarNumero)
        self.leNumero.editingFinished.connect(self.trobatNumero)
        # self.leNumero.returnPressed.connect(self.trobatNumero)

    def activatCarrer(self, carrer):
        self.carrerActivat = True
        print(carrer)
        self.leCarrer.setText(carrer)
        self.iniAdreca()
        if carrer in self.dictCarrers:
            self.nomCarrer = carrer
            self.codiCarrer = self.dictCarrers[self.nomCarrer]
            self.prepararCompleterNumero()
            self.focusANumero()

    def trobatCarrer(self):
        self.carrerActivat = False
        if not self.carrerActivat:
            txt = self.completerCarrer.currentCompletion()
            self.leCarrer.setText(txt)

            if txt != '':
                self.iniAdreca()
                if txt != self.nomCarrer:
                    # self.iniAdreca()
                    if txt in self.dictCarrers:
                        self.nomCarrer = txt
                        self.codiCarrer = self.dictCarrers[self.nomCarrer]
                        self.prepararCompleterNumero()
                        self.focusANumero()
                    else:
                        info="\""+txt+"\""
                        info="Has introduït: "+info+ "\nCarrer incorrecte [4]"
                        self.sHanTrobatCoordenades.emit(4,info) #direccion no está en diccicionario
                        self.iniAdreca()
                else:
                    info="\""+txt+"\""
                    info="Oops! \nTorna a introduir l'adreça i després el número [5]"
                    self.sHanTrobatCoordenades.emit(5,info)    #nunca
            else:
                info="\""+txt+"\""
                info= "No s'ha trobat el carrer" 
                self.sHanTrobatCoordenades.emit(6,info) #adreça vacia
                
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
                    # pass
            with open(self.__numerosCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row
                    # pass

                # splash_1.destroy()
                return True
        except:
            print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
            return False


    def activatNumero(self,txt):
        self.leNumero.setText(txt)
        self.iniAdrecaNumero()
        if  txt in self.dictNumerosFiltre:
            self.numeroCarrer = txt
            self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
            self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), \
                                        float(self.infoAdreca['ETRS89_COORD_Y']))
            self.leNumero.clearFocus()
            
            info="\""+self.nomCarrer+"\"  \"" +txt  +"\""
            self.sHanTrobatCoordenades.emit(0,info)                


    def trobatNumero(self):
        txt = self.completerNumero.currentCompletion()
        self.leNumero.setText(txt)
        if txt != '': # and txt != self.numeroCarrer:
            self.iniAdrecaNumero()
            if self.nomCarrer != '':
                if  txt in self.dictNumerosFiltre:
                    self.numeroCarrer = txt
                    self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                    self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), \
                                                float(self.infoAdreca['ETRS89_COORD_Y']))
                    self.leNumero.clearFocus()
                    
                    info="\""+self.nomCarrer+"\"  \"" +txt  +"\""
                    self.sHanTrobatCoordenades.emit(0,info)                
                else:
                    info="\""+self.nomCarrer+"\"  \"" +txt  +"\""
                    info="Has introduït: "+info+ " \nNúmero inexistent/incorrecte [1]"
                    self.sHanTrobatCoordenades.emit(1,info)  #numero no está en diccicionario
            else:
                info="\""+self.nomCarrer+"\"  \"" +txt  +"\""
                info= "Oops! \nTorna a introduir l'adreça i després el número [2]"
                self.sHanTrobatCoordenades.emit(2,info) #adreça vacia  nunca
        else:
            info="\""+self.nomCarrer+"\"  \"" +txt  +"\""
            info= literal= "Has introduït: "+info+ " \nNúmero en blanc [3]"
            self.sHanTrobatCoordenades.emit(3,info)   #numero en blanco
            

    def focusANumero(self):
        self.leNumero.setFocus()


        

    def esborrarNumero(self):
        self.leNumero.clear()
        #self.leNumero.setCompleter(None)


from moduls.QvImports import *
if __name__ == "__main__":
    projecteInicial='projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        canvas = QgsMapCanvas()
        canvas.setGeometry(10,10,1000,1000)
        canvas.setCanvasColor(QColor(10,10,10))
        le1 = QLineEdit()
        le2 = QLineEdit()
        le1.show()
        le2.show()

        QCercadorAdreca(le1, le2)
        project= QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        canvas.show()