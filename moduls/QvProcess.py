# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QProgressDialog, QApplication, QMessageBox, QMenu
from qgis.core import QgsProcessingFeedback
from moduls.QvFuncions import debugging
import os
import csv

# INICIALIZACIÓN ENTORNO PROCESSING
# Añadimos (y luego quitamos) el path a plugins de python para hacer el import processing
# from qgis import processing funciona, pero no from processing.core.Processing import Processing
# Nota: la variable de entorno QGIS_WIN_APP_NAME existe al ejecutar QGIS y no con pyQGIS
pythonPath = os.environ.get('PYTHONPATH', '').split(os.pathsep)[0]
os.sys.path.insert(0, pythonPath +  r"\plugins")
import processing
del os.sys.path[0]
from processing.core.Processing import Processing

class QvProcessCsv:

    _PROCESSING_CSV = os.getcwd() + r"\processos\processing.csv"

    @staticmethod
    def snParam(value, default):
        value = value.upper()
        if value == 'S':
            return True
        elif value == 'N':
            return False
        else:
            return default

    @staticmethod
    def readerCsv():
        with open(QvProcessCsv._PROCESSING_CSV, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # Saltar los registros que empiecen por #
                # (solo despues de la línea de cabecera)
                if row['NAME'].strip()[0] == '#': continue
                yield row

    @staticmethod
    def rowProcess(row):
        return row['NAME'].strip().lower()

    @staticmethod
    def rowParams(row):
        params = {}
        try:
            for field in row:
                val = row[field].strip()
                if field == 'NAME': val = val.lower()
                if field == 'STEPS': val = val.split(',')
                if field == 'DIALOG': val = QvProcessCsv.snParam(val, True)
                if field == 'PROGRESS': val = QvProcessCsv.snParam(val, True)
                if field == 'GENERAL': val = QvProcessCsv.snParam(val, False)
                params[field] = val
        except Exception as e:
            print(str(e))
        finally:
            if len(params) > 0:
                return params
            else:
                return None

    @staticmethod
    def readParams(process):
        params = {}
        try:
            # with open(_PROCESSING_CSV, newline='') as csvfile:
            #     reader = csv.DictReader(csvfile, delimiter=';')
            #     for row in reader:
            #         if rowProcess() == process:
            #             params = rowParams(row)
            #             break
            for row in QvProcessCsv.readerCsv():
                if QvProcessCsv.rowProcess(row) == process:
                    params = QvProcessCsv.rowParams(row)
                    break
        except Exception as e:
            print(str(e))
        finally:
            if len(params) > 0:
                return params
            else:
                return None

class QvProcessProgress:
    def __init__(self):
        self.numProceso = 1
        self.numTotal = 1
        self.feedback = None
        self.progress = None
        self.canceled = False
        self.processDialog = None
        self.msg = None
        # Valores del csv:
        self.title = None
        self.steps = []
        self.showDialog = True
        self.showProgress = True
        self.general = False

    def setSteps(self, steps):
        self.steps = steps
        num = len(self.steps)
        # Si no hay steps, se añade uno con el contenido de title
        if num == 0:
            self.steps.append(self.title)
        # Si no hay title, se pone el contenido del step 1
        elif num == 1 and self.title is None:
            self.title = self.steps[0]
        elif num > 1:
            self.numTotal = num

    def getStep(self):
        index = self.numProceso - 1
        if index >= 0 and index < len(self.steps):
            return self.steps[index]
        else:
            return None

    def setProcessDialog(self, dlg):
        if dlg is not None:
            self.processDialog = dlg
            if self.title is not None:
                self.processDialog.setWindowTitle(self.title)

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
                if debugging(): print("INI PROCESO PROGRESO")
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
                # self.feedback.canceled.disconnect()
            self.progress.canceled.connect(self.cancel)
            self.change(0.0)
            self.feedback.progressChanged.connect(self.change)
            # self.feedback.canceled.connect(self.cancel)
            title, self.msg = self.calcTexts()
            self.progress.setWindowTitle(title)
        else:
            if self.numProceso == 1:
                if debugging(): print("INI PROCESO SIN PROGRESO")
                self.canceled = False
                QApplication.instance().setOverrideCursor(Qt.WaitCursor)
        self.numProceso += 1
        return self.feedback

    def change(self, percent):
        if self.progress is None or self.canceled: return
        num = round(percent)
        if num == 0:
            self.progress.setLabelText(self.msg)
        # if debugging(): print('-', self.numProceso - 1, num)
        self.progress.setValue(num)

    def reset(self):
        if self.showProgress:
            if debugging(): print("FIN PROCESO PROGRESS")
            if self.feedback is not None: self.feedback.cancel()
            if self.progress is not None: self.progress.hide()
        else:
            if debugging(): print("FIN PROCESO SIN PROGRESS")
            QApplication.instance().restoreOverrideCursor()
        self.numProceso = 1

    def cancel(self):
        self.canceled = True
        if self.processDialog is not None: self.processDialog.hide()
        self.reset()

    def end(self):
        self.change(100)
        if self.numProceso > self.numTotal:
            if self.progress is not None: self.progress.hide()
            self.reset()

class QvProcess:
    def __init__(self, process):
        self.process = None
        self.processFunction = None
        self.progress = None
        self.init(process)

    def init(self, process=None):
        self.progress = QvProcessProgress()
        self.process, self.processFunction = self.prepare(process)
            
    def setParams(self, params):
        self.progress.title = params['TITLE']
        self.progress.setSteps(params['STEPS'])
        self.progress.showDialog = params['DIALOG']
        self.progress.showProgress = params['PROGRESS']
        self.progress.general = params['GENERAL']

    def getFunction(self, process):
        # Enlace con la clase de proceso
        import processos.processing as modulProcs
        modulProcs.processingClass = self
        # Se obtiene la funcion de proceso del modulo processing
        moduleName = process + "_processing"
        dialogName = process + "_dialog"
        import importlib
        m = importlib.import_module(f"processos.{process}.{process}_processing")
        # Se busca la función _dialog o la función _processing, según el csv
        if self.progress.showDialog:
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
            params = QvProcessCsv.readParams(process)
            if params is not None:
                self.setParams(params)
                func = self.getFunction(process)
            else:
                process = None
        except Exception as e:
            print(str(e))
            process = None
        finally:
            return process, func

    def cancel(self):
        if self.progress is not None:
            self.progress.cancel()
            self.progress = None

    def canceled(self):
        if self.progress is not None:
            return self.progress.canceled
        else:
            return True

    def end(self):
        if self.progress is not None:
            self.progress.end()

    def errorMsg(self, msg):
        print(msg)
        self.cancel()
        if self.process is None:
            QMessageBox.warning(None, f"No s'ha pogut executar el procés", msg)
        else:
            QMessageBox.warning(None, f"Procés '{self.process}' no finalitzat correctament", msg)

    def callFunction(self):
        if self.processFunction is None:
            self.errorMsg("Hi ha errors a la configuració del procés")
            return False
        try:
            res = self.processFunction()
            if res is None and not self.canceled():
                self.errorMsg("S'ha produït un error intern al procés")
                return False
            if self.progress.showDialog:
                self.progress.setProcessDialog(res)
            else:
                self.cancel()
            return True
        except Exception as e:
            self.errorMsg("ERROR: " + str(e))
            return False

    @staticmethod
    def setMenu(widget):
    # Hay que indicar el widget donde aparece el menu para acceder al sender()
    # De ahí recogemos el proceso a ejecutar de la propiedad 'qv_process' del widget
        try:
            menu = QMenu()
            menu.setTitle('Processos')
            for row in QvProcessCsv.readerCsv():
                params = QvProcessCsv.rowParams(row)
                process = params['NAME']
                title = params['TITLE']
                general = params['GENERAL']
                if general and process is not None and not process == '':
                    act = menu.addAction(title)
                    act.setProperty('qv_process', process)
                    act.triggered.connect(lambda: QvProcess.execute(widget.sender().property('qv_process')))
            if menu.isEmpty():
                return None
            else:
                return menu
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def execute(process):
        try:
            p = QvProcess(process)
            return p.callFunction()
        except Exception as e:
            print(str(e))            
            return False

    def run(self, name, params):
        res = None
        try:
            feedback = self.prepareProgress()
            if debugging(): print("RUN - Ini")
            Processing.initialize()
            res = processing.run(name, params, feedback=feedback)
            if debugging(): print("RUN - Fin")
            if self.canceled(): return None
            if res is None:
                self.cancel()
            else:
                self.end()
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

