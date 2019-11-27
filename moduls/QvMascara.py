from moduls.QvImports import *
from moduls.QvConstants import QvConstants
from moduls.QvMemoria import QvMemoria
from qgis.gui import QgsMapTool, QgsRubberBand
import math


class MascaraAux:
    # Una classe per encapsular variables i coses
    teAux = False
    geom = None
    qV = None

# geoms: iterable de QgsGeometry


def aplicaMascara(qV, geoms, mascara=None):
    MascaraAux.qV = qV
    eliminaMascara(qV, False)
    mascara = obteMascara(qV)
    mascaraAux = qV.project.mapLayersByName('Màscara auxiliar')[0]
    if MascaraAux.geom is None:
        primera_feature = next(mascaraAux.getFeatures())
        MascaraAux.geom = primera_feature.geometry()
    for x in geoms:
        MascaraAux.geom = MascaraAux.geom.difference(x)
    feat = QgsFeature()
    feat.setGeometry(MascaraAux.geom)
    pr = mascara.dataProvider()

    pr.addFeatures([feat])
    mascara.commitChanges()
    qV.project.addMapLayers([mascara])
    qV.canvas.refresh()


def obteMascara(qV):
    MascaraAux.qV = qV
    mascares = qV.project.mapLayersByName('Màscara')
    if len(mascares) == 0:
        return creaMascara(qV)
    return mascares[0]


def filtraMascara(qV):
    # OCULTAR EL QUE NO ESTIGUI DINS LA MÀSCARA
    layer = qV.llegenda.currentLayer()
    if layer is not None:
        subsetAnt = layer.subsetString()
        layer.setSubsetString('')
        featsPnt = layer.getFeatures(
            QgsFeatureRequest().setFilterRect(MascaraAux.geom.boundingBox()))
        featsPnt = (x if x.geometry().within(
            MascaraAux.geom) else None for x in featsPnt)
        featsPnt = filter(lambda x: x is not None, featsPnt)
        ids = [str(x.attribute('fid')) for x in featsPnt]

        # Obtenim un string de l'estil 'fid not in (id1, id2, id3,...)'. La llista seran les ids que formen part de la màscara, de manera
        subs = 'fid NOT IN (%s)' % ', '.join(ids)
        if subsetAnt != '':
            subs = '('+subsetAnt+')'+' AND '+'('+subs+')'
        layer.setSubsetString(subs)
        qV.llegenda.actIconaFiltre(layer)


def creaMascara(qV):
    MascaraAux.qV = qV
    epsg = qV.canvas.mapSettings().destinationCrs().authid()
    mascara = QgsVectorLayer('MultiPolygon?crs=%s' % epsg, 'Màscara', 'memory')
    aplicaParametresMascara(mascara, *QvMemoria().getParametresMascara())
    if not MascaraAux.teAux:
        mascaraAux = QgsVectorLayer(
            'MultiPolygon?crs=%s' % epsg, 'Màscara auxiliar', 'memory')
        rect = qV.canvas.fullExtent()
        geom = QgsGeometry().fromRect(rect)
        # punts=[(0.,0.),(0.,10000000.),(10000000.,10000000.),(10000000.,0.)]
        # punts=[QgsPointXY(*x) for x in punts]
        # geom=QgsGeometry.fromPolygonXY([punts])
        feat = QgsFeature()
        feat.setGeometry(geom)

        pr = mascaraAux.dataProvider()
        pr.addFeatures([feat])
        mascaraAux.commitChanges()
        qV.project.addMapLayers([mascaraAux], False)
        MascaraAux.teAux = True
    qV.project.addMapLayers([mascara])
    qV.canvas.refresh()

    return mascara


def carregaMascara(qV):
    MascaraAux.qV = qV
    try:
        rutaMasc = qV.pathProjecteActual[:-4]+'mascara'+'.gpkg'
        if not os.path.exists(rutaMasc):
            return
        mascara = QgsVectorLayer(rutaMasc, 'Màscara', 'ogr')
        color, opacitat = QvMemoria().getParametresMascara()
        aplicaParametresMascara(mascara, color, opacitat/100)
        qV.project.addMapLayers([mascara])
    except:
        pass


