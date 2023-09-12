import csv
import itertools
import math
import os
from types import prepare_class

from qgis.core import (QgsFeature, QgsFeatureRequest, QgsGeometry, QgsMapLayer,
                       QgsPointXY, QgsRectangle, QgsVector, QgsVectorLayer,
                       QgsWkbTypes)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsVertexMarker
from qgis.PyQt.QtCore import QSize, Qt, QVariant, pyqtSignal
from qgis.PyQt.QtGui import QColor, QIcon, QIntValidator, QPolygonF
from qgis.PyQt.QtWidgets import (QAbstractItemView, QAction, QCheckBox,
                                 QColorDialog, QFileDialog, QFrame, QGroupBox,
                                 QHBoxLayout, QLabel, QLineEdit, QListWidget,
                                 QMessageBox, QRadioButton, QSizePolicy,
                                 QSlider, QTableWidget, QTableWidgetItem,
                                 QToolBox, QVBoxLayout, QWidget)

import configuracioQvista
from moduls import QvFuncions
from moduls.QvApp import QvApp
from moduls.QvAtributsForms import QvFormAtributs
from moduls.QvConstants import QvConstants
from moduls.QVDistrictesBarris import QVDistrictesBarris
from moduls.QvLlegendaMascara import QvLlegendaMascara
from moduls.QvMemoria import QvMemoria
from moduls.QvPushButton import QvPushButton

def difGeom(geom1, geom2):
    return geom1.difference(geom2).area()

# Retorna True si la diferència d'àrees entre geom1 i geom2 és menor o igual a prop*geom1.area()
# Això és perquè a vegades la geometria no està contenida del tot per una diferència molt petita
def conteRel(geom1, geom2, prop=0.01):
    return geom1.intersects(geom2) and difGeom(geom1, geom2) <= prop*geom1.area()

