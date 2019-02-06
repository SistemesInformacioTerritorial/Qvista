
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

        # Convertim paràmetres en variables de classe
        self.canvas = canvas
        self.tamanyPetit = tamanyPetit
        
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
            self.xTamany = 267
            self.yTamany = 284
                        
            # self.xTamany = 389
            # self.yTamany = 390
            self.setStyleSheet('QFrame {background-image: url("imatges/MAPETA_SITUACIO_267x284.bmp");}')
            # self.setStyleSheet('QFrame {background-image: url("imatges/MAPETA_SITUACIO_267x284_rot.bmp");}')
            # self.setStyleSheet('QFrame {background-image: url("imatges/MAPETA_SITUACIO_389x390_rot.bmp");}')




        # Definim la geometria del frame del mapeta
        self.setGeometry(0,0,self.xTamany,self.yTamany)
        self.canvas.rotate(0)
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
        # qp.drawRect(QRect(self.begin, self.end))  
        rect = self.canvas.extent()
        puntIn = self.conversioMapaPantalla([rect.xMinimum(),rect.yMinimum()])
        puntFi = self.conversioMapaPantalla([rect.xMaximum(),rect.yMaximum()])
        xMin = puntIn[0]
        yMin = puntIn[1]
        xMax = puntFi[0]
        yMax = puntFi[1]
        self.begin = QPoint(xMin,yMin)
        self.end = QPoint(xMax,yMax)
        self.repaint()
        # print (xMin,yMin, xMax, yMax)
        # print ('hola')

    def paintEvent(self, event):
        qp = QPainter(self)
        # self.pintor = qp
        br = QBrush(QColor(50, 110, 90, 70))  
        qp.setBrush(br)   
        qp.drawRect(QRect(self.begin, self.end))
        # print(self.begin.x(), self.end.x(),self.begin.x() +(self.end.x()-self.begin.x())/2)

        
        qp.drawLine(QLineF( QPoint(  self.begin.x() +(self.end.x()-self.begin.x())/2  ,        0), 
                            QPoint(  self.begin.x() +(self.end.x()-self.begin.x())/2   ,     self.yTamany)  ))
        qp.drawLine(QLineF( QPoint(  0, self.begin.y() +(self.end.y()-self.begin.y())/2 ), 
                            QPoint(    self.xTamany, self.begin.y() +(self.end.y()-self.begin.y())/2  )  ))

        #self.qp.drawRect(QRect(self.begin, self.end))       
        #self.lblMapeta.setPixmap(self.imatge)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def conversioPantallaMapa(self,punt):
        # xmin ymin xmax y max calculados para el canvas girado 44 grados y con tamañp       390 x  389
        # 412649 4582568 444481 4583144 
        

        x = punt[0]
        y = punt[1]

        # aqui
        pixelX = (436230-420900)/self.xTamany
        pixelY = (4591170-4574600)/self.yTamany
        

        xMapa = x*pixelX+420900
        yMapa = y*pixelY+4574600
        # print (xMapa, yMapa)
        return [xMapa, yMapa]

    def conversioMapaPantalla(self,punt):
        x = punt[0]-420900
        y = punt[1]-4574600
        pixelX = self.xTamany/(436230-420900)
        # pixelY = self.yTamany/(4591170-4574600)
        pixelY = self.yTamany/(4590906-4574600)
        xPantalla = x*pixelX
        yPantalla = self.yTamany - y*pixelY
        # print (xPantalla, yPantalla)
        return [xPantalla, yPantalla]

    def mouseReleaseEvent(self, event):
        self.end = event.pos()

        self.xIn = self.begin.x()
        self.yIn = self.yTamany - self.begin.y()
        self.xFi = self.end.x()
        self.yFi = self.yTamany - self.end.y()

        print('xIn',self.xIn,'  xFi',self.xFi)
        print('yIn',self.yIn,'  yFi',self.yFi)
        punt1 = self.conversioPantallaMapa([self.xIn, self.yIn])
        punt2 = self.conversioPantallaMapa([self.xFi, self.yFi])
        # print('punt1',punt1,'  punt2',punt2)
        rang = QgsRectangle(punt1[0], punt1[1], punt2[0], punt2[1])

        # Canviem l'extensió del canvas segons el rang recien calculat.
        self.canvas.zoomToFeatureExtent(rang)
        print(round(punt1[0]), round(punt1[1]), round(punt2[0]), round(punt2[1]))
        
        
        # print (self.begin, self.end)
        # self.lblMapeta.update()

