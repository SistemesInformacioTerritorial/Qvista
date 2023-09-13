from moduls.QvImports import *
from moduls.QvLlegenda import QvLlegenda
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile

# projecteInicial = 'd:/colegis3.qgs'
# esencialmente tenemos gpkg colelect_plot_gpkg, que guarda datos
# projecteInicial = r'D:\aranyas2\2023_02_28_Locals possibles_procesados\print_Y_control.qgs'
projecteInicial = r'D:\aranyas3\impresion\impresion.qgz'

def imprimirPlanol(dte, barri,cole,colegi, adreca, meses, x_min, y_min, x_max, y_max, rotacion, templateFile, path_sortida, tipusSortida):
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
        labelColegi2 = layout.itemById('LabelColegi2')
        labelSeccions = layout.itemById('LabelSeccions')
        labelSeccions2 = layout.itemById('LabelSeccions2')
        labelDte = layout.itemById('LabelDte')
        labelAdreca = layout.itemById('LabelAdreca')
        labelColegi.setText('Col·legi Electoral: ' + colegi)
        labelColegi2.setText(colegi)
        labelSeccions.setText('Meses: ' + meses)
        labelSeccions2.setText(meses)
        labelDte.setText('Districte: '+str(dte)+' -'+cole)
        labelAdreca.setText(adreca)
        
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
        relacio = 287 / 173
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
            # aqui, rasterizar imagen
            settings.rasterizeWholeImage = True
            settings.exportMetadata=True
            #  Dte-Barri-Codi
            # fitxerSortida="{}_{}_{}{}{}".format('D:/aranyas2/2023_02_28_Locals possibles_procesados/salida_PDF/sortida',cole,colegi,timestamp,'.PDF')
            fitxerSortida="{p1}{p2}_{p4}_{p5}{p6}{p7}".format(p1=path_sortida,p2=str(dte).zfill(2),p3=str(barri).zfill(2),p4=str(cole).zfill(3),p5=colegi,p6=timestamp,p7='.PDF')
            
            # fitxerSortida = '{p1}\DTE {p2} - *\Fitxes 2023\{p3}-{p4}-*.xls*'.format(p1=raiz,p2=dte,p3=dte.zfill(2),p4=codi.zfill(3))
            
            result = exporter.exportToPdf(fitxerSortida, settings)

            print (fitxerSortida)

        if tipusSortida=='PNG':
            settings = QgsLayoutExporter.ImageExportSettings()
            settings.dpi = 300

            # fitxerSortida='d:/sortida_'+timestamp+'.PNG'
            fitxerSortida="{}{}{}{}".format('D:/aranyas2/2023_02_28_Locals possibles_procesados/salida_PNG/sortida_',colegi,timestamp,'.PNG')
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
    plantillaMapa3 = 'plantillaColegisA3_2Cares.qpt'
    plantillaMapa2 = 'plantillaColegisA2_2Cares.qpt'
    posXY = [430036,4583163]    

    # layer = llegenda.capaPerNom('COLELEC_PLOT')  # funcionamiento anterior
    layer = llegenda.capaPerNom('colelect_plot_gpkg')

    # layerSeccions = llegenda.capaPerNom('GSEC_CENS2')  # funcionamiento anterior
    layerSeccions = llegenda.capaPerNom('Seccions censals_gpkg')
    layerTratados = llegenda.capaPerNom('Centres_possiblesTratados.csv')
    layerCentresPosibles =  llegenda.capaPerNom('Centres_possibles')

    # para asegurarme de que los codigos estan agrupados
    listaCodiClaves=[]
    for feat in layerTratados.getFeatures():  
        codi =  feat["CODI"]
        codi_padded = str(codi).rjust(5, '0')
        clave =  feat["Clave"]
        nom_clave = "{}_{}".format(codi_padded,clave)
        listaCodiClaves.append(nom_clave)

    # Obtener todas las seccioens censales que estan asignadas a un colegio
    dicCod_Clave ={}
    listaClavesDelCodigo=[]
    listaCodiClaves.sort(reverse=False)  #ascending
    codi_old =''
    for eleList in listaCodiClaves:
        nn = eleList.find('_')
        codi= eleList[0:nn]
        clave=eleList[nn+1:1000]
        # print(codi,clave)
        if codi != codi_old:
            listaClavesDelCodigo=[]
        listaClavesDelCodigo.append(clave)
        dicCod_Clave[codi]= listaClavesDelCodigo
        codi_old= codi


    # Obtencion de rangos de secciones censales
    dic_xmin= {}; dic_xmax= {}; dic_ymin= {}; dic_ymax= {}
    for feat in layerSeccions.getFeatures():
        migeo= feat.geometry().boundingBox()
        # clave =  feat["CODI_CENS"]
        clave =  feat["clave"]
        dic_xmin[clave]= str(migeo.xMinimum())
        dic_xmax[clave]= str(migeo.xMaximum())
        dic_ymin[clave]= str(migeo.yMinimum())
        dic_ymax[clave]= str(migeo.yMaximum())        
   
    # poner en edicion la capa colelect_plot_gpkg
    layer.startEditing()
    # abrir para lectura la capa Centres_possibles

    listOfIds = [feat.id() for feat in layer.getFeatures()]
    layer.deleteFeatures( listOfIds )

    layer.commitChanges()
    QApplication.processEvents()  
    
    layer.startEditing()
    for feat in layerCentresPosibles.getFeatures():  
        try:
            feat_w = QgsFeature(layer.fields())
            codi = feat["CODI"]
            feat_w.setAttribute('CODI_COLE', codi)
            feat_w.setAttribute('LOCAL', feat["NOM"])
            feat_w.setAttribute('ADREÇA', feat["ADRECA"])
            feat_w.setAttribute('BARRI', feat["BARRI"])
            feat_w.setAttribute('DTE', feat["DTE"])

            codi_padded = str(codi).rjust(5, '0')
            secciones = dicCod_Clave[codi_padded]

            dic_tra_xmin= {}; dic_tra_xmax= {}; dic_tra_ymin= {}; dic_tra_ymax= {}
            secciones_string=""
            for elelista in secciones:
                secciones_string += "," + elelista
                # Buscar el rango de esta seccion
                dic_tra_xmin[elelista] =dic_xmin[elelista] 
                dic_tra_xmax[elelista] =dic_xmax[elelista] 
                dic_tra_ymin[elelista] =dic_ymin[elelista] 
                dic_tra_ymax[elelista] =dic_ymax[elelista]                 

                # Calculo del minimo y maximo en un diccionario
            secciones_string= secciones_string[1:]
            feat_w.setAttribute('SECCIONS', secciones_string)

            # añado la geometria del centro current
            migeo= feat.geometry().boundingBox()
            dic_tra_xmin["current"]= str(migeo.xMinimum())
            dic_tra_xmax["current"]= str(migeo.xMaximum())
            dic_tra_ymin["current"]= str(migeo.yMinimum())
            dic_tra_ymax["current"]= str(migeo.yMaximum())        

            x_tra_min= min(dic_tra_xmin.items(), key=lambda x: x[1]) 
            y_tra_min= min(dic_tra_ymin.items(), key=lambda x: x[1])                 
            x_tra_max= max(dic_tra_xmax.items(), key=lambda x: x[1]) 
            y_tra_max= max(dic_tra_ymax.items(), key=lambda x: x[1]) 

            # FALTA INCORPORAR COORDENADAS DEL CENTRO EN EL CALCULO DEL RANGO DE REPRESENTACION

            feat_w.setAttribute('XMIN', float(x_tra_min[1]))
            feat_w.setAttribute('yMIN', float(y_tra_min[1]))            
            feat_w.setAttribute('XMAX', float(x_tra_max[1]))
            feat_w.setAttribute('YMAX', float(y_tra_max[1]))            

            feat_w.setAttribute('MESES', feat["MESES_LOCAL_2023"])
            feat_w.setGeometry(feat.geometry())
            (res, outFeats) = layer.dataProvider().addFeatures([feat_w])
            layer.updateFeature(feat_w )
        except:
            pass
        
  
    layer.commitChanges()

    QgsProject.instance().reloadAllLayers() 
    QApplication.processEvents()  




    # layer = LAYER DE COLEGIS
    nn=0
    for feature in layer.getFeatures():
        nn += 1
        print(nn)
        colegi = feature.attributes()[layer.fields().lookupField('LOCAL')]
        cole = feature.attributes()[layer.fields().lookupField('CODI_COLE')]
        seccions = feature.attributes()[layer.fields().lookupField('SECCIONS')]
        adreca = feature.attributes()[layer.fields().lookupField('ADREÇA')]
        meses = feature.attributes()[layer.fields().lookupField('MESES')]
        x_min = feature.attributes()[layer.fields().lookupField('XMIN')]
        y_min = feature.attributes()[layer.fields().lookupField('YMIN')]
        x_max = feature.attributes()[layer.fields().lookupField('XMAX')]
        y_max = feature.attributes()[layer.fields().lookupField('YMAX')]
        dte =  feature.attributes()[layer.fields().lookupField('DTE')]
        barri =  feature.attributes()[layer.fields().lookupField('BARRI')]

        # Filtro para mostrar solo las secciones censales afectadas por el centro current
        textFiltre = "INSTR('"+seccions+"',DISTRICTE||SEC_CENS)>0"
        layerSeccions.setSubsetString(textFiltre) 
        # Filtro para mostrar solo el centro current
        textFiltre2 = 'CODI_COLE'+"='"+cole+"'"
        layer.setSubsetString(textFiltre2)    