class QvSeleccioGrafica(QWidget):
    '''Widget de seleccionar i emmascarar'''
    __zones = r'Dades\Zones.gpkg'
    def __init__(self, canvas, projecte, llegenda):
        QWidget.__init__(self)
        self.canvas = canvas
        self.llegenda = llegenda
        self.projecte = projecte
        # self.projecte.fileNameChanged.connect(lambda: self.esborrarSeleccio(True, True))
        self.interficie()

        self.einaClick = QvMascaraEinaClick(self, self.projecte, self.canvas, self.llegenda, **self.getParametres())
        self.einaDibuixa = QvMascaraEinaDibuixa(self, self.projecte, self.canvas, self.llegenda, **self.getParametres())
        self.einaCercle = QvMascaraEinaCercle(self, self.projecte, self.canvas, self.llegenda, **self.getParametres())
        for x in (self.einaClick, self.einaDibuixa, self.einaCercle):
            x.selecciona.connect(self.seleccionar)
            x.emmascara.connect(self.aplicaMascara)
        self.tool = None

        self.geomMascara = None # Aquí anirem acumulant la màscara aplicada

    def interficie(self):
        self.color = QColor('white')
        self.setWhatsThis(QvApp().carregaAjuda(self))
        self.lytSeleccioGrafica = QVBoxLayout()
        self.lytSeleccioGrafica.setAlignment(Qt.AlignTop)
        self.setLayout(self.lytSeleccioGrafica)
        self.lytBotonsSeleccio = QHBoxLayout()
        # self.leSel2 = QLineEdit()
        # self.lytSeleccioGrafica.addWidget(self.leSel2)
        # self.leSel2.editingFinished.connect(seleccioExpressio)
        self.lytSeleccioGrafica.addLayout(self.lytBotonsSeleccio)

        self.bs1 = QvPushButton(flat=True)
        # self.bs1.setCheckable(True)
        self.bs1.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'apuntar.png')))
        self.bs1.setToolTip('Seleccionar elements de la capa activa')
        self.bs2 = QvPushButton(flat=True)
        # self.bs2.setCheckable(True)
        self.bs2.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'shape-polygon-plus.png')))
        self.bs2.setToolTip('Dibuixar un polígon')
        self.bs3 = QvPushButton(flat=True)
        # self.bs3.setCheckable(True)
        self.bs3.setIcon(QIcon(os.path.join(configuracioQvista.imatgesDir,'vector-circle-variant.png')))
        self.bs3.setToolTip('Dibuixar un cercle')
        self.bs4 = QvPushButton('Netejar')
        # self.projecte.fileNameChanged.connect(self.setNouProjecte)
        # self.bs4.setCheckable(True)
        # self.bs4.setIcon(QIcon(configuracioQvista.imatgesDir+'trash-can-outline.png'))

        # self.lblNombreElementsSeleccionats = QLabel('No hi ha elements seleccionats.')
        self.lblCapaSeleccionada = QLabel('No hi capa seleccionada.')

        self.lwFieldsSelect = QListWidget()
        self.lwFieldsSelect.setSelectionMode(
            QAbstractItemView.ExtendedSelection)

        self.bs5 = QvPushButton('Calcular', flat=True)
        self.bs5.clicked.connect(self.calcularSeleccio)

        self.bs6 = QvPushButton('Crear CSV')
        self.bs6.clicked.connect(lambda: self.crearCsv())

        # Tool Box de resultats, on afegirem múltiples pestanyes
        self.tbResultats = QToolBox()
        self.gbResultats = QGroupBox('0 elements seleccionats visibles')
        layGB = QVBoxLayout() # Layout d'un únic element, per posar la taula dins d'una Group Box
        layGB.addWidget(self.tbResultats)
        self.gbResultats.setLayout(layGB)

        # Taula de resultats
        self.twResultats = QTableWidget()
        layCalculsNumerics = QVBoxLayout()
        lblCalculsNumerics = QLabel('Suma i mitjana dels camps seleccionats que siguin numèrics.')
        lblCalculsNumerics.setWordWrap(True)
        layCalculsNumerics.addWidget(lblCalculsNumerics)
        layCalculsNumerics.addWidget(self.twResultats)
        widCalculs = QWidget()
        widCalculs.setLayout(layCalculsNumerics)

        # Taula de les previsualitzacions (no implementada)
        self.twPreview = QTableWidget()
        layPreview = QVBoxLayout()
        lblPreview = QLabel('Taula de previsualització del contingut seleccionat. Com a màxim es mostren els 20 primers elements.')
        lblPreview.setWordWrap(True)
        layPreview.addWidget(lblPreview)
        layPreview.addWidget(self.twPreview)
        widPreview = QWidget()
        widPreview.setLayout(layPreview)

        # Arbre de selecció
        self.distBarrisSelMasc = QVDistrictesBarris()
        self.distBarrisSelMasc.view.clicked.connect(self.clickArbreSelMasc)

        layCamps = QVBoxLayout()
        lblCamps = QLabel('Seleccioneu els camps dels que voleu fer-ne una extracció a un arxiu CSV.')
        lblCamps.setWordWrap(True)
        layCamps.addWidget(lblCamps)
        layCamps.addWidget(self.lwFieldsSelect)
        layCamps.addWidget(self.bs6)
        widCamps = QWidget()
        widCamps.setLayout(layCamps)

        self.tbResultats.addItem(widCamps, 'Selecció i extracció de camps')
        # self.tbResultats.addItem(self.twResultats, 'Càlculs numèrics')
        self.tbResultats.addItem(widCalculs, 'Càlculs numèrics')
        self.tbResultats.addItem(widPreview,'Preview de la selecció')
        self.tbResultats.addItem(self.distBarrisSelMasc.view, 'Selecció per zones')
        # layGB = QVBoxLayout()
        # layGB.addWidget(self.twResultats)
        # self.gbResultats.setLayout(layGB)

        # Ja no són checkbox però no els canviem el nom jaja salu2
        self.checkOverlap = QRadioButton('Solapant')
        self.checkNoOverlap = QRadioButton('Totalment dins')
        self.checkNoOverlap.setChecked(True)
        self.checkSeleccio = QRadioButton('Seleccionar')
        self.checkSeleccio.setChecked(True)
        self.checkMascara = QRadioButton('Emmascarar')

        color, opacitat = QvMemoria().getParametresMascara()
        self.lblOpacitat = QLabel('70 %')
        self.sliderOpacitat = QSlider(Qt.Horizontal, self)
        self.sliderOpacitat.setMinimum(0)
        self.sliderOpacitat.setMaximum(100)
        self.sliderOpacitat.setSingleStep(1)
        self.sliderOpacitat.valueChanged.connect(
            lambda x: self.lblOpacitat.setText(str(x)+' %'))
        self.sliderOpacitat.setValue(opacitat)

        def canviColor(color):
            self.color = color
            self.bsSeleccioColor.setStyleSheet(
                'background: solid %s; border: none' % color.name())
            self.actualitzaTool()

        def openColorDialog():
            canviColor(QColorDialog().getColor())
        self.bsSeleccioColor = QvPushButton(flat=True)
        self.bsSeleccioColor.setIcon(QIcon('Imatges/da_color.png'))
        self.bsSeleccioColor.setStyleSheet(
            'background: solid %s; border: none' % color.name())
        self.bsSeleccioColor.setIconSize(QSize(25, 25))
        self.bsSeleccioColor.clicked.connect(openColorDialog)
        self.color = color
        QvConstants.afegeixOmbraWidget(self.bsSeleccioColor)

        self.checkOverlap.toggled.connect(self.actualitzaTool)
        self.checkSeleccio.toggled.connect(self.actualitzaTool)
        self.checkMascara.toggled.connect(self.actualitzaTool)
        self.sliderOpacitat.valueChanged.connect(self.actualitzaTool)
        self.bs1.clicked.connect(self.setEinaClick)
        self.bs2.clicked.connect(self.setEinaDibuixa)
        self.bs3.clicked.connect(self.setEinaCercle)
        self.bs4.clicked.connect(lambda: self.esborrarSeleccio(True))
        self.bs4.clicked.connect(lambda: self.esborrarMascara(True))

        self.lytBotonsSeleccio.addWidget(self.bs1)
        self.lytBotonsSeleccio.addWidget(self.bs2)
        self.lytBotonsSeleccio.addWidget(self.bs3)
        self.lytBotonsSeleccio.addWidget(self.bs4)

        lytSelMasc = QHBoxLayout()
        lytSelMasc.addWidget(self.checkSeleccio)
        lytSelMasc.addWidget(self.checkMascara)
        gbSelMasc = QGroupBox()
        gbSelMasc.setLayout(lytSelMasc)
        lytOverlap = QHBoxLayout()
        lytOverlap.addWidget(self.checkNoOverlap)
        lytOverlap.addWidget(self.checkOverlap)

        lytColorOpacitatLbl = QVBoxLayout()
        lytColorOpacitatLbl.addWidget(QLabel('Opacitat i color de la màscara'))
        lytColorOpacitat = QHBoxLayout()
        lytColorOpacitat.addWidget(self.lblOpacitat)
        lytColorOpacitat.addWidget(self.sliderOpacitat)
        lytColorOpacitat.addWidget(self.bsSeleccioColor)
        lytColorOpacitatLbl.addLayout(lytColorOpacitat)
        self.frameColorOpacitat = QFrame(self)
        self.frameColorOpacitat.setLayout(lytColorOpacitatLbl)
        self.frameColorOpacitat.hide()
        self.frameColorOpacitat.setFrameStyle(QFrame.StyledPanel)

        self.leRadiCercle = QLineEdit()
        self.leFixarCentre = QLineEdit()
        self.canvas.xyCoordinates.connect(self.showXY)
        val = QIntValidator()
        val.setBottom(0)
        self.leRadiCercle.setValidator(val)
        self.leRadiCercle.returnPressed.connect(self.radiCercle)
        self.leFixarCentre.returnPressed.connect(self.cercleCentreFixe)
        self.cbFixarRadi = QCheckBox('Fixar radi')
        self.cbFixarRadi.stateChanged.connect(self.radiCercle)
        layRadi = QHBoxLayout()
        layRadi.addWidget(self.leRadiCercle)
        layRadi.addWidget(self.cbFixarRadi)
        layCentre = QHBoxLayout()
        layCentre.addWidget(self.leFixarCentre)
        self.lytSeleccioGrafica.addLayout(layRadi)
        self.lytSeleccioGrafica.addLayout(layCentre)
        self.leRadiCercle.hide()
        self.leFixarCentre.hide()
        self.cbFixarRadi.hide()

        self.gbOverlap = QGroupBox()
        self.gbOverlap.setLayout(lytOverlap)
        self.lytSeleccioGrafica.addWidget(gbSelMasc)
        self.lytSeleccioGrafica.addWidget(self.gbOverlap)
        self.lytSeleccioGrafica.addWidget(self.frameColorOpacitat)
        # self.lytSeleccioGrafica.addWidget(self.lblNombreElementsSeleccionats)
        self.lytSeleccioGrafica.addWidget(self.lblCapaSeleccionada)
        # self.lytSeleccioGrafica.addWidget(self.lwFieldsSelect)
        # self.lytSeleccioGrafica.addWidget(self.bs5)
        # self.lytSeleccioGrafica.addStretch()
        # self.lytSeleccioGrafica.addWidget(self.bs6)
        # self.lytSeleccioGrafica.addWidget(self.twResultats)
        self.lytSeleccioGrafica.addWidget(self.gbResultats)
    
    def checkTool(self, tool):
        # Comprovem que l'eina es pugui utilitzar.
        # Si no es pot, informem de per què
        esPot, err = tool.checkTool()
        if not esPot:
            QMessageBox.warning(self, 'Atenció',err)
            # Mostrar error
            pass
            
        return esPot

    # Cal netejar les rubberbands???
    def setEinaClick(self):
        # self.foraEines()
        if self.checkTool(self.einaClick):
            self.tool = self.einaClick
            self.canvas.setMapTool(self.tool)
            
            self.leRadiCercle.hide()
            self.cbFixarRadi.hide()

    def setEinaDibuixa(self):
        # self.foraEines()
        if self.checkTool(self.einaDibuixa):
            self.tool = self.einaDibuixa
            self.canvas.setMapTool(self.tool)
            
            self.leRadiCercle.hide()
            self.cbFixarRadi.hide()

    def setEinaCercle(self):
        # self.foraEines()
        if self.checkTool(self.einaCercle):
            self.tool = self.einaCercle
            self.canvas.setMapTool(self.tool)
            
            self.leRadiCercle.show()
            self.cbFixarRadi.show()

    def radiCercle(self):
        radi = self.leRadiCercle.text()
        if self.cbFixarRadi.isChecked() and radi!='' and int(radi)!=0:
            self.einaCercle.cercleFixe = True
            self.einaCercle.radiCercle = int(radi)
        else:
            self.einaCercle.cercleFixe = False
            self.einaCercle.rubberbandCercle.reset(True)
        self.leFixarCentre.setVisible(self.einaCercle.cercleFixe)
    
    # inspirat en el funcionament de leXY a QvStatusBar
    def cercleCentreFixe(self):
        coordenades = self.leFixarCentre.text()
        try:
            coordX, coordY = coordenades.split(';')
            x, xOk = QvApp().locale.toFloat(coordX)
            y, yOk = QvApp().locale.toFloat(coordY)
            dist, distOk = QvApp().locale.toFloat(self.leRadiCercle.text())
            if xOk and yOk and distOk:
                punt = QgsPointXY(x, y)
                vora = punt+QgsVector(dist, 0)
                # punt2 = QgsPointXY(x+dist, y)

                # poligon, _ = self.tool.getPoligon(punt, punt2, 100)
                poligon, _ = self.tool.getPoligon(punt, vora, 100)
                self.tool.rbcircle(punt, vora, segments=100)
                self.tool.rubberbandCercle = self.tool.novaRubberband()
                # self.tool.rubberbandCercle.setToGeometry(poligon, self.tool.getCapa())
                if self.checkMascara.isChecked():
                    self.aplicaMascara([poligon])
                else:
                    # rb = self.tool.novaRubberband()
                    # rb = QgsRubberBand(self.canvas, False)
                    # rb.setToGeometry(poligon, self.llegenda.currentLayer())
                    self.tool.seleccionaPoligon(poligon)
                self.canvas.setCenter(punt)
                self.canvas.refresh()
            # print(coordX, coordY)
        except Exception as e:
            pass

    def getXY(self, p, numDec=3):
        text = QvApp().locale.toString(p.x(), 'f', numDec) + ';' + \
                QvApp().locale.toString(p.y(), 'f', numDec)
        return text

    def showXY(self, p, numDec=3):
        try:
            text = self.getXY(p,numDec)
            self.leFixarCentre.setText(text)
        except Exception as e:
            pass
    
    @QvFuncions.mostraSpinner
    def crearCsv(self):
        capa = self.llegenda.currentLayer()
        if capa is not None:
            camps = [camp.text() for camp in self.lwFieldsSelect.selectedItems()]
            if camps==[]:
                # Queixar-nos de que no hi ha cap camp
                pass
            nfile, _ = QFileDialog.getSaveFileName(None, "Desar arxiu CSV", ".", "Arxius CSV (*.csv)")
            if nfile=='': return
            # feats = capa.selectedFeatures()
            with open(nfile,'w', newline='') as f:
                writer = csv.DictWriter(f,fieldnames=camps, delimiter=';')
                writer.writeheader()
                # for feat in feats:
                for feat in self.llegenda.getLayerVisibleFeatures(capa):
                    d = {}
                    for camp in camps:
                        field = capa.fields().field(camp)
                        # pyQt és un embolcall de Qt en C++. A C++ els float eren de 32 bits
                        # Els float utilitzen IEEE 754, que permet representar un gran ventall de números, però sense ser del tot exacte
                        # Reproducció de l'error:
                        #   import numpy
                        #   num = numpy.float32(72.32)
                        #   print(float(num)) # imprimeix 72.31999969482422
                        # Per evitar aquest problema, fem un arrodoniment a la precisió que tenia el camp de la base de dades
                        if 'NUMBER' in field.typeName() and not isinstance(feat[camp],QVariant):
                            if  field.precision()>0:
                                try:
                                    res = round(feat[camp], field.precision())
                                except Exception as e:
                                    res = feat[camp]
                            else:
                                try:
                                    res = int(feat[camp])
                                except:
                                    res = feat[camp]
                        else:
                            res = feat[camp]
                        d[camp] = res
                    writer.writerow(d)
        else:
            # avís de que no hi ha capa seleccionada
            # Nota: no és massa bona pràctica tenir la funció en una classe si
            #  també s'utilitzarà des d'altres classes, però segons diu el PEP 20: 
            #   Although practicality beats purity.
            QvSeleccioElement.missatgeCaixa('Cal tenir seleccionat un nivell per poder exportar una selecció','Seleccioneu un nivell, realitzeu una selecció i podreu exportar-la')
            pass
        
    
    def setPreview(self):
        camps = [camp.text() for camp in self.lwFieldsSelect.selectedItems()]
        capa = self.llegenda.currentLayer()
        # capa.selectedFeatures() retorna un iterable amb els elements, però només volem els 20 primers
        # una altra opció seria fer alguna cosa similar a:
        # feats = list(capa.selectedFeatures())[:20]
        # Això ens donaria també els 20 primers elements, però amb un cost molt més gran
        # en cas que tinguéssim molts elements seleccionats, ja que primer fem una llista enorme i després la partim
        # feats = list(itertools.islice(capa.selectedFeatures(),20))
        feats = list(self.llegenda.getLayerVisibleFeatures(capa, max=20))
        self.twPreview.setColumnCount(len(camps))
        self.twPreview.setRowCount(len(feats))
        self.twPreview.setHorizontalHeaderLabels(camps)

        # self.twPreview.horizontalHeader().setResizeMode(QHeaderView.Stretch | QHeaderView.Interactive)
        self.twPreview.horizontalHeader().setStretchLastSection(True)

        for (i,feat) in enumerate(feats):
            for (j,camp) in enumerate(camps):
                self.twPreview.setItem(i,j,QTableWidgetItem(str(feat[camp])))


    def clickArbreSelMasc(self):
        rang = self.distBarrisSelMasc.llegirRang()
        # self.canvas.zoomToFeatureExtent(rang)

        ID = self.distBarrisSelMasc.llegirID()
        path = self.__zones
        if self.distBarrisSelMasc.esDistricte():
            # vLayer = QgsVectorLayer(
            #     'Dades/Districtes.sqlite', 'Districtes_aux', 'ogr')
            path += '|layername=districtes'
        else:
            # vLayer = QgsVectorLayer('Dades/Barris.sqlite', 'Barris_aux', 'ogr')
            path += '|layername=barris'
        vLayer = QgsVectorLayer(path, 'ogr')
        vLayer.setProviderEncoding("UTF-8")
        if not vLayer.isValid():
            return
        vLayer.setSubsetString('CODI="%s"' % ID)
        feats = vLayer.getFeatures()

        if self.checkSeleccio.isChecked():
            # Selecció gràfica
            layer = self.llegenda.currentLayer()
            if layer is None:
                return
            try:
                feat = next(feats)
            except StopIteration: # Si no hi ha cap feature, sortim
                return
            featsPnt = layer.getFeatures(
                QgsFeatureRequest().setFilterRect(rang))
            for f in featsPnt:
                if self.checkOverlap.isChecked():
                    if f.geometry().intersects(feat.geometry()):  # Within? Intersects?
                        layer.select(f.id())
                else:
                    if conteRel(f.geometry(), feat.geometry()):
                        layer.select(f.id())
            self.calcularSeleccio()

        else:
            self.esborrarMascara(False)
            self.aplicaMascara([x.geometry() for x in feats])

    def esborrarSeleccio(self, tambePanCanvas=True):
        'Esborra les seleccions (no els elements) de qualsevol layer del canvas.'
        layers = self.canvas.layers()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()
        # self.lblNombreElementsSeleccionats.setText('No hi ha elements seleccionats.')
        # self.idsElementsSeleccionats = []
        # Movem el self.canvas.panCanvas a una funció que es diu foraEines per poder treure les eines del mapa sense treure les seleccions, màscares...
        if tambePanCanvas:
            self.foraEines()

        try:
            self.canvas.scene().removeItem(self.toolSelect.rubberband)
        except:
            pass
        self.calcularSeleccio()
        if self.tool is not None:
            self.tool.eliminaRubberbands()
    
    def esborrarMascara(self, tambePanCanvas=True):
        if self.llegenda.mask is not None:
            self.llegenda.mask.maskSwitch(False)
            self.llegenda.mask = None
        self.eliminaMascara()
        self.geomMascara = None
        if tambePanCanvas:
            self.foraEines()
        if self.tool is not None:
            for x in [*self.tool.rubberbands, *self.tool.markers]:
                self.canvas.scene().removeItem(x)
        self.canvas.refreshAllLayers()

    def foraEines(self):
        self.canvas.panCanvas()

    def getParametres(self):
        # Falta incloure color i opacitat
        return {'overlap': self.checkOverlap.isChecked(),
                'seleccionar': self.checkSeleccio.isChecked(),
                # 'color':self.color,
                # 'opacitat':qV.sliderOpacitat.value(),
                'emmascarar': self.checkMascara.isChecked()
                }

    def actualitzaTool(self):
        QvMemoria().setParametresMascara(self.color, self.sliderOpacitat.value())
        for tool in (self.einaClick, self.einaCercle, self.einaDibuixa):
            tool.setParametres(self.checkMascara.isChecked(), self.checkSeleccio.isChecked(), self.checkOverlap.isChecked())
        self.gbOverlap.setVisible(self.checkSeleccio.isChecked())
        self.frameColorOpacitat.setVisible(self.checkMascara.isChecked())
        masc = self.obteMascara()
        pars = QvMemoria().getParametresMascara()
        self.aplicaParametresMascara(masc, *pars)

    def setVisible(self, visible):
        super().setVisible(visible)
        if not visible:
            pass
            # qV.foraEinaSeleccio()

    def setInfoLbl(self, txtSelec):
        self.lblCapaSeleccionada.setText(txtSelec)

    def calcularSeleccio(self):

