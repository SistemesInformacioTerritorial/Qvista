import glob
import math
import time
from time import strftime
from pathlib import Path
import os
import re
from functools import reduce
from typing import List, Optional


from qgis.core import (QgsGeometry, QgsLayout, QgsLayoutExporter, QgsPointXY,
                       QgsProject, QgsReadWriteContext, QgsVector,
                       QgsVectorLayer, QgsLayoutItemLabel)
from qgis.core.contextmanagers import qgisapp
from qgis.gui import (QgsLayerTreeMapCanvasBridge, QgsMapCanvas, QgsMapTool,
                      QgsRubberBand)
from qgis.PyQt.QtCore import QFile, QUrl
from qgis.PyQt.QtGui import QColor, QDesktopServices
from qgis.PyQt.QtWebKitWidgets import QWebPage, QWebView  # ???
from qgis.PyQt.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                                 QVBoxLayout, QWidget)
from qgis.PyQt.QtXml import QDomDocument

from configuracioQvista import pathPlantilles, tempdir
import configuracioQvista
from moduls.QvApp import QvApp
from moduls.QvPushButton import QvPushButton
from moduls import QvFuncions

projecteInicial='../dades/projectes/BCN11_nord.qgs'


class PointTool(QgsMapTool):
    def __init__(self, parent, canvas, layer):
        QgsMapTool.__init__(self, canvas)
        self.parent = parent
        self.canvas = canvas
        self.layer = layer
        self.rubberband = QgsRubberBand(self.canvas)
        self.rubberband.setColor(QColor(0,0,0,50))
        self.rubberband.setWidth(4)
        self.pucMoure = True
        self.incX, self.incY = None, None

        self.activated.connect(self.rubberband.show)
        self.deactivated.connect(self.rubberband.hide)


    def canvasMoveEvent(self, event):
        self.parent.dockX = event.pos().x()
        self.parent.dockY = event.pos().y()
        # print (x, y)
        # self.parent.move(x, y)

        # point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        p = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y()) # comprovar que sigui així
        if self.pucMoure:
            if self.canvas.rotation()==0:
                self.posXY = [p.x()+self.incX/2, p.y()+self.incY/2]
                self.rubberband.movePoint(0,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
                self.rubberband.movePoint(1,QgsPointXY(p.x()+self.incX,p.y()),0)
                self.rubberband.movePoint(2,QgsPointXY(p.x(),p.y()),0)
                self.rubberband.movePoint(3,QgsPointXY(p.x(),p.y()+self.incY),0)
                self.rubberband.movePoint(4,QgsPointXY(p.x()+self.incX,p.y()+self.incY),0)
            else:
                alpha=math.radians(self.canvas.rotation())
                beta=math.atan(self.incY/self.incX)
                d=math.sqrt(self.incX**2+self.incY**2)
                self.posXY = [(2*p.x()+d*math.cos(alpha+beta))/2,(2*p.y()+d*math.sin(alpha+beta))/2]
                self.rubberband.movePoint(0,QgsPointXY(p.x()+d*math.cos(alpha+beta),p.y()+d*math.sin(alpha+beta)),0)
                self.rubberband.movePoint(1,QgsPointXY(p.x()+self.incX*math.cos(alpha),p.y()+self.incX*math.sin(alpha)),0)
                self.rubberband.movePoint(2,QgsPointXY(p.x(),p.y()),0)
                self.rubberband.movePoint(3,QgsPointXY(p.x()+self.incY*math.cos(math.radians(90+45)),p.y()+self.incY*math.sin(math.radians(90+45))),0)
                self.rubberband.movePoint(4,QgsPointXY(p.x()+d*math.cos(alpha+beta),p.y()+d*math.sin(alpha+beta)),0)
            self.rubberband.show()

    def canvasReleaseEvent(self, event):
        
        self.point = self.toMapCoordinates(event.pos())

        self.potsMoure(False)
    
    def potsMoure(self, pucMoure=True):
        self.pucMoure = pucMoure
    
    def setIncXY(self, incX, incY):
        self.incX = incX
        self.incY = incY
        self.potsMoure()
    
    def canviOrientacio(self):
        self.potsMoure()
        self.incX, self.incY = self.incY, self.incX
    
    def pintarRectangle(self,poligon):
        points=[QgsPointXY(0,0),QgsPointXY(0,10),QgsPointXY(10,10),QgsPointXY(0,10),QgsPointXY(0,0)]
        poligono=QgsGeometry.fromRect(poligon)
        self.rubberband.setToGeometry(poligono,self.layer)
        self.rubberband.hide()
    
        
class QvPrint(QWidget):
    """Una classe del tipus QWidget que servirà per imprimir un area determinada.
    El widget conté un botó per imprimir, un per tornar a posicionar l'area d'impresió, i un comboBox per escollir l'escala.
    """
    
    @QvFuncions.mostraSpinner
    def __init__(self, project, canvas, poligon, parent=None):
        """Inicialització de la clase:
            Arguments:
                project {QgsProject().instance()} -- El projecte actiu
                canvas {QgsVectorLayer} -- El canvas sobre el que es coloca la rubberband.   
                poligon {QgsPoligon} -- Poligon inicial. A revisar.
        """
        # We inherit our parent's properties and methods.
        QWidget.__init__(self, parent)
        self.parent = parent
        # Creating a memory layer to draw later the rubberband.
        estatDirtybit = self.parent.canvisPendents

        # El rectangle serà dibuixat sobre una capa temporal
        self.layer = QgsVectorLayer('Point?crs=epsg:23031', "Capa temporal d'impressió","memory")
        project.addMapLayer(self.layer, False)
        

        # We store safely the parameters as class variables.
        self.canvas = canvas
        self.project = project
        self.poligon = poligon

        # Escales de la combobox (100, 200, 250, 500, 1000, 2000... 50000)
        self.llistaEscales = [str(int(x*y)) for y in (100, 1000, 10000) for x in (1, 2, 2.5, 5)]

        # S'assignen a la funció llegeixDirsPlantilles()
        # self.dirsPlantilles té la forma següent
        # {
        #     'NomCategoria' :{'NomPlantilla1':ruta1, 'NomPlantilla2':ruta2...},
        #     'NomCategoria2':{'NomPlantilla3':ruta3, 'NomPlantilla4':ruta4...}
        # }
        self.dirsPlantilles = {}
        # self.mides té la forma següent
        # {
        #     ruta1:{mida1:['H','V'], mida2:['H','V'], mida3:['H']...},
        #     ruta2:{mida4:['V']...}
        # }
        self.mides = {}

        self.inputs_fitxer = {}
        self.inputs = {}

        # We instanciate de PointTool tool, to wait for clicks
        # After that, we assign the tool to the canvas.
        self.rp = PointTool(self, self.canvas, self.layer)
        canvas.setMapTool(self.rp)

        self.llegeixDirsPlantilles()
        self.titols = []

        self.setupUI()
        self.canvas.xyCoordinates.connect(self.mocMouse)

        self.rp.pintarRectangle(self.poligon)

        self.parent.setDirtyBit(estatDirtybit)

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10,20,10,20)
        self.layout.setSpacing(14)
        # self.layout.setAlignment(Qt.AlignTop)

        self.layoutCategoria = QHBoxLayout()
        self.lblCategoria = QLabel('Categoria: ')
        self.cbCategoria = QComboBox(self)
        self.cbCategoria.addItems(self.dirsPlantilles.keys())
        self.cbCategoria.currentTextChanged.connect(self.canviCategoria)
        self.layoutCategoria.addWidget(self.lblCategoria)
        self.layoutCategoria.addWidget(self.cbCategoria)

        self.layoutPlantilla = QHBoxLayout()
        self.lblPlantilla = QLabel('Plantilla: ')
        self.cbPlantilla = QComboBox(self)
        self.cbPlantilla.currentTextChanged.connect(self.canviPlantilla)
        self.layoutPlantilla.addWidget(self.lblPlantilla)
        self.layoutPlantilla.addWidget(self.cbPlantilla)

        self.cbOrientacio=QComboBox(self)
        self.cbOrientacio.currentTextChanged.connect(self.canviOrientacio)
        self.lblCBOrientacio = QLabel("Orientació: ")
        self.layoutCBOrientacio = QHBoxLayout()
        self.layoutCBOrientacio.addWidget(self.lblCBOrientacio)
        self.layoutCBOrientacio.addWidget(self.cbOrientacio)

        self.combo = QComboBox(self)
        self.combo.setEditable(True)
        self.combo.addItems(self.llistaEscales)
        self.combo.currentTextChanged.connect(self.canviEscala)
        self.lblEscales = QLabel("Escales")
        self.layEscales = QHBoxLayout()
        self.layEscales.addWidget(self.lblEscales)
        self.layEscales.addWidget(self.combo)

        self.cbMida=QComboBox(self)
        self.cbMida.currentTextChanged.connect(self.canviEscala)
        self.cbMida.currentTextChanged.connect(self.actualitzaCBOrientacio)
        self.lblCBmida = QLabel("Paper: ")
        self.layoutCBmida = QHBoxLayout()
        self.layoutCBmida.addWidget(self.lblCBmida)
        self.layoutCBmida.addWidget(self.cbMida)

        self.boto = QvPushButton(text='Generar PDF',destacat=True, parent=self)
        self.boto.clicked.connect(self.printPlanol)
        self.boto.setFixedWidth(240)
        self.boto2 = QvPushButton(text='Emmarcar zona a imprimir',parent=self)
        self.boto2.clicked.connect(self.potsMoure)
        self.boto2.setFixedWidth(240)
        self.boto3 = QvPushButton(text='Generar PNG',destacat=True, parent=self)
        self.boto3.clicked.connect(self.printPlanolPNG)
        self.boto3.setFixedWidth(240)


        self.nota = QLabel("NOTA: Alguns navegadors web alteren l'escala d'impressió dels PDFs. Per màxima exactitud imprimiu des de l'Adobe Acrobat.")
        styleheetLabel='''
            QLabel {
                color: grey;
            }'''
        self.nota.setStyleSheet(styleheetLabel)
        self.nota.setMaximumWidth(240)
        self.nota.setWordWrap(True)

        self.layout.addLayout(self.layoutCategoria)
        self.layout.addLayout(self.layoutPlantilla)
        self.layout.addLayout(self.layEscales)
        self.layout.addLayout(self.layoutCBmida)
        self.layout.addLayout(self.layoutCBOrientacio)

        input_ids = self.getInputIds()

        for input_id in input_ids:
            self.inputs[input_id] = {}
            self.inputs[input_id]["layoutTitol"] = QHBoxLayout()
            lbl_text = input_id.replace("qV_", "").capitalize()

            self.inputs[input_id]["lblTitol"] = QLabel(lbl_text)
            self.inputs[input_id]["leTitol"] = QLineEdit(self)
            self.inputs[input_id]["leTitol"].setText(self.parent.titolProjecte)

            self.inputs[input_id]["layoutTitol"].addWidget(self.inputs[input_id]["lblTitol"])
            self.inputs[input_id]["layoutTitol"].addWidget(self.inputs[input_id]["leTitol"])


        for element in self.inputs.values():
            self.layout.addLayout(element["layoutTitol"])

        self.layout.addWidget(self.boto2)
        self.layout.addWidget(self.boto3)
        self.layout.addWidget(self.boto)
        self.layout.addWidget(self.nota)
        # self.layout.addWidget(self.wFormat)
        # self.layout.addWidget(self.rbVertical)
        # self.layout.addWidget(self.rbHoritzontal)
        self.layout.addStretch()
        self.actualitzaCBPlantilles()

    def getInputText(self, fitxer:str, input_id:str) -> Optional[str]:
        for element in self.inputs_fitxers[fitxer]:
            if element["id"] == input_id:
                return element["text"]

        return None

    def getInputIds(self)->List[str]:
        ids = []

        for entry in self.inputs_fitxers.values():
            for input_properties in entry:
                if input_properties["id"].startswith("qV_"):
                    ids.append(input_properties["id"])


        return list(set(ids))

    @staticmethod
    def nomPlantillaCorrecte(nomPlantilla, nomBase):
        aux = nomPlantilla.replace(nomBase,'').replace('.qpt','')
        pattern = re.compile(r'A[0-9][VH]')
        return pattern.fullmatch(aux)

    def getPlantillaFields(self, plantilla:str) -> Optional[List] :
        """
        Retorna els labels de la plantilla
        """

        temp_projecte = QgsProject.instance()
        template = QFile(plantilla)
        doc = QDomDocument()
        doc.setContent(template, False)

        layout = QgsLayout(temp_projecte)
        context = QgsReadWriteContext()
        items, _ = layout.loadFromTemplate(doc, context)

        return [
            {"id":item.id(),"text": item.text()}
            for item in items
            if isinstance(item, QgsLayoutItemLabel) and item.id().startswith("qV_") ]

    def llegeixDirsPlantilles(self):
        self.dirsPlantilles = {
            'Plantilla per defecte':{'plantillaMapa':str(Path(pathPlantilles,'plantillaMapa'))}
        }

        dirCataleg = configuracioQvista.carpetaCatalegProjectesPrivats
        try:
            base, dirs, _ = next(os.walk(dirCataleg))
        except BaseException as e:
            # Si l'usuari no veu cap directori privat, no fem res
            dirs = []
        for d in dirs:
            p = Path(base, d, 'plantilles')
            if p.exists():
                self.dirsPlantilles[d] = {}
                basePlantilla, plantilles, _ = next(os.walk(p))
                for plantilla in plantilles:
                    self.dirsPlantilles[d][plantilla] = str(Path(basePlantilla, plantilla))
        # Tindrem un diccionari on la clau serà la ruta de la plantilla,
        #  i el valor un diccionari on la clau seran les mides (A0, A1...)
        #  i els valors una llista que podrà contenir "H" i/o "V"
        self.mides = {}

        self.inputs_fitxers = {}
        self.inputs = {}

        for grup in self.dirsPlantilles.values():
            for (nom, ruta) in grup.items():
                self.mides[ruta] = {}
                arxius_qpt = glob.glob(os.path.join(ruta, '*.qpt'))
                for arxiu in arxius_qpt:
                    nomArxiu = Path(arxiu).name
                    if self.nomPlantillaCorrecte(nomArxiu, nom):
                        aux = nomArxiu.replace(nom, '')
                        mida = aux[:2]
                        orientacio = aux[2]
                        if mida not in self.mides[ruta]:
                            self.mides[ruta][mida] = []
                        self.mides[ruta][mida].append(orientacio)
                        self.inputs_fitxers[arxiu] = self.getPlantillaFields(arxiu)



    def potsMoure(self):
        # self.canvas.scene().removeItem(self.rubberband)
        # self.pucMoure = True
        if self.canvas.mapTool()!=self.rp:
            self.canvas.setMapTool(self.rp)
        self.rp.potsMoure()

    def getCategoria(self):
        return self.cbCategoria.currentText()

    def getPlantilla(self):
        return self.cbPlantilla.currentText()

    def getMida(self):
        return self.cbMida.currentText()

    def getOrientacio(self):
        return self.cbOrientacio.currentText()

    def getEscala(self):
        return self.combo.currentText()

    def actualitzaCBPlantilles(self):
        self.cbPlantilla.clear()
        plantilles = self.dirsPlantilles[self.getCategoria()]
        self.cbPlantilla.addItems(plantilles)

    def actualitzaInputsPlantilla(self):
        plantilla = self.getPlantillaActual()
        if plantilla is not None:
            input_ids_actuals = self.inputs_fitxers[plantilla]

            for input_obj in self.inputs.values():
                input_obj["lblTitol"].hide()
                input_obj["leTitol"].hide()

            for input_info in input_ids_actuals:
                input_id = input_info["id"]
                self.inputs[input_id]["lblTitol"].show()
                self.inputs[input_id]["leTitol"].show()
                if plantilla:
                    self.inputs[input_id]["leTitol"].setText(self.getInputText(plantilla, input_id))

    def actualitzaCBOrientacio(self):
        categoria = self.getCategoria()
        plantilla = self.getPlantilla()
        mida = self.getMida()
        if mida!='':
            self.cbOrientacio.clear()
            plantilla = self.dirsPlantilles[categoria][plantilla]
            orientacions = self.mides[plantilla][mida]
            orientacionsAux = ['Horitzontal' if x=='H' else 'Vertical' for x in orientacions]
            self.cbOrientacio.addItems(orientacionsAux)
            self.canviEscala()
        self.actualitzaInputsPlantilla()


    def actualitzaCBMida(self):
        categoria = self.getCategoria()
        plantilla = self.getPlantilla()
        if plantilla!='':
            self.cbMida.clear()
            plantilla = self.dirsPlantilles[categoria][plantilla]
            mides = list(self.mides[plantilla].keys())
            self.cbMida.addItems(mides)

            # Posem per defecte la mida més petita
            self.cbMida.setCurrentText(mides[-1])
    
    def canviCategoria(self):
        self.actualitzaCBPlantilles()
    
    def canviPlantilla(self):
        self.actualitzaCBMida()

    def canviEscala(self):
        escala = int(self.getEscala())
        mides = self.getMidesMapa()
        if mides is None:
            return
        amplada, alcada = mides

        # amplada i alcada representen les dimensions del mapa en mm
        # escala és l'escala que volem (si és 1:100, escala=100)
        # incX i incY han d'estar en metres, així que multipliquem i convertim a metres
        incX = amplada*escala/1000
        incY = alcada*escala/1000
        self.rp.setIncXY(incX, incY)

    def variablePerId(self, var):
        layout, ok = self.getLayout()
        if not ok or layout is None:
            return None
        return layout.itemById(var)

    def plantillaTeVariable(self, var) -> bool:
        return self.variablePerId(var) is not None


    def plantillaTeTitol(self) -> bool:
        """
        Returns if the plantilla has a title
        """
        return len(self.inputs.keys()) > 0

    def plantillaTeData(self):
        return self.plantillaTeVariable('idData')

    def getLayout(self):
        templateFile = self.getPlantillaActual()
        if templateFile is None:
            return None, False
        template = QFile(templateFile)
        doc = QDomDocument()
        doc.setContent(template, False)
        layout = QgsLayout(self.project)
        context = QgsReadWriteContext()
        items, ok = layout.loadFromTemplate(doc, context)
        return layout, ok

    def getMidesMapa(self):
        layout, ok = self.getLayout()

        if not ok or layout is None:
            return None

        mapa = layout.referenceMap()
        return mapa.rect().width(), mapa.rect().height()

    def canviOrientacio(self):
        self.canviEscala()
        if self.plantillaTeTitol():
            self.actualitzaInputsPlantilla()
            #for input_obj in self.inputs.values():
            #    input_obj["lblTitol"].show()
            #    input_obj["leTitol"].show()
        else:
            for input_obj in self.inputs.values():
                input_obj["lblTitol"].hide()
                input_obj["leTitol"].hide()

    def mocMouse(self,p):
        if not self.isVisible():
            self.canvas.unsetMapTool(self.rp)

    def closeEvent(self, e):
        super().closeEvent(e)
        if not self.isVisible():
            self.canvas.unsetMapTool(self.rp)



    def pintarRectangle(self,poligon):
        points=[QgsPointXY(0,0),QgsPointXY(0,10),QgsPointXY(10,10),QgsPointXY(0,10),QgsPointXY(0,0)]
        poligono=QgsGeometry.fromRect(self.poligon)
        self.rubberband.setToGeometry(poligono,self.layer)

    @staticmethod
    def nomArxiu(plantilla, orientacio, mida):
        if mida=='' or orientacio=='': return None
        orientacio = orientacio[0].upper()
        return plantilla.replace('.qpt','')+mida+orientacio+'.qpt'

    def getPlantillaActual(self) -> Optional[str]:
        orientacio = self.getOrientacio()
        mida = self.getMida()
        pathPlantilla = self.dirsPlantilles.get(self.getCategoria(), {}).get(self.getPlantilla())
        if pathPlantilla is None:
            return None
        nomArxiu = self.nomArxiu(Path(pathPlantilla).name, orientacio, mida)
        if nomArxiu is not None:
            return str(Path(pathPlantilla, nomArxiu))
        else:
            return None


    def printPlanol(self):
        rotacio=self.canvas.rotation()
        mida = self.getMida()
        escala = self.getEscala()
        self.plantillaMapa = self.getPlantillaActual()

        t = time.localtime()
        timestamp = time.strftime('%d-%b-%Y_%H%M%S', t)
        sortida=tempdir+'sortida_'+timestamp
        
        self.imprimirPlanol(self.rp.posXY[0], self.rp.posXY[1], int(escala), rotacio, mida, self.plantillaMapa, sortida, 'PDF')
       
        QvApp().logRegistre('Impressió: '+self.getEscala())

    def printPlanolPNG(self):
        rotacio=self.canvas.rotation()
        mida = self.getMida()
        escala = self.getEscala()
        self.plantillaMapa = self.getPlantillaActual()

        t = time.localtime()
        timestamp = time.strftime('%d-%b-%Y_%H%M%S', t)
        sortida=tempdir+'sortida_'+timestamp
        
        self.imprimirPlanol(self.rp.posXY[0], self.rp.posXY[1], int(escala), rotacio, mida, self.plantillaMapa, sortida, 'PNG')
       
        QvApp().logRegistre('Impressió: '+self.getEscala())   

    def imprimirPlanol(self,x, y, escala, rotacion, midaPagina, templateFile, fitxerSortida, tipusSortida):
        tInicial=time.time()


        template = QFile(templateFile)
        doc = QDomDocument()
        doc.setContent(template, False)

        layout, ok = self.getLayout()

        if ok and layout is not None:
            refMap = layout.referenceMap()

            if self.plantillaTeTitol():
                for input_id, _ in self.inputs.items():
                    titol = layout.itemById(input_id)
                    if titol:
                        if self.inputs[input_id]["leTitol"]:
                            titol.setText(self.inputs[input_id]["leTitol"].text())
                        else:
                            titol.setText('')
            if self.plantillaTeData():
                dataMapa=layout.itemById('idData')
                t = time.localtime()
                dataMapa.setText(strftime('%b-%d-%Y %H:%M', t))


            rect = refMap.extent()
            vector = QgsVector(x - rect.center().x(), y - rect.center().y())
            rect += vector
            refMap.setExtent(rect)
            refMap.setScale(escala)
            refMap.setMapRotation(rotacion)
            #Depenent del tipus de sortida...
            
            exporter = QgsLayoutExporter(layout) 
            # image_settings = exporter.ImageExportSettings()
            # image_settings.dpi = 30
                
            # result = exporter.exportToImage('d:/dropbox/qpic/preview.png',  image_settings)
            # imatge = QPixmap('d:/dropbox/qpic/preview.png')
            # self.ui.lblImatgeResultat.setPixmap(imatge)
            
            if tipusSortida=='PDF':
                settings = QgsLayoutExporter.PdfExportSettings()
                settings.dpi=300
                settings.exportMetadata=False
                
                # fitxerSortida='d:/sortida_'+timestamp+'.PDF'
                fitxerSortida+='.PDF'
                result = exporter.exportToPdf(fitxerSortida, settings) #Cal desar el resultat (???)

                print (fitxerSortida)

            if tipusSortida=='PNG':
                settings = QgsLayoutExporter.ImageExportSettings()
                settings.dpi = 300

                # fitxerSortida='d:/sortida_'+timestamp+'.PNG'
                fitxerSortida+='.PNG'
                result = exporter.exportToImage(fitxerSortida, settings) #Cal desar el resultat (???)
        
            #Obra el document si està marcat checkObrirResultat
            QDesktopServices().openUrl(QUrl(fitxerSortida))
            
            segonsEmprats=round(time.time()-tInicial,1) #???
            layersTemporals = self.project.mapLayersByName("Capa temporal d'impressió")

            estatDirtybit = self.parent.canvisPendents
            for layer in layersTemporals:
                self.project.removeMapLayer(layer.id())
            self.parent.setDirtyBit(estatDirtybit)

    def oculta(self):
        #Eliminem la capa temporal
        estatDirtybit = self.parent.canvisPendents
        layersTemporals = self.project.mapLayersByName("Capa temporal d'impressió")
        for layer in layersTemporals:
            self.project.removeMapLayer(layer.id())
        self.parent.setDirtyBit(estatDirtybit)
        #Falta posar el ratolí anterior
    
        


