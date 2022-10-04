import collections
import itertools
import json
import functools
import re
import sys
import unicodedata

from qgis.core import QgsPointXY, QgsProject
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsVertexMarker
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QValidator
from qgis.PyQt.QtSql import QSqlQuery
from qgis.PyQt.QtWidgets import (QCompleter, QHBoxLayout, QLineEdit,
                                 QMessageBox, QStyleFactory, QVBoxLayout,
                                 QWidget)

from moduls.QvApp import QvApp


def encaixa(sub, string):
    '''Retorna True si alguna de les paraules de sub encaixa exactament dins de string (és a dir, a sub hi ha "... xxx ..." i a string també) i la resta apareixen però no necessàriament encaixant'''
    string = string.lower()
    subs = sub.split(' ')
    words = string.split(' ')
    # encaixaUna = False
    # for x in subs:
    #     if len(x) < 3:
    #         continue  # no té sentit si escrius "av d" que et posi a dalt de tot el Carrer d'Aiguablava perquè la d encaixa exactament amb una paraula
    #     if x not in string:
    #         return False  # Un dels substrings de la cerca no apareix dins de l'adreça
    #     if x in words:
    #         encaixaUna = True  # Hem trobat una que encaixa
    # return encaixaUna

    def x_in_words(x):
        return x in words and len(x)>=3
    return any(map(x_in_words, subs))


def conte(sub, string):
    '''Retorna true si string conté tots els strings representats a subs '''
    string = string.lower()
    subs = sub.split(' ')
    # for x in subs:
    #     if x not in string:
    #         return False
    # return True
    
    def x_not_in_string(x):
        return x not in string
    return not any(map(x_not_in_string, subs))


def comenca(sub, string):
    '''Retorna True si alguna de les paraules de string comença per alguna de les paraules de sub'''
    string = string.lower()
    #cal treure els parèntesis a l'hora de fer regex donat que hi ha problemes en el moment de fer parse amb re
    string = string.replace("(","")
    string = string.replace(")","")
    subs = sub.split(' ')
    # comencaUna = False
    # for x in subs:
    #     if x == '':
    #         print(':(')
    #         continue
    #     trobat = (x in string)
    #     if not trobat:
    #         return False
    #     # Si ja hem trobat que comença amb una no cal tornar a comprovar-ho. Seguim iterant només perquè la resta han d'estar contingudes
    #     if not comencaUna and re.search(' '+x, ' '+string) is not None:
    #         comencaUna = True
    # return comencaUna

    def x_in_string(x):
        return x in string
    def substring_comenca_per_x(x):
        return re.search(' '+x, ' '+string) is not None

    totes_hi_son = any(map(x_in_string, subs))
    comenca_una = any(map(substring_comenca_per_x, subs))
    # podria tenir sentit posar els any al return directament. Així, si la primera és falsa, la segona no s'arriba a mirar.
    # guanyaríem velocitat gràcies a la lazy evaluation, però perdríem llegibilitat
    return totes_hi_son and comenca_una


def variant(sub, string, variants):
    # for x in variants.split(','):
    #     if sub in x: return True
    # return False

    def sub_in_x(x):
        return sub in x
    return any(map(sub_in_x,variants.split(',')))

# per utilitzar la funció functools.lru_cache cal que tots els paràmetres siguin hashables
# ja que Python no té un diccionari immutable per defecte, fem això
class DiccionariHashable(dict):
    def __hash__(self):
        return hash(json.dumps(self))