# CPC
# Limpiar si hay cambio de capa activa: qVista.canviLayer()
# Recalcular si hay cambio de visualización en la capa activa: visibilityChanged()
# Coordinar con selección alfanumérica

        layerActiu = self.llegenda.currentLayer()
        if layerActiu is None:
            return
        taula = self.twResultats
        fila = 0
        
        taula.setColumnCount(3)
        taula.setHorizontalHeaderLabels(['', 'Total', 'Mitjana'])
        nombreFieldsSeleccionats = 0

        if len(self.lwFieldsSelect.selectedItems())==0: # Si no hi ha cap item seleccionat, se seleccionen tots
            self.lwFieldsSelect.selectAll()
        # nombreElements = len(layerActiu.selectedFeatures())
        nombreElements = self.llegenda.numLayerVisibleFeatures(layerActiu)
        campsNumerics = [field.name() for field in layerActiu.fields() if field.typeName() in ('Integer64','Real')]
        itemsNumerics = [x for x in self.lwFieldsSelect.selectedItems() if x.text() in campsNumerics]
        # for a in itemsNumerics:
        #     nombreFieldsSeleccionats = nombreFieldsSeleccionats+1
        nombreFieldsSeleccionats = len(itemsNumerics)
        taula.setRowCount(nombreFieldsSeleccionats+1)

        for a in itemsNumerics:
            total = 0
            item = QTableWidgetItem(a.text())
            taula.setItem(fila+1, 0, item)
            # for feature in layer.selectedFeatures():
            #     calcul = feature.attributes(
            #     )[layer.fields().lookupField(a.text())]
            #     total = total+calcul
            # total = sum(feature.attributes()[layerActiu.fields().lookupField(a.text())] for feature in layerActiu.selectedFeatures())
            if nombreElements > 0:
                total = sum(feature.attributes()[layerActiu.fields().lookupField(a.text())] for feature in self.llegenda.getLayerVisibleFeatures(layerActiu))
                mitjana = total / nombreElements
            else:
                mitjana = 0
            item = QTableWidgetItem(str('% 12.2f' % total))
            taula.setItem(fila+1, 1, item)
            item = QTableWidgetItem(str('% 12.2f' % mitjana))
            taula.setItem(fila+1, 2, item)
            # print('Total: '+a.text()+": ",total)
            fila = fila+1
        item = QTableWidgetItem("Seleccionats:")
        taula.setItem(0, 0, item)
        item = QTableWidgetItem(str(nombreElements))
        taula.setItem(0, 1, item)
        self.bs6.setText(f'Crear CSV ({nombreElements} seleccionats)')
        if nombreElements > 0 and layerActiu.hasScaleBasedVisibility():
            aviso = " (s'ignoran els filtres d'escala)"
        else:
            aviso = ""
        self.gbResultats.setTitle(f'{nombreElements} elements seleccionats visibles{aviso}')
        taula.resizeColumnsToContents()

        self.setPreview()

    def calculaFields(self, layerActiu):
        fields = layerActiu.fields()
        for field in fields:
            # if (field.typeName() == 'Real' or field.typeName() == 'Integer64'):
            #     self.lwFieldsSelect.addItem(field.name())
            self.lwFieldsSelect.addItem(field.name())
    def canviLayer(self):
        if self.llegenda.currentLayer() is not None:
            # self.calculaFields()
            self.calcularSeleccio()
        pass
    def hideEvent(self,e):
        super().hideEvent(e)
        self.foraEines() 
        if hasattr(self,'tool') and self.tool is not None:
            self.tool.eliminaRubberbands()
    
    def obteMascara(self):
        mascares = self.projecte.mapLayersByName('Màscara')
        if len(mascares) == 0:
            return self.creaMascara()
        return mascares[0]
    def creaMascara(self):
        epsg = self.canvas.mapSettings().destinationCrs().authid()
        mascara = QgsVectorLayer('MultiPolygon?crs=%s' % epsg, 'Màscara', 'memory')
        self.aplicaParametresMascara(mascara, *QvMemoria().getParametresMascara())

        mascaraAux = QgsVectorLayer(
            'MultiPolygon?crs=%s' % epsg, 'Màscara auxiliar', 'memory')
        rect = self.canvas.fullExtent()
        geom = QgsGeometry().fromRect(rect)
        feat = QgsFeature()
        feat.setGeometry(geom)

        pr = mascaraAux.dataProvider()
        pr.addFeatures([feat])
        mascaraAux.commitChanges()
        self.projecte.addMapLayers([mascaraAux], False)

        self.projecte.addMapLayers([mascara])

        return mascara
    def aplicaParametresMascara(self, mascara, color, opacitat):
        if opacitat > 1:
            opacitat /= 100  # Si és més que 1 vol dir que està en %
        mascara.startEditing()
        mascara.renderer().symbol().setColor(color)
        mascara.renderer().symbol().symbolLayer(0).setStrokeColor(color)
        mascara.setOpacity(opacitat)
        mascara.commitChanges()
    
    def aplicaMascara(self, geoms):
        self.eliminaMascara()
        mascara = self.obteMascara()
        mascaraAux = self.projecte.mapLayersByName('Màscara auxiliar')[0]
        mascara.startEditing()
        if self.geomMascara is None:
            primera_feature = next(mascaraAux.getFeatures())
            self.geomMascara = primera_feature.geometry()
        for x in geoms:
            dif = self.geomMascara.difference(x)
            self.geomMascara = self.geomMascara.difference(x)
        feat = QgsFeature()
        feat.setGeometry(self.geomMascara)
        pr = mascara.dataProvider()

        pr.addFeatures([feat])
        mascara.commitChanges()

        self.llegenda.mask = QvLlegendaMascara(self.llegenda, mascara, 1)
        self.llegenda.mask.maskSwitch(True)
    
    # Elimina la màscara, però desa la geometria definida anteriorment
    # Si es vol eliminar també la geometria, cridar a esborrarMascara
    def eliminaMascara(self):
        try:
            self.projecte.removeMapLayer(self.projecte.mapLayersByName('Màscara')[0])
            self.projecte.removeMapLayer(self.projecte.mapLayersByName('Màscara auxiliar')[0])
        except Exception as e:
            # Si no hi ha màscara, passem
            pass

    def seleccionar(self, ids):
        layer = self.llegenda.currentLayer()
        seleccionats = set(layer.selectedFeatureIds())
        ids = set(ids)
        if ids<=seleccionats:
            aSeleccionar = list(seleccionats-ids)
        else:
            aSeleccionar = list(seleccionats | ids)
        layer.selectByIds(aSeleccionar)
        self.calcularSeleccio()


