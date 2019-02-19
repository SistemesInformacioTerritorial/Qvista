from qgis.core import QgsApplication, \
                      QgsProject, \
                      QgsLayout, \
                      QgsReadWriteContext, \
                      QgsRectangle, \
                      QgsMapLayer, \
                      QgsLayoutItemMap, \
                      QgsLayoutExporter, \
                      QgsVector

from qgis.PyQt.QtCore import QFile, QTextStream, QTime, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QPixmap
from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt.QtWidgets import QWidget, QFileDialog
from qgis.PyQt.QtXml import QDomDocument, QDomElement, QDomAttr, QDomText

import time
import datetime

class QvGenerarThumbnails():
    """Aquesta classe ofereix les eines per generar thumbnails de projectes.

    Una finestra de dialeg permet escollir els projectes a tractar.
    (En un futur la classe pot permetre escollir si es vol dialeg o si es prefereix alimentar d'un fitxer extern, per exemple.)

    Els fitxers resultants tenen el mateix nom que el projecte i son PNG's ubicats al mateix directori que el projecte.
    """

    def __init__(self,escala):
        self.project = QgsProject.instance()

        # Dades inicials
        tipusSortida='PNG'
        gir=0
        plantillaPlanol = 'plantillaThumbnail.qpt'

        # Omplim la llista de projectes a partir del dialeg.
        projectes = self.obrirDialegProjecte()
        fitxerSortida = None
        for projecte in projectes:
            # timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
            self.imprimirPlanol(431975,4583899, 
                            escala, 
                            gir,
                            projecte,
                            plantillaPlanol,
                            fitxerSortida,
                            tipusSortida)

    def obrirDialegProjecte(self):
        """Retorna una llista de fitxers seleccionats en el dialeg.
        
        Returns:
            [llista de strings] -- [Una llista amb string que contenen el path complert i nom de cada projecte.]
        """

        dialegObertura=QFileDialog()
        dialegObertura.setDirectoryUrl(QUrl('../dades/projectes/'))

        nfiles,_ = dialegObertura.getOpenFileNames(None,"Open Projecte Qgis", ".", "Projectes Qgis (*.qgs)")
        return nfiles

    def imprimirPlanol(self,x, y, escala, rotacion, projectePlanol, templateFile, fitxerSortida, tipusSortida):
        self.project.read(projectePlanol)
        template = QFile(templateFile)

        # Creem un document amb la plantilla
        doc = QDomDocument()
        doc.setContent(template, False)

        # Aquest layout no té res a veure amb els layaouts de PyQt. 
        # Es una plantilla per el projecte. You must believe it.
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
            image_settings = exporter.ImageExportSettings()
            image_settings.dpi = 60
                
            # result = exporter.exportToImage('d:/dropbox/qpic/preview.png',  image_settings)
            # imatge = QPixmap('d:/dropbox/qpic/preview.png')
            t = time.localtime()

            timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)

            if tipusSortida=='PDF':
                settings = QgsLayoutExporter.PdfExportSettings()
                settings.dpi=60
                settings.exportMetadata=False
                
                fitxerSortida='d:/dropbox/qpic/sortida_'+timestamp+'.PDF'
                result = exporter.exportToPdf(fitxerSortida, settings)

                print (fitxerSortida)

            if tipusSortida=='PNG':
                settings = QgsLayoutExporter.ImageExportSettings()
                settings.dpi = 60

                # fitxerSortida='sortida_'+timestamp+'.PNG'
                fitxerSortida = projectePlanol[0:-4]+'.png'
                result = exporter.exportToImage(fitxerSortida, settings)
            
            # QDesktopServices().openUrl(QUrl(fitxerSortida))
            # segonsEmprats=round(time.time()-tInicial,1)


qgs = QgsApplication([], False)
qgs.initQgis()

QvGenerarThumbnails(2000)

qgs.exitQgis()