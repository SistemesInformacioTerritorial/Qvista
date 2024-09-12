import collections
import itertools
import json
import functools
import re
import unicodedata

from moduls.imported.simplekml.featgeom import Geometry
from qgis.core import QgsPointXY, QgsProject, QgsExpressionContextUtils, QgsVectorLayer, QgsWkbTypes, QgsFeature
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsVertexMarker
from qgis.PyQt import QtCore,QtWidgets
from qgis.PyQt.QtCore import QObject, Qt, pyqtSignal, QSortFilterProxyModel, QStringListModel, QModelIndex
from qgis.PyQt.QtGui import QColor, QValidator
from qgis.PyQt.QtSql import QSqlQuery,QSqlDatabase
from qgis.PyQt.QtWidgets import (QCompleter, QHBoxLayout, QLineEdit,
                                 QMessageBox, QStyleFactory, QVBoxLayout,
                                 QWidget)

from moduls.QvApp import QvApp
from typing import Dict, List,Optional, Tuple, Union
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

class CarrerCompleterModel(QSortFilterProxyModel):
    def __init__(self, dict_capa_tupla: dict, parent: QObject = None):
        """
        Inicialitza el model de filtrat per al completador amb un diccionari de carrers.

        Args:
            dict_capa_tupla (dict): Diccionari que relaciona identificadors de carrers (str) amb noms de carrers (str).
            parent (QObject, optional): Widget pare del model. Defaults to None.
        """
        super().__init__(parent)
        self.dict_capa_tupla = dict_capa_tupla
        self.last_returned = None

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Determina si la fila especificada ha de ser inclosa en el model.

        Args:
            source_row (int): Índex de la fila a comprovar.
            source_parent (QModelIndex): Índex del pare de la fila a comprovar.

        Returns:
            bool: True si el nom del carrer està present en el diccionari de carrers, False en cas contrari.
        """
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        return model.data(index, Qt.DisplayRole) in self.dict_capa_tupla.keys()

    def data(self, index: QModelIndex, role: int) -> tuple[str]:
        """
        Proporciona les dades del carrer corresponent per a l'índex i rol especificats.

        Args:
            index (QModelIndex): Índex de la dada a retornar.
            role (int): Rol de les dades a retornar.

        Returns:
            str: El nom del carrer associat a l'identificador si el rol és DisplayRole, en cas contrari, retorna el valor per defecte.
        """
        if role == Qt.DisplayRole:
            id_carrer = self.sourceModel().data(index, Qt.DisplayRole)
            valor = self.dict_capa_tupla.get(id_carrer, "")
            self.last_returned = (valor, id_carrer)
            return valor
        return super().data(index, role)


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
        self.llista_cerques = []
        self.dict_carrers = {}
        self.dictNumeros = collections.defaultdict(dict)
        self.dictCantonades = collections.defaultdict(dict)
        self.dict_capa = collections.defaultdict(dict)
        self.dict_capes = collections.defaultdict(dict)

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
        QgsProject.instance().layersAdded.connect(self.modify_layers)

    def modify_layers(self):
        """
        Gestiona l'afegit/eliminació de noves capes al projecte, afegint les capes pertinents a la cerca.
        """
        self.carregar_tipus_cerques()

    def connect_layers_removed(self):
        """
        Connecta el senyal de la retirada de capes al mètode de gestió corresponent.
        """
        QgsProject.instance().layersRemoved.connect(self.modify_layers)

    def reset_cerca(self):
        """
        Reinicia la llista de cerques i el combo box de tipus de cerca als valors per defecte.
        """
        self.llista_cerques = []
        if hasattr(self, "combo_tipus_cerca"):
            self.combo_tipus_cerca.clear()
            self.combo_tipus_cerca.addItems([TipusCerca.ADRECAPOSTAL.value, TipusCerca.CRUILLA.value])
            self.combo_tipus_cerca.setItemData(0, "Cerca per adreça postal", Qt.ToolTipRole)
            self.combo_tipus_cerca.setItemData(1, "Cerca per cruilla", Qt.ToolTipRole)

    def obtenir_variables_projecte(self) -> List[str]:
        """
        Obté les variables de cerca del projecte que comencen amb un prefix específic.
        """
        variable_names = QgsExpressionContextUtils.projectScope(self.project).variableNames()
        search_variables = [name for name in variable_names if name.startswith(PREFIX_SEARCH)]
        return sorted(search_variables)

    def processar_variables_projecte(self) -> None:
        """
        Processa les variables de cerca, utilitzant expressions regulars per extreure la capa, el camp i la descripció de cada variable.
        Afegeix cada conjunt de valors a la llista de cerques i afegeix la descripció al comboBox de tipus de cerca.
        """
        search_variables = self.obtenir_variables_projecte()

        for var in search_variables:
            raw_value = QgsExpressionContextUtils.projectScope(self.project).variable(var)
            matches = self.regex_variables(raw_value)
            matches['nom_variable'] = var
            #Cal ficar-lo perquè si venim de capa layer_net!=layer i cal per carregar capa si variable capa, malgrat que aqui sigui igual
            matches['layer_net'] = matches['layer']
            if matches['layer'] and matches['field']:
                self.carregar_variables_projecte(matches)

    def regex_variables(self, variable: str, id_capa: str = None) -> Dict[str, str]:
        """
        Retorna una diccionari a partir de l'obtingut sobre un text via regex

        Args:
            value (str): Text on es buscaran els patrons.
            id_capa (str): Id de la capa si hi és

        Returns:
            Dict[str, str]: Diccionari amb el contingut obtingut via regex
        """
        layer_regex = re.compile(r'layer="([^"]*)"')
        field_regex = re.compile(r'field="([^"]*)"')
        desc_regex = re.compile(r'desc="([^"]*)"')
        fieldtext_regex = re.compile(r'fieldtext="([^"]*)"')

        layer_match = layer_regex.search(variable)
        field_match = field_regex.search(variable)
        desc_match = desc_regex.search(variable)
        fieldtext_match = fieldtext_regex.search(variable)

        if not id_capa:
            id_capa = layer_match.group(1)

        return {
            "layer": id_capa,
            "field": field_match.group(1),
            "desc": desc_match.group(1),
            "fieldtext": fieldtext_match.group(1) if fieldtext_match else None
        }

    def carregar_variables_projecte(self, variable: Dict[str, str]) -> None:
        """
        Carrega les variables de projecte especificades en 'matches' i actualitza la llista de cerques i la interfície d'usuari.

        Args:
            matches (Dict[str, str]): Diccionari amb les dades de la cerca, incloent la capa, el camp, la descripció i el camp de text.
        """

        error = {}
        hi_ha_error = False
        capa = QgsProject.instance().mapLayersByName(variable['layer'])
        clau_errors_de_carrega = 'projecte' + '-' + variable['layer_net'] + '-' + variable['nom_variable']
        if capa:
            hi_ha_error = self.hi_ha_error_carregar_variable(variable, capa[0], clau_errors_de_carrega, 'projecte')
            if not hi_ha_error:
                variable['layer'] = capa[0].id()
                self.llista_cerques.append(variable)
                index = self.combo_tipus_cerca.count()
                self.combo_tipus_cerca.addItem(variable['desc'])
                self.combo_tipus_cerca.setItemData(index, f"Capa: {capa[0].name()}", Qt.ToolTipRole)
        else:
            error['layer'] = f"Error en carregar la variable {variable['nom_variable']}, que és una variable de PROJECTE, ja que no existeix la capa {variable['layer']}"
            self.errors_de_carrega[clau_errors_de_carrega] = error


    def carregar_totes_capes(self) -> None:
        """
        Carrega totes les capes del projecte de QGIS que encara no s'han afegit a la llista de cerques.
        """
        for layer in QgsProject.instance().mapLayers().values():
            layer_id = layer.id()
            self.afegir_elements_capa_qvSearch(layer_id)

    def obtenir_variables_capa(self, capa: QgsVectorLayer) -> Optional[List[Dict[str,str]]]:
        """
        Obté totes les variables que comencen amb PREFIX_SEARCH d'una capa donada.

        Args:
            capa (QgsVectorLayer): La capa de la qual obtenir les variables.
            id_capa (str): El nom de la capa on afegim les variables

        Returns:
            Optional[list[Dict[str,str]]]: Una llista de diccionaris amb layer,field,desc,field_nom o None si no trobem cap variable que comenci per PREFIX_SEARCH.
        """

        totes_variables = QgsExpressionContextUtils.layerScope(capa).variableNames()
        resultats = []

        for nom_variable in totes_variables:
            if nom_variable.startswith(PREFIX_SEARCH):
                valor_variable = QgsExpressionContextUtils.layerScope(capa).variable(nom_variable)
                conjunt_elements = self.regex_variables(valor_variable, capa.id())
                conjunt_elements['nom_variable'] = nom_variable
                conjunt_elements['layer_net'] = capa.name()
                resultats.append(conjunt_elements)


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
        resultats = self.obtenir_variables_capa(capa)
        if not resultats:
            return
        for variable in resultats:
            clau_errors_de_carrega = 'projecte' + '-' + variable['layer_net'] + '-' + variable['nom_variable']
            hi_ha_error = self.hi_ha_error_carregar_variable(variable, capa, clau_errors_de_carrega, 'capa')
            if not hi_ha_error:
                self.llista_cerques.append(variable)
                index = self.combo_tipus_cerca.count()
                self.combo_tipus_cerca.addItem(variable['desc'])
                self.combo_tipus_cerca.setItemData(index, f"Capa: {capa.name()}", Qt.ToolTipRole)


    def carregar_tipus_cerques(self) -> None:
        """
        Carrega els tipus de cerques disponibles a partir de les variables del projecte que comencen amb un prefix específic.
        """
        self.errors_de_carrega = {}
        self.reset_cerca()
        self.processar_variables_projecte()
        self.carregar_totes_capes()
        self.carregar_elements_capes()

    def hi_ha_error_carregar_variable(self, variable:Dict[str,str], capa:QgsVectorLayer, clau_errors_de_carrega:str, procedencia:str) -> bool:
        """
        Comprova si hi ha errors en carregar una variable d'una capa vectorial de QGIS.

        Args:
            variable (Dict[str,str]): Diccionari que conté informació sobre la variable, incloent els camps 'field' i 'fieldtext'.
            capa (QgsVectorLayer): La capa vectorial de QGIS de la qual es volen obtenir els valors.
            clau_errors_de_carrega (str): La clau del diccionari que omplirem si hi ha cap error.
            procedencia(str): Capa si és variable de capa o projecte si és variable de projecte.

        Returns:
            bool: True si hi ha errors, False en cas contrari.
        """
        error = {}
        try:
            next(capa.getFeatures()).attribute(variable['field'])
        except KeyError as e:
            error['error_field'] = f"Error en carregar la variable {variable['nom_variable']} de la capa: {variable['layer_net']} que és una variable de {procedencia.upper()}, en el paràmetre FIELD que té el valor de {e}, i aquesta columna no existeix"

        if not variable.get('desc'):
            error["desc"] = f"Error en carregar la variable {variable['nom_variable']} amb layer: {variable['layer_net']} que és una variable de {procedencia.upper()}, i té el paràmetre de DESCRIPCIÓ buit"

        if variable.get('fieldtext'):
            try:
                next(capa.getFeatures()).attribute(variable['fieldtext'])
            except KeyError as e:
                error['error_fieldtext'] = f"Error en carregar la variable {variable['nom_variable']} de la capa: {variable['layer_net']} que és una variable de {procedencia.upper()}, en el paràmetre FIELDTEXT que té el valor de {e}, i aquesta columna no existeix"

        if error:
            self.errors_de_carrega[clau_errors_de_carrega] = error
            return True
        return False


    def obtenir_valors_capes(self, variable: str, capa: QgsVectorLayer) -> Dict[str, Union[str, Tuple[str, str]]]:
        """
        Obté els valors d'una variable específica de les entitats d'una capa vectorial de QGIS.

        Args:
            variable (str): Un diccionari amb 'field' amb el nom del camp a obtenir,
                            i opcionalment amb 'fieldtext' amb el nom d'un segon camp a obtenir.
            capa (QgsVectorLayer): La capa vectorial de QGIS de la qual s'obtenen els valors.

        Returns:
            Dict[str, Union[str, Tuple[str, str]]]: Diccionari amb els valors dels camps especificats.
        """
        dict_capa_local = {}

        for element in capa.getFeatures():
            id_element = str(element.id())
            field_value = element.attribute(variable['field'])

            if variable.get('fieldtext'):
                fieldtext_value = element.attribute(variable['fieldtext'])
                dict_capa_local[id_element] = (field_value, fieldtext_value)
            else:
                dict_capa_local[id_element] = field_value
        return dict_capa_local


    def carregar_elements_capes(self) -> None:
        """
        Carrega els elements de les capes especificades en la llista de cerques de la instància.
        """
        hi_ha_error=False
        posicio = 1
        for variable in self.llista_cerques:
            capa = QgsProject.instance().mapLayers().get(variable['layer']) #si ho fessim amb variable['layer_net'], ERROR
            if not capa:
                return

            dict_capa_local = self.obtenir_valors_capes(variable, capa)
            self.dict_capes[posicio] = dict_capa_local
            posicio += 1

    def habilitaLeNum(self, valor_antic):
        self.carrerActivat = False
        condicio_per_habilitar = valor_antic in self.dict_carrers
        self.leNumero.setEnabled(condicio_per_habilitar)

    def cercadorAdrecaFi(self):
        if self.db.isOpen():
            self.db.close()

    def prepararCompleterAltres(self):
        """
        Configura el QCompleter per a 'LineEdit' si existeix la variable 'fieldtext'. Si la variable s'ha proporcionat,
        el valor és una tupla amb dos elements, i es requereix un QCompleter personalitzat que permeti escriure un element i seleccionar l'altre.
        Si no s'ha proporcionat la variable, el valor és únic i s'utilitza un QCompleter estàndard.
        """

        self.dict_capa_invers = {}
        self.dict_capa_tupla = {}

        dict_value = next(iter(self.dict_capa.values()))
        self.te_field_text = isinstance(dict_value, tuple)

        for clau, valor in self.dict_capa.items():
            if isinstance(valor, tuple):
                self.dict_capa_invers[str(valor[0]).replace('<br>', ' ')] = clau
                self.dict_capa_tupla[str(valor[0])] = str(valor[1]).replace('<br>', ' ')
            else:
                self.dict_capa_invers[str(valor).replace('<br>', ' ')] = clau

        if self.te_field_text:
            model = QStringListModel(list(self.dict_capa_tupla.keys()), self)
            self.proxy_model = CarrerCompleterModel(self.dict_capa_tupla, self)
            self.proxy_model.setSourceModel(model)
            self.completer_altres = QCompleter(self.proxy_model, self.leCarrer)
        else:
            self.completer_altres = QCompleter(list(self.dict_capa_invers.keys()), self.leCarrer)

        self.completer_altres.setFilterMode(QtCore.Qt.MatchContains)
        self.completer_altres.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer_altres.activated.connect(self.activatAltres)
        self.leCarrer.setCompleter(self.completer_altres)

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
            self.dict_carrers, self.leCarrer)
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
        Estableix les connexions necessàries pels LineEdits de carrers i números.
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
        Desconnecta qualsevol senyal previ de 'editingFinished' del LineEdit de carrers i estableix una nova connexió basada en el tipus de cerca seleccionat.
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
                index_tipus_cerca = self.get_posicio_capa()
                self.dict_capa = self.dict_capes[index_tipus_cerca]
                self.prepararCompleterAltres()
            except ValueError as e:
                mostrar_error(e)
            self.leCarrer.editingFinished.connect(self.trobat_altres)


    def connectarLineEditsNumero(self):
        """
        Configura els connectadors per als LineEdits de números basant-se en el tipus de cerca seleccionat.
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

    def get_posicio_capa(self):
        """
        Cerca dins de la llista de cerques (qComboBox) i retorna la posició de l'element a dictCapes (que és on es carreguen els elements de les capes)

        Returns:
            int: La posició de l'element coincident dins de la llista de cerques, o None si no es troba cap coincidència.
        """
        for index,cerca in enumerate(self.llista_cerques):
            if self.get_tipus_cerca() == cerca['desc']:
                return index+1
        return None


    def get_nom_layer(self) -> Optional[str]:
        """
        Retorna el nom de la capa associada amb la descripció seleccionada al comboBox.

        Retorna:
        - str: El nom de la capa si es troba una coincidència.
        - None: Si no es troba cap coincidència després d'iterar sobre tota la llista.
        """
        for cerca in self.llista_cerques:
            if self.get_tipus_cerca() == cerca['desc']:
                id_capa = cerca['layer']
                return QgsProject.instance().mapLayers().get(id_capa).name()
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
        Activa l'element especificat, actualitza l'interfície d'usuari per reflectir l'element actiu i inicialitza l'adreça.
        Si l'element està present en el diccionari `dictCapa`, també estableix el nom de l'element.

        Args:
            element (str): L'element a activar i mostrar en l'interfície d'usuari.

        Returns:
            bool: Retorna True si l'element està en `dictCapa` i s'ha activat correctament, False altrament.
        """
        self.carrerActivat = True
        if element in self.dict_capa_invers:
            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(element)
            self.iniAdreca()
            self.txto = element
            self.get_tipus_geometria()


    # Venimos del completer, un click en desplegable ....
    def activatCarrer(self, carrer: str) -> Optional[bool]:
        """
        Processa el carrer proporcionat, neteja el nom del carrer i estableix l'adreça si el carrer existeix.
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
        if carrer in self.dict_carrers:
            self.nomCarrer = carrer
            self.codiCarrer = self.dict_carrers[self.nomCarrer]

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

    def trobat_altres(self) -> None:
        """
        Gestiona la selecció d'elements en un autocompletador i actualitza l'interfície d'usuari
        """
        if self.te_field_text:
            # Si entrem aquí a partir del QCompleter personalitzat haurem de passar a activatAltres perquè per defecte obtenim fieldtext i no field
            # (ex del que pot passar: el nomCarrer a partir d'idCarrer, però pot passar que un carrer tingui N idCarrers, essent field=ID i textfield=NOM)
            if self.completer_altres.popup().currentIndex().data() is None:
                return
            _, id_carrer = self.proxy_model.last_returned
            self.activatAltres(id_carrer)
            return
        if self.leCarrer.text() == '':
            return
        if not self.carrerActivat:
            self.txto = self.completer_altres.popup().currentIndex().data()
            if self.txto is None:
                self.txto = self.completer_altres.currentCompletion()
            if self.txto == '':
                return
            self.leCarrer.setAlignment(Qt.AlignLeft)
            self.leCarrer.setText(self.txto)
            self.iniAdreca()
            self.get_tipus_geometria()


    def trobatCarrer(self) -> Optional[bool]:
        """
        Processa l'actual text del carrer, neteja el nom del carrer i busca l'adreça.
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
                if self.txto in self.dict_carrers:
                    self.nomCarrer = self.txto
                    self.codiCarrer = self.dict_carrers[self.nomCarrer]
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
        if self.txto not in self.dict_carrers:
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
                self.dict_carrers[clave] = codi_carrer

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
        if self.txto in self.dict_carrers:
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
            if self.txto in self.dict_carrers:

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
        layer_name = self.get_nom_layer()
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

        index = self.dict_capa_invers.get(self.txto)
        llista_posicions = list(self.dict_capa_invers.values()).index(index)
        features = list(layer.getFeatures())
        return features[llista_posicions]

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
        leNumero = QLineEdit()
        leNumero.setPlaceholderText('Número')

        layCerc=QHBoxLayout()
        layCerc.addWidget(le1)
        layCerc.addWidget(leNumero)
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
        cercador=QCercadorAdreca(le1, lineEditNumero=leNumero)
        cercador.coordenades_trobades.connect(trobat)
        cercador.area_trobada.connect(trobat)

        project = QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        wid.show()
