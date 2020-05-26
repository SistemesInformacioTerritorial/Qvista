# comprobacion de calculos en QvMapeta

## Idea general
La clase QvMapeta realiza calculos geometricos dificiles de seguir sin una representación grafica. La versión de desarrollo QvMapeta_vba.py va escribiendo los resultados de los cálculos en el fichero CM.bas que microstation es capaz de ejecutar.


## Ubicación de ficheros
 - D:\qVista\Codi\guies\DocModuls\QvMapeta

## ComprobacionesMapeta.dgn
DGN donde se representaran los calculos.
Tiene referenciado como raster fondo_Barcelona.png, (2 veces) en: 
 - coordenadas 0,0   --> 600,600
 - coordenadas xmin,ymin  --> xmax, ymax

## fondo_Barcelona.pgn
png con la informacion raster de Barcelona
tamaño 600 x 600
corresponde al rango:
xmin,ymin:   xy= 419514.49,4573673.32
xmax,ymax: xy= 437653.75, 4591812.58

## fondo_Barcelona.pgw
Georeferenciación de fondo_Barcelona.pgn (World file)
[https://en.wikipedia.org/wiki/World_file](https://en.wikipedia.org/wiki/World_file)

## CM.bas
Fichero vba, escrito por QvMapeta_vba.py, que dibuja en el DGN los calculos.

## Ejecución

 - Ejecutar QvMapeta_vba.py
	 - Establecer rotacion
	 - Pulsar botón para comenzar a grabar operaciones.
	 - Realizar las opperaciones que se quieran comprobar.
	 - Pulsar botón para finalizar la grabación de operaciones.
	
- Entrar en el ComprobacionesMapeta.dgn
	- Ejecutar cm.bas, para ello:
		- Utilidades >> Macros >>  Microstation BASIC >> Examinar
		- Buscar D:\qVista\Codi\guies\DocModuls\QvMapeta\cm.bas
		- Ejecutar o editar (para poder ir paso a paso)