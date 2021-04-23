# https://www.qtcentre.org/threads/53745-QPixmap-as-background-of-QWidget
from moduls.QvImports  import *

from qgis.core import QgsRectangle, QgsPointXY
from qgis.gui import QgsMapTool
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout 
from PyQt5.QtWidgets import QHBoxLayout, QFrame
from PyQt5.QtWidgets import  QApplication, QMessageBox
from moduls import QvFuncions
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QvMultiruta import *
from moduls.QvReverse import QvReverse

class QAdrecaPostalLineEdit(QLineEdit):
    def focusInEvent(self, event):
        if self.text().startswith("--"):
            self.setText('')
        super(QAdrecaPostalLineEdit, self).focusInEvent(event)

class PointTool(QgsMapTool):  
        def __init__(self, canvas, parent):
            QgsMapTool.__init__(self, canvas)
            self.canvas = canvas  
            self.parent = parent

        def canvasPressEvent(self, event):
            if self.parent.getPoint == 1:
                startPoint = QgsPointXY(event.mapPoint())
                self.parent.startPoint = startPoint
                self.parent.mStart.setCenter(startPoint)

                #TODO: improve speed
                reverseSearch = QvReverse(startPoint)
                self.parent.IniciLECarrer.setText("-- " + reverseSearch.nomCarrer + " --")
                if (reverseSearch.numCarrer != ""):
                    self.parent.IniciLENumero.setText("-- " + reverseSearch.numCarrer + " --")

            elif self.parent.getPoint == 2:
                endPoint = QgsPointXY(event.mapPoint())
                self.parent.endPoint = endPoint
                self.parent.mEnd.setCenter(endPoint)

                #TODO: imrpove speed
                reverseSearch = QvReverse(endPoint)
                self.parent.FiLECarrer.setText("-- " + reverseSearch.nomCarrer + " --")
                if (reverseSearch.numCarrer != ""):
                    self.parent.FiLENumero.setText("-- " + reverseSearch.numCarrer + " --")

