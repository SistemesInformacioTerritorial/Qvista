#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DOCKWIDGET DE PROCESOS MÍNIMO
Proof of Concept para ProcessingChain en qVista

Características:
  - Carga algoritmos QGIS disponibles
  - Panel dinámico de parámetros
  - Ejecución en thread
  - Barra de progreso
  - Manejo básico de errores
"""

import sys
from typing import List, Dict, Any

from qgis.core import (
    QgsApplication, QgsProject, QgsProcessing,
    QgsProcessingContext, QgsProcessingFeedback,
    QgsVectorLayer, QgsRasterLayer
)
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton, QProgressBar,
    QScrollArea, QFrame, QSpinBox, QDoubleSpinBox,
    QLineEdit, QMessageBox, QListWidget, QListWidgetItem,
    QCheckBox
)
from qgis.PyQt.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize
)
from qgis.PyQt.QtGui import QFont, QColor, QTextCursor


class ProcessingStep:
    """Representa un paso en la cadena de procesos"""
    
    def __init__(self, algorithm_id: str, parameters: Dict[str, Any]):
        self.algorithm_id = algorithm_id
        self.parameters = parameters
        self.result = None
        self.error = None
    
    def execute(self, context: QgsProcessingContext, feedback: QgsProcessingFeedback) -> bool:
        """Ejecutar este paso"""
        try:
            registry = QgsApplication.processingRegistry()
            algorithm = registry.algorithmById(self.algorithm_id)
            
            if not algorithm:
                self.error = f"Algoritmo no encontrado: {self.algorithm_id}"
                return False
            
            # Reemplazar referencias a pasos anteriores
            params = self._replace_references(self.parameters)
            
            result = algorithm.run(params, context, feedback)
            
            if result[0]:  # True si éxito
                self.result = result[1]
                return True
            else:
                self.error = "El algoritmo retornó False"
                return False
                
        except Exception as e:
            self.error = str(e)
            return False
    
    def _replace_references(self, params: Dict) -> Dict:
        """Reemplazar referencias a salidas anteriores"""
        # TODO: Implementar lógica de referencias
        return params


class ProcessingExecutorThread(QThread):
    """Thread para ejecutar procesos sin bloquear UI"""
    
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool)  # True si éxito
    error = pyqtSignal(str)
    
    def __init__(self, steps: List[ProcessingStep]):
        super().__init__()
        self.steps = steps
        self.context = QgsProcessingContext()
        self.context.setProject(QgsProject.instance())
    
    def run(self):
        """Ejecutar todos los pasos"""
        feedback = QgsProcessingFeedback()
        feedback.progressChanged.connect(self.on_progress)
        
        try:
            for i, step in enumerate(self.steps):
                self.message.emit(f"Ejecutando: {step.algorithm_id}")
                
                success = step.execute(self.context, feedback)
                
                if not success:
                    self.error.emit(f"Error en paso {i+1}: {step.error}")
                    self.finished.emit(False)
                    return
                
                progress = int((i + 1) / len(self.steps) * 100)
                self.progress.emit(progress)
            
            self.message.emit("✓ Cadena completada exitosamente")
            self.finished.emit(True)
            
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False)
    
    def on_progress(self, value):
        """Feedback de progreso"""
        self.progress.emit(value)


class ParameterWidget(QFrame):
    """Widget dinámico para parámetros de algoritmo"""
    
    def __init__(self, param_definition):
        super().__init__()
        self.param = param_definition
        self.widget = None
        
        layout = QHBoxLayout(self)
        
        # Label del parámetro
        label = QLabel(param_definition.description())
        label.setMaximumWidth(200)
        layout.addWidget(label)
        
        # Widget según tipo
        param_type = param_definition.type()
        
        if param_type == 'raster' or param_type == 'vector':
            self.widget = self._create_layer_combo()
        elif param_type == 'number':
            self.widget = QSpinBox()
            self.widget.setRange(-999999, 999999)
        elif param_type == 'distance':
            self.widget = QDoubleSpinBox()
            self.widget.setValue(100)
        else:
            self.widget = QLineEdit()
        
        layout.addWidget(self.widget, 1)
        self.setLayout(layout)
    
    def _create_layer_combo(self) -> QComboBox:
        """Crear combobox con capas del proyecto"""
        combo = QComboBox()
        
        for capa in QgsProject.instance().mapLayers().values():
            combo.addItem(capa.name(), capa.id())
        
        return combo
    
    def get_value(self):
        """Obtener valor del parámetro"""
        if isinstance(self.widget, QComboBox):
            return self.widget.currentData()
        elif isinstance(self.widget, QSpinBox):
            return self.widget.value()
        elif isinstance(self.widget, QDoubleSpinBox):
            return self.widget.value()
        else:
            return self.widget.text()


class ProcessingChainDock(QDockWidget):
    """DockWidget para encadenamiento de procesos QGIS"""
    
    status_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Procesos QGIS", parent)
        self.parent = parent
        self.steps = []
        self.executor_thread = None
        self.parameter_widgets = {}
        
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)
        
        self.init_ui()
        self.load_algorithms()
    
    def init_ui(self):
        """Inicializar interfaz"""
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # ===== SELECTOR DE ALGORITMO =====
        algo_label = QLabel("1. Seleccionar algoritmo:")
        layout.addWidget(algo_label)
        
        algo_combo_layout = QHBoxLayout()
        
        self.combo_algorithms = QComboBox()
        self.combo_algorithms.currentIndexChanged.connect(self.on_algorithm_changed)
        algo_combo_layout.addWidget(self.combo_algorithms, 1)
        
        btn_reload = QPushButton("🔄")
        btn_reload.setMaximumWidth(40)
        btn_reload.setToolTip("Recargar algoritmos")
        btn_reload.clicked.connect(self.load_algorithms)
        algo_combo_layout.addWidget(btn_reload)
        
        layout.addLayout(algo_combo_layout)
        
        # ===== PARÁMETROS =====
        layout.addWidget(QLabel("2. Parámetros:"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.param_frame = QFrame()
        self.param_layout = QVBoxLayout(self.param_frame)
        scroll.setWidget(self.param_frame)
        layout.addWidget(scroll)
        
        # ===== BOTONES DE PASOS =====
        button_layout = QHBoxLayout()
        
        btn_add = QPushButton("➕ Añadir paso")
        btn_add.clicked.connect(self.add_step)
        button_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("➖ Quitar paso")
        btn_remove.clicked.connect(self.remove_step)
        button_layout.addWidget(btn_remove)
        
        layout.addLayout(button_layout)
        
        # ===== LISTA DE PASOS =====
        layout.addWidget(QLabel("3. Cadena de procesos:"))
        
        self.steps_list = QListWidget()
        self.steps_list.itemSelectionChanged.connect(self.on_step_selected)
        layout.addWidget(self.steps_list)
        
        # ===== BOTÓN EJECUTAR =====
        btn_execute = QPushButton("▶ EJECUTAR CADENA")
        btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        btn_execute.clicked.connect(self.execute_chain)
        layout.addWidget(btn_execute)
        
        # ===== PROGRESO =====
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # ===== ESTADO =====
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        main_widget.setLayout(layout)
        self.setWidget(main_widget)
    
    def load_algorithms(self):
        """Cargar algoritmos disponibles"""
        try:
            # Limpiar combo anterior
            self.combo_algorithms.clear()
            
            # Importar Processing para inicializarlo
            from qgis.analysis import QgsNativeAlgorithms
            
            # Obtener registry
            registry = QgsApplication.processingRegistry()
            
            # Si el registry está vacío o sin providers, inicializar
            providers = registry.providers()
            print(f"DEBUG: Providers actuales: {len(providers)}")
            
            algorithms = list(registry.algorithms())
            print(f"DEBUG: Algoritmos encontrados: {len(algorithms)}")
            
            if len(algorithms) == 0:
                # Intentar agregar algoritmos nativos
                print("DEBUG: Agregando QgsNativeAlgorithms...")
                try:
                    native = QgsNativeAlgorithms()
                    registry.addProvider(native)
                    algorithms = list(registry.algorithms())
                    print(f"DEBUG: Ahora hay {len(algorithms)} algoritmos")
                except Exception as e:
                    print(f"DEBUG: Error agregando nativos: {e}")
            
            if len(algorithms) == 0:
                self.status_label.setText("⚠ No se encontraron algoritmos. Verifica la instalación de QGIS.")
                self.status_label.setStyleSheet("color: orange;")
                return
            
            algo_names = []
            for algo in algorithms:
                try:
                    algo_names.append((algo.displayName(), algo.id()))
                except:
                    pass
            
            # Ordenar por nombre
            algo_names.sort(key=lambda x: x[0])
            
            # Agregar al combo
            for display_name, algo_id in algo_names:
                self.combo_algorithms.addItem(display_name, algo_id)
            
            self.status_changed.emit(f"Cargados {len(algo_names)} algoritmos")
            self.status_label.setText(f"✓ {len(algo_names)} algoritmos disponibles")
            self.status_label.setStyleSheet("color: green;")
            
        except Exception as e:
            self.status_label.setText(f"✗ Error cargando algoritmos: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            self.status_changed.emit(f"Error cargando algoritmos: {str(e)}")
            print(f"DEBUG: Exception en load_algorithms: {e}")
            import traceback
            traceback.print_exc()
    
    def on_algorithm_changed(self):
        """Actualizar parámetros cuando cambia algoritmo"""
        algo_id = self.combo_algorithms.currentData()
        
        if not algo_id:
            return
        
        try:
            registry = QgsApplication.processingRegistry()
            algorithm = registry.algorithmById(algo_id)
            
            if not algorithm:
                return
            
            # Limpiar widgets anteriores
            while self.param_layout.count():
                item = self.param_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            self.parameter_widgets = {}
            
            # Crear widgets para cada parámetro
            for param in algorithm.parameterDefinitions():
                # Ignorar parámetros ocultos
                if param.flags() & 4:  # FlagHidden
                    continue
                
                try:
                    param_widget = ParameterWidget(param)
                    self.parameter_widgets[param.name()] = param_widget
                    self.param_layout.addWidget(param_widget)
                except:
                    pass
            
            spacer = self.param_layout.addStretch()
            
        except Exception as e:
            print(f"Error: {e}")
    
    def add_step(self):
        """Añadir paso a la cadena"""
        algo_id = self.combo_algorithms.currentData()
        algo_name = self.combo_algorithms.currentText()
        
        if not algo_id:
            QMessageBox.warning(self, "Error", "Selecciona un algoritmo")
            return
        
        # Recopilar parámetros
        parameters = {}
        for param_name, param_widget in self.parameter_widgets.items():
            parameters[param_name] = param_widget.get_value()
        
        # Crear paso
        step = ProcessingStep(algo_id, parameters)
        self.steps.append(step)
        
        # Añadir a lista visual
        item = QListWidgetItem(f"#{len(self.steps)} - {algo_name}")
        self.steps_list.addItem(item)
        
        self.status_changed.emit(f"Paso añadido: {algo_name}")
    
    def remove_step(self):
        """Quitar paso seleccionado"""
        current_row = self.steps_list.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un paso para eliminar")
            return
        
        self.steps.pop(current_row)
        self.steps_list.takeItem(current_row)
        
        self.status_changed.emit(f"Paso {current_row + 1} eliminado")
    
    def on_step_selected(self):
        """Cuando se selecciona un paso (para futuras características)"""
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            step = self.steps[current_row]
            self.status_changed.emit(f"Paso seleccionado: {step.algorithm_id}")
    
    def execute_chain(self):
        """Ejecutar la cadena de procesos"""
        
        if not self.steps:
            QMessageBox.warning(self, "Error", "La cadena está vacía")
            return
        
        if self.executor_thread and self.executor_thread.isRunning():
            QMessageBox.warning(self, "Error", "Ya hay una ejecución en curso")
            return
        
        # Mostrar progreso
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText("Ejecutando...")
        self.status_label.setStyleSheet("color: orange;")
        
        # Crear y conectar thread
        self.executor_thread = ProcessingExecutorThread(self.steps)
        self.executor_thread.progress.connect(self.on_progress)
        self.executor_thread.message.connect(self.on_message)
        self.executor_thread.finished.connect(self.on_finished)
        self.executor_thread.error.connect(self.on_error)
        
        # Iniciar
        self.executor_thread.start()
    
    def on_progress(self, value):
        """Actualizar progreso"""
        self.progress.setValue(value)
    
    def on_message(self, message):
        """Mostrar mensaje"""
        self.status_label.setText(message)
        self.status_changed.emit(message)
    
    def on_error(self, error):
        """Error en ejecución"""
        self.status_label.setText(f"❌ Error: {error}")
        self.status_label.setStyleSheet("color: red;")
        self.status_changed.emit(f"Error: {error}")
        QMessageBox.critical(self, "Error en proceso", error)
    
    def on_finished(self, success):
        """Ejecución completada"""
        self.progress.setVisible(False)
        
        if success:
            self.status_label.setText("✓ Cadena completada")
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, "Éxito", "Cadena ejecutada exitosamente")
        else:
            self.status_label.setText("❌ Cadena fallida")
            self.status_label.setStyleSheet("color: red;")
    
    def update_layers(self):
        """Actualizar lista de capas cuando cambia proyecto"""
        # Reconstruir combos de capas en los parámetros
        self.on_algorithm_changed()


if __name__ == "__main__":
    # Test standalone (no recomendado, usar desde qgs_viewer_poc.py)
    print("Este módulo debe importarse desde qgs_viewer_poc.py")