class QvMesuraGrafica(QWidget):
    '''Widget de fer mesures sobre el mapa'''
    colorCanviat = pyqtSignal(QColor)
    acabatMesurar = pyqtSignal()

    def __init__(self, canvas, llegenda, parent=None):
        QWidget.__init__(self)
        self.parent=parent
        self.canvas = canvas
        self.llegenda = llegenda
        self.setWhatsThis(QvApp().carregaAjuda(self))
        self.lytMesuraGrafica = QVBoxLayout()
        self.lytMesuraGrafica.setAlignment(Qt.AlignTop)
        self.setLayout(self.lytMesuraGrafica)
        self.lytBotonsMesura = QHBoxLayout()

        self.lytMesuraGrafica.addLayout(self.lytBotonsMesura)

        self.lytDistanciesArees = QVBoxLayout()
        self.lytBotonsMesura.addLayout(self.lytDistanciesArees)
        self.lytBotonsMesura.addStretch()

        self.color = QvConstants.COLORDESTACAT
        self.bmSeleccioColor = QvPushButton(flat=True)
        self.bmSeleccioColor.setIcon(QIcon('Imatges/da_color.png'))
        self.bmSeleccioColor.setStyleSheet(
            'background: solid %s; border: none' % self.color.name())
        self.bmSeleccioColor.setIconSize(QSize(25, 25))
        QvConstants.afegeixOmbraWidget(self.bmSeleccioColor)

        def canviColor(color):
            self.color = color
            self.bmSeleccioColor.setStyleSheet(
                'background: solid %s; border: none' % color.name())
            self.colorCanviat.emit(color)

        def openColorDialog():
            canviColor(QColorDialog().getColor())
        self.bm4 = QvPushButton(destacat=False)
        self.bm4.setText('Netejar')

        self.lblDistanciaTotal = QLabel()
        self.setDistanciaTotal(0)
        self.lblMesuraArea = QLabel('')
        self.cbCercles = QCheckBox('Mostrar cercles auxiliars')

        self.lwMesuresHist = QListWidget()
        self.lwMesuresHist.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.lwMesuresHist.setMinimumHeight(50)

        self.twResultatsMesura = QTableWidget()

        self.bmSeleccioColor.clicked.connect(openColorDialog)
        # Si eventualment ho movem a un altre arxiu això no funcionarà
        # Fer el doble connect sembla cutre (i ho és)
        # Però com que esborrarMesures deixava de mesurar, i volem seguir mesurant, doncs ho fem a mà i ja
        # Caldria refactoritzar en algun moment
        self.bm4.clicked.connect(lambda: self.esborrarMesures(True))
        self.bm4.clicked.connect(self.mesuraDistancies)

        self.lytBotonsMesura.addWidget(self.bmSeleccioColor)
        self.lytBotonsMesura.addWidget(self.bm4)
        self.lytDistanciesArees.addWidget(self.lblDistanciaTotal)
        self.lytDistanciesArees.addWidget(self.lblMesuraArea)
        self.lytDistanciesArees.addWidget(self.cbCercles)

        self.lytMesuraGrafica.addWidget(self.lwMesuresHist)
        self.setMinimumWidth(350)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.resize(350, 100)

        self.markers = QgsVertexMarker(self.canvas)
        self.resize(400,150)

    def hide(self):
        super().hide()
        self.acabatMesurar.emit()

    def clear(self):
        return
        self.lwMesuresHist.clear()

    def setDistanciaTotal(self, dist):
        self.dist = max(round(dist, 2), 0)
        self.lblDistanciaTotal.setText(
            'Distància total: ' + str(self.dist) + ' m')

    def setDistanciaTempsReal(self, dist):
        return

    def setArea(self, area):
        if area is None:
            self.lblMesuraArea.setText(
                "Tanqueu un polígon per calcular l'àrea")
            self.area = None
        else:
            self.area = round(area, 2)
            self.lblMesuraArea.setText('Àrea: ' + str(self.area) + ' m²')

    def actualitzaHistorial(self):
        if self.dist == 0:
            return
        if self.area is not None:
            self.lwMesuresHist.insertItem(
                0, 'Distància: %.2f m --- Àrea: %.2f m²' % (self.dist, self.area))
        else:
            self.lwMesuresHist.insertItem(0, 'Distància: %.2f m' % self.dist)
    def showEvent(self,e):
        super().showEvent(e)
        self.bm4.animateClick()
        if self.parent is not None:
            print(self.parent.pos())
            self.move(self.parent.mapToGlobal(self.parent.pos()))

    def obrir(self):
        self.show()

    def tancar(self):
        self.esborrarMesures(True)
        self.canvas.unsetMapTool(self.toolMesura)
    def hideEvent(self,e):
        super().hideEvent(e)
        self.tancar()
    def close(self):
        super().close()
        self.tancar()
    def canviaVisibilitatDw(self, visibilitat):
        if visibilitat:
            self.obrir()
        else:
            self.hide()

    def mesuraDistancies(self):
        layer = self.llegenda.currentLayer()
        self.markers.hide()
        try:
            # qV.esborrarSeleccio()
            self.esborrarMesures()
        except:
            pass

        self.actionMapMesura = QAction('Mesura dibuixant', self)
        self.toolMesura = QvMesuraMultiLinia(self.canvas, layer, self)

        self.toolMesura.setAction(self.actionMapMesura)
        self.canvas.setMapTool(self.toolMesura)

    def esborrarMesures(self, tambePanCanvas=True):

        if tambePanCanvas:
            self.canvas.panCanvas()

        try:
            self.canvas.scene().removeItem(self.toolMesura.rubberband)
            self.canvas.scene().removeItem(self.toolMesura.rubberband2)
            for x in self.toolMesura.rubberbands:
                self.canvas.scene().removeItem(x)
            for x in self.toolMesura.cercles:
                self.canvas.scene().removeItem(x)
            self.canvas.scene().removeItem(self.toolMesura.rubberband)
            self.canvas.scene().removeItem(self.toolMesura.rubberband2)
            self.canvas.scene().removeItem(self.toolMesura.rubberbandCercle)
            self.clear()
            # self.lwMesuresHist.clear()

            for ver in self.toolMesura.markers:
                # if ver in  qV.canvas.scene().items():
                self.canvas.scene().removeItem(ver)
            # taulaAtributs('Total',layer)
            self.setDistanciaTotal(0)
            self.setArea(0)
            self.setDistanciaTempsReal(0)
            # qV.lblDistanciaTotal.setText('Distància total: ')
            # qV.lblMesuraArea.setText('Àrea: ')
            # qV.lblDistanciaTempsReal.setText('Distáncia últim tram: ')
        except:
            pass

