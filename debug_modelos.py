#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEBUG: Mostrar qué modelos se detectan
Verifica que tus modelos en:
C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models
se cargan correctamente.
"""

import sys
import os
from pathlib import Path

from qgis.core.contextmanagers import qgisapp
from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms

def debug_models():
    """Mostrar modelos disponibles"""
    
    print("=" * 80)
    print("DEBUG: MODELOS EN CARPETA")
    print("=" * 80)
    
    with qgisapp(sysexit=False) as app:
        
        # Carpeta de modelos
        models_dir = Path(os.getenv('APPDATA')) / "QGIS" / "QGIS3" / "profiles" / "default" / "processing" / "models"
        print(f"\n[1] CARPETA DE MODELOS:")
        print(f"    {models_dir}")
        print(f"    Existe: {models_dir.exists()}")
        
        if models_dir.exists():
            files = list(models_dir.glob("*.qgxml"))
            print(f"    Archivos .qgxml: {len(files)}")
            
            for f in files:
                print(f"      • {f.name}")
        
        # Inicializar Processing
        print(f"\n[2] INICIALIZANDO PROCESSING:")
        registry = QgsApplication.processingRegistry()
        
        if len(list(registry.algorithms())) == 0:
            print("    Agregando QgsNativeAlgorithms...")
            registry.addProvider(QgsNativeAlgorithms())
        
        algorithms = list(registry.algorithms())
        print(f"    Total algoritmos: {len(algorithms)}")
        
        # Filtrar modelos
        print(f"\n[3] MODELOS DETECTADOS POR REGISTRY:")
        
        model_count = 0
        for algo in algorithms:
            algo_id = algo.id()
            display_name = algo.displayName()
            
            # Detectar si es modelo
            try:
                provider = algo.provider()
                provider_id = provider.id() if provider else ""
                
                # Mostrar si es modelo
                if "model" in algo_id.lower() or "model" in provider_id.lower():
                    print(f"    • {display_name}")
                    print(f"      ID: {algo_id}")
                    print(f"      Provider: {provider_id}")
                    print()
                    model_count += 1
            except:
                pass
        
        print(f"    Total modelos detectados: {model_count}")
        
        # Mostrar providers
        print(f"\n[4] PROVIDERS DISPONIBLES:")
        providers = registry.providers()
        print(f"    Total: {len(providers)}")
        for provider in providers:
            print(f"      • {provider.id()}: {provider.name()}")
        
        # Búsqueda por nombre
        print(f"\n[5] ALGORITMOS CON 'PROCESS' EN NOMBRE:")
        process_algos = [a for a in algorithms if "process" in a.displayName().lower()]
        print(f"    Encontrados: {len(process_algos)}")
        for algo in process_algos[:10]:
            print(f"      • {algo.displayName()}")
        
        # Mostrar todos los IDs de algoritmos
        print(f"\n[6] TODOS LOS IDS DE ALGORITMOS (primeros 30):")
        for i, algo in enumerate(algorithms[:30]):
            print(f"    {i+1:2d}. {algo.id()}")
        
        print("\n" + "=" * 80)
        print("FIN DEBUG")
        print("=" * 80)

if __name__ == "__main__":
    try:
        debug_models()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
