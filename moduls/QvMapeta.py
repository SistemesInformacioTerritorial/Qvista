from moduls.QvImports  import *
from qgis.core import QgsRectangle


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
        self.vengoDeMapeta=False

        # Convertim paràmetres en variables de classe
        self.canvas = canvas
        self.tamanyPetit = tamanyPetit
        self.MouseMoveFlag = False
        # Posem per defecte a False
        self.petit = False
       
        # Preparem el canvas per capturar quan es modifica, i poder repintar el mapeta.
        self.canvas.extentsChanged.connect(self.pintarMapeta)

        # Dimensions i fons del mapeta segosn si és gran o petit
        if self.tamanyPetit:
            self.xTamany = 179
            self.yTamany = 180
            self.setStyleSheet('QFrame {opacity: 50; background-image: url("imatges/MapetaPetit.jpg");}')
        else:
            self.Escala = 15330/ 267 # relacion base "mundo" base mapeta--> 57.457.15730337078651685393258426966
            self.InvEscala= 1/self.Escala  # paracalculos de retorno




            if self.canvas.rotation() == 44:
                self.canvasRotado44= True
                self.xTamany = 389
                self.yTamany = 390
                self.setStyleSheet('QFrame {background-image: url("imatges/MAPETA_SITUACIO_391x392_rot_mio.bmp");}')
                self.seno_44= math.sin(-44 * math.pi /180)
                self.coseno_44= math.cos(-44 * math.pi /180)
                self.seno44= math.sin(44 * math.pi /180)
                self.coseno44= math.cos(44 * math.pi /180)                 
            else:
                self.canvasRotado44= False
                self.xTamany = 267
                self.yTamany = 284
                self.setStyleSheet('QFrame {background-image: url("imatges/MAPETA_SITUACIO_267x284.bmp");}')

        # Definim la geometria del frame del mapeta
        self.setGeometry(0,0,self.xTamany,self.yTamany)
        self.begin = QPoint()
        self.end = QPoint()

        # Aixó serveix per donar ombra al frame
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(5)
        effect.setColor(QColor(120,120,120,0))
        effect.setXOffset(5)
        effect.setYOffset(5)
        effect.setColor(QColor(150,150,150))
        self.setGraphicsEffect(effect)

        # El botó per minimitzar el mapa
        self.botoFerPetit = QPushButton(self)
        icon = QIcon('imatges/mapeta-collapse.png')
        self.botoFerPetit.setIcon(icon)
        self.botoFerPetit.setGeometry(0,0,25,25)
        self.botoFerPetit.show()
        self.botoFerPetit.clicked.connect(self.ferPetit)

        self.show()

    def setBotoMinimitzar(self, botoMinimitzar):
        """Per assignar o no 
        
        Arguments:
            botoMinimitzar {[type]} -- [description]
        """
        if botoMinimitzar:
            self.botoFerPetit.show()
        else:
            self.botoFerPetit.hide()

    def ferPetit(self):
        if self.petit:
            self.setGeometry(0,0,self.xTamany,self.yTamany)
            self.petit = False
            icon = QIcon('imatges/arrow-collapse.png')
            self.botoFerPetit.setIcon(icon)
        else:
            self.setGeometry(0,0,25,25)
            self.petit = True
            icon = QIcon('imatges/mapetaPetit.jpg')
            self.botoFerPetit.setIcon(icon)


    def pintarMapeta(self):
        # Leo rango del canvas rotado 44, pues se ha adaptado a la geometria de la ventana
        rect = self.canvas.extent()
        print('co=6 naranja Canvas queda con angulo 44  xy=',round(rect.xMinimum()),',',round(rect.yMinimum()),'xy=',round(rect.xMaximum()),',',round(rect.yMaximum()))
        
        # Desde el rango del canvas girado 44 , he de calcular el rango inscrito en el que se veria con el canvas a 0 grados
        PPa1=QPoint()
        PPa2=QPoint()
        PPa3=QPoint()
        PPa4=QPoint()

        PPa1.x= rect.xMinimum()
        PPa1.y= rect.yMinimum()
        PPa3.x= rect.xMaximum()
        PPa3.y= rect.yMaximum()
        
        PPa2.x=  PPa3.x
        PPa2.y=  PPa1.y
        PPa4.x=  PPa1.x
        PPa4.y=  PPa3.y
        
        w= self.canvas.widthMM()
        h= self.canvas.heightMM()
        H= (h*self.coseno44)+ (w*self.seno44)
        W= (h*self.seno44)  + (w*self.coseno44)
        anchoMundoVerde= PPa3.x - PPa1.x
        altoMundoVerde=  PPa3.y - PPa1.y
        Escalax= anchoMundoVerde / W
        Escalay= altoMundoVerde / H
        
        Pa1=QPoint()
        Pa2=QPoint()
        Pa3=QPoint()
        Pa4=QPoint()    

        t1= Escalax*h*self.seno44
        t2= Escalax*w*self.coseno44
        t3= Escalax*h*self.coseno44
        t4= Escalax*w*self.seno44

        Pa1.x = PPa1.x
        Pa1.y = PPa1.y + t3
        Pa2.x = PPa4.x + t2
        Pa2.y = PPa4.y
        Pa3.x = PPa2.x
        Pa3.y = PPa2.y + t4
        Pa4.x = PPa1.x + t1
        Pa4.y = PPa1.y

        print('co=7 azul claro  xy=',Pa1.x,',',Pa1.y)
        print('co=7 azul claro  xy=',Pa2.x,',',Pa2.y)
        print('co=7 azul claro  xy=',Pa3.x,',',Pa3.y)
        print('co=7 azul claro  xy=',Pa4.x,',',Pa4.y)

        ancho= ((Pa2.x-Pa1.x)**2+(Pa2.y-Pa1.y)**2)**0.5
        alto=  ((Pa2.x-Pa3.x)**2+(Pa2.y-Pa3.y)**2)**0.5
        ancho=ancho/self.Escala
        alto=alto/self.Escala

        xx= ((Pa1.x -420900) /self.Escala ) -127.088
        yy= ((Pa1.y -4574600) /self.Escala ) +135.111

  
        Par1=QPoint()
        Par2=QPoint()
        Par3=QPoint()
        Par4=QPoint()   

        Par1.x=  (xx * self.coseno_44 - yy * self.seno_44 )
        Par1.y=  (xx * self.seno_44 + yy * self.coseno_44 )
        Par2.x= Par1.x + ancho
        Par2.y= Par1.y 
        Par3.x= Par2.x 
        Par3.y= Par2.y - alto
        Par4.x= Par3.x -ancho
        Par4.y= Par3.y

        print('co=168 gris  xy=',round(Par1.x),',',round(Par1.y))
        print('co=168 gris  xy=',round(Par2.x),',',round(Par2.y))
        print('co=168 gris  xy=',round(Par3.x),',',round(Par3.y))
        print('co=168 gris  xy=',round(Par4.x),',',round(Par4.y))

        puntIn=[]
        puntIn.append(Par1.x)
        puntIn.append(Par1.y)
        puntFi=[]
        puntFi.append(Par2.x)
        puntFi.append(Par2.y)
        puntIn=[]
        puntIn.append(Par1.x)
        puntIn.append(Par1.y)
        puntFi=[]
        puntFi.append(Par3.x)
        puntFi.append(Par3.y)

        xMin = min(puntIn[0],puntFi[0])    #xmin
        xMax = max(puntIn[0],puntFi[0])    #xmax
        yMin = min(puntIn[1],puntFi[1])    #ymin
        yMax = max(puntIn[1],puntFi[1])    #ymax

        self.begin = QPoint(xMin,yMin)
        self.end = QPoint(xMax,yMax)
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(50, 110, 90, 70))  
        qp.setBrush(br)  

        begin_ = QPoint()
        end_ =  QPoint()

        begin_.x= self.begin.x()
        end_.x= self.end.x()
        if self.MouseMoveFlag== False:
            begin_.y= self.yTamany-self.begin.y()
            end_.y=   self.yTamany- self.end.y()
        else:
            begin_.y= self.begin.y()
            end_.y= self.end.y()

        self.MouseMoveFlag= False
        # Pinto rectanculo
        qp.drawRect(begin_.x,begin_.y,end_.x-begin_.x,end_.y-begin_.y)
        # Pinto cruz
        qp.drawLine(QLineF( QPoint( begin_.x +(end_.x-begin_.x)/2, 0),  QPoint( begin_.x +(end_.x-begin_.x)/2,self.yTamany)  ))
        qp.drawLine(QLineF( QPoint( 0, begin_.y +(end_.y-begin_.y)/2),  QPoint( self.xTamany,begin_.y +(end_.y-begin_.y)/2 )  ))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.MouseMoveFlag= True
        self.canvas.update()

    def conversioPantallaMapa(self,punt):
        # xmin ymin xmax y max calculados para el canvas girado 44 grados y con tamañp       390 x  389
        # 412649 4582568 444481 4583144 
        x = punt[0]
        y = punt[1]
        
        xMapa = 420900  +self.Escala * x
        yMapa = 4574600 + self.Escala * y 
        return [xMapa, yMapa]

    
    def mouseReleaseEvent(self, event):
        self.end = event.pos()

        self.xIn = self.begin.x()
        self.yIn = self.yTamany - self.begin.y()
        self.xFi = self.end.x()
        self.yFi = self.yTamany - self.end.y()

      
        # Convierto las coordenadas del mapeta girado 44 a coordenadas de mapeta no girado
        # para buscar la utm
        P1=QPoint()
   
        # segun calculos 
        P1.x=  127.088
        P1.y=  -135.111            

        # Intercepto para hacer las pruebas primer punto de control
        # self.xIn=69
        # self.yIn=170
        # self.xFi=104
        # self.yFi=152

        # Intercepto para hacer las pruebas segundo punto de control
        # self.xIn=208
        # self.yIn=292
        # self.xFi=226
        # self.yFi=257
 
        # print('------------------------')
        # print('co=1 azul En girado 44 (mapeta)  xy=',self.xIn,',',self.yIn,'xy=',self.xFi,',',self.yFi)

        # Calculo las coordenadas en el mapeta "normal" (sin giro) con las coordenadas del mapeta girado
        # a las que les aplico un giro de 44 grados, escala=1 y un desplazamiento de P1
        # ...Para el punto inicial
        self.xIn_= P1.x +  (self.xIn * self.coseno44 - self.yIn * self.seno44 )
        self.yIn_= P1.y +  (self.xIn * self.seno44 + self.yIn * self.coseno44 )
        # ...Para el punto final
        self.xFi_= P1.x +  (self.xFi * self.coseno44 - self.yFi * self.seno44 )
        self.yFi_= P1.y +  (self.xFi * self.seno44 + self.yFi * self.coseno44 )
        # print('co=99 Marron En girado 0 (mapeta)  xy=',self.xIn_,',',self.yIn_,'xy=',self.xFi_,',',self.yFi_)
       
        # Convertimos las coordenadas del punto inicial del mapeta_ang=0 a coordenadas Mundo
        punt1 = self.conversioPantallaMapa([self.xIn_, self.yIn_])
        # print('co=2 verde claro punt1Mundo',punt1)

        # Calculo la la ventana mundo "girado" correspondiente a los puntos del mapeta
        Paux1=QPoint()
        Paux2=QPoint()
        Paux3=QPoint()
        Paux4=QPoint()

        # ancho y alto de la seleccion en el mapeta girado (en mundo)
        distX=  (self.xFi - self.xIn)   # ancho mapeta
        distX= distX * self.Escala           # ancho mundo
        distY=  (self.yFi - self.yIn)   # alto mapeta
        distY= distY * self.Escala           # alto mundo 
        # coordenadas mundo de los 4 puntos señalados en el mapeta
        Paux1.x= punt1[0]
        Paux1.y= punt1[1]
        Paux2.x= Paux1.x + (distX * self.coseno44)
        Paux2.y= Paux1.y + (distX * self.seno44)
        Paux3.x= Paux2.x - (distY * self.seno44)
        Paux3.y= Paux2.y + (distY * self.coseno44)
        Paux4.x= Paux1.x - (distY * self.seno44)
        Paux4.y= Paux1.y + (distY * self.coseno44)
        
        # print('co=3 rojo Caja mundo girada  P2 xy=',round(Paux1.x),',',round(Paux1.y))
        # print('co=3 rojo Caja mundo girada  P2 xy=',round(Paux2.x),',',round(Paux2.y))
        # print('co=3 rojo Caja mundo girada  P3 xy=',round(Paux3.x),',',round(Paux3.y))
        # print('co=3 rojo Caja mundo girada  P4 xy=',round(Paux4.x),',',round(Paux4.y))

        # Calculo rango de esa caja girada, (minima, caja que la engloba)
        punt1[0]= min(Paux1.x, Paux2.x, Paux3.x,Paux4.x)    #xmin
        punt1[1]= min(Paux1.y, Paux2.y, Paux3.y,Paux4.y)    #ymin
        punt2=[]
        punt2.append(max(Paux1.x, Paux2.x, Paux3.x,Paux4.x))
        punt2.append(max(Paux1.y, Paux2.y, Paux3.y,Paux4.y))
        
        # print('co=4 amarillo  Rango de caja girada  xy=',round(punt1[0]),',',round(punt1[1]),'xy=',round(punt2[0]),',',round(punt2[1]))
        # Necesitare tener estas coordenadas como QgsRectangle...
        rang = QgsRectangle(punt1[0], punt1[1], punt2[0], punt2[1])
        
        # Pasamos rango al canvas para que lo represente
        # print('co=5 violeta  claro Coord que pasamos al canvas:  xy=',round(rang.xMinimum()),',',round(rang.yMinimum()),'xy=',round(rang.xMaximum()),',',round(rang.yMaximum()))
        self.canvas.setExtent(rang)
        self.canvas.refresh()



import math

if __name__ == "__main__":
    # exit()
    # projecteInicial='../dades/projectes/tra/mio.qgs'
    projecteInicial='D:/qVista/Dades/Projectes/tra/mio.qgs'


    with qgisapp() as app:
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
        canvas.show()
        canvas.setRotation(44)

        qvMapeta = QvMapeta(canvas, tamanyPetit = False, pare=canvas)
        qvMapeta.move(0,0)
        qvMapeta.setBotoMinimitzar(True)
        qvMapeta.show()
