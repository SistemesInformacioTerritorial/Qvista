"""
Botonera genérica que lee configuración desde un fichero JSON
y crea secciones colapsables con botones dinámicamente.

El fichero JSON debe estar en la misma carpeta que el proyecto QGIS
y tener el mismo nombre (ej: proyecto.json para proyecto.qgs)
"""

import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import (QDockWidget, QFrame, QSizePolicy,
                                 QSpacerItem, QVBoxLayout, QPushButton,
                                 QWidget, QMessageBox)
from qgis.core import QgsProject

from moduls.QvPushButton import QvPushButton

# Configurar logging
logger = logging.getLogger(__name__)


class QQueryFileLoader:
    """Lee y parsea archivos de query QGIS (.qqf)"""
    
    @staticmethod
    def read_filter_expression(query_file: Path) -> Optional[str]:
        """
        Lee un fichero .qqf (formato estándar de QGIS) y extrae la expresión de filtro.
        
        Formato estándar de QGIS:
        <Query>expresión de filtro aquí</Query>
        
        Ejemplo:
        <Query>"M1_DISTRICTE" = '03' OR "M3_NUM_PROP_PRIVATS" = 5</Query>
        
        Args:
            query_file: Ruta al fichero .qqf
            
        Returns:
            String con la expresión del filtro, o None si no se puede leer
        """
        if not query_file.exists():
            logger.error(f"Fichero de query no encontrado: {query_file}")
            return None
        
        try:
            content = query_file.read_text(encoding='utf-8').strip()
            
            if not content:
                logger.error(f"Fichero {query_file.name} está vacío")
                return None
            
            # Parsear XML y extraer expresión del elemento <Query>
            root = ET.fromstring(content)
            
            if root.tag == 'Query' and root.text:
                expression = root.text.strip()
                logger.info(f"Expresión extraída de {query_file.name}: {expression[:80]}...")
                return expression
            
            logger.error(f"Formato de .qqf inválido: no se encontró elemento <Query> en {query_file.name}")
            return None
                
        except ET.ParseError as e:
            logger.error(f"Error parseando XML en {query_file.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error leyendo {query_file.name}: {e}")
            return None


class CollapsibleSection(QWidget):
    """Widget colapsable para agrupar botones en secciones"""
    
    def __init__(self, title: str, collapsed: bool = True):
        """
        Args:
            title: Título de la sección
            collapsed: Si True, la sección empieza contraída
        """
        super().__init__()
        self.title = title
        self.is_expanded = not collapsed
        
        # Botón para expandir/contraer
        arrow = "▼" if self.is_expanded else "▶"
        self.toggle_btn = QPushButton(f"{arrow} {title}")
        self.toggle_btn.setFlat(True)
        self.toggle_btn.setStyleSheet("Text-align: left; font-weight: bold;")
        self.toggle_btn.clicked.connect(self.toggle)
        
        # Container para los botones
        self.content_widget = QFrame()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        self.content_layout.setSpacing(2)
        self.content_widget.setVisible(self.is_expanded)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.toggle_btn)
        main_layout.addWidget(self.content_widget)
    
    def add_button(self, button: QWidget) -> None:
        """Añade un botón a la sección"""
        self.content_layout.addWidget(button)
    
    def toggle(self) -> None:
        """Expande o contrae la sección"""
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        arrow = "▼" if self.is_expanded else "▶"
        self.toggle_btn.setText(f"{arrow} {self.title}")


class BotonConfig:
    """Representa la configuración de un botón"""
    
    def __init__(self, data: dict):
        self.text = data.get('text', 'Sin texto')
        self.action = data.get('action', '')
        self.action_type = data.get('action_type', 'url')  # 'url', 'qgis_query', 'command', 'custom'
        self.layers = data.get('layers', [])  # Para queries: lista de capas destino
    
    def validate(self) -> bool:
        """Valida que el botón tenga configuración mínima según su tipo"""
        if not self.text:
            logger.warning("Botón sin texto")
            return False
        if not self.action:
            logger.warning(f"Botón '{self.text}' sin acción")
            return False
        
        # Validaciones específicas por tipo
        if self.action_type == 'qgis_query':
            if not self.layers:
                logger.warning(f"Botón query '{self.text}' sin capas especificadas")
                return False
        
        return True


class SeccionConfig:
    """Representa la configuración de una sección"""
    
    def __init__(self, data: dict):
        self.title = data.get('title', 'Sección sin título')
        self.collapsed = data.get('collapsed', True)
        self.buttons = [BotonConfig(btn) for btn in data.get('buttons', [])]
    
    def validate(self) -> bool:
        """Valida que la sección tenga configuración mínima"""
        if not self.title:
            logger.warning("Sección sin título")
            return False
        if not self.buttons:
            logger.warning(f"Sección '{self.title}' sin botones")
            return False
        return True