@QvFuncions.creaEina(titol="Eina Multiruta (OSRM)", esEinaGlobal = True, apareixDockat = False)
class EinaMultiruta(QWidget):
    getPoint = 0
    """
    Valors del getPoint:
        0 - no seleccionar un punt
        1 - seleccionar punt inicial
        2 - seleccionar punt final
    """
    # canvas = None
    tool = None

    # pGirs = [] #punts de gir
    # indicacions = [] #descripcions de la ruta

    startPoint = QgsPointXY(float(0),float(0))
    endPoint = QgsPointXY(float(0),float(0))

    mStart = None
    mEnd = None

    ruta = QvMultiruta([None,None])

    FiLECarrer = QAdrecaPostalLineEdit()
    FiLENumero = QAdrecaPostalLineEdit()

    def APostaltoCoord_Inici(self,rsc):
        if rsc==0:
            self.startPoint = self.cercadorInici.coordAdreca
            self.mStart.setCenter(self.startPoint)

    def APostaltoCoord_Final(self,rsc):
        if rsc==0:
            self.endPoint = self.cercadorFinal.coordAdreca
            self.mEnd.setCenter(self.endPoint)

    def __init__(self, pare):
        def getCoordInici():
            """
            handling botó d'obtenir punt inicial
            """
            if (self.IniciButtonGPS.isChecked() == True):
                self.canvas.setMapTool(self.tool)
                self.FiButtonGPS.setChecked(False)
                self.FiLECarrer.setEnabled(True)
                self.FiLENumero.setEnabled(True)
                self.getPoint = 1
                self.IniciLECarrer.setEnabled(False)
                self.IniciLENumero.setEnabled(False)
            else:
                self.getPoint = 0
                self.IniciLECarrer.setEnabled(True)
                self.IniciLENumero.setEnabled(True)
                if (self.FiButtonGPS.isChecked() == False):
                    self.canvas.unsetMapTool(self.tool)

        def getCoordFi():
            """
            handling botó d'obtenir punt final
            """
            if (self.FiButtonGPS.isChecked() == True):
                self.canvas.setMapTool(self.tool)
                self.IniciButtonGPS.setChecked(False)
                self.IniciLECarrer.setEnabled(True)
                self.IniciLENumero.setEnabled(True)
                self.getPoint = 2
                self.FiLECarrer.setEnabled(False)
                self.FiLENumero.setEnabled(False)
            else:
                self.getPoint = 0
                self.FiLECarrer.setEnabled(True)
                self.FiLENumero.setEnabled(True)
                if (self.IniciButtonGPS.isChecked() == False):
                    self.canvas.unsetMapTool(self.tool)

        def getIndicacions(girs):
            descripcions = []
            for gir in girs:
                descripcions.append(gir.descripcio)
            return descripcions

        def calcularRuta():
            self.IniciButtonGPS.setChecked(False)
            self.FiButtonGPS.setChecked(False)
            self.IniciLECarrer.setEnabled(True)
            self.FiLECarrer.setEnabled(True)
            self.canvas.unsetMapTool(self.tool)
            self.getPoint = 0

            self.ruta.hideRoute()
            # self.ruta.ocultarPuntsGir()
            self.ruta = QvMultiruta([self.startPoint,self.endPoint])
            self.ruta.setRouteOptions(True, True, True)
            self.ruta.getRoute()
            self.ruta.printRoute(self.canvas)

            # self.indicacioBox.clear()
            # self.lblDistancia.setText("")
            # self.lblDurada.setText("")

            if (self.ruta.routeOK == False):
                print("error calculant la ruta")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error calculant la ruta")
                msg.setInformativeText("La ruta no s'ha pogut calcular. Provi amb uns altres punts i asseguri's que el seu ordinador està connectat a la xarxa interna.")
                msg.setWindowTitle("Error")
                msg.exec_()
                self.lblDistancia.setText("Distancia: No s'ha pogut obtenir")
                self.lblDurada.setText("Durada: No s'ha pogut obtenir")
                # self.layoutInfo.removeWidget(self.lblDistancia)
                # self.layoutInfo.removeWidget(self.lblDurada)
                
            else:
                # Mostra distancia i durada de la ruta
                # getDistanciaDurada()
                # Incialitzem layout per a mostrar descripcio de la ruta i els seus botons
                # getIndicacionsDeRuta()
                pass

                    
        def preparacioUI():
            def preparacioCercadorPostal(lay):
                def preparacioCercadorStartPoint(lay):
                    #layout vertical per posar títol
                    layoutLlocInici = QVBoxLayout()
                    lblTextInici = QLabel("Lloc d'inici")
                    layoutLlocInici.addWidget(lblTextInici)

                    layoutAdrecaInicial = QHBoxLayout()              
                    layoutLlocInici.addLayout(layoutAdrecaInicial)

                    #elements layout cercador
                    lblTextCarrer = QLabel('Carrer:')
                    lblTextNumero = QLabel('Num:')

                    self.IniciLECarrer = QAdrecaPostalLineEdit()
                    self.IniciLECarrer.setToolTip('Introdueix adreça i selecciona de la llista')
                    self.IniciLECarrer.setMinimumWidth(200)

                    self.IniciLENumero = QAdrecaPostalLineEdit()
                    self.IniciLENumero.setToolTip('Introdueix número, selecciona de la llista i prem RETURN')
                    self.IniciLENumero.setMaximumWidth(100)
                    self.IniciLENumero.setMinimumWidth(100)

                    self.IniciButtonGPS = QPushButton("", self)
                    self.IniciButtonGPS.setGeometry(200, 150, 100, 30)
                    self.IniciButtonGPS.clicked.connect(getCoordInici)
                    self.IniciButtonGPS.setCheckable(True)
                    self.IniciButtonGPS.setIcon(QIcon('Imatges/logoGPS.png'))

                    #afegir elements al layout cercador
                    layoutAdrecaInicial.addWidget(lblTextCarrer)
                    layoutAdrecaInicial.addWidget(self.IniciLECarrer)
                    layoutAdrecaInicial.addWidget(lblTextNumero)
                    layoutAdrecaInicial.addWidget(self.IniciLENumero)
                    layoutAdrecaInicial.addWidget(self.IniciButtonGPS)

                    lay.addLayout(layoutLlocInici)

                    # Activem la clase de cerca d'adreces
                    self.cercadorInici = QCercadorAdreca(self.IniciLECarrer, self.IniciLENumero,'SQLITE')
                    self.cercadorInici.sHanTrobatCoordenades.connect(self.APostaltoCoord_Inici)

                def preparacioCercadorEndPoint(lay):
                    #layout vertical per posar títol
                    layoutLlocFinal = QVBoxLayout()
                    lblTextInici = QLabel("Lloc d'arribada")
                    layoutLlocFinal.addWidget(lblTextInici)

                    layoutAdrecaFinal = QHBoxLayout()
                    layoutLlocFinal.addLayout(layoutAdrecaFinal)

                    #Elementos para layout H, del cercador
                    lblTextCarrer = QLabel('Carrer:')
                    lblTextNumero = QLabel('Num:')

                    self.FiLECarrer=QAdrecaPostalLineEdit()
                    self.FiLECarrer.setToolTip('Introdueix adreça i selecciona de la llista')
                    self.FiLECarrer.setMinimumWidth(200) 

                    self.FiLENumero=QAdrecaPostalLineEdit()                           
                    self.FiLENumero.setToolTip('Introdueix número, selecciona de la llista i prem RETURN')
                    self.FiLENumero.setMaximumWidth(100)                   
                    self.FiLENumero.setMinimumWidth(100)

                    self.FiButtonGPS = QPushButton("", self)
                    self.FiButtonGPS.setGeometry(200, 150, 100, 30)
                    self.FiButtonGPS.clicked.connect(getCoordFi)
                    self.FiButtonGPS.setCheckable(True)
                    self.FiButtonGPS.setIcon(QIcon('Imatges/logoGPS.png'))

                    # llenamos layout horizontal de adreca
                    layoutAdrecaFinal.addWidget(lblTextCarrer)
                    layoutAdrecaFinal.addWidget(self.FiLECarrer)
                    layoutAdrecaFinal.addWidget(lblTextNumero)
                    layoutAdrecaFinal.addWidget(self.FiLENumero)
                    layoutAdrecaFinal.addWidget(self.FiButtonGPS)

                    lay.addLayout(layoutLlocFinal)

                    # Activem la clase de cerca d'adreces
                    self.cercadorFinal = QCercadorAdreca(self.FiLECarrer, self.FiLENumero,'SQLITE')
                    self.cercadorFinal.sHanTrobatCoordenades.connect(self.APostaltoCoord_Final)
                
                    
                preparacioCercadorStartPoint(lay)
                preparacioCercadorEndPoint(lay)

            QWidget.__init__(self)

            if isinstance(pare, QgsMapCanvas):
                self.canvas = pare
            else: 
                self.canvas = pare.canvas
            
            lay = QVBoxLayout()
            self.setLayout(lay)

            preparacioCercadorPostal(lay)

            calcRouteButton = QPushButton()
            calcRouteButton.pressed.connect(calcularRuta)
            calcRouteButton.setText("Calcular ruta")
            lay.addWidget(calcRouteButton)

        preparacioUI()
        self.initMarkers()
        self.tool = PointTool(self.canvas, self)

    def eventComboBox(self, index):
        self.canvas.setCenter(self.pGirs[int(index.row())].coord)
        self.canvas.zoomScale(1000)
        self.canvas.refresh()
    
    # def goNext(self):
    #     if(self.index != None):
    #         if(int(self.index) < self.indicacioBox.count()-1):
    #             self.index += 1
    #             self.canvas.setCenter(self.pGirs[self.index].coord)
    #             self.indicacioBox.setCurrentIndex(self.index)
    #             self.canvas.zoomScale(1000)
    #             self.canvas.refresh()

    # def goPrev(self):
    #     if(self.index != None):
    #         if(int(self.index) > 0):
    #             self.index -= 1
    #             self.canvas.setCenter(self.pGirs[self.index].coord)
    #             self.indicacioBox.setCurrentIndex(self.index)
    #             self.canvas.zoomScale(1000)
    #             self.canvas.refresh()

    def initMarkers(self):
        self.mStart = QgsVertexMarker(self.canvas)
        self.mStart.setColor(QColor(255, 0, 0)) #(R,G,B)
        self.mStart.setIconSize(12)
        self.mStart.setIconType(QgsVertexMarker.ICON_CROSS)
        self.mStart.setPenWidth(3)

        self.mEnd = QgsVertexMarker(self.canvas)
        self.mEnd.setColor(QColor(0, 0, 255)) #(R,G,B)
        self.mEnd.setIconSize(12)
        self.mEnd.setIconType(QgsVertexMarker.ICON_CROSS)
        self.mEnd.setPenWidth(3)

    def hideEvent(self,event):
        super().hideEvent(event)
        self.canvas.unsetMapTool(self.tool)
        self.canvas.scene().removeItem(self.mStart)
        self.canvas.scene().removeItem(self.mEnd)
        self.ruta.hideRoute()
        # self.ruta.ocultarPuntsGir()
        # self.indicacioBox.hide()
        # self.botoPrevi.hide()
        # self.botoNext.hide()
        # self.indicacioBox.clear()
        # self.lblDistancia.clear()
        # self.lblDurada.clear()

    def showEvent(self,event):
        super().showEvent(event)
        self.initMarkers()
        self.getPoint = 0
        self.IniciLECarrer.setEnabled(True)
        self.IniciLENumero.setEnabled(True)
        self.FiLECarrer.setEnabled(True)
        self.FiLENumero.setEnabled(True)
        self.IniciButtonGPS.setChecked(False)
        self.IniciLECarrer.setText("")
        self.IniciLENumero.setText("")
        self.FiButtonGPS.setChecked(False)
        self.FiLECarrer.setText("")
        self.FiLENumero.setText("")

if __name__ == "__main__":
    with qgisapp() as app:
        from qgis.gui import  QgsLayerTreeMapCanvasBridge
        from moduls.QvLlegenda import QvLlegenda
        from qgis.gui import QgsMapCanvas
        from qgis.core import QgsProject
        from qgis.core.contextmanagers import qgisapp
     
        # Canvas, projecte i bridge
        start1 = time.time()
        canvas = QgsMapCanvas()
        
        canvas.show()
        canvas.setRotation(0)
        project = QgsProject.instance()
        projecteInicial='mapesOffline/qVista default map.qgs'

        if project.read(projecteInicial):
            root = project.layerTreeRoot()
            bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
            qvEinaRuta = EinaRuta(canvas)
            dwEC = QDockWidget()
            dwEC.setWidget(qvEinaRuta)
            dwEC.show()
            print ('resto: ',time.time()-start1)
        else:
            print("error en carga del proyecto qgis")