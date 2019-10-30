from moduls.QvImports import *
from moduls.QvConstants import QvConstants
from qgis.gui import QgsMapTool, QgsRubberBand
import math


class QvMascaraEinaPlantilla(QgsMapTool):
    def __init__(self, qV, canvas, color=QColor(255,255,255), opacitat=0.70, emmascarar=True, seleccionar=True, overlap=True):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.qV = qV
        self.setColor(color)
        self.setOpacitat(opacitat)
        self.afegida=True
        self.seleccionar=seleccionar
        self.overlap=overlap
        self.emmascarar=emmascarar

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
        if not self.emmascarar:
            layer = self.qV.llegenda.currentLayer()
            if layer is None or layer.type()!=QgsMapLayer.VectorLayer:
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
                return None
            return layer
        mascares=self.qV.project.mapLayersByName('Màscara')
        if len(mascares)==0:
            self.mascara=QgsVectorLayer('Polygon?crs=epsg:25831','Màscara','memory')
            self.mascara.renderer().symbol().setColor(self.color)
            self.mascara.renderer().symbol().symbolLayer(0).setStrokeColor(self.color)
            self.mascara.setRenderer(QgsInvertedPolygonRenderer.convertFromRenderer(self.mascara.renderer()))
            self.mascara.setOpacity(self.opacitat)
            self.afegida=False
        elif len(mascares)==1:
            self.mascara=mascares[0]
        else:
            print(':(')
            self.mascara=mascares[0]
        return self.mascara
    def actualitza(self):
        if self.emmascarar:
            self.mascara.updateExtents()
            # if self.qV.project.mapLayersByName('Màscara') is None:
            if not self.afegida:
                self.qV.project.addMapLayers([self.mascara])
                self.afegida=True
            self.mascara.renderer().embeddedRenderer().symbol().setColor(self.color)
            self.mascara.setOpacity(self.opacitat)
        # self.canvas.refresh()
        self.canvas.refreshAllLayers()
    def setColor(self,color):
        self.color=color
    def setOpacitat(self,opacitat):
        self.opacitat=opacitat
        

