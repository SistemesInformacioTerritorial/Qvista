# https://doc.qt.io/qt-5/qwidget.html#grab
# https://steakrecords.com/es/672213-drag-and-drop-qlabels-with-pyqt5-python-python-3x-drag-and-drop-pyqt-pyqt5.html

import configuracioQvista
import math
import os.path
from qgis.PyQt.QtGui import QPixmap
from qgis.core import QgsRectangle,   QgsProject, QgsPointXY, QgsGeometry
from qgis.PyQt.QtCore import QUrl
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core.contextmanagers import qgisapp
from PyQt5.QtCore import QModelIndex, Qt, QRect, QPoint, QTimer, QSize, QObject,\
     pyqtSignal, QEvent, pyqtSlot

from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDockWidget, QTreeView,\
    QAction, QVBoxLayout, QGridLayout, QSplitter
from PyQt5.QtWidgets import  QHBoxLayout ,QAbstractItemView, QLabel, QWidget, QLineEdit,\
     QPushButton, QSpinBox, QFileDialog, QSpacerItem, QSizePolicy, QColorDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QImage, QBrush
from moduls.QvPushButton import QvPushButton


projecteInicial='mapesOffline/qVista default map.qgs'



class QvColocacionCirculo(QgsMapTool):
    """ Dibuixa un cercle i selecciona els elements."""
    def __init__(self, canvas,   numeroSegmentsCercle, parent,lado):
        '''
        '''
        self.canvas = canvas
        self.parent= parent
        self.lado= lado
        self.tempdir=configuracioQvista.tempdir
       
        
        QgsMapTool.__init__(self, self.canvas)

        # clickable(self).connect(self.showText1)
        self.status = 0
        self.numeroSegmentsCercle = numeroSegmentsCercle

        self.rubberband=QgsRubberBand(self.canvas)
        self.rubberband.setColor( QColor("Blue") )
        self.rubberband.setWidth(1)
        self.rubberband.setIconSize(10)
        # self.overlap = False
        # self.radio  =0

    def canvasPressEvent(self,e):
        '''
        Data en canvas. Segun boton iz o derecho se que es modo win o no....
        Guardo el centro
        '''
        if self.canvas.rotation() != 0:
            self.canvas.setRotation(0)

        # self.parent.label.setPixmap(QPixmap())
        try:
            self.rubberband.reset(True)
        except:
            pass  

        self.status = 1   #Estamos pintando circulo!!
        # self.centre  centro del circulo
        self.centre = self.toMapCoordinates(e.pos())
        self.centroEnPantalla= e.pos()
        return
    def canvasMoveEvent(self,e):
        '''
          Hay que pintar dinamicamente el circulo
        '''        
        if self.status == 0:  # si no estoy en modo pintar circulo, no continuo
            return

        # guardo punto pantalla
        self.final=e.pos()
        # punto pantalla a mundo
        cp = self.toMapCoordinates(e.pos())

        # establezco color de rubberband
        self.rubberband.setColor(QColor("blue"))

        # dibujo el circulo
        self.rbcircle(self.rubberband, self.centre, cp, self.numeroSegmentsCercle)
        # r = math.sqrt(self.centre.sqrDist(cp))
    def rbcircle(self, rb,center,edgePoint,segments):
        '''
        Calculo circulo y lo cargo en rubberband
        '''
        rd = math.sqrt(center.sqrDist(edgePoint))
        self.radio = rd

        rb.reset(True )
        pi =3.1416
        llistaPunts=[]
        theta = 1*(2.0 * pi/segments)
        rb.addPoint(QgsPointXY(center.x()+1*math.cos(theta), center.y()+1*math.sin(theta)))
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            rb.addPoint(QgsPointXY(center.x()+rd*math.cos(theta),center.y()+rd*math.sin(theta)))
    def pre_saveCanvas(self):
        self.canvas.mapCanvasRefreshed.disconnect(self.pre_saveCanvas)
        QTimer.singleShot(0, self.saveCanvas)
    def saveCanvas(self):
        fic_tmp=os.path.join(self.tempdir,"temporal.png")
        self.canvas.saveAsImage(fic_tmp) 
        self.hacer4()
    def saveCanvas1(self):
        fic_tmp=os.path.join(self.tempdir,"temporal.png")
        self.canvas.saveAsImage(fic_tmp) 
        self.hacer4()
    def hacer4(self):  

        fic_tmp=os.path.join(self.tempdir,"temporal.png")    
        self.pixmap = QPixmap(fic_tmp)  
        # self.pixmap=self.canvas.grab() # no acaba de ir bien, me carga en pixmap tambien el circulo pintado
        # tamaño del pixmap
        hp= self.pixmap.height()                                         # alto imagen 
        wp= self.pixmap.width()                                          # ancho imagen salvada
        # radio. 
        if hp < wp:
            self.rP= hp/2
        else:
            self.rP= wp/2

        self.xcP = wp/2
        self.ycP = hp/2
        # self.rP = math.sqrt(math.pow((self.xcP-self.xrP), 2) + math.pow((self.ycP-self.yrP), 2))  # radio pantalla
        pcX= self.xcP - self.rP ; pcY= self.ycP - self.rP                                    # punto inicio crop
        self.an= 2* self.rP;      self.al= self.an                            # an, ancho para crop   al, alto para crop
        escala= self.rP /self.rM                                                   # escala, como relacion de radiopantalla a radiomundo
        pmin= QPoint();   pmin.setX(pcX); pmin.setY(pcY+self.al);       self.Pmin = self.toMapCoordinates(pmin)
        pmax= QPoint();   pmax.setX(pcX+self.an); pmax.setY(pcY);       self.Pmax = self.toMapCoordinates(pmax)        

        # calculo area de recorte para hacer el crop 
        rect= QRect(pcX, pcY, self.an, self.al)
        # hago crop
        cropped_pixmap = self.pixmap.copy(rect) 
        
        # escalo el pixmap al tamaño que quiero
        self.scaled_pixmap = cropped_pixmap.scaled(self.parent.lado, self.parent.lado, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # de pixmap a image
        image=QImage(self.scaled_pixmap.toImage())
        image = image.convertToFormat(QImage.Format_ARGB32)

        # preparo imagen de salida transparente y del tamaño del de entrada....
        out_img = QImage(image.width(), image.width(), QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        # Create a texture brush and paint a circle with the original image onto
        # the output image: Chapeau!!

        # pintamos circulo relleno de imagen
        painter = QPainter(out_img)  # Paint the output image
        brush = QBrush(image)        # Create texture brush
        painter.setBrush(brush)      # Use the image texture brush  (como se pintara el relleno)
        pen= QPen(self.parent.color,  1, Qt.SolidLine)    #qVista claro         
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
        painter.drawEllipse(0, 0, image.width(), image.width())  # Actually draw the circle
        painter.end()                # We are done (segfault if you forget this)







        # de out_img a pixmap
        self.scaled_pixmap = QPixmap.fromImage(out_img)

        # muestro ese pixmap en label...
        self.parent.label.setPixmap(self.scaled_pixmap)

        # y lo salvo como temporal2
        fic_tmp=os.path.join(self.tempdir,"temporal2.png")  
        self.fileName= fic_tmp 

        if self.fileName:
            # Guardo el pixmap como png
            self.scaled_pixmap.save(self.fileName)
            # Calculo info para el PQW
            # rango mundo x e y
            xdist = self.Pmax.x()- self.Pmin.x()   
            ydist = self.Pmax.y()- self.Pmin.y() 

            # ancho y alto de la imagen
            iheight = self.scaled_pixmap.height() 
            iwidth =  self.scaled_pixmap.width()  

            # Preparo nombre del PGW
            split_nombre=os.path.splitext(self.fileName)
            filenamePgw=split_nombre[0]+".pgw"

            # Escribo PGW
            wld =open(filenamePgw, "w")   
            wld.writelines("%s\n" % (xdist/iwidth))
            wld.writelines("0.0\n")
            wld.writelines("0.0\n")
            wld.writelines("%s\n" % (ydist/iheight))
            wld.writelines("%s\n" % self.Pmin.x())
            wld.writelines("%s\n" % self.Pmin.y())
            wld.close


        #  muestro datos de georeferenciacion
        literal= "xmin,ymin=" + str(round(self.Pmin.x(),3)) +"  "+ str(round(self.Pmin.y(),3))
        self.parent.xmin_ymin.setText(literal)
        literal= "xmax,ymax=" + str(round(self.Pmax.x(),3)) +"  "+ str(round(self.Pmax.y(),3))
        self.parent.xmax_ymax.setText(literal)

 
        try:
            self.reset()
        except:
            pass       
     
    
    
    def canvasReleaseEvent(self,e):
        '''
        Damos por dibujado el circulo al dejar de presionar el boton
        '''
        if self.status == 0:
            return

        # Calculo datos para el recorte
        self.xcM= self.centre.x();             self.ycM= self.centre.y()           # Punto centro circulo Mundo
        self.xcP= self.centroEnPantalla.x();   self.ycP= self.centroEnPantalla.y() # Punto centro circulo Pantalla
        self.xrP= self.final.x();              self.yrP= self.final.y()            # Punto radio Pantalla
        self.rM= self.radio   

        # Calculo rango del circulo
        xmin= self.xcM - self.rM; ymin= self.ycM - self.rM
        xmax= self.xcM + self.rM; ymax= self.ycM + self.rM

        # Se lo paso al canvas para hacer zoom a esa zona
        self.rang = QgsRectangle(xmin, ymin, xmax, ymax)

        self.canvas.mapCanvasRefreshed.connect(self.pre_saveCanvas)
        self.canvas.setExtent(self.rang)
        self.canvas.refresh()
    def reset(self):
        '''
        '''
        self.status = 0
        self.rb.reset( True )
    def deactivate(self):
        '''
        '''
        pass
        # self.emit(SIGNAL("deactivated()"))




class QvCrearMapetaConBotones(QWidget):
    '''
    Pongo botones para:\n
      Poner un circulo con ruberband\n
      Guardar la ruberband
    '''

    Sig_MapetaTemporal = pyqtSignal('QString ')
    def __init__(self, canvas,pare=None):
        '''
        '''
        self.canvas=canvas
        if self.canvas.rotation() != 0:
            self.canvas.setRotation(0)

        QWidget.__init__(self)
        self.dadesdir=configuracioQvista.dadesdir
        self.setParent(pare)
        self.pare = pare
        self.existeCirculo=False  

        #defino botones y las funciones de su click
        self.botoponerCirculo = QPushButton("Posar circle")
        self.botoponerCirculo.setToolTip('Color perimetre')
        self.botoponerCirculo.clicked.connect(self.ponerCirculo)
        self.botoponerCirculo.setFixedWidth(120) 

        self.botoEnvMap = QPushButton('Enviar a mapeta')
        self.botoEnvMap.setToolTip('Color perimetre')
        self.botoEnvMap.clicked.connect(self.EnvMap)   
        self.botoEnvMap.setFixedWidth(120)      

        self.botoActualizar = QPushButton("Actualizar")
        self.botoEnvMap.setToolTip('Color perimetre')
        self.botoActualizar.clicked.connect(self.actualizar)
        self.botoActualizar.setFixedWidth(120) 

        self.botoColor = QPushButton('Sel·lecc. color')
        self.botoColor.setToolTip('Color perimetre')
        self.botoColor.clicked.connect(self.showDialogColor)
        self.botoColor.setFixedWidth(120) 

        self.botoCargar =  QPushButton('Cargar')  
        self.botoCargar.setToolTip('Color perimetre')
        self.botoCargar.clicked.connect(self.Cargar)
        self.botoCargar.setFixedWidth(120) 

        self.botoSalvar =  QPushButton('Salvar')  
        self.botoSalvar.setToolTip('Color perimetre')
        self.botoSalvar.clicked.connect(self.Salvar)   
        self.botoSalvar.setFixedWidth(120)    


        self.label = QLabel(self)  #para el pixmap
        
        # self.label.setDragEnabled(True)      no va!!!
        

        self.color= QColor(121,144,155)
        self.xmax_ymax = QLabel(" ",self)
        self.xmin_ymin = QLabel(" ",self)



        self.spinBox = QSpinBox(self)
        self.spinBox.setFixedWidth(60)
        self.spinBox.setRange(50, 600)
        self.spinBox.setSingleStep(20)
        self.spinBox.setValue(200)
        self.lado=self.spinBox.value()
        self.spinBox.valueChanged.connect(self.tamanyoLadoCirculo)

        spacerItem = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layH1=QHBoxLayout()
        self.layH1.addWidget(self.botoponerCirculo)
        
        self.layH1.addWidget(self.botoEnvMap)

        self.layH1.addItem(spacerItem)

        self.layH2=QHBoxLayout()
        self.layH2.addWidget(self.botoActualizar)
        self.layH2.addWidget(self.botoColor) 
        self.layH2.addItem(spacerItem)  

        self.layH3=QHBoxLayout()
        self.layH3.addWidget(self.botoCargar)
        self.layH3.addWidget(self.botoSalvar) 
        self.layH3.addItem(spacerItem)  

        
        self.layH4=QHBoxLayout()
        self.layH4.addWidget(self.xmax_ymax)
        self.layH4.addItem(spacerItem) 

        self.layH5=QHBoxLayout()
        self.layH5.addWidget(self.xmin_ymin)
        self.layH5.addItem(spacerItem)      


        self.layH6=QHBoxLayout()
        self.layH6.addWidget(self.spinBox)
        self.layH6.addItem(spacerItem) 

        self.layH7=QHBoxLayout()
        self.layH7.addWidget(self.label)
        self.layH7.addItem(spacerItem)      

        spacerItem2 = QSpacerItem(0,0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.layV1=QVBoxLayout()
        self.layV1.addLayout(self.layH1) 
        self.layV1.addLayout(self.layH2) 
        self.layV1.addLayout(self.layH3) 
        self.layV1.addLayout(self.layH4) 
        self.layV1.addLayout(self.layH5) 
        self.layV1.addLayout(self.layH6) 
        self.layV1.addItem(spacerItem2)
        self.layV1.addLayout(self.layH7) 
        self.setLayout(self.layV1)



    def EnvMap(self):

        try:
            self.Sig_MapetaTemporal.emit(self.colocoCirculo.fileName)
        except Exception as ee:
            self.actualizar()
            fic_tmp=os.path.join(self.tempdir,"temporal2.png")  
            self.Sig_MapetaTemporal.emit(fic_tmp)
        
        



    def tamanyoLadoCirculo(self):
        '''
        lado me gusta mas que spinB...value
        '''
        self.lado= self.spinBox.value() 

    def hacer5(self):  
        self.tempdir=configuracioQvista.tempdir
        fic_tmp=os.path.join(self.tempdir,"temporal.png")    
        self.pixmap = QPixmap(fic_tmp)  
        # self.pixmap=self.canvas.grab() # no acaba de ir bien, me carga en pixmap tambien el circulo pintado
        # tamaño del pixmap
        hp= self.pixmap.height()                                         # alto imagen 
        wp= self.pixmap.width()                                          # ancho imagen salvada
        # radio. 
        if hp < wp:
            self.rP= hp/2
        else:
            self.rP= wp/2

        self.xcP = wp/2
        self.ycP = hp/2
        # self.rP = math.sqrt(math.pow((self.xcP-self.xrP), 2) + math.pow((self.ycP-self.yrP), 2))  # radio pantalla
        pcX= self.xcP - self.rP ; pcY= self.ycP - self.rP                                    # punto inicio crop
        self.an= 2* self.rP;      self.al= self.an                            # an, ancho para crop   al, alto para crop
        # escala= self.rP /self.rM                                                   # escala, como relacion de radiopantalla a radiomundo
        # pmin= QPoint();   
        # pmin.setX(pcX); 
        # pmin.setY(pcY+self.al); 
        # self.Pmin = self.toMapCoordinates(pmin)
        # pmax= QPoint();   
        # pmax.setX(pcX+self.an); 
        # pmax.setY(pcY); 
        # self.Pmax = self.toMapCoordinates(pmax)        

        # calculo area de recorte para hacer el crop 
        rect= QRect(pcX, pcY, self.an, self.al)
        # hago crop
        cropped_pixmap = self.pixmap.copy(rect) 
        
        # escalo el pixmap al tamaño que quiero
        self.scaled_pixmap = cropped_pixmap.scaled(self.lado, self.lado, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # de pixmap a image
        image=QImage(self.scaled_pixmap.toImage())
        image = image.convertToFormat(QImage.Format_ARGB32)

        # preparo imagen de salida transparente y del tamaño del de entrada....
        out_img = QImage(image.width(), image.width(), QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        # Create a texture brush and paint a circle with the original image onto
        # the output image: Chapeau!!
        brush = QBrush(image)        # Create texture brush
        painter = QPainter(out_img)  # Paint the output image
        painter.setBrush(brush)      # Use the image texture brush
        # painter.setPen(Qt.NoPen)     # Don't draw an outline
        # pen= QPen(QColor(121,144,155),  1, Qt.SolidLine)    #qVista claro         
        pen= QPen(self.color,  1, Qt.SolidLine)    #qVista claro         
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
        painter.drawEllipse(0, 0, image.width(), image.width())  # Actually draw the circle
        painter.end()                # We are done (segfault if you forget this)

        # de out_img a pixmap
        self.scaled_pixmap = QPixmap.fromImage(out_img)

        # muestro ese pixmap en label...
        self.label.setPixmap(self.scaled_pixmap)

        # y lo salvo como temporal2
        fic_tmp=os.path.join(self.tempdir,"temporal2.png")  
        self.fileName= fic_tmp 

        if self.fileName:
            # Guardo el pixmap como png
            self.scaled_pixmap.save(self.fileName)
            # Calculo info para el PQW
            # rango mundo x e y



            xdist = self.xmax- self.xmin   
            ydist = self.ymax- self.ymin
            # ancho y alto de la imagen
            iheight = self.scaled_pixmap.height() 
            iwidth =  self.scaled_pixmap.width()  

            # Preparo nombre del PGW
            split_nombre=os.path.splitext(self.fileName)
            filenamePgw=split_nombre[0]+".pgw"

            # Escribo PGW
            wld =open(filenamePgw, "w")   
            wld.writelines("%s\n" % (xdist/iwidth))
            wld.writelines("0.0\n")
            wld.writelines("0.0\n")
            wld.writelines("%s\n" % (ydist/iheight))
            wld.writelines("%s\n" % self.xmin)
            wld.writelines("%s\n" % self.ymin)
            wld.close


        # #  muestro datos de georeferenciacion
        # literal= "xmin,ymin=" + str(round(self.Pmin.x(),3)) +"  "+ str(round(self.Pmin.y(),3))
        # self.parent.xmin_ymin.setText(literal)
        # literal= "xmax,ymax=" + str(round(self.Pmax.x(),3)) +"  "+ str(round(self.Pmax.y(),3))
        # self.parent.xmax_ymax.setText(literal)

 
        try:
            self.reset()
        except:
            pass       
     


    def actualizar(self):
        try:
            self.colocoCirculo.saveCanvas1()
        except Exception  as ee:
            print("Desde carga Aun no implementado")
            self.hacer5()
       

            pass
        
    def ponerCirculo(self):
        '''
        Dibujo circulo, dinamicamente
        '''

        if self.canvas.rotation() != 0:
            self.canvas.setRotation(0)

        self.label.setPixmap(QPixmap())
        numeroSegmentsCercle=360
        lado=self.lado
        # if not self.existeCirculo:
        #     self.colocoCirculo= QvColocacionCirculo(self.canvas,  numeroSegmentsCercle,self,lado)
        #     self.existeCirculo=True
        #     self.canvas.setMapTool(self.colocoCirculo)

        # reseterar circulo
        try:
            self.colocoCirculo.rubberband.reset(True)
        except :
            pass

        self.colocoCirculo= QvColocacionCirculo(self.canvas,  numeroSegmentsCercle,self,lado)
        self.existeCirculo=True
        self.canvas.setMapTool(self.colocoCirculo)
    
    def showDialogColor(self):
        d_color= QColorDialog()
        
        col = d_color.getColor()
        if col.isValid():
            self.color=col



    def Cargar(self):
        '''
        Leo PNG y PGW
        ''' 
        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl(self.dadesdir))

        # Images (*.png );;World files (*.pgw)
        self.fileName,_ = dialegObertura.getOpenFileName(parent=self,\
                                                        caption= 'Cargar mapeta',\
                                                        directory='', 
                                                        filter="World files(*.pgw);;Images(*.png);;Tot(*.*)")
        if self.fileName:   
            split_nombre=os.path.splitext(self.fileName)
            filenamePGW=split_nombre[0]+".pgw"
            filenamePNG=split_nombre[0]+".png"
            datos_mapeta = self.CalcularPNGyRangoMapeta(filenamePNG)

            pixmap = QPixmap(filenamePNG) 
            self.label.setPixmap(pixmap) 

            literal= "xmin,ymin=" + str(round(datos_mapeta[1],3)) +"  "+ str(round(datos_mapeta[2],3))
            self.xmin_ymin.setText(literal)
            literal= "xmax,ymax=" + str(round(datos_mapeta[3],3)) +"  "+ str(round(datos_mapeta[4],3))
            self.xmax_ymax.setText(literal)
            self.spinBox.setValue(datos_mapeta[5])

            self.xmin= datos_mapeta[1]
            self.ymin= datos_mapeta[2]
            self.xmax= datos_mapeta[3]
            self.ymax= datos_mapeta[4]
            pass
            #  TODO: Actualizar variables necesarias para poder hacer recalculos
            self.rang = QgsRectangle(self.xmin,self.ymin,self.xmax,self.ymax)
            self.canvas.setExtent(self.rang)


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
        widthPNG= pixmap.width()    
        
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
            x=heigthPNG;             y=widthPNG
            x1= A*x + B*y + C;       y1 =D*x + E*y + F
            xmin= C;            ymin= F
            xmax= x1;           ymax= y1
            return ficheroPNG,xmin,ymin,xmax,ymax,  widthPNG , heigthPNG        

        except:
            print("problemas PGW")    




    def Salvar(self):
        '''
        Escribo PNG y PGW
        '''        
        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl(self.dadesdir))
        self.fileName,_ = dialegObertura.getSaveFileName(self, 'Guardar mapeta', '', 'PNG(*.png)')
        if self.fileName:
            # Guardo el pixmap como png
            self.colocoCirculo.scaled_pixmap.save(self.fileName)
            # Calculo info para el PQW
            # rango mundo x e y
            xdist = self.colocoCirculo.Pmax.x()- self.colocoCirculo.Pmin.x()   
            ydist = self.colocoCirculo.Pmax.y()- self.colocoCirculo.Pmin.y() 

            # ancho y alto de la imagen
            iheight = self.colocoCirculo.scaled_pixmap.height() 
            iwidth =  self.colocoCirculo.scaled_pixmap.width()  

            # Preparo nombre del PGW
            split_nombre=os.path.splitext(self.fileName)
            filenamePgw=split_nombre[0]+".pgw"

            # Escribo PGW
            wld =open(filenamePgw, "w")   
            wld.writelines("%s\n" % (xdist/iwidth))
            wld.writelines("0.0\n")
            wld.writelines("0.0\n")
            wld.writelines("%s\n" % (ydist/iheight))
            wld.writelines("%s\n" % self.colocoCirculo.Pmin.x())
            wld.writelines("%s\n" % self.colocoCirculo.Pmin.y())
            wld.close

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("You sure?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


    def closeEvent(self,event):
        pass
        # fic_tmp=os.path.join(fic_tmp,"temporal.png")    
        # if os.path.exists(fic_tmp):
        #     os.remove(fic_tmp)
        # else:
        #     print("The file does not exist")               

        # fic_tmp=os.path.join(fic_tmp,"temporal2.png")    
        # if os.path.exists(fic_tmp):
        #     os.remove(fic_tmp)
        # else:
        #     print("The file does not exist")   

        # fic_tmp=os.path.join(fic_tmp,"temporal.pgw")    
        # if os.path.exists(fic_tmp):
        #     os.remove(fic_tmp)
        # else:
        #     print("The file does not exist")   




# Demo d'ús quan es crida el fitxer de la classe per separat
if __name__ == "__main__":
    
    with qgisapp() as app:
        # Canvas, projecte i bridge
        canvas=QgsMapCanvas()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)

        # llegim un projecte de demo
        project.read(projecteInicial)
        # windowTest = QMainWindow()
        windowTest = MyWindow()

        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)

        # Instanciamos la classe QvcrearMapetaConBotones
        crearMapetaConBotones = QvCrearMapetaConBotones(canvas)
        crearMapetaConBotones.show()

        """
        Amb aquesta linia:
        crearMapeta.show()
        es veuria el widget suelto, separat del canvas.
        Les següents línies mostren com integrar el widget 'crearMapeta' com a dockWidget.
        """
        # Creem un dockWdget i definim les característiques
        dwcrearMapeta = QDockWidget( "CrearMapeta", windowTest )
        dwcrearMapeta.setContextMenuPolicy(Qt.PreventContextMenu)
        dwcrearMapeta.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwcrearMapeta.setContentsMargins ( 1, 1, 1, 1 )
        
        # # # AÑADIMOS  nuestra instancia al dockwidget
        dwcrearMapeta.setWidget(crearMapetaConBotones)

        # # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwcrearMapeta)

        # # Fem visible el dockWidget
        dwcrearMapeta.show()  #atencion

        # Fem visible la finestra principal
        canvas.show()
        windowTest.show()



        