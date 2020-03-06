from moduls.QvImports import *
from moduls.QvAtributs import QvFitxesAtributs
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton
from moduls.QvMemoria import QvMemoria
from moduls.QvConstants import QvConstants
from moduls.QVDistrictesBarris import QVDistrictesBarris
from qgis.gui import QgsMapTool, QgsRubberBand
import math

class MascaraAux:
    # Una classe per encapsular variables i coses
    teAux = False
    geom = None
    projecte = None
    canvas = None

# geoms: iterable de QgsGeometry
def aplicaMascara(projecte, canvas, geoms, mascara=None):
    MascaraAux.projecte = projecte
    MascaraAux.canvas = canvas
    eliminaMascara(projecte, False)
    mascara = obteMascara(projecte, canvas)
    mascaraAux = projecte.mapLayersByName('Màscara auxiliar')[0]
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
    projecte.addMapLayers([mascara])
    canvas.refresh()


def obteMascara(projecte, canvas):
    # MascaraAux.qV = qV
    MascaraAux.projecte = projecte
    mascares = projecte.mapLayersByName('Màscara')
    if len(mascares) == 0:
        return creaMascara(projecte,canvas)
    return mascares[0]


#Inutilitzada
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


def creaMascara(projecte, canvas):
    MascaraAux.projecte = projecte
    MascaraAux.canvas = canvas
    epsg = canvas.mapSettings().destinationCrs().authid()
    mascara = QgsVectorLayer('MultiPolygon?crs=%s' % epsg, 'Màscara', 'memory')
    aplicaParametresMascara(mascara, *QvMemoria().getParametresMascara())
    if not MascaraAux.teAux:
        mascaraAux = QgsVectorLayer(
            'MultiPolygon?crs=%s' % epsg, 'Màscara auxiliar', 'memory')
        rect = canvas.fullExtent()
        geom = QgsGeometry().fromRect(rect)
        # punts=[(0.,0.),(0.,10000000.),(10000000.,10000000.),(10000000.,0.)]
        # punts=[QgsPointXY(*x) for x in punts]
        # geom=QgsGeometry.fromPolygonXY([punts])
        feat = QgsFeature()
        feat.setGeometry(geom)

        pr = mascaraAux.dataProvider()
        pr.addFeatures([feat])
        mascaraAux.commitChanges()
        projecte.addMapLayers([mascaraAux], False)
        MascaraAux.teAux = True
    projecte.addMapLayers([mascara])
    canvas.refresh()

    return mascara


def carregaMascara(projecte):
    MascaraAux.projecte = projecte
    try:
        rutaMasc = projecte.absoluteFilePath()[:-4]+'mascara'+'.gpkg'
        if not os.path.exists(rutaMasc):
            return
        mascara = QgsVectorLayer(rutaMasc, 'Màscara', 'ogr')
        color, opacitat = QvMemoria().getParametresMascara()
        aplicaParametresMascara(mascara, color, opacitat/100)
        projecte.addMapLayers([mascara])
    except:
        pass


def aplicaParametresMascara(mascara, color, opacitat):
    if opacitat > 1:
        opacitat /= 100  # Si és més que 1 vol dir que està en %
    mascara.renderer().symbol().setColor(color)
    mascara.renderer().symbol().symbolLayer(0).setStrokeColor(color)
    mascara.setOpacity(opacitat)
    MascaraAux.canvas.refreshAllLayers()


def eliminaMascara(projecte, tambeAuxiliar=True):
    MascaraAux.projecte = projecte
    try:
        projecte.removeMapLayer(projecte.mapLayersByName('Màscara')[0])
        if tambeAuxiliar:
            projecte.removeMapLayer(
                projecte.mapLayersByName('Màscara auxiliar')[0])
            MascaraAux.teAux = False
            MascaraAux.geom = None
    except Exception as e:
        # Si no hi ha màscara, suda
        pass