class CompleterAdreces(QCompleter):
    def __init__(self, elems, widget):
        super().__init__(elems, widget)
        # self.elements=elems
        # Tindrem un diccionari on la clau serà el carrer i el valor les variants
        aux = [x.split(chr(29)) for x in elems]
        self.variants = DiccionariHashable({x[0]: x[1].lower() for x in aux})
        self.elements = tuple(self.variants.keys())
        self.le = widget
        # Aparellem cada carrer amb el rang del seu codi
        aux = zip(self.obteRangCodis(), self.elements)
        # Creem un diccionari que conté com a clau el nom del carrer i com a valor el codi
        # Així podrem ordenar els carrers en funció d'aquests codis
        self.dicElems = DiccionariHashable({y: y[x[0]:x[1]] for x, y in aux})
        self.popup().selectionModel().selectionChanged.connect(self.seleccioCanviada)
        self.modelCanviat = False

    def obteRangCodis(self):
        # Fem servir una expressió regular per buscar el rang dels codis. Creem un generador que conté el resultat
        return (re.search(r"\([0-9]*\)", x).span() for x in self.elements)

    def seleccioCanviada(self, nova, antiga):
        text = self.popup().currentIndex().data()
        ind = text.find(chr(30))
        if ind != -1:
            text = text[:ind-1]
        self.le.setText(text.strip())
        # print(text)
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def cerca(word,elements,dicElems, vars):
        # Volem dividir la llista en cinc llistes
        # -Carrers on un dels elements cercats encaixen amb una paraula del carrer
        # -Carrers on una de les paraules del carrer comencen per un dels elements cercats
        # -Carrers que contenen les paraules cercades
        # -Carrers que tenen una variant que contingui les paraules cercades
        # -La resta
        # Podria semblar que la millor manera és crear quatre llistes, fer un for, una cadena if-then-else i posar cada element en una de les quatre. Però això és molt lent
        # Aprofitant-nos de que les coses definides per python són molt ràpides (ja que es programen en C) podem resoldre el problema utilitzant funcions d'ordre superior i operacions sobre sets
        # Bàsicament farem servir filter per filtrar els elements que compleixen la funció, desar-los, i els extreurem dels restants.
        def filtra(llista, func):
            """Divideix una llista entre dues llistes, segons si compleixen la funció o no

            Args:
                llista (iterable[str]): llista que volem dividir
                func (Callable(str) -> boolean): funció que determina si els elements de la llista inicial van a la primera o a la segona

            Returns:
                tuple[iterable[str], iterable[str]]: Les dues llistes que contenen els elements de la llista inicial dividides segons la descripció
            """
            # EXPLICACIÓ TÈCNICA
            # La solució anterior (basada en sets) perdia l'ordre
            # Això requeria una ordenació posterior, que es menjava tota l'eficiència
            # Els diccionaris a partir de Python 3.6 conserven l'ordre. 
            # Traslladant el que abans es feia en sets als diccionaris, aconseguim millorar l'eficiència
            encaixen = {x:None for (i,x) in enumerate(llista) if func(x)}
            return encaixen.keys(), (x for x in llista if x not in encaixen)
        
        if len(word)<3:
            # Si la paraula que cerquem és curta (1 o 2 caràcters) només mirem els que comencen
            encaixen = []
            comencen, _ = filtra(elements, lambda x: comenca(word, x))
            contenen = []
            variants = []
        else:
            encaixen, altres = filtra(elements, lambda x: encaixa(word, x))
            comencen, altres = filtra(altres, lambda x: comenca(word, x))
            contenen, altres = filtra(altres, lambda x: conte(word, x))
            variants, _ = filtra(altres, lambda x: variant(word, x, vars[x]))

        # itertools.chain(l1, l2, l3) és "equivalent" a fer l1+l2+l3
        # en realitat no ajunta les llistes, de manera que no necessita iterar-les senceres, optimitzant una mica
        # Als elements de les llistes encaixen, comencen i contenen els afegim les variants al final
        # Als elements de la llista variants també li afegim, però també posem (var) al principi
        res = (x+chr(29)+vars[x] for x in itertools.chain(encaixen, comencen, contenen))
        res = itertools.chain(res, ('(var) '+x+chr(29)+vars[x] for x in variants))
        # OPCIÓ 1: ENS QUEDEM NOMÉS N FILES DEL RESULTAT
        #return list(res)[:20]
        return [x for (x,_) in zip(res,range(20))]
        # OPCIÓ 2: RETORNEM TOT
        # return list(res)

    def update(self, word):
        '''Funció que actualitza els elements'''
        if len(word) < 3 and self.modelCanviat:
            self.model().setStringList(self.elements)
            self.modelCanviat = False
            return
        self.word = word.lower()


        resultatCerca = self.cerca(self.word, self.elements, self.dicElems, self.variants)
        self.model().setStringList(resultatCerca)
        self.m_word = word
        self.complete()
        self.modelCanviat = True

    def splitPath(self, path):
        self.update(path)
        res = path.split(' ')
        return [res[-1]]


