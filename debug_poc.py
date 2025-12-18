#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug para validar que funciona correctamente
"""

import sys
import os

from qgis.core.contextmanagers import qgisapp
from qgis.core import QgsApplication, QgsProject, QgsMapCanvas
from qgis.gui import QgsLayerTreeMapCanvasBridge

def debug_qgis():
    """Validar funcionalidad de QGIS"""
    
    print("=" * 70)
    print("DEBUG VIEWER POC")
    print("=" * 70)
    
    with qgisapp(sysexit=False) as app:
        
        # Test 1: Processing Registry
        print("\n[1] TESTING PROCESSING REGISTRY")
        print("-" * 70)
        
        registry = QgsApplication.processingRegistry()
        print(f"Registry: {registry}")
        print(f"Providers: {registry.providers()}")
        
        algorithms = list(registry.algorithms())
        print(f"Total algorithms: {len(algorithms)}")
        
        if len(algorithms) == 0:
            print("⚠ No hay algoritmos cargados")
            print("\nIntentando cargar algoritmos nativos...")
            
            try:
                from qgis.analysis import QgsNativeAlgorithms
                native = QgsNativeAlgorithms()
                registry.addProvider(native)
                
                algorithms = list(registry.algorithms())
                print(f"✓ Ahora hay {len(algorithms)} algoritmos")
                
                # Mostrar algunos
                print("\nPrimeros 5 algoritmos:")
                for algo in algorithms[:5]:
                    print(f"  - {algo.id()}: {algo.displayName()}")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("✓ Algoritmos cargados correctamente")
            print("\nPrimeros 5 algoritmos:")
            for algo in algorithms[:5]:
                print(f"  - {algo.id()}: {algo.displayName()}")
        
        # Test 2: Cargar proyecto
        print("\n[2] TESTING PROYECTO")
        print("-" * 70)
        
        project = QgsProject.instance()
        qgs_file = r"d:\qVista\Codi\mapesOffline\qVista default map.qgs"
        
        if os.path.exists(qgs_file):
            print(f"Cargando: {qgs_file}")
            
            if project.read(qgs_file):
                layers = project.mapLayers()
                print(f"✓ Proyecto cargado: {len(layers)} capas")
                
                for layer_id, layer in layers.items():
                    print(f"  - {layer.name()} ({layer.type()})")
            else:
                print(f"✗ No se pudo leer el proyecto")
        else:
            print(f"✗ Archivo no existe: {qgs_file}")
        
        # Test 3: Canvas
        print("\n[3] TESTING CANVAS")
        print("-" * 70)
        
        canvas = QgsMapCanvas()
        canvas.setProject(project)
        
        layers = list(project.mapLayers().values())
        if layers:
            canvas.setLayers(layers)
            canvas.zoomToFullExtent()
            print(f"✓ Canvas configurado con {len(layers)} capas")
        else:
            print("⚠ No hay capas para mostrar en canvas")
        
        print("\n" + "=" * 70)
        print("✓ DEBUG COMPLETADO")
        print("=" * 70)

if __name__ == "__main__":
    try:
        debug_qgis()
    except Exception as e:
        print(f"\n✗ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
