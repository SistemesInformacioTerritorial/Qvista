# qVista

qVista és una eina construida sobre la API de Qgis, per simnplificar l'ús d'informació territorial de Barcelona, amb especial énfasi en serveis técnics i equips gerencials.

És un projecte desenvolupat pel Departament de Sistemes d'Informació Territorial, del Institut Municipal d'Informàtica del Ajuntament de Barcelona.

En aqust moment el project es troba en fase de desenvolupament. Aixó vol dir que poden haver-hi errors, canvis freqüents, i inestabilitat en les dades que s'ofereixen. Però per fer-ne proves i jugar-hi, podeu instal.lar-ho de la següent manera:

- Instal.lació previa de QGIS 3.4
- Fer un clon del repositori a una carpeta local (Ex: d:\Qvista\codi) D'aquesta carpeta i penjaran els fitxers i carpetes de Github
- Crear un accés directe (al escriptori o on és vulgui), amb les següents característiques:
  - La destinació ha de ser semblant a aixó: "C:\Program Files\QGIS 3.4\bin\python-qgis.bat" d:\qvista\codi\qvista.py
  - El directori de trebal del accés directe ha de ser el mateix on està qvista.py, en aquest cas: d:\qvista\codi
  - En resum: estem invocant mitjançant un .bat estandar de la instal.lació de Qgis (python-qgis.bat) que crida el script inicial de python del qVista (qVista.py)
  
  El funcionament de l'aplicació és diferent si hi ha connexió a la xarxa corporativa del Ajuntament de Barcelona que si no n'hi ha. En el segon cas, tan sols podrem accedir a un mapa base, i haurem de treballar amb la nostra informació pàrticular. Si tenim connexió corporativa podrem accedir al catàleg corporatiu (encara en construcció).

  
