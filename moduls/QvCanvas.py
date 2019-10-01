# coding:utf-8


from moduls.QvEinesGrafiques import QvSeleccioElement
from qgis.PyQt.QtCore import Qt, QSize
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan
from qgis.PyQt.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from qgis.PyQt.QtGui import QIcon, QPainter, QCursor,QPixmap, QKeyEvent
from moduls.QvApp import QvApp
from moduls.QvImports  import *
from qgis.core.contextmanagers import qgisapp
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from moduls.QvConstants import QvConstants
from moduls.QvStreetView import *
#from qVista import QVista



class QvCanvas(QgsMapCanvas):
    def __init__(self, pare = None, llistaBotons= None, botoneraHoritzontal = False, posicioBotonera = 'NO', mapesBase = False, llegenda = None): #mapesBase (???)
        QgsMapCanvas.__init__(self)
        self.botoneraHoritzontal = botoneraHoritzontal
        self.llistaBotons = llistaBotons
        self.posicioBotonera = posicioBotonera
        self.llegenda = llegenda
        self.pare = pare
        self.setSelectionColor(QvConstants.COLORDESTACAT)
        self.setAcceptDrops(True)
        
        # self.setWhatsThis(QvApp().carregaAjuda(self))

        self._preparacioBotonsCanvas()
        if self.llistaBotons is not None:
            self.panCanvas()
            

    def keyPressEvent(self, event):
        """ Defineix les actuacions del QvMapeta en funció de la tecla apretada.
        """
        if event.key() == Qt.Key_Escape:
            if self.pare is not None:
                if not self.pare.mapaMaxim:
                    self.pare.ferGran()
                try:
                    self.pare.esborrarSeleccio(tambePanCanvas = False)
                    self.tool.fitxaAtributs.close()
                except:
                    pass
        if event.key()==Qt.Key_F11:
            if self.pare is not None:
                self.pare.ferGran()

    def panCanvas(self):        # MANO
        # bucle para quitar todos los cursores guardados. quiero que use el que ofrece MapTool
        # while self.pare.app.overrideCursor() != None:
        #     self.pare.app.restoreOverrideCursor()


        if self.bPanning.isChecked():
            self.bApuntar.setChecked(False)
            self.bZoomIn.setChecked(False)
            self.bZoomOut.setChecked(False)
            self.bCentrar.setChecked(False)
           
            self.tool_pan = QgsMapToolPan(self)
            self.setMapTool(self.tool_pan)


        else: 
            self.bPanning.setChecked(True)

    def amagaStreetView(self):
        self.bstreetview.setChecked(False)

    def centrarMapa(self):
        if self.bCentrar.isChecked():
            self.zoomToFullExtent()
            self.refresh()
        self.bCentrar.setChecked(False)
        # self.bCentrar.setChecked(True)

    def zoomIn(self):
        if self.bZoomIn.isChecked():
            self.bApuntar.setChecked(False)
            self.bZoomOut.setChecked(False)
            self.bPanning.setChecked(False)
            self.bCentrar.setChecked(False)
           
            self.tool_zoomin = QgsMapToolZoom(self, False)
            self.setMapTool(self.tool_zoomin)
        else: 
            self.bZoomIn.setChecked(True)
        self.setCursor(QvConstants.cursorZoomIn())

    def zoomOut(self):
        if self.bZoomOut.isChecked():
            self.bApuntar.setChecked(False)
            self.bZoomIn.setChecked(False)
            self.bPanning.setChecked(False)
            self.bCentrar.setChecked(False)
           
            self.tool_zoomout = QgsMapToolZoom(self, True)
            self.setMapTool(self.tool_zoomout)
        else: 
            self.bZoomOut.setChecked(True)

        self.setCursor(QvConstants.cursorZoomOut())

    def seleccioClick(self):
        if  self.bApuntar.isChecked():

            self.bZoomIn.setChecked(False)
            self.bZoomOut.setChecked(False)
            self.bPanning.setChecked(False)
            self.bCentrar.setChecked(False)

            try:
                self.pare.esborrarSeleccio(tambePanCanvas = False)
                self.tool.fitxaAtributs.close()
            except:
                pass

            try:
                self.tool = QvSeleccioElement(self, llegenda = self.llegenda)
                self.setMapTool(self.tool)
            except:
                pass
        else:
            self.bApuntar.setChecked(True)
        
        self.setCursor(QvConstants.cursorDit())


    def setLlegenda(self, llegenda):
        self.llegenda = llegenda
    def setStreetView(self,streetView):
        self.qvSv=streetView
        #self.bstreetview.clicked.connect(self.qvSv.segueixBoto)
    def _botoMapa(self,imatge = None):
        boto = QvPushButton(flat=True)
        boto.setStyleSheet('background: rgba(255,255,255,168); padding: 1px;')
        boto.setCheckable(True)
        if imatge is not None:
            icon=QIcon(imatge)
            boto.setIcon(icon)
        boto.setWindowOpacity(0.5)
        boto.setIconSize(QSize(24,24))
        boto.setGeometry(0,0,24,24)
        return boto

    def _preparacioBotonsCanvas(self):
        self.botoneraMapa = QFrame()

        #self.botoneraMapa.move(90,20)#nofares

        #self.botoneraMapa.setFrameShape(QFrame.StyledPanel)
        #self.botoneraMapa.setFrameShadow(QFrame.Raised)

        if self.botoneraHoritzontal:
            self.layoutCanvas = QVBoxLayout(self)
            self.layoutBotoneraMapa = QHBoxLayout(self.botoneraMapa)
        else:
            self.layoutCanvas = QHBoxLayout(self)
            self.layoutBotoneraMapa = QVBoxLayout(self.botoneraMapa)

        self.layoutCanvas.setContentsMargins(15,15,15,15)
        self.layoutBotoneraMapa.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layoutCanvas) 

        spacer = QSpacerItem(9999, 9999, QSizePolicy.Expanding,QSizePolicy.Maximum)
                    
        self.botoneraMapa.setLayout(self.layoutBotoneraMapa)

        if self.posicioBotonera == 'NE':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignRight) 
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignTop) 
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  



        if self.posicioBotonera == 'NO':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                self.offsetEsq = QLabel()
                self.offsetEsq.setFixedWidth(200)
                self.offsetUp = QLabel()
                self.offsetUp.setFixedHeight(0)
                self.layoutBotoneraMapa.addWidget(self.offsetEsq)
                # self.layoutCanvas.addWidget(self.offsetUp)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
                #self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                #self.layoutCanvas.addWidget(self.botoneraMapa)  
                #self.layoutCanvas.addSpacerItem(spacer)   
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignTop)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
                


        if self.posicioBotonera == 'SE':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignRight)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignBottom)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)                


        if self.posicioBotonera == 'SO':
            if self.botoneraHoritzontal:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignLeft)
                self.layoutCanvas.addSpacerItem(spacer)   
                self.layoutCanvas.addWidget(self.botoneraMapa)  
            else:
                self.layoutBotoneraMapa.setAlignment(Qt.AlignBottom)
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   

            # self.botoneraMapa.setMaximumHeight(25)
            # self.botoneraMapa.setMinimumHeight(25)
            # self.botoneraMapa.setMaximumWidth(9999)
            # self.botoneraMapa.setMinimumWidth(100)


        if self.llistaBotons is not None:
            if "apuntar" in self.llistaBotons:
                self.bApuntar = self._botoMapa('imatges/apuntar.png')
                self.bApuntar.setToolTip('Seleccioneu objectes per veure la seva informació')
                self.layoutBotoneraMapa.addWidget(self.bApuntar)  
                self.bApuntar.setCursor(QvConstants.cursorFletxa())       
                self.bApuntar.clicked.connect(self.seleccioClick)
            if "panning" in self.llistaBotons:
                self.bPanning = self._botoMapa('imatges/pan_tool_black_24x24.png')
                self.bPanning.setToolTip('Desplaçament sobre el mapa')
                self.layoutBotoneraMapa.addWidget(self.bPanning)   
                self.bPanning.setCursor(QvConstants.cursorFletxa())   
                self.bPanning.clicked.connect(self.panCanvas)
            if "centrar" in self.llistaBotons:
                self.bCentrar = self._botoMapa('imatges/fit.png')
                self.bCentrar.setToolTip('Enquadrar el mapa complet a la pantalla')
                self.layoutBotoneraMapa.addWidget(self.bCentrar) 
                self.bCentrar.setCursor(QvConstants.cursorFletxa())     
                self.bCentrar.clicked.connect(self.centrarMapa)
            if "zoomIn" in self.llistaBotons:
                self.bZoomIn = self._botoMapa('imatges/zoom_in.png')
                self.bZoomIn.setToolTip('Zoom per apropar-se')
                self.layoutBotoneraMapa.addWidget(self.bZoomIn)  
                self.bZoomIn.setCursor(QvConstants.cursorFletxa())
                self.bZoomIn.clicked.connect(self.zoomIn)
            if "zoomOut" in self.llistaBotons:
                self.bZoomOut = self._botoMapa('imatges/zoom_out.png')
                self.bZoomOut.setToolTip('Zoom per allunyar-se')
                self.layoutBotoneraMapa.addWidget(self.bZoomOut) 
                self.bZoomOut.setCursor(QvConstants.cursorFletxa())  
                self.bZoomOut.clicked.connect(self.zoomOut)
            if 'enrere' in self.llistaBotons:
                self.bEnrere=self._botoMapa('Imatges/qv_vista_anterior.png')
                self.bEnrere.setToolTip('Retrocedeix al zoom previ')
                self.layoutBotoneraMapa.addWidget(self.bEnrere)
                self.bEnrere.setCursor(QvConstants.cursorFletxa())
                self.bEnrere.clicked.connect(self.zoomToPreviousExtent)
                self.bEnrere.setCheckable(False)
            if 'endavant' in self.llistaBotons:
                self.bEndavant=self._botoMapa('Imatges/qv_vista_seguent.png')
                self.bEndavant.setToolTip('Avançar al zoom següent')
                self.layoutBotoneraMapa.addWidget(self.bEndavant)
                self.bEndavant.setCursor(QvConstants.cursorFletxa())
                self.bEndavant.clicked.connect(self.zoomToNextExtent)
                self.bEndavant.setCheckable(False)
            if "streetview" in self.llistaBotons:
                self.bstreetview = self._botoMapa('imatges/littleMan.png') 
                self.bstreetview.setDragable(True)
                self.bstreetview.setCheckable(False)
                self.bstreetview.setToolTip('Google Street view')
                self.layoutBotoneraMapa.addWidget(self.bstreetview)   
                self.bstreetview.setCursor(QvConstants.cursorFletxa()) 
                # self.bstreetview.clicked.connect(self.amagaStreetView)  
                #self.bstreetview.clicked.connect(QvStreetView.segueixBoto)
            if 'maximitza' in self.llistaBotons:
                self.iconaMaximitza=QIcon('imatges/fullscreen.png')
                self.iconaMinimitza=QIcon('imatges/fullscreen-exit.png')
                self.bMaximitza = self._botoMapa('imatges/fullscreen.png') 
                self.bMaximitza.setToolTip('Pantalla completa (F11)')
                self.layoutBotoneraMapa.addWidget(self.bMaximitza)   
                self.bMaximitza.setCursor(QvConstants.cursorFletxa()) 
                self.bMaximitza.clicked.connect(self.pare.ferGran)  
                self.bMaximitza.setCheckable(False)

        # spacer = QSpacerItem(0, 50, QSizePolicy.Expanding, QSizePolicy.Maximum)
        # self.layoutBotoneraMapa.addSpacerItem(spacer)

        self.butoMostra = QvPushButton(flat=True)
        self.butoMostra.setMaximumHeight(80)
        self.butoMostra.setMinimumHeight(80)
        self.butoMostra.setMaximumWidth(80)
        self.butoMostra.setMinimumWidth(80)

        icon=QIcon('imatges/mapeta1.png')
        self.butoMostra.setIconSize(QSize(80,80))
        self.butoMostra.setIcon(icon)

        self.butoMostra2 = QvPushButton(flat=True)
        self.butoMostra2.setMaximumHeight(80)
        self.butoMostra2.setMinimumHeight(80)
        self.butoMostra2.setMaximumWidth(80)
        self.butoMostra2.setMinimumWidth(80)
        icon=QIcon('imatges/mapeta2.png')
        self.butoMostra2.setIconSize(QSize(80,80))
        self.butoMostra2.setIcon(icon)
        self.botoneraMostres = QFrame()

        
        # self.layoutCanvas = QVBoxLayout(self)
        # self.layoutCanvas.setContentsMargins(0,0,0,0)
        # self.setLayout(self.layoutCanvas)

        self.layoutBotoneraMostres = QHBoxLayout(self.botoneraMostres)
        self.botoneraMostres.setLayout(self.layoutBotoneraMostres)
        # self.layoutCanvas.setAlignment(Qt.AlignVCenter)
        self.layoutBotoneraMostres.addWidget(self.butoMostra)
        self.layoutBotoneraMostres.addWidget(self.butoMostra2)
        self.layoutBotoneraMostres.setAlignment(Qt.AlignRight)
        # self.layoutCanvas.addWidget(self.botoneraMapa)
        # self.layoutCanvas.addWidget(self.botoneraMostres)    
    def dragEnterEvent(self, e):
      
        e.accept()
        

    def dropEvent(self, e):

        position = e.pos()
        self.qvSv.rp.portam(position)
        # self.button.move(position)

        e.setDropAction(Qt.MoveAction)
        e.accept()
 


