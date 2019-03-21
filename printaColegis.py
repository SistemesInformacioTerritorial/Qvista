from QvImports import *

def imprimirPlanol(self,x, y, escala, rotacion, templateFile, fitxerSortida, tipusSortida):
    tInicial=time.time()

    template = QFile(templateFile)
    doc = QDomDocument()
    doc.setContent(template, False)

    layout = QgsLayout(self.project)
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
        layersTemporals = self.project.mapLayersByName("Capa temporal d'impressió")
        for layer in layersTemporals:
            self.project.removeMapLayer(layer.id())
  

with qgisapp() as app:
    boyo = QtPushButton('hola')
    boyo.show()