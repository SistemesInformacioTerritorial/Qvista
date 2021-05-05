# https://www.qtcentre.org/threads/53745-QPixmap-as-background-of-QWidget
from moduls.QvImports  import *

from qgis.core import QgsRectangle, QgsPointXY
from qgis.gui import QgsMapTool
from moduls.QvConstants import QvConstants
from moduls.QvPushButton import QvPushButton
from configuracioQvista import *
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication, QMessageBox
from moduls import QvFuncions
from moduls.QVCercadorAdreca import QCercadorAdreca
from moduls.QvMultiruta import *
from moduls.QvReverse import QvReverse

class QAdrecaPostalLineEdit(QLineEdit):
    def focusInEvent(self, event):
        if self.text().startswith("Punt seleccionat"):
            self.setText('')
        super(QAdrecaPostalLineEdit, self).focusInEvent(event)

class QPointNameLabel(QLabel):
    def __init__(self, buddy, parent = None):
        super(QPointNameLabel, self).__init__(parent)
        self.buddy = buddy

    # When it's clicked, hide itself and show its buddy
    def mousePressEvent(self, event):
        self.hide()
        self.buddy.show()
        self.buddy.setFocus() # Set focus on buddy so user doesn't have to click again

class PointUI:
    pointList = []
    #layout
    #eina

    def __init__(self,lay,eina):
        self.layout = lay
        self.eina = eina

    def addItem(self,customName):
        new_element = PointUI_element(self.layout,len(self.pointList),customName,self) #la classe PointUI_element ja s'encarrega d'afegir al layout el conjunt d'elements
        self.pointList.append(new_element)
        # self.eina.routePoints.append(QgsPointXY(-1,-1))
        # self.eina.routePointMarkers.append(QgsVertexMarker(self.eina.canvas))
        self.refreshLayout()
        self.checkRemoveButtons()

    def addBetweenPoints(self,actPoint,customName):
        new_element = PointUI_element(self.layout,actPoint,customName,self) #la classe PointUI_element ja s'encarrega d'afegir al layout el conjunt d'elements
        i = actPoint
        while i < len(self.pointList):
            self.pointList[i].pointNumber = self.pointList[i].pointNumber + 1
            self.pointList[i].updateLbl()
            i += 1
        self.pointList.insert(actPoint, new_element)
        self.refreshLayout()
        self.checkRemoveButtons()

    #check whether the remove items need to be enabled or not
    def checkRemoveButtons(self):
        if len(self.pointList) > 2:
            self.enableRemoveButtons()
        else:
            self.disableRemoveButtons()

    def enableRemoveButtons(self):
        for el in self.pointList:
            el.buttonRemovePoint.setEnabled(True)

    def disableRemoveButtons(self):
        for el in self.pointList:
            el.buttonRemovePoint.setEnabled(False)

    def refreshLayout(self):
        #eliminar i tornar a afegir els layouts per a que estiguin endreçats
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).setParent(None)

        for el in self.pointList:
            self.layout.addLayout(el.layoutPunt)

    def refreshLabels(self):
        #refrescar els labels que hi ha per cada punts
        for el in self.pointList:
            el.updateLbl()

    def removeItem(self,item):
        actLayout = self.layout.itemAt(item)

        #delete the marker
        self.eina.canvas.scene().removeItem(self.pointList[item].marker)

        #delete all the widgets from the layout
        for i in reversed(range(actLayout.count())):
            if actLayout.itemAt(i).widget() != None:
                actLayout.itemAt(i).widget().setParent(None)

        #delete the layout from the list
        actLayout.setParent(None)
        self.pointList.pop(item)

        #renumerate the points
        for i, el in enumerate(self.pointList):
            el.pointNumber = i

        #refresca els textos dels noms dels punts
        self.refreshLabels()

        self.checkRemoveButtons()

    def pressButtonGPS(self,item):
        if self.pointList[item].buttonGPS.isChecked():
            for pointElement in self.pointList:
                pointElement.buttonGPS.setChecked(False)
                pointElement.LECarrer.setEnabled(True)
                pointElement.LENumero.setEnabled(True)
            self.pointList[item].buttonGPS.setChecked(True)
            self.pointList[item].LECarrer.setEnabled(False)
            self.pointList[item].LENumero.setEnabled(False)
        else:
            self.pointList[item].LECarrer.setEnabled(True)
            self.pointList[item].LENumero.setEnabled(True)
        
    #retornar els punts
    def getPoints(self):
        ret = []
        for pointElement in self.pointList:
            ret.append(pointElement.point)
        return ret

    #retornar els markers
    def getMarkers(self):
        ret = []
        for pointElement in self.pointList:
            ret.append(pointElement.marker)
        return ret

    #escriure el resultat de la reverse search als QLineEdits
    def setReverse(self,item,result):
        self.pointList[item].LECarrer.setText(result.nomCarrer)
        if (result.numCarrer != ""):
            self.pointList[item].LENumero.setText(result.numCarrer)

    def hideMarkers(self):
        for i in reversed(range(len(self.pointList))):
            self.eina.canvas.scene().removeItem(self.pointList[i].marker)

    def resetUI(self):
        #TODO: improve speed
        for i in reversed(range(len(self.pointList))):
            self.eina.canvas.scene().removeItem(self.pointList[i].marker)
            actLayout = self.pointList[i].layoutPunt
            #delete all the widgets from the layout
            for j in reversed(range(actLayout.count())):
                if actLayout.itemAt(j).widget() != None:
                    actLayout.itemAt(j).widget().setParent(None)

            #delete the layout from the list
            actLayout.setParent(None)
            self.pointList.pop(i)
        self.addItem("")
        self.addItem("")