# A partir d'aquí, no caldria utilitzar-ho. Se suposa que tot això ho han de gestionar els widgets corresponents. No obstant, en certes situacions pot ser útil tenir les eines i/o les funcions sense els widgets




class QvMascaraEinaPlantilla(QgsMapTool):
    # les rubberbands de totes les instàncies seran compartides
    # això permet que, quan es canvia d'eina, es conservin fins que es fa una nova selecció
    rubberbands = [] 
    markers = []
    # Posem "object" com a tipus genèric. Ha de ser algun tipus d'iterable
    selecciona = pyqtSignal(object) # S'emetrà quan s'hagi de seleccionar, amb una llista d'ids
    emmascara = pyqtSignal(object) # s'emetrà quan s'hagi d'emmascarar, amb una llista de geometries
    def __init__(self, wSeleccioGrafica, projecte, canvas, llegenda, **kwargs):
        QgsMapTool.__init__(self, canvas)
        self.wSeleccioGrafica = wSeleccioGrafica
        self.canvas = canvas
        self.projecte = projecte
        self.llegenda = llegenda
        self.setParametres(**kwargs)
        # self.rubberbands = []

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
        return self.wSeleccioGrafica.obteMascara()

    def actualitza(self):
        return
        try:
            if self.emmascarar and hasattr(self, 'mascara'):
                self.mascara = self.getCapa()
                self.mascara.updateExtents()
                aplicaParametresMascara(
                    self.mascara, self.color, self.opacitat)
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

    def novaRubberband(self, elimina=False):
        if elimina:
            self.eliminaRubberbands()
        rb = QgsRubberBand(self.canvas, True)
        rb.setColor(QvConstants.COLORDESTACAT)
        rb.setWidth(2)
        self.rubberbands.append(rb)
        return rb

    def eliminaRubberbands(self):
        for x in self.rubberbands:
            x.hide()
        for x in self.markers:
            x.hide()
    def __del__(self):
        self.eliminaRubberbands()



