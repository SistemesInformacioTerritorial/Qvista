import collections
import itertools
import json
import functools
import re
import sys
import time
import unicodedata
import copy

from PyQt5.QtSql import QSqlDatabase
from moduls.imported.simplekml.featgeom import Geometry
from qgis.core import QgsPointXY, QgsProject, QgsExpressionContextUtils, QgsVectorLayer, QgsWkbTypes, QgsFeature
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsVertexMarker
from qgis.PyQt import QtCore,QtWidgets
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


PREFIX_SEARCH = 'qV_search'


def mostrar_error(e: Exception) -> None:
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
    coordenades_trobades = pyqtSignal(int, 'QString')
    area_trobada = pyqtSignal(int, 'QString')
    punt_trobat = pyqtSignal(int, 'QString')

    def __init__(self, lineEditCarrer, origen='SQLITE', lineEditNumero=None, project=None, comboTipusCerca=None):
        super().__init__()

        self.project = project
        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        if comboTipusCerca:
            self.combo_tipus_cerca = comboTipusCerca

            try:
                self.combo_tipus_cerca.currentIndexChanged.connect(self.connectarLineEdits)
            except ValueError as e:
                print("Error")
        
        self.leNumero.returnPressed.connect(self.trobatCantonada)
        self.leNumero.returnPressed.connect(self.trobatNumero)
        self.leCarrer.textChanged.connect(lambda: self.habilitaLeNum(self.leCarrer.text()))

        self.carrerActivat = False
        self.llistaCerques = []
        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)
        self.dictCantonades = collections.defaultdict(dict)
        self.dictCapa = collections.defaultdict(dict)
        self.dictCapes = collections.defaultdict(dict)

        self.numClick=0
        self.db = QvApp().dbGeo

        if self.db is None:
            QMessageBox.critical(None, "Error al abrir la base de datos.\n\n"
                                "Click para cancelar y salir.", QMessageBox.Cancel)

        self.query = QSqlQuery(self.db)
        self.txto = ''
        self.calle_con_acentos = ''

        if self.llegirAdreces():
            self.prepararCompleterCarrer()
        
        QTimer.singleShot(0, self.connect_layers_removed)
        QTimer.singleShot(0, self.connect_layers_added)

    def set_projecte(self,project):
        self.project = project

    def connect_layers_added(self):
        """
        Connecta el senyal de l'afegit de capes al mètode de gestió corresponent.
        """
        QgsProject.instance().layersAdded.connect(self.layers_added)

    def layers_added(self, layer_ids:list):
        """
        Gestiona l'afegit de noves capes al projecte, afegint les capes pertinents a la cerca.
        
        Args:
            layer_ids (list): Llista d'identificadors de les capes afegides.
        """
        for layer_id in layer_ids:
            obtenir_capes = self.obtenir_variables_qvSearch(layer_id)
            if obtenir_capes:
                for field, desc in obtenir_capes:
                    self.afegir_cerca(layer_id.id(),field,desc)
                    self.combo_tipus_cerca.addItem(desc)
        self.carregar_elements_capes()

    def connect_layers_removed(self):
        """
        Connecta el senyal de la retirada de capes al mètode de gestió corresponent.
        """
        QgsProject.instance().layersRemoved.connect(self.layers_removed)

    def layers_removed(self, layer_ids:list) -> None:
        """
        Gestiona la retirada de capes del projecte, eliminant les capes pertinents de la cerca.
        
        Args:
            layer_ids (list): Llista d'identificadors de les capes retirades.
        """
        layer_str = layer_ids[0]
        for element in self.llistaCerques.copy():
            if element['layer'] == layer_str:
                index = self.combo_tipus_cerca.findText(element['desc'])
                if index >= 0:
                    self.combo_tipus_cerca.removeItem(index)
                self.llistaCerques.remove(element)

    def reset_cerca(self):
        """
        Reinicia la llista de cerques i el combo box de tipus de cerca als valors per defecte.
        """
        self.llistaCerques = []
        self.combo_tipus_cerca.clear()
        self.combo_tipus_cerca.addItems([TipusCerca.ADRECAPOSTAL.value, TipusCerca.CRUILLA.value])


    def afegir_cerca(self, layer_name:str, field_name:str, desc_value:str) -> None:
        """
        Aquesta funció afegeix una nova cerca a la llista de cerques i al comboBox de tipus de cerca.
        """
        values_dict = {
            'layer': layer_name,
            'field': field_name,
            'desc': desc_value
        }
        self.llistaCerques.append(values_dict)

    def obtenir_variables_cerca(self) -> List[str]:
        """
        Aquesta funció obté les variables de cerca del projecte que comencen amb un prefix específic.
        """
        variable_names = QgsExpressionContextUtils.projectScope(self.project).variableNames()
        search_variables = [name for name in variable_names if name.startswith(PREFIX_SEARCH)]
        return sorted(search_variables)

    def processar_variables_projecte(self) -> None:
        """
        Aquesta funció processa les variables de cerca, utilitzant expressions regulars per extreure la capa, el camp i la descripció de cada variable.
        Afegeix cada conjunt de valors a la llista de cerques i afegeix la descripció al comboBox de tipus de cerca.
        """
        search_variables = self.obtenir_variables_cerca()
        
        layer_regex = re.compile(r'layer="([^"]*)"')
        field_regex = re.compile(r'field="([^"]*)"')
        desc_regex = re.compile(r'desc="([^"]*)"')

        for var in search_variables:
            raw_value = QgsExpressionContextUtils.projectScope(self.project).variable(var)

            layer_match = layer_regex.search(raw_value)
            field_match = field_regex.search(raw_value)
            desc_match = desc_regex.search(raw_value)

            if layer_match and field_match and desc_match:
                layer_name = layer_match.group(1)
                layers = QgsProject.instance().mapLayersByName(layer_name)
                if layers:
                    layer_id = layers[0].id()
                    self.afegir_cerca(layer_id, field_match.group(1), desc_match.group(1))
                    self.combo_tipus_cerca.addItem(desc_match.group(1))
                    self.afegir_elements_capa_qvSearch(layer_id)
                else:
                    print(f"No existeix la capa {layer_name}")
            else:
                print(f"Error en carregar el contingut de la capa {var}")


    def carregar_totes_capes(self) -> None:
        """
        Aquesta funció carrega totes les capes del projecte de QGIS que encara no s'han afegit a la llista de cerques.
        """
        for layer in QgsProject.instance().mapLayers().values():
            layer_id = layer.id()

            if not any(search['layer'] == layer_id for search in self.llistaCerques):
                self.afegir_elements_capa_qvSearch(layer_id)

    def obtenir_variables_qvSearch(self, capa: QgsVectorLayer) -> Optional[tuple[str,str]]:
        """
        Obté totes les variables que comencen amb PREFIX_SEARCH d'una capa donada.
        
        Args:
            capa (QgsVectorLayer): La capa de la qual obtenir les variables.
        
        Returns:
            Optional[tuple[str,str]]: Una llista de tuples amb les parelles (field, desc) de les variables trobades,
                                    o None si no es troba cap variable que comenci amb PREFIX_SEARCH.
        """

        totes_variables = QgsExpressionContextUtils.layerScope(capa).variableNames()
        resultats = []

        for nom_variable in totes_variables:
            if nom_variable.startswith(PREFIX_SEARCH):
                valor_variable = QgsExpressionContextUtils.layerScope(capa).variable(nom_variable)

                field_regex = re.compile(r'field="([^"]*)"')
                desc_regex = re.compile(r'desc="([^"]*)"')
                field_match = field_regex.search(valor_variable)
                desc_match = desc_regex.search(valor_variable)

                if field_match and desc_match:
                    resultats.append((field_match.group(1), desc_match.group(1)))
                else:
                    print(f"Error amb en carregar la variable {nom_variable}")

        return resultats if resultats else None

    def afegir_elements_capa_qvSearch(self, id_capa:str) -> None:
        """
        Afegeix elements d'una capa específica a la llista de cerques i al combo box de tipus de cerca.
        
        Args:
            id_capa (str): Identificador de la capa de la qual s'han d'afegir els elements.
        """
        capa = QgsProject.instance().mapLayer(id_capa)
        if not capa:
            return
        resultats = self.obtenir_variables_qvSearch(capa)
        if not resultats:
            return
        for resultat in resultats:
            self.afegir_cerca(id_capa, resultat[0], resultat[1])
            self.combo_tipus_cerca.addItem(resultat[1])
            


    def carregar_tipus_cerques(self) -> None:
        """
        Aquesta funció carrega els tipus de cerques disponibles a partir de les variables del projecte que comencen amb un prefix específic.
        """
        self.reset_cerca()
        self.processar_variables_projecte()
        self.carregar_totes_capes()
        self.carregar_elements_capes()

    def carregar_elements_capes(self) -> None:
        """
        Aquesta funció carrega les capes especificades en la llista de cerques.
        Per a cada element de la llista, crida a `getElementsCapa` amb el nom de la capa i l'identificador 'fid'.
        També manté un comptador de la posició que s'incrementa amb cada iteració.
        """
        posicio = 1
        for variable in self.llistaCerques:
            capa = QgsProject.instance().mapLayers().get(variable['layer'])
            if not capa:
                return

            dict_capa_local = {}
            element_cerca = variable['field']
            for element in capa.getFeatures():
                id_element = str(element.id())
                atribut_element = element.attribute(element_cerca)
                dict_capa_local[id_element] = atribut_element
            self.dictCapes[posicio] = dict_capa_local
            posicio += 1


    def habilitaLeNum(self, valor_antic):
        self.carrerActivat = False
        condicio_per_habilitar = valor_antic in self.dictCarrers
        self.leNumero.setEnabled(condicio_per_habilitar)

    def cercadorAdrecaFi(self):
        if self.db.isOpen():
            self.db.close()

    def prepararCompleterAltres(self):
        """
        Prepara el completador per a la caixa de text de la cerca, basant-se en les claus del diccionari invers de capes.
        """
        self.dictCapaInvers = {str(valor).replace('<br>', ' '): clau for clau, valor in self.dictCapa.items()}
        self.completerAltres = QCompleter(list(self.dictCapaInvers.keys()), self.leCarrer)
        self.completerAltres.setFilterMode(QtCore.Qt.MatchContains)
        self.completerAltres.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completerAltres.activated.connect(self.activatAltres)
        self.leCarrer.setCompleter(self.completerAltres)

    def prepararCompleterCantonada(self):
        self.dictCantonadesFiltre = self.dictCantonades [self.codiCarrer]
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
        """
        Aquesta funció estableix les connexions necessàries pels LineEdits de carrers i números.
        Connecta el senyal 'textChanged' del LineEdit de carrers amb la funció `esborrarNumero`.
        Després crida a `connectarLineEditsCarrer` per establir connexions addicionals basades en el tipus de cerca.
        Finalment, ajusta l'alineació del text del LineEdit de carrers a l'esquerra i crida a `connectarLineEditsNumero` per a més configuracions.

        """
        self.leCarrer.textChanged.connect(self.esborrarNumero)

        try:
            self.leCarrer.editingFinished.disconnect()
        except:
            pass

        self.connectarLineEditsCarrer()

        self.leCarrer.setAlignment(Qt.AlignLeft)
        self.connectarLineEditsNumero()

    def get_tipus_cerca(self) -> Optional[str]:
        """
        Intenta obtenir el text actual del comboBox. Si el comboBox no existeix,
        retorna el valor predeterminat de TipusCerca.ADRECAPOSTAL.

        Returns:
            str: El tipus de cerca actual. Si el comboBox no està definit,
                retorna el valor `ADRECAPOSTAL` de l'enumeració `TipusCerca`.
        """
        try:
            return self.combo_tipus_cerca.currentText()
        except AttributeError:
            return TipusCerca.ADRECAPOSTAL.value
        

    def connectarLineEditsCarrer(self):
        """
        Aquesta funció desconnecta qualsevol senyal previ de 'editingFinished' del LineEdit de carrers i estableix una nova connexió basada en el tipus de cerca seleccionat.
        Si el tipus de cerca és TipusCerca.ADRECAPOSTAL.value o TipusCerca.CRUILLA.value, intenta preparar l'autocompletar per a carrers.
        Si el tipus de cerca és diferent i no està buit, obté la posició del tipus de cerca, actualitza el diccionari de capes i prepara l'autocompletar per a altres tipus de cerques.
        En cas d'error, es mostra un missatge d'error.

        Raises:
            Exception: Si hi ha un error en desconnectar els senyals o en preparar l'autocompletar.
            ValueError: Si hi ha un error en obtenir la posició del tipus de cerca o en actualitzar el diccionari de capes.
        """
        if self.get_tipus_cerca() in [TipusCerca.ADRECAPOSTAL.value,TipusCerca.CRUILLA.value]:
            try:
                self.prepararCompleterCarrer()
            except Exception as e:
                mostrar_error(e)
            self.leCarrer.editingFinished.connect(self.trobatCarrer)
        elif self.get_tipus_cerca() != '':
            try:
                self.iniAdreca()
                index_tipus_cerca = self.obt_posicio_capa()
                self.dictCapa = self.dictCapes[index_tipus_cerca]
                self.prepararCompleterAltres()
            except ValueError as e:
                mostrar_error(e)
            self.leCarrer.editingFinished.connect(self.trobatAltres)


    def connectarLineEditsNumero(self):
        """
        Aquesta funció configura els connectadors per als LineEdits de números basant-se en el tipus de cerca seleccionat.
        Si el tipus de cerca és TipusCerca.ADRECAPOSTAL.value, intenta obtenir els números del carrer i preparar l'autocompletar.
        Si es produeix un error de valor, es mostra un missatge d'error.
        Si el tipus de cerca és TipusCerca.CRUILLA.value, intenta obtenir les cantonades del carrer i preparar l'autocompletar.
        En qualsevol cas, connecta el senyal 'editingFinished' del LineEdit de números amb la funció corresponent per processar la cerca realitzada.

        Raises:
            ValueError: Si hi ha un error en obtenir les dades necessàries per a l'autocompletar.

        """
        if self.get_tipus_cerca() == TipusCerca.ADRECAPOSTAL.value and hasattr(self, 'codiCarrer'): 
            try:
                self.getCarrerNumeros()
                self.prepararCompleterNumero()
            except ValueError as e:
                mostrar_error(e)
            self.leNumero.editingFinished.connect(self.trobatNumero)
        elif self.get_tipus_cerca() == TipusCerca.CRUILLA.value and hasattr(self, 'codiCarrer'):
            try:
                self.getCarrerCantonades()
                self.prepararCompleterCantonada()
            except ValueError as e:
                mostrar_error(e)
            self.leNumero.editingFinished.connect(self.trobatCantonada)


                
    def obt_posicio_capa(self):
        """
        Aquesta funció cerca dins de la llista de cerques (qComboBox) i retorna la posició de l'element a dictCapes (que és on es carreguen els elements de les capes)

        Returns:
            int: La posició de l'element coincident dins de la llista de cerques, o None si no es troba cap coincidència.
        """
        index = 0
        while index < len(self.llistaCerques):
            if self.get_tipus_cerca() == self.llistaCerques[index]['desc']:
                return index+1
            index += 1
        return None

    
    def getLayer(self) -> Optional[str]:
        """
        Retorna el nom de la capa associada amb la descripció seleccionada al comboBox.

        Retorna:
        - str: El nom de la capa si es troba una coincidència.
        - None: Si no es troba cap coincidència després d'iterar sobre tota la llista.
        """
        index = 0
        while index < len(self.llistaCerques):
            if self.get_tipus_cerca() == self.llistaCerques[index]['desc']:
                id_capa = self.llistaCerques[index]['layer']
                return QgsProject.instance().mapLayers().get(id_capa).name()
            index += 1
        return None



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
            row['NUM_LLETRA_POST'] = self.query.value(1)
            row['ETRS89_COORD_X'] = self.query.value(2)
            row['ETRS89_COORD_Y'] = self.query.value(3)
            row['NUM_OFICIAL'] = self.query.value(4)

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


    def activatAltres(self, element: str):
        """
        Aquesta funció activa l'element especificat, actualitza l'interfície d'usuari per reflectir l'element actiu i inicialitza l'adreça.
        Si l'element està present en el diccionari `dictCapa`, també estableix el nom de l'element.

        Args:
            element (str): L'element a activar i mostrar en l'interfície d'usuari.

        Returns:
            bool: Retorna True si l'element està en `dictCapa` i s'ha activat correctament, False altrament.
        """
        self.carrerActivat = True
        if element in self.dictCapaInvers:
            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(element)
            self.iniAdreca()
            self.txto = element
            self.get_tipus_geometria()


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

        carrerAntic = carrer
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

                if self.get_tipus_cerca() == TipusCerca.ADRECAPOSTAL.value: 
                    self.prepararCompleterNumero()
                else:
                    self.prepararCompleterCantonada()

                self.focusANumero()

            except Exception as e:
                mostrar_error(e)

        else:
            info = "L'adreça és buida. Codi d'error 1"
            self.coordenades_trobades.emit(1, info)
        self.habilitaLeNum(carrerAntic)
        self.focusANumero()

    def trobatAltres(self) -> Optional[bool]:
        if self.leCarrer.text() == '':
            return
        if not self.carrerActivat:
            self.txto = self.completerAltres.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completerAltres.currentCompletion()
            if self.txto == '':
                return
            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(self.txto)
            self.iniAdreca()
            self.get_tipus_geometria()


    def trobatCarrer(self) -> Optional[bool]:
        """
        Aquesta funció processa l'actual text del carrer, neteja el nom del carrer i busca l'adreça.
        Si l'adreça no es troba, s'inicialitza l'adreça.
        Si es produeix algun error durant el processament, es gestiona l'excepció i la funció retorna False.

        Returns:
            bool: Retorna None si s'ha pogut processar l'adreça, fals altrament.
        """

        txtoAntic = ''
        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
            return
        if not self.carrerActivat:
            self.txto = self.completerCarrer.popup().currentIndex().data()
            txtoAntic = self.txto
            if self.txto is None:
                return
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

                        if self.get_tipus_cerca() == TipusCerca.ADRECAPOSTAL.value: 
                            self.prepararCompleterNumero()
                        else:
                            self.prepararCompleterCantonada()
                        self.focusANumero()

                    except Exception as e:
                        mostrar_error(e)

                else:
                    info = "La direcció no és al diccionari. Codi d'error 2"
                    self.coordenades_trobades.emit(2, info)
                    self.iniAdreca()
            else:
                info = "Codi d'error 3"
                self.coordenades_trobades.emit(3, info)
        else:
            info = "L'adreça és buida. Codi d'error 1"
            self.coordenades_trobades.emit(1, info)
        
        self.habilitaLeNum(txtoAntic)

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
        self.coordenades_trobades.emit(0, "[0]")

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
            raise ValueError(f"El carrer {self.txto} no es troba als carrers especificats. Codi d'error 7")

        if cantonada not in self.dictCantonadesFiltre:
            raise ValueError(f"La cantonada {cantonada} no es troba en el filtre d'ubicacions. Codi d'error 6")

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
            mostrar_error(e)
    
    def trobatCantonada(self) -> None:
        """
        Gestiona la selecció o introducció d'una cantonada només quan l'usuari prem enter.
        """
        if self.get_tipus_cerca() == TipusCerca.CRUILLA.value and self.leNumero.hasFocus():
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
                mostrar_error(e)
        

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
                codi_carrer = self.query.value(0)
                nombre = self.query.value(1)
                variants = self.query.value(2).lower()
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
            mostrar_error(e)

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
            self.txto = ''
        else:
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
                self.coordenades_trobades.emit(0, info)
                self.leNumero.clear()

        else:
            info = "El número és buit. Codi d'error 4"
            self.coordenades_trobades.emit(4, info)

    def trobatNumero(self):
        if self.get_tipus_cerca() != TipusCerca.ADRECAPOSTAL.value: 
            return None
        
        if self.leCarrer.text() == '':
            self.leNumero.setCompleter(None)
        if self.leNumero.text() == '':
            return
        try:
            self.txto = self.completerCarrer.popup().currentIndex().data()
            if self.txto is None:
                self.txto = ''
            else:
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
                            self.coordenades_trobades.emit(0, info)
                            self.leNumero.clear()

                        else:
                            info = "El número no és al diccionari. Codi d'error 5"
                            self.coordenades_trobades.emit(5, info)
                    else:
                        info = "El número és buit. Codi d'error 4"
                        self.coordenades_trobades.emit(
                            4, info)
                else:
                    info = "El número està en blanc. Codi d'error 6"
                    self.coordenades_trobades.emit(6, info)
            else:
                self.leNumero.clear()
                info = "El número és en blanc. Codi d'error 6"
                self.coordenades_trobades.emit(6, info)
        except:
            mostrar_error(info)

    def focusANumero(self):
        self.leNumero.setFocus()

    def esborrarNumero(self):
        self.calle_con_acentos = ''
        self.leNumero.clear()

    def get_tipus_geometria(self):
        """
        Determina la geometria de l'element seleccionat a partir de l'index i actualitza les coordenades d'adreça.
        
        Raises:
            ValueError: Si 'self.txto' no es pot convertir a enter o si l'índex està fora de rang.
            AttributeError: Si el tipus de geometria no és reconegut o no es pot convertir adequadament.
        """
        try:
            layer = self.get_layer()
            feature = self.get_feature(layer)
            self.update_address_coordinates(feature)
        except ValueError as e:
            mostrar_error(e)
        except AttributeError as e:
            mostrar_error(e)


    def get_layer(self) -> QgsVectorLayer:
        """
        Obté la capa actual del projecte.
        
        Returns:
            QgsMapLayer: La capa actual del projecte.
        Raises:
            ValueError: Si no es troba cap capa amb el nom proporcionat.
        """
        layer_name = self.getLayer()
        if layer_name is None:
            mostrar_error("No s'ha trobat cap capa amb el nom proporcionat.")
        return self.project.mapLayersByName(layer_name)[0]

    def get_feature(self, layer:QgsVectorLayer) -> QgsFeature:
        """
        Recupera la característica de la capa basada en l'índex proporcionat.
        
        Args:
            layer (QgsVectorLayer): La capa de la qual recuperar la característica.
        
        Returns:
            QgsFeature: La característica recuperada.
        
        Raises:
            ValueError: Si 'self.txto' no es pot convertir a enter o si l'índex està fora de rang.
        """
        index = int(self.dictCapaInvers.get(self.txto)) - 1

        features = list(layer.getFeatures())
        if index < -1 or index >= len(features):
            mostrar_error("L'índex està fora de rang.")
        
        return features[index]

    def update_address_coordinates(self, feature: QgsFeature):
        """
        Actualitza les coordenades d'adreça basant-se en la geometria de la característica.
        
        Args:
            feature (QgsFeature): La característica de la qual obtenir la geometria.
        
        Raises:
            AttributeError: Si el tipus de geometria no és reconegut o no es pot convertir adequadament.
        """
        geometria = feature.geometry()
        if geometria.type() == QgsWkbTypes.PolygonGeometry:
            self.coordAdreca = geometria
            self.area_trobada.emit(0, "")
        elif geometria.type() == QgsWkbTypes.LineGeometry:
            self.coordAdreca = geometria
            self.punt_trobat.emit(0,"")
        elif geometria.wkbType() == QgsWkbTypes.Point:
            punt = geometria.asPoint()
            self.coordAdreca = QgsPointXY(punt.x(), punt.y())
            self.coordenades_trobades.emit(0, "")
        elif geometria.wkbType() == QgsWkbTypes.MultiPoint:
            punts = geometria.asMultiPoint()
            if punts:
                punt = punts[0]
                self.coordAdreca = QgsPointXY(punt.x(), punt.y())
                self.coordenades_trobades.emit(0, "")
        else:
            mostrar_error("Tipus de geometria no reconegut")


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
        cercador.coordenades_trobades.connect(trobat)
        cercador.area_trobada.connect(trobat)

        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        wid.show()
