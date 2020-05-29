dv. 29/05/2020  7:56


*Documentación complementaria y verbosa de algunas funciones de la clase QvMapeta 
(como excusa para aprender Markdown)*

# QvMapeta in module moduls.QvMapeta:
QvMapeta define un pequeño mapa de posicionamiento que controla un 
canvas.

### Triggers:
| Event| Ejecuta
-- | -- 
ChgRotation    | cambiarMapeta 
ChgExtent     | pintarMapeta
Canvas.refresh | paintEvent
Mapeta.repaint | paintEvent

### Flags:
 Flag|True|False|Obser.| 
--|--|--|--
self.pPM |init|mousePressEvent|punto sobre mapeta
self.MousePressFlag| mousePressEvent|init <br> mousePressEvent<br>  mouseReleaseEvent | mouse apretado
self.MouseMoveFlag| mouseMove |init<br>paintEvent  | mouse movido




     
### mouse en Mapeta, dentro/fuera del círculo  
Casos|mousePress  |mouseMove  |mouseRelease  |Comportamiento | Destinatario final
--|--|--|--| -- | --
|1| dentro |dentro  |dentro  |window area | mapeta
|2| dentro | -|dentro  |window center el Press |mapeta
|3| dentro |dentro/fuera  |fuera| window area |mapeta
|4| fuera|fuera/dentro  |dentro  | para compass el Press | compass
|5| fuera|fuera|fuera|para compass el Press | compass
|6| fuera|-|fuera|para compass el Press | compass

## mousePressEvent
- Presión de un botón del ratón cuando el cursor está sobre el mapeta. **El Press determina si el punto está destinado al mapeta o al compass**
- Comprueba si el punto estra dentro del círculo inscrito:
	- Si **dentro** del circulo (casos 1,2,3): 
	    - Funcionamiento mapeta standart
	    - self.pPM = True
	- Si **fuera** del circulo (casos 4,5,6):
	  - emite las coordenadas (que recibirá MapetaBrujulado y se las enviará a Compass) 
	  - self.pPM= False
		
- Guarda coordenadas de punto del mapeta en *self.begin y self.end*

  
## mouseMoveEvent
- Presión de un botón del ratón mantenida y movimiento sobre el mapeta. Seguramente el usuario está haciendo un window area
- **ejecuta repaint de mapeta para forzar [paintEvent](#paintEvent)**  (que pintará rectángulo y cruz)

## mouseReleaseEvent
 - Dejamos de hacer presión sobre un botón del ratón mientras está sobre mapeta
	- Dentro del circulo inscrito: 
		- Se puede esta dando punto final de windowArea  -->  casos 1, 3
		- Se está dando punto final de windowCenter --> caso 2
		- Puede ser que sea el punto final de un windowArea con pnt inicial fuera  --> caso4 
	- Fuera del circulo inscrito:
		-  Son finalización de puntos para compass --> casos  5,6
 - Calculo las coordenadas pantalla del centro del rectángulo de selección, o lo que es lo mismo del punto que señala la cruz y las transformo a coordenadas mundo.
 - Si el mapeta esta girado, hay que rotar esas coordenadas (en función de la rotación) para tenerlas en "mapeta 0º" y a partir de ahí buscar su correspondientes coordenadas mundo.
 - **canvas.setExtent() forzará  [pintarMapeta](#pintarMapeta)** 
 - **repaint de mapeta para forzar  [paintEvent](#paintEvent)** (pintar rectangulo y cruz)
    
## paintEvent
- Pinta en mapeta rectangulo y cruz.
- Se basa en las coordenadas self.begin y self.end. 
 - Puede ser invocado por:
	 - Una modificacion del canvas
	      -  ChgExtent => pintarMapeta: *self.begin self.end* 
	 - Una acción sobre el mapeta:
	     -  En mousePressEvent *self.begin*
	     - En mouseMove= *self.end*
	     - En mouseRelease: *self.end*
- Con el mapeta circular, solo se dibujan los trozos de rectángulo y cruz interiores al circulo

## pintarMapeta
- Se invoca cuando cambian el tamaño del canvas y cuando hay una   rotacion del canvas
  -  Despues de seleccionar una ventana en el mapeta, se actualiza   la cartografia correspondiente  en el canvas, y se adapta alas proporciones del canvas (estado inicial y  redimensionamientos).
       
 >Estás proporciones serán diferentes a las de la ventana  del mapeta (nuestra seleccion) y por lo tanto debemos recalcular la ventana del mapeta representando sobre éste el area de cartografia visible y una cruz que indica el centro
  
Esta funcion calcula unas coordenadas para que trabaje el 
paintEvent (que es quien pinta la caja y la cruz...)
- **repaint de mapeta para forzar paintEvent** (pintar rectangulo y cruz)
    
## cambiarMapeta
> Actualiza imagen del mapeta conforme a la rotación del canvas
- Se invoca en la carga y cuando se detecta una rotación
- La imagen del mapeta 0º se gira lo que manda la rotación del canvas y se recarga en el mapeta


   
   
  
   Read more [More] (file:///guies/DocModuls/QvMapeta/comprobacionesQvMapeta.md)
   
> Written with [StackEdit](https://stackedit.io/).