class QvMascaraEinaClick(QvMascaraEinaPlantilla):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    
    def checkTool(self):
        layer = self.llegenda.currentLayer()
        if layer is None or layer.type() != QgsMapLayer.VectorLayer:
            check = False
            err = "Cal tenir una capa seleccionada per poder seleccionar o emmascarar fent clicks"
        else:
            check = True
            err = ''
        return check, err

    def canvasReleaseEvent(self, event):
        # Get the click
        self.eliminaRubberbands()
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
                    geoms = [x.geometry() for x in items]

                    self.emmascara.emit(geoms)
                if self.seleccionar:
                    # seleccionats = layer.selectedFeatureIds()
                    # layer.selectByIds(seleccionats+ids)
                    # self.wSeleccioGrafica.calcularSeleccio()
                    self.selecciona.emit(ids)
                # La part d'eliminar funciona màgicament. No existeix cap raó lògica que ens digui que s'eliminarà, però ho fa
                self.actualitza()
            except Exception as e:
                print(e)
        else:
            self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                               'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # TODO: Crear una altra excepció més específica
            raise Exception("No hi havia nivell seleccionat")


class QvMascaraEinaDibuixa(QvMascaraEinaPlantilla):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = []
        self.point = None
        self.rubberband = self.novaRubberband()
    
    def checkTool(self):
        layer = self.llegenda.currentLayer()
        if layer is None and self.seleccionar:
            check = False
            err = 'Cal tenir una capa seleccionada per poder fer seleccions'
        else:
            check = True
            err = ''
        return check, err

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            if len(self.points)>2:
                self.point = self.points[0]
            elif len(self.points)==0:
                return
            else:
                # netejar
                pass
        else:
            if self.point is None:
                self.rubberband = self.novaRubberband()
                self.points = []
            self.point = self.toMapCoordinates(event.pos())
        self.points.append(QgsPointXY(self.point))
        if len(self.points) == 1:
            self.posB = event.pos()
        self.selectPoly()
        if len(self.points) > 2 and self.qpointsDistance(self.toCanvasCoordinates(self.points[0]), self.toCanvasCoordinates(self.points[-1])) < 10:
            self.tancarPoligon()

    def canvasMoveEvent(self, event):
        poligono = QgsGeometry.fromPolylineXY(
            self.points+[self.toMapCoordinates(event.pos())])
        try:
            if self.point is None:
                return
            self.rubberband.setToGeometry(
                poligono, self.getCapa())  # falta establir la layer
        except Exception as e:
            print(e)

    def tancarPoligon(self):
        try:

            list_polygon = []
            self.selectPoly()
            self.points = self.points[:-1]
            for x in self.points:
                list_polygon.append(QgsPointXY(x))
            geom = QgsGeometry.fromPolygonXY([list_polygon])
            if self.emmascarar:
                self.emmascara.emit([geom])
            layer = self.llegenda.currentLayer()
            if self.seleccionar and layer is not None:
                # Seleccionem coses
                featsPnt = layer.getFeatures(
                    QgsFeatureRequest().setFilterRect(geom.boundingBox()))
                # for featPnt in featsPnt:
                #     if self.overlap:
                #         if featPnt.geometry().intersects(geom):
                #             layer.select(featPnt.id())
                #     else:
                #         if featPnt.geometry().within(geom):
                #             layer.select(featPnt.id())
                if self.overlap:
                    ids = (featPnt.id() for featPnt in featsPnt if featPnt.geometry().intersects(geom))
                else:
                    ids = (featPnt.id() for featPnt in featsPnt if featPnt.geometry().within(geom))
                self.selecciona.emit(ids)
                # self.wSeleccioGrafica.calcularSeleccio()
            # self.rubberband.hide()
            # self.rubberband = self.novaRubberband()
            self.actualitza()
            self.point = None
            # self.points = []
        except Exception as e:
            print(e)

    def selectPoly(self):
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
        # self.rubberbandRadi = self.novaRubberband()
        self.rubberbandCercle = self.novaRubberband()
        self.centre = None
        self.cercleFixe = False
        self.radiCercle = 0
    
    def checkTool(self):
        layer = self.llegenda.currentLayer()
        if layer is None and self.seleccionar:
            check = False
            err = 'Cal tenir seleccionat un nivell per poder fer una selecció'
        else:
            check = True
            err = ''
        return check, err

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Tancar polígon??
            return
        if self.cercleFixe:
            centre = self.toMapCoordinates(event.pos())
            
            poligon, _ = self.getPoligon(centre,centre+QgsVector(self.radiCercle,0),100)
            # self.rbcircle(centre, centre+QgsVector(self.radiCercle,0))
            self.rubberbandCercle = self.novaRubberband()
            if self.emmascarar:
                self.emmascara.emit([poligon])
            if self.seleccionar:
                self.seleccionaPoligon(poligon)
            
        elif self.centre is None:
            self.rubberbandCercle = self.novaRubberband()
            self.rubberbandRadi = self.novaRubberband()
            self.points = []
        self.centre = self.toMapCoordinates(event.pos())
        self.marker(self.centre)

    def canvasMoveEvent(self, event):
        if self.cercleFixe:
            centre = self.toMapCoordinates(event.pos())
            self.rbcircle(centre, centre+QgsVector(self.radiCercle,0))
        elif self.centre is not None:
            punt = self.toMapCoordinates(event.pos())
            self.rbcircle(self.centre, punt)
            dist = self.centre.distance(punt)
            self.wSeleccioGrafica.leRadiCercle.setText(str(int(dist)))

    def canvasReleaseEvent(self, event):
        if event.button()==Qt.RightButton:
            return
        poligon, _ = self.getPoligon(self.centre, self.toMapCoordinates(event.pos()), 100)
        if self.emmascarar:
            self.emmascara.emit([poligon])
            # self.emmascaraPoligon(poligon)
        
        if self.seleccionar:
            # self.selecciona.emit([poligon])
            self.seleccionaPoligon(poligon)
        self.centre = None
        self.actualitza()
        # self.rubberbandCercle.hide()

    def seleccionaPoligon(self,poligon):
        layer = self.llegenda.currentLayer()
        if layer is not None:
            featsPnt = layer.getFeatures(
                QgsFeatureRequest().setFilterRect(poligon.boundingBox()))
            if self.overlap:
                ids = (featPnt.id() for featPnt in featsPnt if featPnt.geometry().intersects(poligon))
            else:
                ids = (featPnt.id() for featPnt in featsPnt if featPnt.geometry().within(poligon))
            self.selecciona.emit(ids)

    def rbcircle(self, center, edgePoint, segments=100):
        try:
            self.rubberbandCercle.reset(True)
        except:
            pass
        self.poligon, llistaPunts = self.getPoligon(
            center, edgePoint, segments)
        for x in llistaPunts:
            self.rubberbandCercle.addPoint(x)

    def marker(self, centre):
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(centre)
        marker.setPenWidth(2)
        self.markers.append(marker)
        return marker
    def getPoligon(self, center, edgePoint, segments):
        if center is None:
            return
        r = math.sqrt(center.sqrDist(edgePoint))
        llistaPunts = []
        pi = 3.1416
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            llistaPunts.append(QgsPointXY(
                center.x()+r*math.cos(theta), center.y()+r*math.sin(theta)))
        return QgsGeometry.fromPolygonXY([llistaPunts[:-2]]), llistaPunts
    



