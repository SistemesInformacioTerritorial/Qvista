from typing import List
from qgis.core import QgsProject, QgsExpressionContextUtils

def te_enllac() -> List[str]:
    """
    Recorre totes les capes del projecte actual i retorna una llista de les variables que comencen per 'qV_button'.
    
    Returns:
        List[str]: Una llista de strings que representen les variables que comencen per 'qV_button'.
    """
    variables_qv_button = []

    for layer in QgsProject.instance().mapLayers().values():
        totes_variables = QgsExpressionContextUtils.layerScope(layer).variableNames()

        for nom_variable in totes_variables:
            if nom_variable.startswith('qV_button'):
                variables_qv_button.append(nom_variable)

    return variables_qv_button