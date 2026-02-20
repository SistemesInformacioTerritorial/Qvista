#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VISOR QGS CON DOS DOCKWIDGETS:
1. ProcessingChainDock - Construir cadenas de procesos (original)
2. ProcessModelsDock - Ejecutar modelos pregrabados (NUEVO)

Versión mejorada con pestaña para elegir modo.
"""

import sys
import os
from pathlib import Path

# Importar QGIS
from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QFileDialog, QMessageBox, QLabel, QSplitter, QDockWidget,
    QTabWidget, QFrame
)
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon

# Importar DockWidgets
from processing_chain_poc import ProcessingChainDock
from process_models_poc import ProcessModelsDock


class QgsViewerAdvanced(QMainWindow):
    """Visor QGS avanzado con cadenas y modelos"""
    
    def __init__(self):
        super().__init__()
        
        self.project = QgsProject.instance()
        self.canvas = None
        self.processing_dock = None
        self.models_dock = None
        
        self.setWindowTitle("QGIS Viewer - Cadenas & Modelos")
        self.setGeometry(100, 100, 1600, 900)
        
        self.initUI()
        self.connectSignals()
    
    def initUI(self):
        """Inicializar interfaz"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Botones superiores
        button_layout = QHBoxLayout()
        
        btn_open = QPushButton("Abrir .qgs")
        btn_open.clicked.connect(self.open_project)
        button_layout.addWidget(btn_open)
        
        btn_clear = QPushButton("Limpiar")
        btn_clear.clicked.connect(self.clear_project)
        button_layout.addWidget(btn_clear)
        
        lbl_status = QLabel("Proyecto: Sin cargar")
        self.lbl_status = lbl_status
        button_layout.addWidget(lbl_status)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Canvas de QGIS
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.enableAntiAliasing(True)
        self.canvas.setMinimumSize(QSize(400, 400))
        
        layout.addWidget(self.canvas)
        
        central_widget.setLayout(layout)
        
        # ===== DOCK WIDGETS LATERALES =====
        
        # DockWidget 1: Cadenas (original)
        self.processing_dock = ProcessingChainDock(self)
        self.processing_dock.setObjectName("ProcessingChainDock")
        self.addDockWidget(Qt.RightDockWidgetArea, self.processing_dock)
        
        # DockWidget 2: Modelos (nuevo)
        self.models_dock = ProcessModelsDock(self)
        self.models_dock.setObjectName("ProcessModelsDock")
        self.addDockWidget(Qt.RightDockWidgetArea, self.models_dock)
        
        # Tabificar para que se muestren como pestañas
        self.tabifyDockWidget(self.processing_dock, self.models_dock)
        
        # Status bar
        self.statusbar_label = QLabel("Listo")
        self.statusBar().addWidget(self.statusbar_label)
    
    def connectSignals(self):
        """Conectar señales"""
        self.processing_dock.status_changed.connect(self.on_status_changed)
        self.models_dock.status_changed.connect(self.on_status_changed)
    
    def open_project(self):
        """Abrir fichero de proyecto"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir proyecto QGIS",
            str(Path.home()),
            "Proyectos QGIS (*.qgs *.qgz);;Todos (*.*)"
        )
        
        if file_path:
            self.load_project(file_path)
    
    def load_project(self, file_path):
        """Cargar proyecto QGIS"""
        try:
            if self.project.read(file_path):
                # Configurar el canvas
                self.canvas.setProject(self.project)
                
                # Obtener todas las capas del proyecto
                layers = self.project.mapLayers()
                
                if len(layers) == 0:
                    self.statusbar_label.setText("Proyecto cargado pero sin capas visibles")
                else:
                    # Agregar capas al canvas
                    layer_list = list(layers.values())
                    self.canvas.setLayers(layer_list)
                    
                    # Zoom a extent completo
                    self.canvas.zoomToFullExtent()
                    self.canvas.refresh()
                
                # Actualizar status
                project_name = Path(file_path).name
                layer_count = len(layers)
                self.lbl_status.setText(f"Proyecto: {project_name} ({layer_count} capas)")
                self.statusbar_label.setText(f"✓ Proyecto cargado: {layer_count} capas")
                
                # Actualizar docks
                if self.processing_dock:
                    self.processing_dock.update_layers()
                if self.models_dock:
                    self.models_dock.update_layers()
                
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Proyecto cargado:\n{project_name}\n{layer_count} capas"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo leer el proyecto:\n{file_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar proyecto:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()
    
    def clear_project(self):
        """Limpiar proyecto"""
        self.project.clear()
        self.canvas.refresh()
        self.lbl_status.setText("Proyecto: Sin cargar")
        self.statusbar_label.setText("Proyecto limpiado")
        
        if self.processing_dock:
            self.processing_dock.update_layers()
        if self.models_dock:
            self.models_dock.update_layers()
    
    def on_status_changed(self, message):
        """Recibir cambios de estado"""
        self.statusbar_label.setText(message)


def main():
    """Punto de entrada"""
    
    # Importar qgisapp context manager
    from qgis.core.contextmanagers import qgisapp
    from qgis.core import QgsApplication
    from qgis.analysis import QgsNativeAlgorithms
    
    # Inicializar QGIS
    with qgisapp(sysexit=False) as qgs_app:
        
        # Inicializar Processing explícitamente
        print("[INIT] Inicializando Processing...")
        registry = QgsApplication.processingRegistry()
        
        if len(list(registry.algorithms())) == 0:
            print("[INIT] Agregando QgsNativeAlgorithms...")
            registry.addProvider(QgsNativeAlgorithms())
            print(f"[INIT] Algoritmos disponibles: {len(list(registry.algorithms()))}")
        
        # Crear ventana
        print("[INIT] Creando ventana...")
        viewer = QgsViewerAdvanced()
        viewer.show()
        
        # Recargar en docks
        print("[INIT] Recargando en docks...")
        if viewer.processing_dock:
            viewer.processing_dock.load_algorithms()
        if viewer.models_dock:
            viewer.models_dock.load_models()
        
        # Si se pasa fichero como argumento
        if len(sys.argv) > 1:
            qgs_file = sys.argv[1]
            if os.path.exists(qgs_file):
                print(f"[INIT] Cargando proyecto: {qgs_file}")
                viewer.load_project(qgs_file)
        
        print("[INIT] ✓ Aplicación lista")
        sys.exit(qgs_app.exec_())


if __name__ == "__main__":
    main()
