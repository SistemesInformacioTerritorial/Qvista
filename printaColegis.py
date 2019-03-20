from moduls.QvImports import *
from moduls.QvLlegenda import QvLlegenda

projecteInicial = 'd:/colegis.qgs'

def imprimirPlanol(x, y, escala, rotacion, templateFile, fitxerSortida, tipusSortida):
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
        seccions = feature.attributes()[layer.fields().lookupField('SECCIONS')]
        textFiltre = "CODI_SECCIO LIKE '%"+seccions+"%'"
        print (textFiltre)
        layerSeccions.setSubsetString(textFiltre)
          
          
    imprimirPlanol(posXY[0], posXY[1], 50000, 0, plantillaMapa , 'd:/EUREKA.pdf', 'PDF')
    
    canvas.show()