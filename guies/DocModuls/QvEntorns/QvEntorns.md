# QvEntorns
QvEntorns és un mòdul pensat per poder afegir entorns a qVista sense necessitat de modificar l'arxiu de codi principal. Un *entorn* es defineix com un QDockWidget que afegeix alguna informació extra sobre algun projecte concret. 

## Com definir un nou entorn
### Creació del QDockWidget
Per definir un entorn cal crear una subclasse de QDockWidget definint tot l'entorn. Preferentment el crearem en un arxiu separat del QvEntorns.py. Per exemple, el crearem a *moduls.QvMarxesCiutat*

```Python
class MarxesCiutat(QDockWidget):
    def __init__(self, parent):
        ...
```

### Afegir-lo a QvEntorns.py
Un cop el tenim a QvEntorns.py, toca afegir-lo al QvEntorns.py. Això ho fem mitjançant una importació amb *from ... import ...*, ja que així el nom passa a formar part de l'espai de noms actual (cosa imprescindible per com està definit el mòdul).

Hem de garantir que el nom sigui únic i que coincideixi amb el que posarem a la variable d'entorn del projecte. Si no és així, podem fer servir un *import as*. Per exemple:

```Python
from moduls.QvMarxesCiutat import MarxesCiutat as MarxesExploratories
```

### Definir les variables d'entorn
Ara que ja tenim l'entorn creat, hem de crear una variable d'entorn en els projectes que volguem mostrar-ho. La variable s'ha de dir **qV_entorn** i ha de tenir com a valor el nom exacte de l'entorn (en l'exemple, "MarxesExploratories")

## Com funciona
Internament el mòdul funciona d'una manera molt senzilla. Quan importem amb un "from ... import ..." el que fem és lligar la classe a l'espai de noms del mòdul, com si l'haguéssim definit a dins directament.

El que fa el mòdul és utilitzar la [reflexió](https://es.wikipedia.org/wiki/Reflexi%C3%B3n_(inform%C3%A1tica)) per obtenir una classe a partir d'un string, i així poder carregar una classe o una altra en funció del valor que té la variable d'entorn. La línia important és la següent:

```Python
return getattr(sys.modules[__name__], nom)
```

El que fem és obtenir el mòdul actual a partir de sys.modules\[\_\_name\_\_\]. Aquest és pura i simplement un objecte representant el mòdul actual. Aleshores obtenim l'entorn que volíem fent servir getattr. 