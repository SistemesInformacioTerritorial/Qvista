# coding:utf-8

from moduls.QvImports import *

from qgis.PyQt.QtCore import pyqtSignal

from qgis.PyQt.QtWebKitWidgets import QWebView , QWebPage #QWebPage (???)
from moduls.QvPushButton import QvPushButton

class BotoQvBrowser(QvPushButton):
    def __init__(self):
        super().__init__()
        # self.setMinimumHeight(30)
        # self.setMaximumHeight(30)
        # self.setMinimumWidth(100)
        # self.setMaximumWidth(100)

class Browser(QWebView):
    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        if (ok):
            frame = self.page().mainFrame()
            document = frame.documentElement()
            button = document.findFirst("div[id=consent-bump]")

            if (not button.isNull()):
                button.takeFromDocument()

class QvBrowser(QWidget):
    svMogut=pyqtSignal(float,float)
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.browser = Browser()
        self.browser.setContentsMargins(0,0,0,0)
        # self.browser.setUrl(QUrl("http://www.qt.io"))
        self.browser.resize(512, 375)
        self.browser.show()
        self.setContentsMargins(0,0,0,0)

        self.layoutBrowser = QVBoxLayout(self)
        self.layoutBrowser.setContentsMargins(0,0,0,0)
        self.layoutBrowser.setSpacing(0)

        self.botoneraQvBrowser = QFrame()
        self.botoneraQvBrowser.setContentsMargins(0,0,0,0)
        self.botoneraQvBrowser.setMinimumHeight(30)
        self.botoneraQvBrowser.setMaximumHeight(45)
        # self.botoneraQvBrowser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # self.botoneraQvBrowser.setVerticalPolicy(QSizePolicy.Minimum)

        self.layoutBotonera = QHBoxLayout(self.botoneraQvBrowser)
        self.layoutBotonera.setContentsMargins(0,0,0,0)
        self.layoutBotonera.setAlignment( Qt.AlignCenter )
        self.botoneraQvBrowser.setLayout(self.layoutBotonera)

        # self.botoTancar = BotoQvBrowser()
        # self.botoTancar.setText('SORTIR')
        # self.botoTancar.clicked.connect(self.tancar)
        # self.botoTancar.show()

        # self.botoOSM = BotoQvBrowser()
        # self.botoOSM.setText('OpenStreet Maps')
        # self.botoOSM.clicked.connect(self.openStreetMaps)

        self.botoGoogleMaps = BotoQvBrowser()
        self.botoGoogleMaps.setText('Google Maps')
        self.botoGoogleMaps.clicked.connect(self.openGoogleMaps)

        self.botoStreetView = BotoQvBrowser()
        self.botoStreetView.setText('Street view')
        self.botoStreetView.clicked.connect(self.openStreetView)

        self.browser.urlChanged.connect(self.extreuCoordenades)

        # self.layoutBotonera.addWidget(self.botoOSM)
        self.layoutBotonera.addWidget(self.botoGoogleMaps)
        self.layoutBotonera.addWidget(self.botoStreetView)
        self.layoutBrowser.addWidget(self.botoneraQvBrowser)
        self.layoutBrowser.addWidget(self.browser)
        self.setLayout(self.layoutBrowser)
        # https://www.openstreetmap.org/#map=17/41.38740/2.17272
    
    def openGoogleMaps(self):
        self.browser.setUrl(QUrl(self.parent.urlGoogleMaps))
    def openStreetMaps(self):
        # self.browser.setUrl(QUrl('https://www.openstreetmap.org/#map=16/41.38740/2.17272'))
        self.browser.setUrl(QUrl(self.parent.urlStreetMaps))
    def openStreetView(self):
        self.browser.setUrl(QUrl(self.parent.urlStreetView))

    def extreuCoordenades(self,url):
        urlStr=url.url()
        URLMAPS='https://www.google.com/maps/@'
        URLSV='https://www.google.com/maps?layer=c&cbll='
        URLOSM='https://www.openstreetmap.org/#map=16/'
        if URLSV in urlStr:
            urlStr=urlStr.replace(URLSV,'')
            y,x = urlStr.split(',')
        elif URLMAPS in urlStr:
            urlStr=urlStr.replace(URLMAPS,'')
            sp=urlStr.split(',')
            y, x = sp[0], sp[1]
            
        elif URLOSM in urlStr:
            #Fer el que toqui
            return
        else:
            return
        x,y = float(x), float(y)
        # self.svMogut.emit(x,y)
        self.svMogut.emit(x,y)
    
    def tancar(self):
        print('sortir')
        self.hide()

