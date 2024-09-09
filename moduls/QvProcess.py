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

# **************************************************************************************************

# CARPETA DE INSTALACIÓN:
# Se identifica un proceso por un nombre en minúsculas; por ejemplo: "soroll"
# Los nombres de los archivos relacionados con este proceso comenzaran con el prefijo "soroll"
# Se colocaran esos ficheros en la carpeta qVista\Codi\processos
# En esa carpeta estarán processing.py y processing.csv, necesarios para la ejecución desde qVista
# La función processing.run() está recubierta en proccessing.py para que qVista la controle
# Esto posibilita que el usuario reciba información del progreso del proceso y de sus errores

# CATÁLOGO EN FICHERO CSV:
# En processing.csv cada línea define un proceso, con información que se mostrará al usuario
# Incluye el campo TITLE y opcionalmente sus STEPS (uno por cada llamada a processing.run()): 
# GLOBAL es para indicar si el proceso puede usarse desde cualquier proyecto o no
# Ejemplo para "soroll", proceso con 3 pasos:
# NAME;TITLE;STEPS;GLOBAL
# soroll;Àrees d'interès;Clustering,Envelop,Buffering;N

# CÓDIGO DE EJECUCIÓN:
# Para soroll, el archivo que contiene el código a ejecutar se llamará soroll_processing.py
# Han de eliminarse las referencias a iface (no compatible con qVista)
# Para que funcione tanto en qVista como en QGIS, el import de processing tendrá esta forma:
# try:
#     from .processing import *    # qVista
# except:
#     from qgis import processing  # QGIS
# Del módulo processing solo se usará la función run: res = processing.run(algorithm, params)
# Para controlar los errores, se ha de chequear el resultado de cada processing.run()

# FUNCIONES DE EJECUCIÓN:
# soroll_processing.py puede contener dos funciones para ser llamadas desde qVista:
# - soroll_dialog(), que presenta al usuario un formulario de parámetros del proceso
# - soroll_processing(), para ejecución directa sin formulario
# Si existe, se ejecuta soroll_dialog() y si no, soroll_processing(), ambas sin parámetros

# EJECUCIÓN CON FORMULARIO:
# La función soroll_dialog() presentará el formulario para recoger los parámetros
# Si va bien, la función retornará el QDialog creado; si no, devolverá None
# Al aceptar el usuario, el formulario invocará a una función de soroll_processing.py
# En el caso de soroll es la función Areas(), encargada de las llamadas a processing.run() 
# Esta función tambien tendrá un control de las excepciones para que no llegen a qVista

# EJECUCIÓN SIN FORMULARIO:
# La función soroll_processing() contendrá las llamadas a processing.run()
# En caso de error o excepción, retornará None
# Si termina con éxito, devolverá el resultado del último processing.run()

# EJEMPLOS DE USO:
# Ejemplo del uso común desde qVista, con diálogos que informan del progreso de la ejecución:
# from moduls.QvProcess import QvProcess
# process = QvProcess('soroll')
# process.execute()
# La función process.execute() devuelve True o False para indicar si el proceso acabó bien o no
# Para ejecutar en modo silencioso (sin información del progreso), cambiar la segunda línea por:
# process = QvProcess('soroll', False)

# DOCS QGIS PROCESSING:
# https://docs.qgis.org/3.22/en/docs/user_manual/processing/index.html

# **************************************************************************************************

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
        self.process, self.modeDialog, self.processFunction = self.prepare(process)
        self.processDialog = None
    
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
        # Modulo namespace
        i = __import__("processos." + moduleName, globals(), locals(), [], 0)
        # Modulo _processing
        m = getattr(i, moduleName)
        # Primero se busca la función _dialog; si no está, la función _processing
        try:
            func =  getattr(m, dialogName)
            return True, func
        except:
            pass
        func =  getattr(m, moduleName)
        return False, func
    
    def prepareProgress(self):
        if self.progress is not None:
            return self.progress.prepare()
        else:
            return None

    def prepare(self, process):
        func = None
        mode = None
        try:
            process = process.lower()
            params = self.readParams(process)
            if params is not None:
                # Parámetros del CSV
                self.progress.setName(params['TITLE'])
                self.progress.setSteps(params['STEPS'].split(','))
                # Enlace con modulo processing
                import processos.processing as modulProcs
                modulProcs.processingClass = self
                # Se obtiene la funcion de proceso
                mode, func = self.getFunction(process)
            else:
                process = None
        except Exception as e:
            print(str(e))
            process = None
        finally:
            return process, mode, func

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
            if self.modeDialog:
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