class QvMesuraMultiLinia(QgsMapTool):
    def __init__(self, canvas, layer, parent):
        self.parent = parent
        self.canvas = canvas
        self.layer = layer
        # self.qV = qV
        #dock = QgsAdvancedDigitizingDockWidget(self.canvas)
        #QgsMapToolAdvancedDigitizing.__init__(self, self.canvas, dock)
        QgsMapTool.__init__(self, self.canvas)
        self.rubberband = self.creaRubberband()
        # self.rubberband.setIconType(QgsVertexMarker.ICON_CIRCLE)

        self.rubberband2 = self.creaRubberband()

        self.rubberbandCercle = self.creaRubberband(cercle=True)

        self.rubberbands = []
        self.cercles = []

        self.point = None
        self.lastPoint = None
        self.points = []
        self.overlap = False
        self.markers = []
        self.startMarker = None
        self.startPoint = None
        self.lastLine = None
        self.hoverSartMarker = None

        self.parent.clear()

        self.parent.colorCanviat.connect(self.canviColor)

    def canviColor(self, color):
        # De moment conservem el color del que ja teníem dibuixat
        # Si més endavant es vol modificar només cal descomentar les línies inferiors
        # for x in self.rubberbands:
        #     x.setColor(color)
        # for x in self.cercles:
        #     x.setColor(color)
        self.rubberband.setColor(color)
        self.rubberband2.setColor(color)
        self.rubberbandCercle.setColor(color)

    def setOverlap(self, overlap):
        self.overlap = overlap

    def qpointsDistance(self, p, q):
        dx = p.x() - q.x()
        dy = p.y() - q.y()
        dist = math.sqrt(dx*dx + dy*dy)
        return dist

    def canvasDoubleClickEvent(self, e):
        # Tancar polígon (de moment no es fa)
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

        # if self.point != None:

    def treuUltimtram(self):
        poligono = QgsGeometry.fromPolylineXY(self.points)
        distancia = poligono.length()
        if self.point is None:
            return False
        self.point = None
        self.points = []
        self.hoverSartMarker = False

        self.rubberband2.hide()
        self.rubberbandCercle.hide()

        self.parent.setDistanciaTotal(distancia)
        self.parent.actualitzaHistorial()
        self.parent.setDistanciaTempsReal(0)
        self.parent.setDistanciaTotal(0)
        self.parent.setArea(0)
        return True

    def novaRubberband(self):
        self.rubberbands.append(self.rubberband)
        self.rubberband = None
        self.rubberband = self.creaRubberband()

    def creaRubberband(self, cercle=False):
        rubberband = QgsRubberBand(self.canvas)
        rubberband.setColor(self.parent.color)
        if cercle:
            rubberband.setWidth(0.25)
            rubberband.setLineStyle(Qt.DashLine)
        else:
            rubberband.setWidth(2)
        rubberband.setIconSize(4)
        return rubberband

    def rbcircle(self, center, edgePoint, desar=False, segments=100):
        r = math.sqrt(center.sqrDist(edgePoint))
        self.rubberbandCercle.reset(True)
        if not self.parent.cbCercles.isChecked():
            return
        pi = 3.1416
        llistaPunts = []
        for itheta in range(segments+1):
            theta = itheta*(2.0 * pi/segments)
            self.rubberbandCercle.addPoint(QgsPointXY(
                center.x()+r*math.cos(theta), center.y()+r*math.sin(theta)))
            llistaPunts.append(QgsPointXY(
                center.x()+r*math.cos(theta), center.y()+r*math.sin(theta)))
        self.poligono = QgsGeometry.fromPolygonXY([llistaPunts])
        if desar:
            self.cercles.append(self.rubberbandCercle)
            self.rubberbandCercle = self.creaRubberband(cercle=True)
            # self.cercles.append(QgsRubberBand(rb))

    def canvasPressEvent(self, e):

        if e.button() == Qt.RightButton:
            if not self.treuUltimtram():
                self.parent.hide()

        else:
            if self.hoverSartMarker:
                self.rbcircle(self.point, self.startPoint, desar=True)
                self.point = self.startPoint
                self.points.append(QgsPointXY(self.point))
                self.tancarPoligon()

            else:
                pointOld = self.point
                self.point = self.toMapCoordinates(e.pos())
                if pointOld is not None:
                    self.rbcircle(pointOld, self.point, desar=True)
                self.points.append(QgsPointXY(self.point))

                self.selectPoly(e)
                self.parent.setArea(None)

    def tancarPoligon(self):
        try:

            # create  float polygon --> construcet out of 'point'
            list_polygon = QPolygonF()

            for x in self.points:
                # since there is no distinction between x and y values we only want every second value
                list_polygon.append(x.toQPointF())

            geomP = QgsGeometry.fromQPolygonF(list_polygon)

            poligono = QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(poligono, self.layer)
            self.rubberband.show()
            self.novaRubberband()

            distancia = geomP.length()
            area = geomP.area()

            self.parent.setDistanciaTotal(distancia)
            self.parent.setArea(area)

            self.point = None
            self.points = []
            self.hoverSartMarker = False

            self.rubberband2.hide()
            self.parent.actualitzaHistorial()
            # self.treuUltimtram()

        except Exception as e:
            # error tancant el polígon
            pass
            # print('Error al tancar el polygon')
            # print(e.__str__)

    def selectPoly(self, e):
        try:

            firstMarker = False
            poligono = QgsGeometry.fromPolylineXY(self.points)
            self.rubberband.setToGeometry(poligono, self.layer)
            self.rubberband.show()
            distancia = poligono.length()
            if distancia <= 0:
                distancia = 0
                self.parent.clear()
                firstMarker = True

                for ver in self.markers:
                    self.canvas.scene().removeItem(ver)

                self.markers = []
            self.parent.setDistanciaTotal(distancia)

            if distancia > 0 and (self.lastLine is not None and round(self.lastLine.length(), 2) > 0):
                self.parent.setDistanciaTempsReal(0)
                self.parent.setDistanciaTotal(distancia)

                self.lastLine = QgsGeometry.fromPolylineXY(
                    [self.lastPoint, self.lastPoint])

            m = QvMarcador(self.canvas)

            m.setColor(QColor(36, 97, 50))
            m.setFillColor(QColor(36, 97, 50))
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
            # Error mesurant
            pass
            # print('ERROR. Error al mesurar ')

    def showlastLine(self, snapingPoint=None):
        if snapingPoint is None:
            listaPoligonos = [self.point, self.lastPoint]
        else:
            listaPoligonos = [self.point, snapingPoint]
        self.lastLine = QgsGeometry.fromPolylineXY(listaPoligonos)
        self.rubberband2.setToGeometry(self.lastLine, self.layer)
        self.rubberband2.show()
        self.rbcircle(self.point, self.lastPoint)
        distancia = self.lastLine.length()
        if distancia <= 0:
            distancia = 0
        poligono = QgsGeometry.fromPolylineXY(self.points)
        if poligono.isGeosValid():
            distTotal = poligono.length()
        else:
            distTotal = 0
        self.parent.setDistanciaTempsReal(distancia)
        self.parent.setDistanciaTotal(distTotal+distancia)


