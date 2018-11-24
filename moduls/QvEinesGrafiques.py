

from moduls.QvImports import *

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
        # self.markers = QgsVertexMarker(self.canvas)
        # self.markers.setCenter(self.point)
        # self.markers.setColor(QtGui.QColor(0,255,0))q
        # self.markers.setIconSize(5)
        # self.markers.setIconType(QgsVertexMarker.ICON_BOX)
        # self.markers.setPenWidth(3)
        self.points.append(QgsPointXY(self.point))
        self.isEmittingPoint = True
        self.selectPoly()

    def selectPoly(self):
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
            

            self.qV.lblNombreElementsSeleccionats.setText('Elements seleccionats: '+str(len(set(self.qV.idsElementsSeleccionats))))


class QvSeleccioElement(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat. 

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
    """

    def __init__(self, canvas, llegenda, radi = 20):
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

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass
        # x = event.pos().x()
        # y = event.pos().y()
        # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        # Lllegim posició del mouse
        x = event.pos().x()
        y = event.pos().y()
        try:
            layer = self.llegenda.currentLayer()
            if layer is None:
                layer = self.canvas.layers()[0]

            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

            rect = QgsRectangle(point.x() - self.radi, point.y() - self.radi, point.x() + self.radi, point.y() + self.radi)
            ids=[]
            if layer is not None:
                it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))
                for feature in it:
                    self.fitxaAtributs = QgsAttributeDialog(layer, feature, False) 
                    self.fitxaAtributs.show()
                    ids.append(feature.id())

                # ids = [i.id() for i in it]
                layer.selectByIds(ids)
            else:
                missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.','Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
        except:
            pass
       
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
    from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        canvas = QgsMapCanvas()

        project = QgsProject.instance()
        project.read('../dades/projectes/bcn11.qgs')
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)
        
        llegenda = QvLlegenda()
        llegenda.show()
        canvas.show()
        tool = QvSeleccioElement(canvas, llegenda)
        canvas.setMapTool(tool)


 