def aplicaParametresMascara(mascara, color, opacitat):
    if opacitat > 1:
        opacitat /= 100  # Si és més que 1 vol dir que està en %
    mascara.renderer().symbol().setColor(color)
    mascara.renderer().symbol().symbolLayer(0).setStrokeColor(color)
    mascara.setOpacity(opacitat)
    MascaraAux.qV.canvas.refreshAllLayers()


def eliminaMascara(qV, tambeAuxiliar=True):
    MascaraAux.qV = qV
    try:
        qV.project.removeMapLayer(qV.project.mapLayersByName('Màscara')[0])
        if tambeAuxiliar:
            qV.project.removeMapLayer(
                qV.project.mapLayersByName('Màscara auxiliar')[0])
            MascaraAux.teAux = False
            MascaraAux.geom = None
    except Exception as e:
        # Si no hi ha màscara, suda
        pass


class QvMascaraEinaPlantilla(QgsMapTool):
    def __init__(self, qV, canvas, **kwargs):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.qV = qV
        self.setParametres(**kwargs)

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def qpointsDistance(self, p, q):
        dx = p.x() - q.x()
        dy = p.y() - q.y()
        dist = math.sqrt(dx*dx + dy*dy)
        return dist

    def missatgeCaixa(self, textTitol, textInformacio):
        msgBox = QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        ret = msgBox.exec()

    def getCapa(self):
        if not self.emmascarar:
            layer = self.qV.llegenda.currentLayer()
            if layer is None or layer.type() != QgsMapLayer.VectorLayer:
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                                   'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
                return None
            return layer
        self.mascara = obteMascara(self.qV)
        return self.mascara

    def actualitza(self):
        try:
            if self.emmascarar and hasattr(self, 'mascara'):
                self.mascara = self.getCapa()
                self.mascara.updateExtents()
                aplicaParametresMascara(
                    self.mascara, self.color, self.opacitat)
            # self.canvas.refreshAllLayers()
        except Exception as e:
            print(e)

    def setColor(self, color):
        self.color = color

    def setOpacitat(self, opacitat):
        self.opacitat = opacitat

    def setOverlap(self, overlap):
        self.overlap = overlap

    def setParametres(self, emmascarar=True, seleccionar=False, overlap=False):
        self.seleccionar = seleccionar
        self.setOverlap(overlap)
        self.emmascarar = emmascarar
        color, opacitat = QvMemoria().getParametresMascara()
        self.setColor(color)
        self.setOpacitat(opacitat/100)
        self.actualitza()


