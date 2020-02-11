from moduls.QvImports import *
from moduls.QvAtributs import QvFitxesAtributs
from moduls.QvConstants import QvConstants
import math
from PyQt5 import QtGui
from qgis.utils import iface

# from qgis.core import QgsFeatureRequest, QgsPointXY, QgsGeometry, QgsRectangle
# from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMapToolZoom, QgsMapToolPan, QgsRubberBand, QgsAttributeDialog
# from qgis.PyQt.QtWidgets import QMessageBox


class QvSeleccioPunt(QgsMapTool):
    def __init__(self, qV, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.qV = qV

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        layer = self.qV.llegenda.currentLayer()
        # layerList = QgsMapLayerRegistry.instance().mapLayersByName("Illes")
        # if layerList: 
        #     layer = layerList[0]
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        radius = 10
        rect = QgsRectangle(point.x() - radius, point.y() - radius, point.x() + radius, point.y() + radius)
        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))
            ids = [i.id() for i in it]
            self.qV.idsElementsSeleccionats.extend(ids)
            try:
                layer.selectByIds(self.qV.idsElementsSeleccionats)
                nombreElements = len(set(self.qV.idsElementsSeleccionats))
                
                self.qV.lblNombreElementsSeleccionats.setText('Elements seleccionats: '+str(nombreElements))
                self.qV.calcularSeleccio()
            except:
                pass
        else:
          self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

    def activate(self): #???
        pass

    def deactivate(self): #???
        pass

    def isZoomTool(self): #???
        return False

    def isTransient(self): #???
        return False

    def isEditTool(self): #???
        return True

    def missatgeCaixa(self, textTitol,textInformacio):
        msgBox=QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        ret = msgBox.exec()

class QvSeleccioCercle(QgsMapTool):
    """ Dibuixa un cercle i selecciona els elements."""
    def __init__(self, qV, color, radi, numeroSegmentsCercle):
        self.canvas = qV.canvas
        QgsMapTool.__init__(self, self.canvas)
        self.qV = qV
        self.status = 0
        self.numeroSegmentsCercle = numeroSegmentsCercle

        self.rubberband=QgsRubberBand(self.canvas,True)
        self.rubberband.setColor( QColor("red") )
        self.rubberband.setWidth( 2 )
        self.overlap = False
        
    def setOverlap(self,overlap):
        self.overlap = overlap

    def canvasPressEvent(self,e):
        if not e.button() == Qt.LeftButton:
            return
        self.status = 1
        self.centre = self.toMapCoordinates(e.pos())

        # self.rbcircle(self.rb, self.centre, self.centre, self.numeroSegmentsCercle)
        return

    def canvasMoveEvent(self,e):
        if not self.status == 1:
                return
        cp = self.toMapCoordinates(e.pos())
        self.rbcircle(self.rubberband, self.centre, cp, self.numeroSegmentsCercle)
        r = math.sqrt(self.centre.sqrDist(cp))

        self.rubberband.show()
  

    def rbcircle(self, rb,center,edgePoint,segments):
        r = math.sqrt(center.sqrDist(edgePoint))
        rb.reset( True )
        pi =3.1416
        llistaPunts=[]
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            rb.addPoint(QgsPointXY(center.x()+r*math.cos(theta),center.y()+r*math.sin(theta)))
            llistaPunts.append(QgsPointXY(center.x()+r*math.cos(theta),center.y()+r*math.sin(theta)))
        self.poligono=QgsGeometry.fromPolygonXY([llistaPunts])
        return

    def canvasReleaseEvent(self,e):
        if not e.button() == Qt.LeftButton:
            return
        layer = self.qV.llegenda.currentLayer()
        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            #convertir rubberband apoligon
            featsPnt = layer.getFeatures(QgsFeatureRequest().setFilterRect(self.poligono.boundingBox()))
            for featPnt in featsPnt:
                
                if self.qV.checkOverlap.checkState():
                    if featPnt.geometry().intersects(self.poligono):
                        layer.select(featPnt.id())
                        self.qV.idsElementsSeleccionats.append(featPnt.id())
                else:
                    if featPnt.geometry().within(self.poligono):
                        layer.select(featPnt.id())
                        self.qV.idsElementsSeleccionats.append(featPnt.id())
            
            self.qV.calcularSeleccio()
            # self.emit( SIGNAL("selectionDone()") )
            self.status = 0
            self.qV.lblNombreElementsSeleccionats.setText('Elements seleccionats: '+str(len(set(self.qV.idsElementsSeleccionats))))
        else: 
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

    def reset(self):
        self.status = 0
        self.rb.reset( True )

    def deactivate(self):
        QgsMapTool.deactivate(self)
        # self.emit(SIGNAL("deactivated()"))
    
    def missatgeCaixa(self,textTitol,textInformacio):
        msgBox=QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        ret = msgBox.exec()



