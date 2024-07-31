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
        self.menu = None
        self.progressDialog = None

    def listReports(self):
        layoutManager = QgsProject.instance().layoutManager()
        return [layout.name() for layout in layoutManager.layouts()]

    def progressCancel(self):
        if debugging(): print("Informe cancel·lat")
        self.feedback.cancel()

    def progressChange(self, progress, txt="Generant informe"):
        num = round(progress)
        if num == 0:
            msg = txt + " ..."
            self.progressDialog.setLabelText(msg)
        elif num > 100:
            num = num // 100
            msg = txt + " - Secció " + str(num) + " ..."
            self.progressDialog.setLabelText(msg)
        else:
            msg = txt + " " + str(num)
        if debugging(): print(msg)
        if self.progressDialog.wasCanceled():
            self.progressDialog.setValue(100)
        else:
            self.progressDialog.setValue(num)

    def msgReport(self, result):
        if result in range(len(QvReports.ExportMsgs)):
            return QvReports.ExportMsgs[result]
        else:
            return "Error en la generació de l'informe"

    def progressInit(self, name, cancel=True, bar=True, title="Informe PDF"):
        self.progressDialog = QProgressDialog()
        if cancel:
            self.progressDialog.canceled.connect(self.progressCancel)
        for w in self.progressDialog.children():
            if isinstance(w, QProgressBar) and not bar:
                w.hide()
            elif isinstance(w, QPushButton) and not cancel:
                w.setEnabled(False)
                w.hide()
            elif isinstance(w, QShortcut) and not cancel:
                w.setEnabled(False)
        self.progressDialog.setRange(0, 100)
        self.progressDialog.setWindowTitle(title + " - " + name)
        self.progressDialog.setMinimumWidth(400)
        self.progressDialog.setMinimumHeight(150)
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.progressChange(0.0)
        return self.progressDialog

    def reportToPdf(self, name):
        try: 
            layoutManager = QgsProject.instance().layoutManager()
            layout = layoutManager.layoutByName(name)
            if layout is None:
                return -1, "Informe no trobat", None
        except Exception as e:
            return -1, "Informe no trobat - " + str(e), None

        try: # https://github.com/carey136/Standalone-Export-Atlas-QGIS3/blob/master/AtlasExport.py

            pdf = self.path + '/' + name + '.pdf'

            if layout.layoutType() == layout.PrintLayout: # static layouts y atlas layouts
                atlas = layout.atlas()
                if atlas.enabled():
                    # Atlas layout
                    # Parámetros
                    atlasLayout = atlas.layout()
                    exporter = QgsLayoutExporter(atlasLayout)
                    settings = exporter.PdfExportSettings()
                    settings.exportLayersAsSeperateFiles = False
                    # Progreso
                    self.feedback = QgsFeedback()
                    self.progressInit(name)
                    self.feedback.progressChanged.connect(self.progressChange)
                    # Exportación
                    result, _ = QgsLayoutExporter.exportToPdf(atlas, pdf, settings, self.feedback)
                else:
                    # Static layout
                    # Parámetros
                    exporter = QgsLayoutExporter(layout)
                    settings = exporter.PdfExportSettings()
                    # Progreso (sin cancel y sin barra)
                    self.progressInit(name, cancel=False, bar=False)
                    # Exportación
                    result = exporter.exportToPdf(pdf, settings)
                    self.progressDialog.reset()

            else: # layout.layoutType() == layout.Report
                # Report layout                
                # Parámetros
                settings = QgsLayoutExporter.PdfExportSettings() # default settings
                settings.exportLayersAsSeperateFiles = False
                # Progreso (sin barra)
                self.feedback = QgsFeedback()
                self.progressInit(name, bar=False)
                self.feedback.progressChanged.connect(self.progressChange)
                # Exportación
                result, _ = QgsLayoutExporter.exportToPdf(layout, pdf, settings, self.feedback)

            msg = self.msgReport(result)
            if result == QgsLayoutExporter.Success:
                return result, msg, pdf
            else:
                return result, msg, None

        except Exception as e:
            return -1, "Error en la generació  - " + str(e), None
        finally:
            if self.progressDialog is not None: 
                self.progressDialog.reset()

    def menuReport(self):
        try:
            report = self.llegenda.sender().text()
            result, msg, pdf = self.reportToPdf(report)
            if result == QgsLayoutExporter.Success:
                os.startfile(pdf)
            else:
                QMessageBox.warning(None, f"No s'ha generat l'informe {report}", msg)
        except Exception as e:
            QMessageBox.warning(None, f"ERROR a l'informe {report}", str(e))

    def setMenu(self, title='Informes PDF'):
        self.menu = QMenu()
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
