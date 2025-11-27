"""
Botonera genérica que lee configuración desde un fichero JSON
y crea secciones colapsables con botones dinámicamente.

El fichero JSON debe estar al mismo nivel del proyecto .qgs
y tener el mismo nombre (ej: proyecto.json para proyecto.qgs)
"""

import json
import logging
from pathlib import Path
from typing import Optional

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import (QDockWidget, QFrame, QSizePolicy,
                                 QSpacerItem, QVBoxLayout, QPushButton,
                                 QWidget)

from moduls.QvPushButton import QvPushButton

# Configurar logging
logger = logging.getLogger(__name__)


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
        self.action_type = data.get('action_type', 'url')  # 'url', 'command', 'custom'
    
    def validate(self) -> bool:
        """Valida que el botón tenga configuración mínima"""
        if not self.text:
            logger.warning("Botón sin texto")
            return False
        if not self.action:
            logger.warning(f"Botón '{self.text}' sin acción")
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


class Botonera(QDockWidget):
    """
    Dock widget genérico que genera una botonera a partir de JSON.
    
    Uso:
        botonera = Botonera(parent, Path('config.json'))
    """
    
    titol = 'Botonera'
    apareixDockat = True
    esEinaGeneral = False
    
    def __init__(self, parent, config_file: Optional[Path] = None):
        """
        Args:
            parent: Widget padre (generalmente la aplicación QGIS)
            config_file: Ruta al fichero JSON. Si no se proporciona, 
                        busca en el directorio actual
        """
        super().__init__("Botonera")
        self.parent = parent
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        
        # Resolver path del config file
        if config_file is None:
            config_file = Path.cwd() / "botonera_config.json"
        else:
            config_file = Path(config_file)
        
        logger.info(f"Buscando configuración en: {config_file}")
        
        # Cargar configuración
        loader = BotonConfigLoader(config_file)
        
        # Crear UI
        self._create_ui(loader.get_sections())
        
        # Configurar dock widget
        self.setMaximumWidth(500)
        self.setMinimumWidth(500)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.setContentsMargins(0, 0, 0, 0)
        self.show()
    
    def _create_ui(self, sections: list) -> None:
        """Crea la interfaz a partir de las secciones configuradas"""
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
                # Aquí se pueden añadir más tipos de acciones
                
                section_widget.add_button(btn)
            
            lytMain.addWidget(section_widget)
        
        # Espaciador al final
        spacer = QSpacerItem(50, 50, QSizePolicy.Expanding, QSizePolicy.Expanding)
        lytMain.addItem(spacer)
        
        self.setWidget(fMain)