#Copiat del QvSeleccioPunt de QvEinesGrafiques.py i adaptat a les nostres necessitats
class QvMascaraEinaClick(QvMascaraEinaPlantilla):

    def __init__(self, qV, canvas, **kwargs):
        layer=qV.llegenda.currentLayer()
        if layer is None or layer.type()!=QgsMapLayer.VectorLayer:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            raise Exception("No hi havia nivell seleccionat") #TODO: Crear una altra excepció més específica
        super().__init__(qV,canvas,**kwargs)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        layer = self.qV.llegenda.currentLayer()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        radius = 10
        rect = QgsRectangle(point.x() - radius, point.y() - radius, point.x() + radius, point.y() + radius)
        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect)) #items seleccionats
            items=[i for i in it] #Ens guardem una llista dels items seleccionats
            ids = [i.id() for i in items]
            if len(ids)==0:
                return
            try:
                if self.emmascarar:
                    mascara=self.getCapa()
                    pr=mascara.dataProvider()
                    polys=[]
                    polysTreure=[]
                    # features=[x.id() for x in mascara.getFeatures(QgsFeatureRequest().setFilterRect(rect))] #Items 
                    for x in items:
                        # if x.id() in features:
                        #     polysTreure.append(x.id)
                        geom=x.geometry()
                        poly=QgsFeature()
                        poly.setGeometry(geom)
                        polys.append(poly)
                    pr.addFeatures(polys)
                if self.seleccionar:
                    seleccionats=layer.selectedFeatureIds()
                    layer.selectByIds(seleccionats+ids)
                #La part d'eliminar funciona màgicament. No existeix cap raó lògica que ens digui que s'eliminarà, però ho fa
                # if not pr.deleteFeatures(polysTreure):
                #     #Ens hauríem de queixar? No? Tractar?
                #     pass
                self.actualitza()
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

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.points=[]
        self.rubberband=self.novaRubberband()
        layer=self.qV.llegenda.currentLayer()
        if layer is None:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció','Podeu emmascarar però no es seleccionaran els elements')
    def novaRubberband(self):
        rb=QgsRubberBand(self.canvas,True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        return rb

    def canvasPressEvent(self,event):
        if event.button()==Qt.RightButton:
            #Tancar polígon??
            return
        self.point=self.toMapCoordinates(event.pos())
        self.points.append(QgsPointXY(self.point))
        if len(self.points)==1:
            self.posB=event.pos()
        self.selectPoly(event)
        if self.qpointsDistance(self.posB,event.pos())<10 and len(self.points)>2:
            self.tancarPoligon()
    def canvasMoveEvent(self,event):
        poligono=QgsGeometry.fromPolylineXY(self.points+[self.toMapCoordinates(event.pos())])
        self.rubberband.setToGeometry(poligono,self.getCapa()) #falta establir la layer
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
            if self.emmascarar:
                pr.addFeatures([poly])

            layer=self.qV.llegenda.currentLayer()
            if self.seleccionar and layer is not None:
                #Seleccionem coses
                featsPnt = layer.getFeatures(QgsFeatureRequest().setFilterRect(geom.boundingBox()))
                for featPnt in featsPnt:
                    if self.overlap:
                        if featPnt.geometry().intersects(geom):
                            layer.select(featPnt.id())
                        pass
                    else:
                        if featPnt.geometry().within(geom):
                            layer.select(featPnt.id())
                        pass
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
            
            
        except Exception as e:
            pass

class QvMascaraEinaCercle(QvMascaraEinaPlantilla):

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.rubberbandRadi=self.novaRubberband()
        self.rubberbandCercle=self.novaRubberband()
        layer=self.qV.llegenda.currentLayer()
        self.centre=None
        if layer is None and self.seleccionar==True:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció','Podeu emmascarar però no es seleccionaran els elements')
    def novaRubberband(self):
        rb=QgsRubberBand(self.canvas,True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        return rb

    def canvasPressEvent(self,event):
        if event.button()==Qt.RightButton:
            #Tancar polígon??
            return
        self.centre=self.toMapCoordinates(event.pos())

    def canvasMoveEvent(self,event):
        if self.centre is not None:
            self.rbcircle(self.centre,self.toMapCoordinates(event.pos()))
            pass
    def canvasReleaseEvent(self,event):
        mascara=self.getCapa()
        pr=mascara.dataProvider()
        poligon,_=self.getPoligon(self.centre,self.toMapCoordinates(event.pos()),100)
        poly=QgsFeature()
        poly.setGeometry(poligon)
        if self.emmascarar:
            pr.addFeatures([poly])

        layer=self.qV.llegenda.currentLayer()
        if self.seleccionar and layer is not None:
            #Seleccionem coses
            featsPnt = layer.getFeatures(QgsFeatureRequest().setFilterRect(poligon.boundingBox()))
            for featPnt in featsPnt:
                if self.overlap:
                    if featPnt.geometry().intersects(poligon):
                        layer.select(featPnt.id())
                    pass
                else:
                    if featPnt.geometry().within(poligon):
                        layer.select(featPnt.id())
                    pass
        self.centre=None
        self.actualitza()

    def rbcircle(self, center,edgePoint,segments=100):
        self.rubberbandCercle.reset( True )
        self.poligon, llistaPunts = self.getPoligon(center,edgePoint,segments)
        for x in llistaPunts:
            self.rubberbandCercle.addPoint(x)
    def getPoligon(self,center,edgePoint,segments):
        r = math.sqrt(center.sqrDist(edgePoint))
        llistaPunts=[]
        pi =3.1416
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            llistaPunts.append(QgsPointXY(center.x()+r*math.cos(theta),center.y()+r*math.sin(theta)))
        return QgsGeometry.fromPolygonXY([llistaPunts]), llistaPunts