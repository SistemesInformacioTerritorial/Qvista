# qVista

## [CAT]

qVista és una eina construïda sobre l'API de QGIS dissenyada per simplificar l'ús de la informació territorial a Barcelona, fent especial èmfasi als serveis tècnics i equips gerencials.

És un projecte desenvolupat pel Departament de Sistemes d'Informació Territorial de l'Institut Municipal d'Informàtica de l'Ajuntament de Barcelona.

En aquest moment el project es troba en una fase de desenvolupament avançada. Aixó vol dir que hi poden haver errors, canvis freqüents i inestabilitat en les dades que s'ofereixen. Però per fer-ne proves i jugar-hi, podeu instal·lar-ho de la següent manera:

1. Instal·lació de QGIS 3.10 LTR seguint [aquesta guia](guies/instalacio-qgis.md)
2. Clonar la branca master a una carpeta local (per exemple, D:\qVista\codi)
3. Crear un accés directe amb les següents característiques:
* L'intèrpret de Python ha de ser similar a "C:\Program Files\QGIS 3.10\bin\python-qgis.bat"
* El fitxer a interpretar ha de ser similar a "D:\qVista\codi\qVista.py"
* En resum: invocar l'intèrpret de Python incorporat per QGIS i fer-li interpretar l'arxiu qVista.py que hem clonat anteriorment
4. Segons el tipus d'instal·lació que vulguem, hem de posar l'arxiu install.cfg corresponent. [L'original](install.cfg) és el de producció, mentre que si volem desenvolupar hem d'agafar el de [desenvolupament intern](docs/install_DSV.cfg) o el de [desenvolupament extern](docs/install_DSV_EXT.cfg). Aquest arxiu el podem copiar a la carpeta pare, per no sobreescriure l'original (en l'exemple, a la carpeta D:\qVista)
5. Si ho necessitem, podem canviar els directoris definits al [configuracioQvista.py](configuracioQvista.py). Això és necessari sobretot amb el catàleg. Les variables que podem necessitar modificar són:
* carpetaCataleg: Carpeta on tenim el catàleg de capes
* carpetaCatalegProjectesPublics: Carpeta (o carpetes) on tenim el catàleg de projectes públics
* carpetaCatalegProjectesPrivats: Carpeta (o carpetes) on tenim el catàleg de projectes privats
* QvTempdir: Carpeta de la qual pengen les carpetes de dades, configuracions i temporals. 
* docdir: Carpeta de la qual penja la documentació de qVista
6. El catàleg de mapes està dissenyat per tenir 3 tipus de contingut. Catàleg públic, catàleg privat i catàleg local.
* Catàleg públic: està pensat per ser un catàleg compartit per tots els usuaris d'un mateix organisme (per exemple, tots els usuaris d'un Ajuntament). Tots els seus mapes són visibles per tots els usuaris de l'organisme. Hauria d'estar en una carpeta de xarxa accessible per tothom
* Catàleg privat: està pensat per funcionar similar al catàleg públic, però amb mapes disponibles només per a determinats usuaris. La idea és posar-ho en una carpeta de xarxa i donar permisos als usuaris que hagin de veure-ho. Els permisos seran els propis del sistema.
* Catàleg local: està pensat perquè cada usuari pugui tenir un catàleg propi dins del seu propi ordinador

Per crear un catàleg es pot crear des del propi qVista, a l'apartat Mapes del menú. L'estructura està més detallada [aquí](guies/creacio-cataleg-mapes.md)

### L'API
qVista és alhora un programa i un conjunt de llibreries. Aquestes estan basades en l'API de QGIS, i estan composades per una sèrie de classes basades en les classes de QGIS. Dins del directori [exemples](exemples/) es poden trobar uns quants exemples de programes creats fent servir aquesta API. A més a més, els mòduls (al directori [moduls](moduls/)) tenen un main d'exemple que ensenya com es fan servir, que mostren com es fa servir aquell mòdul concret.

### Sobre les dades publicades
Les dades publicades en aquest repositori de Github són dades públiques. Donada la naturalesa de les dades, que són canviants, i dels repositoris de Github, que són còpies, no podem garantitzar que les dades publicades aquí siguin les més recents. 