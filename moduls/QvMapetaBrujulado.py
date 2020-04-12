from qgis.core import QgsRectangle
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit, QApplication, QHBoxLayout
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QSize

import sys
import os
from moduls.QvImports  import *
from moduls.QvDropFiles import QvDropFiles
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvCompass_2 import QvCompass
from moduls.QvMapeta import QvMapeta
from configuracioQvista import *
from PyQt5.QtWidgets import QFrame, QSpinBox, QLineEdit
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygon
import numpy as np


class QvMapetaBrujulado(QFrame):
    def __init__(self,ficheroMapeta,  canvas,  pare = None):
        QFrame.__init__(self)
        self.canvas=canvas
        self.setParent(pare)
        self.pare= pare

        
        self.setDropable()
        self.ficheroMapeta = ficheroMapeta
        # leer info del mapeta
        datos_mapeta = self.CalcularPNGyRangoMapeta(ficheroMapeta)
        # inicialmente ancho (y alto)
        ancho_mapeta = datos_mapeta[5]
        self.radio = ancho_mapeta
        # print("ancho_mapeta", ancho_mapeta)

        # calcular el margen
        self.margen= ancho_mapeta/7
        ancho_mapetaBrujulado = ancho_mapeta + self.margen*2

        # dimensionar mapeta brujulado a ancho+margen
        self.setGeometry(0,0,ancho_mapetaBrujulado,ancho_mapetaBrujulado)
        self.setMinimumSize(QSize(ancho_mapetaBrujulado, ancho_mapetaBrujulado))
        self.setMaximumSize(QSize(ancho_mapetaBrujulado, ancho_mapetaBrujulado))

        self.setWindowTitle('MapetaBrujulado')
        

        # dimensionar compass a ancho+margen
        # self.qvCompass = Compass(self.qvMapeta) 
        # self.qvCompass = QvCompass(self.canvas,  pare=self.qvMapeta)
        self.qvCompass = QvCompass(self.canvas,self)
        self.qvCompass.setGeometry(0, 0, ancho_mapetaBrujulado, ancho_mapetaBrujulado)
        self.qvCompass.show()


        # dimensionar mapeta a ancho
        # self.qvMapeta = Mapeta(self)   
        # self.qvMapeta.setGeometry(0, 0, ancho_mapeta, ancho_mapeta)
        # self.qvMapeta.show()

        self.qvMapeta = QvMapeta(self.canvas, ficheroMapeta, pare=self.qvCompass)
        self.qvMapeta.show()           

        # relaciono mapeta y compas. Mapeta dentro de compass
        self.lContenidoCompass = QHBoxLayout ()
        self.lContenidoCompass.setContentsMargins(self.margen, self.margen, self.margen, self.margen)
        self.lContenidoCompass.addWidget(self.qvMapeta)
        try:
            self.qvCompass.setLayout(self.lContenidoCompass)
        except Exception as ee:
            pass
            # print(str(ee))
        

        #relaciono compass mapeta brujulado. Compass dentro mapetaBrujulado
        self.lcontenidoMapetaBrujulado = QHBoxLayout ()
        self.lcontenidoMapetaBrujulado.setContentsMargins( 0, 0, 0,0)
        self.lcontenidoMapetaBrujulado.addWidget(self.qvCompass)
        self.setLayout(self.lcontenidoMapetaBrujulado)

        # Desde clase contenedora hago que 
        self.qvMapeta.dadoPNT.connect(self.EnviarPNTCompass)
        # if the signal has the data as argument:
        # self.qvMapeta.dadoPNT.connect(self.qvCompass.gestionoPnt)
    
    def PngPgwDroped_MB(self,ficheroMapeta):
        '''
        Recibe un fichero soltado y lo manda a funcion para calcular el
        nombre del mapeta y su rango
        '''
        # print("PngPgwDroped_MB")

        ficheroEnviado= ficheroMapeta[0]
        datos_mapeta= self.CalcularPNGyRangoMapeta(ficheroEnviado)
        self.PngMapeta= datos_mapeta[0]
        self.xmin_0=    datos_mapeta[1]
        self.ymin_0=    datos_mapeta[2]
        self.xmax_0=    datos_mapeta[3]
        self.ymax_0=    datos_mapeta[4]
        self.xTamany = datos_mapeta[5]  
        ancho_mapeta = datos_mapeta[5]    
        self.yTamany = datos_mapeta[6]   

        # print("ancho_mapeta", ancho_mapeta)

        # calcular el margen
        self.margen= ancho_mapeta/7
        ancho_mapetaBrujulado = ancho_mapeta + self.margen*2

        # dimensionar mapeta brujulado a ancho+margen
        self.setGeometry(0,0,ancho_mapetaBrujulado,ancho_mapetaBrujulado)
        self.setMinimumSize(QSize(ancho_mapetaBrujulado, ancho_mapetaBrujulado))
        self.setMaximumSize(QSize(ancho_mapetaBrujulado, ancho_mapetaBrujulado))


        # pasar parametros a  Compas
        self.qvMapeta.PngPgwDroped([ficheroEnviado])
        # pasar parametros a  Compas
        self.qvCompass.setGeometry(0, 0, ancho_mapetaBrujulado, ancho_mapetaBrujulado)
        self.lContenidoCompass.setContentsMargins(self.margen,self.margen,self.margen,self.margen)
          
        linea= "FicMB: "+ str(datos_mapeta[0]) +'\n'
        linea= linea + 'xmin:  '+ str(round(datos_mapeta[1],2)) +'\n'
        linea= linea + 'ymin:  '+ str(round(datos_mapeta[2],2)) +'\n'
        linea= linea + 'xmax:  '+ str(round(datos_mapeta[3],2)) +'\n'
        linea= linea + 'ymax:  '+ str(round(datos_mapeta[4],2)) +'\n'
        linea= linea + 'W:  '+ str(datos_mapeta[5]) +'\n'
        linea= linea + 'H:  '+ str(datos_mapeta[6])
        self.setToolTip(linea)

   
    def setDropable(self):
        '''
         Implementacion Drop ficheros png y pgw sobre el mapeta. 
         Mapeta será capaz de recibir PNG o PGW para recargar su imagen
        '''
        self.setAcceptDrops(True)
        drop = QvDropFiles(self)
        drop.llistesExts(['.png', '.pgw'])
        drop.arxiusPerProcessar.connect(self.PngPgwDroped_MB)
    #endregion
        
    #region Funciones relacionadas con el dibujo de la cruz y ventanaMapeta
  
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

    def EnviarPNTCompass(self):
        # fuerzo funcion de una clase compass con parametro de clase mapeta
        try:
            self.qvCompass.gestionoPnt(self.qvMapeta.the_data)
        except :
            pass
        




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
        projecteInicial='D:/qVista/Codi/mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

            qvMapetaBrujado = QvMapetaBrujulado("mapesOffline/default.png", canvas,  pare=canvas)
            qvMapetaBrujado.show()            

            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")
     