import math


def escalar(a,b):
    escalar1=a.x*b.x + a.y*b.y
    return escalar1


def prueba_0():
    # funcionan con radianes
    seno0= math.sin(0 * math.pi /180)
    coseno0= math.cos(0 * math.pi /180)
    
    p1= QPoint()
    p2=QPoint()
    P1= QPoint()
    P2=QPoint()
    P_max=QPoint()
    P_min=QPoint()
    P_resultado=QPoint()
    p_mapeta=QPoint()
    
    p1.x= 0
    p1.y=0
    p2.x= 267
    p2.y=0

    P1.x= 420900
    P1.y=4574600
    P2.x= 436230
    P2.y=4574600
    Escala_x= (P2.x-P1.x) / (p2.x-p1.x)

    p_mapeta.x=251
    p_mapeta.y=173
   

    P_resultado.x= round(P1.x + Escala_x * (p_mapeta.x * coseno0 - p_mapeta.y * seno0 ))
    P_resultado.y= round(P1.y + Escala_x * (p_mapeta.y * seno0 + p_mapeta.y * coseno0 ))
    # en vec_  .x= xfin-xini
    # en vec_  .y= yfin-yini
    #esc_a_b= escalar(vec_a, vec_b)

    #mod_a= math.hypot(vec_a.x, vec_a.y)
    print(p_mapeta.x,p_mapeta.y)
    print(P_resultado.x,P_resultado.y)
    pass

def prueba_44():
    # funcionan con radianes
    seno44= math.sin(44 * math.pi /180)
    coseno44= math.cos(44 * math.pi /180)
    
    p1= QPoint()
    p2=QPoint()
    P1= QPoint()
    P2=QPoint()
    P_max=QPoint()
    P_min=QPoint()
    P_resultado=QPoint()
    p_mapeta=QPoint()
    
    p1.x= 0
    p1.y=0
    p2.x= 267
    p2.y=0

    P1.x= 420900
    P1.y=4574600
    P2.x= 436230
    P2.y=4574600
    Escala_x= (P2.x-P1.x) / (p2.x-p1.x)

    p_mapeta.x=72
    p_mapeta.y=33


    P_resultado.x= round(P1.x + Escala_x * (p_mapeta.x * coseno44 - p_mapeta.y * seno44 ))
    P_resultado.y= round(P1.y + Escala_x * (p_mapeta.y * seno44 + p_mapeta.y * coseno44 ))

    print(p_mapeta.x,p_mapeta.y)
    print(P_resultado.x,P_resultado.y)
    pass


def calculo_pmax_pmin():
    # funcionan con radianes
    seno44= math.sin(44 * math.pi /180)
    coseno44= math.cos(44 * math.pi /180)


    P2=QPoint()
    P3=QPoint()
    P_max=QPoint()
    P_min=QPoint()

    P2.x= 436230
    P2.y= 4574600

    P3.x= 436230
    P3.y= 4591112

    mod_a1= P3.y-P2.y
    mod_b1= mod_a1 * seno44
    mod_c1= mod_a1 * coseno44
    
    incX1= mod_c1 * seno44
    incY1= mod_c1 * coseno44
    P_max.x = 436230 + incX1
    P_max.y = 4574600 + incY1

    mod_a2= mod_a1
    mod_b2= mod_a2 * coseno44
    mod_c2= mod_a2 * seno44
    
    incX2= mod_c2 * coseno44
    incY2= mod_c2 * seno44
    P_min.x = 420900 - incX2
    P_min.y = 4574600 + incY2

    print(round(P_min.x),round(P_min.y),round(P_max.x),round(P_max.y))

    

  

if __name__ == "__main__":
    calculo_pmax_pmin()
    prueba_0()
    prueba_44()    
    
    projecteInicial='../dades/projectes/BCN11_nord.qgs'


    with qgisapp() as app:
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
        canvas.show()

        qvMapeta = QvMapeta(canvas, tamanyPetit = False, pare=canvas)
        qvMapeta.move(20,20)
        qvMapeta.setBotoMinimitzar(True)
        qvMapeta.show()