class PointUI_element:
    #parent (layout)
    index = -1
    pointNumber = -1
    customName = ""
    #buttonGPS
    #point = QgsPointXY(-1,-1)

    def updateLbl(self):
        self.pointText_label.setText("Punt #" + str(self.pointNumber) + " " + self.customName)

    def pointNameEdited(self):
        self.customName = self.pointText_edit.text()
        self.updateLbl()
        self.pointText_edit.hide()
        self.pointText_label.show()

    def __init__(self,parent,pointNumber,customName,UIparent):
        self.parent = parent
        self.pointNumber = pointNumber
        self.UIparent = UIparent
        self.point = QgsPointXY(-1,-1)
        self.marker = QgsVertexMarker(self.UIparent.eina.canvas)
        eina = UIparent.eina

        self.layoutPunt = QHBoxLayout()

        self.pointText_edit = QLineEdit()
        self.pointText_edit.hide()
        self.pointText_edit.editingFinished.connect(self.pointNameEdited)
        self.pointText_label = QPointNameLabel(self.pointText_edit)
        self.pointText_label.setText("Punt #" + str(self.pointNumber) + " " + self.customName) #TODO: personalitzar noms
        self.layoutPunt.addWidget(self.pointText_edit)
        self.layoutPunt.addWidget(self.pointText_label)

        self.layoutAdrecaPostal = QHBoxLayout()
        self.layoutPunt.addLayout(self.layoutAdrecaPostal) #TODO: cercador postal universal

        self.lblTextCarrer = QLabel('Carrer:')
        self.LECarrer = QAdrecaPostalLineEdit()
        self.LECarrer.setToolTip('Introdueix adreça i selecciona de la llista')
        self.LECarrer.setMinimumWidth(200)

        self.lblTextNumero = QLabel('Núm:')
        self.LENumero = QAdrecaPostalLineEdit()
        self.LENumero.setToolTip('Introdueix número, selecciona de la llista i prem RETURN')
        self.LENumero.setMaximumWidth(100)
        self.LENumero.setMinimumWidth(100)

        self.buttonGPS = QPushButton("")
        self.buttonGPS.setGeometry(200, 150, 100, 30)
        self.parent.pointUI_index = self.pointNumber
        self.buttonGPS.clicked.connect(lambda: eina.getCoords(self.pointNumber))
        self.buttonGPS.setCheckable(True)
        self.buttonGPS.setIcon(QIcon('Imatges/logoGPS.png'))
        
        self.buttonNewPoint = QPushButton("")
        self.buttonNewPoint.setGeometry(200, 150, 100, 30)
        self.buttonNewPoint.clicked.connect(lambda:self.UIparent.addBetweenPoints(self.pointNumber+1,""))
        self.buttonNewPoint.setIcon(QIcon('Imatges/logoNewPoint.png'))

        self.buttonRemovePoint = QPushButton("")
        self.buttonRemovePoint.setGeometry(200, 150, 100, 30)
        self.buttonRemovePoint.clicked.connect(lambda:self.UIparent.removeItem(self.pointNumber))
        self.buttonRemovePoint.setIcon(QIcon('Imatges/logoRemovePoint.png'))

        self.layoutPunt.addWidget(self.lblTextCarrer)
        self.layoutPunt.addWidget(self.LECarrer)
        self.layoutPunt.addWidget(self.lblTextNumero)
        self.layoutPunt.addWidget(self.LENumero)
        self.layoutPunt.addWidget(self.buttonGPS)
        self.layoutPunt.addWidget(self.buttonNewPoint)
        self.layoutPunt.addWidget(self.buttonRemovePoint)

        self.cercador = QCercadorAdreca(self.LECarrer, self.LENumero,'SQLITE')
        self.cercador.sHanTrobatCoordenades.connect(lambda:eina.APostaltoCoord(self.pointNumber))