class ValidadorNums(QValidator):
    '''NO UTILITZADA. Serviria per poder impedir que es posin números no existents per l'adreça'''

    def __init__(self, elems, parent):
        super().__init__(parent)
        self.permesos = elems.keys()

    def validate(self, input, pos):
        if input in self.permesos:
            return QValidator.Acceptable, input, pos
        filt = filter(lambda x: x.startswith(input), self.permesos)
        if any(True for _ in filt):
            return QValidator.Intermediate, input, pos
        return QValidator.Invalid, input, pos


class QCercadorAdreca(QObject):
    sHanTrobatCoordenades = pyqtSignal(int, 'QString')  # atencion

    def __init__(self, lineEditCarrer, lineEditNumero, origen='SQLITE'):
        super().__init__()

        # self.pare= pare

        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        self.connectarLineEdits()
        self.carrerActivat = False

        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)

        # self.db.setConnectOptions("QSQLITE_OPEN_READONLY")
        self.numClick=0
        self.db = QvApp().dbGeo

        if self.db is None:  # not self.db.open(): # En caso de que no se abra
            QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                                 "Click para cancelar y salir.", QMessageBox.Cancel)

        self.query = QSqlQuery(self.db)  # Intancia del Query
        self.txto = ''
        self.calle_con_acentos = ''
        self.habilitaLeNum()

        self.iniAdreca()

        if self.llegirAdreces():
            # si se ha podido leer las direciones... creando el diccionario...
            self.prepararCompleterCarrer()

    def habilitaLeNum(self):
        self.carrerActivat = False
        return  # De moment no es desactivarà mai
        # Hauria de funcionar només amb la primera condició, però per raons que escapen al meu coneixement, no anava :()
        self.leNumero.setEnabled(
            self.calle_con_acentos != '' or self.txto != '')

    def cercadorAdrecaFi(self):
        if self.db.isOpen():
            self.db.close()

    def prepararCompleterCarrer(self):
        # creo instancia de completer que relaciona diccionario de calles con lineEdit
        # self.completerCarrer = QCompleter(self.dictCarrers, self.leCarrer)
        self.completerCarrer = CompleterAdreces(
            self.dictCarrers, self.leCarrer)
        # Determino funcionamiento del completer
        self.completerCarrer.setFilterMode(QtCore.Qt.MatchContains)
        self.completerCarrer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # Funcion que se ejecutará cuando
        self.completerCarrer.activated.connect(self.activatCarrer)
        # Asigno el completer al lineEdit
        self.leCarrer.setCompleter(self.completerCarrer)

    def prepararCompleterNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        self.completerNumero = QCompleter(
            self.dictNumerosFiltre, self.leNumero)
        self.completerNumero.activated.connect(self.activatNumero)
        self.completerNumero.setFilterMode(QtCore.Qt.MatchStartsWith)
        self.completerNumero.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(self.completerNumero)
        # self.leNumero.setValidator(ValidadorNums(self.dictNumeros[self.codiCarrer],self))

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
        self.NumeroOficial = ''

    def connectarLineEdits(self):
        self.leCarrer.textChanged.connect(self.esborrarNumero)
        self.leCarrer.editingFinished.connect(self.trobatCarrer)
        # CUARENTENA
        # self.leCarrer.mouseDoubleClickEvent = self.clear_leNumero_leCarrer
        # self.leCarrer.mouseDoubleClickEvent = self.SeleccPalabraOTodoEnFrase
        self.leCarrer.setAlignment(Qt.AlignLeft)

        self.leNumero.editingFinished.connect(self.trobatNumero)
        # self.leNumero.returnPressed.connect(self.trobatNumero)

    def SeleccPalabraOTodoEnFrase(self, event):
        """
          Funcion conectada al dobleclick.
          Si se dobleclica 1 vez---> selecciona la palabra (lo que hay entre dos blancos)
          Se se dobleclica 2 veces---> selecciona toda la frase 
        """
        self.carrerActivat=False
        #  self.numClick en def __init__ se inicializa a 0
        if self.numClick == 1:  # segundo doble click => seleccionar toda la frase
            self.leCarrer.selectAll()
            self.numClick =-1
        else:      # primer doble click selecciona la palabra
            # Limite de la palabra por la izquierda (blanco o inicio por izquierda)
            self.ii = self.leCarrer.cursorPosition() - 1
            while self.ii >=0 and self.leCarrer.text()[self.ii] != ' ': 
                self.ii -= 1 ;   self.inicio= self.ii

            # Limite de la palabra por la derecha (blanco o fin por derecha)
            self.ii= self.leCarrer.cursorPosition() - 1 
            while self.ii < len(self.leCarrer.text()) and self.leCarrer.text()[self.ii] != ' ': 
                self.ii += 1 ;   self.fin= self.ii                

            # selecciona palabra en frase por posicion
            self.leCarrer.setSelection(self.inicio+1,self.fin-self.inicio-1)
            
        self.numClick += 1  
    # CUARENTENA
    # def clear_leNumero_leCarrer(self, carrer):
    #     self.carrerActivat = False
    #     self.leNumero.clear()
    #     self.leCarrer.clear()

    # Venimos del completer, un click en desplegable ....
    def activatCarrer(self, carrer):
        self.carrerActivat = True
        # print(carrer)

        carrer=carrer.replace('(var) ','')
        # if chr(29) in carrer:
        #     carrer=carrer.split(chr(29))[0]
        nn = carrer.find(chr(30))
        if nn == -1:
            ss = carrer
        else:
            ss = carrer[0:nn-1]
        # ss=ss.replace('(var) ','')

        self.calle_con_acentos = ss.rstrip()

        self.leCarrer.setAlignment(Qt.AlignLeft)
        self.leCarrer.setText(self.calle_con_acentos)

        # self.leCarrer.setText(carrer)
        self.iniAdreca()
        if carrer in self.dictCarrers:
            self.nomCarrer = carrer
            self.codiCarrer = self.dictCarrers[self.nomCarrer]

            try:
                index = 0
                # self.query = QSqlQuery() # Intancia del Query
                # self.query.exec_("select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros where codi = '" + self.codiCarrer +"'")

                self.query.exec_(
                    "select codi,case num_lletra_post when '0' then ' ' else num_lletra_post end,  etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros   where codi = '" + self.codiCarrer + "'")
                # self.query.exec_("select codi,case num_lletra_post when '0' then ' ' else num_lletra_post end,  etrs89_coord_x, etrs89_coord_y, case num_oficial when '0' then ' ' else num_oficial end  from Numeros   where codi = '" + self.codiCarrer +"'")

                while self.query.next():
                    row = collections.OrderedDict()
                    row['NUM_LLETRA_POST'] = self.query.value(
                        1)  # Numero y Letra
                    row['ETRS89_COORD_X'] = self.query.value(2)  # coor x
                    row['ETRS89_COORD_Y'] = self.query.value(3)  # coor y
                    row['NUM_OFICIAL'] = self.query.value(4)  # numero oficial

                    self.dictNumeros[self.codiCarrer][self.query.value(
                        1)] = row
                    index += 1

                self.query.finish()
                # self.db.close()

                self.prepararCompleterNumero()
                self.focusANumero()

            except Exception as e:
                print(str(e))
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)

                msg.setText(str(sys.exc_info()[1]))
                # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
                msg.setWindowTitle("qVista ERROR")
                msg.setStandardButtons(QMessageBox.Close)
                retval = msg.exec_()  # No fem res amb el valor de retorn (???)

                print('QCercadorAdreca.iniAdreca(): ',
                      sys.exc_info()[0], sys.exc_info()[1])
                return False
            else:
                pass

        else:
            info = "ERROR >> [1]"
            self.sHanTrobatCoordenades.emit(1, info)  # adreça vacia
        self.habilitaLeNum()
        # self.prepararCompleterNumero()
        # self.focusANumero()

    def trobatCarrer(self):
        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
            return
        if not self.carrerActivat:
            # print(self.leCarrer.text())
            # així obtenim el carrer on estàvem encara que no l'haguem seleccionat explícitament
            self.txto = self.completerCarrer.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completerCarrer.currentCompletion()
            if self.txto == '':
                return
            # self.txto=self.txto.split(chr(29))[0]

            nn = self.txto.find(chr(30))
            self.txto=self.txto.replace('(var) ','')
            if nn == -1:
                ss = self.txto
            else:
                ss = self.txto[0:nn-1]
            # ss=ss.replace('(var) ','')

            # ss= self.txto[0:nn-1]
            self.calle_con_acentos = ss.rstrip()

            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(self.calle_con_acentos)

            self.iniAdreca()
            if self.txto != self.nomCarrer:
                # self.iniAdreca()
                if self.txto in self.dictCarrers:
                    self.nomCarrer = self.txto
                    self.codiCarrer = self.dictCarrers[self.nomCarrer]
                    self.focusANumero()

                    try:
                        index = 0
                        # self.query = QSqlQuery() # Intancia del Query
                        # self.query.exec_("select codi, num_lletra_post, etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros where codi = '" + self.codiCarrer +"'")
                        self.query.exec_(
                            "select codi,case num_lletra_post when '0' then ' ' else num_lletra_post end,  etrs89_coord_x, etrs89_coord_y, num_oficial  from Numeros   where codi = '" + self.codiCarrer + "'")

                        while self.query.next():
                            row = collections.OrderedDict()
                            row['NUM_LLETRA_POST'] = self.query.value(
                                1)  # Numero y Letra
                            row['ETRS89_COORD_X'] = self.query.value(
                                2)  # coor x
                            row['ETRS89_COORD_Y'] = self.query.value(
                                3)  # coor y
                            row['NUM_OFICIAL'] = self.query.value(
                                4)  # numero oficial

                            self.dictNumeros[self.codiCarrer][self.query.value(
                                1)] = row
                            index += 1

                        self.query.finish()
                        # self.db.close()
                        self.prepararCompleterNumero()
                        self.focusANumero()

                    except Exception as e:
                        print(str(e))
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)

                        msg.setText(str(sys.exc_info()[1]))
                        # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
                        msg.setWindowTitle("qVista ERROR")
                        msg.setStandardButtons(QMessageBox.Close)
                        retval = msg.exec_()  # No fem res amb el valor de retorn (???)

                        print('QCercadorAdreca.iniAdreca(): ',
                              sys.exc_info()[0], sys.exc_info()[1])
                        return False

                else:
                    info = "ERROR >> [2]"
                    # direccion no está en diccicionario
                    self.sHanTrobatCoordenades.emit(2, info)
                    self.iniAdreca()
            else:
                info = "ERROR >> [3]"
                self.sHanTrobatCoordenades.emit(3, info)  # nunca
        else:
            info = "ERROR >> [4]"
            self.sHanTrobatCoordenades.emit(4, info)  # adreça vac
        self.habilitaLeNum()

    def llegirAdreces(self):
        if self.origen == 'SQLITE':
            ok = self.llegirAdrecesSQlite()
        else:
            ok = False
        return ok

    def llegirAdrecesSQlite(self):
        try:
            index = 0
            # self.query = QSqlQuery() # Intancia del Query
            self.query.exec_(
                "select codi , nom_oficial , variants  from Carrers")

            while self.query.next():
                codi_carrer = self.query.value(0)  # Codigo calle
                nombre = self.query.value(1)  # numero oficial
                variants = self.query.value(2).lower()  # Variants del nom
                nombre_sin_acentos = self.remove_accents(nombre)
                if nombre == nombre_sin_acentos:
                    # clave= nombre + "  (" + codi_carrer + ")"
                    clave = nombre + \
                        "  (" + codi_carrer + \
                        ")                                                  " + \
                        chr(30)
                else:
                    clave = nombre + "  (" + codi_carrer + ")                                                  "+chr(
                        30)+"                                                         " + nombre_sin_acentos
                    # asignacion al diccionario
                variants.replace(',', 50*' ')
                clave += chr(29)+50*' '+variants
                self.dictCarrers[clave] = codi_carrer

                index += 1

            self.query.finish()
            # self.db.close()
            return True
        except Exception as e:
            print(str(e))
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText(str(sys.exc_info()[1]))
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("qVista ERROR")
            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()  # No fem res amb el valor de retorn (???)

            print('QCercadorAdreca.llegirAdrecesSQlite(): ',
                  sys.exc_info()[0], sys.exc_info()[1])
            return False

    # Normalización caracteres quitando acentos

    def remove_accents(self, input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii.decode("utf8")

    def activatNumero(self, txt):
        self.leNumero.setText(txt)
        self.iniAdrecaNumero()
        # if self.leCarrer.text() in self.dictCarrers:
        # self.txto = self.completerCarrer.currentCompletion()
        self.txto = self.completerCarrer.popup().currentIndex().data()
        if self.txto is None:
            self.txto = self.completerCarrer.currentCompletion()
        self.txto=self.txto.replace('(var) ','')
        if self.txto in self.dictCarrers:
            if txt in self.dictNumerosFiltre:
                self.numeroCarrer = txt
                self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']),
                                              float(self.infoAdreca['ETRS89_COORD_Y']))

                self.NumeroOficial = self.infoAdreca['NUM_OFICIAL']
                self.leNumero.setText(self.NumeroOficial)
                self.leNumero.clearFocus()

                info = "[0]"
                self.sHanTrobatCoordenades.emit(0, info)
                if self.leNumero.text() == ' ':
                    self.leNumero.clear()

        else:
            info = "ERROR >> [5]"
            self.sHanTrobatCoordenades.emit(5, info)  # numero

    def trobatNumero(self):
        # Si no hi ha carrer, eliminem el completer del número
        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
        if self.leNumero.text() == '':
            return
        # self.txto = self.completerCarrer.currentCompletion()
        try:
            # if self.leCarrer.text() in self.dictCarrers:
            self.txto = self.completerCarrer.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completerCarrer.currentCompletion()
            self.txto=self.txto.replace('(var) ','')
            if self.txto in self.dictCarrers:

                if self.leNumero.text() != '':
                    txt = self.completerNumero.popup().currentIndex().data()
                    if txt is None:
                        txt = self.completerNumero.currentCompletion()
                    # txt = self.completerNumero.currentCompletion()
                    self.leNumero.setText(txt)
                else:
                    txt = ' '

                if txt != '':  # and txt != self.numeroCarrer:
                    self.iniAdrecaNumero()
                    if self.nomCarrer != '':
                        if txt in self.dictNumerosFiltre:
                            self.numeroCarrer = txt
                            self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                            self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']),
                                                          float(self.infoAdreca['ETRS89_COORD_Y']))
                            self.NumeroOficial = self.infoAdreca['NUM_OFICIAL']
                            self.leNumero.clearFocus()
                            self.leNumero.setText(self.NumeroOficial)
                            info = "[0]"
                            self.sHanTrobatCoordenades.emit(0, info)
                            if self.leNumero.text() == ' ':
                                self.leNumero.clear()

                        else:
                            info = "ERROR >> [6]"
                            # numero no está en diccicionario
                            self.sHanTrobatCoordenades.emit(6, info)
                    else:
                        info = "ERROR >> [7]"
                        self.sHanTrobatCoordenades.emit(
                            7, info)  # adreça vacia  nunca
                else:
                    info = "ERROR >> [8]"
                    self.sHanTrobatCoordenades.emit(
                        8, info)  # numero en blanco
            else:
                self.leNumero.clear()
                info = "ERROR >> [9]"
                self.sHanTrobatCoordenades.emit(9, info)  # numero en blanco
        except:
            return
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            info_rsc = 'ERROR: ' + str(sys.exc_info()[0])
            msg.setText(info_rsc)
            # msg.setInformativeText("OK para salir del programa \nCANCEL para seguir en el programa")
            msg.setWindowTitle("qVista >> QVCercadorAdreca>> trobatNumero")

            msg.setStandardButtons(QMessageBox.Close)
            retval = msg.exec_()  # No fem res amb el valor de retorn (???)

    def focusANumero(self):
        self.leNumero.setFocus()

    def esborrarNumero(self):
        # self.carrerActivat = False
        self.calle_con_acentos = ''
        self.leNumero.clear()
        # self.leNumero.setCompleter(None)