class QvSeleccioPerPoligon(QgsMapToolEmitPoint):
    def __init__(self, qV, canvas, layer):
        self.canvas = canvas
        self.layer = layer
        self.qV = qV
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberband = QgsRubberBand(self.canvas)
        self.rubberband.setColor(QColor(0,0,0,50))
        self.rubberband.setWidth(4)
        self.point = None
        self.points = []
        self.overlap = False

    def setOverlap(self,overlap):
        """
        overlap = True: Selecció amb overlap | False: Selecció sense overlap
        Es a dir, si overlap es True, es suficient amb que un apart del element estigui dins del poligon per ser seleccionat.
        """
        self.overlap = overlap

    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        
        self.points.append(QgsPointXY(self.point))
        self.selectPoly()

    def selectPoly(self):
        if self.layer.type() != QgsMapLayer.VectorLayer:
            return
        listaPoligonos=[self.points]
        poligono=QgsGeometry.fromPolygonXY(listaPoligonos)
        self.rubberband.setToGeometry(poligono,self.layer)
        self.rubberband.show()
        if (len(self.points) > 1):
            # g = self.rubberband.asGeometry()
            # self.layer.removeSelection()
            featsPnt = self.layer.getFeatures(QgsFeatureRequest().setFilterRect(poligono.boundingBox()))
            for featPnt in featsPnt:
                if self.overlap:
                    if featPnt.geometry().intersects(poligono):
                        self.layer.select(featPnt.id())
                        self.qV.idsElementsSeleccionats.append(featPnt.id())
                else:
                    if featPnt.geometry().within(poligono):
                        self.layer.select(featPnt.id())
                        self.qV.idsElementsSeleccionats.append(featPnt.id())
            
            self.qV.calcularSeleccio()
            

            self.qV.lblNombreElementsSeleccionats.setText('Elements seleccionats: '+str(len(set(self.qV.idsElementsSeleccionats))))

