from moduls.QvImports import *
from moduls.QvAtributs import QvFitxesAtributs
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton
from moduls.QvMemoria import QvMemoria
from moduls.QvConstants import QvConstants
from moduls.QVDistrictesBarris import QVDistrictesBarris
from moduls import QvFuncions
from qgis.gui import QgsMapTool, QgsRubberBand
import math
import csv
import itertools


class QvSeleccioGrafica(QWidget):
    '''Widget de seleccionar i emmascarar'''
    __zones = r'Dades\Zones.gpkg'
    def __init__(self, canvas, projecte, llegenda):
        QWidget.__init__(self)
        self.canvas = canvas
        self.llegenda = llegenda
        self.projecte = projecte
        self.interficie()

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
        self.bs1.setIcon(QIcon(os.path.join(imatgesDir,'apuntar.png')))
        self.bs1.setToolTip('Seleccionar elements de la capa activa')
        self.bs2 = QvPushButton(flat=True)
        # self.bs2.setCheckable(True)
        self.bs2.setIcon(QIcon(os.path.join(imatgesDir,'shape-polygon-plus.png')))
        self.bs2.setToolTip('Dibuixar un polígon')
        self.bs3 = QvPushButton(flat=True)
        # self.bs3.setCheckable(True)
        self.bs3.setIcon(QIcon(os.path.join(imatgesDir,'vector-circle-variant.png')))
        self.bs3.setToolTip('Dibuixar un cercle')
        self.bs4 = QvPushButton('Netejar')
        # self.bs4.setCheckable(True)
        # self.bs4.setIcon(QIcon(imatgesDir+'trash-can-outline.png'))

        # self.lblNombreElementsSeleccionats = QLabel('No hi ha elements seleccionats.')
        self.lblCapaSeleccionada = QLabel('No hi capa seleccionada.')

        self.lwFieldsSelect = QListWidget()
        self.lwFieldsSelect.setSelectionMode(
            QAbstractItemView.ExtendedSelection)

        self.bs5 = QvPushButton('Calcular', flat=True)
        self.bs5.clicked.connect(self.calcularSeleccio)

        self.bs6 = QvPushButton('Crear CSV', flat=True)
        self.bs6.clicked.connect(lambda: self.crearCsv())

        # Tool Box de resultats, on afegirem múltiples pestanyes
        self.tbResultats = QToolBox()
        self.gbResultats = QGroupBox('Hola :D')
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
        lblPreview = QLabel('Previsualització del contingut seleccionat. En aquesta taula es visualitzen els 20 primers elements seleccionats')
        lblPreview.setWordWrap(True)
        layPreview.addWidget(lblPreview)
        layPreview.addWidget(self.twPreview)
        widPreview = QWidget()
        widPreview.setLayout(layPreview)

        # Arbre de selecció
        self.distBarrisSelMasc = QVDistrictesBarris()
        self.distBarrisSelMasc.view.clicked.connect(self.clickArbreSelMasc)

        layCamps = QVBoxLayout()
        lblCamps = QLabel('Seleccioneu els camps dels que voleu fer-ne una extracció a un arxiu CSV')
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
        self.bs1.clicked.connect(lambda x: seleccioClicks(self))
        self.bs2.clicked.connect(lambda x: seleccioLliure(self))
        self.bs3.clicked.connect(lambda x: seleccioCercle(self))
        self.bs4.clicked.connect(lambda: self.esborrarSeleccio(True, True))

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

    
    @QvFuncions.mostraSpinner
    def crearCsv(self):
        camps = [camp.text() for camp in self.lwFieldsSelect.selectedItems()]
        if camps==[]:
            # Queixar-nos de que no hi ha cap camp
            pass
        nfile, _ = QFileDialog.getSaveFileName(None, "Desar arxiu CSV", ".", "Arxius CSV (*.csv)")
        if nfile=='': return
        
        capa = self.llegenda.currentLayer()
        feats = capa.selectedFeatures()
        with open(nfile,'w', newline='') as f:
            writer = csv.DictWriter(f,fieldnames=camps, delimiter=';')
            writer.writeheader()
            for feat in feats:
                d = {}
                for camp in camps:
                    d[camp] = feat[camp]
                writer.writerow(d)
    
    def setPreview(self):
        camps = [camp.text() for camp in self.lwFieldsSelect.selectedItems()]
        capa = self.llegenda.currentLayer()
        # capa.selectedFeatures() retorna un iterable amb els elements, però només volem els 20 primers
        # una altra opció seria fer alguna cosa similar a:
        # feats = list(capa.selectedFeatures())[:20]
        # Això ens donaria també els 20 primers elements, però amb un cost molt més gran
        # en cas que tinguéssim molts elements seleccionats, ja que primer fem una llista enorme i després la partim
        feats = list(itertools.islice(capa.selectedFeatures(),20))
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
                if self.checkOverlap:
                    if f.geometry().intersects(feat.geometry()):  # Within? Intersects?
                        layer.select(f.id())
                else:
                    if f.geometry().within(feat.geometry()):  # Within? Intersects?
                        layer.select(f.id())
            self.calcularSeleccio()

        else:
            eliminaMascara(self.projecte)
            # mascara=obteMascara(self)
            aplicaMascara(self.projecte, self.canvas, [
                          x.geometry() for x in feats])

    def esborrarSeleccio(self, tambePanCanvas=True, mascara=False):
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
        if mascara:
            try:
                # qV.project.removeMapLayer(qV.project.mapLayersByName('Màscara')[0])
                eliminaMascara(self.projecte)
                self.canvas.refresh()
            except Exception as e:
                print(e)

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

    def setTool(self, tool):
        self.tool = tool

    def actualitzaTool(self):
        QvMemoria().setParametresMascara(self.color, self.sliderOpacitat.value())
        self.gbOverlap.setVisible(self.checkSeleccio.isChecked())
        self.frameColorOpacitat.setVisible(self.checkMascara.isChecked())
        masc = obteMascara(self.projecte, self.canvas)
        pars = QvMemoria().getParametresMascara()
        aplicaParametresMascara(masc, *pars)

    def setVisible(self, visible):
        super().setVisible(visible)
        if not visible:
            pass
            # qV.foraEinaSeleccio()

    def setInfoLbl(self, txtSelec):
        self.lblCapaSeleccionada.setText(txtSelec)

    def calcularSeleccio(self):
        layer = self.llegenda.currentLayer()
        taula = self.twResultats
        numeroFields = 0  # ???
        fila = 0
        columna = 0  # ???
        nombreElements = 0
        taula.setColumnCount(3)
        taula.setHorizontalHeaderLabels(['', 'Total', 'Mitjana'])
        nombreFieldsSeleccionats = 0

        if len(self.lwFieldsSelect.selectedItems())==0: # Si no hi ha cap item seleccionat, se seleccionen tots
            self.lwFieldsSelect.selectAll()
        layerActiu = self.llegenda.currentLayer()
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
            # print (field)
            nombreElements = 0
            for feature in layer.selectedFeatures():
                calcul = feature.attributes(
                )[layer.fields().lookupField(a.text())]
                total = total+calcul
                nombreElements = nombreElements+1
            if nombreElements > 0:
                mitjana = total/nombreElements
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
        self.bs6.setText(f'Crear CSV ({nombreElements} seleccionats=')
        taula.resizeColumnsToContents()

        self.setPreview()

    def calculaFields(self, layerActiu):
        fields = layerActiu.fields()
        for field in fields:
            # if (field.typeName() == 'Real' or field.typeName() == 'Integer64'):
            #     self.lwFieldsSelect.addItem(field.name())
            self.lwFieldsSelect.addItem(field.name())


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