if __name__ == "__main__":
    projecteInicial = 'mapesOffline/qVista default map.qgs'
    from moduls.QvCanvas import QvCanvas

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        # canvas = QgsMapCanvas()
        canvas = QvCanvas(llistaBotons=['panning','zoomIn','zoomOut'])
        canvas.setGeometry(10, 10, 1000, 1000)
        canvas.setCanvasColor(QColor(10, 10, 10))
        le1 = QLineEdit()
        le1.setPlaceholderText('Carrer')
        le2 = QLineEdit()
        le2.setPlaceholderText('Número')

        layCerc=QHBoxLayout()
        layCerc.addWidget(le1)
        layCerc.addWidget(le2)
        lay=QVBoxLayout()
        lay.setContentsMargins(0,0,0,0)
        lay.addLayout(layCerc)
        lay.addWidget(canvas)
        wid=QWidget()
        wid.setLayout(lay)

        marcaLloc=None
        def trobat(codi,info):
            global marcaLloc
            if codi!=0:
                print(info)
                return
            if marcaLloc is not None:
                marcaLloc.hide()
            marcaLloc=QgsVertexMarker(canvas)
            marcaLloc.setCenter( cercador.coordAdreca )
            marcaLloc.setColor(QColor(255, 0, 0))
            marcaLloc.setIconSize(15)
            marcaLloc.setIconType(QgsVertexMarker.ICON_BOX)
            marcaLloc.setPenWidth(3)
            marcaLloc.show()
        # Instanciar el cercador requereix de dos QLineEdit (camp d'adreces i camp de números)
        # El cercador té una senyal que es llença quan troba una adreça. Aquesta senyal passa dos paràmetres.
        #  - Un enter, amb un codi d'error. Si és 0, tot ha anat bé. La resta, es poden veure al codi
        #  - Un text, amb la informació de l'error
        # Per accedir a les coordenades es pot fer mitjançant l'atribut coordAdreca del cercador, que s'haurà actualitzat quan les hagi trobat
        cercador=QCercadorAdreca(le1, le2)
        cercador.sHanTrobatCoordenades.connect(trobat)
        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        wid.show()
