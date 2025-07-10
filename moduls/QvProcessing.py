# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QProgressDialog, QApplication, QMessageBox, QMenu, QAction, QPushButton,
                                 QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem)
from qgis.core import QgsApplication
from moduls.QvProviders import QvModelProvider, QvScriptProvider
from moduls.QvSingleton import singleton
from moduls.QvFuncions import debugging, getPythonPath
import os
import csv

@singleton
class QvProcessingConfig:
    """
    Clase para configurar el entorno de procesamiento en QGIS
    También se encarga de cambiar el código Python en un módulo implicado
    para evitar problemas de importación de iface en QGIS
    """
    def __init__(self):
    # INICIALIZACIÓN ENTORNO PROCESSING

        # Primero hay que obtener la ruta de Python para los imports
        # y cambiar código python en un módulo implicado para que no use iface:
        # general.py en python\plugins\processing\tools
        self.pythonPath = getPythonPath()
        self.replacePy = self.changePythonCode() 

        # Añadimos el path al directorio de plugins de python para hacer el import processing
        # from qgis import processing funciona, pero no from processing.core.Processing import Processing
        # Se ha de mantener esa ruta para que se carguen correctamente los algoritmos externos
        # Nota: la variable de entorno QGIS_WIN_APP_NAME existe al ejecutar QGIS y no con pyQGIS
        os.sys.path.insert(0, self.pythonPath +  r"\plugins")
        from processing.core.Processing import Processing
        Processing.initialize()

    def changePythonCode(self):
    # Módulo implicado que usa iface:
    # - C:\OSGeo4W\apps\qgis-ltr\python\plugins\processing\tools\general.py
    # En ese fichero, hay que reemplazar:
    # from qgis.utils import iface
    # por:
    # try:
    #     from _qgis.utils import iface
    # except:
    #     from qgis.utils import iface
        filePath = f"{self.pythonPath}\\plugins\\processing\\tools\\general.py"
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

@singleton
class QvProcessing:
    """
    Clase singleton para gestionar el procesamiento de QGIS en qVista
    """
    def __init__(self):
        # Añade los proveedores de modelos y scripts de qVista al registro de procesamiento
        self.qvModelProvider = QvModelProvider(
            'qvmodel',
            'qVista models',
            'Models disponibles a qVista',
            str(os.path.join(os.getcwd(), "processing", "models"))
        )
        QgsApplication.processingRegistry().addProvider(self.qvModelProvider)
        self.qvScriptProvider = QvScriptProvider(
            'qvscript',
            'qVista scripts',
            'Scripts disponibles a qVista',
            str(os.path.join(os.getcwd(), "processing", "scripts"))
        )
        QgsApplication.processingRegistry().addProvider(self.qvScriptProvider)

    def printAlgorithms(self, onlyProviders=True):
        # Imprime los algoritmos de procesamiento disponibles
        # Si onlyProviders es True, solo imprime los proveedores
        print("*** PROVIDERS:")
        for prov in QgsApplication.processingRegistry().providers():
            print(prov.id(), "-", prov.name(), "->", prov.longName(), "#algs:", len(prov.algorithms()))
            if onlyProviders: continue
            for alg in prov.algorithms():
                print('-', alg.id(), "->", alg.displayName())

    def showAlgorithms(self, providersExcluded=['grass', 'model', 'script']):
        # Se excluyen los proveedores 'model' y 'script' porque son del perfil de usuario
        # y tambien 'grass' porque falta ver cómo se configura para que funcione desde qVista
        algorithmsList = []
        for prov in QgsApplication.processingRegistry().providers():
            if providersExcluded is not None and prov.id() in providersExcluded:
                continue
            item = prov.name() + " - " + prov.longName() + ": #" + str(len(prov.algorithms()))
            algorithmsList.append(item)
            for alg in prov.algorithms():
                item = '- ' + alg.id() + " - " + alg.displayName()
                algorithmsList.append(item)
        selected = QvAlgorithmDialog.show('\n'.join(algorithmsList))
        # Eliminar el guión y todo lo que quede a su derecha
        if selected is not None:
            selected = selected.split('-')[0].strip()
        return selected

    @staticmethod
    def setMenu(title='Processos'):
        # Crea un menú de procesos incrustados en el proyecto QGIS
        # que se puede añadir a un menú de contexto o a una barra de herramientas
        try:
            menu = QMenu()
            menu.setTitle(title)
            prov = QgsApplication.processingRegistry().providerById('project')
            if prov is None:
                return None # No hay proveedor de procesos de proyecto
            # Añadir los algoritmos del proveedor de procesos de proyecto
            for alg in prov.algorithms():
                act = menu.addAction(alg.displayName())
                act.triggered.connect(lambda: QvProcessing().execAlgorithm(alg.id()))
            if menu.isEmpty():
                return None # No hay algoritmos disponibles
            else:
                return menu
        except Exception as e:
            print(str(e))
            return None
        
    def execAlgorithm(self, name, params={}, feedback=False):
        # Ejecuta un algoritmo de procesamiento
        # name: nombre del algoritmo (ej. 'native:buffer')
        msg = "No s'ha pogut iniciar l'algorisme"
        try:
            import processing
            alg = QgsApplication.processingRegistry().algorithmById(name)
            if alg is None:
                QMessageBox.warning(None, msg, f"Algorisme {name} no disponible")
                return
            # Si hay parámetros, se crea el diálogo
            if len(alg.parameterDefinitions()) > 0:
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
            # Si no hay parámetros, se ejecuta directamente sin dialogo
            else:
                processing.run(name, params, feedback=feedback)
        except Exception as e:
            QMessageBox.warning(None, msg, f"Error a l'algorisme {name}\n\n" + str(e))

    # Ejemplo Llamada a proceso desde Python
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

class QvAlgorithmDialog:

    @staticmethod
    def show(texto):
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
        btn_buscar = QPushButton("Cerca")
        btn = QPushButton("Executa")
        btn.setEnabled(False)  # Desactivado por defecto
        btn_cancelar = QPushButton("Tanca")
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

        # Copiar al portapapeles el string hasta el primer guión al hacer doble click en un item hijo
        def on_item_double_clicked(item, column):
            if item and item.parent():
                text = item.text(0)
                text_copiar = text.split('-')[0].strip()
                QApplication.clipboard().setText(text_copiar)

        tree.itemDoubleClicked.connect(on_item_double_clicked)

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
            search_dlg.setWindowTitle("Cerca algorisme")
            search_dlg.setModal(True)
            search_layout = QVBoxLayout(search_dlg)
            from PyQt5.QtWidgets import QLineEdit, QLabel
            lbl = QLabel("Introdueix el text a cercar:")
            search_layout.addWidget(lbl)
            txt = QLineEdit()
            search_layout.addWidget(txt)
            btns = QHBoxLayout()
            btn_ok = QPushButton("Següent")
            btn_prev = QPushButton("Anterior")
            btn_close = QPushButton("Tanca")
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
                    lbl_no_found.setText("No s'ha trobat cap coincidència")
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
