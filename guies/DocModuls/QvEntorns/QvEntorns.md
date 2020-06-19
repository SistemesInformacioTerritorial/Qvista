# QvEntorns
QvEntorns és un mòdul pensat per poder afegir entorns i eines a qVista sense necessitat de modificar l'arxiu de codi principal. 

Eina: Una *eina* es defineix com un QDockWidget que afegeix alguna informació o funcionalitat extra a qVista. Aquesta eina pot ser general (apareix sempre a qVista) o específica (apareix només en determinats projectes)
Entorn: Un *entorn* es defineix com una eina que s'obre automàticament en obrir el projecte. Per definició, un entorn va lligat a un projecte concret

## Com definir una nova eina
### Creació del QDockWidget
Per definir un entorn cal crear una subclasse de QDockWidget definint tot l'entorn. El crearem en un arxiu separat del QvEntorns.py, i allotjat al directori moduls/entorns. Per exemple, el crearem a *moduls/entorns/MarxesExploratories*

```Python
class MarxesExploratories(QDockWidget):
    esEinaGeneral = ...
    titol = ...
    apareixDockat = ...
    def __init__(self, parent=None):
        ...
```

Per donar més informació a qVista sobre aquesta eina, podem declarar les variables de classe que es veuen a l'exemple:

* **esEinaGeneral:** Indica si volem que l'eina sigui general (apareix per tots els projectes). Si no s'especifica res, només apareixerà en els projectes que se li indiqui
* **titol:** El títol que volem que aparegui a l'acció del menu. Si no s'especifica, serà el nom de la classe.
* **apareixDockat:** Si està a True, el dockwidget apareix dockat a la dreta. Si està a False, apareix flotant

### Definir les variables de projecte
Tenim dues variables d'entorn que podem definir en els projectes. **qV_entorn** i **qV_eines**. El seu contingut ha de ser, o bé un únic literal (el nom de l'eina), o bé una llista de literals.

**qV_entorn:** Totes les eines que s'hi declarin es mostraran en carregar el projecte. També apareixeran al menú d'eines
**qV_eines:** Totes les eines que s'hi posin apareixeran al menú d'eines, però no s'obriran fins que l'usuari hi faci click

Un exemple dels valors que podem definir és el següent:
```
'qV_entorn': '[MarxesExploratories, DobleCanvas]'
'qV_eines': 'IntegracioPatrimoni'
```

És important remarcar que les cometes no s'han de posar explícitament, ja les posa QGIS. Si es posen, en principi no passa res, però no està garantit que funcioni.

## Com funciona
Internament el mòdul funciona d'una manera molt senzilla:

El que fa el mòdul és utilitzar la [reflexió](https://es.wikipedia.org/wiki/Reflexi%C3%B3n_(inform%C3%A1tica)) per importar un mòdul i obtenir la seva classe a partir d'un string, i així poder carregar una classe o una altra en funció del valor que té la variable del projecte. 

```Python
mod = importlib.import_module(f'moduls.entorns.{nom}')
return getattr(mod,nom)
```

La primera línia el que fa és importar el mòdul indicat, i ens l'assigna a la variable *mod*. La segona obté la classe del mòdul i la retorna.

Dins del programa principal de qVista, la gestió és una mica més complexa. Per carregar les eines generals, s'itera tota la carpeta, per cada classe es consulta la variable esEinaGlobal i es fa en funció del seu valor. Per carregar les eines específiques i els entorns, com que ja es tenen els noms, s'importen directament amb QvEntorns, es creen les accions i tot això i es carrega. 