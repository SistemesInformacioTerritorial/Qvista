# coding:utf-8

from moduls.QvImports import *
from moduls.QvEinesGrafiques import QvSeleccioElement
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtWidgets import QFrame
from moduls.QvApp import QvApp
from qgis.core.contextmanagers import qgisapp


class QvCanvas(QgsMapCanvas):
    def __init__(self, pare = None, llistaBotons= None, botoneraHoritzontal = False, posicioBotonera = 'NO', mapesBase = False, llegenda = None):
        QgsMapCanvas.__init__(self)
        self.botoneraHoritzontal = botoneraHoritzontal
        self.llistaBotons = llistaBotons
        self.posicioBotonera = posicioBotonera
        self.llegenda = llegenda
        self.pare = pare
        self.setWhatsThis(QvApp().carregaAjuda(self))

        self._preparacioBotonsCanvas()
        self.panCanvas()

    def seleccioClick(self):    
        checked = self.bApuntar.isChecked()
        print(checked)
        if  self.bApuntar.isChecked():
            tool = QvSeleccioElement(self, llegenda = self.llegenda)
            self.bZoomIn.setChecked(False)
            self.bZoomOut.setChecked(False)
            self.bPanning.setChecked(False)
            self.bZoomIn.setChecked(False)
            self.bCentrar.setChecked(False)
            try:
                self.setMapTool(tool)
            except:
                print ('except')
                pass
        else:
            self.bApuntar.setChecked(True)

    def centrarMapa(self):
        self.zoomToFullExtent()
        self.refresh()
        self.bCentrar.setChecked(False)

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

    def panCanvas(self):
        if self.bPanning.isChecked():
            self.bApuntar.setChecked(False)
            self.bZoomIn.setChecked(False)
            self.bZoomOut.setChecked(False)
            self.bCentrar.setChecked(False)
            self.tool_pan = QgsMapToolPan(self)
            self.setMapTool(self.tool_pan)
            self.pare.esborrarSeleccio(tambePanCanvas = False)
        else: 
            self.bPanning.setChecked(True)

    def setLlegenda(self, llegenda):
        self.llegenda = llegenda
        
    def _botoMapa(self,imatge):
        boto = QPushButton()
        boto.setCheckable(True)
        icon=QIcon(imatge)
        boto.setIcon(icon)
        boto.setWindowOpacity(0.5)
        boto.setIconSize(QSize(25,25))
        boto.setGeometry(0,0,25,25)
        return boto

    def _preparacioBotonsCanvas(self):
        self.botoneraMapa = QFrame()
        # self.botoneraMapa.setStyleSheet("QFrame {background-color: #ffffff;}")

        # self.botoneraMapa.move(10,10)

        # self.botoneraMapa.setFrameShape(QFrame.StyledPanel)
        # self.botoneraMapa.setFrameShadow(QFrame.Raised)

        if self.botoneraHoritzontal:
            self.layoutCanvas = QVBoxLayout(self)
            self.layoutBotoneraMapa = QHBoxLayout(self.botoneraMapa)
        else:
            self.layoutCanvas = QHBoxLayout(self)
            self.layoutBotoneraMapa = QVBoxLayout(self.botoneraMapa)

        self.layoutCanvas.setContentsMargins(3,3,3,3)
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
                self.layoutCanvas.addWidget(self.botoneraMapa)  
                self.layoutCanvas.addSpacerItem(spacer)   
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



        if "panning" in self.llistaBotons:
            self.bPanning = self._botoMapa('imatges/pan_tool_black_24x24.png')
            self.layoutBotoneraMapa.addWidget(self.bPanning)     
            self.bPanning.clicked.connect(self.panCanvas)
        if "centrar" in self.llistaBotons:
            self.bCentrar = self._botoMapa('imatges/fit.png')
            self.layoutBotoneraMapa.addWidget(self.bCentrar)     
            self.bCentrar.clicked.connect(self.centrarMapa)
        if "zoomIn" in self.llistaBotons:
            self.bZoomIn = self._botoMapa('imatges/zoom_in.png')
            self.layoutBotoneraMapa.addWidget(self.bZoomIn)     
            self.bZoomIn.clicked.connect(self.zoomIn)
        if "zoomOut" in self.llistaBotons:
            self.bZoomOut = self._botoMapa('imatges/zoom_out.png')
            self.layoutBotoneraMapa.addWidget(self.bZoomOut)     
            self.bZoomOut.clicked.connect(self.zoomOut)
        if "apuntar" in self.llistaBotons:
            self.bApuntar = self._botoMapa('imatges/apuntar.png')
            self.layoutBotoneraMapa.addWidget(self.bApuntar)        
            self.bApuntar.clicked.connect(self.seleccioClick)

        # spacer = QSpacerItem(0, 50, QSizePolicy.Expanding, QSizePolicy.Maximum)
        # self.layoutBotoneraMapa.addSpacerItem(spacer)

        self.butoMostra = QPushButton()
        self.butoMostra.setMaximumHeight(80)
        self.butoMostra.setMinimumHeight(80)
        self.butoMostra.setMaximumWidth(80)
        self.butoMostra.setMinimumWidth(80)

        icon=QIcon('imatges/mapeta1.png')
        self.butoMostra.setIconSize(QSize(80,80))
        self.butoMostra.setIcon(icon)

        self.butoMostra2 = QPushButton()
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


class Marc(QFrame):
    def __init__(self, master=None):
        QFrame.__init__(self, master)

    def paintEvent(self, ev):
        painter = QPainter(self)
        # gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        # gradient.setColorAt(0.0, Qt.black)
        # gradient.setColorAt(0.4, Qt.gray)
        # gradient.setColorAt(0.7, Qt.black)
        painter.setBrush(QColor(100,100,100))
        painter.drawRoundedRect(self.rect(), 10.0, 10.0)
        # painter.end()

if __name__ == "__main__":
    from qgis.core import QgsProject
    from qgis.gui import  QgsLayerTreeMapCanvasBridge
    from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
   

    projecteInicial='../dades/projectes/BCN11_nord.qgs'

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