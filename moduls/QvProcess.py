# -*- coding: utf-8 -*-

import os
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QProgressDialog, QApplication, QMessageBox
from qgis.core import QgsProcessingFeedback
from moduls.QvFuncions import debugging

# INICIALIZACIÓN ENTORNO PROCESSING
# Añadimos (y luego quitamos) el path a plugins de python para hacer el import processing
# from qgis import processing funciona, pero no from processing.core.Processing import Processing
# Nota: la variable de entorno QGIS_WIN_APP_NAME existe al ejecutar QGIS y no con pyQGIS
pythonPath = os.environ.get('PYTHONPATH', '').split(os.pathsep)[0]
os.sys.path.insert(0, pythonPath +  r"\plugins")
import processing
del os.sys.path[0]
from processing.core.Processing import Processing
Processing.initialize()

class QvProcessProgress:
    def __init__(self, showProgress=True):
        self.numProceso = 1
        self.numTotal = 1
        self.feedback = None
        self.progress = None
        self.showProgress = showProgress
        self.title = None
        self.msg = None
        self.steps = []
        self.dialog = True
        self.general = False
        self.canceled = False
        
    def setName(self, name):
        self.title = name
        if len(self.steps) == 0:
            self.steps.append(name)

    def setSteps(self, steps):
        self.steps = steps
        num = len(self.steps)
        if num == 1 and self.title is None:
            self.title = self.steps[0]
        elif num > 1:
            self.numTotal = num

    def getStep(self):
        index = self.numProceso - 1
        if index >= 0 and index < len(self.steps):
            return self.steps[index]
        else:
            return None

    def calcTexts(self):
        title = "Procés"
        msg = "Executant procés"
        try:
            if self.title is not None:
                title = self.title
            if self.numTotal > 1:
                title += " (" + str(self.numProceso) + " de " + str(self.numTotal) + ")"
            step = self.getStep()
            if step is not None:
                title += " - " + step
                msg += " " + step
            msg += " ..."
        except Exception as e:
            print(str(e))
        finally:
            return title, msg

    def prepare(self):
        if self.showProgress:
            if self.numProceso == 1:
                if debugging(): print("INI PROCESO DIALOG")
                self.canceled = False
                self.feedback = QgsProcessingFeedback()
                self.progress = QProgressDialog()
                self.progress.setAutoClose(False)
                self.progress.setAutoReset(False)
                self.progress.setRange(0, 100)
                self.progress.setMinimumWidth(400)
                self.progress.setMinimumHeight(150)
                self.progress.setWindowModality(Qt.WindowModal)
                self.progress.setWindowFlags(Qt.WindowStaysOnTopHint)
            else:
                self.progress.canceled.disconnect()
                self.feedback.progressChanged.disconnect()
            self.progress.canceled.connect(self.cancel)
            self.change(0.0)
            self.feedback.progressChanged.connect(self.change)
            title, self.msg = self.calcTexts()
            self.progress.setWindowTitle(title)
        else:
            if self.numProceso == 1:
                if debugging(): print("INI PROCESO SIN DIALOG")
                self.canceled = False
                QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        self.numProceso += 1
        return self.feedback

    def cancel(self):
        if self.showProgress:
            if debugging(): print("FIN PROCESO DIALOG")
            # self.feedback.cancel()
            self.canceled = True
            if self.progress is not None: self.progress.hide()
        else:
            if debugging(): print("FIN PROCESO SIN DIALOG")
            self.canceled = True
            QApplication.instance().restoreOverrideCursor()

    def change(self, percent):
        if self.canceled: return
        num = round(percent)
        if num == 0:
            self.progress.setLabelText(self.msg)
        self.progress.setValue(num)

