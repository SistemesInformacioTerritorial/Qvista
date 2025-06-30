# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QProgressDialog, QApplication, QMessageBox, QMenu, QAction, QPushButton,
                                 QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem)
from qgis.core import QgsProcessingFeedback, QgsApplication
from moduls.QvProviders import QvProjectProvider, QvQvistaProvider
from moduls.QvSingleton import singleton
from moduls.QvFuncions import debugging
import os
import csv

class QvProcessingInit:

    @staticmethod    
    def getPythonPath():
        for p in os.environ.get('PYTHONPATH', '').split(os.pathsep):
            if p.split('\\')[-1] == 'python':
                return p
        return ''

    @staticmethod    
    def changePythonCode():
    # Módulo implicado que usa iface:
    # - C:\OSGeo4W\apps\qgis-ltr\python\plugins\processing\tools\general.py
    # En ese fichero, hay que reemplazar:
    # from qgis.utils import iface
    # por:
    # try:
    #     from _qgis.utils import iface
    # except:
    #     from qgis.utils import iface
        filePath = f"{_PYTHON_PATH}\\plugins\\processing\\tools\\general.py"
        qgisImport = "from qgis.utils import iface"
        qvistaImport = "from _qgis.utils import iface"
        tryImport =f"try:\n\t{qvistaImport}\nexcept:\n\t{qgisImport}"

        # Leer general.py
        with open(filePath, 'r') as file:
            fileContents = file.read()
        # Si ya contiene el import de qvista, salir
        if fileContents.find(qvistaImport) != -1: return True
        # Reemplazar el import de qgis por el import combinado con try
        updatedContents = fileContents.replace(qgisImport, tryImport, 1)
        # Si no se ha reemplazado nada, salir
        if updatedContents == fileContents: return True
        # Guardar cambios en general.py
        with open(filePath, 'w') as file:
            file.write(updatedContents)
            return True
        return False

# INICIALIZACIÓN ENTORNO PROCESSING

# Primero hay que obtener la ruta de Python para los imports
# y cambiar código python en un módulo implicado para que no use iface
_PYTHON_PATH = QvProcessingInit.getPythonPath()
_REPLACE_PY = QvProcessingInit.changePythonCode()

# Añadimos el path al directorio de plugins de python para hacer el import processing
# from qgis import processing funciona, pero no from processing.core.Processing import Processing
# Se ha de mantener esa ruta para que se carguen correctamente los algoritmos externos
# Nota: la variable de entorno QGIS_WIN_APP_NAME existe al ejecutar QGIS y no con pyQGIS
os.sys.path.insert(0, _PYTHON_PATH +  r"\plugins")
import processing
from processing.core.Processing import Processing
Processing.initialize()

class QvPluginsCsv:

    _PLUGINS_CSV = os.getcwd() + r"\processos\plugins\processing.csv"

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
        with open(QvPluginsCsv._PLUGINS_CSV, newline='') as csvfile:
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
                if field == 'PROGRESS': val = QvPluginsCsv.snParam(val, True)
                if field == 'GENERAL': val = QvPluginsCsv.snParam(val, False)
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
            for row in QvPluginsCsv.readerCsv():
                if QvPluginsCsv.rowProcess(row) == process:
                    params = QvPluginsCsv.rowParams(row)
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
        self.showDialog = None
        # Valores del csv:
        self.title = None
        self.steps = []
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

class QvProcessPlugin:
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
        self.progress.showProgress = params['PROGRESS']
        self.progress.general = params['GENERAL']

    def getFunction(self, process):
        func = None
        self.progress.showDialog = None
        try:
            # Enlace con la clase de proceso
            import processos.plugins.processing as modulProcs
            modulProcs.processingClass = self
            # Se obtiene la funcion de proceso del modulo processing
            moduleName = process + "_processing"
            dialogName = process + "_dialog"
            import importlib
            m = importlib.import_module(f"processos.plugins.{process}.{process}_processing")
            # Se busca la función _dialog y la función _processing, en este orden
            if hasattr(m, dialogName):
                func = getattr(m, dialogName)
                self.progress.showDialog = True
            elif hasattr(m, moduleName):
                func = getattr(m, moduleName)
                self.progress.showDialog = False
        except Exception as e:
            print(str(e))
            func = None
            self.progress.showDialog = None
        finally:
            return func
    
    def prepareProgress(self):
        if self.progress is not None:
            return self.progress.prepare()
        else:
            return None

    def prepare(self, process):
        func = None
        try:
            process = process.lower()
            params = QvPluginsCsv.readParams(process)
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
        
    def run(self, name, params):
        res = None
        try:
            feedback = self.prepareProgress()
            if debugging(): print("RUN - Ini")
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

