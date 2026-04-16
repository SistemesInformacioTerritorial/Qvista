#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VISOR QGS MÍNIMO CON DOCKWIDGET DE PROCESOS
Proof of Concept para ProcessingChain en qVista

Uso:
  python3 qgs_viewer_poc.py [fichero.qgs]
"""

import sys
import os
from pathlib import Path

# Importar QGIS
from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QFileDialog, QMessageBox, QLabel, QSplitter, QDockWidget
)
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon

# Importar nuestro DockWidget de procesos
from processing_chain_poc import ProcessingChainDock


class QgsViewerPOC(QMainWindow):
    """Visor QGS mínimo con DockWidget de procesos"""
    
    def __init__(self):
        super().__init__()
        
        self.project = QgsProject.instance()
        self.canvas = None
        
        self.setWindowTitle("QGIS Viewer - Processing Chain POC")
        self.setGeometry(100, 100, 1400, 900)
        
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
        
        # DockWidget de procesos (lateral derecho)
        self.processing_dock = ProcessingChainDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.processing_dock)
        
        self.statusbar_label = QLabel("Listo")
        self.statusBar().addWidget(self.statusbar_label)
        
    def connectSignals(self):
        """Conectar señales"""
        if self.processing_dock:
            self.processing_dock.status_changed.connect(self.on_status_changed)
    
    def open_project(self):
        """Abrir fichero .qgs"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir proyecto QGIS",
            "",
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
                
                # Actualizar dock de procesos con capas
                if self.processing_dock:
                    self.processing_dock.update_layers()
                
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
    
    def on_status_changed(self, message):
        """Recibir cambios de estado del dock"""
        self.statusbar_label.setText(message)


def main():
    """Punto de entrada"""
    
    # Importar qgisapp context manager (como en qVista.py)
    from qgis.core.contextmanagers import qgisapp
    from qgis.core import QgsApplication
    from qgis.analysis import QgsNativeAlgorithms
    
    # Inicializar QGIS usando context manager (método correcto)
    with qgisapp(sysexit=False) as qgs_app:
        
        # Inicializar Processing de forma explícita
        print("[INIT] Inicializando Processing...")
        registry = QgsApplication.processingRegistry()
        
        # Agregar algoritmos nativos si no los hay
        providers = registry.providers()
        print(f"[INIT] Providers: {len(providers)}")
        
        if len(list(registry.algorithms())) == 0:
            print("[INIT] Agregando QgsNativeAlgorithms...")
            registry.addProvider(QgsNativeAlgorithms())
            print(f"[INIT] Algoritmos disponibles: {len(list(registry.algorithms()))}")
        
        # Crear ventana
        print("[INIT] Creando ventana...")
        viewer = QgsViewerPOC()
        viewer.show()
        
        # Recargar algoritmos en el dock (por si acaso)
        print("[INIT] Recargando algoritmos en DockWidget...")
        if viewer.processing_dock:
            viewer.processing_dock.load_algorithms()
        
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
