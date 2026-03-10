"""
MaBIM_FilterUtils.py - Utilidades para aplicar filtros a capas de MaBIM

Proporciona funciones para:
1. Parsear ficheros .qqf (Quantum GIS Query Filter)
2. Aplicar filtros a capas específicas
3. Gestionar el estado de los filtros
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Optional, List, Tuple
from qgis.core import QgsVectorLayer, QgsMapLayer, QgsProject
from PyQt5.QtWidgets import QMessageBox


class MaBIMFilterReader:
    """Lee y parsea ficheros de filtro (.qqf)"""
    
    @staticmethod
    def read_filter_expression(filter_file: Path) -> Optional[str]:
        """
        Lee un fichero de filtro y extrae la expresión.
        
        Soporta múltiples formatos QGIS:
        1. Formato nativo .qqf: <Query>EXPRESIÓN</Query>
        2. Formato Layer Definition: <layerdefinition><subset>EXPRESIÓN</subset></layerdefinition>
        3. Formato completo QGIS: <qgis version="3.0">...</qgis>
        4. Texto plano con expresión SQL/QGIS
        
        Args:
            filter_file: Ruta al fichero .qqf
            
        Returns:
            String con la expresión de filtro, o None si error
        """
        if not filter_file.exists():
            error_msg = f"Fichero de filtro no encontrado: {filter_file}"
            print(f"ERROR: {error_msg}")
            return None
        
        try:
            content = filter_file.read_text(encoding='utf-8').strip()
            
            if not content:
                print(f"ERROR: Fichero {filter_file.name} está vacío")
                return None
            
            # Intentar parsear como XML
            if content.startswith('<') or content.startswith('<?xml'):
                result = MaBIMFilterReader._parse_xml_filter(content)
                if result is None:
                    print(f"ADVERTENCIA: No se pudo extraer expresión de {filter_file.name}")
                    print(f"  Contenido: {content[:100]}...")
                return result
            else:
                # Tratar como expresión de texto plano
                print(f"INFO: {filter_file.name} es texto plano")
                return content
                
        except Exception as e:
            print(f"ERROR leyendo {filter_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _parse_xml_filter(xml_content: str) -> Optional[str]:
        """
        Parsea contenido XML de filtro en cualquier formato QGIS.
        
        Soporta:
        1. Formato nativo .qqf:        <Query>EXPRESIÓN</Query>
        2. Formato Layer Definition:    <layerdefinition><subset>EXPRESIÓN</subset></layerdefinition>
        3. Formato QGIS completo:      <qgis version="3.0"><layerdefinition>...</qgis>
        """
        try:
            root = ET.fromstring(xml_content)
            
            # FORMATO 1: Si el root mismo es <Query>
            if root.tag == 'Query' and root.text:
                return root.text.strip()
            
            # FORMATO 1b: Buscar <Query> dentro del árbol
            query_elem = root.find('Query')
            if query_elem is not None and query_elem.text:
                return query_elem.text.strip()
            
            # FORMATO 2/3: Buscar layerdefinition > subset
            for layer_def in root.findall('.//layerdefinition'):
                subset = layer_def.find('subset')
                if subset is not None and subset.text:
                    return subset.text.strip()
            
            # FALLBACK: Buscar atributo subset
            for layer_def in root.findall('.//layerdefinition'):
                subset_attr = layer_def.get('subset')
                if subset_attr:
                    return subset_attr.strip()
            
            # FALLBACK: Buscar elemento filter directo
            for filt in root.findall('.//filter'):
                if filt.text:
                    return filt.text.strip()
                    
            return None
            
        except ET.ParseError as e:
            print(f"Error parseando XML de filtro QGIS: {e}")
            return None


class MaBIMFilterApplier:
    """Aplica filtros a las capas de MaBIM"""
    
    def __init__(self, proyecto=None):
        """
        Inicializa el aplicador de filtros.
        
        Args:
            proyecto: Proyecto QgsProject (si None, usa la instancia actual)
        """
        self.proyecto = proyecto or QgsProject.instance()
        self.filtered_layers = []  # Track de capas filtradas
    
    def apply_filter_by_file(
        self,
        filter_file: Path,
        target_layer_names: List[str],
        show_messages: bool = True,
        parent_widget=None
    ) -> bool:
        """
        Aplica un filtro desde un fichero .qqf a las capas especificadas.
        
        Args:
            filter_file: Ruta del fichero .qqf
            target_layer_names: Lista de nombres de capas a filtrar
            show_messages: Si mostrar diálogos de información
            parent_widget: Widget padre para diálogos
            
        Returns:
            True si se aplicó correctamente, False si error
        """
        # Leer expresión del fichero
        expression = MaBIMFilterReader.read_filter_expression(filter_file)
        if not expression:
            if show_messages:
                self._show_error(
                    "Error al leer filtro",
                    f"No se pudo extraer expresión de:\n{filter_file.name}",
                    parent_widget
                )
            return False
        
        # Buscar y aplicar filtro a capas
        applied_to = []
        for layer_name in target_layer_names:
            layer = self._find_layer_by_name(layer_name)
            if layer is None:
                print(f"Advertencia: Capa no encontrada: {layer_name}")
                continue
            
            if not self._is_vector_layer(layer):
                print(f"Advertencia: {layer_name} no es capa vectorial")
                continue
            
            try:
                layer.setSubsetString(expression)
                applied_to.append(layer_name)
                self.filtered_layers.append(layer)
            except Exception as e:
                print(f"Error aplicando filtro a {layer_name}: {e}")
        
        if not applied_to:
            if show_messages:
                self._show_error(
                    "No se pudieron filtrar capas",
                    f"No se encontraron las capas:\n{', '.join(target_layer_names)}",
                    parent_widget
                )
            return False
        
        # Mostrar mensaje de éxito
        if show_messages:
            message = f"Filtro aplicado a:\n{', '.join(applied_to)}"
            self._show_info("Filtro aplicado", message, parent_widget)
        
        print(f"Filtro aplicado a: {applied_to}")
        return True
    
    def apply_filter_expression(
        self,
        expression: str,
        target_layer_names: List[str],
        show_messages: bool = True,
        parent_widget=None
    ) -> bool:
        """
        Aplica una expresión de filtro directamente a capas.
        
        Args:
            expression: Expresión de filtro SQL/QGIS
            target_layer_names: Lista de nombres de capas
            show_messages: Si mostrar diálogos
            parent_widget: Widget padre
            
        Returns:
            True si se aplicó, False si error
        """
        applied_to = []
        for layer_name in target_layer_names:
            layer = self._find_layer_by_name(layer_name)
            if layer is None or not self._is_vector_layer(layer):
                continue
            
            try:
                layer.setSubsetString(expression)
                applied_to.append(layer_name)
                self.filtered_layers.append(layer)
            except Exception as e:
                print(f"Error: {e}")
        
        if not applied_to:
            return False
        
        if show_messages:
            self._show_info(
                "Filtro aplicado",
                f"Aplicado a: {', '.join(applied_to)}",
                parent_widget
            )
        
        return True
    
    def clear_filters(self, layer_names: List[str] = None) -> None:
        """
        Elimina filtros de capas.
        
        Args:
            layer_names: Nombres de capas (None = todas las filtradas)
        """
        layers_to_clear = []
        
        if layer_names is None:
            layers_to_clear = self.filtered_layers
        else:
            for name in layer_names:
                layer = self._find_layer_by_name(name)
                if layer:
                    layers_to_clear.append(layer)
        
        for layer in layers_to_clear:
            if self._is_vector_layer(layer):
                layer.setSubsetString("")
        
        self.filtered_layers.clear()
        print(f"Filtros eliminados de {len(layers_to_clear)} capas")
    
    def get_filter_status(self, layer_name: str) -> str:
        """Retorna el estado del filtro de una capa"""
        layer = self._find_layer_by_name(layer_name)
        if layer is None:
            return "Capa no encontrada"
        
        if not self._is_vector_layer(layer):
            return "No es capa vectorial"
        
        subset = layer.subsetString()
        if subset:
            return f"Filtro activo: {subset}"
        else:
            return "Sin filtro"
    
    # Métodos privados
    
    def _find_layer_by_name(self, layer_name: str) -> Optional[QgsVectorLayer]:
        """Busca una capa por nombre en el proyecto"""
        for layer in self.proyecto.mapLayers().values():
            if layer.name() == layer_name:
                return layer
        return None
    
    def _is_vector_layer(self, layer) -> bool:
        """Verifica si una capa es vectorial"""
        return layer.type() == QgsMapLayer.VectorLayer
    
    def _show_error(self, title: str, message: str, parent=None) -> None:
        """Muestra diálogo de error"""
        if parent:
            QMessageBox.warning(parent, title, message)
        else:
            print(f"ERROR [{title}]: {message}")
    
    def _show_info(self, title: str, message: str, parent=None) -> None:
        """Muestra diálogo de información"""
        if parent:
            QMessageBox.information(parent, title, message)
        else:
            print(f"INFO [{title}]: {message}")


class FilterDefinition:
    """Representa la definición de un filtro en JSON"""
    
    def __init__(self, json_dict: dict):
        """
        Inicializa desde diccionario JSON.
        
        Estructura esperada:
        {
            "id": "identificador_único",
            "texto": "Descripción para botón",
            "action_type": "filter_qqf",
            "filter_file": "ruta/relativa/filtro.qqf",
            "target_layers": ["Capa1", "Capa2"],
            "descripcion": "Descripción opcional"
        }
        """
        self.id = json_dict.get('id')
        self.texto = json_dict.get('texto', 'Filtro sin nombre')
        self.action_type = json_dict.get('action_type', 'filter_qqf')
        self.filter_file = json_dict.get('filter_file')
        self.target_layers = json_dict.get('target_layers', [])
        self.descripcion = json_dict.get('descripcion', '')
    
    def is_valid(self) -> bool:
        """Valida que la definición sea correcta"""
        return (
            self.id and
            self.action_type == 'filter_qqf' and
            self.filter_file and
            len(self.target_layers) > 0
        )
    
    def get_filter_path(self, base_dir: str = None) -> Path:
        """
        Obtiene la ruta completa al fichero de filtro.
        
        Args:
            base_dir: Directorio base para rutas relativas
            
        Returns:
            Path absoluto al fichero
        """
        filter_path = Path(self.filter_file)
        
        if filter_path.is_absolute():
            return filter_path
        
        if base_dir:
            return Path(base_dir) / filter_path
        
        return filter_path