class PointTool(QgsMapTool):  
        def __init__(self, canvas, parent):
            QgsMapTool.__init__(self, canvas)
            self.canvas = canvas  
            self.parent = parent

        def canvasPressEvent(self, event):
            auxPoint = QgsPointXY(event.mapPoint())
            print(str(self.parent.pointUI_index) + str(auxPoint))
            self.parent.pointUI.pointList[self.parent.pointUI_index].point = auxPoint
            self.parent.pointUI.pointList[self.parent.pointUI_index].marker.setCenter(auxPoint)
            self.parent.pointUI.setReverse(self.parent.pointUI_index, QvReverse(auxPoint))

@QvFuncions.creaEina(titol="Eina Multiruta (OSRM)", esEinaGlobal = True, apareixDockat = False)
class EinaMultiruta(QWidget):
    getPoint = 0
    """
    Valors del getPoint:
        0 - no seleccionar un punt
        1 - seleccionar punt inicial
        2 - seleccionar punt final
    """
    # canvas
    tool = None

    # pGirs = [] #punts de gir
    # indicacions = [] #descripcions de la ruta

    # routePoints = []
    # routePointMarkers = []

    ruta = QvMultiruta([None,None])
    roundtrip = False
    source = True
    destination = True
    trip = True
    transportationMode = "vehicle"

    #pointUI
    pointUI_index = -1

    def APostaltoCoord(self, index):
        self.pointUI_index = index
        auxPoint = self.pointUI.pointList[self.pointUI_index].cercador.coordAdreca
        if (auxPoint != None):
            self.pointUI.pointList[self.pointUI_index].point = auxPoint
            self.pointUI.pointList[self.pointUI_index].marker.setCenter(auxPoint)

    def getCoords(self, index):
            """
            handling botó d'obtenir punt inicial
            """
            self.pointUI_index = index
            self.canvas.setMapTool(self.tool)
            self.pointUI.pressButtonGPS(self.pointUI_index)

    def setRouteOptions_roundtrip(self, boolean):
        self.roundtrip = boolean
        if not boolean:
            self.tripOptions_puntinici.setEnabled(False)
            self.tripOptions_puntinici.setChecked(True)
            self.tripOptions_puntfinal.setEnabled(False)
            self.tripOptions_puntfinal.setChecked(True)
        else:
            self.tripOptions_puntinici.setEnabled(True)
            self.tripOptions_puntfinal.setEnabled(True)

    def setRouteOptions_source(self, boolean):
        self.source = boolean

    def setRouteOptions_destination(self, boolean):
        self.destination = boolean

    def setRouteType(self,boolean):
        self.trip = boolean
        if (self.trip):
            self.tripOptions_groupbox.setEnabled(True)
        else:
            self.tripOptions_groupbox.setEnabled(False)

    def setTransportationMode(self,mode):
        self.transportationMode = mode

    #funció de càlcul de ruta. és cridada quan es clica al botó "calcular ruta"
    def calcularRuta(self):
        self.canvas.unsetMapTool(self.tool)
        self.getPoint = 0

        #TODO: activar el QLineEdit que hi havia activat i deseleccionar el maptool

        self.ruta.hideRoute() #reset ruta anterior
        self.ruta = QvMultiruta(self.pointUI.getPoints())
        self.ruta.setRouteOptions(self.roundtrip, self.source, self.destination)
        self.ruta.setRouteType(self.trip)
        self.ruta.setTransportationMode(self.transportationMode)
        self.ruta.getRoute()
        self.ruta.printRoute(self.canvas)

        if (self.ruta.routeOK == False):
            print("error calculant la ruta")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error calculant la ruta")
            msg.setInformativeText("La ruta no s'ha pogut calcular, asseguri's que té connexió a Internet. L'API d'OpenStreetMaps podria estar caiguda.")
            msg.setWindowTitle("Error")
            msg.exec_()

        else: #ruta calculada.
            self.setUI_Result()

    def exportRoute(self):
        pass

    #preparació UI pantalla resultat
    def setUI_Result(self):
        #layout principal
        container = QWidget()
        routeResult = QVBoxLayout(container)

        #groupbox
        routeResult_layout = QVBoxLayout()
        routeResult_groupbox = QGroupBox("Resultats de la ruta")
        routeResult_groupbox.setLayout(routeResult_layout)

        ####### UI dels punts visitats
        #creació d'un scrollable
        routeResult_scrollable = QScrollArea()
        routeResult_scrollable_widget = QWidget()
        routeResult_scrollable_layout = QVBoxLayout()
        routeResult_scrollable_widget.setLayout(routeResult_scrollable_layout)
        routeResult_scrollable.setWidget(routeResult_scrollable_widget)

        #opcions del scrollable
        routeResult_scrollable.setFixedHeight(450)
        routeResult_scrollable.setWidgetResizable(True)
        routeResult_scrollable.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        for i, wp in enumerate(self.ruta.waypoints):
            if (self.ruta.routeType):
                point_index = wp["waypoint_index"]
            else:
                point_index = i
            
            point_name = self.pointUI.pointList[point_index].LECarrer.text().split(" (")[0] + ' ' + self.pointUI.pointList[point_index].LENumero.text()

            if (i < len(self.ruta.legs) or ( self.ruta.routeType and self.ruta.roundtrip and i == len(self.ruta.legs))):
                point_duration = self.ruta.legs[i]["duration"]
                point_distance = self.ruta.legs[i]["distance"]
            else:
                point_duration = -1
                point_distance = -1

            waypoint_label = QLabel(point_name)
            waypoint_label.setFont(QFont("Times",10,weight=QFont.Bold))
            routeResult_scrollable_layout.addWidget(waypoint_label)

            if (point_duration > -1):
                waypoint_distduration = QLabel(str(int(point_duration/60)) + " min (" +  "{:.2f}".format(point_distance/1000) + " km)")
                waypoint_distduration.setAlignment(Qt.AlignRight)

                routeResult_scrollable_layout.addWidget(waypoint_distduration)
        
        #afegir al layout l'scrollable dels punts
        routeResult_layout.addWidget(routeResult_scrollable)

        #DEFINICIÓ DE ZONA DE BOTONS
        buttons_layout = QHBoxLayout()
        routeResult_layout.addLayout(buttons_layout)
        #botó de tornar a la pantalla de planificació de ruta
        routeOptions = QPushButton("Planificació de ruta")
        routeOptions.clicked.connect(lambda:self.switchScreen(container))
        buttons_layout.addWidget(routeOptions)

        #exportació de rutes en format kmx
        routeExport = QPushButton("Exportar ruta")
        routeExport.clicked.connect(self.exportRoute)
        buttons_layout.addWidget(routeExport)

        #canviar el layout del window als resultats de la ruta
        routeResult.addWidget(routeResult_groupbox)
        self.layout().addWidget(container)
        self.layout().setCurrentIndex(1)

    #passar de pantalla de preparació de ruta a resultats de ruta
    def switchScreen(self,container):
        self.layout().setCurrentIndex(0)
        self.layout().removeWidget(container)
        
    #preparació UI pantalla preparació
    def setUI_RoutePlanning(self):
        #creació del layout principal
        self.routeOptionsLayout = QVBoxLayout()

        #opcions de ruta. a peu, en bicicleta o en vehicle motoritzat.
        transportMode_groupbox = QGroupBox("Mode de desplaçament")
        transportMode_layout = QHBoxLayout()
        transportMode_groupbox.setLayout(transportMode_layout)
        transportMode_walk = QRadioButton("A peu")
        transportMode_walk.clicked.connect(lambda:self.setTransportationMode("walk"))
        transportMode_bike = QRadioButton("En bicicleta")
        transportMode_bike.clicked.connect(lambda:self.setTransportationMode("bike"))
        transportMode_vehicle = QRadioButton("En cotxe")
        transportMode_vehicle.clicked.connect(lambda:self.setTransportationMode("vehicle"))
        transportMode_vehicle.setChecked(True)
        transportMode_layout.addWidget(transportMode_walk)
        transportMode_layout.addWidget(transportMode_bike)
        transportMode_layout.addWidget(transportMode_vehicle)

        #tipus de ruta. trip o route
        typeofRoute_groupbox = QGroupBox("Tipus de ruta")
        typeofRoute_layout = QHBoxLayout()
        typeofRoute_groupbox.setLayout(typeofRoute_layout)
        typeofRoute_radiobutton_route = QRadioButton("Ruta seqüencial")
        typeofRoute_radiobutton_route.setToolTip("La ruta calculada serà la ruta més ràpida que passi per tots els punts, respectant l'ordre introduït per l'usuari.")
        typeofRoute_radiobutton_trip = QRadioButton("Ruta òptima")
        typeofRoute_radiobutton_trip.setToolTip("La ruta calculada serà una aproximació a la ruta més ràpida que passi per tots els punts sense ordenar")
        typeofRoute_radiobutton_route.clicked.connect(lambda:self.setRouteType(False))
        typeofRoute_radiobutton_trip.clicked.connect(lambda:self.setRouteType(True))
        typeofRoute_radiobutton_trip.setChecked(True)
        typeofRoute_layout.addWidget(typeofRoute_radiobutton_route)
        typeofRoute_layout.addWidget(typeofRoute_radiobutton_trip)

        #configuració de ruta tipus trip
        self.tripOptions_groupbox = QGroupBox("Opcions de ruta òptima")
        tripOptions_layout = QHBoxLayout()
        self.tripOptions_groupbox.setLayout(tripOptions_layout)
        self.tripOptions_circular = QCheckBox("Ruta circular")
        self.tripOptions_circular.stateChanged.connect(lambda:self.setRouteOptions_roundtrip(self.tripOptions_circular.isChecked()))
        self.tripOptions_puntinici = QCheckBox("Punt de sortida fixat")
        self.tripOptions_puntinici.setToolTip("El primer punt de la llista serà el punt de sortida de la ruta")
        self.tripOptions_puntinici.stateChanged.connect(lambda:self.setRouteOptions_source(self.tripOptions_puntinici.isChecked()))
        self.tripOptions_puntfinal = QCheckBox("Punt d'arribada fixat")
        self.tripOptions_puntfinal.setToolTip("L'últim punt de la llista serà el punt de sortida de la ruta")
        self.tripOptions_puntfinal.stateChanged.connect(lambda:self.setRouteOptions_destination(self.tripOptions_puntfinal.isChecked()))
        tripOptions_layout.addWidget(self.tripOptions_circular)
        tripOptions_layout.addWidget(self.tripOptions_puntinici)
        tripOptions_layout.addWidget(self.tripOptions_puntfinal)
        self.tripOptions_circular.setChecked(False)
        self.tripOptions_puntinici.setEnabled(False)
        self.tripOptions_puntinici.setChecked(True)
        self.tripOptions_puntfinal.setEnabled(False)
        self.tripOptions_puntfinal.setChecked(True)

        #configuració del layout
        self.routeOptionsLayout.addWidget(transportMode_groupbox)
        self.routeOptionsLayout.addWidget(typeofRoute_groupbox)
        self.routeOptionsLayout.addWidget(self.tripOptions_groupbox)
                
    def __init__(self, pare):
        QWidget.__init__(self)

        if isinstance(pare, QgsMapCanvas):
            self.canvas = pare
        else: 
            self.canvas = pare.canvas
        
        #layout de la finestra. es defineix un QStackedLayout per permetre que la finestra tingui difernets layouts (calcul de ruta i resultats de ruta)
        #el contenidor és una espècie de wrapper d'un layout per a que es pugui afegir al stacked layout.


        windowStack = QStackedLayout()
        self.setLayout(windowStack)
        container = QWidget()
        windowStack.addWidget(container)
        self.calcRouteLayout = QVBoxLayout(container)


        #definició del layout de llistat de punts
        points_groupbox = QGroupBox("Llistat de punts")
        self.pointLayout = QVBoxLayout()
        points_groupbox.setLayout(self.pointLayout)
        self.pointUI = PointUI(self.pointLayout,self) 
        self.setUI_RoutePlanning() #crida a funció que crea els QLineEdits

        #afegir layouts de'opcions de ruta
        self.calcRouteLayout.addLayout(self.routeOptionsLayout)
        #afegir layout de llistat de punts
        self.calcRouteLayout.addWidget(points_groupbox)

        #botons
        calcRouteButton = QPushButton()
        calcRouteButton.pressed.connect(self.calcularRuta)
        calcRouteButton.setText("Calcular ruta")
        self.calcRouteLayout.addWidget(calcRouteButton)

        #definir el tool de l'eina
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

    # def initMarkers(self):
    #     self.mStart = QgsVertexMarker(self.canvas)
    #     self.mStart.setColor(QColor(255, 0, 0)) #(R,G,B)
    #     self.mStart.setIconSize(12)
    #     self.mStart.setIconType(QgsVertexMarker.ICON_CROSS)
    #     self.mStart.setPenWidth(3)

    #     self.mEnd = QgsVertexMarker(self.canvas)
    #     self.mEnd.setColor(QColor(0, 0, 255)) #(R,G,B)
    #     self.mEnd.setIconSize(12)
    #     self.mEnd.setIconType(QgsVertexMarker.ICON_CROSS)
    #     self.mEnd.setPenWidth(3)

    def hideEvent(self,event):
        super().hideEvent(event)
        self.canvas.unsetMapTool(self.tool)
        self.ruta.hideRoute()
        self.pointUI.hideMarkers()

    def showEvent(self,event):
        super().showEvent(event)
        self.getPoint = 0
        self.pointUI.resetUI()
        # self.resize(self.minimumSizeHint())

if __name__ == "__main__":
    from qgis.gui import  QgsLayerTreeMapCanvasBridge
    from moduls.QvLlegenda import QvLlegenda
    from qgis.gui import QgsMapCanvas
    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp

    projecteInicial = 'MapesOffline/qVista default map.qgs'

    with qgisapp() as app:
        win = QMainWindow()
        # canvas = QvCanvas(llistaBotons=llistaBotons, posicioBotonera = 'SE', botoneraHoritzontal = True)
        canvas = QgsMapCanvas()
        win.setCentralWidget(canvas)
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root,canvas)

        # leyenda = QvLlegenda(canvas, tablaAtributos)
        qvEinaRuta = EinaMultiruta(canvas)
        dwEC = QDockWidget()
        dwEC.setWidget(qvEinaRuta)
        win.addDockWidget(Qt.LeftDockWidgetArea, dwEC)
        win.show()
        project.read(projecteInicial)      
            
            