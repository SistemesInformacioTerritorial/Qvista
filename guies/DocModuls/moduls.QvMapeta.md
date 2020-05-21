*Documentacion complementaria y verbosa de algunas funciones de la clase QvMapeta 
(como escusa para aprender Markdown)*

# QvMapeta in module moduls.QvMapeta:
La classe que defineix el mapeta de posicionament i que controla un 
canvas.


> **triggers** 
> ChgRotation  => CambiarMapeta
> ChgExtent      => pintarMapeta
> RefreshCanvas => paintEvent
> Mapeta.repaint =>paintevent


    
## cambiarMapeta(self)
- La imagen del mapeta 0º se gira lo que manda la rotación del canvas y se recarga en el mapeta
- Se invoca en la carga y cuando se detecta una rotacion

    
## mouseMoveEvent(self, event)
- Presion de un boton del raton mantenia y movimiento sobre el mapeta
- **repaint de mapeta para forzar paintEvent**  (pintar rectangulo y cruz)
    
## mousePressEvent(self, event)- Presion de un boton del raton cuando el cursor está sobre el mapeta
- Guarda coordenadas de punto del mapeta en *self.begin y self.end*
- Comprueba si el punto dado está en el circulo inscrito del mapeta, y si no lo está emite esas coordenadas (serán para compass)
- Mantiene self.pPM (punto para mapeta) a True si lo ha de gestionar mapeta o a False si ha de utilzarlo Compass
  
## mouseReleaseEvent(self, event)
 - Dejamos de hacer presion sobre un boton del raton mientras está sobre mapeta
 - Calculo las coordenadas pantalla del centro del rectangulo de selección, o lo que es lo mismo del punto que señala la cruz y las transformo a coordenadas mundo.
 - Si el mapeta esta girado, hay que rotar esas coordenadas en función de la rotación para tenerlas en "mapeta 0º" y a partir de ahi buscar su correspondendientes coordfenadas mundo.
 - **canvas.setExtent() forzará pintarMapeta** 
 - **repaint de mapeta para forzar paintEvent** (pintar rectangulo y cruz)
    
## paintEvent(self, event)
- pinto en mapeta rectangulo y cruz.
- En esta version, con el mapeta circular, solo se dibuja los trozos de rectangulo y cruz interiores al circulo

## pintarMapeta(self)
- Se invoca cuando cambian el tamaño del canvas y cuando hay una   rotacion del canvas
  
-  Despues de seleccionar una ventana en el mapeta, se actualiza   la cartografia correspondiente  en el canvas, y se adapta alas proporciones del canvas (estado inicial y  redimensionamientos).
       
 >Estás proporciones serán diferentes a las de la ventana  del mapeta (nuestra seleccion) y por lo tanto debemos recalcular la ventana del mapeta representando sobre éste el area de cartografia visible y una cruz que indica el centro
  
Esta funcion calcula unas coordenadas para que trabaje el 
paintEvent (que es quien pinta la caja y la cruz...)
- **repaint de mapeta para forzar paintEvent** (pintar rectangulo y cruz)
    
 