class QvProcess:
    def __init__(self, process, showProgress=True):
        self.showProgress = showProgress
        self.progress = QvProcessProgress(self.showProgress)
        self.process, self.processFunction = self.prepare(process)
        self.processDialog = None
    
    def snParam(self, value, default):
        value = value.upper()
        if value == 'S':
            return True
        elif value == 'N':
            return False
        else:
            return default

    def readParams(self, process):
        params = {}
        try:
            import csv
            nameFile = os.getcwd() + r"\processos\processing.csv"
            with open(nameFile, newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if row['NAME'].strip().lower() == process:
                        for field in row:
                            val = row[field].strip()
                            if field == 'NAME': val = val.lower()
                            if field == 'STEPS': val = val.split(',')
                            if field == 'DIALOG': val = self.snParam(val, True)
                            if field == 'GENERAL': val = self.snParam(val, False)
                            params[field] = val
                        break
        except Exception as e:
            print(str(e))
        finally:
            if len(params) > 0:
                return params
            else:
                return None

    def getFunction(self, process):
        moduleName = process + "_processing"
        dialogName = process + "_dialog"
        import importlib
        m = importlib.import_module(f"processos.{process}.{process}_processing")
        # Se busca la función _dialog o la función _processing, según el csv
        if self.progress.dialog:
            return getattr(m, dialogName)
        else:
            return getattr(m, moduleName)
    
    def prepareProgress(self):
        if self.progress is not None:
            return self.progress.prepare()
        else:
            return None

    def prepare(self, process):
        func = None
        try:
            process = process.lower()
            params = self.readParams(process)
            if params is not None:
                # Parámetros del CSV
                self.progress.setName(params['TITLE'])
                self.progress.setSteps(params['STEPS'])
                self.progress.dialog = params['DIALOG']
                self.progress.general = params['GENERAL']
                # Enlace con modulo processing
                import processos.processing as modulProcs
                modulProcs.processingClass = self
                # Se obtiene la funcion de proceso
                func = self.getFunction(process)
            else:
                process = None
        except Exception as e:
            print(str(e))
            process = None
        finally:
            return process, func

    def cancel(self):
        if self.processDialog is not None: self.processDialog.hide()
        if self.progress is not None:
            self.progress.cancel()
            self.progress = None

    def canceled(self):
        if self.progress is not None:
            return self.progress.canceled
        else:
            return True

    def errorMsg(self, msg):
        print(msg)
        self.cancel()
        QMessageBox.warning(None, f"Procés '{self.process}' no finalitzat correctament", msg)

    def execute(self):
        if self.processFunction is None: return False
        try:
            res = self.processFunction()
            if res is None and not self.canceled():
                self.errorMsg("S'ha produït un error intern al procés")
                return False
            if self.progress.dialog:
                self.processDialog = res
            else:
                self.cancel()
            return True
        except Exception as e:
            self.errorMsg("ERROR: " + str(e))
            return False
        
    def run(self, name, params):
        res = None
        try:
            if self.canceled(): return None
            feedback = self.prepareProgress()
            if debugging(): print("RUN - Ini")
            res = processing.run(name, params, feedback=feedback)
            if debugging(): print("RUN - Fin")
            if self.canceled(): return None
            if res is None: self.cancel()
            return res
        except Exception as e:
            self.errorMsg("ERROR: " + str(e))
            return None


    # # Llamada al proceso
    # def run(self, progress=True):
    #     params = {
    #         'INPUT':'D:/qVista/EndrecaSoroll/sorollIris.gpkg|layername=sorollIris',
    #         'MIN_SIZE':5,
    #         'EPS':1,
    #         'DBSCAN*':False,
    #         'FIELD_NAME':'CLUSTER_ID',
    #         'SIZE_FIELD_NAME':'CLUSTER_SIZE',
    #         'OUTPUT':'TEMPORARY_OUTPUT'
    #     }
    #     feedback = None
    #     try:
    #         if progress:
    #             feedback = self.progress.prepare()
    #         else:
    #             QApplication.instance().setOverrideCursor(Qt.WaitCursor)
    #         res = processing.run("native:dbscanclustering", params, feedback=feedback)
    #         if self.progress.wasCanceled():
    #             return None
    #         salida = res['OUTPUT']
    #         QgsProject.instance().addMapLayer(salida)
    #         return res
    #     except Exception as e:
    #         print(str(e))
    #         return None
    #     finally:
    #         if not progress:
    #             QApplication.instance().restoreOverrideCursor()