if __name__ == "__main__":
    with qgisapp() as app:
        # app.setStyle(QStyleFactory.create('fusion'))
        # Canvas, projecte i bridge
        #canvas=QvCanvas()
        canvas=QgsMapCanvas()
        # canvas.xyCoordinates.connect(mocMouse)
        # canvas.show()
        project=QgsProject().instance()
        root=project.layerTreeRoot()
        bridge=QgsLayerTreeMapCanvasBridge(root,canvas)
        bridge.setCanvasLayers()

        # llegim un projecte de demo
        project.read(projecteInicial)
        

 
        #layer = project.instance().mapLayersByName('BCN_Districte_ETRS89_SHP')[0]


        qvPrint = QvPrint(project, canvas, canvas.extent())
        qvPrint.show()

        """
        Amb aquesta linia:
        qvPrint.show()
        es veuria el widget suelto, separat del canvas.
        Les següents línies mostren com integrar el widget 'ubicacions' com a dockWidget.
        """
        # Definim una finestra QMainWindow
        """ 
        windowTest = QMainWindow()
        # Posem el canvas com a element central
        windowTest.setCentralWidget(canvas)
        # Creem un dockWdget i definim les característiques
        dwPrint = QDockWidget( "qV Print", windowTest )
        dwPrint.setAllowedAreas( Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea )
        dwPrint.setContentsMargins ( 1, 1, 1, 1 )
        dwPrint.setMaximumHeight(200)
        # Afegim el widget ubicacions al dockWidget
        dwPrint.setWidget(qvPrint)
        # Coloquem el dockWidget al costat esquerra de la finestra
        windowTest.addDockWidget( Qt.LeftDockWidgetArea, dwPrint)
        # Fem visible el dockWidget
        # dwPrint.show()
        # Fem visible la finestra principal
        windowTest.show() """
        canvas.show()