class Marc(QFrame):
    def __init__(self, master=None):
        QFrame.__init__(self, master)
    #ENTRA????
    def paintEvent(self, ev):
        painter = QPainter(self)
        # gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        # gradient.setColorAt(0.0, Qt.black)
        # gradient.setColorAt(0.4, Qt.gray)
        # gradient.setColorAt(0.7, Qt.black)
        painter.setBrush(Qt.QColor(100,100,100))
        painter.drawRoundedRect(self.rect(), 10.0, 10.0)
        # painter.end()

class BotoStreetView(QPushButton):
  
    def __init__(self, title, parent):
        super().__init__(title, parent)
        
        self.setAcceptDrops(True)
        

    def dragEnterEvent(self, e):
      
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e):
        
        self.setText(e.mimeData().text()) 



if __name__ == "__main__":
    from qgis.core import QgsProject
    from qgis.gui import  QgsLayerTreeMapCanvasBridge
    from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel
    from qgis.PyQt.QtGui import QColor
   

    
    projecteInicial='D:/qVista/Dades/Projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        # app.setStyle(QStyleFactory.create('fusion'))
        
        llistaBotons = ['centrar', 'zoomIn', 'zoomOut', 'panning']
        widget = QWidget()
        widget.show()
        canvas = QvCanvas(llistaBotons, posicioBotonera = 'NO', botoneraHoritzontal = True)
        canvas.setParent(widget)
        canvas.setGeometry(10,10,1000,1000)
        canvas.setCanvasColor(QColor(10,10,10))
        marc = Marc(canvas)
        marc.setGeometry(10,10,100,100)
        marc.show()
        label = QLabel(marc)
        label.setGeometry(10,10,10,10)
        label.setText('sdf')

        project= QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        # canvas.show()