class QvMarcador (QgsVertexMarker):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsVertexMarker.__init__(self, self.canvas)

    def mouseMoveOver(self):
        self.setColor(QColor(199, 239, 61))
        self.setFillColor(QColor(199, 239, 61))

    def mouseOverRelease(self):
        self.setColor(QColor(36, 97, 50))
        self.setFillColor(QColor(36, 97, 50))


class QvSeleccioElement(QgsMapTool):
    """Aquesta clase és un QgsMapTool que selecciona l'element clickat. 

       Si la llegenda no té un layer actiu, és treballa amb el primer visible al canvas.
    """

    elementsSeleccionats = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject') # layer, features

    def __init__(self, canvas, llegenda, radi=10, senyal=False):
        """[summary]

        Arguments:
            canvas {QgsMapCanvas} -- El canvas de la app
            llegenda {QvLlegenda} -- La llegenda de la app

        Keyword Arguments:
            radi {int} -- [El radi de tolerancia de la seleccio (default: 20)
            senyal {bool} -- False: mostra fitxa del(s) element(s) seleccionat(s)
                             True: llença un senyal (default: False)
        """

        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.llegenda = llegenda
        self.radi = radi
        self.senyal = senyal
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

    @staticmethod
    def missatgeCaixa(textTitol, textInformacio):
        msgBox = QMessageBox()
        msgBox.setText(textTitol)
        msgBox.setInformativeText(textInformacio)
        msgBox.exec()

    def heCerradoFicha(self):  # ???
        bb = self.parent()

        bb.pare.esborrarSeleccio(tambePanCanvas=False)

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
                QMessageBox.warning(self.canvas, "No hi ha capa activa",
                                    "S'ha de seleccionar una capa a la llegenda per poder veure l'informació del seus objectes")
                return
            if layer.geometryType() == QgsWkbTypes.NullGeometry:
                QMessageBox.warning(self.canvas, "Capa activa sense geometria",
                                    "Seleccioni una capa amb geometria a la llegenda abans de clicar sobre el mapa")
                return

            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

            pnt= QgsPointXY(x,y) 
            alfa=180+45  # 45, para que sea cuadrado, 180 por distinto punto origen angulos
            pntEsquerraDalt = pnt.project(self.radi, alfa - self.canvas.rotation())
            esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(round(pntEsquerraDalt.x()),  round(pntEsquerraDalt.y()))

            alfa=alfa+180
            pntDretaBaix = pnt.project(self.radi, alfa - self.canvas.rotation())
            dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(round(pntDretaBaix.x()), round(pntDretaBaix.y()))

            marcaLloc = QgsVertexMarker(self.canvas)
            marcaLloc.setCenter( point )
            marcaLloc.setColor(QColor(255, 0, 0))
            marcaLloc.setIconSize(15)
            marcaLloc.setIconType(QgsVertexMarker.ICON_CROSS) # or ICON_CROSS, ICON_X
            marcaLloc.setPenWidth(0)
            marcaLloc.show()
          

            rect = QgsRectangle(point.x() - self.radi, point.y() - self.radi, point.x() + self.radi, point.y() + self.radi)
            rect = QgsRectangle(esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())

            rb = QgsRubberBand(self.canvas, True)
            rb.setToGeometry(QgsGeometry().fromRect(rect))


            # import math
            # pi =3.1416
            # llistaPunts=[]
            # theta = 1*(2.0 * pi/360)
            # segments=360
            
            # for itheta in range(segments+1):
            #     theta = itheta*(2.0 * pi/segments)
            #     xx= point.x()+self.radi*math.cos(theta)
            #     yy= point.y()+self.radi*math.sin(theta)
            #     llistaPunts.append(QgsPointXY(xx,yy))
            
            # polygon= QgsGeometry.fromPolygonXY([llistaPunts])
            # rb = QgsRubberBand(self.canvas, True)            
            # rb.setToGeometry(polygon)

            rb.show()
            # ids=[]
            features = []
            if layer is not None and layer.type() == QgsMapLayer.VectorLayer:
                # per defecte calcula la intersecció utilitzant les bounding box. Forcem a que ho faci amb una intersecció exacta
                it = layer.getFeatures(QgsFeatureRequest().setFilterRect(rect).setFlags(QgsFeatureRequest.ExactIntersect))

                for feature in it:
                    # ids.append(feature.id())
                    features.append(feature)

                # ids = [i.id() for i in it]
                # layer.selectByIds(ids)

                if len(features) > 0:
                    if self.senyal:
                        self.elementsSeleccionats.emit(layer, features)
                    else:
                        self.fitxaAtributs = QvFormAtributs.create(layer, features, self.canvas, self.llegenda.atributs)
                        self.fitxaAtributs.exec_()
                        self.fitxaAtributs = None
            else:
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                                   'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
            # per alguna raó abans desapareixien sols, però ara no. Per tant, fem un hide i ja està
            marcaLloc.hide()
            rb.hide()
            marcaLloc.deleteLater()
            rb.deleteLater()
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
    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp
    from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas
    from qgis.PyQt.QtGui import QPushButton
    from moduls.QvCanvas import QvCanvas
    from moduls.QvLlegenda import QvLlegenda
    with qgisapp() as app:
        # canvas = QgsMapCanvas()
        canvas = QvCanvas(llistaBotons=["panning","zoomIn","zoomOut"])

        project = QgsProject.instance()
        projecteInicial = './mapesOffline/qVista default map.qgs'
        project.read(projecteInicial)
        root = project.layerTreeRoot()
        bridge = QgsLayerTreeMapCanvasBridge(root, canvas)

        llegenda = QvLlegenda()
        llegenda.show()
        canvas.show()
        wSeleccio = QvSeleccioGrafica(canvas,project,llegenda)
        wMesures = QvMesuraGrafica(canvas,llegenda,wSeleccio)

        lay = QHBoxLayout()
        layV = QVBoxLayout()
        layV.addWidget(llegenda)
        layH = QHBoxLayout()
        bSeleccio = QPushButton('Selecció gràfica')
        bSeleccio.clicked.connect(wSeleccio.show)
        bMesures = QPushButton('Mesura gràfica')
        bMesures.clicked.connect(wMesures.show)
        layH.addWidget(bSeleccio)
        layH.addWidget(bMesures)
        layV.addLayout(layH)
        lay.addLayout(layV)
        lay.addWidget(canvas)
        wid = QWidget()
        wid.setLayout(lay)
        wid.show()