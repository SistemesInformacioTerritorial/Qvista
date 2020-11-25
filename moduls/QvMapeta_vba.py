from moduls.QvImports  import *

from qgis.core import QgsRectangle, QgsPointXY

from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout 
from PyQt5.QtWidgets import QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QImage, QPainter, QTransform, QColor, QPen
from PyQt5.QtGui import  QBrush, QPolygon, QPalette
from moduls.QvDropFiles import QvDropFiles
from PyQt5.QtCore import QRect, Qt,  QPoint, QPointF

import os.path
import math
import os
from datetime import datetime
import configuracioQvista

# import time


class QvMapeta(QFrame):
    """La classe que defineix el mapeta de posicionament i que controla un 
    canvas."""
    """
    CONVENIO DE SISTEMAS DE COORDENADAS Y ANGULOS:
    El mapeta tiene su origen en la esquina superior izquierda.
    Las X crecen hacia el Este
    Las Y crecen hacia el sur
    Las rotaciones se hacen desde su centro, con origen en en el eje de las Y.
    Los angulos son en el sentido de las agujas del reloj
    Las coordenadas X del Mundo, crecen en sentido Este. Las Y en sentido Norte
    El Mapeta debe ser cuadrado, y con el mismo factor de escala en X y en Y

    """
    def __init__(self, canvas, ficheroMapeta, pare = None):
        """Inicialització del mapeta.
        
        Arguments:
            QFrame {[self]} -- [QvMapeta]
            canvas {[QgsMapCanvas]} -- [El canvas que gesrtionarà el mapeta.]
        
        Keyword Arguments:
            tamanyPetit {bool} -- [True pel Mapeta petit, False pel Mapeta
             gran] (default: {False})
            pare {[QWidget]} -- [El widget sobre el que es pintarà el mapeta.
             és obligatori.] (default: {None})
        """
        QFrame.__init__(self)

        # Assigno el mapeta al parent  JNB
        self.setParent(pare)
        self.pare = pare
        self.setDropable()
        self.pintoCentro = False   # auxiliar...

        self.sw_l = False   # para crear .bas

        self.Cuadrante = 0
        self.centro_v= QPoint()
        
        self.ficheroMapeta = ficheroMapeta
        datos_mapeta = self.CalcularPNGyRangoMapeta(ficheroMapeta)


        linea= "Fic: "+ str(datos_mapeta[0]) +'\n'
        linea= linea + 'xmin:  '+ str(round(datos_mapeta[1],2)) +'\n'
        linea= linea + 'ymin:  '+ str(round(datos_mapeta[2],2)) +'\n'
        linea= linea + 'xmax:  '+ str(round(datos_mapeta[3],2)) +'\n'
        linea= linea + 'ymax:  '+ str(round(datos_mapeta[4],2)) +'\n'
        linea= linea + 'W:  '+ str(datos_mapeta[5]) +'\n'
        linea= linea + 'H:  '+ str(datos_mapeta[6])
        self.setToolTip(linea)
        # print(datos_mapeta)
        # nombre png
        self.PngMapeta = datos_mapeta[0]

        # rango mundo
        self.xmin_0 = datos_mapeta[1];  self.ymin_0 = datos_mapeta[2]
        self.xmax_0 = datos_mapeta[3];  self.ymax_0 = datos_mapeta[4]

        # ancho, alto PNG
        self.xTamany = datos_mapeta[5];   self.yTamany = datos_mapeta[6]

        # De entrada cargo el mapeta no girado, angulo=0
        self.seno_antigiro = 0;            self.coseno_antigiro = 1
        self.seno_giro = 0;                self.coseno_giro = 1

        # Convertim paràmetres en variables de classe
        self.canvas = canvas
        self.MouseMoveFlag = False
        self.MousePressFlag = False
       
        # Preparem el canvas per capturar quan es modifica, i poder repintar
        #  el mapeta.
        self.canvas.extentsChanged.connect(self.pintarMapeta)
        # Cuando el canvas cambie su rotacion, cambiará la imagen del mapeta
        self.canvas.rotationChanged.connect(self.cambiarMapeta)




        # Cargamos el PNG en el widget Mapeta, que es un Frame via 
        # setStyleSheet
        parametro = "{opacity: 50; background-image: url("+self.PngMapeta+");} "
        parametro =parametro.replace('\\','/')
        self.setStyleSheet('QFrame' + parametro)

        # Escala como relacion base Mundo" base Mapeta. Se podria calcular en
        #  base a las Y
        self.Escala = (self.xmax_0 - self.xmin_0) / self.xTamany 

        # Definim la geometria del frame del mapeta, el PGW manda.
        self.setGeometry(0, 0, self.xTamany, self.yTamany)
        # self.setGeometry(20,20,self.xTamany,self.yTamany)
        # self.move(20,20)

        # puntos que definen la ventana sobre el Mapeta que muestra el area de 
        # cartografia visible
        self.begin = QPoint();     self.end = QPoint()
        # region Efectossss
    
        # Aixó serveix per donar ombra al frame
        # effect = QGraphicsDropShadowEffect()
        # effect.setBlurRadius(5)
        # effect.setColor(QColor(120,120,120,0))
        # effect.setXOffset(5)
        # effect.setYOffset(5)
        # effect.setColor(QColor(150,150,150))
        # self.setGraphicsEffect(effect)

        # ombra=QvConstants.ombra(self,radius=20)
        # self.setGraphicsEffect(ombra)

        # QvConstants.afegeixOmbraWidget(self)
        # endregion
        
        # region BOTONES AUXILIARES para hacer comprobaciones

        # BOTON AUXILIAR PARA COMPROBACIONES, INVOCA EL CAMBIO DE ROTACION 
        self.botocambiarRotacion = QPushButton("Rot +", self)
        self.botocambiarRotacion.setGeometry(0, 0, 50, 25)
        self.botocambiarRotacion.move(20,0)
        self.botocambiarRotacion.show()  
        self.botocambiarRotacion.clicked.connect(self.cambiarRotacion_mas)



        # # BOTON AUXILIAR PARA COMPROBACIONES, 
        self.botomuestro = QPushButton("Rot -", self)
        self.botomuestro.setGeometry(0, 0, 50, 25)
        self.botomuestro.move(20, 30)
        self.botomuestro.show()
        self.botomuestro.clicked.connect(self.cambiarRotacion_menos)        
       
        # # BOTON AUXILIAR PARA COMPROBACIONES, QUE SEÑALA EL CENTRO DEL CANVAS 
        # self.botocentroCanvas = QPushButton("Centro", self)
        # self.botocentroCanvas.setGeometry(0, 0, 50, 25)
        # self.botocentroCanvas.move(20,60)
        # self.botocentroCanvas.show()   
        # self.botocentroCanvas.clicked.connect(self.centroCanvas)


        # # BOTON AUXILIAR PARA COMPROBACIONES, QUE activa coordenadas mouse
        self.botologMSt = QPushButton("logMSt",self)
        self.botologMSt.setGeometry(0, 0, 50, 25); self.botologMSt.move(20, 90)
        self.botologMSt.show()
        self.botologMSt.clicked.connect(self.logMSt)   
        # endregion
     
        # region  cuarentena
        # self.ledit = QLineEdit("entrar angulo",self)
        # self.ledit.editingFinished.connect(self.cambiarRotacion)
        # self.ledit.show()
        # endregion

        # self.canvas.setCenter(QgsPointXY(xcent, ycent))
        # self.setMouseTracking(True)
    
    #region  Funciones auxiliares y relacionadas con botones los auxiliares

            

    
    
    
    def logMSt(self):
        '''
        Funcion auxiliar para comprobaciones. Gestiona variable global como 
        interruptor  True/False  de  manera que si True se printan valores 
        en distintas partes del programa
        '''
        if self.sw_l is True:
            self.botologMSt.setText("NO logMSt")
            self.sw_l=False
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #block
                linea= '    MbeSendKeyin "null"\n';  fbas.write( linea)  
                linea= 'End Sub\n';  fbas.write( linea) 


                datos_mapeta= self.CalcularPNGyRangoMapeta(self.ficheroMapeta)


                linea= "    'datos mapeta: "+ str(datos_mapeta[0])
                linea= linea + '  '+ str(datos_mapeta[1])
                linea= linea + '  '+ str(datos_mapeta[2])
                linea= linea + '  '+ str(datos_mapeta[3])
                linea= linea + '  '+ str(datos_mapeta[4])
                linea= linea + '  '+ str(datos_mapeta[5])
                linea= linea + '  '+ str(datos_mapeta[6])
            
 
                linea=linea+"\n"
                fbas.write( linea) 





        else:
            self.botologMSt.setText("SI logMSt")
            self.sw_l=True 
            try:
                os.remove('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas')
            except :
                pass
            
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'w') as fbas:
                linea= "    'ANGULO: "+ str(self.canvas.rotation()) +"\n"; fbas.write( linea)
                fbas.write("Sub main\n") 
                fbas.write("    Dim pt As Mbepoint\n")  
            # crear log

    # def mostrar(self):
    #     '''
    #     Funcion auxiliar para comprobaciones\n
    #     Establece inicio de registro escribiendo linea y fechahora
    #     Actualiza label del boton
    #     '''
    #     try:
    #         os.system('cls')  
    #     except:
    #         pass    

    #     print(); print(); print(); print()
    #     print("________________________________________")
    #     now = datetime.now() # current date and time
    #     date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    #     print("Día y hora:", date_time)

    #     if self.sw_p==True:
    #         self.botomuestro.setText("NO print")
    #         self.sw_p=False
    #     else:
    #         self.botomuestro.setText("SI print")
    #         self.sw_p=True
    def centroCanvas(self): 
        '''
        Funcion auxiliar para hacer pruebas, marca con cruz el centro del 
        canvas
        '''
        self.botocentroCanvas.setText("centro")
        
        if self.pintoCentro == True:
            self.pintoCentro=False
        else:
            self.pintoCentro=True
        
        self.repaint()
    def cambiarRotacion_mas(self): 
        '''
        Funcion auxiliar para hacer pruebas
        '''
        #region Trozo de codigo inutil aqui pero reaprovechable
        # parametro= "{opacity: 50; background-image: url("+self.PngMapeta+");} "
        # self.setStyleSheet('QFrame {opacity: 50; background-image: url(D:/tmp/JNB_temporal.png);}')
        # parametro= "{opacity: 50; background-image: url(D:/tmp/temporal.png);} "
        # parametro= "{opacity: 50; background-image: url();} "
        # parametro=parametro.replace('\\','/')
        # self.setStyleSheet('QFrame'+ parametro)

        # self.setGeometry(0,0,200,200)
        # oImage = QImage("D:/tmp/temporal.png")

        # palette = QPalette()
        # rect= QRect(300, 300, 200, 200)
        # sImage = oImage.copy(rect) 
        # palette.setBrush(QPalette.Window, QBrush(sImage))                        
        # self.setPalette(palette)
        # self.show()

        # oImage = QImage("D:/tmp/temporal.png")
        # palette = QPalette()
        # # rect= QRect(0, 0, 3, 300)
        # # sImage = oImage.copy(rect) 
        # palette.setBrush(QPalette.Window, QBrush(oImage))                        
        # self.setPalette(palette)
        # self.show()
        #endregion

        if self.canvas.rotation() >= 360:
            
            self.canvas.setRotation(self.canvas.rotation() -360)  

