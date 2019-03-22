from moduls.QvImports import *
from moduls.QvLlegenda import QvLlegenda

projecteInicial = 'd:/colegis3.qgs'

def imprimirPlanol(x_min, y_min, x_max, y_max, rotacion, templateFile, fitxerSortida, tipusSortida):
    tInicial=time.time()

    template = QFile(templateFile)
    doc = QDomDocument()
    doc.setContent(template, False)

    layout = QgsLayout(project)
    context = QgsReadWriteContext()
    [items, ok] = layout.loadFromTemplate(doc, context)

    if ok:
        refMap = layout.referenceMap()
        
        rect = refMap.extent()
        vector = QgsVector(x_min - rect.center().x(), y_min - rect.center().y())
        rect += vector

        offsetX = (x_max - x_min) / 6
        offsetY = (y_max - y_min) / 6
        x_min = x_min - offsetX
        y_min = y_min - offsetY
        x_max = x_max + offsetX
        y_max = y_max + offsetY
        distX = (x_max - x_min) 
        distY = (y_max - y_min) 
        relacio = 280 / 165
        newOffsetY = 1
        newOffsetX = 1

        while distX / (distY + newOffsetY) > relacio:
            newOffsetY = newOffsetY + 1

        while (distX + newOffsetX) / distY < relacio:
            newOffsetX = newOffsetX + 1
         
        newOffsetY = newOffsetY / 2
        newOffsetX = newOffsetX / 2

        rectangle = QgsRectangle(x_min - newOffsetX, y_min - newOffsetY, x_max + newOffsetX, y_max + newOffsetY)

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
            
            fitxerSortida='d:/sortida_'+timestamp+'.PDF'
            result = exporter.exportToPdf(fitxerSortida, settings)

            print (fitxerSortida)

        if tipusSortida=='PNG':
            settings = QgsLayoutExporter.ImageExportSettings()
            settings.dpi = 300

            fitxerSortida='d:/sortida_'+timestamp+'.PNG'
            result = exporter.exportToImage(fitxerSortida, settings)
    
        #Obra el document si està marcat checkObrirResultat
        QDesktopServices().openUrl(QUrl(fitxerSortida))
        
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

    plantillaMapa = 'plantillaMapaH.qpt'

    posXY = [430036,4583163]    
    
    layer = llegenda.capaPerNom('COLELEC_PLOT')
    layerSeccions = llegenda.capaPerNom('GSEC_CENS2')

    # layer = LAYER DE COLEGIS
    for feature in layer.getFeatures():
        colegi = feature.attributes()[layer.fields().lookupField('LOCAL')]
        cole = feature.attributes()[layer.fields().lookupField('CODI_COLE')]
        seccions = feature.attributes()[layer.fields().lookupField('SECCIONS')]
        x_min = feature.attributes()[layer.fields().lookupField('XMIN')]
        y_min = feature.attributes()[layer.fields().lookupField('YMIN')]
        x_max = feature.attributes()[layer.fields().lookupField('XMAX')]
        y_max = feature.attributes()[layer.fields().lookupField('YMAX')]


        textFiltre = "INSTR('"+seccions+"',DISTRICTE||SEC_CENS)>0"
        textFiltre2 = 'CODI_COLE'+"='"+cole+"'"
        layerSeccions.setSubsetString(textFiltre) 
        layer.setSubsetString(textFiltre2)     
        imprimirPlanol(x_min, y_min, x_max, y_max, 0, plantillaMapa , 'd:/EUREKA.pdf', 'PDF')
    
    canvas.show()