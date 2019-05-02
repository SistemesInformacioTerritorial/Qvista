from qgis.core import QgsPointXY
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter
import sys
import csv
import collections
import unicodedata
import re
import csv





class QCercadorAdreca(QObject):

    __carrersCSV = 'dades\CARRERER.csv'
    __path_disgregados= 'Dades\dir_ele\\' 
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

        self.txto =''

        self.iniAdreca()

        if self.llegirAdreces():
            # si se ha podido leer las direciones... creando el diccionario...
            self.prepararCompleterCarrer()

    def prepararCompleterCarrer(self):
        # creo instancia de completer que relaciona diccionario de calles con lineEdit
        self.completerCarrer = QCompleter(self.dictCarrers, self.leCarrer)
        # Determino funcionamiento del completer
        self.completerCarrer.setFilterMode(QtCore.Qt.MatchContains)
        self.completerCarrer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # Funcion que se ejecutará cuando 
        self.completerCarrer.activated.connect(self.activatCarrer)
        # Asigno el completer al lineEdit
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
        self.leCarrer.mouseDoubleClickEvent = self.clear_leNumero_leCarrer

        self.leNumero.returnPressed.connect(self.trobatNumero)
        # self.leNumero.returnPressed.connect(self.trobatNumero)

    def clear_leNumero_leCarrer(self, carrer):
        self.leNumero.clear()
        self.leCarrer.clear()

    # Venimos del completer, un click en desplegable ....
    def activatCarrer(self, carrer):
        self.carrerActivat = True
        # print(carrer)

        nn= carrer.find(chr(30))
        ss= carrer[0:nn]
        self.calle_con_acentos=ss.rstrip()

        self.leCarrer.setAlignment(Qt.AlignLeft)  
        self.leCarrer.setText(self.calle_con_acentos)


        # self.leCarrer.setText(carrer)
        self.iniAdreca()
        if carrer in self.dictCarrers:
            self.nomCarrer = carrer
            self.codiCarrer = self.dictCarrers[self.nomCarrer]

            path= self.__path_disgregados+str(self.codiCarrer)+'.csv'
            with open(path, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row

            self.prepararCompleterNumero()
            self.focusANumero()
        else:
            info= "ERROR >> [1]" 
            self.sHanTrobatCoordenades.emit(1,info) #adreça vacia

    def trobatCarrer(self):
        self.carrerActivat = False
        if not self.carrerActivat:
            self.txto = self.completerCarrer.currentCompletion()

            nn= self.txto.find(chr(30))
            ss= self.txto[0:nn]
            self.calle_con_acentos=ss.rstrip()

            self.leCarrer.setAlignment(Qt.AlignLeft)  
            self.leCarrer.setText(self.calle_con_acentos)

            if self.txto != '':
                self.iniAdreca()
                if self.txto != self.nomCarrer:
                    # self.iniAdreca()
                    if self.txto in self.dictCarrers:
                        self.nomCarrer = self.txto
                        self.codiCarrer = self.dictCarrers[self.nomCarrer]
                        self.focusANumero()
                        path= self.__path_disgregados+str(self.codiCarrer)+'.csv'
                        with open(path, encoding='utf-8', newline='') as csvFile:
                            reader = csv.DictReader(csvFile, delimiter=',')
                            for row in reader:
                                self.dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row

                        self.prepararCompleterNumero()
                        self.focusANumero()

                    else:
                        info="ERROR >> [2]"
                        self.sHanTrobatCoordenades.emit(2,info) #direccion no está en diccicionario
                        self.iniAdreca()
                else:
                    info="ERROR >> [3]"
                    self.sHanTrobatCoordenades.emit(3,info)    #nunca
            else:
                info="ERROR >> [4]"
                self.sHanTrobatCoordenades.emit(4,info) #adreça vac       

            
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

    # Normalización caracteres quitando acentos
    def remove_accents(self,input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii.decode("utf8")

    # Leer fichero de direcciones craendo un diccionario, 
    # la clave será el nombre de la calle y el nombre de la calle sin acentos
    # el valor relacionado el codigo de calle
    # La idea es que tanto si el usuario teclea el nombre con/sin acentos encuentre el codigo de calle
    def llegirAdrecesCSV(self):
        try:
            with open(self.__carrersCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    # leemo linea del csv y extraemos campos....
                    nombre= row['NOM_OFICIAL']
                    nombre_sin_acentos= self.remove_accents(nombre)
                    codi_carrer= row['CODI_VIA']
                    # creamos clave.... pongo caracter 30 (invisible), para separar ambas partes
                    if nombre == nombre_sin_acentos:
                        clave= nombre + "  (" + codi_carrer + ")                                                  "+chr(30)
                    else:
                        clave= nombre + "  (" + codi_carrer + ")                                                  "+chr(30)+"                                                         " + nombre_sin_acentos
                    # asignacion al diccionario
                    self.dictCarrers[clave] = codi_carrer 
                    
            return True
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            
            msg.setText(str(sys.exc_info()[1]))
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("qVista ERROR")
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()




            # print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
            return False

    def activatNumero(self,txt):
        self.leNumero.setText(txt)
        self.iniAdrecaNumero()
        # if self.leCarrer.text() in self.dictCarrers:
        self.txto = self.completerCarrer.currentCompletion()
        if self.txto in self.dictCarrers:
            if  txt in self.dictNumerosFiltre:
                self.numeroCarrer = txt
                self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), \
                                            float(self.infoAdreca['ETRS89_COORD_Y']))
                self.leNumero.clearFocus()

                info="[0]"
                self.sHanTrobatCoordenades.emit(0,info)  
        else :
            info="ERROR >> [5]"
            self.sHanTrobatCoordenades.emit(5,info)  #numero          

    def trobatNumero(self):
        
        try:
            # if self.leCarrer.text() in self.dictCarrers:
            if self.txto in self.dictCarrers:
                
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
                            info="[0]"
                            self.sHanTrobatCoordenades.emit(0,info)                
                        else:
                            info="ERROR >> [6]"
                            self.sHanTrobatCoordenades.emit(6,info)  #numero no está en diccicionario
                    else:
                        info="ERROR >> [7]"
                        self.sHanTrobatCoordenades.emit(7,info) #adreça vacia  nunca
                else:
                    info="ERROR >> [8]"
                    self.sHanTrobatCoordenades.emit(8,info)   #numero en blanco
            else:
                self.leNumero.clear()
                info="ERROR >> [9]"
                self.sHanTrobatCoordenades.emit(9,info)   #numero en blanco
        except: 
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            info_rsc= 'ERROR: '+ str(sys.exc_info()[0])
            msg.setText(info_rsc)
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("qVista >> QVCercadorAdreca>> trobatNumero")
            
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()

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
        le1.setWindowTitle("Calle")
        le1.show()
        le2.setWindowTitle("Numero")
        le2.show()

        QCercadorAdreca(le1, le2)
        project= QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        canvas.show()