# aqui
        rect_a = self.canvas.extent()  
        # Convierto las coordenadas del mapeta girado 44 a coordenadas de mapeta no girado para buscar la utm')
        self.canvas.setRotation(self.canvas.rotation()+20)
        rect_d = self.canvas.extent()  
        if self.sw_l:  #escribir  caja xIn,yIn a xFi,yFi
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= '    MbeSendKeyin "pla block":    MbeSendKeyin "co=Yellow":    MbeSendKeyin "lc=2":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_a.xMinimum(),2), round(rect_a.yMinimum(),2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_a.xMaximum(),2), round(rect_a.yMaximum(),2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_d.xMinimum(),2), round(rect_d.yMinimum(),2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_d.xMaximum(),2), round(rect_d.yMaximum(),2)); fbas.write( linea)                


        # self.canvas.setRotation(30)    # primer cuadrante ok
        # self.canvas.setRotation(120)    # segundo cuadrante
        # self.canvas.setRotation(210)    # tercer cuadrante ok
        # self.canvas.setRotation(300)    # cuarto cuadrante
        # rect_a = self.canvas.extent() 
        # if self.canvas.rotation()==0:
        #     self.canvas.setRotation(200)    # 
        # else:
        #     self.canvas.setRotation(0)
        # rect_d = self.canvas.extent()  
        # if self.sw_l:  #escribir  caja xIn,yIn a xFi,yFi
        #     with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
        #         linea= '    MbeSendKeyin "pla block":    MbeSendKeyin "co=Yellow":    MbeSendKeyin "lc=2":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_a.xMinimum(),2), round(rect_a.yMinimum(),2)); fbas.write( linea)
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_a.xMaximum(),2), round(rect_a.yMaximum(),2)); fbas.write( linea)
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_d.xMinimum(),2), round(rect_d.yMinimum(),2)); fbas.write( linea)
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect_d.xMaximum(),2), round(rect_d.yMaximum(),2)); fbas.write( linea)                


        self.botocambiarRotacion.setText(str(self.canvas.rotation()))
        self.canvas.repaint() 
        self.pintarMapeta()

    def cambiarRotacion_menos(self): 
        '''
        Funcion auxiliar para hacer pruebas
        '''
      

        if self.canvas.rotation() >= 360:
            self.canvas.setRotation(self.canvas.rotation() -360)        
        self.canvas.setRotation(self.canvas.rotation()-10)

        
        self.botomuestro.setText(str(self.canvas.rotation()))
        self.canvas.repaint() 
        self.pintarMapeta()

    def prtPnt(self,nota,Pnt,Pnt2=None):
        '''
        Para comprobaciones en microstation, facilita la transcripcion de coordenadas
        '''
        if Pnt2 != None:
            try:
                literal= "xy="+str(round(Pnt,3))+","+str(round(Pnt2,3))

            except :
                pass
            print(nota,literal)  
            return


        try:
            literal= "xy="+str(round(Pnt.x,3))+","+str(round(Pnt.y,3))
            literal=literal.replace(' ','')
        except :
            try:
                literal= "xy="+str(round(Pnt.x(),3))+","+str(round(Pnt.y(),3))
                literal=literal.replace(' ','')
            except:
                try:
                    literal= "xy="+str(round(Pnt[0],3))+","+str(round(Pnt[1],3))
                    literal=literal.replace(' ','')
                except :
                    pass
        print(nota,literal)    
    def prtRect(self,nota,rango):
        '''
        Para comprobaciones en microstation, facilita la transcripcion de 
        coordenadas
        '''
        xmin=rango.xMinimum();   ymin=rango.yMinimum()
        xmax=rango.xMaximum();   ymax=rango.yMaximum()
        try:
            literal= "min xy="+str(round(xmin,3))+","+str(round(ymin,3))
            print(nota,literal)
            literal= "max xy="+str(round(xmax,3))+","+str(round(ymax,3))
            print(nota,literal)

        except :
            pass
    def mouseDoubleClickEvent (self, event):
        '''
        Escribe la hora y las xy del dobleclick\n
        Inhibe el mostrar
        '''
    def conversioPantallaMapa(self,punt):
        """
        Entran: coordenadas del mapeta\n
        Salen: coordenadas mundo
        """
        x = punt[0];                                    y = punt[1]
        xMapa = self.xmin_0  +self.Escala * x;          
        yMapa = self.ymin_0 + self.Escala * y 
        return [xMapa, yMapa]     
    def DetectoCuadrante(self):
        """
        Retorno el cuadrante en que está el angulo de rotacion
        4  |  1
        3  |  2
        """
        Cuadrante=0
        if 0 <= self.canvas.rotation() <=90:             Cuadrante=1
        elif 90 < self.canvas.rotation() <= 180:         Cuadrante=2
        elif 180 < self.canvas.rotation() <= 270:        Cuadrante=3
        elif 270 < self.canvas.rotation() <= 360:        Cuadrante=4
        else:                                            Cuadrante= -1
        return Cuadrante    
    

   
    #region  Funciones relacionadas con el DROP sobre mapeta
    def CalcularPNGyRangoMapeta(self,ficheroEnviado):
        '''
        Hay 2 ficheros complementarios: PNG y PGW. (PNG la imagen, 
        PGW su georeferenciacio,  en esta versión referida a un mapeta sin 
        rotación). La funcion recibe un fichero (cualquiera de los dos) y 
        busca su complementario. 
        Con ambos calcula y la anchura y altura del PNG, y su rango.
        '''
        split_nombre=os.path.splitext(ficheroEnviado)
        ficheroPNG=  split_nombre[0]+".png"
        ficheroPGW=  split_nombre[0]+".pgw"

        pixmap = QPixmap(ficheroPNG)                     
        heigthPNG= pixmap.height()                       
        widthPWG= pixmap.width()    
        
        try:
            if not os.path.exists(ficheroPGW):
                print("PNG sin PGW")
                return

            wld =open(ficheroPGW, "r")   
            A=float(wld.readlines(1)[0])
            D=float(wld.readlines(2)[0])
            B=float(wld.readlines(3)[0])
            E=float(wld.readlines(4)[0])
            C=float(wld.readlines(5)[0])
            F=float(wld.readlines(6)[0])
            wld.close
            x=heigthPNG;             y=widthPWG
            x1= A*x + B*y + C;       y1 =D*x + E*y + F
            xmin= C;            ymin= F
            xmax= x1;           ymax= y1
            return ficheroPNG,xmin,ymin,xmax,ymax,  widthPWG , heigthPNG        

        except:
            print("problemas PGW")      
    def PngPgwDroped(self,ficheroMapeta):
        '''
        Recibe un fichero soltado y lo manda a funcion para calcular el
        nombre del mapeta y su rango
        '''
        ficheroEnviado= ficheroMapeta[0]
        datos_mapeta= self.CalcularPNGyRangoMapeta(ficheroEnviado)

        # if self.sw_l:  #escribir datos_mapeta
        #     with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
        #         linea= "    'datos mapeta: "+  datos_mapeta
        #         linea=linea+"\n"
        #         fbas.write( linea) 
  
        
        linea= "Fic: "+ str(datos_mapeta[0]) +'\n'
        linea= linea + 'xmin:  '+ str(round(datos_mapeta[1],2)) +'\n'
        linea= linea + 'ymin:  '+ str(round(datos_mapeta[2],2)) +'\n'
        linea= linea + 'xmax:  '+ str(round(datos_mapeta[3],2)) +'\n'
        linea= linea + 'ymax:  '+ str(round(datos_mapeta[4],2)) +'\n'
        linea= linea + 'W:  '+ str(datos_mapeta[5]) +'\n'
        linea= linea + 'H:  '+ str(datos_mapeta[6])
        self.setToolTip(linea)

        self.PngMapeta= datos_mapeta[0]
        self.xmin_0=    datos_mapeta[1]
        self.ymin_0=    datos_mapeta[2]
        self.xmax_0=    datos_mapeta[3]
        self.ymax_0=    datos_mapeta[4]
        self.xTamany = datos_mapeta[5]      
        self.yTamany = datos_mapeta[6]   

        self.setGeometry(0, 0, self.xTamany, self.yTamany)   # Actualizo tamaño mapeta (aqui??)  
        # self.move(20,20) 
        self.cambiarMapeta()    
    def setDropable(self):
        '''
         Implementacion Drop ficheros png y pgw sobre el mapeta. 
         Mapeta será capaz de recibir PNG o PGW para recargar su imagen
        '''
        self.setAcceptDrops(True)
        drop = QvDropFiles(self)
        drop.llistesExts(['.png', '.pgw'])
        drop.arxiusPerProcessar.connect(self.PngPgwDroped)
    #endregion
        
    #region Funciones relacionadas con el dibujo de la cruz y ventanaMapeta
    def SegmentoEnCirculo(self, P1, P2, centro, radio):
        # print(P1);         print(P2);         print(centro);         print (radio)
       
        if P1.x()== P2.x():
            x=P1.x()
            a= centro.x()
            b= centro.y()
            y=  math.sqrt(math.pow(radio, 2) - math.pow((x-a), 2)) + b
            Ymenor= 2*b-y
            Ymayor= y

            return QPoint(x,Ymenor),QPoint(x,Ymayor)
        
        if P1.y()== P2.y():
            y=P1.y()
            a= centro.x()
            b= centro.y()
            x=  math.sqrt(math.pow(radio, 2) - math.pow((y-b), 2)) + a
            Xmenor= 2*b-x
            Xmayor= x

            return QPoint(Xmenor,y),QPoint(Xmayor,y)            
    def discrimimar_caso_H(self,P1, PW, PE):
        '''
        Saber si P1 esta en zona West/Centro/ Est delimitadas por PW y PE
        '''
        if P1.x() <= PW.x():
            return "casoW" 
        elif P1.x() >= PE.x():
            return "casoE"             
        else:
            return "casoHC"
    def discrimimar_caso_V(self,P1, PN, PS):
        '''
        Saber si P1 esta en zona Norte/Centro/ Sur delimitadas por PN y PS
        '''
        if P1.y() <= PN.y():
            return "casoN" 
        elif P1.y() >= PS.y():
            return "casoS"             
        else:
            return "casoVC"            
    def SegmentoDeRangoEnCirculo(self,P1,P2,centro,radio):
        '''
        Retorna l trozo d segmento incluido n un circulo y l caso pra control
                P2
                (W) (C) (E) 
        P1  (W) 1   2   3
            (C) 4   5   6
            (E) 7   8   9
        '''
        # print(P1);         print(P2);         print(centro);         print (radio)
       
        if P1.x()== P2.x():    # caso vertical
            
            x=P1.x()
            a= centro.x()
            b= centro.y()
            y=  math.sqrt(math.pow(radio, 2) - math.pow((x-a), 2)) + b
            Ymenor= 2*b-y;        Ymayor= y
            PN= QPoint(x,Ymenor);       PS= QPoint(x,Ymayor)

            caso1 = self.discrimimar_caso_V(P1, PN, PS)
            caso2 = self.discrimimar_caso_V(P2, PN, PS)
            if caso1== "casoN":
                if caso2== "casoN":      return None, None,"V1",False   # 
                elif caso2== "casoVC":   return PN, P2,"v2" ,True        #
                elif caso2== "casoS":    return PN, PS,"V3" ,True        # 

            elif caso1== "casoVC":
                if caso2== "casoN":      return None,None,"V4", False  # no posible por ordenacion de datos entrada  
                elif caso2== "casoVC":   return P1,P2,"V5" ,True    #
                elif caso2== "casoS":    return P1,PS,"V6" ,True   #
            
            elif caso1== "casoS":
                if caso2== "casoN":      return None,None,"v7" , False    # no posible por ordenacion de datos entrada
                elif caso2== "casoVC":   return None,None,"V8" , False   # no posible por ordenacion de datos entrada
                elif caso2== "casoS":    return None,None,"V9" , False    # no posible por ordenacion de datos entrada

            return None,None,None,False
        if P1.y()== P2.y():    # caso horizontal
            y=P1.y();   
            a= centro.x(); b= centro.y()
            try:
                x=  math.sqrt(math.pow(radio, 2) - math.pow((y-a), 2)) + a
            except :
                pass
            
            Xmenor= 2*b-x;              Xmayor= x
            PW= QPoint(Xmenor,y);       PE= QPoint(Xmayor,y)
            caso1 = self.discrimimar_caso_H(P1, PW, PE)
            caso2 = self.discrimimar_caso_H(P2, PW, PE)
            if caso1== "casoW":
                if caso2== "casoW":      return None, None,"H1",False   # 
                elif caso2== "casoHC":   return PW, P2,"H2" ,True        #
                elif caso2== "casoE":    return PW, PE,"H3" ,True        # 

            elif caso1== "casoHC":
                if caso2== "casoW":      return None,None,"H4", False  # no posible por ordenacion de datos entrada  
                elif caso2== "casoHC":   return P1,P2,"H5" ,True    #
                elif caso2== "casoE":    return P1,PE,"H6" ,True   #
            
            elif caso1== "casoE":
                if caso2== "casoW":      return None,None,"H7" , False    # no posible por ordenacion de datos entrada
                elif caso2== "casoHC":   return None,None,"H8" , False   # no posible por ordenacion de datos entrada
                elif caso2== "casoE":    return None,None,"H9" , False    # no posible por ordenacion de datos entrada

            return None,None,None,False
    #endregion
    

    #  M E O L L O  !!!!!!!
    def cambiarMapeta(self):
        """
          El canvas ha girado. Hay que recargar la imagen del mapeta apropiada.\n
          La imagen sin giro se gira lo que manda la rotación del canvas y se recarga en el mapeta
          Se invoca en la carga y cuando se detecta una rotacion
        """
        if self.sw_l:  #escribir rotacion
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= "    'detecto giro: "+ str(self.canvas.rotation())
                linea=linea+"\n"
                fbas.write( linea) 

        angulo_rotacion=self.canvas.rotation()
        # Roto la imagen
        pixmap=QPixmap(self.PngMapeta)
        # self.setGeometry(20,20,self.xTamany,self.yTamany)
        rot_pixmap = pixmap.transformed(QTransform().rotate(angulo_rotacion),Qt.SmoothTransformation)
                
        # Recorto la imagen al tamaño establecido en el PGW
        hp= rot_pixmap.height()
        pc=(hp-self.xTamany)/2
        rect= QRect(pc, pc, self.xTamany, self.yTamany)
        cropped_pixmap = rot_pixmap.copy(rect) 

        # paso FEO (salvar a disco) para recargar la imagen. 
        cropped_pixmap.save("mapesOffline/JNB_temporal.png","PNG",100) 
        # AQUI, intento de calcular las coordenadas del centro de la ventana
        # self.xIn=  ((self.xIn -(self.xTamany/2)) * self.coseno_giro     - (self.yIn -(self.xTamany/2) ) * self.seno_giro )   + (self.xTamany/2) 
        # self.yIn=  ((self.xIn -(self.xTamany/2)) * self.seno_giro       + (self.yIn -(self.xTamany/2) ) * self.coseno_giro )  + (self.xTamany/2) 

        self.setStyleSheet('QFrame {opacity: 50; background-image: url(mapesOffline/JNB_temporal.png);}')
    def pintarMapeta(self):
        """
        Se invoca cuando cambian el tamaño del canvas y cuando hay una 
        rotacion del canvas\n
        Despues de seleccionar una ventana en el mapeta, se actualiza 
        la cartografia correspondiente  en el canvas, y se adapta a
        las proporciones del canvas (estado inicial y 
        redimensionamientos).\n
        Estás proporciones serán diferentes a las de la ventana ventana 
        del mapeta (nuestra seleccion) y por lo tanto debemos recalcular 
        la ventana del mapeta representando sobre éste el area de 
        cartografia visible y una cruz que indica el centro\n
        Esta funcion calcula unas coordenadas para que trabaje el 
        paintEvent (que es quien pinta la caja y la cruz...) 
        """
        
        # detecto cuadrante, habra que hacer calculos en funcion de el....
        self.Cuadrante = self.DetectoCuadrante()
        if self.sw_l:  #escribir cuadrante y rotacion
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= "    'Cuadrante: "+ str(self.Cuadrante) +"\n"; fbas.write( linea) 
                linea= "    'rotation: "+ str(self.canvas.rotation()) +"\n"; fbas.write( linea)

        #region: Declaración variables que usare
        PPa1=QPoint(); PPa2=QPoint(); PPa3=QPoint(); PPa4=QPoint()  # mundo 
        Par1=QPoint(); Par2=QPoint(); Par3=QPoint(); Par4=QPoint()  # mapeta
        Pa1=QPoint();  Pa2=QPoint();  Pa3=QPoint();  Pa4=QPoint()   # mundo
        #endregion: Declaración variables que usare

        # Leo rango del canvas , pues se ha adaptado a la geometria de 
        # la ventana y calculo el rango inscrito en el que se veria con el
        #  canvas a 0 grados
        rect = self.canvas.extent()
        # Cuando hay rotacion el canvas.extend NO nos da 
        # el correspondiente al que vemos, sino el necesario
        # para mostrar lo que vemos. 
        #
        #  
        PPa1.x= rect.xMinimum();    PPa1.y= rect.yMinimum()   # abajo izquierda
        PPa3.x= rect.xMaximum();    PPa3.y= rect.yMaximum()   # arriba derecha
        PPa2.x=  PPa3.x;            PPa2.y=  PPa1.y           # abajo derecha
        PPa4.x=  PPa1.x;            PPa4.y=  PPa3.y           # arriba izquierda
        if self.sw_l:  # escribir Blue la extension del canvas
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #line_string
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=Blue":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(PPa1.x,2), round(PPa1.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(PPa2.x,2), round(PPa2.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(PPa3.x,2), round(PPa3.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(PPa4.x,2), round(PPa4.y,2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea) 
                
        # Hay que ajustar la ventana girada al canvas
        
        # anchura y altura de la cartografia del canvas en coord mundo
        anchoMundoAzul= (PPa3.x - PPa1.x);    altoMundoAzul=  (PPa3.y - PPa1.y)

        # Proporciones canvas
        w= self.canvas.widthMM();              h= self.canvas.heightMM()
        # ww= self.canvas.width();               hh= self.canvas.height()   # ???




       
        # Calculo de Escalax (Escalay innecesario porque el mapeta es cuadrado)
        # h --> altura del canvas en mm
        # w --> anchura del canvas en mm
        # H --> altura del canvas girado
        # W --> anchura del canvas girado
        # Escalax --> Factor de escala par poder encajar el canvas girado en el "mundo"
        # Escalay --> Concepto analogo al anterior. No lo usare 

        angulo= self.canvas.rotation()
        self.seno_giro= math.sin(math.radians(angulo))
        self.coseno_giro= math.cos(math.radians(angulo))
        self.seno_antigiro= math.sin(math.radians(360 - angulo))
        self.coseno_antigiro= math.cos(math.radians(360 - angulo))   




        if (self.Cuadrante == 1) or (self.Cuadrante == 3): 
            if self.Cuadrante == 1:  
                self.seno_giro_c= math.sin(math.radians(angulo))
                self.coseno_giro_c= math.cos(math.radians(angulo))
            elif (self.Cuadrante == 3): 
                self.seno_giro_c= math.sin(math.radians(angulo-180) )
                self.coseno_giro_c= math.cos(math.radians(angulo-180))          
            h1= (w*self.seno_giro_c)
            h2= (h*self.coseno_giro_c)
            w1= (w*self.coseno_giro_c)
            w2= (h*self.seno_giro_c) 
        elif (self.Cuadrante == 2) or (self.Cuadrante == 4):  
            if self.Cuadrante == 2:  
                self.seno_giro_c= math.sin(math.radians(angulo-90))
                self.coseno_giro_c= math.cos(math.radians(angulo-90))
            elif (self.Cuadrante == 4): 
                self.seno_giro_c= math.sin(math.radians(angulo-270) )
                self.coseno_giro_c= math.cos(math.radians(angulo-270))
            h1= (w*self.coseno_giro_c)
            h2= (h*self.seno_giro_c)
            w1= (h*self.coseno_giro_c)
            w2= (w*self.seno_giro_c)
        
        W = w1 + w2 ;                  H = h1 + h2   
        Escalax= anchoMundoAzul / W;   Escalay= altoMundoAzul /  H 
        if self.sw_l:  #escribir w, h, W, H, Escalax, Escalay, Cuadrante
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= "    'anchoMundoAzul: "+ str(anchoMundoAzul) +"\n";  fbas.write( linea) 
                linea= "    'altoMundoAzul: "+ str(altoMundoAzul) +"\n";  fbas.write( linea) 
                linea= "    'w: "+ str(w) +"\n";  fbas.write( linea) 
                linea= "    'h: "+ str(h) +"\n";  fbas.write( linea) 
                linea= "    'W: "+ str(W) +"\n";  fbas.write( linea) 
                linea= "    'H: "+ str(H) +"\n";  fbas.write( linea) 
                linea= "    'Escalax: "+ str(Escalax) +"\n";  fbas.write( linea) 
                linea= "    'Escalay: "+ str(Escalay) +"\n";  fbas.write( linea)
                linea= "    'Cuadrante: "+ str(self.Cuadrante) +"\n";  fbas.write( linea) 

        # Los puntos Pa son coordendas mundo y representan la ventana que se verá en el mapeta
        # Es un poligo girado la rotation e inscrito en el canvas "aumentado"



        if (self.Cuadrante ==1) or (self.Cuadrante ==3):
            Pa1.x = PPa1.x;                    Pa1.y = PPa1.y + Escalay * h2  
            Pa2.x = PPa4.x + Escalax * w1;     Pa2.y = PPa4.y                  
            Pa3.x = PPa2.x;                    Pa3.y = PPa2.y + Escalay * h1  
            Pa4.x = PPa1.x + Escalax * w2;     Pa4.y = PPa1.y 
        elif (self.Cuadrante ==2)  or (self.Cuadrante ==4):
            Pa1.x = PPa2.x;                    Pa1.y = PPa2.y + Escalay * h1
            Pa2.x = PPa1.x + Escalax * w1;     Pa2.y = PPa1.y             
            Pa3.x = PPa1.x;                    Pa3.y = PPa1.y + Escalay * h2   
            Pa4.x = PPa4.x + Escalax * w2;     Pa4.y = PPa4.y    
     
        if self.sw_l:  #escribir Pa
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=green":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Pa1.x,2), round(Pa1.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Pa2.x,2), round(Pa2.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Pa3.x,2), round(Pa3.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Pa4.x,2), round(Pa4.y,2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea) 
                  
        def distancia(p1,p2):
            return ((p2.x-p1.x)**2+(p2.y-p1.y)**2)**0.5
        ancho_mun= distancia(Pa2, Pa1) 
        self.ancho = ancho_mun /self.Escala
        alto_mun = distancia(Pa3, Pa2) 
        self.alto = alto_mun /self.Escala
    

        if self.sw_l:  #escribir ancho alto ancho_mun alto_mun
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= "    'ancho_mun: "+ str(ancho_mun) +"\n"; fbas.write( linea) 
                linea= "    'alto_mun: "+ str(alto_mun) +"\n"; fbas.write( linea) 
                linea= "    'ancho: "+ str(self.ancho) +"\n"; fbas.write( linea) 
                linea= "    'alto: "+ str(self.alto) +"\n"; fbas.write( linea) 

        #Hay qye calcular como punto medio de caja azul
        PcentAzul= QPoint()
        PcentAzul.x= (PPa3.x + PPa1.x)/2
        PcentAzul.y= (PPa3.y + PPa1.y)/2
        # pasarlo a pantalla....
        xx= ((PcentAzul.x -self.xmin_0)  /self.Escala );  
        yy= ((PcentAzul.y -self.ymin_0) /self.Escala )  
        # y corregir el angulo   
        Par1.x=  ((xx-(self.xTamany/2) ) * self.coseno_antigiro - (yy -(self.xTamany/2) ) * self.seno_antigiro )   + (self.xTamany/2) 
        Par1.y=  ((xx-(self.xTamany/2) ) *  self.seno_antigiro   + (yy -(self.xTamany/2)) * self.coseno_antigiro ) + (self.xTamany/2) 
        # centro ventana
        self.centro_v.setX(Par1.x)
        self.centro_v.setY(Par1.y)



        # La caja roja la construyo basandome en el centro de la ventana
        Par1.x= self.centro_v.x() - self.ancho/2;      Par1.y= self.centro_v.y() + self.alto/2
        Par2.x= self.centro_v.x() + self.ancho/2;      Par2.y= self.centro_v.y() + self.alto/2
        Par3.x= self.centro_v.x() + self.ancho/2;      Par3.y= self.centro_v.y() - self.alto/2
        Par4.x= self.centro_v.x() - self.ancho/2;      Par4.y= self.centro_v.y() - self.alto/2

        if self.sw_l:  #escribir Par
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=Red":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Par1.x,2), round(Par1.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Par2.x,2), round(Par2.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Par3.x,2), round(Par3.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Par4.x,2), round(Par4.y,2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea)  
            # linea= 'End Sub';  fbas.write( linea)     
        # xmin, ymin, xmax, ymax para que las vea el paintEvent
        xMin = min(Par1.x,Par2.x,Par3.x,Par4.x);   yMin = min(Par1.y,Par2.y,Par3.y,Par4.y)
        xMax = max(Par1.x,Par2.x,Par3.x,Par4.x);   yMax = max(Par1.y,Par2.y,Par3.y,Par4.y)   
        self.begin = QPoint(xMin,yMin);            self.end = QPoint(xMax,yMax) 
        
        if self.sw_l:
            now = datetime.now() # current date and time
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= "    'NOW: "+ str(date_time) +"\n"; fbas.write( linea)  
            
        self.repaint()   # Fuerzo el paintEvent   

    def paintEvent(self, event): 
        """
        pinto en mapeta rectangulo y cruz.\n
        En esta version, con el mapeta circular, solo se dibuja los trozos de rectangulo y cruz 
        interiores al circulo
        """

        rect=self.canvas.extent()
        
        # Auxiliar: Pinta cruz en centro de canvas para facilitar comprobaciones y el texto "centro"
        if self.pintoCentro:
            pen= QPen(Qt.black);              pen.setWidth(1);         pen.setStyle(Qt.SolidLine)
            painter = QPainter(self);         painter.setPen(pen)
            centro_x= self.canvas.width()/2;  centro_y= self.canvas.height()/2
            painter.drawLine(centro_x-20, centro_y, centro_x+20, centro_y)
            painter.drawLine(centro_x, centro_y-20, centro_x, centro_y+20)
            rect= QRect(centro_x-20, centro_y-20, 40, 20)
            painter.drawText(rect, Qt.AlignCenter, "centro") 
            painter.end() 

        #region QPainter... Como dibujaremos...
        qp = QPainter(self)
        #br = QBrush(QColor(50, 110, 90, 70))  
        br = QBrush(QvConstants.COLORCLARSEMITRANS) #Color de fons del quadrat
        qp.setBrush(br)  

        # pen= QPen(QvConstants.COLORFOSC,  1, Qt.SolidLine)
        pen= QPen(QColor(255,98,1),  1, Qt.SolidLine)
        qp.setPen(pen)
        # pen=QPen(QvConstants.COLORFOSC)
        #endregion QPainter... Como dibujaremos...
        
        # capturo coordenadas:
        # vamos a manejar begin_ y end_
        # Se cargan en base a self.begin y self.end que se cargan en:
        # mousePressEvent y se modifican en....Aqui 
        begin_ = QPoint();           end_ =  QPoint()
        begin_.x= self.begin.x();    end_.x= self.end.x()
        # Si se llega aqui despues de hacer una ventana sobre el mapeta
        #    se pone el origen de coordenadas en la esquina inferior izquierda del mapeta
        # Caso contrario no se hace
        if self.MouseMoveFlag== False:
            begin_.y= self.yTamany-self.begin.y()
            end_.y=   self.yTamany- self.end.y()
        else:
            begin_.y= self.begin.y()
            end_.y= self.end.y()
        
        self.MouseMoveFlag= False

        # Pinto el rectangulo como 4 segmentos recortados si es necesario NUEVO
        radio= self.xTamany/2
        centro=QPoint(self.xTamany/2,self.yTamany/2)  

        # 
        P_xmin_ymin=  QPoint(begin_.x, end_.y)
        P_xmax_ymin=  QPoint(end_.x,   end_.y)
        P_xmax_ymax=  QPoint(end_.x,   begin_.y)
        P_xmin_ymax=  QPoint(begin_.x, begin_.y)  


        # Pinto ventana cartografia con 4 lineas
        try:   # lado HORIZONTAL ARRIBA NUEVO --> ok
            PR_xmin_ymin,PR_xmax_ymin,caso,pintar = self.SegmentoDeRangoEnCirculo(P_xmin_ymin,P_xmax_ymin,centro,radio)
            if pintar:  qp.drawLine(QLineF( PR_xmin_ymin,PR_xmax_ymin ))
        except:
            pass
        try:  # lado HORIZONTAL ABAJO NUEVO --> ok
            PR_xmin_ymax,PR_xmax_ymax,caso,pintar = self.SegmentoDeRangoEnCirculo(P_xmin_ymax,P_xmax_ymax,centro,radio)
            if pintar:  qp.drawLine(QLineF( PR_xmin_ymax,PR_xmax_ymax ))
        except :
            pass
        try:  # lado VERTICAL IZQUIERDO NUEVO --> ok
            PR_xmin_ymin,PR_xmin_ymax,caso,pintar = self.SegmentoDeRangoEnCirculo(P_xmin_ymin,P_xmin_ymax,centro,radio)
            if pintar:  qp.drawLine(QLineF( PR_xmin_ymin,PR_xmin_ymax ))
        except :
            pass
        try:  # lado VERTICAL DERECHO  NUEVO --> ok
            PR_xmax_ymin,PR_xmax_ymax,caso,pintar = self.SegmentoDeRangoEnCirculo(P_xmax_ymin,P_xmax_ymax,centro,radio)
            if pintar:  qp.drawLine(QLineF( PR_xmax_ymin,PR_xmax_ymax ))
        except :
            pass

        #region cuarentena Pinto cruz  ORIGINAL' )
       
            # qp.drawLine(QLineF( QPoint( begin_.x +(end_.x-begin_.x)/2, 0),  QPoint( begin_.x +(end_.x-begin_.x)/2,self.yTamany)  ))
            # qp.drawLine(QLineF( QPoint( 0, begin_.y +(end_.y-begin_.y)/2),  QPoint( self.xTamany,begin_.y +(end_.y-begin_.y)/2 )  ))
            ## Pinto rectangulo')
            # qp.drawRect(begin_.x,begin_.y,end_.x-begin_.x,end_.y-begin_.y)
        #endregion NOOOOO Pinto cruz  ORIGINAL' )

        #region Pinto CRUZ RECORTADA por el circulo NUEVO --> ok')
        try:
            P1=  QPoint(begin_.x +(end_.x-begin_.x)/2, 0)
            P2=  QPoint(begin_.x +(end_.x-begin_.x)/2,self.yTamany)
            P3=  QPoint(0, begin_.y +(end_.y-begin_.y)/2)
            P4=  QPoint(self.xTamany,begin_.y +(end_.y-begin_.y)/2)

            # Calculo interseccion de linea horizontal con circulo (P1 arriba P2 abajo)
            P1R, P2R=  self.SegmentoEnCirculo(P1,P2,centro,radio)
            # Calculo interseccion de linea vertical con circulo (P3 izquierda P4 derecha)
            P3R, P4R=  self.SegmentoEnCirculo(P3,P4,centro,radio)
            # dibujo ambas lineas
            qp.drawLine(QLineF( P1R,  P2R ))
            qp.drawLine(QLineF( P3R,  P4R ))
        except :
            pass
        #endregion Pinto CRUZ RECORTADA por el circulo NUEVO --> ok')

        qp.end()

        #region cuarentena
        # out_img = QImage(self.xTamany, self.yTamany, QImage.Format_ARGB32)
        # # out_img.fill(Qt.transparent)
        # out_img.fill(Qt.white)

        # # Create a texture brush and paint a circle with the original image onto
        # # the output image: Chapeau!!
        # brush = QBrush()        # Create texture brush
        # qp = QPainter(out_img)  # Paint the output image
        # qp.setBrush(brush)      # Use the image texture brush

        # qp.setPen(Qt.NoPen)
        # qp.setRenderHint(QPainter.Antialiasing, True)  # Use AA
        # qp.drawEllipse(0, 0, self.xTamany, self.yTamany)  # Actually draw the circle
        #endregion cuarentena
    def mousePressEvent(self, event):
        """
        Presion de un boton del raton cuando el cursor está sobre el mapeta\n
        Guarda coordenadas de punto del mapeta
        """
        self.begin = event.pos()
        self.end = event.pos()
        self.MousePressFlag=True
        rect = self.canvas.extent()
    def enterEvent(self, event):
        self.setCursor(QCursor(QPixmap(imatgesDir+'cruz.cur')))    
    def mouseMoveEvent(self, event):
        """
        Presion de un boton del raton mantenida y movimiento sobre el mapeta
        """
        if self.MousePressFlag== True:        
            self.end = event.pos()
            self.MouseMoveFlag= True
            self.canvas.update()
        else:
            pass
            # print("He pasado por aqui_01")
    def mouseReleaseEvent(self, event):
        """
        Dejamos de hacer presion sobre un boton del raton mientras está sobre mapeta\n

        Aqui se puede llegar haciendo una ventana sobre el mapeta 0 o sobre el mapeta 44
        Si es sobre el mapeta 0, las coordenadas se pueden buscar la correspondencia de esas coordenadas 
        con el mundo.\n
        Si el mapeta esta girado, lo que hare sera buscar la correspondencia de las coordenadas de 
        este mapeta con el mapeta no girado.\n 
        Para ello habra que girarlas 44.5 grados y restarles el desplazamiento
        """
        #region declaracion variables
        Paux1=QPoint() #  Pto arriba izquierda
        Paux2=QPoint() #  Pto arriba derecha
        Paux3=QPoint() #  Pto abajo derecha
        Paux4=QPoint() #  Pto abajo izquierda
        #endregion
        
        self.end = event.pos()
        self.MousePressFlag=False

        ## Cambio origen de coordenadas "Y" poniendolo abajo-izquierda. Acorde con sistema del Mapa')
        self.xIn = self.begin.x();      self.yIn = self.yTamany - self.begin.y()   
        self.xFi = self.end.x();        self.yFi = self.yTamany - self.end.y()
        self.centro_v.setX((self.xFi-self.xIn)/2 + self.xIn)
        self.centro_v.setY((self.yFi-self.yIn)/2 + self.yIn)
        if self.sw_l:  #escribir  caja xIn,yIn a xFi,yFi
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
                linea= '    MbeSendKeyin "pla block":    MbeSendKeyin "co=Red":    MbeSendKeyin "lc=2":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn,2), round(self.yIn,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xFi,2), round(self.yFi,2)); fbas.write( linea)
        # Convierto las coordenadas del mapeta girado 44 a coordenadas de mapeta no girado para buscar la utm')
 
        #  En el mapeta (girado o no) he señalado una ventana. Calculo su tamaño
        # Calculo la la ventana mundo "girado" correspondiente a los puntos del mapeta
        distXma=  (self.xFi - self.xIn)   # ancho mapeta
        distX= distXma * self.Escala      # ancho mundo
        distYma=  (self.yFi - self.yIn)   # alto mapeta
        distY= distYma * self.Escala      # alto mundo 

        # giro 44.5 (contra reloj)
        # ...Giro el punto inicial
        self.xIn_=  ((self.xIn -(self.xTamany/2)) * self.coseno_giro     - (self.yIn -(self.xTamany/2) ) * self.seno_giro )   + (self.xTamany/2) 
        self.yIn_=  ((self.xIn -(self.xTamany/2)) * self.seno_giro       + (self.yIn -(self.xTamany/2) ) * self.coseno_giro )  + (self.xTamany/2) 
        if self.sw_l:  #escribir xIn,yIn, xIn_,yIn y linea que los une
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #point
                linea= '    MbeSendKeyin "pla point":    MbeSendKeyin "co=210":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=20"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn,2), round(self.yIn,2)); fbas.write( linea)
                
                linea= '    MbeSendKeyin "pla point":    MbeSendKeyin "co=Green":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=16"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn_,2), round(self.yIn_,2)); fbas.write( linea)                
                linea= '    MbeSendReset\n';  fbas.write( linea)   
                
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=210":    MbeSendKeyin "lc=3":    MbeSendKeyin "wt=1"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn,2), round(self.yIn,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn_,2), round(self.yIn_,2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea) 

        # añado el desplazamiento
        self.xIn= self.xIn_;       self.yIn= self.yIn_ 

        ## en este punto las coordenadas mapeta que manejo estan referidas al mapeta 0')
        ## Convertimos las coordenadas del punto inicial del mapeta_ang=0 a coordenadas Mundo')
        # Miraremos la proporcion de las coordenadas xy sobre el mapeta y lo multiplicaremos por la escala y 
        # se lo sumaremos a la coordenada del origen...'''
        punt1 = self.conversioPantallaMapa([self.xIn, self.yIn])
        if self.sw_l:  #escribir linea xInYin  punt1 y punt1
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #point
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=1":    MbeSendKeyin "lc=3":    MbeSendKeyin "wt=1"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(self.xIn,2), round(self.yIn,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(punt1[0],2), round(punt1[1],2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea) 
                linea= '    MbeSendKeyin "pla point":    MbeSendKeyin "co=35":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=20"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(punt1[0],2), round(punt1[1],2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea)           
        
        # coordenadas mundo de los 4 puntos señalados en el mapeta. Traslado el rectangulo del mapeta al mundo')
        Paux1.x= punt1[0];                              Paux1.y= punt1[1]
        Paux2.x= Paux1.x + (distX * self.coseno_giro);  Paux2.y= Paux1.y + (distX * self.seno_giro)
        Paux3.x= Paux2.x - (distY * self.seno_giro);    Paux3.y= Paux2.y + (distY * self.coseno_giro)
        Paux4.x= Paux1.x - (distY * self.seno_giro);    Paux4.y= Paux1.y + (distY * self.coseno_giro)
        if self.sw_l:  #escribir Paux
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #line_string
                linea= '    MbeSendKeyin "pla ls":    MbeSendKeyin "co=Violet":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Paux1.x,2), round(Paux1.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Paux2.x,2), round(Paux2.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Paux3.x,2), round(Paux3.y,2)); fbas.write( linea)
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(Paux4.x,2), round(Paux4.y,2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea) 
        
        self.w3= ((Paux2.x-Paux1.x)**2+(Paux2.y-Paux1.y)**2)**0.5
        self.h3= ((Paux3.x-Paux2.x)**2+(Paux3.y-Paux2.y)**2)**0.5

        ## Calculo rango de esa caja girada, (minima, caja que la engloba) para pasarle unas coordenadas al canvas que engloben la caja. Esto solo seria necesario en el caso de rotacion')
        punt1[0]= min(Paux1.x, Paux2.x, Paux3.x,Paux4.x)    #xmin
        punt1[1]= min(Paux1.y, Paux2.y, Paux3.y,Paux4.y)    #ymin
        if self.sw_l:  #escribir punt1
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #point
                linea= '    MbeSendKeyin "pla point":    MbeSendKeyin "co=Yellow":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=20"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(punt1[0],2), round(punt1[1],2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea)          
        punt2=[]
        punt2.append(max(Paux1.x, Paux2.x, Paux3.x,Paux4.x)) #xmax
        punt2.append(max(Paux1.y, Paux2.y, Paux3.y,Paux4.y)) #ymax

        self.l1= punt2[0]-punt1[0]
        self.l2= punt2[1]-punt1[1]
        if self.sw_l:  #escribir punt2
            with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #point
                linea= '    MbeSendKeyin "pla point":    MbeSendKeyin "co=30":    MbeSendKeyin "lc=0":    MbeSendKeyin "wt=20"\n';  fbas.write( linea) 
                linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(punt2[0],2), round(punt2[1],2)); fbas.write( linea)
                linea= '    MbeSendReset\n';  fbas.write( linea)           

        ## Pasamos rango al canvas para que lo represente')
        # Necesitare tener estas coordenadas como QgsRectangle...
        rang = QgsRectangle(punt1[0], punt1[1], punt2[0], punt2[1])
        # if self.sw_l:
        #     with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:
        #         linea= '    MbeSendKeyin "pla block":    MbeSendKeyin "co=Red":    MbeSendKeyin "lc=2":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rang.xMinimum(),2), round(rang.yMinimum(),2)); fbas.write( linea)
        #         linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rang.xMaximum(),2), round(rang.yMaximum(),2)); fbas.write( linea)

        self.canvas.setExtent(rang)
        self.canvas.refresh()
        
        rect = self.canvas.extent()
        # if self.sw_l:
        #     with open('D:/qVista/Codi/guies/DocModuls/QvMapeta/cm.bas', 'a') as fbas:  #block
        #         # linea= '    MbeSendKeyin "pla block":    MbeSendKeyin "co=Red":    MbeSendKeyin "lc=2":    MbeSendKeyin "wt=2"\n';  fbas.write( linea) 
        #         # linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect.xMinimum(),2), round(rect.yMinimum(),2)); fbas.write( linea)
        #         # linea= "    pt.x =  {} :pt.y =  {} :  MbeSendDatapoint pt\n".format(round(rect.xMaximum(),2), round(rect.yMaximum(),2)); fbas.write( linea)
      

 


import math

if __name__ == "__main__":
       
    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
     
        # Canvas, projecte i bridge
        start1 = time.time()
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
            qvMapeta = QvMapeta(canvas, r"mapesOffline/default.png", pare=canvas)
            qvMapeta.show()
            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")
