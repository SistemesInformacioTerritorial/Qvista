#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug: Probar carga de modelos en QGIS
"""

import os
import sys

# Configurar QGIS
from qgis.core import QgsApplication
qgisapp = QgsApplication([], True)
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
qgisapp.initQgisApplication()

registry = QgsApplication.processingRegistry()

models_dir = r"C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models"

print("=" * 80)
print("DEBUG: Buscando modelos en QGIS registry")
print("=" * 80)

# Listar todos los proveedores
print("\nProveedores disponibles:")
for provider_id in registry.providerIds():
    provider = registry.provider(provider_id)
    print(f"  • {provider_id}: {provider.name()}")
    
    # Si es proveedor de modelos, lista modelos
    if hasattr(provider, 'models'):
        try:
            models = provider.models()
            print(f"    Modelos: {len(models)}")
            for model in models[:3]:
                model_id = model.id() if hasattr(model, 'id') else "???"
                model_name = model.displayName() if hasattr(model, 'displayName') else "???"
                print(f"      - {model_id}: {model_name}")
        except:
            pass

# Buscar modelo específico
print("\n" + "=" * 80)
print("Buscando modelos por ID...")
print("=" * 80)

test_ids = [
    "model:SalidaExcel_BIMs",
    "model:Conflicte 01",
    "SalidaExcel_BIMs",
    "Conflicte 01"
]

for test_id in test_ids:
    algo = registry.algorithmById(test_id)
    status = "✓ ENCONTRADO" if algo else "✗ no encontrado"
    print(f"{test_id}: {status}")

print("\n" + "=" * 80)