class PointTool(QgsMapTool):
    def __init__(self, parent, canvas):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent
        self.canvas = canvas
        self.moureBoto = False
        self.parent.m = QgsVertexMarker(self.canvas)
            
    def canvasMoveEvent(self, event):
        self.parent.dockX = event.pos().x()
        self.parent.dockY = event.pos().y()
        if self.moureBoto:
            self.parent.boto.move(event.x()-30,event.y()-30)


    def tresParaules(self,xx,yy):
        try:
            point= QgsPointXY(xx, yy)

            self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:25831"), 
                                QgsCoordinateReferenceSystem("EPSG:4326"), 
                                QgsProject.instance())

            self.puntTransformat=self.transformacio.transform(point) 
            self.parent.urlStreetView = "https://maps.google.com/maps?layer=c&cbll={},{}".format(self.puntTransformat.y(), self.puntTransformat.x())

            self.parent.qbrowser.browser.setUrl(QUrl(self.parent.urlStreetView))
            self.parent.qbrowser.show()
            self.parent.show()
        except:
            pass  


    
    def llevame(self,x,y):
        self.portam(QPoint(x,y))
    # def llevame(self,point):
    #     self.portam(point)
    
    def llevameP(self,x,y):
        self.llevameP(QPoint(x,y))
    def llevameP(self,point):
        '''Obre streetview donada una posició de la pantalla
        '''
        self.portam(self.toMapCoordinates(point))

    def portam(self,point):
        self.point=QgsPointXY(point)
        # self.point = self.toMapCoordinates(point)
        xMon = self.point.x() #???
        yMon = self.point.y() #???

        self.transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:25831"), 
                             QgsCoordinateReferenceSystem("EPSG:4326"), 
                             QgsProject.instance())

        self.puntTransformat=self.transformacio.transform(self.point) 

        self.parent.pucMoure = False
        # streetView = 'https://www.google.com/maps/@{},{},3a,75y,0h,75t'.format(self.puntTransformat.y(),puntTransformat.x())
        # streetView = 'https://www.google.com/maps/@{},{},2a/data=!3m1!1e3'.format(puntTransformat.y(),puntTransformat.x())
        self.parent.urlStreetView = "https://maps.google.com/maps?layer=c&cbll={},{}".format(self.puntTransformat.y(), self.puntTransformat.x())
        self.parent.urlGoogleMaps = 'https://www.google.com/maps/@{},{},2a/data=!3m1!1e3'.format(self.puntTransformat.y(), self.puntTransformat.x())
        self.parent.urlStreetMaps = "https://www.openstreetmap.org/#map=16/{}/{}".format(self.puntTransformat.y(), self.puntTransformat.x())

        self.parent.qbrowser.browser.setUrl(QUrl(self.parent.urlStreetView))
        self.parent.qbrowser.show()
        self.parent.show()            
        try:
            import what3words

            geocoder = what3words.Geocoder("HTD7LNB9")
            palabras = geocoder.convert_to_3wa(what3words.Coordinates(self.puntTransformat.y(), self.puntTransformat.x()), language='es')
            # coordenadas = geocoder.convert_to_coordinates('agudo.lista.caja')
            print(palabras['words'])
        except:
            print('No va 3 words')
        # self.parent.boto.move(40, 5) 
        # self.m.setCenter(QgsPointXY(event.x()-30,event.y()-30))
        self.canvas.scene().removeItem(self.parent.m)
        self.parent.m = QgsVertexMarker(self.canvas)
        self.parent.m.setCenter( QgsPointXY( self.point.x(), self.point.y() ) )
        self.parent.m.setColor(QColor(255, 0, 0))
        self.parent.m.setIconSize(15)
        self.parent.m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.parent.m.setPenWidth(3)
        self.parent.m.show()
        self.moureBoto = False
    def canvasReleaseEvent(self, event):
        self.llevameP(event.pos())

class QvStreetView(QWidget):
    """Una classe del tipus QWidget 
    """
    def __init__(self, canvas, parent = None):
        """Inicialització de la clase:
            Arguments:
                canvas {QgsVectorLayer} -- El canvas sobre el que es clicka   
        """
        # We inherit our parent's properties and methods.
        QWidget.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)

        self.canvas = canvas
        self.parent = parent
        self.rp = PointTool(self, self.canvas)
        # self.canvas.setMapTool(self.rp)
        # self.boto = QvPushButton(parent = self.canvas, flat = True)
        # self.icon=QIcon(os.path.join(imatgesDir,'littleMan.png'))
        # self.boto.setIcon(self.icon)
        # # self.boto.clicked.connect(self.segueixBoto)
        # self.boto.setGeometry(8,713,25,25)
        # self.boto.hide()
        # self.boto.setIconSize(QSize(25,25))
        # self.boto.hide()
        

        self.setupUI()
        # self.canvas.xyCoordinates.connect(self.mocMouse)
    def getBoto(self):
        return self.boto
    def segueixBoto(self):
        return
        self.boto.show()
        self.canvas.setMapTool(self.rp)
        self.rp.moureBoto = True

    def setupUI(self):
        self.layoutH = QHBoxLayout(self)
        self.layoutH.setContentsMargins(0,0,0,0)
        self.layoutH.setSpacing(0)
        self.setLayout(self.layoutH)

        self.qbrowser = QvBrowser(self)
        self.qbrowser.show()
        self.qbrowser.svMogut.connect(self.mogut)

        self.layoutH.addWidget(self.qbrowser)

    def mogut(self, x, y):
        transformacio = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"), 
                            QgsCoordinateReferenceSystem("EPSG:25831"), 
                            QgsProject.instance())
        transformat=transformacio.transform(x,y)
        self.m.setCenter( QgsPointXY( transformat.x(), transformat.y() ) )






if __name__ == "__main__":
    projecteInicial='../dades/projectes/BCN11_nord.qgs'
    with qgisapp():
        canvas=QgsMapCanvas()
        canvas.setContentsMargins(0,0,0,0)
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo

        project.read(projecteInicial)
        
        qvSv = QvStreetView(canvas)
        qvSv.setContentsMargins(0,0,0,0)
        qvSv.show()

        canvas.show()

