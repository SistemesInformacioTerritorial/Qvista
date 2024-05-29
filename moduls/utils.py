from typing import Dict, List, Optional, Tuple
from qgis.core import QgsProject, QgsExpressionContextUtils
import re

def get_content_link(valor_variable: str, nom_variable: str, layer: str) -> Optional[Tuple[str, str]]:
    """
    Extreu la descripció i l'enllaç d'una variable donada.

    Args:
    valor_variable (str): El valor de la variable des de la qual s'extrai la descripció i l'enllaç.
    nom_variable (str): El nom de la variable.
    layer (str): La capa a la qual pertany la variable.

    Returns:
    Optional[Tuple[str, str]]: Una tupla amb dos strings, la descripció i l'enllaç. Retorna None si no es compleixen les condicions.
    """
    desc_regex = re.compile(r'desc="([^"]*)"')
    link_regex = re.compile(r'link="([^"]*)"')
    desc_match = desc_regex.search(valor_variable)
    link_match = link_regex.search(valor_variable)
    if check_content_link(desc_match,link_match,nom_variable,layer) is False:
        return None
    return desc_match.group(1), link_match.group(1)

def check_content_link(desc_match: re.Match, link_match: re.Match, nom_variable: str, layer: str) -> bool:
    """
    Comprova si la descripció i l'enllaç estan presents i no estan buits.

    Args:
    desc_match (re.Match): El resultat de la cerca de la descripció.
    link_match (re.Match): El resultat de la cerca de l'enllaç.
    nom_variable (str): El nom de la variable.
    layer (str): La capa a la qual pertany la variable.

    Returns:
    bool: Retorna True si la descripció i l'enllaç estan presents i no estan buits, False en cas contrari.
    """
    if not desc_match or desc_match.group(1) == '':
        print("Falta la descripció en la variable:", nom_variable, "a la capa:", layer)
        return False
    if not link_match or link_match.group(1) == '':
        print("Falta l'enllaç en la variable:", nom_variable, "a la capa:", layer)
        return False
    return True

def get_links() -> List[Dict[str, str]]:
    """
    Recorre totes les capes del projecte actual i retorna una llista de diccionaris. 
    Cada diccionari conté la descripció i l'enllaç de les variables que comencen per 'qV_button'.

    Returns:
    List[Dict[str, str]]: Una llista de diccionaris. Cada diccionari conté la descripció ('desc') i l'enllaç ('link') 
    de les variables que comencen per 'qV_button'.
    """

    variables_qv_button = []
    for layer in QgsProject.instance().mapLayers().values():
        totes_variables = QgsExpressionContextUtils.layerScope(layer).variableNames()

        for nom_variable in totes_variables:
            if nom_variable.startswith('qV_button'):
                valor_variable = QgsExpressionContextUtils.layerScope(layer).variable(nom_variable)
                desc_value,link_value = get_content_link(valor_variable,nom_variable,layer)
                values_dict = {'desc': desc_value, 'link': link_value}
                variables_qv_button.append(values_dict)
    return variables_qv_button