# Importacions necessàries
import sys
# Fi de les importacions necessàries

# Importació d'entorns
from moduls.QvMarxesCiutat import MarxesCiutat as MarxesExploratories
# Fi de la importació d'entorns

# Ús del mòdul QvEntorns:
# Hi ha una classe (QvEntorns) que serveix pura i simplement per obtenir els entorns
# Per cada entorn que vulguem definir (per exemple, MarxesExploratories), hem de tenir una classe que es digui així i sigui visible des del context d'aquest mòdul
#  Aquesta classe cal que sigui subclasse de QDockWidget
# Això ho podem fer de dues maneres
# 1: declarar la classe tal qual dins d'aquest mateix mòdul (preferiblement només amb entorns molt senzills)
# class MarxesExploratories(QDockWidget):
#     ...
# 2: declarar-la en un altre mòdul i importar-la amb un "from ... import ..."
#  Donat que potser el nom no és exactament el mateix, podem fer servir un import as per evitar-nos el problema

class QvEntorns:
    """Classe estàtica permet encapsular l'ús dels diferents entorns. Disposa d'una funció "entorn" que et dóna l'entorn amb el nom indicat
    """
    @staticmethod
    def entorn(nom: str):
        nom = nom.replace('"',' ').replace("'",' ') # eliminem cometes extra que s'hagin pogut colar
        return getattr(sys.modules[__name__], nom)