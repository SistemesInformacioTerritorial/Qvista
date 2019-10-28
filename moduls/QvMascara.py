from moduls.QvImports import *
from moduls.QvConstants import QvConstants
from qgis.gui import QgsMapTool, QgsRubberBand
import math


class QvMascaraEinaPlantilla(QgsMapTool):
    def __init__(self, qV, canvas, color=QvConstants.COLORDESTACAT, opacitat=0.5):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.qV = qV
        self.color=color
        self.opacitat=opacitat

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
    def qpointsDistance(self, p, q):
        dx = p.x() - q.x()     
        dy = p.y() - q.y()     
        dist = math.sqrt( dx*dx + dy*dy )
        return dist
    def missatgeCaixa(self, textTitol,textInformacio):
        msgBox=QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        ret = msgBox.exec()
    def getCapa(self):
        if hasattr(self,'mascara'):
            return self.mascara
        mascares=self.qV.project.mapLayersByName('Màscares')
        if len(mascares)==0:
            self.mascara=QgsVectorLayer('Polygon?crs=epsg:25831','Màscares','memory')
            self.mascara.renderer().symbol().setColor(self.color)
            self.mascara.setRenderer(QgsInvertedPolygonRenderer.convertFromRenderer(self.mascara.renderer()))
            self.mascara.setOpacity(self.opacitat)
        elif len(mascares)==1:
            self.mascara=mascares[0]
        else:
            print(':(')
            self.mascara=mascares[0]
        return self.mascara
    def actualitza(self):
        self.mascara.updateExtents()
        self.qV.project.addMapLayers([self.mascara])
        self.canvas.refreshAllLayers()
        

#Copiat del QvSeleccioPunt de QvEinesGrafiques.py i adaptat a les nostres necessitats
class QvMascaraEinaClick(QvMascaraEinaPlantilla):

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
            it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect)) #items seleccionats
            items=[i for i in it] #Ens guardem una llista dels items seleccionats
            ids = [i.id() for i in items]
            if len(ids)==0:
                # self.missatgeCaixa('Perdoneu, no he entès quin element volíeu seleccionar','Intenteu ser més precisos fent-hi click')
                return
            try:
                # layer.selectByIds(ids)
                # geom=items[0].geometry()
                mascara=self.getCapa()
                pr=mascara.dataProvider()
                polys=[]
                for x in items:
                    geom=x.geometry()
                    poly=QgsFeature()
                    poly.setGeometry(geom)
                    polys.append(poly)
                pr.addFeatures(polys)
                # mascara.renderer().symbol().setOpacity(self.opacitat)
                self.actualitza()
                

                
                # self.rubberband=QgsRubberBand(self.canvas)
                # self.rubberband.setColor(QColor(255,98,21,50))
                # self.rubberband.setWidth(4)
                # self.rubberband.setToGeometry(geom,mascara)
                print(':D')
            except Exception as e:
                print(e)
                pass
        else:
          self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

    # def activate(self): #???
    #     pass

    # def deactivate(self): #???
    #     pass

    # def isZoomTool(self): #???
    #     return False

    # def isTransient(self): #???
    #     return False

    # def isEditTool(self): #???
    #     return True

class QvMascaraEinaDibuixa(QvMascaraEinaPlantilla):

    def __init__(self,qV, canvas, color=QvConstants.COLORDESTACAT, opacitat=0.5):
        super().__init__(qV,canvas,color,opacitat)
        self.points=[]
        self.rubberband=self.novaRubberband()
    def novaRubberband(self):
        rb=QgsRubberBand(self.canvas,True)
        rb.setColor(self.color)
        rb.setWidth(2)
        return rb

    def canvasPressEvent(self,event):
        if event.button()==Qt.RightButton:
            #Tancar polígon??
            return
        self.point=self.toMapCoordinates(event.pos())
        self.points.append(QgsPointXY(self.point))
        self.selectPoly(event)
        if self.qpointsDistance(self.points[0],self.point)<10 and len(self.points)>2:
            self.tancarPoligon()
    def tancarPoligon(self):
        try:
            list_polygon = []
            mascara=self.getCapa()
            pr=mascara.dataProvider()
            self.points=self.points[:-1]
            for x in self.points:
                list_polygon.append(QgsPointXY(x))
            geom = QgsGeometry.fromPolygonXY([list_polygon])
            poly=QgsFeature()
            poly.setGeometry(geom)
            print(geom)
            pr.addFeatures([poly])
            self.rubberband.hide()
            self.rubberband=self.novaRubberband()
            self.actualitza()
            self.point=None
            self.points=[]
        except Exception as e:
            print(e)
    
    def selectPoly(self, e):
        try:

            firstMarker = False
            poligono=QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(poligono,self.getCapa()) #falta establir la layer
            self.rubberband.show()
            print(':D')
            
            # m = QvMarcador(self.canvas)

            # m.setColor(QColor(36,97,50))
            # m.setFillColor(QColor(36,97,50))
            # m.setIconSize(9)
            # m.setIconType(QvMarcador.ICON_CIRCLE)
            # m.setPenWidth(5)

            # m.setCenter(QgsPointXY(self.point))

            # if firstMarker:
            #     self.startMarker = m
            #     self.startPoint = QgsPointXY(self.point)

            #     #point = QgsPoint(self.canvas.getCoordinateTransform().toMapCoordinates(x, y))

            # self.markers.append(m)
            # self.novaRubberband()
            
        except Exception as e:
            #Error mesurant
            pass
            # print('ERROR. Error al mesurar ')