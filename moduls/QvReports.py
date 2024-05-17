# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsLayoutExporter, QgsReport
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMenu, QMessageBox, QApplication

from DataPlotly.QvDataPlotly import QvDataPlotly

import os 

class QvReports(QvDataPlotly):

    DataPlotlyVersion = QvDataPlotly.VERSION
    PathInformes = 'C:/temp/qVista/dades'

    ExportMsgs = [
        'L\'exportació ha estat exitosa.',
        'L\'exportació ha estat cancel·lada.',
        'No es pot assignar la memòria necessària per fer l\'exportació.',
        'No s\'ha pogut escriure al fitxer de destinació, probablement a causa d\'un bloqueig mantingut per una altra aplicació.',
        'No s\'ha pogut iniciar la impressió al dispositiu de destinació.',
        'No s\'ha pogut crear el fitxer SVG en capes.',
        'Error en iterar sobre el disseny.'
    ]

    def __init__(self, llegenda, path=PathInformes, settings=None):
        super().__init__()
        self.initGui()
        self.llegenda = llegenda
        self.path = path
        if settings is None:
            self.settings = QgsLayoutExporter.PdfExportSettings()
        else:
            self.settings = settings
        self.menu = QMenu()
        self.lastPdf = ''

    def listReports(self):
        layoutManager = QgsProject.instance().layoutManager()
        return [layout.name() for layout in layoutManager.layouts()]

    def exportMsg(self, result):
        if result in range(len(QvReports.ExportMsgs)):
            return QvReports.ExportMsgs[result]
        else:
            return "Error en la generació de l'informe"

    def exportToPdf(self, name):
        try: 
            layoutManager = QgsProject.instance().layoutManager()
            layout = layoutManager.layoutByName(name)
            if layout is None:
                return -1, f"Informe {name} no trobat" 
        except Exception as e:
            return -1, f"Informe {name} no trobat - " + str(e)

        try:        
            pdfPath = self.path + '/' + name + '.pdf'
            if type(layout) is QgsReport:
                # Informes compuestos
                result, _ = QgsLayoutExporter.exportToPdf(layout, pdfPath, self.settings)
            else:
                # Informes sencilos
                exporter = QgsLayoutExporter(layout)
                result = exporter.exportToPdf(pdfPath, self.settings)
            msg = self.exportMsg(result)
            if result == 0:
                self.lastPdf = pdfPath
            return result, msg
        
        except Exception as e:
            return -1, "Error en l'exportació  - " + str(e)

    def menuReport(self):
        QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        try:
            report = self.llegenda.sender().text()
            result, msg = self.exportToPdf(report)
            if result == 0:
                os.startfile(self.lastPdf)
                QApplication.instance().restoreOverrideCursor()
            else:
                QApplication.instance().restoreOverrideCursor()
                QMessageBox.warning(None, f"ERROR a l'informe '{report}'", msg)
        except Exception as e:
            QApplication.instance().restoreOverrideCursor()
            QMessageBox.warning(None, f"ERROR a l'informe '{report}'", str(e))

    def setMenu(self, title='Informes PDF'):
        self.menu.clear()
        self.menu.setTitle(title)
        for report in self.listReports():
            act = self.menu.addAction(report)
            act.triggered.connect(self.menuReport)
        if self.menu.isEmpty():
            return None
        else:
            self.menu.addSeparator()
            act = self.menu.addAction("Carpeta d'informes")
            act.triggered.connect(lambda: os.startfile(self.path))
            return self.menu

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from qgis.core import QgsLayoutExporter, QgsReport, QgsApplication
    from qgis.gui import QgsMapCanvas
    from moduls.QvLlegenda import QvLlegenda
    from moduls.QvApp import QvApp
    from moduls.QvAtributs import QvAtributs
    from DataPlotly.QvDataPlotly import QvDataPlotly
    from qgis.analysis import QgsNativeAlgorithms
    
    import sys

    with qgisapp() as app:

        qApp = QvApp()
        qApp.carregaIdioma(app, 'ca')

        canvas = QgsMapCanvas()

        atributs = QvAtributs(canvas)

        llegenda = QvLlegenda(canvas, atributs)

        # sys.path.append('C:/Users/de1717.CORPPRO/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins')

        # nAlgs = QgsNativeAlgorithms()
        # nAlgs.loadAlgorithms()
        # QgsApplication.processingRegistry().addProvider(nAlgs) 

        dp = QvDataPlotly()
        dp.initGui()

        # llegenda.project.read('projectes/Illes.qgs')
        llegenda.project.read("D:/qVista/Zonas/Diagramas.3.22.qgs")

        llegenda.setWindowTitle('Llegenda')
        llegenda.setGeometry(50, 50, 300, 400)
        llegenda.show()

        canvas.setWindowTitle('Mapa')
        canvas.setGeometry(400, 50, 700, 400)
        canvas.show()

        # Abrimos una tabla de atributos
        # layer = llegenda.capaPerNom('Illes')
        # atributs.obrirTaula(layer)

        atributs.setWindowTitle('Atributs')
        atributs.setGeometry(50, 500, 1050, 250)
        llegenda.obertaTaulaAtributs.connect(atributs.show)

        # Obtiene el administrador de composiciones
        layoutManager = llegenda.project.layoutManager()
        settings = QgsLayoutExporter.PdfExportSettings()

        print(f"Composiciones de {llegenda.project.fileName()}")
        # Itera sobre las composiciones existentes
        for layout in layoutManager.layouts():
            name = layout.name()
            print(f"- {name}")

            # Define la ruta de salida para el archivo PDF
            pdfPath = llegenda.project.homePath() + '/Test' + name + '.pdf'

            # Exporta la composición a PDF
            if type(layout) is QgsReport:
                result, error = QgsLayoutExporter.exportToPdf(layout, pdfPath, settings)
            else:
                exporter = QgsLayoutExporter(layout)
                result = exporter.exportToPdf(pdfPath, settings)

            if result == 0:
                print(f"  Informe '{name}' exportado a: {pdfPath}")
            else:
                print(f"  Error al exportar el informe '{name}': {result}")

        print("*** FIN")
