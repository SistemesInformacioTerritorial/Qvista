# Programa 

from moduls.QvImports import *
from moduls.QvLlegenda import QvLlegenda

projecteInicial = 'd:/MapaEscolar/MapaEscolar.qgs'

def imprimirPlanol(colegi, codiColegi, x_min, y_min, x_max, y_max, rotacion, templateFile, fitxerSortida, tipusSortida):
    tInicial=time.time()

    template = QFile(templateFile)
    doc = QDomDocument()
    doc.setContent(template, False)

    layout = QgsLayout(project)
    context = QgsReadWriteContext()
    [items, ok] = layout.loadFromTemplate(doc, context)

    if ok:
        refMap = layout.referenceMap()
        labelColegi = layout.itemById('LabelColegi')
        labelSeccions = layout.itemById('LabelSeccions')
        # labelColegi.setText(colegi)
        labelSeccions.setText(codiColegi+': '+colegi)
        
        rect = refMap.extent()
        vector = QgsVector(x_min - rect.center().x(), y_min - rect.center().y())
        rect += vector

        offsetX = (x_max - x_min) / 12
        offsetY = (y_max - y_min) / 12
        x_min = x_min - offsetX
        y_min = y_min - offsetY
        x_max = x_max + offsetX
        y_max = y_max + offsetY
        distX = (x_max - x_min) 
        distY = (y_max - y_min) 

        relacio = 297 / 210
        newOffsetY = 1
        newOffsetX = 1

        while distX / (distY + newOffsetY) > relacio:
            newOffsetY = newOffsetY + 1

        while (distX + newOffsetX) / distY < relacio:
            newOffsetX = newOffsetX + 1
         
        newOffsetY = newOffsetY / 2
        newOffsetX = newOffsetX / 2

        rectangle = QgsRectangle(x_min - newOffsetX, y_min - newOffsetY, x_max + newOffsetX, y_max + newOffsetY)
        # rectangle = QgsRectangle(x_min, y_min, x_max, y_max)

        refMap.setExtent(rectangle)
        refMap.setMapRotation(rotacion)
        #Depenent del tipus de sortida...
        
        exporter = QgsLayoutExporter(layout) 
        # image_settings = exporter.ImageExportSettings()
        # image_settings.dpi = 30
            
        # result = exporter.exportToImage('d:/dropbox/qpic/preview.png',  image_settings)
        # imatge = QPixmap('d:/dropbox/qpic/preview.png')
        # self.ui.lblImatgeResultat.setPixmap(imatge)
        t = time.localtime()

        timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)

        if tipusSortida=='PDF':
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.dpi=300
            settings.exportMetadata=False
            
            fitxerSortida='d:/MapaEscolar_'+timestamp+'.PDF'
            result = exporter.exportToPdf(fitxerSortida, settings)

            print (fitxerSortida)

        if tipusSortida=='PNG':
            settings = QgsLayoutExporter.ImageExportSettings()
            settings.dpi = 300

            fitxerSortida='d:/sortida_'+timestamp+'.PNG'
            result = exporter.exportToImage(fitxerSortida, settings)
    
        #Obra el document si està marcat checkObrirResultat
        # QDesktopServices().openUrl(QUrl(fitxerSortida))
        
        segonsEmprats=round(time.time()-tInicial,1)
        layersTemporals = project.mapLayersByName("Capa temporal d'impressió")
        for layer in layersTemporals:
            project.removeMapLayer(layer.id())
  

with qgisapp() as app:
    canvas = QgsMapCanvas()
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root,canvas)
    bridge.setCanvasLayers()
    project.read(projecteInicial)
    llegenda = QvLlegenda(canvas)
    llegenda.show()

    plantillaMapa = 'plantillaMapaEscolarA1.qpt'

    posXY = [430036,4583163]    
    
    layerCentres = llegenda.capaPerNom('CENTRES')
    layerIlles = llegenda.capaPerNom('ILLES')

    # layer = LAYER DE COLEGIS
    # textFiltre = "CODI_CENTRE = '08077101'"
    # print (textFiltre)
    # layerIlles.setSubsetString(textFiltre)
    # layerCentres.setSubsetString(textFiltre)

    for feature in layerCentres.getFeatures():
        illa = feature.attributes()[layerCentres.fields().lookupField('ILLA')]
        codi_centre = feature.attributes()[layerCentres.fields().lookupField('CODI_CENTRE')]
        edifici = feature.attributes()[layerCentres.fields().lookupField('EDIFICI')]
        titularitat = feature.attributes()[layerCentres.fields().lookupField('TITULARITAT')]
        assignada = feature.attributes()[layerCentres.fields().lookupField('ASSIGNADA')]
        distancia = feature.attributes()[layerCentres.fields().lookupField('DISTANCIA')]
        adreca = feature.attributes()[layerCentres.fields().lookupField('ADRECA')]
        nom = feature.attributes()[layerCentres.fields().lookupField('NOM')]
        adreca = feature.attributes()[layerCentres.fields().lookupField('ADRECA')]
        xMin = feature.attributes()[layerCentres.fields().lookupField('XMIN')]
        yMin = feature.attributes()[layerCentres.fields().lookupField('YMIN')]
        xMax = feature.attributes()[layerCentres.fields().lookupField('XMAX')]
        yMax = feature.attributes()[layerCentres.fields().lookupField('YMAX')]
        # if codi_centre == '08077101':
        textFiltre = "CODI_CENTRE = '"+codi_centre+"'"
        print (textFiltre)
        layerIlles.setSubsetString(textFiltre) 
        layerCentres.setSubsetString(textFiltre)

        # layer.setSubsetString(textFiltre2)     
        imprimirPlanol(nom, codi_centre, xMin, yMin, xMax, yMax, 0, plantillaMapa , 'd:/EUREKA.pdf', 'PDF')
    
