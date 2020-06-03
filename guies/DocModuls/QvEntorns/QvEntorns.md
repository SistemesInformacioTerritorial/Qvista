# QvEntorns
QvEntorns és un mòdul pensat per poder afegir entorns a qVista sense necessitat de modificar l'arxiu de codi principal. Un *entorn* es defineix com un QDockWidget que afegeix alguna informació extra sobre algun projecte concret. 

## Com definir un nou entorn
### Creació del QDockWidget
Per definir un entorn cal crear una subclasse de QDockWidget definint tot l'entorn. El crearem en un arxiu separat del QvEntorns.py, i allotjat al directori moduls/entorns. Per exemple, el crearem a *moduls/entorns/MarxesExploratories*

```Python
class MarxesExploratories(QDockWidget):
    def __init__(self, parent=None):
        ...
```

### Definir les variables de projecte
Ara que ja tenim l'entorn creat, hem de crear una variable de projecte en els projectes que volguem mostrar-ho. La variable s'ha de dir **qV_entorn** i ha de tenir com a valor el nom exacte de l'entorn (en l'exemple, "MarxesExploratories")

## Com funciona
Internament el mòdul funciona d'una manera molt senzilla:

El que fa el mòdul és utilitzar la [reflexió](https://es.wikipedia.org/wiki/Reflexi%C3%B3n_(inform%C3%A1tica)) per importar un mòdul i obtenir la seva classe a partir d'un string, i així poder carregar una classe o una altra en funció del valor que té la variable del projecte. 

```Python
mod = importlib.import_module(f'moduls.entorns.{nom}')
return getattr(mod,nom)
```

La primera línia el que fa és importar el mòdul indicat, i ens l'assigna a la variable *mod*. La segona obté la classe del mòdul i la retorna