class BotonConfigLoader:
    """Carga y valida configuración desde JSON"""
    
    def __init__(self, config_file: Path):
        """
        Args:
            config_file: Ruta al fichero JSON de configuración
        """
        self.config_file = Path(config_file)
        self.sections = []
        self.widget_title = "Botonera"  # Valor por defecto
        
        if self._file_exists():
            self._load_config()
        else:
            logger.error(f"Fichero de configuración no encontrado: {self.config_file}")
    
    def _file_exists(self) -> bool:
        """Verifica que el fichero de configuración existe"""
        if self.config_file.exists():
            return True
        logger.error(f"Fichero no encontrado: {self.config_file}")
        return False
    
    def _load_config(self) -> None:
        """Carga y valida la configuración desde JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar título del widget si está disponible
            self.widget_title = data.get('widget_title', 'Botonera')
            
            self.sections = [
                SeccionConfig(sec) 
                for sec in data.get('sections', [])
                if SeccionConfig(sec).validate()
            ]
            
            logger.info(f"Configuración cargada: {len(self.sections)} secciones")
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def get_sections(self) -> list:
        """Retorna la lista de secciones configuradas"""
        return self.sections
    
    def get_widget_title(self) -> str:
        """Retorna el título del widget configurado en JSON, o por defecto 'Botonera'"""
        return self.widget_title


class Botonera(QDockWidget):
    """
    Dock widget genérico que genera una botonera colapsable a partir de configuración JSON.
    
    La clase crea dinámicamente una interfaz de usuario con secciones colapsables conteniendo
    botones que ejecutan acciones definidas en un fichero JSON. Cada sección puede expandirse
    o contraerse, y los botones pueden ejecutar acciones como abrir URLs o ficheros.
    
    Características:
    ================
    - Lectura dinámica de configuración desde JSON
    - Secciones colapsables/expandibles
    - Título del widget configurable desde JSON
    - Búsqueda automática del JSON en la carpeta del proyecto QGIS
    - Fallback a botonera_config.json si no hay proyecto abierto
    - Integración con QGIS como dock widget
    
    Estructura del JSON:
    ====================
    {
      "widget_title": "Título del Widget",
      "sections": [
        {
          "title": "Nombre de Sección",
          "collapsed": true,
          "buttons": [
            {
              "text": "Texto del Botón",
              "action": "file:///path/to/file.pdf",
              "action_type": "url"
            }
          ]
        }
      ]
    }
    
    Búsqueda de ficheros:
    ====================
    1. Si se proporciona config_file: usa esa ruta
    2. Si hay proyecto QGIS abierto: busca {proyecto}.json en la misma carpeta
       Ejemplo: para "miproyecto.qgs" → busca "miproyecto.json"
    3. Si no hay proyecto: busca "botonera_config.json" en el directorio actual
    
    Uso:
    ====
    # Inicialización básica (busca automáticamente según proyecto QGIS)
    botonera = Botonera(parent_widget)
    
    # Inicialización con ruta específica
    botonera = Botonera(parent_widget, Path('/ruta/config.json'))
    
    Atributos de clase:
    ===================
    - titol (str): Título del widget (compatible con QvApp)
    - apareixDockat (bool): Indica que aparece como dock widget
    - esEinaGeneral (bool): Marca si es una herramienta general
    """
    
    titol = 'Botonera'
    apareixDockat = True
    esEinaGeneral = False
    
    def __init__(self, parent, config_file: Optional[Path] = None):
        """
        Inicializa el dock widget de botonera con configuración desde JSON.
        
        El método resuelve automáticamente la ubicación del fichero JSON siguiendo
        esta estrategia de búsqueda:
        
        1. Si config_file se proporciona: usa esa ruta directamente
        2. Si hay un proyecto QGIS abierto:
           - Obtiene el nombre y carpeta del proyecto
           - Busca un fichero JSON con el mismo nombre en la misma carpeta
           - Ejemplo: "D:/Proyectos/miproyecto.qgs" → busca "D:/Proyectos/miproyecto.json"
        3. Si no hay proyecto abierto:
           - Fallback a "botonera_config.json" en el directorio de trabajo actual
        
        Una vez localizado el fichero JSON:
        - Lo carga y valida con BotonConfigLoader
        - Extrae el título del widget del campo "widget_title" (default: "Botonera")
        - Crea la UI con las secciones y botones configurados
        - Configura el dock widget (ancho, posición, márgenes)
        
        Args:
            parent (QWidget): Widget padre, generalmente la aplicación QGIS principal.
                             Necesario para integrar el dock widget correctamente.
            config_file (Optional[Path]): Ruta explícita al fichero JSON de configuración.
                                         Si es None, usa la estrategia de búsqueda automática.
        
        Raises:
            Si el fichero JSON no se encuentra o no puede parsearse, se registra un error
            en el logger pero la aplicación continúa (fallback a título por defecto).
        
        Examples:
            # Inicialización automática basada en proyecto QGIS
            botonera = Botonera(iface.mainWindow())
            
            # Inicialización con ruta específica
            config_path = Path('D:/Configs/botonera.json')
            botonera = Botonera(iface.mainWindow(), config_path)
        
        Notas de implementación:
            - La búsqueda de JSON se basa en QgsProject.instance().fileName()
            - Se usa Path.stem para extraer el nombre sin extensión
            - Los logs de debug permiten rastrear qué fichero se intenta cargar
            - El dock widget se configura para aparecer en areas izquierda o derecha
        """
        # Resolver path del config file
        if config_file is None:
            # Obtener ruta del proyecto QGIS
            project = QgsProject.instance()
            project_file = project.fileName()
            
            if project_file:
                # Si hay proyecto abierto, buscar JSON en su carpeta
                project_path = Path(project_file)
                config_file = project_path.parent / f"{project_path.stem}.json"
                logger.info(f"Buscando configuración basada en proyecto QGIS: {config_file}")
            else:
                # Fallback: directorio actual
                config_file = Path.cwd() / "botonera_config.json"
                logger.info(f"No hay proyecto QGIS abierto, usando directorio actual: {config_file}")
        else:
            config_file = Path(config_file)
        
        logger.info(f"Ruta configuración: {config_file}")
        
        # Cargar configuración
        loader = BotonConfigLoader(config_file)
        
        # Inicializar con título del JSON
        super().__init__(loader.get_widget_title())
        
        # Actualizar atributo de clase para compatibilidad
        self.titol = loader.get_widget_title()
        
        self.parent = parent
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        # Crear UI
        self._create_ui(loader.get_sections())
        
        # Configurar dock widget
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.setContentsMargins(0, 0, 0, 0)
        self.show()
    
    def _create_ui(self, sections: list) -> None:
        """
        Construye la interfaz gráfica a partir de las secciones configuradas.
        
        Este método privado es responsable de:
        1. Crear el frame principal y su layout
        2. Iterar sobre cada sección de configuración
        3. Crear widgets CollapsibleSection para cada sección
        4. Crear botones dinámicos para cada botón configurado
        5. Conectar las acciones a los botones según su tipo
        6. Añadir un espaciador al final para mejor distribución visual
        
        Comportamiento:
        ===============
        - Cada sección se renderiza como un CollapsibleSection que puede expandirse
        - Los botones se alinean a la izquierda dentro de cada sección
        - Los botones de tipo 'url' abren URLs/ficheros con QDesktopServices.openUrl()
        - Los botones inválidos (sin texto o acción) se saltan silenciosamente
        - El layout se alinea al top para mejorar la presentación visual
        
        Args:
            sections (list): Lista de objetos SeccionConfig con la estructura de la UI.
                           Cada sección contiene botones configurados.
        
        Efectos secundarios:
            - Modifica self.setWidget() con el frame principal
            - Conecta señales clicked de botones a handlers de acciones
            - Los botones se añaden directamente al widget padre (self)
        
        Notas técnicas:
            - Usa lambda para capturar el valor de 'url' correctamente en el loop
            - QvPushButton se importa de moduls.QvPushButton (estilo personalizado)
            - El espaciador (QSpacerItem) con Expanding garantiza alineación al top
        """
        fMain = QFrame()
        lytMain = QVBoxLayout(fMain)
        lytMain.setAlignment(Qt.AlignTop)
        lytMain.setContentsMargins(0, 0, 0, 0)
        lytMain.setSpacing(5)
        
        fMain.setLayout(lytMain)
        
        # Crear secciones
        for seccion in sections:
            section_widget = CollapsibleSection(seccion.title, seccion.collapsed)
            
            # Crear botones en la sección
            for boton in seccion.buttons:
                if not boton.validate():
                    continue
                
                btn = QvPushButton(boton.text, flat=True)
                btn.setStyleSheet("Text-align: left")
                
                # Conectar acción según tipo
                if boton.action_type == 'url':
                    btn.clicked.connect(
                        lambda checked=False, url=boton.action: 
                        QDesktopServices().openUrl(QUrl(url))
                    )
                elif boton.action_type == 'qgis_query':
                    # Para queries: capturar el archivo y las capas
                    query_file = boton.action
                    layers = boton.layers
                    btn.clicked.connect(
                        lambda checked=False, qf=query_file, lyr=layers: 
                        self._execute_query(qf, lyr)
                    )
                # Aquí se pueden añadir más tipos de acciones
                
                section_widget.add_button(btn)
            
            lytMain.addWidget(section_widget)
        
        # Espaciador al final
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lytMain.addItem(spacer)
        
        self.setWidget(fMain)
    
    def _execute_query(self, query_filename: str, layer_names: list) -> None:
        """
        Ejecuta un query QGIS (.qqf) sobre las capas especificadas.
        
        Este método:
        1. Resuelve la ubicación del archivo .qqf (busca en carpeta 'queries/')
        2. Lee el archivo y extrae la expresión de filtro
        3. Aplica el filtro a cada capa especificada
        4. Recarga el canvas para visualizar los cambios
        5. Maneja errores con mensajes informativos
        
        Args:
            query_filename: Nombre del archivo .qqf (ej: 'viviendas_tipo_a.qqf')
            layer_names: Lista de nombres de capas donde aplicar el query
                        (ej: ['Entitats en PV', 'Entitats en PH'])
        
        Returns:
            None. Los resultados se visualizan en el mapa.
        
        Efectos secundarios:
            - Modifica el subset string de las capas indicadas
            - Recarga el canvas QGIS
            - Muestra mensajes de error si hay problemas
        """
        try:
            # Resolver ruta del archivo .qqf
            project = QgsProject.instance()
            project_file = project.fileName()
            
            if not project_file:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No hay proyecto QGIS abierto. No se puede ejecutar query."
                )
                return
            
            # Buscar carpeta 'queries/' en el mismo directorio que el proyecto
            project_path = Path(project_file)
            queries_folder = project_path.parent / "queries"
            query_file = queries_folder / query_filename
            
            # Verificar que el archivo existe
            if not query_file.exists():
                QMessageBox.warning(
                    self,
                    "Error: Query no encontrado",
                    f"El archivo de query no existe:\n{query_file}\n\n"
                    f"Asegúrese de que existe la carpeta 'queries/' "
                    f"en el mismo directorio que su proyecto QGIS"
                )
                logger.error(f"Query file not found: {query_file}")
                return
            
            # Leer la expresión de filtro del archivo .qqf
            filter_expression = QQueryFileLoader.read_filter_expression(query_file)
            
            if not filter_expression:
                QMessageBox.warning(
                    self,
                    "Error: Query inválido",
                    f"No se pudo extraer expresión de filtro de:\n{query_file}"
                )
                logger.error(f"Could not extract filter expression from {query_file}")
                return
            
            logger.info(f"Expresión de filtro: {filter_expression}")
            
            # Aplicar filtro a cada capa especificada
            applied_to_layers = []
            failed_layers = []
            
            for layer_name in layer_names:
                layers = project.mapLayersByName(layer_name)
                
                if not layers:
                    failed_layers.append(f"'{layer_name}' (no encontrada)")
                    logger.warning(f"Layer not found: {layer_name}")
                    continue
                
                layer = layers[0]  # Tomar la primera capa con ese nombre
                
                try:
                    # Aplicar subset string
                    layer.setSubsetString(filter_expression)
                    applied_to_layers.append(layer_name)
                    logger.info(f"Filter applied to layer: {layer_name}")
                    
                except Exception as e:
                    failed_layers.append(f"'{layer_name}' (error: {str(e)[:50]})")
                    logger.error(f"Error applying filter to {layer_name}: {e}")
            
            # Refrescar canvas
            project.mapCanvas().refreshAllLayers()
            
            # Mostrar resultado
            if applied_to_layers and not failed_layers:
                QMessageBox.information(
                    self,
                    "Query ejecutado",
                    f"Filtro aplicado exitosamente a:\n" +
                    "\n".join(f"  • {l}" for l in applied_to_layers)
                )
            elif applied_to_layers and failed_layers:
                QMessageBox.warning(
                    self,
                    "Query parcialmente aplicado",
                    f"Filtro aplicado a:\n" +
                    "\n".join(f"  ✓ {l}" for l in applied_to_layers) +
                    f"\n\nNo se pudo aplicar a:\n" +
                    "\n".join(f"  ✗ {l}" for l in failed_layers)
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error: Query no aplicado",
                    f"No se pudo aplicar filtro a ninguna capa:\n" +
                    "\n".join(f"  ✗ {l}" for l in failed_layers)
                )
        
        except Exception as e:
            logger.error(f"Error in _execute_query: {e}")
            QMessageBox.critical(
                self,
                "Error executing query",
                f"Error inesperado:\n{str(e)}"
            )
