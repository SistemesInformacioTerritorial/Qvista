#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug: Analizar estructura XML de los modelos
Para encontrar dónde está el nombre del modelo
"""

import xml.etree.ElementTree as ET
from pathlib import Path

file_path = r'C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models\SalidaExcel_BIMs.model3'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

root = ET.fromstring(content)

print("=" * 80)
print("ANÁLISIS ESTRUCTURA XML")
print("=" * 80)

# Mostrar atributos raíz
print("\n1. Atributos raíz:")
print(f"   Tag: {root.tag}")
print(f"   Atributos: {root.attrib}")

# Buscar elementos 'name' y sus valores
print("\n2. Buscando elementos 'name':")
for elem in root.iter():
    if 'name' in elem.attrib:
        name_val = elem.get('name')
        value_val = elem.get('value', '')
        elem_type = elem.get('type', '')
        
        if name_val:
            print(f"   {elem.tag}[name='{name_val}'] type='{elem_type}'")
            if value_val:
                print(f"      → value: {value_val[:100]}")

# Buscar Option con type='QString'
print("\n3. Elementos Option con type='QString':")
options = root.findall(".//Option[@type='QString']")
for i, opt in enumerate(options[:15]):
    name = opt.get('name', '???')
    value = opt.get('value', '')
    if value:
        print(f"   {i}: name='{name}' → {value[:100]}")

# Buscar según modelo estándar
print("\n4. Atributo 'name' global (si existe):")
name_attr = root.get('name')
if name_attr:
    print(f"   Root name: {name_attr}")
else:
    print("   No encontrado en raíz")

print("\n" + "=" * 80)
