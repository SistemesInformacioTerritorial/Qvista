#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test: Verificar que QgsModelAlgorithm.fromFile() funciona
"""

import os
import sys

print("1. Inicializando QGIS...")
from qgis.core import QgsApplication, QgsModelAlgorithm

qgis_app = QgsApplication([], True)
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
qgis_app.initQgisApplication()

print("   ✓ QGIS inicializado")

# Ruta del modelo
model_file = r"C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models\SalidaExcel_BIMs.model3"

print(f"\n2. Cargando modelo desde: {os.path.basename(model_file)}")
print(f"   Existe: {os.path.exists(model_file)}")

# Intentar cargar el modelo
try:
    model = QgsModelAlgorithm()
    success = model.fromFile(model_file)
    
    print(f"   fromFile() retornó: {success}")
    
    if success:
        print(f"   ✓ Modelo cargado exitosamente")
        print(f"   Nombre: {model.displayName()}")
        print(f"   ID: {model.id()}")
        print(f"   Pasos: {model.stepCount()}")
    else:
        print(f"   ✗ fromFile() retornó False")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
