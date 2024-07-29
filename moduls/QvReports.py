# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsLayoutExporter, QgsReport, QgsFeedback
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMenu, QMessageBox, QApplication, QProgressDialog, QProgressBar, QPushButton, QShortcut 

from DataPlotly.QvDataPlotly import QvDataPlotly

from moduls.QvFuncions import debugging
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

    def __init__(self, llegenda, path=PathInformes):
        super().__init__()
        self.initGui()
        self.llegenda = llegenda
        self.path = path
        self.menu = QMenu()
        self.progressBar = None

    def listReports(self):
        layoutManager = QgsProject.instance().layoutManager()
        return [layout.name() for layout in layoutManager.printLayouts()]

        # for layout in layoutManager.printLayouts():
        #     if layout.atlas().enabled():
        #         yield layout.name()

    def msgReport(self, result):
        if result in range(len(QvReports.ExportMsgs)):
            return QvReports.ExportMsgs[result]
        else:
            return "Error en la generació de l'informe"

    def cancelReport(self):
        if debugging(): print("Informe cancel·lat")
        self.feedback.cancel()

    def progressDialog(self, cancel=True, title="Informe PDF"):
        progressBar = QProgressDialog()
        if cancel:
            progressBar.canceled.connect(self.cancelReport)
        else:
            for w in progressBar.children():
                if isinstance(w, QProgressBar):
                    w.hide()
                elif isinstance(w, QPushButton):
                    w.setEnabled(False)
                    w.hide()
                elif isinstance(w, QShortcut):
                    w.setEnabled(False)
        progressBar.setRange(0, 100)
        progressBar.setWindowTitle(title)
        progressBar.setMinimumWidth(400)
        progressBar.setMinimumHeight(150)
        progressBar.setWindowModality(Qt.WindowModal)
        progressBar.setWindowFlags(Qt.WindowStaysOnTopHint)
        progressBar.setMinimumDuration(0)
        return progressBar

    def progressReport(self, porcentaje, name='', txt="Generant informe"):
        num = round(porcentaje)
        if num == 0:
            msg = txt + " " + name + " ..."
            self.progressBar.setLabelText(msg)
        else:            
            msg = txt + " " + str(num) + " %"
        if debugging(): print(msg)
        if self.progressBar.wasCanceled():
            self.progressBar.setValue(100)
        else:
            self.progressBar.setValue(num)

    def reportToPdf(self, name):
        try: 
            layoutManager = QgsProject.instance().layoutManager()
            layout = layoutManager.layoutByName(name)
            if layout is None:
                return -1, "Informe no trobat", None
            # if not atlas.enabled():
            #     return -1, "Informe desactivat", None
        except Exception as e:
            return -1, "Informe no trobat - " + str(e), None

        try:        
            # https://github.com/carey136/Standalone-Export-Atlas-QGIS3/blob/master/AtlasExport.py

            pdf = self.path + '/' + name + '.pdf'

            atlas = layout.atlas()
            if atlas.enabled():
                # Parámetros
                atlasLayout = atlas.layout()
                exporter = QgsLayoutExporter(atlasLayout)
                settings = exporter.PdfExportSettings()
                settings.exportLayersAsSeperateFiles = False
                # Progreso
                self.feedback = QgsFeedback()
                self.progressBar = self.progressDialog()
                self.feedback.progressChanged.connect(self.progressReport)
                self.progressReport(0.0, name)
                # Exportación
                result, _ = QgsLayoutExporter.exportToPdf(atlas, pdf, settings, self.feedback)
            else:
                # Parámetros
                exporter = QgsLayoutExporter(layout)
                settings = exporter.PdfExportSettings()
                # Progreso sin cancel
                self.progressBar = self.progressDialog(False)
                self.progressReport(0.0, name)
                # Exportación
                result = exporter.exportToPdf(pdf, settings)
                self.progressBar.reset()

            msg = self.msgReport(result)
            if result == QgsLayoutExporter.Success:
                return result, msg, pdf
            else:
                return result, msg, None

        except Exception as e:
            return -1, "Error en la generació  - " + str(e), None
        finally:
            if self.progressBar is not None: 
                self.progressBar.reset()

    def menuReport(self):
        # QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        try:
            report = self.llegenda.sender().text()
            result, msg, pdf = self.reportToPdf(report)
            if result == QgsLayoutExporter.Success:
                os.startfile(pdf)
                # QApplication.instance().restoreOverrideCursor()
            else:
                # QApplication.instance().restoreOverrideCursor()
                QMessageBox.warning(None, f"No s'ha generat l'informe {report}", msg)
        except Exception as e:
            # QApplication.instance().restoreOverrideCursor()
            QMessageBox.warning(None, f"ERROR a l'informe {report}", str(e))

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

        # sys.path.append(r'C:\OSGeo4W\apps\qgis-ltr\python\plugins')
        # import processing

        # nAlgs = QgsNativeAlgorithms()
        # nAlgs.loadAlgorithms()
        # QgsApplication.processingRegistry().addProvider(nAlgs) 

        dp = QvDataPlotly()
        dp.initGui()

        # llegenda.project.read('projectes/Illes.qgs')
        llegenda.project.read("D:/qVista/DataPlotly/Diagramas.qgs")

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

        # INI Prueba QProgressDialog
        # 
        # m = ""

        # bar = QProgressDialog(m, "Cancel", 0, 100)
        # import time

        # bar.setWindowModality(Qt.WindowModal)
        # bar.setWindowFlags(Qt.WindowStaysOnTopHint)

        # m = "Operation 1 in progress"
        # bar.setLabelText(m)

        # for i in range(101):
        #     time.sleep(0.05)
        #     bar.setValue(i)

        # m = "Operation 2 in progress"
        # bar.setLabelText(m)

        # for i in range(101):
        #     time.sleep(0.05)
        #     bar.setValue(i)

        # m = "Operation 3 in progress"
        # bar.setLabelText(m)

        # for i in range(101):
        #     time.sleep(0.05)
        #     bar.setValue(i)
        # 
        # FIN Prueba QProgressDialog

        # Obtiene el administrador de composiciones
        layoutManager = llegenda.project.layoutManager()
        settings = QgsLayoutExporter.PdfExportSettings()

        print(f"Composiciones de {llegenda.project.fileName()}")
        # Itera sobre las composiciones existentes
        for layout in layoutManager.printLayouts():
            name = layout.name()
            print(f"- {name}")

            # Define la ruta de salida para el archivo PDF
            pdf = llegenda.project.homePath() + '/Test' + name + '.pdf'

            # Exporta la composición a PDF
            exporter = QgsLayoutExporter(layout)
            result = exporter.exportToPdf(pdf, settings)

            # # Exporta la composición a PDF
            # if type(layout) is QgsReport:
            #     result, error = QgsLayoutExporter.exportToPdf(layout, pdfPath, settings)
            # else:
            #     exporter = QgsLayoutExporter(layout)
            #     result = exporter.exportToPdf(pdfPath, settings)

            if result == QgsLayoutExporter.Success:
                print(f"  Informe '{name}' exportado a: {pdf}")
            else:
                print(f"  Error al exportar el informe '{name}': {result}")

        print("*** FIN")