def seleccioCercle(wSeleccioGrafica):
    seleccioClick() 
    try:
        wSeleccioGrafica.canvas.scene().removeItem(wSeleccioGrafica.toolSelect.rubberband)
    except:
        pass
    # qV.toolSelect = QvSeleccioCercle(qV, 10, 10, 30)
    try:
        wSeleccioGrafica.toolSelect = QvMascaraEinaCercle(wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas, wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
        wSeleccioGrafica.setTool(wSeleccioGrafica.toolSelect)
        # qV.toolSelect.setOverlap(qV.checkOverlap.checkState())
        wSeleccioGrafica.canvas.setMapTool(wSeleccioGrafica.toolSelect)
    except Exception as e:
        print(e)
        pass

def seleccioClicks(wSeleccioGrafica):
    seleccioClick()
    try:
        wSeleccioGrafica.canvas.scene().removeItem(wSeleccioGrafica.toolSelect.rubberband)
    except:
        pass

    try:
        tool = QvMascaraEinaClick(wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas, wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
        wSeleccioGrafica.setTool(tool)
        wSeleccioGrafica.canvas.setMapTool(tool)
    except Exception as e:
        print(e)
        pass
def seleccioLliure(wSeleccioGrafica):
    # qV.markers.hide()
    try:
        #Això no hauria de funcionar
        qV.esborrarSeleccio()
    except:
        pass

    try:
        wSeleccioGrafica.actionMapSelect = QAction('Seleccionar dibuixant', wSeleccioGrafica)
        # qV.toolSelect = QvSeleccioPerPoligon(qV,qV.canvas, layer)
        wSeleccioGrafica.tool = QvMascaraEinaDibuixa(wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas, wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
        wSeleccioGrafica.setTool(wSeleccioGrafica.tool)

        # qV.tool.setOverlap(qV.checkOverlap.checkState())

        wSeleccioGrafica.tool.setAction(wSeleccioGrafica.actionMapSelect)
        wSeleccioGrafica.canvas.setMapTool(wSeleccioGrafica.tool)
        # taulaAtributs('Seleccionats', layer)
    except:
        pass
def seleccioClick():
    try:
        self.esborrarMesures()
    except:
        pass    

class QvMascaraEinaPlantilla(QgsMapTool):
    def __init__(self, wSeleccioGrafica, projecte, canvas, llegenda, **kwargs):
        QgsMapTool.__init__(self, canvas)
        self.wSeleccioGrafica=wSeleccioGrafica
        self.canvas = canvas
        self.projecte = projecte
        self.llegenda=llegenda
        self.setParametres(**kwargs)
        self.rubberbands=[]

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()


    def qpointsDistance(self, p, q):
        dx = p.x() - q.x()
        dy = p.y() - q.y()
        dist = math.sqrt(dx*dx + dy*dy)
        return dist

    def missatgeCaixa(self, textTitol, textInformacio):
        msgBox = QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        msgBox.exec()

    def getCapa(self):
        if not self.emmascarar:
            layer = self.llegenda.currentLayer()
            if layer is None or layer.type() != QgsMapLayer.VectorLayer:
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                                   'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
                return None
            return layer
        self.mascara = obteMascara(self.projecte, self.canvas)
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

    def novaRubberband(self):
        rb = QgsRubberBand(self.canvas, True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        self.rubberbands.append(rb)
        return rb
    def eliminaRubberbands(self):
        for x in self.rubberbands: x.hide()


# Copiat del QvSeleccioPunt de QvEinesGrafiques.py i adaptat a les nostres necessitats
class QvMascaraEinaClick(QvMascaraEinaPlantilla):

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        layer = self.llegenda.currentLayer()
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")
        super().__init__(*args, **kwargs)

    def canvasReleaseEvent(self, event):
        # Get the click
        x = event.pos().x()
        y = event.pos().y()
        layer = self.llegenda.currentLayer()
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
                    geoms = (x.geometry() for x in items)

                    aplicaMascara(self.projecte,self.canvas, geoms, self.getCapa())
                if self.seleccionar:
                    seleccionats = layer.selectedFeatureIds()
                    layer.selectByIds(seleccionats+ids)
                    self.wSeleccioGrafica.calcularSeleccio()
                # La part d'eliminar funciona màgicament. No existeix cap raó lògica que ens digui que s'eliminarà, però ho fa
                # if not pr.deleteFeatures(polysTreure):
                #     #Ens hauríem de queixar? No? Tractar?
                #     pass
                self.actualitza()
            except Exception as e:
                print(e)
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
        layer = self.llegenda.currentLayer()
        if layer is None and self.seleccionar:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Tancar polígon??
            return
        self.point = self.toMapCoordinates(event.pos())
        self.points.append(QgsPointXY(self.point))
        if len(self.points) == 1:
            self.posB = event.pos()
        self.selectPoly(event)
        if len(self.points) > 2 and self.qpointsDistance(self.toCanvasCoordinates(self.points[0]), event.pos()) < 10:
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
            self.points = self.points[:-1]
            for x in self.points:
                list_polygon.append(QgsPointXY(x))
            geom = QgsGeometry.fromPolygonXY([list_polygon])
            if self.emmascarar:
                aplicaMascara(self.projecte, self.canvas, [geom], self.getCapa())
                # pr.addFeatures([poly])
            layer = self.llegenda.currentLayer()
            if self.seleccionar and layer is not None:
                # Seleccionem coses
                featsPnt = layer.getFeatures(
                    QgsFeatureRequest().setFilterRect(geom.boundingBox()))
                for featPnt in featsPnt:
                    if self.overlap:
                        if featPnt.geometry().intersects(geom):
                            layer.select(featPnt.id())
                    else:
                        if featPnt.geometry().within(geom):
                            layer.select(featPnt.id())
                self.wSeleccioGrafica.calcularSeleccio()
            self.rubberband.hide()
            self.rubberband = self.novaRubberband()
            self.actualitza()
            self.point = None
            self.points = []
        except Exception as e:
            print(e)

    def selectPoly(self, e):
        try:

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
        layer = self.llegenda.currentLayer()
        self.centre = None
        if layer is None and self.seleccionar:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Tancar polígon??
            return
        self.centre = self.toMapCoordinates(event.pos())

    def canvasMoveEvent(self, event):
        if self.centre is not None:
            self.rbcircle(self.centre, self.toMapCoordinates(event.pos()))

    def canvasReleaseEvent(self, event):
        mascara = self.getCapa()
        poligon, _ = self.getPoligon(
            self.centre, self.toMapCoordinates(event.pos()), 100)
        if self.emmascarar:
            aplicaMascara(self.projecte, self.canvas, [poligon], self.getCapa())
            # pr.addFeatures([poly])

        layer = self.llegenda.currentLayer()
        if self.seleccionar and layer is not None:
            # Seleccionem coses
            featsPnt = layer.getFeatures(
                QgsFeatureRequest().setFilterRect(poligon.boundingBox()))
            for featPnt in featsPnt:
                if self.overlap:
                    if featPnt.geometry().intersects(poligon):
                        layer.select(featPnt.id())
                else:
                    if featPnt.geometry().within(poligon):
                        layer.select(featPnt.id())
            self.wSeleccioGrafica.calcularSeleccio()
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

    def __init__(self, canvas, llegenda, radi = 10):
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
        msgBox.exec()

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
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x-self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x+self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))

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

class QvSeleccioGrafica(QWidget):
    def __init__(self, canvas, projecte, llegenda):
        QWidget.__init__(self)
        self.canvas=canvas
        self.llegenda=llegenda
        self.projecte=projecte
        self.interficie()
    def interficie(self):
        self.color=QColor('white')
        self.setWhatsThis(QvApp().carregaAjuda(self))
        self.lytSeleccioGrafica = QVBoxLayout()
        self.lytSeleccioGrafica.setAlignment(Qt.AlignTop)
        self.setLayout(self.lytSeleccioGrafica)
        self.lytBotonsSeleccio = QHBoxLayout()
        self.leSel2 = QLineEdit()
        self.lytSeleccioGrafica.addWidget(self.leSel2)
        # self.leSel2.editingFinished.connect(seleccioExpressio)
        self.lytSeleccioGrafica.addLayout(self.lytBotonsSeleccio)


        self.bs1 = QvPushButton(flat=True)
        # self.bs1.setCheckable(True)
        self.bs1.setIcon(QIcon(imatgesDir+'apuntar.png'))
        self.bs1.setToolTip('Seleccionar elements de la capa activa')
        self.bs2 = QvPushButton(flat=True)
        # self.bs2.setCheckable(True)
        self.bs2.setIcon(QIcon(imatgesDir+'shape-polygon-plus.png'))
        self.bs2.setToolTip('Dibuixar un polígon')
        self.bs3 = QvPushButton(flat=True)
        # self.bs3.setCheckable(True)
        self.bs3.setIcon(QIcon(imatgesDir+'vector-circle-variant.png'))
        self.bs3.setToolTip('Dibuixar un cercle')
        self.bs4 = QvPushButton('Netejar')
        # self.bs4.setCheckable(True)
        # self.bs4.setIcon(QIcon(imatgesDir+'trash-can-outline.png'))

        # self.lblNombreElementsSeleccionats = QLabel('No hi ha elements seleccionats.')
        self.lblCapaSeleccionada = QLabel('No hi capa seleccionada.')
        
        self.lwFieldsSelect = QListWidget()
        self.lwFieldsSelect.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.bs5 = QvPushButton('Calcular',flat=True)
        self.bs5.clicked.connect(self.calcularSeleccio)
        
        self.bs6 = QvPushButton('Crear CSV',flat=True)
        # self.bs6.clicked.connect(self.crearCsv)

        self.twResultats = QTableWidget()

        #Ja no són checkbox però no els canviem el nom jaja salu2
        self.checkOverlap = QRadioButton('Solapant')
        self.checkNoOverlap = QRadioButton('Totalment dins')
        self.checkNoOverlap.setChecked(True)
        self.checkSeleccio = QRadioButton('Seleccionar')
        self.checkSeleccio.setChecked(True)
        self.checkMascara = QRadioButton('Emmascarar')
        
        color, opacitat = QvMemoria().getParametresMascara()
        self.lblOpacitat=QLabel('70 %')
        self.sliderOpacitat=QSlider(Qt.Horizontal,self)
        self.sliderOpacitat.setMinimum(0)
        self.sliderOpacitat.setMaximum(100)
        self.sliderOpacitat.setSingleStep(1)
        self.sliderOpacitat.valueChanged.connect(lambda x: self.lblOpacitat.setText(str(x)+' %'))
        self.sliderOpacitat.setValue(opacitat)
        def canviColor(color):
            self.color=color
            self.bsSeleccioColor.setStyleSheet('background: solid %s; border: none'%color.name())
            self.actualitzaTool()
        def openColorDialog():
            canviColor(QColorDialog().getColor())
        self.bsSeleccioColor=QvPushButton(flat=True)
        self.bsSeleccioColor.setIcon(QIcon('Imatges/da_color.png'))
        self.bsSeleccioColor.setStyleSheet('background: solid %s; border: none'%color.name())
        self.bsSeleccioColor.setIconSize(QSize(25,25))
        self.bsSeleccioColor.clicked.connect(openColorDialog)
        self.color=color
        QvConstants.afegeixOmbraWidget(self.bsSeleccioColor)

        self.checkOverlap.toggled.connect(self.actualitzaTool)
        self.checkSeleccio.toggled.connect(self.actualitzaTool)
        self.checkMascara.toggled.connect(self.actualitzaTool)
        self.sliderOpacitat.valueChanged.connect(self.actualitzaTool)
        self.bs1.clicked.connect(lambda x: seleccioClicks(self))
        self.bs2.clicked.connect(lambda x: seleccioLliure(self))
        self.bs3.clicked.connect(lambda x: seleccioCercle(self))
        self.bs4.clicked.connect(lambda: self.esborrarSeleccio(True, True))

        self.lytBotonsSeleccio.addWidget(self.bs1)
        self.lytBotonsSeleccio.addWidget(self.bs2)
        self.lytBotonsSeleccio.addWidget(self.bs3)
        self.lytBotonsSeleccio.addWidget(self.bs4)
        
        lytSelMasc=QHBoxLayout()
        lytSelMasc.addWidget(self.checkSeleccio)
        lytSelMasc.addWidget(self.checkMascara)
        gbSelMasc=QGroupBox()
        gbSelMasc.setLayout(lytSelMasc)
        lytOverlap=QHBoxLayout()
        lytOverlap.addWidget(self.checkNoOverlap)
        lytOverlap.addWidget(self.checkOverlap)

        lytColorOpacitatLbl=QVBoxLayout()
        lytColorOpacitatLbl.addWidget(QLabel('Opacitat i color de la màscara'))
        lytColorOpacitat=QHBoxLayout()
        lytColorOpacitat.addWidget(self.lblOpacitat)
        lytColorOpacitat.addWidget(self.sliderOpacitat)
        lytColorOpacitat.addWidget(self.bsSeleccioColor)
        lytColorOpacitatLbl.addLayout(lytColorOpacitat)
        self.frameColorOpacitat=QFrame(self)
        self.frameColorOpacitat.setLayout(lytColorOpacitatLbl)
        self.frameColorOpacitat.hide()
        self.frameColorOpacitat.setFrameStyle(QFrame.StyledPanel)

        self.gbOverlap=QGroupBox()
        self.gbOverlap.setLayout(lytOverlap)
        self.lytSeleccioGrafica.addWidget(gbSelMasc)
        self.lytSeleccioGrafica.addWidget(self.gbOverlap)
        self.lytSeleccioGrafica.addWidget(self.frameColorOpacitat)
        # self.lytSeleccioGrafica.addWidget(self.lblNombreElementsSeleccionats)
        self.lytSeleccioGrafica.addWidget(self.lblCapaSeleccionada)
        self.lytSeleccioGrafica.addWidget(self.lwFieldsSelect)
        # self.lytSeleccioGrafica.addWidget(self.bs5)
        self.lytSeleccioGrafica.addWidget(self.bs6)
        self.lytSeleccioGrafica.addWidget(self.twResultats)
        
        self.distBarrisSelMasc = QVDistrictesBarris()
        # self.distBarrisSelMasc.view.clicked.connect(self.clickArbreSelMasc)
        self.lytSeleccioGrafica.addWidget(self.distBarrisSelMasc.view)
    def getParametres(self):
        #Falta incloure color i opacitat
        return {'overlap': self.checkOverlap.isChecked(),
                'seleccionar': self.checkSeleccio.isChecked(),
                # 'color':self.color,
                # 'opacitat':qV.sliderOpacitat.value(),
                'emmascarar': self.checkMascara.isChecked()
                }
    def setTool(self,tool):
        self.tool=tool
    def actualitzaTool(self):
        QvMemoria().setParametresMascara(self.color,self.sliderOpacitat.value())
        self.gbOverlap.setVisible(self.checkSeleccio.isChecked())
        self.frameColorOpacitat.setVisible(self.checkMascara.isChecked())
        masc=obteMascara(self.projecte, self.canvas)
        pars=QvMemoria().getParametresMascara()
        aplicaParametresMascara(masc,*pars)
    def setVisible(self,visible):
        super().setVisible(visible)
        if not visible:
            qV.foraEinaSeleccio()
    def setInfoLbl(self,txtSelec):
        self.lblCapaSeleccionada.setText(txtSelec)
    def calcularSeleccio(self):
        layer = self.llegenda.currentLayer()
        taula=self.twResultats
        numeroFields=0 #???
        fila=0
        columna=0 #???
        nombreElements = 0
        taula.setColumnCount(3)
        taula.setHorizontalHeaderLabels(['','Total', 'Mitjana'])
        nombreFieldsSeleccionats=0
        for a in self.lwFieldsSelect.selectedItems():
            nombreFieldsSeleccionats=nombreFieldsSeleccionats+1
        taula.setRowCount(nombreFieldsSeleccionats+1)
        for a in self.lwFieldsSelect.selectedItems():
            total=0
            item = QTableWidgetItem(a.text())
            taula.setItem(fila+1,0,item)
            # print (field)
            nombreElements=0
            for feature in layer.selectedFeatures():
                calcul=feature.attributes()[layer.fields().lookupField(a.text())]
                total=total+calcul
                nombreElements=nombreElements+1
            if nombreElements>0:
                mitjana = total/nombreElements
            else:
                mitjana = 0
            item = QTableWidgetItem(str('% 12.2f' % total))
            taula.setItem(fila+1,1,item)
            item = QTableWidgetItem(str('% 12.2f' % mitjana))
            taula.setItem(fila+1,2,item)
            # print('Total: '+a.text()+": ",total)
            fila=fila+1
        item = QTableWidgetItem("Seleccionats:")
        taula.setItem(0,0,item)
        item = QTableWidgetItem(str(nombreElements))
        taula.setItem(0,1,item)
        taula.resizeColumnsToContents()
    def calculaFields(self, layerActiu):
        fields = layerActiu.fields()
        for field in fields:
            # print(field.typeName())
            # if (field.typeName()!='String' and field.typeName()!='Date' and field.typeName()!='Date'):
            if (field.typeName()=='Real' or field.typeName()=='Integer64'):
                self.lwFieldsSelect.addItem(field.name())


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


 