class QvProcessingMenu:
    def __init__(self, widget, singleMenu):
    # Hay que indicar el widget donde aparece el menu para acceder al sender()
    # Del widget recogemos el proceso a ejecutar de la propiedad 'qv_process' del widget
        self.widget = widget
        self.singleMenu = singleMenu
        self.menuPlugins = self.setMenuPlugins()
        self.menuAlgorithms = self.setMenuModels()
        self.menuProcesses = self.setMenuProcesses()

    def menu(self):
        return self.menuProcesses
    
    def addMenuAction(self, menu, process, title, plugin=False, label=None):
        if plugin:
            triggerFunction = QvProcessing().execPlugin
            if label is None: label = 'Plugin'
        else:
            triggerFunction = QvProcessing().execAlgorithm
            if label is None: label = 'Algorisme'
        toolTip = label + ' ' + process
        act = menu.addAction(title)
        act.setToolTip(toolTip)
        act.setProperty('qv_process', process)
        act.triggered.connect(lambda: triggerFunction(self.widget.sender().property('qv_process')))

    def addMenuProviderActions(self, provider, menu):
        if provider is None: return
        for alg in provider.algorithms():
            if provider.id() in ('model', 'project', 'qvista'):
                label = 'Model'
            else:
                label = 'Algorisme'
            process = provider.id() + ':' + alg.name()
            title = alg.displayName()
            self.addMenuAction(menu, process, title, False, label)

    def setMenuPlugins(self):
        try:
            menu = QMenu('Plugins')
            menu.setToolTipsVisible(True)
            for row in QvPluginsCsv.readerCsv():
                params = QvPluginsCsv.rowParams(row)
                process = params['NAME']
                title = params['TITLE']
                general = params['GENERAL']
                if general and process is not None and not process == '':
                    self.addMenuAction(menu, process, title, True)
            if menu.isEmpty():
                return None
            else:
                return menu
        except Exception as e:
            print(str(e))
            return None

    def setMenuModels(self):
        try:
            menu = QMenu('Models')
            menu.setToolTipsVisible(True)
            # Models provider 'project'
            self.addMenuProviderActions(QvProcessing().projectProvider, menu)
            # Models provider 'qvista'
            self.addMenuProviderActions(QvProcessing().qvistaProvider, menu)
            if menu.isEmpty():
                return None
            else:
                return menu
        except Exception as e:
            print(str(e))
            return None

    def setMenuProcesses(self):
        try:
            label = 'Processos'
            if self.menuPlugins is None:
                if self.singleMenu and self.menuAlgorithms is not None:
                    self.menuAlgorithms.setTitle(label)
                return self.menuAlgorithms
            else:
                if self.menuAlgorithms is None:
                    if self.singleMenu: self.menuPlugins.setTitle(label)
                    return self.menuPlugins
                else:
                    menu = QMenu(label)
                    menu.setToolTipsVisible(True)
                    if self.singleMenu:
                        for act in self.menuPlugins.actions():
                            menu.addAction(act)
                        menu.addSeparator()
                        for act in self.menuAlgorithms.actions():
                            menu.addAction(act)
                    else:
                        menu.addMenu(self.menuPlugins)
                        menu.addMenu(self.menuAlgorithms)
                    return menu
        except Exception as e:
            print(str(e))
            return None

