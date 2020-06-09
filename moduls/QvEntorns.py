# Importacions necessàries
import sys
import importlib
# Fi de les importacions necessàries

# Importació d'entorns
# from moduls import entorns
# Fi de la importació d'entorns

# Ús del mòdul QvEntorns:
# Hi ha una classe (QvEntorns) que serveix pura i simplement per obtenir els entorns
# Per cada entorn que vulguem definir (per exemple, MarxesExploratories), hem de tenir una classe que es digui així i estigui dins d'un arxiu py del mateix nom a la carpeta moduls/entorns
#  Aquesta classe cal que sigui subclasse de QDockWidget
# Per exemple, podem tenir la classe MarxesExploratories, definida a moduls/entorns/MarxesExploratories.py, que definirà l'entorn MarxesExploratories

class QvEntorns:
    """Classe estàtica que permet encapsular l'ús dels diferents entorns. Disposa d'una funció "entorn" que et dóna l'entorn amb el nom indicat
    """
    @staticmethod
    def entorn(nom: str):
        nom = nom.replace('"','').replace("'",'') # eliminem cometes extra que s'hagin pogut colar
        mod = importlib.import_module(f'moduls.entorns.{nom}')
        return getattr(mod,nom)