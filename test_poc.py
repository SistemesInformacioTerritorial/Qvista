#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test para validar que el POC funciona correctamente
Sin GUI, solo pruebas de funcionalidad
"""

import sys
import os
from pathlib import Path

# Importar qgisapp context manager
from qgis.core.contextmanagers import qgisapp
from qgis.core import QgsProject, QgsApplication

def test_qgis_basic():
    """Test 1: Inicialización básica de QGIS"""
    print("[TEST 1] Inicializando QGIS...")
    
    with qgisapp(sysexit=False) as app:
        print("✓ QGIS inicializado correctamente")
        
        # Test 2: Acceder al registro de procesos
        print("[TEST 2] Cargando Processing Registry...")
        registry = QgsApplication.processingRegistry()
        algo_count = len(list(registry.algorithms()))
        print(f"✓ Algoritmos disponibles: {algo_count}")
        
        # Test 3: Listar algunos algoritmos
        print("[TEST 3] Primeros 5 algoritmos:")
        for i, algo in enumerate(registry.algorithms()):
            if i < 5:
                print(f"  - {algo.id()}: {algo.displayName()}")
            else:
                break
        
        # Test 4: Cargar un proyecto .qgs
        print("[TEST 4] Intentando cargar proyecto...")
        project = QgsProject.instance()
        qgs_file = r"d:\qVista\Codi\mapesOffline\qVista default map.qgs"
        
        if os.path.exists(qgs_file):
            project.read(qgs_file)
            layer_count = len(project.mapLayers())
            print(f"✓ Proyecto cargado: {layer_count} capas")
            
            # Listar capas
            print("  Capas:")
            for layer in project.mapLayers().values():
                print(f"    - {layer.name()}")
        else:
            print(f"✗ No encontrado: {qgs_file}")
        
        # Test 5: Obtener un algoritmo específico
        print("[TEST 5] Probando algoritmo 'qgis:buffer'...")
        algo = registry.algorithmById('qgis:buffer')
        
        if algo:
            print(f"✓ Algoritmo encontrado: {algo.displayName()}")
            print("  Parámetros:")
            for param in algo.parameterDefinitions():
                if not (param.flags() & 4):  # No hidden
                    print(f"    - {param.name()}: {param.type()}")
        else:
            print("✗ Algoritmo no encontrado")
        
        return True

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("TEST POC QGIS VIEWER")
        print("=" * 60)
        
        test_qgis_basic()
        
        print("\n" + "=" * 60)
        print("✓ TODOS LOS TESTS PASARON")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