@singleton
class QvProcessing:
    def __init__(self):
        self.projectProvider = None
        self.qvistaProvider = QvQvistaProvider()
        QgsApplication.processingRegistry().addProvider(self.qvistaProvider)
        self.processingMenu = None
        self.algorithmsList = []

    def initializeProcessing(self):
        Processing.initialize()
        self.projectProvider = QvProjectProvider.loadAlgorithms()
        if debugging():
            self.printAlgorithms(('project', 'model', 'qvista'))

    def printAlgorithms(self, providersList=None):
        print("*** PROVIDERS:")
        for prov in QgsApplication.processingRegistry().providers():
            print(prov.id(), "-", prov.name(), "->", prov.longName(), "#algs:", len(prov.algorithms()))
            if providersList is not None and prov.id() not in providersList: continue
            for alg in prov.algorithms():
                print('-', alg.id(), "->", alg.displayName())

    def showAlgorithms(self, providersList=None):
        for prov in QgsApplication.processingRegistry().providers():
            item = prov.name() + " - " + prov.longName() + ": #" + str(len(prov.algorithms()))
            self.algorithmsList.append(item)
            if providersList is not None and prov.id() not in providersList: continue
            for alg in prov.algorithms():
                item = '- ' + alg.id() + " - " + alg.displayName()
                self.algorithmsList.append(item)
        selected = self.selectAlgorithm('\n'.join(self.algorithmsList))
        # Eliminar el guión y todo lo que quede a su derecha
        if selected is not None:
            selected = selected.split('-')[0].strip()
        return selected

    def selectAlgorithm(self, texto):
        """
        Muestra un diálogo para seleccionar un item de una estructura tipo:
        Nivel 1
        - Item 1
        - Item 2
        Nivel 2
        - Item A
        - Item B
        """
        # Parsear el texto
        niveles = {}
        nivel_actual = None
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith('-'):
                if nivel_actual:
                    niveles[nivel_actual].append(linea[1:].strip())
            else:
                nivel_actual = linea
                niveles[nivel_actual] = []

        # Crear el diálogo
        dlg = QDialog()
        dlg.setWindowTitle("Selecciona un algorisme per executar")
        dlg.resize(800, 500)
        layout = QVBoxLayout(dlg)
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        for nivel, items in niveles.items():
            parent = QTreeWidgetItem([nivel])
            parent.setFlags(parent.flags() & ~Qt.ItemIsSelectable)  # No seleccionable
            parent.setSelected(False)
            for item in items:
                child = QTreeWidgetItem([item])
                parent.addChild(child)
            tree.addTopLevelItem(parent)
        layout.addWidget(tree)
        btn_layout = QHBoxLayout()
        btn_buscar = QPushButton("🔍 Cerca")
        btn = QPushButton("⚙️ Executa")
        btn.setEnabled(False)  # Desactivado por defecto
        btn_cancelar = QPushButton("❌ Tanca")
        btn_layout.addWidget(btn_buscar)
        btn_layout.addWidget(btn)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
        btn_cancelar.setDefault(True)
        btn_cancelar.setAutoDefault(True)

        seleccion = {'item': None}

        def on_tree_selection_changed():
            item = tree.currentItem()
            # Solo activar si es un hijo (tiene padre)
            btn.setEnabled(item is not None and item.parent() is not None)

        tree.currentItemChanged.connect(lambda curr, prev: on_tree_selection_changed())

        # Deseleccionar item si su rama se cierra
        def on_item_collapsed(item):
            # Si el item colapsado tiene un hijo seleccionado, deseleccionarlo
            selected = tree.currentItem()
            if selected and selected.parent() == item:
                tree.setCurrentItem(None)

        tree.itemCollapsed.connect(on_item_collapsed)

        def aceptar():
            item = tree.currentItem()
            if item and item.parent():
                seleccion['item'] = item.text(0)
                dlg.accept()

        def cancelar():
            seleccion['item'] = None
            dlg.reject()

        def buscar():
            # Formulario flotante para buscar string
            search_dlg = QDialog(dlg)
            search_dlg.setWindowTitle("Cerca item")
            search_dlg.setModal(True)
            search_layout = QVBoxLayout(search_dlg)
            from PyQt5.QtWidgets import QLineEdit, QLabel
            lbl = QLabel("Introdueix el text a cercar:")
            search_layout.addWidget(lbl)
            txt = QLineEdit()
            search_layout.addWidget(txt)
            btns = QHBoxLayout()
            btn_ok = QPushButton("🔍 Següent")
            btn_prev = QPushButton("🔍 Anterior")
            btn_close = QPushButton("❌ Tanca")
            btns.addWidget(btn_ok)
            btns.addWidget(btn_prev)
            btns.addWidget(btn_close)
            search_layout.addLayout(btns)
            lbl_no_found = QLabel("")
            search_layout.addWidget(lbl_no_found)

            # Recopilar todos los items hijos en una lista para búsqueda secuencial
            items_hijos = []
            for i in range(tree.topLevelItemCount()):
                parent = tree.topLevelItem(i)
                for j in range(parent.childCount()):
                    items_hijos.append(parent.child(j))

            # Estado de búsqueda
            estado = {'indices': [], 'actual': -1, 'last_text': ''}

            def do_search(next=True):
                texto_buscar = txt.text().strip().lower()
                if not texto_buscar:
                    lbl_no_found.setText("")
                    return
                # Si cambia el texto de búsqueda, recalcular coincidencias
                if texto_buscar != estado['last_text']:
                    estado['indices'] = [idx for idx, item in enumerate(items_hijos) if texto_buscar in item.text(0).lower()]
                    estado['actual'] = -1
                    estado['last_text'] = texto_buscar
                if not estado['indices']:
                    lbl_no_found.setText("No s'ha trobat cap item")
                    return
                # Mostrar cuántas coincidencias hay y la posición actual
                total = len(estado['indices'])
                actual = (estado['actual'] + 1) if estado['actual'] >= 0 else 1
                lbl_no_found.setText(f"Coincidències: {total} ({actual}/{total})")
                # Buscar siguiente o anterior
                if next:
                    estado['actual'] = (estado['actual'] + 1) % total
                else:
                    estado['actual'] = (estado['actual'] - 1) % total
                idx = estado['indices'][estado['actual']]
                item = items_hijos[idx]
                tree.setCurrentItem(item)
                tree.scrollToItem(item)

            btn_ok.clicked.connect(lambda: do_search(True))
            btn_prev.clicked.connect(lambda: do_search(False))
            btn_close.clicked.connect(search_dlg.reject)
            search_dlg.exec_()
        btn.clicked.connect(aceptar)
        btn_cancelar.clicked.connect(cancelar)
        btn_buscar.clicked.connect(buscar)
        # Por defecto, foco en Cancelar
        btn_cancelar.setDefault(True)
        btn_cancelar.setAutoDefault(True)
        dlg.exec_()
        return seleccion['item']

    def addMenuProcess(self, process, title, label=None):
        self.processingMenu.addMenuAction(self.processingMenu.menu(), process, title, False, label)
    
    def setMenu(self, widget, singleMenu=True):
        self.initializeProcessing()
        self.processingMenu = QvProcessingMenu(widget, singleMenu)
        return self.processingMenu.menu()

    def execPlugin(self, process):
        try:
            self.initializeProcessing()
            p = QvProcessPlugin(process)
            return p.callFunction()
        except Exception as e:
            print(str(e))            
            return False

    def execAlgorithm(self, name, params={}):
        msg = "No s'ha pogut iniciar l'algorisme"
        try:
            self.initializeProcessing()
            dialog = processing.createAlgorithmDialog(name, params)
            if dialog is None:
                QMessageBox.warning(None, msg, f"Algorisme {name} no disponible")
                return
            # Se elimina el boton de ejecución por lotes
            for button in dialog.findChildren(QPushButton):
                if ' lots' in button.text():
                    button.setDisabled(True)
                    button.setVisible(False)
                    break
            dialog.show()
        except Exception as e:
            QMessageBox.warning(None, msg, f"Error a l'algorisme {name}\n\n" + str(e))


