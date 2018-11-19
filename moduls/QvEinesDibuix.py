from qgis.gui import (
                    QgsMapTool, 
                    QgsMapToolEmitPoint, 
                    QgsMapCanvas, 
                    QgsRubberBand, 
                    QgsVertexMarker, 
                    QgsLayerTreeMapCanvasBridge,
                    QgsAttributeTableModel,
                    QgsAttributeTableView,
                    QgsAttributeTableFilterModel
                    )
                    
class PointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

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
        print (x,y)
        layer = qV.llegenda.view.currentLayer()
        # layerList = QgsMapLayerRegistry.instance().mapLayersByName("Illes")
        # if layerList: 
        #     layer = layerList[0]
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        radius = 20
        rect = QgsRectangle(point.x() - radius, point.y() - radius, point.x() + radius, point.y() + radius)
        if layer:
          it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))
          ids = [i.id() for i in it]
          layer.selectByIds(ids)
          taulaAtributs('Seleccionats',layer)
        else:
          missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class SelectMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, lyr):
        self.canvas = canvas
        self.lyr = lyr
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        qV.rubberband = QgsRubberBand(self.canvas)
        
        qV.rubberband.setColor(QtGui.QColor(0,0,0,50))
        qV.rubberband.setWidth(4)
        self.point = None
        self.points = []
    def canvasPressEvent(self, e):
        self.point = self.toMapCoordinates(e.pos())
        # qV.markers = QgsVertexMarker(self.canvas)
        # qV.markers.setCenter(self.point)
        # qV.markers.setColor(QtGui.QColor(0,255,0))
        # qV.markers.setIconSize(5)
        # qV.markers.setIconType(QgsVertexMarker.ICON_BOX)
        # qV.markers.setPenWidth(3)
        self.points.append(QgsPointXY(self.point))
        self.isEmittingPoint = True
        self.selectPoly()

    def selectPoly(self):
        listaPoligonos=[self.points]
        poligono=QgsGeometry.fromPolygonXY(listaPoligonos)
        qV.rubberband.setToGeometry(poligono,self.lyr)
        qV.rubberband.show()
        if (len(self.points) > 1):
          # g = self.rubberband.asGeometry()
          self.lyr.removeSelection()
          featsPnt = self.lyr.getFeatures(QgsFeatureRequest().setFilterRect(poligono.boundingBox()))
          for featPnt in featsPnt:
            if 66==qV.tecla:
              if featPnt.geometry().intersects(poligono):
                self.lyr.select(featPnt.id())
            else:
              if featPnt.geometry().within(poligono):
               self.lyr.select(featPnt.id())