# --------------

        # from PyQt5.QtWidgets import QApplication
        # from qgis.utils import iface

        # all_widgets = QApplication.instance().allWidgets()
        # attribute_table_widgets = [widget for widget in all_widgets if "AttributeTable" in widget.objectName()]
        # for attribute_table in attribute_table_widgets:
        #     if 'Centres_possibles' in attribute_table.objectName():
        #         attribute_table.close()
                

        # layer=None
        # #for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        # for lyr in QgsProject.instance().mapLayers().values():    
        #     if lyr.name() == "Centres_possibles":
        #         layer = lyr
        #         iface.showAttributeTable(layer)
        #         break


        # codigos de colegio que presisan impresion A2
        if cole in ("538","777","692","491","541","292","757","52","823","632","966","635","985","526","229","925","385","55"):
            # impresiones con plantilla formatoA2
            imprimirPlanol(dte, barri,cole,colegi, adreca, meses, x_min, y_min, x_max, y_max, 0, plantillaMapa2 , 'D:/aranyas3/impresion/salida_PDF2/', 'PDF')
        else:
            # impresiones con plantilla formatoA3
            imprimirPlanol(dte, barri,cole,colegi, adreca, meses, x_min, y_min, x_max, y_max, 0, plantillaMapa3 , 'D:/aranyas3/impresion/salida_PDF/', 'PDF')
            
       
        layerSeccions.setSubsetString("") 
        layer.setSubsetString("")  
    
    canvas.show()