class QvMesuraMultiLinia(QgsMapTool):
    def __init__(self, qV, canvas, layer):
        self.canvas = canvas
        self.layer = layer
        self.qV = qV
        #dock = QgsAdvancedDigitizingDockWidget(self.canvas)
        #QgsMapToolAdvancedDigitizing.__init__(self, self.canvas, dock)
        QgsMapTool.__init__(self, self.canvas)
        self.rubberband = self.creaRubberband()
        #self.rubberband.setIconType(QgsVertexMarker.ICON_CIRCLE)

        self.rubberband2 = self.creaRubberband()

        self.rubberbandCercle=self.creaRubberband(cercle=True)

        self.rubberbands=[]
        self.cercles=[]

        self.point = None
        self.lastPoint = None
        self.points = []
        self.overlap = False
        self.markers = []
        self.startMarker = None
        self.startPoint = None
        self.lastLine = None
        self.hoverSartMarker = None

        self.qV.wMesuraGrafica.clear()

        self.qV.wMesuraGrafica.colorCanviat.connect(self.canviColor)

        # self.qV.lwMesuresHist.clear()
    def canviColor(self,color):
        #De moment conservem el color del que ja teníem dibuixat
        #Si més endavant es vol modificar només cal descomentar les línies inferiors
        # for x in self.rubberbands:
        #     x.setColor(color)
        # for x in self.cercles:
        #     x.setColor(color)
        self.rubberband.setColor(color)
        self.rubberband2.setColor(color)
        self.rubberbandCercle.setColor(color)
    def setOverlap(self,overlap):
        self.overlap = overlap

    def qpointsDistance(self, p, q):
        dx = p.x() - q.x()     
        dy = p.y() - q.y()     
        dist = math.sqrt( dx*dx + dy*dy )
        return dist

    def canvasDoubleClickEvent(self, e):
        #Tancar polígon (de moment no es fa)
        pass
        # self.tancarPoligon()
    
    def canvasMoveEvent(self, e):
        self.lastPoint = self.toMapCoordinates(e.pos())
        startPos = None

        if self.point is not None:
            startPos = self.toCanvasCoordinates(self.startPoint)
            distance = self.qpointsDistance(e.pos(), startPos)
            if distance < 9:
                if len(self.points) > 2:
                    self.hoverSartMarker = True
                    self.startMarker.mouseMoveOver()
                    self.showlastLine(self.startPoint)
                else:
                    self.hoverSartMarker = False
                    self.showlastLine()
            else:
                self.hoverSartMarker = False
                self.startMarker.mouseOverRelease()
                self.showlastLine()


        #if self.point != None:
    def treuUltimtram(self):
        poligono=QgsGeometry.fromPolylineXY(self.points)
        distancia = poligono.length()
        if self.point is None:
            return False
        self.point = None
        self.points = []
        self.hoverSartMarker = False
        
        self.rubberband2.hide()
        self.rubberbandCercle.hide()

        self.qV.wMesuraGrafica.setDistanciaTotal(distancia)
        self.qV.wMesuraGrafica.actualitzaHistorial()
        self.qV.wMesuraGrafica.setDistanciaTempsReal(0)
        self.qV.wMesuraGrafica.setDistanciaTotal(0)
        self.qV.wMesuraGrafica.setArea(0)
        # self.qV.lblDistanciaTempsReal.setText('Distáncia últim tram: 0 m')       
        return True
    def novaRubberband(self):
        self.rubberbands.append(self.rubberband)
        self.rubberband=None
        self.rubberband=self.creaRubberband()
    def creaRubberband(self,cercle=False): 
        rubberband=QgsRubberBand(self.canvas)
        rubberband.setColor(self.qV.wMesuraGrafica.color)
        if cercle:
            rubberband.setWidth(0.25)
            rubberband.setLineStyle(Qt.DashLine)
        else:
            rubberband.setWidth(2)
        rubberband.setIconSize(4)
        return rubberband
    def rbcircle(self, center,edgePoint,desar=False,segments=100):
        r = math.sqrt(center.sqrDist(edgePoint))
        self.rubberbandCercle.reset( True )
        if not self.qV.wMesuraGrafica.cbCercles.isChecked():
            return
        pi =3.1416
        llistaPunts=[]
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            self.rubberbandCercle.addPoint(QgsPointXY(center.x()+r*math.cos(theta),center.y()+r*math.sin(theta)))
            llistaPunts.append(QgsPointXY(center.x()+r*math.cos(theta),center.y()+r*math.sin(theta)))
        self.poligono=QgsGeometry.fromPolygonXY([llistaPunts])
        if desar:
            self.cercles.append(self.rubberbandCercle)
            self.rubberbandCercle=self.creaRubberband(cercle=True)
            # self.cercles.append(QgsRubberBand(rb))
    def canvasPressEvent(self, e):
                
        
        if e.button() == Qt.RightButton:
            if not self.treuUltimtram():
                # self.qV.wMesuraGrafica.tancar()
                self.qV.dwMesuraGrafica.hide()
                # self.canvas.unsetMapTool()
            
        else:
            if self.hoverSartMarker:
                self.rbcircle(self.point,self.startPoint, desar=True)
                self.point = self.startPoint
                self.points.append(QgsPointXY(self.point))
                self.tancarPoligon()

            else:
                pointOld=self.point
                self.point = self.toMapCoordinates(e.pos())
                if pointOld is not None: self.rbcircle(pointOld,self.point, desar=True)
                self.points.append(QgsPointXY(self.point))
                
                self.selectPoly(e)
                self.qV.wMesuraGrafica.setArea(None)
                


    def tancarPoligon(self):
        try:
            
            point = QPointF()
            # create  float polygon --> construcet out of 'point'
            list_polygon = QPolygonF()

            for x in self.points:
                # since there is no distinction between x and y values we only want every second value 
                    list_polygon.append(x.toQPointF())
            
            geomP = QgsGeometry.fromQPolygonF(list_polygon)
            
            poligono = QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(poligono,self.layer)
            self.rubberband.show()
            self.novaRubberband()

            distancia = geomP.length()
            area = geomP.area()

            self.qV.wMesuraGrafica.setDistanciaTotal(distancia)
            self.qV.wMesuraGrafica.setArea(area)

            # self.qV.lwMesuresHist.addItem(str(round(self.lastLine.length(),2)))
            # self.qV.lblDistanciaTotal.setText('Distància total: ' + str(round(distancia,2)) + ' m')
            # self.qV.lblMesuraArea.setText('Àrea: ' + str(round(area,2)) + ' m²')

            self.point = None
            self.points = []
            self.hoverSartMarker = False
            
            self.rubberband2.hide()
            self.qV.wMesuraGrafica.actualitzaHistorial()
            # self.treuUltimtram()

        except Exception as e:
            #error tancant el polígon
            pass
            # print('Error al tancar el polygon')
            # print(e.__str__)

    def selectPoly(self, e):
        try:

            firstMarker = False
            poligono=QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(poligono,self.layer)
            self.rubberband.show()
            distancia = poligono.length()
            if distancia <= 0:
                distancia = 0
                self.qV.wMesuraGrafica.clear()
                #

                # self.qV.lwMesuresHist.clear()
                # self.qV.lblMesuraArea.setText('Àrea: ')
                firstMarker = True

                for ver in self.markers:
                    self.canvas.scene().removeItem(ver)

                self.markers = []
            self.qV.wMesuraGrafica.setDistanciaTotal(distancia)
            # self.qV.lblDistanciaTotal.setText('Distància total: ' + str(round(distancia,2)) + ' m')
            
            if distancia > 0 and (self.lastLine is not None and round(self.lastLine.length(),2) > 0):
                """
                rowPosition = self.qV.twResultatsMesura.rowCount()
                self.qV.twResultatsMesura.insertRow(rowPosition)
                self.qV.twResultatsMesura.setItem(rowPosition , 0, QTableWidgetItem(str(round(distancia,2))))
                """
                self.qV.wMesuraGrafica.setDistanciaTempsReal(0)
                self.qV.wMesuraGrafica.setDistanciaTotal(distancia)
                # self.qV.lwMesuresHist.addItem(str(round(self.lastLine.length(),2)))
                # self.qV.lblDistanciaTempsReal.setText('Distáncia últim tram: 0 m')

                self.lastLine = QgsGeometry.fromPolylineXY([self.lastPoint, self.lastPoint])

            m = QvMarcador(self.canvas)

            m.setColor(QColor(36,97,50))
            m.setFillColor(QColor(36,97,50))
            m.setIconSize(9)
            m.setIconType(QvMarcador.ICON_CIRCLE)
            m.setPenWidth(5)

            m.setCenter(QgsPointXY(self.point))

            if firstMarker:
                self.startMarker = m
                self.startPoint = QgsPointXY(self.point)

                #point = QgsPoint(self.canvas.getCoordinateTransform().toMapCoordinates(x, y))

            self.markers.append(m)
            self.novaRubberband()
            
        except Exception as e:
            #Error mesurant
            pass
            # print('ERROR. Error al mesurar ')
        
    
    def showlastLine(self, snapingPoint = None):
        if snapingPoint is None:
            listaPoligonos=[self.point, self.lastPoint]
        else:
            listaPoligonos=[self.point, snapingPoint]
        self.lastLine = QgsGeometry.fromPolylineXY(listaPoligonos)
        self.rubberband2.setToGeometry(self.lastLine,self.layer)
        self.rubberband2.show()
        self.rbcircle(self.point,self.lastPoint)
        distancia = self.lastLine.length()
        if distancia <= 0:
            distancia = 0
        poligono=QgsGeometry.fromPolylineXY(self.points)
        if poligono.isGeosValid():
            distTotal=poligono.length()
        else:
            distTotal=0
        self.qV.wMesuraGrafica.setDistanciaTempsReal(distancia)
        self.qV.wMesuraGrafica.setDistanciaTotal(distTotal+distancia)
        # self.qV.lblDistanciaTempsReal.setText('Distáncia últim tram: ' + str(round(distancia,2)) + ' m')
        
