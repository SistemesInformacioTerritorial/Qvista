# qVista

## [CAST]

qVista es una herramienta construida sobre la API de QGIS, para simplificar el uso de información territorial en Barcelona, con especial énfasis a los servicios técnicos i los equipos gerenciales.

Es un proyecto desarrollado por el Departamento de Sistemas de Información Territorial del Instituto Municipal de Informática del Ayuntamiento de Barcelona.

En este momento el proyecto se encuentra aún en fase embrionaria. Pueden, por tanto, haber errores, cambios frecuentes y inestabilidad en los datos ofrecidos. 

La rama funcional es master.

Requisitos de funcionamiento:

- Instalación previa de QGIS 3.4
- Clonar el repositiorio a una carpeta locacl (Ej: d:\qvista\codi) De esta carpeta colgarán los ficheros y carpetas de Github.
- Crear un acceso directo (en el escritorio o donde se quiera). 

El funcionamiento de la aplicación está pensado para su uso dentro de la infraestructura de comunicaciones del Ayuntamiento de Barcelona. En caso de no tener esa conexión sólo podremos acceder a un mapa base y tendremos que trabajar con nuestra información particular. Si disponemos de conexión corporativa, tendremos acceso al catálogo de mapas y capas corporativo 

## [CAT]

qVista és una eina construida sobre l'API de Qgis per simplificar l'ús d'informació territorial de Barcelona amb especial èmfasi en serveis técnics i equips gerencials.

És un projecte desenvolupat pel Departament de Sistemes d'Informació Territorial de l'Institut Municipal d'Informàtica de l'Ajuntament de Barcelona.

En aquest moment el project es troba en fase de desenvolupament. Aixó vol dir que hi poden haver errors, canvis freqüents i inestabilitat en les dades que s'ofereixen. Però per fer-ne proves i jugar-hi, podeu instal·lar-ho de la següent manera:

(La branca funcional és master)

- Instal·lació previa de QGIS 3.4.
- Fer un clon del repositori a una carpeta local (Ex: d:\Qvista\codi). D'aquesta carpeta hi penjaran els fitxers i carpetes de Github.
- Crear un accés directe (a l'escriptori o on es vulgui), amb les següents característiques:
  - La destinació ha de ser semblant a la següent: "C:\Program Files\QGIS 3.4\bin\python-qgis.bat" d:\qvista\codi\qvista.py.
  - El directori de treball de l'accés directe ha de ser el mateix on està qvista.py, en aquest cas: d:\qvista\codi.
  - En resum: estem invocant mitjançant un .bat estàndard de la instal·lació de Qgis (python-qgis.bat) que crida al script inicial de python del qVista (qVista.py)

  El funcionament de l'aplicació és diferent si hi ha connexió a la xarxa corporativa de l'Ajuntament de Barcelona que si no n'hi ha. En el segon cas, tan sols podrem accedir a un mapa base i haurem de treballar amb la nostra informació particular. Si tenim connexió corporativa podrem accedir al catàleg corporatiu (encara en construcció), així com als avisos i notícies

Posteriorment documentarem quina estructura han de tenir el catàleg, les notícies i aquestes coses

prova
