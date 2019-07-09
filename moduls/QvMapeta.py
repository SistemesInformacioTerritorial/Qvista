from moduls.QvImports  import *
from qgis.core import QgsRectangle
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton


# import time


class QvMapeta(QFrame):
    """La classe que defineix el mapeta de posicionament i que controla un canvas."""
    def __init__(self, canvas, tamanyPetit = False, pare = None):
        """Inicialització del mapeta.
        
        Arguments:
            QFrame {[self]} -- [QvMapeta]
            canvas {[QgsMapCanvas]} -- [El canvas que gesrtionarà el mapeta.]
        
        Keyword Arguments:
            tamanyPetit {bool} -- [True pel Mapeta petit, False pel Mapeta gran] (default: {False})
            pare {[QWidget]} -- [El widget sobre el que es pintarà el mapeta. No és obligatori.] (default: {None})
        """
        
        QFrame.__init__(self)
       
        # Assigno el mapeta al parent
        self.setParent(pare)
        self.pare= pare
        # angulo 0 rangos mundo equivalentes a mapeta
        self.xmin_0= 419691.945
        self.ymin_0=4574155.024
        self.xmax_0= 436891.945
        self.ymax_0=4591355.024  

        # Convertim paràmetres en variables de classe
        self.canvas = canvas
         
        self.tamanyPetit = tamanyPetit
        self.MouseMoveFlag = False
        self.MousePressFlag= False
        # Posem per defecte a False
        self.petit = False
       
        # Preparem el canvas per capturar quan es modifica, i poder repintar el mapeta.
        self.canvas.extentsChanged.connect(self.pintarMapeta)

        
        

        # Dimensions i fons del mapeta segosn si és gran o petit
        if self.tamanyPetit:
            self.xTamany = 185
            self.yTamany = 185
            self.setStyleSheet('QFrame {opacity: 50; background-image: url("imatges/QVista_Mapeta_0graus_peque.png");}')
        else:
            # De entrada cargo el mapeta no girado
            self.seno_antigiro= 0
            self.coseno_antigiro= 1
            self.seno_giro= 0
            self.coseno_giro= 1

            self.xTamany = 250
            self.yTamany = 250            
            self.setStyleSheet('QFrame {background-image: url("imatges/QVista_Mapeta_0graus.png");}')

            # Ya puedo calcular la escala entre el mapeta y la realidad, basandome en las X (presupongo que la escala Y sera la misma)
            # Las coordenadas mundo son un dato obtenido con qgis

        self.Escala =  (self.xmax_0 - self.xmin_0) / self.xTamany # relacion base "mundo" base mapeta--> 68.8
      
        # Definim la geometria del frame del mapeta
        self.setGeometry(20,20,self.xTamany,self.yTamany)
        self.move(20,20)
        self.begin = QPoint()
        self.end = QPoint()

        # Aixó serveix per donar ombra al frame
        # effect = QGraphicsDropShadowEffect()
        # effect.setBlurRadius(5)
        # effect.setColor(QColor(120,120,120,0))
        # effect.setXOffset(5)
        # effect.setYOffset(5)
        # effect.setColor(QColor(150,150,150))
        # self.setGraphicsEffect(effect)

        ombra=QvConstants.ombra(self,radius=20)
        self.setGraphicsEffect(ombra)

        # QvConstants.afegeixOmbraWidget(self)

        # El botó per minimitzar el mapa
        self.botoFerPetit = QPushButton(self)
        icon = QIcon('imatges/mapeta-collapse.png')
        self.botoFerPetit.setIcon(icon)
        self.botoFerPetit.setGeometry(0,0,25,25)

        self.botoFerPetit.show()
        self.botoFerPetit.setChecked(False)
        
        
        self.botoFerPetit.clicked.connect(self.ferPetit)

        # BOTON QUE INVOCA EL CAMBIO DE ROTACION MEDIANTE LA FUNCION self.cambiarRotacion
        # self.botocambiarRotacion = QPushButton(self)
        # icon = QIcon('imatges/giro_0_44.png')
        # self.botocambiarRotacion.setIcon(icon)
        # self.botocambiarRotacion.setGeometry(0,0,25,25)
        # self.botocambiarRotacion.move(20,0)
        # self.botocambiarRotacion.show()
        # self.botocambiarRotacion.clicked.connect(self.cambiarRotacion)
        # self.show()

        # self.canvas.setCenter(QgsPointXY(xcent, ycent))
        
        # self.setMouseTracking(True)
    

        

    def cambiarRotacion(self):
        # entramos aqui cuando se pulsa el boton de cambiar rotacion
        # Si esta a 44.5 la pone a 0, y viceversa.
        # En funcion de la rotacion carga el mapeta correspondiente
        if self.tamanyPetit == False:
            if self.canvas.rotation() == 44.5:
                self.canvas.setRotation(0)
                self.setStyleSheet('QFrame {background-image: url("imatges/QVista_Mapeta_0graus.png");}')
            else:
                self.canvas.setRotation(44.5)
                if self.petit == False:
                    self.setGeometry(20,20,self.xTamany,self.yTamany)
                    self.move(20,20)
                else:
                    self.setGeometry(20,20,25,25)
                    self.move(20,20)
                # self.setGeometry(0,0,self.xTamany,self.yTamany)
                self.setStyleSheet('QFrame {background-image: url("imatges/QVista_Mapeta_44_5graus_mio.png");}')
        else:
            if self.canvas.rotation() == 44.5:
                self.canvas.setRotation(0)
                self.setStyleSheet('QFrame {background-image: url("imatges/QVista_Mapeta_0graus_peque.png");}')
            else:
                self.canvas.setRotation(44.5)
                if self.petit == False:
                    self.setGeometry(20,20,self.xTamany,self.yTamany)
                    self.move(20,20)
                else:
                    self.setGeometry(20,20,25,25)
                    self.move(20,20)
                self.setStyleSheet('QFrame {background-image: url("imatges/QVista_Mapeta_44_5graus_mio_peque.png");}')


        self.canvas.refresh()
        self.pintarMapeta()



        # if self.botoMinimitzar:
        #     self.botoFerPetit.show()
        # else:
        #     self.botoFerPetit.hide()

        # self.botoFerPetit.setChecked(False)

    # def setBotoMinimitzar(self, botoMinimitzar):
    #     """Per assignar o no 
        
    #     Arguments:
    #         botoMinimitzar {[type]} -- [description]
    #     """
    #     self.botoMinimitzar = botoMinimitzar

    #     if self.botoMinimitzar:
    #         self.botoFerPetit.show()
    #     else:
    #         self.botoFerPetit.hide()
    #     self.botoFerPetit.setChecked(False)

    def ferPetit(self):
        if self.petit:
            self.setGeometry(0,0,self.xTamany,self.yTamany)
            self.move(20,20)
            self.petit = False
            # icon = QIcon('imatges/arrow-collapse.png')

            icon = QIcon('imatges/mapeta-collapse.png')
            self.botoFerPetit.setIcon(icon)
        else:
            self.setGeometry(0,0,25,25)
            self.move(20,20)
            self.petit = True
            icon = QIcon('imatges/mapetaPetit.jpg')
            self.botoFerPetit.setIcon(icon)
        self.botoFerPetit.setChecked(False)

    def pintarMapeta(self):
        # Cuando hay alteraciones en el canvas, se han de repercutir sobre el mapeta, representando sobre éste el area de cartografia visible
        # y una cruz que indica el centro 
        # Esta funcion calcula unas coordenadas para que trabaje el paintEvent (que es quien pinta la caja y la cruz...)

        PPa1=QPoint()   # Pto abajo izquierda del canvas (Mundo)
        PPa2=QPoint()   # Pto abajo derecha del canvas
        PPa3=QPoint()   # Pto arriba derecha del canvas
        PPa4=QPoint()   # Pto arriba izquierda del canvas

        Par1=QPoint()  #  Pto arriba izquierda (Mapeta) Mundo proyectado a mapeta
        Par2=QPoint()  #  Pto arriba derecha
        Par3=QPoint()  #  Pto abajo derecha
        Par4=QPoint()  #  Pto abajo izquierda
        
        Pa1=QPoint()   #  Pto arriba izquierda
        Pa2=QPoint()
        Pa3=QPoint()
        Pa4=QPoint()   

        # Leo rango del canvas , pues se ha adaptado a la geometria de la ventana
        rect = self.canvas.extent()
       
        # Desde el rango del canvas, he de calcular el rango inscrito en el que se veria con el canvas a 0 grados
        PPa1.x= rect.xMinimum()
        PPa1.y= rect.yMinimum()
        PPa3.x= rect.xMaximum()
        PPa3.y= rect.yMaximum()
        PPa2.x=  PPa3.x
        PPa2.y=  PPa1.y
        PPa4.x=  PPa1.x
        PPa4.y=  PPa3.y

        # anchura y altura de la cartografia del canvas en coord mundo
        anchoMundoVerde= (PPa3.x - PPa1.x)  
        altoMundoVerde=  (PPa3.y - PPa1.y)

        # Proporciones canvas
        w= self.canvas.widthMM()
        h= self.canvas.heightMM()

        if self.canvas.rotation()==0:
            self.seno_giro= math.sin(0 * math.pi /180)
            self.coseno_giro= math.cos(0 * math.pi /180)
            self.seno_antigiro= math.sin(0 * math.pi /180)
            self.coseno_antigiro= math.cos(0 * math.pi /180)            
        else:
            self.seno_giro= math.sin(44.5 * math.pi /180)
            self.coseno_giro= math.cos(44.5 * math.pi /180)
            self.seno_antigiro= math.sin(-44.5 * math.pi /180)
            self.coseno_antigiro= math.cos(-44.5 * math.pi /180)            
           
        H= (h*self.coseno_giro)+ (w*self.seno_giro)
        W= (h*self.seno_giro)  + (w*self.coseno_giro)
        Escalax= anchoMundoVerde / W
        Escalay= altoMundoVerde /  H

        Pa1.x = PPa1.x
        Pa1.y = PPa1.y + Escalax*h*self.coseno_giro
        Pa2.x = PPa4.x + Escalax*w*self.coseno_giro
        Pa2.y = PPa4.y
        Pa3.x = PPa2.x
        Pa3.y = PPa2.y + Escalax*w*self.seno_giro
        Pa4.x = PPa1.x + Escalax*h*self.seno_giro
        Pa4.y = PPa1.y
        
        ancho=((Pa2.x-Pa1.x)**2+(Pa2.y-Pa1.y)**2)**0.5/self.Escala
        alto= ((Pa2.x-Pa3.x)**2+(Pa2.y-Pa3.y)**2)**0.5/self.Escala
        # Correspondencia del punto 1 mundo en el mapeta. 
        xx= ((Pa1.x -self.xmin_0)  /self.Escala ) 
        yy= ((Pa1.y -self.ymin_0) /self.Escala ) 
        
        if self.canvas.rotation()==0:
            Par1.x = xx
            Par1.y= yy
        else:
            Par1.x=  ((xx-(self.xTamany/2) ) * self.coseno_antigiro - (yy -(self.xTamany/2) ) * self.seno_antigiro )   + (self.xTamany/2) 
            Par1.y=  ((xx-(self.xTamany/2) ) *  self.seno_antigiro   + (yy -(self.xTamany/2)) * self.coseno_antigiro ) + (self.xTamany/2) 

        Par2.x= Par1.x + ancho
        Par2.y= Par1.y
        Par3.x= Par2.x 
        Par3.y= Par2.y - alto
        Par4.x= Par3.x -ancho
        Par4.y= Par3.y
    
        xMin = min(Par1.x,Par2.x,Par3.x,Par4.x)    #xmin
        xMax = max(Par1.x,Par2.x,Par3.x,Par4.x)    #xmax
        yMin = min(Par1.y,Par2.y,Par3.y,Par4.y)    #ymin
        yMax = max(Par1.y,Par2.y,Par3.y,Par4.y)    #ymax
    
        self.begin = QPoint(xMin,yMin)
        self.end = QPoint(xMax,yMax)
        self.repaint()            
 

    def paintEvent(self, event):

        # Cuando se detecta evento de refresco??
        # Pinto en mapeta rectangulo y cruz
        qp = QPainter(self)
        #br = QBrush(QColor(50, 110, 90, 70))  
        br = QBrush(QvConstants.COLORCLARSEMITRANS) #Color de fons del quadrat
        qp.setBrush(br)  

        pen=QPen(QvConstants.COLORFOSC)
        qp.setPen(pen)
        begin_ = QPoint()
        end_ =  QPoint()

        # capturo coordenadas 
        begin_.x= self.begin.x()
        end_.x= self.end.x()

        ## Se cambia el sentido de las coordenadas en y, se pone el 0 en la parte de abajo del mapeta, en funcion de MouseMoveFlag')
        if self.MouseMoveFlag== False:
            begin_.y= self.yTamany-self.begin.y()
            end_.y=   self.yTamany- self.end.y()
        else:
            begin_.y= self.begin.y()
            end_.y= self.end.y()
        
        self.MouseMoveFlag= False
        ## Pinto rectangulo')
        qp.drawRect(begin_.x,begin_.y,end_.x-begin_.x,end_.y-begin_.y)
        ## Pinto cruz')
        qp.drawLine(QLineF( QPoint( begin_.x +(end_.x-begin_.x)/2, 0),  QPoint( begin_.x +(end_.x-begin_.x)/2,self.yTamany)  ))
        qp.drawLine(QLineF( QPoint( 0, begin_.y +(end_.y-begin_.y)/2),  QPoint( self.xTamany,begin_.y +(end_.y-begin_.y)/2 )  ))


    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.MousePressFlag=True

    def mouseMoveEvent(self, event):
        # self.pare.app.restoreOverrideCursor()
        # self.pare.app.setOverrideCursor(QCursor(QPixmap('imatges/cruz.cur'))) 
        # self.setCursor(QCursor(QPixmap('imatges/cruz.cur')))
        if self.MousePressFlag== True:        
            self.end = event.pos()
            self.MouseMoveFlag= True
            self.canvas.update()

    def conversioPantallaMapa(self,punt):
        x = punt[0]
        y = punt[1]
        xMapa = self.xmin_0  +self.Escala * x
        yMapa = self.ymin_0 + self.Escala * y 
        return [xMapa, yMapa]

    def leaveEvent(self, event):
        # self.pare.app.restoreOverrideCursor()
        pass

    def enterEvent(self, event):
        # self.pare.app.setOverrideCursor(QCursor(QPixmap('imatges/cruz.cur')))  
        self.setCursor(QCursor(QPixmap('imatges/cruz.cur')))     

    def mouseReleaseEvent(self, event):
        Paux1=QPoint() #  Pto arriba izquierda
        Paux2=QPoint() #  Pto arriba derecha
        Paux3=QPoint() #  Pto abajo derecha
        Paux4=QPoint() #  Pto abajo izquierda
        self.end = event.pos()
        self.MousePressFlag=False

     

        ## Cambio origen de coordenadas "Y" poniendolo abajo-izquierda. Acorde con sistema del Mapa')
        self.xIn = self.begin.x()
        self.yIn = self.yTamany - self.begin.y()
        self.xFi = self.end.x()
        self.yFi = self.yTamany - self.end.y()
      
        ## Convierto las coordenadas del mapeta girado 44 a coordenadas de mapeta no girado para buscar la utm')
 
        # Aqui se puede llegar haciendo una ventana sobre el mapeta 0 o sobre el mapeta 44
        # Si es sobre el mapeta 0, las coordenadas se pueden buscar la correspondencia de esas coordenadas 
        # con el mundo
        # Si el mapeta esta girado, lo que hare sera buscar la correspondencia de las corrdenadas de este mapeta con el mapeta 
        # no girado. Para ello habra que girarlas 44.5 grados y restarles el desplazamiento

        #  En el mapeta (girado o no) he señalado una ventana. Calculo su tamaño
        # Calculo la la ventana mundo "girado" correspondiente a los puntos del mapeta
        distX=  (self.xFi - self.xIn)   # ancho mapeta
        distX= distX * self.Escala      # ancho mundo
        distY=  (self.yFi - self.yIn)   # alto mapeta
        distY= distY * self.Escala      # alto mundo 

        if self.canvas.rotation()==44.5:
            # giro 44.5 (contra reloj)
            # ...Giro el punto inicial
            self.xIn_=  ((self.xIn -(self.xTamany/2)) * self.coseno_giro     - (self.yIn -(self.xTamany/2) ) * self.seno_giro )   + (self.xTamany/2) 
            self.yIn_=  ((self.xIn -(self.xTamany/2)) * self.seno_giro       + (self.yIn -(self.xTamany/2) ) * self.coseno_giro )  + (self.xTamany/2) 
            # añado el desplazamiento
            self.xIn= self.xIn_ 
            self.yIn= self.yIn_ 

        ## en este punto las coordenadas mapeta que manejo estan referidas al mapeta 0')
        ## Convertimos las coordenadas del punto inicial del mapeta_ang=0 a coordenadas Mundo')
        # Miraremos la proporcion de las coordenadas xy sobre el mapeta y lo multiplicaremos por la escala y 
        # se lo sumaremos a la coordenada del origen...
        punt1 = self.conversioPantallaMapa([self.xIn, self.yIn])

        ## coordenadas mundo de los 4 puntos señalados en el mapeta. Traslado el rectangulo del mapeta al mundo')
        Paux1.x= punt1[0]  
        Paux1.y= punt1[1]
        Paux2.x= Paux1.x + (distX * self.coseno_giro)
        Paux2.y= Paux1.y + (distX * self.seno_giro)
        Paux3.x= Paux2.x - (distY * self.seno_giro)
        Paux3.y= Paux2.y + (distY * self.coseno_giro)
        Paux4.x= Paux1.x - (distY * self.seno_giro)
        Paux4.y= Paux1.y + (distY * self.coseno_giro)

        ## Calculo rango de esa caja girada, (minima, caja que la engloba) para pasarle unas coordenadas al canvas que engloben la caja. Esto solo seria necesario en el caso de rotacion')
        punt1[0]= min(Paux1.x, Paux2.x, Paux3.x,Paux4.x)    #xmin
        punt1[1]= min(Paux1.y, Paux2.y, Paux3.y,Paux4.y)    #ymin
        punt2=[]
        punt2.append(max(Paux1.x, Paux2.x, Paux3.x,Paux4.x)) #xmax
        punt2.append(max(Paux1.y, Paux2.y, Paux3.y,Paux4.y)) #ymax

        ## Pasamos rango al canvas para que lo represente')
        # Necesitare tener estas coordenadas como QgsRectangle...
        rang = QgsRectangle(punt1[0], punt1[1], punt2[0], punt2[1])
        
        self.canvas.setExtent(rang)
        self.canvas.refresh()
        rect = self.canvas.extent()





        

import math

if __name__ == "__main__":
    # exit()
    # projecteInicial='D:/qVista/Dades/Projectes/tra/mio.qgs'
    projecteInicial='D:/qVista/Dades/Projectes/BCN11_nord.qgs'


    with qgisapp() as app:
        # Canvas, projecte i bridge
        start1 = time.time()
        canvas=QgsMapCanvas()
        
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
        canvas.show()
        canvas.setRotation(0)

        qvMapeta = QvMapeta(canvas, tamanyPetit = False, pare=canvas)
        qvMapeta.move(0,0)
        qvMapeta.setBotoMinimitzar(True)
        qvMapeta.show()
        print ('resto: ',time.time()-start1)
