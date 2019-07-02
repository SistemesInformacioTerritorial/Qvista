# qVista

qVista és una eina construida sobre l'API de Qgis, per simnplificar l'ús d'informació territorial de Barcelona amb especial èmfasi en serveis técnics i equips gerencials.

És un projecte desenvolupat pel Departament de Sistemes d'Informació Territorial de l'Institut Municipal d'Informàtica de l'Ajuntament de Barcelona.

En aquest moment el project es troba en fase de desenvolupament. Aixó vol dir que hi poden haver errors, canvis freqüents i inestabilitat en les dades que s'ofereixen. Però per fer-ne proves i jugar-hi, podeu instal·lar-ho de la següent manera:

(La branca funcional és prePro)

- Instal·lació previa de QGIS 3.4.
- Fer un clon del repositori a una carpeta local (Ex: d:\Qvista\codi). D'aquesta carpeta hi penjaran els fitxers i carpetes de Github.
- Crear un accés directe (a l'escriptori o on es vulgui), amb les següents característiques:
  - La destinació ha de ser semblant a la següent: "C:\Program Files\QGIS 3.4\bin\python-qgis.bat" d:\qvista\codi\qvista.py.
  - El directori de treball de l'accés directe ha de ser el mateix on està qvista.py, en aquest cas: d:\qvista\codi.
  - En resum: estem invocant mitjançant un .bat estàndard de la instal·lació de Qgis (python-qgis.bat) que crida al script inicial de python del qVista (qVista.py)
  
  El funcionament de l'aplicació és diferent si hi ha connexió a la xarxa corporativa de l'Ajuntament de Barcelona que si no n'hi ha. En el segon cas, tan sols podrem accedir a un mapa base i haurem de treballar amb la nostra informació particular. Si tenim connexió corporativa podrem accedir al catàleg corporatiu (encara en construcció), així com als avisos.

  