# Copiat del QvSeleccioPunt de QvEinesGrafiques.py i adaptat a les nostres necessitats
class QvMascaraEinaClick(QvMascaraEinaPlantilla):

    def __init__(self, qV, canvas, **kwargs):
        layer = qV.llegenda.currentLayer()
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")
        super().__init__(qV, canvas, **kwargs)

    def canvasReleaseEvent(self, event):
        # Get the click
        x = event.pos().x()
        y = event.pos().y()
        layer = self.qV.llegenda.currentLayer()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        radius = 10
        rect = QgsRectangle(point.x() - radius, point.y() -
                            radius, point.x() + radius, point.y() + radius)
        if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
            # items seleccionats
            it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect))
            # Ens guardem una llista dels items seleccionats
            items = [i for i in it]
            ids = [i.id() for i in items]
            if len(ids) == 0:
                return
            try:
                if self.emmascarar:
                    mascara = self.getCapa()
                    pr = mascara.dataProvider()
                    geoms = (x.geometry() for x in items)

                    aplicaMascara(self.qV, geoms, self.getCapa())
                if self.seleccionar:
                    seleccionats = layer.selectedFeatureIds()
                    layer.selectByIds(seleccionats+ids)
                    self.qV.calcularSeleccio()
                # La part d'eliminar funciona màgicament. No existeix cap raó lògica que ens digui que s'eliminarà, però ho fa
                # if not pr.deleteFeatures(polysTreure):
                #     #Ens hauríem de queixar? No? Tractar?
                #     pass
                self.actualitza()
            except Exception as e:
                print(e)
                pass
        else:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = []
        self.rubberband = self.novaRubberband()
        layer = self.qV.llegenda.currentLayer()
        if layer is None and self.seleccionar:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")

    def novaRubberband(self):
        rb = QgsRubberBand(self.canvas, True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        return rb

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Tancar polígon??
            return
        self.point = self.toMapCoordinates(event.pos())
        self.points.append(QgsPointXY(self.point))
        if len(self.points) == 1:
            self.posB = event.pos()
        self.selectPoly(event)
        if self.qpointsDistance(self.posB, event.pos()) < 10 and len(self.points) > 2:
            self.tancarPoligon()

    def canvasMoveEvent(self, event):
        poligono = QgsGeometry.fromPolylineXY(
            self.points+[self.toMapCoordinates(event.pos())])
        try:
            self.rubberband.setToGeometry(
                poligono, self.getCapa())  # falta establir la layer
        except Exception as e:
            print(e)

    def tancarPoligon(self):
        try:

            list_polygon = []
            mascara = self.getCapa()
            pr = mascara.dataProvider()
            self.points = self.points[:-1]
            for x in self.points:
                list_polygon.append(QgsPointXY(x))
            geom = QgsGeometry.fromPolygonXY([list_polygon])
            if self.emmascarar:
                aplicaMascara(self.qV, [geom], self.getCapa())
                # pr.addFeatures([poly])
            layer = self.qV.llegenda.currentLayer()
            if self.seleccionar and layer is not None:
                # Seleccionem coses
                featsPnt = layer.getFeatures(
                    QgsFeatureRequest().setFilterRect(geom.boundingBox()))
                for featPnt in featsPnt:
                    if self.overlap:
                        if featPnt.geometry().intersects(geom):
                            layer.select(featPnt.id())
                        pass
                    else:
                        if featPnt.geometry().within(geom):
                            layer.select(featPnt.id())
                        pass
                self.qV.calcularSeleccio()
            self.rubberband.hide()
            self.rubberband = self.novaRubberband()
            self.actualitza()
            self.point = None
            self.points = []
        except Exception as e:
            print(e)

    def selectPoly(self, e):
        try:

            firstMarker = False
            poligono = QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(
                poligono, self.getCapa())  # falta establir la layer
            self.rubberband.show()

        except Exception as e:
            pass


class QvMascaraEinaCercle(QvMascaraEinaPlantilla):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rubberbandRadi = self.novaRubberband()
        self.rubberbandCercle = self.novaRubberband()
        layer = self.qV.llegenda.currentLayer()
        self.centre = None
        if layer is None and self.seleccionar:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")

    def novaRubberband(self):
        rb = QgsRubberBand(self.canvas, True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        return rb

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Tancar polígon??
            return
        self.centre = self.toMapCoordinates(event.pos())

    def canvasMoveEvent(self, event):
        if self.centre is not None:
            self.rbcircle(self.centre, self.toMapCoordinates(event.pos()))
            pass

    def canvasReleaseEvent(self, event):
        mascara = self.getCapa()
        pr = mascara.dataProvider()
        poligon, _ = self.getPoligon(
            self.centre, self.toMapCoordinates(event.pos()), 100)
        if self.emmascarar:
            aplicaMascara(self.qV, [poligon], self.getCapa())
            # pr.addFeatures([poly])

        layer = self.qV.llegenda.currentLayer()
        if self.seleccionar and layer is not None:
            # Seleccionem coses
            featsPnt = layer.getFeatures(
                QgsFeatureRequest().setFilterRect(poligon.boundingBox()))
            for featPnt in featsPnt:
                if self.overlap:
                    if featPnt.geometry().intersects(poligon):
                        layer.select(featPnt.id())
                    pass
                else:
                    if featPnt.geometry().within(poligon):
                        layer.select(featPnt.id())
                    pass
            self.qV.calcularSeleccio()
        self.centre = None
        self.actualitza()
        self.rubberbandCercle.hide()

    def rbcircle(self, center, edgePoint, segments=100):
        self.rubberbandCercle.reset(True)
        self.poligon, llistaPunts = self.getPoligon(
            center, edgePoint, segments)
        for x in llistaPunts:
            self.rubberbandCercle.addPoint(x)

    def getPoligon(self, center, edgePoint, segments):
        r = math.sqrt(center.sqrDist(edgePoint))
        llistaPunts = []
        pi = 3.1416
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            llistaPunts.append(QgsPointXY(
                center.x()+r*math.cos(theta), center.y()+r*math.sin(theta)))
        return QgsGeometry.fromPolygonXY([llistaPunts[:-2]]), llistaPunts
