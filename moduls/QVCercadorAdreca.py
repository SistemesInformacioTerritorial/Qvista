import collections
import itertools
import json
import functools
import re
import sys
import unicodedata
import copy

from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsPointXY, QgsProject
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsVertexMarker
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QValidator
from qgis.PyQt.QtSql import QSqlQuery,QSqlDatabase
from qgis.PyQt.QtWidgets import (QCompleter, QHBoxLayout, QLineEdit,
                                 QMessageBox, QStyleFactory, QVBoxLayout,
                                 QWidget)

from moduls.QvApp import QvApp
from typing import List,Optional
from moduls.constants import TipusCerca

from PyQt5.QtCore import QTimer


def mostrarError(e: Exception) -> None:
    """
    Mostra un error en una finestra de diàleg.

    Args:
        e (Exception): Excepció que es vol mostrar en la finestra de diàleg.
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(f"ERROR: {str(e)}")
    msg.setWindowTitle("No s'ha trobat el resultat")
    msg.setStandardButtons(QMessageBox.Close)
    msg.exec_()

def arreglaCarrer(carrer):
    res = carrer.strip()
    res = res.replace('(','').replace(')','')
    return res.lower()
def encaixa(sub, string):
    '''Retorna True si alguna de les paraules de sub encaixa exactament dins de string (és a dir, a sub hi ha "... xxx ..." i a string també) i la resta apareixen però no necessàriament encaixant'''
    string = string.lower()
    sub = sub.strip()
    subs = sub.split(' ')
    words = string.split(' ')

    def x_in_words(x):
        return x in words
    return any(map(x_in_words, subs)) and conte(sub,string)


def conte(sub, string):
    '''Retorna true si string conté tots els strings representats a subs '''
    string = string.lower()
    sub = sub.strip()
    subs = sub.split(' ')
    
    def x_not_in_string(x):
        return x not in string
    return all(x in string for x in subs)


def comenca(sub, string):
    '''Retorna True si alguna de les paraules de string comença per alguna de les paraules de sub'''
    string = string.lower()
    #cal treure els parèntesis a l'hora de fer regex donat que hi ha problemes en el moment de fer parse amb re
    string = string.replace("(","")
    string = string.replace(")","")
    sub = sub.strip()
    subs = sub.split(' ')

    def x_in_string(x):
        return x in string
    def substring_comenca_per_x(x):
        return re.search(' '+x, ' '+string) is not None

    # # podria tenir sentit posar els any al return directament. Així, si la primera és falsa, la segona no s'arriba a mirar.
    # # guanyaríem velocitat gràcies a la lazy evaluation, però perdríem llegibilitat
    # return totes_hi_son and comenca_una
    return any(map(substring_comenca_per_x, subs)) and conte(sub,string)


def variant(sub, string, variants):

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
    
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def cerca(word,elements,dicElems, vars):
        # Volem dividir la llista en cinc llistes
        # -Carrers on un dels elements cercats encaixen amb una paraula del carrer
        # -Carrers on una de les paraules del carrer comencen per un dels elements cercats
        # -Carrers que contenen les paraules cercades
        # -Carrers que tenen una variant que contingui les paraules cercades
        # -La resta
        # D'aquestes 5, el completer mostrarà les primeres 4, que són les que són interessants
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

            # Respecte la possibilitat basada en llistes (dues llistes, un bucle i anar posant on pertoqui) el guany és del 50%
            # (en casos concrets hi ha pèrdues, en d'altres guanys molt grans)
            encaixen = {x:None for (i,x) in enumerate(llista) if func(x)}
            return list(encaixen.keys()), [x for x in llista if x not in encaixen]
        
        if False and len(word)<3:
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

        # Als elements de les llistes encaixen, comencen i contenen els afegim les variants al final
        # Als elements de la llista variants també li afegim, però també posem (var) al principi, ja que el resultat ha sigut trobat dins d'una variant
        res = (x+chr(29)+vars[x] for x in itertools.chain(encaixen, comencen, contenen))
        res = itertools.chain(res, ('(var) '+x+chr(29)+vars[x] for x in variants))

        res = [x for (x,_) in zip(res,range(20))]
        return res

    def update(self, word):
        '''Funció que actualitza els elements'''
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
    sHanTrobatCoordenades = pyqtSignal(int, 'QString')

    def __init__(self, lineEditCarrer, lineEditNumero, origen='SQLITE', comboTipusCerca=None):
        super().__init__()

        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        self.tipusCerca = comboTipusCerca

        self.tipusCerca.currentIndexChanged.connect(self.connectarLineEdits)
        self.leNumero.returnPressed.connect(self.trobatCantonada)

        self.connectarLineEdits()

        self.carrerActivat = False

        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)
        self.dictCantonades = collections.defaultdict(dict)

        self.numClick=0
        self.db = QvApp().dbGeo

        if self.db is None:
            QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                                "Click para cancelar y salir.", QMessageBox.Cancel)

        self.query = QSqlQuery(self.db)
        self.txto = ''
        self.calle_con_acentos = ''
        self.habilitaLeNum()

        self.iniAdreca()

        if self.llegirAdreces():
            self.prepararCompleterCarrer()
            super().__init__()

            self.origen = origen
            self.leCarrer = lineEditCarrer
            self.leNumero = lineEditNumero
            self.tipusCerca = comboTipusCerca

            self.carrerActivat = False

            self.dictCarrers = {}
            self.dictNumeros = collections.defaultdict(dict)
            self.dictCantonades = collections.defaultdict(dict)

            self.numClick=0
            self.db = QvApp().dbGeo

            if self.db is None:
                QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                                    "Click para cancelar y salir.", QMessageBox.Cancel)

            self.query = QSqlQuery(self.db)
            self.txto = ''
            self.calle_con_acentos = ''
            self.habilitaLeNum()

            self.iniAdreca()

            if self.llegirAdreces():
                self.prepararCompleterCarrer()

    def habilitaLeNum(self):
        self.carrerActivat = False
        condicio_per_habilitar = (self.calle_con_acentos != '' or self.txto != '' or self.leCarrer.text().strip() != '')
        self.leNumero.setEnabled(condicio_per_habilitar)


    def cercadorAdrecaFi(self):
        if self.db.isOpen():
            self.db.close()

    def prepararCompleterCantonada(self):
        self.dictCantonadesFiltre = self.dictCantonades[self.codiCarrer]
        self.completerCantonada = QCompleter(
            self.dictCantonadesFiltre, self.leNumero)
        self.completerCantonada.setFilterMode(QtCore.Qt.MatchContains)
        self.completerCantonada.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completerCantonada.activated.connect(self.activatCantonada)
        self.leNumero.setCompleter(self.completerCantonada)

    def prepararCompleterCarrer(self):
        # creo instancia de completer que relaciona diccionario de calles con lineEdit
        self.completerCarrer = CompleterAdreces(
            self.dictCarrers, self.leCarrer)
        self.completerCarrer.setFilterMode(QtCore.Qt.MatchContains)
        self.completerCarrer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completerCarrer.activated.connect(self.activatCarrer)
        self.leCarrer.setCompleter(self.completerCarrer)

    def prepararCompleterNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        # afegim el 0 com a "número postal" --> fa referencia a ' '
        if ' ' in self.dictNumerosFiltre:
            self.dictNumerosFiltre['0'] = self.dictNumerosFiltre[' ']
        self.completerNumero = QCompleter(
            self.dictNumerosFiltre, self.leNumero)
        self.completerNumero.activated.connect(self.activatNumero)
        self.completerNumero.setFilterMode(QtCore.Qt.MatchStartsWith)
        self.completerNumero.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(self.completerNumero)
        # El ' ' fa referència al centre del carrer
        # Si només tenim aquest, anem directament allà sense necessitar número
        if len(self.dictNumerosFiltre)==2 and ' ' in self.dictNumerosFiltre:
            self.activatNumero(' ')

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

    def iniAdrecaCantonada(self):
        self.carrerOriginalCantonada = ''
        self.coordCantonada = None
        self.infoCantonada = None
        self.carrerCantonada = ''
        
    def connectarLineEdits(self):
        self.leCarrer.textChanged.connect(self.esborrarNumero)
        try:
            self.leCarrer.editingFinished.connect(self.trobatCarrer)
        except ValueError as e:
            mostrarError(e)
        self.leCarrer.setAlignment(Qt.AlignLeft)

        if self.tipusCerca.currentText() == TipusCerca.ADRECAPOSTAL.value: 
            try:
                self.leNumero.editingFinished.disconnect(self.trobatCantonada)
                self.getCarrerNumeros()
                self.prepararCompleterNumero()
            except:
                pass
            self.leNumero.editingFinished.connect(self.trobatNumero)
        else:
            try:
                self.leNumero.editingFinished.disconnect(self.trobatNumero)
                self.getCarrerCantonades()
                self.prepararCompleterCantonada()
            except:
                pass
            self.leNumero.editingFinished.connect(self.trobatCantonada)

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


    # Obtenir les dades de les cantonades+numeros associats a un carrer

    def getCarrerNumeros(self):
        """
        Obté els números del carrer de la base de dades.

        Realitza una consulta a la base de dades per aconseguir els números corresponents al carrer actual.

        Retorna:
        None
        """

        self.query.prepare(f"""
            SELECT codi,
                CASE num_lletra_post 
                    WHEN '0' THEN ' ' 
                    ELSE num_lletra_post 
                END,
                etrs89_coord_x,
                etrs89_coord_y,
                num_oficial
            FROM Numeros
            WHERE codi = :codiCarrer""")
        self.query.bindValue(":codiCarrer", self.codiCarrer)

        if not self.query.exec_():
            print(self.query.lastError().text())

        while self.query.next():
            row = collections.OrderedDict()
            row['NUM_LLETRA_POST'] = self.query.value(1)  # Numero y Letra
            row['ETRS89_COORD_X'] = self.query.value(2)  # coor x
            row['ETRS89_COORD_Y'] = self.query.value(3)  # coor y
            row['NUM_OFICIAL'] = self.query.value(4)  # numero oficial

            self.dictNumeros[self.codiCarrer][self.query.value(1)] = row

        self.query.finish()

    def getCarrerCantonades(self):
        """
        Obté les cantonades del carrer de la base de dades.

        Realitza una consulta a la base de dades per aconseguir les cantonades corresponents al carrer actual.

        Retorna:
        None
        """
        self.query.prepare(f"""
            SELECT Cantons.CODI_CANTO, 
                Carrers.NOM_OFICIAL, 
                Cantons.ETRS89_COORD_X, 
                Cantons.ETRS89_COORD_Y
            FROM Cantons 
            JOIN Carrers ON Cantons.CODI_CANTO = Carrers.CODI 
            WHERE Cantons.CODI = :codiCarrer""")
        self.query.bindValue(":codiCarrer", self.codiCarrer)

        if not self.query.exec_():
            print("Error getting order with: ", self.query.lastError().text())
            return

        while self.query.next():
            row = collections.OrderedDict()
            row['CODI_CANTO'] = self.query.value(0)
            row['CARRER CANTO'] = self.query.value(1)
            row['ETRS89_COORD_X'] = self.query.value(2)
            row['ETRS89_COORD_Y'] = self.query.value(3)

            self.dictCantonades[self.codiCarrer][self.query.value(1) + "   (" + str(self.query.value(0)) + ")"] = row 
            
        self.query.finish()

    # Venimos del completer, un click en desplegable ....
    def activatCarrer(self, carrer: str) -> Optional[bool]:
        """
        Aquesta funció processa el carrer proporcionat, neteja el nom del carrer i estableix l'adreça si el carrer existeix.
        Si el carrer no existeix o si hi ha hagut un error durant el processament, la funció retorna False.  
        
        Args:
            carrer (str): Nom del carrer a processar.
        
        Returns:
            bool: Retorna None si s'ha pogut processar el carrer, fals altrament.
        """

        self.carrerActivat = True

        carrer=carrer.replace('(var) ','')
        nn = carrer.find(chr(30))
        if nn == -1:
            ss = carrer
        else:
            ss = carrer[0:nn-1]

        self.calle_con_acentos = ss.rstrip()

        self.leCarrer.setAlignment(Qt.AlignLeft)
        self.leCarrer.setText(self.calle_con_acentos)
        self.iniAdreca()
        if carrer in self.dictCarrers:
            self.nomCarrer = carrer
            self.codiCarrer = self.dictCarrers[self.nomCarrer]

            try:

                self.getCarrerCantonades()
                self.getCarrerNumeros()

                if self.tipusCerca.currentText() == TipusCerca.ADRECAPOSTAL.value: 
                    self.prepararCompleterNumero()
                else: 
                    self.prepararCompleterCantonada()
                    
                self.focusANumero()

            except Exception as e:
                mostrarError(e)

        else:
            info = "L'adreça és buida. Codi d'error 1"
            self.sHanTrobatCoordenades.emit(1, info)  # adreça vacia
        self.habilitaLeNum()
        self.focusANumero()

    def trobatCarrer(self) -> Optional[bool]:
        """
        Aquesta funció processa l'actual text del carrer, neteja el nom del carrer i busca l'adreça.
        Si l'adreça no es troba, s'inicialitza l'adreça.
        Si es produeix algun error durant el processament, es gestiona l'excepció i la funció retorna False.
        
        Returns:
            bool: Retorna None si s'ha pogut processar l'adreça, fals altrament.
        """

        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
            return
        if not self.carrerActivat:
            # així obtenim el carrer on estàvem encara que no l'haguem seleccionat explícitament
            self.txto = self.completerCarrer.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completerCarrer.currentCompletion()
            if self.txto == '':
                return

            nn = self.txto.find(chr(30))
            self.txto=self.txto.replace('(var) ','')
            if nn == -1:
                ss = self.txto
            else:
                ss = self.txto[0:nn-1]

            self.calle_con_acentos = ss.rstrip()
            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(self.calle_con_acentos)
            self.iniAdreca()
            if self.txto != self.nomCarrer:
                if self.txto in self.dictCarrers:
                    self.nomCarrer = self.txto
                    self.codiCarrer = self.dictCarrers[self.nomCarrer]
                    self.focusANumero()

                    try:
                        self.getCarrerCantonades()
                        self.getCarrerNumeros()

                        if self.tipusCerca.currentText() == TipusCerca.ADRECAPOSTAL.value: 
                            self.prepararCompleterNumero()
                        else: 
                            self.prepararCompleterCantonada()
                        self.focusANumero()

                    except Exception as e:
                        mostrarError(e)

                else:
                    info = "La direcció no és al diccionari. Codi d'error 2"
                    # direccion no está en diccicionario
                    self.sHanTrobatCoordenades.emit(2, info)
                    self.iniAdreca()
            else:
                info = "Codi d'error 3"
                self.sHanTrobatCoordenades.emit(3, info)  # nunca
        else:
            info = "Adreça buida. Codi d'error 4"
            self.sHanTrobatCoordenades.emit(4, info)  # adreça vac
        
        self.habilitaLeNum()

    def obtenirTextCompletat(self) -> str:
        """
        Retorna el text completat a partir del completerCarrer.

        Returna:
            str: Text completat després de revisar si és buit o no i treure qualsevol ocurrença de '(var)' i espais en blanc.
        """
        textCompletat = self.completerCarrer.popup().currentIndex().data()

        if textCompletat is None:
            textCompletat = self.completerCarrer.currentCompletion()

        return textCompletat.replace('(var)', '').strip()

    def establirCantonadaMapa(self, cantonada: str) -> None:
        """
        Estableix una cantonada al mapa en funció de la cantonada proporcionada.

        Args:
            cantonada (str): La cantonada a establir en el mapa.
        """
        self.numeroCarrer = cantonada
        self.infoAdreca = self.dictCantonadesFiltre[self.numeroCarrer]
        self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), 
                                    float(self.infoAdreca['ETRS89_COORD_Y']))
        self.leNumero.clearFocus()
        self.sHanTrobatCoordenades.emit(0, "[0]")

        if self.leNumero.text() == ' ':
            self.leNumero.clear()

    def comprovarCantonadesCarrer(self, cantonada: str) -> None:
        """
        Comprova la cantonada d'un carrer i llança excepcions si no es troba als carrers especificats o en el filtre d'ubicacions.

        Args:
            cantonada (str): La cantonada del carrer a comprovar.

        Raises:
            ValueError: Si el carrer no es troba als carrers especificats o si la cantonada no es troba en el filtre d'ubicacions.
        """
        self.txto = self.obtenirTextCompletat()
        if self.txto not in self.dictCarrers:
            self.leNumero.clear()
            raise ValueError(f"El carrer {self.txto} no es troba als carrers especificats. Codi d'error 9")

        if cantonada not in self.dictCantonadesFiltre:
            raise ValueError(f"La cantonada {cantonada} no es troba en el filtre d'ubicacions. Codi d'error 8")

    def activatCantonada(self, cantonada: str) -> None:
        """
        Activa una cantonada específica passada com a argument. 

        Args:
            cantonada (str): El nom de la cantonada a activar.
        """
        try:
            self.leNumero.setText(cantonada)
            self.iniAdrecaCantonada() 

            self.comprovarCantonadesCarrer(cantonada)
            self.establirCantonadaMapa(cantonada)
        except Exception as e:
            mostrarError(e)
    
    def trobatCantonada(self) -> None:
        """
        Gestiona la selecció o introducció d'una cantonada només quan l'usuari prem enter.
        """
        if self.comboTipusCerca.currentText() == TipusCerca.CRUILLA.value and self.leNumero.hasFocus():
            try:
                cantonada = self.leNumero.text()
                self.comprovarCantonadesCarrer(cantonada)

                if cantonada:
                    self.iniAdrecaCantonada()
                    if not self.nomCarrer:
                        raise ValueError("Adreça buida. Codi d'error 7")
                
                    if cantonada in self.dictCantonadesFiltre and self.nomCarrer:
                        self.establirCantonadaMapa(cantonada)
                else:
                    raise ValueError("La cantonada no és al diccionari. Codi d'error 6")
            except Exception as e:
                mostrarError(e)
        

    def llegirAdreces(self):
        if self.origen == 'SQLITE':
            ok = self.llegirAdrecesSQlite()
        else:
            ok = False
        return ok

    def llegirAdrecesSQlite(self):
        try:
            index = 0
            self.query.exec_(
                "select codi , nom_oficial , variants  from Carrers")

            while self.query.next():
                codi_carrer = self.query.value(0)  # Codigo calle
                nombre = self.query.value(1)  # numero oficial
                variants = self.query.value(2).lower()  # Variants del nom
                nombre_sin_acentos = self.remove_accents(nombre)
                if nombre == nombre_sin_acentos:
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
            return True
        except Exception as e:
            mostrarError(e)

    # Normalización caracteres quitando acentos

    def remove_accents(self, input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii.decode("utf8")

    def activatNumero(self, txt):
        self.leNumero.setText(txt)
        self.iniAdrecaNumero()
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
            info = "Número de carrer buit. Codi d'error 5"
            self.sHanTrobatCoordenades.emit(5, info)  # numero

    def trobatNumero(self):
        if self.tipusCerca.currentText() != TipusCerca.ADRECAPOSTAL.value: 
            return None
        
        # Si no hi ha carrer, eliminem el completer del número
        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
        if self.leNumero.text() == '':
            return
        try:
            self.txto = self.completerCarrer.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completerCarrer.currentCompletion()
            self.txto=self.txto.replace('(var) ','')
            if self.txto in self.dictCarrers:

                if self.leNumero.text() != '':
                    txt = self.completerNumero.popup().currentIndex().data()
                    if txt is None:
                        txt = self.completerNumero.currentCompletion()
                    self.leNumero.setText(txt)
                else:
                    txt = ' '

                if txt != '':
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
                            info = "El número no és al diccionari. Codi d'error 6"
                            # numero no está en diccicionario
                            self.sHanTrobatCoordenades.emit(6, info)
                    else:
                        info = "L'adreça és buida. Codi d'error 7"
                        self.sHanTrobatCoordenades.emit(
                            7, info)  # adreça vacia  nunca
                else:
                    info = "El número de carrer és en blanc. Codi d'error 8"
                    self.sHanTrobatCoordenades.emit(
                        8, info)  # numero en blanco
            else:
                self.leNumero.clear()
                info = "El número de carrer és en blanc. Codi d'error 9"
                self.sHanTrobatCoordenades.emit(9, info)  # numero en blanco
        except:
            mostrarError(info)

    def focusANumero(self):
        self.leNumero.setFocus()

    def esborrarNumero(self):
        self.calle_con_acentos = ''
        self.leNumero.clear()


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
