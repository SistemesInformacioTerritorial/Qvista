# coding:utf-8

from importaciones import *
# import recursos
from configuracioQvista import *
from plantillaQvista_3 import Ui_MainWindow
from QvUbicacions import QvUbicacions
from QvPrint import QvPrint
from QvAnotacions import QvAnotacions
from QvEinesGrafiques import QvSeleccioElement, QvSeleccioPerPoligon

from QvStreetView import QvStreetView
from moduls.QvLlegenda import QvLlegenda
from moduls.QvAtributs import QvAtributs


class QvCanvas(QgsMapCanvas):
    def __init__(self, llistaBotons, botoneraHoritzontal = False, posicioBotonera = 'NO', mapesBase = False, llegenda = None): #mapesBase (???)
        QgsMapCanvas.__init__(self)
        self.botoneraHoritzontal = botoneraHoritzontal
        self.llistaBotons = llistaBotons
        self.posicioBotonera = posicioBotonera
        self.llegenda = llegenda

        self._preparacioBotonsCanvas()

    def seleccioClick(self):    
        tool = QvSeleccioElement(self, llegenda = self.llegenda)
        try:
            qV.canvas.setMapTool(tool)
        except:
            pass

    def centrarMapa(self):
        self.zoomToFullExtent()
        self.refresh()

    def zoomIn(self):
        self.tool_zoomin = QgsMapToolZoom(self, False)
        self.setMapTool(self.tool_zoomin)

    def zoomOut(self):
        self.tool_zoomout = QgsMapToolZoom(self, True)
        self.setMapTool(self.tool_zoomout)

    def panCanvas(self):
        self.tool_pan = QgsMapToolPan(self)
        self.setMapTool(self.tool_pan)

    def _botoMapa(self,imatge):
        boto = QtWidgets.QToolButton()
        icon=QIcon(imatge)
        boto.setIcon(icon)
        boto.setWindowOpacity(0.5)
        boto.setIconSize(QtCore.QSize(25,25))
        boto.setGeometry(0,0,25,25)
        return boto

    def _preparacioBotonsCanvas(self):
        self.botoneraMapa = QtWidgets.QFrame()
        # self.botoneraMapa.move(10,10)

        # self.botoneraMapa.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.botoneraMapa.setFrameShadow(QtWidgets.QFrame.Raised)

        if self.botoneraHoritzontal:
            self.layoutCanvas = QVBoxLayout(self)
            self.layoutBotoneraMapa = QHBoxLayout(self.botoneraMapa)
        else:
            self.layoutCanvas = QHBoxLayout(self)
            self.layoutBotoneraMapa = QVBoxLayout(self.botoneraMapa)

        self.layoutCanvas.setContentsMargins(3,3,3,3)
        self.layoutBotoneraMapa.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layoutCanvas) 

        spacer = QtWidgets.QSpacerItem(9999, 9999, QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Maximum)
                    
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


        if "apuntar" in self.llistaBotons:
            self.bApuntar = self._botoMapa('apuntar.png')
            self.layoutBotoneraMapa.addWidget(self.bApuntar)        
            self.bApuntar.clicked.connect(self.seleccioClick)
        if "centrar" in self.llistaBotons:
            self.bCentrar = self._botoMapa('imatges/ic_zoom_out_map_black_48dp.png')
            self.layoutBotoneraMapa.addWidget(self.bCentrar)     
            self.bCentrar.clicked.connect(self.centrarMapa)
        if "zoomIn" in self.llistaBotons:
            self.bZoomIn = self._botoMapa('imatges/zoom_in.png')
            self.bZoomIn.setCheckable(True)
            self.layoutBotoneraMapa.addWidget(self.bZoomIn)     
            self.bZoomIn.clicked.connect(self.zoomIn)
        if "zoomOut" in self.llistaBotons:
            self.bZoomOut = self._botoMapa('imatges/zoom_out.png')
            self.layoutBotoneraMapa.addWidget(self.bZoomOut)     
            self.bZoomOut.clicked.connect(self.zoomOut)
        if "panning" in self.llistaBotons:
            self.bPanning = self._botoMapa('imatges/pan_tool_black_24x24.png')
            self.layoutBotoneraMapa.addWidget(self.bPanning)     
            self.bPanning.clicked.connect(self.panCanvas)

        # spacer = QtWidgets.QSpacerItem(0, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        # self.layoutBotoneraMapa.addSpacerItem(spacer)

        self.butoMostra = QtWidgets.QPushButton()
        self.butoMostra.setMaximumHeight(80)
        self.butoMostra.setMinimumHeight(80)
        self.butoMostra.setMaximumWidth(80)
        self.butoMostra.setMinimumWidth(80)

        icon=QIcon('mapeta1.png')
        self.butoMostra.setIconSize(QtCore.QSize(80,80))
        self.butoMostra.setIcon(icon)

        self.butoMostra2 = QtWidgets.QPushButton()
        self.butoMostra2.setMaximumHeight(80)
        self.butoMostra2.setMinimumHeight(80)
        self.butoMostra2.setMaximumWidth(80)
        self.butoMostra2.setMinimumWidth(80)
        icon=QIcon('mapeta2.png')
        self.butoMostra2.setIconSize(QtCore.QSize(80,80))
        self.butoMostra2.setIcon(icon)
        self.botoneraMostres = QtWidgets.QFrame()

        
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



if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        llistaBotons = ['centrar', 'zoomIn', 'zoomOut', 'panning']
        canvas = QvCanvas(llistaBotons, posicioBotonera = 'NO', botoneraHoritzontal = True)

        project= QgsProject().instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        project.read(projecteInicial)

        canvas.show()