*Documentación complementaria y verbosa de algunas funciones de la clase QvMapeta 
(como excusa para aprender Markdown)*

# QvMapeta in module moduls.QvMapeta:
QvMapeta define un pequeño mapa de posicionamiento que controla un 
canvas.

     #triggers 
     ChgRotation    => cambiarMapeta
     ChgExtent      => pintarMapeta
     Canvas.refresh => paintEvent
     Mapeta.repaint => paintEvent
     
     
mouse en Mapeta, dentro/fuera del círculo  
Casos|mousePress  |mouseMove  |mouseRelease  |Comportamiento
--|--|--|--| --
|1| dentro |dentro  |dentro  |window area
|2| dentro | -|dentro  |window center el Press
|3| dentro |dentro/fuera  |fuera| window area
|4| fuera|fuera/dentro  |dentro  | para compass el Press
|5| fuera|fuera|fuera|para compass el Press
|6| fuera|-|fuera|para compass el Press

 
## cambiarMapeta(self)

> Actualiza imagen del mapeta conforme a la rotación del canvas
- Se invoca en la carga y cuando se detecta una rotación
- La imagen del mapeta 0º se gira lo que manda la rotación del canvas y se recarga en el mapeta


## mouseMoveEvent(self, event)
- Presión de un botón del ratón mantenida y movimiento sobre el mapeta. Seguramente el usuario está haciendo un window area
- **ejecuta repaint de mapeta para forzar paintEvent**  (que pintará rectángulo y cruz)
    
## mousePressEvent(self, event)
- Presión de un botón del ratón cuando el cursor está sobre el mapeta. Se puede estar haciendo un window center, iniciando un window area o dando un punto para que lo recoja Compass y se gire el mapeta
- Guarda coordenadas de punto del mapeta en *self.begin y self.end*
- Comprueba si el punto dado está en el circulo inscrito del mapeta, y si no lo está, emite las coordenadas (que recibirá MapetaBrujulado y se las enviará a Compass) 
- Mantiene flag self.pPM (punto para mapeta):
  - True si lo ha de gestionar mapeta  
  - False si ha de utilizarlo Compass
  
## mouseReleaseEvent(self, event)
 - Dejamos de hacer presión sobre un botón del ratón mientras está sobre mapeta
 - Calculo las coordenadas pantalla del centro del rectángulo de selección, o lo que es lo mismo del punto que señala la cruz y las transformo a coordenadas mundo.
 - Si el mapeta esta girado, hay que rotar esas coordenadas (en función de la rotación) para tenerlas en "mapeta 0º" y a partir de ahí buscar su correspondientes coordenadas mundo.
 - **canvas.setExtent() forzará pintarMapeta** 
 - **repaint de mapeta para forzar paintEvent** (pintar rectangulo y cruz)
    
## paintEvent(self, event)
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

## pintarMapeta(self)
- Se invoca cuando cambian el tamaño del canvas y cuando hay una   rotacion del canvas
  -  Despues de seleccionar una ventana en el mapeta, se actualiza   la cartografia correspondiente  en el canvas, y se adapta alas proporciones del canvas (estado inicial y  redimensionamientos).
       
 >Estás proporciones serán diferentes a las de la ventana  del mapeta (nuestra seleccion) y por lo tanto debemos recalcular la ventana del mapeta representando sobre éste el area de cartografia visible y una cruz que indica el centro
  
Esta funcion calcula unas coordenadas para que trabaje el 
paintEvent (que es quien pinta la caja y la cruz...)
- **repaint de mapeta para forzar paintEvent** (pintar rectangulo y cruz)
    
 


> Written with [StackEdit](https://stackedit.io/).

