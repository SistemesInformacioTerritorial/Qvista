#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Solución: Cargar modelo directamente usando QgsModelAlgorithm
"""

from pathlib import Path
import xml.etree.ElementTree as ET

# Ruta del modelo
model_file = r"C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models\SalidaExcel_BIMs.model3"

print(f"Analizando: {model_file}")
print(f"Existe: {Path(model_file).exists()}")

with open(model_file, 'r') as f:
    content = f.read()

print(f"Tamaño: {len(content)} bytes")
print(f"Formato: {'XML' if content.startswith('<') else 'JSON'}")

# Parsear XML
root = ET.fromstring(content)

# Información del modelo
model_name = root.find(".//Option[@name='model_name'][@type='QString']").get('value')
print(f"\nNombre: {model_name}")

# Pasos/Algoritmos
children = root.find(".//Option[@name='children']")
print(f"Número de pasos: {len(children)}")

for i, child in enumerate(children):
    algo_id = child.find(".//Option[@name='alg_id'][@type='QString']")
    if algo_id is not None:
        alg_name = algo_id.get('value')
        print(f"  Paso {i}: {alg_name}")