class QvMarcador (QgsVertexMarker):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsVertexMarker.__init__(self, self.canvas)

    def mouseMoveOver(self):
        self.setColor(QColor(199, 239, 61))
        self.setFillColor(QColor(199, 239, 61))


    def mouseOverRelease(self):
        self.setColor(QColor(36,97,50))
        self.setFillColor(QColor(36,97,50))


class QvSeleccioElement(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat. 

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
    """

    def __init__(self, canvas, llegenda, radi = 4):
        """[summary]
        
        Arguments:
            canvas {[QgsMapCanvas]} -- [El canvas de la app]
            llegenda {QvLlegenda} -- La llegenda de la app
        
        Keyword Arguments:
            radi {int} -- [El radi de tolerancia de la seleccio] (default: {20})
        """

        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.llegenda = llegenda
        self.radi = radi
        self.fitxaAtributs = None

    def keyPressEvent(self, event):
        """ Defineix les actuacions del QvMapeta en funció de la tecla apretada.
        """
        if event.key() == Qt.Key_Escape:
            pass
        #     if self.pare is not None:
        #         self.pare.esborrarSeleccio(tambePanCanvas = False)
        # self.tool.fitxaAtributs.close()


    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass
        # x = event.pos().x()
        # y = event.pos().y()
        # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def missatgeCaixa(self,textTitol,textInformacio):
        msgBox=QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        ret = msgBox.exec()

    def heCerradoFicha(self): #???
        bb= self.parent()
        
        bb.pare.esborrarSeleccio(tambePanCanvas = False)



    def canvasReleaseEvent(self, event):
        # print("CANVAS RELEASE")
        if self.fitxaAtributs is not None:
            self.fitxaAtributs.accept()
            self.fitxaAtributs = None
        # Lllegim posició del mouse
        x = event.pos().x()-1
        y = event.pos().y()-8
        try:
            layer = self.llegenda.currentLayer()
            if layer is None:
                layer = self.canvas.layers()[0]

            # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            if self.canvas.rotation()==0:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi, y-self.radi)
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi, y+self.radi)
            else:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi*sqrt(2), y-self.radi*sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*sqrt(2), y-self.radi*sqrt(2))

            # marcaLloc = QgsVertexMarker(self.canvas)
            # marcaLloc.setCenter( point )
            # marcaLloc.setColor(QColor(255, 0, 0))
            # marcaLloc.setIconSize(15)
            # marcaLloc.setIconType(QgsVertexMarker.ICON_CROSS) # or ICON_CROSS, ICON_X
            # marcaLloc.setPenWidth(0)
            # marcaLloc.show()
            # return

            # rect = QgsRectangle(point.x() - self.radi, point.y() - self.radi, point.x() + self.radi, point.y() + self.radi)
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())
            # ids=[]
            features=[]
            if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
                it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))

                for feature in it:       
                    # ids.append(feature.id())
                    features.append(feature)

                # ids = [i.id() for i in it]
                # layer.selectByIds(ids)
                if len(features) > 0:
                    self.fitxaAtributs = QvFitxesAtributs(layer, features)
                    self.fitxaAtributs.exec_()
                    self.fitxaAtributs = None

            else:
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
        except Exception as e:
            print(str(e))
       
        # modelIndex = self.currentIndex()
        # if modelIndex is not None and modelIndex.isValid():
        #     self.feature = self.model.feature(modelIndex)
        #     if self.feature is not None and self.feature.isValid():
        #         dialog = QgsAttributeDialog(self.layer, self.feature, False) # , self)
        #         # dialog = QgsAttributeForm(self.layer, self.feature)
        #         if filtre:
        #             dialog.setWindowTitle(self.layer.name() + ' - Filtres')
        #             dialog.setMode(QgsAttributeForm.SearchMode)
        #         else:
        #             dialog.setWindowTitle(self.layer.name() + ' - Element ' + str(self.feature.id() + 1))
        #             dialog.setMode(QgsAttributeForm.SingleEditMode)

if __name__ == "__main__":    
    from qgis.gui import  QgsLayerTreeMapCanvasBridge
    from moduls.QvLlegenda import QvLlegenda
    from qgis.gui import QgsMapCanvas
    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp
    with qgisapp() as app:
        canvas = QgsMapCanvas()

        project = QgsProject.instance()
        projecteInicial='D:/qVista/Dades/Projectes/BCN11_nord.qgs'
        project.read(projecteInicial)
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        
        llegenda = QvLlegenda()
        llegenda.show()
        canvas.show()
        tool =  QvSeleccioElement(canvas, llegenda)
        canvas.setMapTool(tool)


 