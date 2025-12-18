#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DOCK WIDGET PARA EJECUTAR MODELOS DE PROCESOS QGIS
(Procesos pregrabados/diseñados en QGIS)

No construye cadenas, sino que ejecuta modelos ya guardados.
"""

import sys
import os
from typing import List, Dict, Any

from qgis.core import (
    QgsApplication, QgsProject, QgsProcessing,
    QgsProcessingContext, QgsProcessingFeedback,
)
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton, QProgressBar,
    QScrollArea, QFrame, QSpinBox, QDoubleSpinBox,
    QLineEdit, QMessageBox, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QCheckBox
)
from qgis.PyQt.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize
)
from qgis.PyQt.QtGui import QFont, QColor, QIcon


class ProcessModelExecutorThread(QThread):
    """Thread para ejecutar modelos de procesos sin bloquear UI"""
    
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    
    def __init__(self, model_id: str, parameters: Dict[str, Any], model_file_path: str = None):
        super().__init__()
        self.model_id = model_id
        self.parameters = parameters
        self.model_file_path = model_file_path
    
    def run(self):
        """Ejecutar el modelo en thread secundario"""
        try:
            registry = QgsApplication.processingRegistry()
            algorithm = registry.algorithmById(self.model_id)
            
            if not algorithm:
                # Si no está en registry, intentar cargar desde archivo
                if self.model_file_path and os.path.exists(self.model_file_path):
                    self.message.emit(f"Modelo no en registry, intentando cargar desde archivo...")
                    algorithm = self._load_model_from_file()
                    if not algorithm:
                        self.error.emit(f"Modelo no encontrado en registry ni en archivo: {self.model_id}")
                        self.finished.emit(False)
                        return
                else:
                    self.error.emit(f"Modelo no encontrado: {self.model_id}")
                    self.finished.emit(False)
                    return
            
            # Preparar contexto y feedback
            context = QgsProcessingContext()
            context.setProject(QgsProject.instance())
            
            feedback = QgsProcessingFeedback()
            feedback.progressChanged.connect(self.on_progress)
            
            display_name = algorithm.displayName() if hasattr(algorithm, 'displayName') else self.model_id
            self.message.emit(f"Ejecutando: {display_name}...")
            
            # Log de parámetros esperados vs. pasados
            debug_log = []
            debug_log.append(f"\nParámetros esperados por el algoritmo:")
            for param in algorithm.parameterDefinitions():
                debug_log.append(f"  • {param.name()} ({param.type()}): {param.description()}")
            
            debug_log.append(f"\nParámetros que estamos pasando:")
            for name, value in self.parameters.items():
                debug_log.append(f"  • {name} = {value} (tipo: {type(value).__name__})")
            
            debug_text = "\n".join(debug_log)
            self.message.emit(debug_text)
            
            # Escribir a archivo también
            with open(r"C:\Users\de1703\Desktop\debug_algoritmo.txt", "w") as f:
                f.write(debug_text)
            
            # Ejecutar modelo
            self.message.emit(f"\nEjecutando algoritmo...")
            result = algorithm.run(self.parameters, context, feedback)
            
            self.message.emit(f"Resultado completo: {result}")
            self.message.emit(f"Tipo resultado: {type(result)}, Longitud: {len(result) if isinstance(result, (tuple, list)) else 'N/A'}")
            
            # Log cada elemento del resultado
            result_log = []
            if isinstance(result, (tuple, list)):
                for i, item in enumerate(result):
                    msg = f"  result[{i}] = {item} (tipo: {type(item).__name__})"
                    self.message.emit(msg)
                    result_log.append(msg)
            
            # Escribir resultado a archivo
            with open(r"C:\Users\de1703\Desktop\debug_resultado.txt", "w") as f:
                f.write(f"Resultado: {result}\n")
                f.write(f"Tipo: {type(result)}\n")
                f.write("\n".join(result_log))
            
            if result[0]:  # True si éxito
                self.message.emit(f"✓ Modelo completado: {display_name}")
                self.progress.emit(100)
                self.finished.emit(True)
            else:
                # El algoritmo falló - el resultado es (False, algo, algo)
                error_message = "Algoritmo falló"
                
                # Intentar extraer información útil
                if isinstance(result, (tuple, list)) and len(result) > 1:
                    # Típicamente: (False, outputs_dict, None) o (False, error_string, None)
                    second_item = result[1]
                    
                    if isinstance(second_item, dict):
                        # Es un diccionario de outputs - probablemente está vacío o invalido
                        error_message = f"Outputs vacíos o inválidos: {second_item}"
                    elif isinstance(second_item, str):
                        error_message = second_item if second_item else "Sin mensaje de error"
                    elif second_item is None:
                        # Buscar en item [2] o posterior
                        if len(result) > 2:
                            error_message = f"Error en posición 2: {result[2]}"
                        else:
                            error_message = "Algoritmo falló sin detalles de error"
                    else:
                        error_message = f"Error (tipo {type(second_item).__name__}): {second_item}"
                else:
                    error_message = f"Formato de resultado inesperado: {result}"
                
                self.message.emit(f"Detalles: {error_message}")
                self.error.emit(f"El algoritmo retornó error: {error_message}")
                self.finished.emit(False)
                
        except Exception as e:
            error_detail = str(e)
            import traceback
            tb = traceback.format_exc()
            self.message.emit(f"Excepción: {error_detail}")
            self.message.emit(f"Traceback:\n{tb}")
            self.error.emit(f"Error ejecutando modelo: {error_detail}\n\n{tb}")
            self.finished.emit(False)
    
    def _load_model_from_file(self):
        """Intentar cargar modelo desde archivo XML o JSON"""
        import os
        import xml.etree.ElementTree as ET
        import json
        
        try:
            if not os.path.exists(self.model_file_path):
                self.message.emit(f"Archivo no existe: {self.model_file_path}")
                return None
            
            self.message.emit(f"Cargando modelo desde archivo: {os.path.basename(self.model_file_path)}")
            
            with open(self.model_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            registry = QgsApplication.processingRegistry()
            
            # Detectar y parsear formato
            if content.startswith('<!DOCTYPE') or content.startswith('<Option'):
                # XML format (antiguo)
                try:
                    root = ET.fromstring(content)
                    
                    # Buscar primer algoritmo en los pasos
                    children = root.find(".//Option[@name='children']")
                    if children is not None and len(children) > 0:
                        # Obtener el primer (o único) paso del modelo
                        first_child = children[0]
                        algo_id_elem = first_child.find(".//Option[@name='alg_id'][@type='QString']")
                        
                        if algo_id_elem is not None:
                            algo_id = algo_id_elem.get('value')
                            self.message.emit(f"Modelo XML contiene algoritmo: {algo_id}")
                            
                            # Buscar el algoritmo en el registry
                            algorithm = registry.algorithmById(algo_id)
                            if algorithm:
                                self.message.emit(f"✓ Algoritmo encontrado: {algorithm.displayName()}")
                                return algorithm
                            else:
                                self.message.emit(f"✗ Algoritmo no encontrado en registry: {algo_id}")
                                return None
                
                except Exception as e:
                    self.message.emit(f"Error parseando XML: {str(e)}")
                    return None
                    
            elif content.startswith('{'):
                # JSON format (nuevo)
                try:
                    model_data = json.loads(content)
                    steps = model_data.get('steps', [])
                    
                    if steps:
                        # Obtener primer paso
                        algo_id = steps[0].get('algorithm')
                        if algo_id:
                            self.message.emit(f"Modelo JSON contiene algoritmo: {algo_id}")
                            
                            # Buscar el algoritmo en el registry
                            algorithm = registry.algorithmById(algo_id)
                            if algorithm:
                                self.message.emit(f"✓ Algoritmo encontrado: {algorithm.displayName()}")
                                return algorithm
                            else:
                                self.message.emit(f"✗ Algoritmo no encontrado en registry: {algo_id}")
                                return None
                
                except Exception as e:
                    self.message.emit(f"Error parseando JSON: {str(e)}")
                    return None
            
            return None
            
        except Exception as e:
            self.message.emit(f"Error cargando modelo desde archivo: {str(e)}")
            return None
    
    def on_progress(self, value):
        """Callback de progreso"""
        self.progress.emit(int(value))


class ModelParameterWidget(QFrame):
    """Widget dinámico para parámetro de modelo"""
    
    def __init__(self, param_definition):
        super().__init__()
        self.param_definition = param_definition
        
        layout = QHBoxLayout(self)
        
        # Label con nombre del parámetro
        label = QLabel(param_definition.description())
        label.setMinimumWidth(150)
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
        elif param_type == 'boolean':
            self.widget = QCheckBox()
        else:
            self.widget = QLineEdit()
        
        layout.addWidget(self.widget, 1)
        self.setLayout(layout)
    
    def _create_layer_combo(self) -> QComboBox:
        """Crear combobox con capas del proyecto"""
        combo = QComboBox()
        combo.addItem("(Seleccionar)", "")
        
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
        elif isinstance(self.widget, QCheckBox):
            return self.widget.isChecked()
        else:
            return self.widget.text()


class ProcessModelsDock(QDockWidget):
    """DockWidget para ejecutar modelos de procesos pregrabados"""
    
    status_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Modelos de Procesos", parent)
        self.parent = parent
        self.executor_thread = None
        self.parameter_widgets = {}
        
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)
        
        self.init_ui()
        self.load_models()
    
    def init_ui(self):
        """Inicializar interfaz"""
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # ===== SELECTOR DE MODELO =====
        models_label = QLabel("1. Seleccionar modelo/proceso:")
        layout.addWidget(models_label)
        
        models_combo_layout = QHBoxLayout()
        
        self.combo_models = QComboBox()
        self.combo_models.currentIndexChanged.connect(self.on_model_changed)
        models_combo_layout.addWidget(self.combo_models, 1)
        
        btn_reload_models = QPushButton("🔄")
        btn_reload_models.setMaximumWidth(40)
        btn_reload_models.setToolTip("Recargar modelos")
        btn_reload_models.clicked.connect(self.load_models)
        models_combo_layout.addWidget(btn_reload_models)
        
        layout.addLayout(models_combo_layout)
        
        # ===== DESCRIPCIÓN DEL MODELO =====
        self.model_description = QLabel("")
        self.model_description.setWordWrap(True)
        self.model_description.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.model_description)
        
        # ===== PARÁMETROS =====
        layout.addWidget(QLabel("2. Parámetros:"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.param_frame = QFrame()
        self.param_layout = QVBoxLayout(self.param_frame)
        scroll.setWidget(self.param_frame)
        layout.addWidget(scroll)
        
        # ===== BOTÓN EJECUTAR =====
        btn_execute = QPushButton("▶ EJECUTAR MODELO")
        btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        btn_execute.clicked.connect(self.execute_model)
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
    
    def load_models(self):
        """Cargar modelos de procesos disponibles"""
        try:
            import os
            from pathlib import Path
            import json
            
            self.combo_models.clear()
            
            registry = QgsApplication.processingRegistry()
            
            # Obtener TODOS los algoritmos (incluyendo modelos)
            all_algorithms = list(registry.algorithms())
            
            # Filtrar para obtener solo modelos
            model_items = []
            model_ids_added = set()  # Para evitar duplicados
            
            # 1. Primero: Buscar modelos en registry
            for algo in all_algorithms:
                algo_id = algo.id()
                display_name = algo.displayName()
                
                try:
                    provider = algo.provider()
                    provider_id = str(provider.id()).lower() if provider else ""
                    
                    # Es modelo si:
                    # - Provider es "model"
                    # - O el ID contiene "model"
                    if "model" in provider_id or "model" in algo_id.lower():
                        if algo_id not in model_ids_added:
                            model_items.append((display_name, algo_id, algo))
                            model_ids_added.add(algo_id)
                except:
                    pass
            
            # 2. Segundo: Buscar ficheros .model3 y .qgxml directamente en carpeta
            models_dir = Path(os.getenv('APPDATA')) / "QGIS" / "QGIS3" / "profiles" / "default" / "processing" / "models"
            
            if models_dir.exists():
                # Buscar .model3 (pueden ser JSON nuevo o XML antiguo - QGIS tiene un bug)
                for model_file in models_dir.glob("*.model3"):
                    try:
                        import xml.etree.ElementTree as ET
                        
                        with open(model_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        model_name = None
                        
                        # Detectar formato: JSON o XML
                        if content.startswith('{'):
                            # JSON format (nuevo)
                            model_data = json.load(open(model_file, 'r', encoding='utf-8'))
                            model_name = model_data.get("name", model_file.stem)
                        
                        elif content.startswith('<!DOCTYPE') or content.startswith('<Option'):
                            # XML format (antiguo, bug de QGIS guardando con extension .model3)
                            try:
                                root = ET.fromstring(content)
                                # Buscar 'model_name' primero, luego 'name'
                                name_elem = root.find(".//Option[@name='model_name'][@type='QString']")
                                if name_elem is None:
                                    name_elem = root.find(".//Option[@name='name'][@type='QString']")
                                if name_elem is not None:
                                    model_name = name_elem.get('value', model_file.stem)
                                else:
                                    model_name = model_file.stem
                            except:
                                model_name = model_file.stem
                        
                        if model_name:
                            model_id = f"model:{model_file.stem}"
                            
                            if model_id not in model_ids_added:
                                algo = registry.algorithmById(model_id)
                                if algo:
                                    model_items.append((model_name, model_id, algo, str(model_file)))
                                    model_ids_added.add(model_id)
                                else:
                                    # Crear entrada aunque no esté en registry, guardando ruta del archivo
                                    model_items.append((model_name, model_id, None, str(model_file)))
                                    model_ids_added.add(model_id)
                    
                    except Exception as e:
                        print(f"DEBUG: Error leyendo {model_file.name}: {e}")
                
                # Buscar .qgxml (formato antiguo, por compatibilidad)
                for qgxml_file in models_dir.glob("*.qgxml"):
                    try:
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(qgxml_file)
                        root = tree.getroot()
                        
                        # Buscar elemento <name>
                        name_elem = root.find(".//name")
                        if name_elem is not None:
                            model_name = name_elem.text
                            model_id = f"model:{qgxml_file.stem}"
                            
                            # Solo agregar si no está ya
                            if model_id not in model_ids_added:
                                algo = registry.algorithmById(model_id)
                                if algo:
                                    model_items.append((model_name, model_id, algo, str(qgxml_file)))
                                    model_ids_added.add(model_id)
                                    print(f"DEBUG: Modelo .qgxml cargado del registry: {model_name}")
                                else:
                                    # Guardar con ruta del archivo
                                    model_items.append((model_name, model_id, None, str(qgxml_file)))
                                    model_ids_added.add(model_id)
                    except Exception as e:
                        print(f"DEBUG: Error leyendo {qgxml_file.name}: {e}")
            
            # Si no encontramos modelos, mostrar todos los algoritmos
            if len(model_items) == 0:
                self.status_label.setText("ℹ No hay modelos. Mostrando todos los algoritmos...")
                self.status_label.setStyleSheet("color: orange;")
                
                for algo in sorted(all_algorithms, key=lambda a: a.displayName()):
                    model_items.append((algo.displayName(), algo.id(), algo, None))  # None = no file path
            
            # Ordenar por nombre
            model_items.sort(key=lambda x: x[0])
            
            # Agregar al combo
            for item_tuple in model_items:
                display_name = item_tuple[0]
                model_id = item_tuple[1]
                algo_obj = item_tuple[2]
                file_path = item_tuple[3] if len(item_tuple) > 3 else None
                # Si algo_obj es None (modelo no en registry), aún así añadirlo
                if algo_obj is not None:
                    self.combo_models.addItem(display_name, (model_id, algo_obj, file_path))
                else:
                    # Placeholder para modelos que no están en registry
                    self.combo_models.addItem(f"{display_name} (?)", (model_id, None, file_path))
            
            count = len(model_items)
            self.status_label.setText(f"✓ {count} modelos disponibles")
            self.status_label.setStyleSheet("color: green;")
            self.status_changed.emit(f"Cargados {count} modelos")
            
        except Exception as e:
            self.status_label.setText(f"✗ Error cargando modelos: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            print(f"DEBUG: Exception en load_models: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_algorithm_from_model_file(self, file_path: str):
        """Cargar algoritmo base desde archivo .model3 o .qgxml"""
        import xml.etree.ElementTree as ET
        import json
        
        try:
            if not os.path.exists(file_path):
                print(f"DEBUG: Archivo no existe: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            registry = QgsApplication.processingRegistry()
            algo_id = None
            
            # Detectar y parsear formato
            if content.startswith('<!DOCTYPE') or content.startswith('<Option'):
                # XML format
                try:
                    root = ET.fromstring(content)
                    
                    # Buscar primer algoritmo en los pasos
                    children = root.find(".//Option[@name='children']")
                    if children is not None and len(children) > 0:
                        first_child = children[0]
                        algo_id_elem = first_child.find(".//Option[@name='alg_id'][@type='QString']")
                        
                        if algo_id_elem is not None:
                            algo_id = algo_id_elem.get('value')
                            print(f"DEBUG: Modelo XML contiene algoritmo: {algo_id}")
                
                except Exception as e:
                    print(f"DEBUG: Error parseando XML: {str(e)}")
                    return None
                    
            elif content.startswith('{'):
                # JSON format
                try:
                    model_data = json.loads(content)
                    steps = model_data.get('steps', [])
                    
                    if steps:
                        algo_id = steps[0].get('algorithm')
                        print(f"DEBUG: Modelo JSON contiene algoritmo: {algo_id}")
                
                except Exception as e:
                    print(f"DEBUG: Error parseando JSON: {str(e)}")
                    return None
            
            # Si encontramos el ID del algoritmo, buscarlo en registry
            if algo_id:
                algorithm = registry.algorithmById(algo_id)
                if algorithm:
                    print(f"DEBUG: ✓ Algoritmo encontrado: {algorithm.displayName()}")
                    return algorithm
                else:
                    print(f"DEBUG: ✗ Algoritmo no encontrado en registry: {algo_id}")
            
            return None
        
        except Exception as e:
            print(f"DEBUG: Error en _load_algorithm_from_model_file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def on_model_changed(self):
        """Actualizar parámetros cuando cambia modelo"""
        
        # Limpiar parámetros anteriores
        while self.param_layout.count():
            item = self.param_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.parameter_widgets = {}
        
        model_data = self.combo_models.currentData()
        
        if not model_data:
            return
        
        try:
            # model_data puede tener 2 o 3 elementos (model_id, algo_obj, file_path)
            model_id = model_data[0]
            algo_obj = model_data[1]
            file_path = model_data[2] if len(model_data) > 2 else None
            
            print(f"DEBUG on_model_changed: model_id={model_id}, algo_obj={algo_obj}, file_path={file_path}")
            
            if not algo_obj:
                # Si algo_obj es None, intentar cargar desde archivo
                if file_path and os.path.exists(file_path):
                    print(f"DEBUG: Cargando algoritmo desde archivo: {file_path}")
                    algo_obj = self._load_algorithm_from_model_file(file_path)
                    if not algo_obj:
                        print(f"DEBUG: No se pudo cargar el algoritmo desde archivo")
                        self.model_description.setText("No se pudo cargar el modelo desde archivo")
                        return
                else:
                    print(f"DEBUG: No hay file_path o archivo no existe")
                    self.model_description.setText("No se puede cargar el modelo")
                    return
            
            # Mostrar descripción
            description = algo_obj.shortDescription() or algo_obj.displayName()
            self.model_description.setText(description)
            
            print(f"DEBUG: Parámetros disponibles:")
            # Crear widgets para parámetros
            for param in algo_obj.parameterDefinitions():
                print(f"  - {param.name()}: flags={param.flags()}")
                # Ignorar parámetros ocultos u opcionales especiales
                if param.flags() & 4:  # FlagHidden
                    print(f"    -> IGNORADO (oculto)")
                    continue
                
                try:
                    param_widget = ModelParameterWidget(param)
                    self.parameter_widgets[param.name()] = param_widget
                    self.param_layout.addWidget(param_widget)
                    print(f"    -> Widget creado")
                except Exception as e:
                    print(f"    -> Error creando widget: {e}")
            
            print(f"DEBUG: Total widgets creados: {len(self.parameter_widgets)}")
            self.param_layout.addStretch()
            
        except Exception as e:
            print(f"Error en on_model_changed: {e}")
            import traceback
            traceback.print_exc()
    
    def execute_model(self):
        """Ejecutar modelo seleccionado"""
        
        model_data = self.combo_models.currentData()
        
        if not model_data:
            QMessageBox.warning(self, "Error", "Selecciona un modelo")
            return
        
        if self.executor_thread and self.executor_thread.isRunning():
            QMessageBox.warning(self, "Error", "Ya hay una ejecución en curso")
            return
        
        try:
            # model_data puede tener 2 o 3 elementos (model_id, algo_obj, file_path)
            model_id = model_data[0]
            algo_obj = model_data[1]
            file_path = model_data[2] if len(model_data) > 2 else None
            
            print(f"DEBUG execute_model: Total widgets disponibles: {len(self.parameter_widgets)}")
            
            # Recopilar parámetros
            parameters = {}
            for param_name, param_widget in self.parameter_widgets.items():
                value = param_widget.get_value()
                parameters[param_name] = value
                print(f"DEBUG: Parámetro {param_name} = {value} (tipo: {type(value)})")
            
            print(f"DEBUG: Total parámetros recopilados: {len(parameters)}")
            
            # Mostrar progreso
            self.progress.setVisible(True)
            self.progress.setValue(0)
            self.status_label.setText("Ejecutando...")
            self.status_label.setStyleSheet("color: orange;")
            
            # Crear y conectar thread (pasando file_path)
            self.executor_thread = ProcessModelExecutorThread(model_id, parameters, file_path)
            self.executor_thread.progress.connect(self.on_progress)
            self.executor_thread.message.connect(self.on_message)
            self.executor_thread.finished.connect(self.on_finished)
            self.executor_thread.error.connect(self.on_error)
            
            # Iniciar
            self.executor_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error preparando ejecución:\n{str(e)}")
    
    def on_progress(self, value):
        """Actualizar barra de progreso"""
        self.progress.setValue(value)
    
    def on_message(self, message):
        """Mostrar mensaje de estado"""
        self.status_label.setText(message)
        self.status_changed.emit(message)
    
    def on_error(self, error):
        """Error durante ejecución"""
        # Truncar para display corto
        error_short = error.split('\n')[0][:100]
        self.status_label.setText(f"❌ Error: {error_short}")
        self.status_label.setStyleSheet("color: red;")
        self.status_changed.emit(f"Error: {error}")
        
        # Mostrar dialog con error completo
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error ejecutando modelo")
        msg_box.setText("Hubo un error al ejecutar el modelo:")
        msg_box.setDetailedText(error)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def on_finished(self, success):
        """Modelo completado"""
        self.progress.setVisible(False)
        
        if success:
            self.status_label.setText("✓ Modelo completado exitosamente")
            self.status_label.setStyleSheet("color: green;")
            QMessageBox.information(self, "Éxito", "Modelo ejecutado exitosamente")
        else:
            self.status_label.setText("❌ Modelo falló")
            self.status_label.setStyleSheet("color: red;")
    
    def update_layers(self):
        """Actualizar capas disponibles cuando cambia proyecto"""
        self.on_model_changed()


if __name__ == "__main__":
    print("Este módulo debe importarse desde qgs_viewer_poc.py")