if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canv = QvCanvas()

        atrib = QvAtributs(canv)

        leyenda = QvLlegenda(canv, atrib)

        leyenda.project.read("D:/soroll/GlobalSoroll.qgs.qgs")

        dialog = None

        # Acciones de usuario para el menú

        #*****************************************************************************

        def modeloProyecto():
            dialog = processing.createAlgorithmDialog("project:EmulacionPlugin", {})
            if dialog is not None: dialog.show()

        act = QAction()
        act.setText("Modelo de proyecto")
        act.triggered.connect(modeloProyecto)
        leyenda.accions.afegirAccio('modeloProyecto', act)

        #*****************************************************************************

        def modeloPerfil():
            ret = processing.execAlgorithmDialog("model:EmulacionPlugin", {})
            dialog = processing.createAlgorithmDialog("project:EmulacionPlugin", {})
            if dialog is not None: dialog.show()

        act = QAction()
        act.setText("Modelo de perfil")
        act.triggered.connect(modeloPerfil)
        leyenda.accions.afegirAccio('modeloPerfil', act)

        #*****************************************************************************

        def buffer():
            dialog = processing.createAlgorithmDialog("native:buffer", {})
            if dialog is not None: dialog.show()

        act = QAction()
        act.setText("Buffer")
        act.triggered.connect(buffer)
        leyenda.accions.afegirAccio('buffer', act)

        #*****************************************************************************

        def menuContexte(tipo):
            if tipo == 'none':
                # leyenda.menuAccions.append('project:EmulacionPlugin')
                # leyenda.menuAccions.append('model:EmulacionPlugin')
                leyenda.menuAccions.append('buffer')
                leyenda.menuAccions.append('modeloProyecto')
                leyenda.menuAccions.append('modeloPerfil')

        leyenda.clicatMenuContexte.connect(menuContexte)

        canv.show()
        leyenda.show()
        leyenda.menuAccions.append('modeloProyecto')
        leyenda.menuAccions.append('modeloPerfil')

        leyenda.clicatMenuContexte.connect(menuContexte)

        canv.show()
        leyenda.show()