class MascaraAux:
    # Una classe per encapsular variables i coses
    teAux = False
    geom = None
    projecte = None
    canvas = None




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
    MascaraAux.projecte = projecte
    mascares = projecte.mapLayersByName('Màscara')
    if len(mascares) == 0:
        return creaMascara(projecte, canvas)
    return mascares[0]


# Inutilitzada
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
        wSeleccioGrafica.canvas.scene().removeItem(
            wSeleccioGrafica.toolSelect.rubberband)
    except:
        pass
    try:
        wSeleccioGrafica.toolSelect = QvMascaraEinaCercle(
            wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas, wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
        wSeleccioGrafica.setTool(wSeleccioGrafica.toolSelect)
        wSeleccioGrafica.canvas.setMapTool(wSeleccioGrafica.toolSelect)
    except Exception as e:
        print(e)
        pass


def seleccioClicks(wSeleccioGrafica):
    seleccioClick()
    try:
        wSeleccioGrafica.canvas.scene().removeItem(
            wSeleccioGrafica.toolSelect.rubberband)
    except:
        pass

    try:
        tool = QvMascaraEinaClick(wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas,
                                  wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
        wSeleccioGrafica.setTool(tool)
        wSeleccioGrafica.canvas.setMapTool(tool)
    except Exception as e:
        print(e)
        pass


def seleccioLliure(wSeleccioGrafica):
    # qV.markers.hide()
    try:
        # Això no hauria de funcionar
        wSeleccioGrafica.esborrarSeleccio()
    except:
        pass

    try:
        wSeleccioGrafica.actionMapSelect = QAction(
            'Seleccionar dibuixant', wSeleccioGrafica)
        # qV.toolSelect = QvSeleccioPerPoligon(qV,qV.canvas, layer)
        wSeleccioGrafica.tool = QvMascaraEinaDibuixa(
            wSeleccioGrafica, wSeleccioGrafica.projecte, wSeleccioGrafica.canvas, wSeleccioGrafica.llegenda, **wSeleccioGrafica.getParametres())
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
        self.wSeleccioGrafica = wSeleccioGrafica
        self.canvas = canvas
        self.projecte = projecte
        self.llegenda = llegenda
        self.setParametres(**kwargs)
        self.rubberbands = []

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
        for x in self.rubberbands:
            x.hide()


class QvMascaraEinaClick(QvMascaraEinaPlantilla):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

                    aplicaMascara(self.projecte, self.canvas,
                                  geoms, self.getCapa())
                if self.seleccionar:
                    seleccionats = layer.selectedFeatureIds()
                    layer.selectByIds(seleccionats+ids)
                    self.wSeleccioGrafica.calcularSeleccio()
                # La part d'eliminar funciona màgicament. No existeix cap raó lògica que ens digui que s'eliminarà, però ho fa
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
                aplicaMascara(self.projecte, self.canvas,
                              [geom], self.getCapa())
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
            aplicaMascara(self.projecte, self.canvas,
                          [poligon], self.getCapa())

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

    def __init__(self, canvas, llegenda, radi=10):
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

    def missatgeCaixa(self, textTitol, textInformacio):
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
                layer = self.canvas.layers()[0]

            # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            if self.canvas.rotation() == 0:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(x -
                                                                                     self.radi, y-self.radi)
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(x +
                                                                                  self.radi, y+self.radi)
            else:
                esquerraDalt = self.canvas.getCoordinateTransform().toMapCoordinates(
                    x-self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))
                dretaBaix = self.canvas.getCoordinateTransform().toMapCoordinates(
                    x+self.radi*math.sqrt(2), y-self.radi*math.sqrt(2))

            # marcaLloc = QgsVertexMarker(self.canvas)
            # marcaLloc.setCenter( point )
            # marcaLloc.setColor(QColor(255, 0, 0))
            # marcaLloc.setIconSize(15)
            # marcaLloc.setIconType(QgsVertexMarker.ICON_CROSS) # or ICON_CROSS, ICON_X
            # marcaLloc.setPenWidth(0)
            # marcaLloc.show()
            # return

            # rect = QgsRectangle(point.x() - self.radi, point.y() - self.radi, point.x() + self.radi, point.y() + self.radi)
            rect = QgsRectangle(
                esquerraDalt.x(), esquerraDalt.y(), dretaBaix.x(), dretaBaix.y())
            # ids=[]
            features = []
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
                self.missatgeCaixa('Cal tenir seleccionat un nivell per poder fer una selecció.',
                                   'Marqueu un nivell a la llegenda sobre el que aplicar la consulta.')
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
    from qgis.gui import QgsLayerTreeMapCanvasBridge
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvCanvas import QvCanvas
    from qgis.gui import QgsMapCanvas
    from qgis.core import QgsProject
    from qgis.core.contextmanagers import qgisapp
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
        wMesures = QvMesuraGrafica(canvas,llegenda,bSeleccio)

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