# https://www.qtcentre.org/threads/53745-QPixmap-as-background-of-QWidget
# from info_ui import Informacio
import time
from os import putenv
from typing import Pattern

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                             QVBoxLayout, QWidget)
from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                       QgsPointXY, QgsProject, QgsRectangle)
from qgis.core.contextmanagers import qgisapp
from qgis.gui import QgsMapCanvas, QgsMapTool, QgsVertexMarker
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (QComboBox, QDockWidget, QLineEdit,
                                 QMessageBox, QPushButton, QSizePolicy)

from moduls import QvFuncions
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton


class PointTool(QgsMapTool):   
    def __init__(self, canvas, parent):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas  
        self.parent = parent
        self.m1 = QgsVertexMarker(canvas)
        self.m1.setColor(QColor(255,0, 0)) #(R,G,B)
        self.m1.setIconSize(12)
        self.m1.setIconType(QgsVertexMarker.ICON_CROSS)
        self.m1.setPenWidth(3)

    def canvasPressEvent(self, event):
        self.parent.nova = False
        x = self.parent.leXcoord1.text()
        y = self.parent.leYcoord1.text()
        self.m1.setCenter(QgsPointXY(float(x),float(y)))
        self.m1.show()



@QvFuncions.creaEina(titol="Eina Coordenades", esEinaGlobal = True, apareixDockat = False)
class EinaCoordenades(QWidget):

    dicEPSG= {                   
        # descripcion                        : [EPSG,                EsTresor,  EsLatitudLongidud]
        "ED50 UTM fus 31"                    : ["EPSG:23031",        False,     False],         
        "ED50 UTM fus 31 retallades (AJB)"   : ["EPSG:23O31",        True,      False],   
        "ED50 geogràfiques (lat, lon)"       : ["EPSG:4230",         False,     True], 
        ""                                   : [""],
        "ETRS89 UTM fus 31"                  : ["EPSG:25831",        False,     False], 
        "ETRS89 UTM fus 31 retallades (AJB)" : ["EPSG:25831",        True,      False], 
        "ETRS89 geogràfiques (lat, lon)"     : ["EPSG:4258",         False,     True], 
        " "                                  : [""],

        "WGS84 UTM fus 31"                   : ["EPSG:32631",        False,     False],         
        "WGS84 geogràfiques (lat, lon)"      : ["EPSG:4326",         False,     True], 
        "  "                                 : [""],
        "WGS84 Pseudo-Mercator"              : ["EPSG:3857",         False,     True]            
    }

    invDicEPGS= {}
    for clave, valor in dicEPSG.items(): 
        invDicEPGS.setdefault(valor[0],clave)


    def __init__(self, pare):
        QWidget.__init__(self)
        if isinstance(pare, QgsMapCanvas):
            self.canvas = pare
        else: 
            self.canvas = pare.canvas
        self.setParent(pare)
        self.pare = pare
        self.nova = True

        self.setFixedWidth(500)
        self.setFixedHeight(120)

        #region Detección sistema coordenadas proyecto
        try:
            # https://qgis.org/api/classQgsCoordinateReferenceSystem.html
            
            
            
            





            self.sistemaCoords = self.canvas.mapSettings().destinationCrs().authid()
            sc= self.canvas.mapSettings().destinationCrs()
            kk= sc.description()
            
            try:
                self.sistemaCoords_info = self.invDicEPGS.get(self.sistemaCoords)
            except Exception as ee:
                self.sistemaCoords_info = self.sistemaCoords
        except:
            print("coords malament")
        #endregion Detección sistema coordenadas proyecto
        #region DEFINICION DE widgets
        # BOTON NUEVO PUNTO
        nou = QPushButton()
        nou.setIcon(QIcon('Imatges/redCross.png'))
        nou.pressed.connect(self.novaCoordenada)
        nou.setText("Nou punt")
        nou.setMaximumWidth(80)

        # BOTON HELP EPSG
        icona_helpEPSG = QIcon('Imatges/help-circle.png')
        binfoEPSG = QPushButton()
        binfoEPSG.setIcon(icona_helpEPSG)
        binfoEPSG.pressed.connect(self.infoEPSG)
        binfoEPSG.setToolTip("info EPSG")
        binfoEPSG.setMaximumWidth(30)

        # LABEL MOSTRARSISTEMA  COORDENADAS DEL PROYECTO
        lblnom1 = QLabel()
        lblnom1.setMinimumWidth(75)
        lblnom1.setText(self.sistemaCoords_info)
        lblnom1.setToolTip(self.sistemaCoords)
        
        # COMBO MOSTRAR EPGS PARA TRANSFORMACIONES
        self.lblnom2 = QComboBox()
        self.lblnom2.setMinimumWidth(75)
        
        

        # LABEL PARA MOSTRAR COOR X LATITUD? DEL MAPA
        self.leXcoord1 = QLineEdit()
        # LABEL PARA MOSTRAR COOR y LONGITUD? DEL MAPA
        self.leYcoord1 = QLineEdit()
                
        self.leXcoord1.returnPressed.connect(self.transformaPunt)
        self.leYcoord1.returnPressed.connect(self.transformaPunt)

        self.leXcoord2 = QLineEdit()
        self.leYcoord2 = QLineEdit()
        
        icona_copiar = QIcon('Imatges/file-document.png')
        b1 = QPushButton()
        b1.pressed.connect(self.f1)
        b1.setIcon(icona_copiar)
        b1.setToolTip("Copia al portaretalls")

        b2 = QPushButton()
        b2.pressed.connect(self.f2)
        b2.setIcon(icona_copiar)
        b2.setToolTip("Copia al portaretalls")
        #endregion
        #region cargar combo con diccionario
        ii = 0
        for clave, valor in self.dicEPSG.items(): 
            if clave.strip()=="":
                self.lblnom2.insertSeparator(ii)        
            else:
                self.lblnom2.addItem(clave);  
            
            self.lblnom2.setItemData(ii, valor[0],QtCore.Qt.ToolTipRole)
            ii += 1
        # endregion cargar combo con diccionario
        #region DISEÑO
        lay = QVBoxLayout()
        lay0 = QHBoxLayout()
        lay1 = QHBoxLayout()
        lay2 = QHBoxLayout()

        Separador = QFrame()
        Separador.setFrameShape(QFrame.NoFrame)
        Separador.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)

        lay0.addWidget(nou)             # boton nuevo punto
        lay0.addWidget(Separador)
        lay0.addWidget(binfoEPSG)       # boton informacion EPSG

        lay1.addWidget(lblnom1)         # EPSG del mapa
        lay1.addWidget(self.leXcoord1)  # coord x? input
        lay1.addWidget(self.leYcoord1)  # coord y? input
        lay1.addWidget(b1)              # boton copiar a portapapeles

        lay2.addWidget(self.lblnom2)         # combo EPSGs conversiones
        lay2.addWidget(self.leXcoord2)  # coord x? output
        lay2.addWidget(self.leYcoord2)  # coord y? output
        lay2.addWidget(b2)              # boton copiar a portapapeles

        lay.addLayout(lay0)             # arriba
        lay.addLayout(lay1)             # en medio
        lay.addLayout(lay2)             # abajo

        self.setLayout(lay)             
        #endregion DISEÑO

        self.canvas.xyCoordinates.connect(self.showXY)  
        self.lblnom2.currentTextChanged.connect(self.cambiadoCombo)            

        self.tool = PointTool(self.canvas, self)
        self.canvas.setMapTool(self.tool)








    def novaCoordenada(self):
        """[summary]
        """
        self.nova = True

    def showXY(self,pnt): 
        """
        Recibe pnt, posicion del mouse
        """
        if self.nova:
            self.pnt = pnt   # para que se vea en toda la clase

            x1=round(pnt.x(),3)
            y1=round(pnt.y(),3)
            self.leXcoord1.setText(str(x1))
            self.leYcoord1.setText(str(y1))
            self.text1 = str(x1) + ", " + str(y1)   # para el paste

            epsg= self.dicEPSG.get(self.lblnom2.currentText())[0]
            esTresor= self.dicEPSG.get(self.lblnom2.currentText())[1]
            EsLatitudLongidud= self.dicEPSG.get(self.lblnom2.currentText())[2]

            # print("EPSG salida {}".format(epsg))

            # creo CRS con formato Proj 
            # Si epgs hace referencia a ED50, ETRS89 en Rango Catalunya....
            self.crsPreciso = QgsCoordinateReferenceSystem()
            self.crsPreciso.createFromProj ('+proj=utm +zone=31 +ellps=intl +nadgrids="C:/Program Files/QGIS 3.10/100800401.gsb" +units=m +wktext +no_defs')
            validado= self.crsPreciso.isValid()


            # print("sistema coordenadas",self.sistemaCoords)
            # self.transformacio = QgsCoordinateTransform(
            #                 QgsCoordinateReferenceSystem(self.sistemaCoords), 
            #                 QgsCoordinateReferenceSystem(epsg), 
            #                 QgsProject.instance())


            self.transformacio = QgsCoordinateTransform(
                            QgsCoordinateReferenceSystem(self.sistemaCoords), 
                            QgsCoordinateReferenceSystem(self.crsPreciso), 
                            QgsProject.instance())                            
            
            
            
            
            # punto transformado

            # print("CRS Description: {}".format(self.sistemaCoords.description()))
            # print("CRS PROJ text: {}".format(epsg.toProj()))

            # https://inecumene.blogspot.com/2013/04/qgis-definicion-y-creacion-de.html
            # app.srsDatabaseFilePath()
            # C:\Program Files\QGIS 3.10\apps\qgis-ltr\resources\srs.db
            self.pnt1=self.transformacio.transform(self.pnt)

            if esTresor == True:
                x2 = int((round(self.pnt1.x(),3)*1000) - 400000000)
                y2 = int((round(self.pnt1.y(),3)*1000) - 4500000000)
            else:
                if EsLatitudLongidud == True:
                    x2 = round(self.pnt1.y(),8)
                    y2 = round(self.pnt1.x(),8)                    
                else:
                    x2 = round(self.pnt1.x(),3)
                    y2 = round(self.pnt1.y(),3)

            self.leXcoord2.setText(str(x2))
            self.leYcoord2.setText(str(y2))
            self.text2 = str(x2) + ", " + str(y2)   


    def hideEvent(self,event):
        super().hideEvent(event)
        self.canvas.unsetMapTool(self.tool)
        self.canvas.scene().removeItem(self.tool.m1)

    def showEvent(self,event):
        super().showEvent(event)
        self.canvas.setMapTool(self.tool)

    def infoEPSG(self):
        msg1= '<a href="https://www.icgc.cat/ca/Web/Ajuda/Preguntes-frequeents/Codis-EPSG">Més sobre Codis EPGS</a> <br>  \
               <a href= "https://www.icgc.cat/Administracio-i-empresa/Eines/Transforma-coordenada-format/Calculadora"> Calculadora geodesica ICC</a><br> \
               <a href="http://www.ign.es/wcts-app/">Calculadora IGN </a> <br><br><img src= "D:/qVista/Codi/Imatges/CodisEPSG.png">'
               
        
        QMessageBox.about(self, "sr ",msg1)     

    def is_number(self,s):
        """
        Para saber si una cadena es numero

        Args:
            literal a testear

        Returns:
            Bool: si la entrada es numerica devuelve True, sino False
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def f1(self):
        """
        Respuesta a boton guardar coordenadas en clipboard
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text1)
    
    def f2(self):
        """
        Respuesta a boton guardar coordenadas en clipboard
        """        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text2)

    def transformaPunt(self):
        """Respuesta al final de una edición de coordenadas
        """
        if self.is_number(self.leXcoord1.text()) and self.is_number(self.leYcoord1.text()):
            x = float(self.leXcoord1.text())
            y = float(self.leYcoord1.text())
            self.pnt = QgsPointXY(x,y)
            estat_nova = self.nova 
            self.nova = True
            self.showXY(self.pnt)
            self.nova = estat_nova

    def cambiadoCombo(self):
        """Se ejecuta cuando hay cambio de valor en el combo de EPSG
        """
        
        estat_nova = self.nova 
        self.nova = True
        self.showXY(self.pnt)
        self.nova = estat_nova

if __name__ == "__main__":
       with qgisapp() as app:
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
        from qgis.gui import QgsLayerTreeMapCanvasBridge

        from moduls.QvLlegenda import QvLlegenda

        # Canvas, projecte i bridge
        start1 = time.time()
        canvas=QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='mapesOffline/qVista default map.qgs'
        projecteInicial='mapesOffline/qVista default map_JNB1.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
            qvEinaCoords = EinaCoordenades(pare=canvas)
            #dwLay = QVBoxLayout()
            dwEC = QDockWidget()
            dwEC.setWidget(qvEinaCoords)
            dwEC.show()
            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")