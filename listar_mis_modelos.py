#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LISTAR MIS MODELOS
Muestra exactamente qué modelos tienes en tu carpeta
Soporta: .model3 (nuevo JSON o antiguo XML) y .qgxml (antiguo XML)
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def list_my_models():
    """Listar modelos guardados"""
    
    models_dir = Path(os.getenv('APPDATA')) / "QGIS" / "QGIS3" / "profiles" / "default" / "processing" / "models"
    
    print("\n" + "=" * 80)
    print("MIS MODELOS QGIS")
    print("=" * 80)
    print(f"\nCarpeta: {models_dir}")
    print(f"Existe: {models_dir.exists()}")
    
    if not models_dir.exists():
        print("\n❌ La carpeta no existe. Los modelos están en otro lugar.")
        print("\nBusca tu carpeta de modelos:")
        print("  Opción 1: En QGIS → Settings → User Profiles → Open active profile folder")
        print("  Opción 2: En QGIS → Processing → Models → Designer → Help")
        return
    
    # Listar ficheros
    model3_files = list(models_dir.glob("*.model3"))
    qgxml_files = list(models_dir.glob("*.qgxml"))
    
    total_files = len(model3_files) + len(qgxml_files)
    
    if total_files == 0:
        print("\n⚠ No hay ficheros de modelos (.model3 o .qgxml)")
        return
    
    print(f"\n✓ Encontrados {total_files} modelos:\n")
    
    # Procesar .model3 (pueden ser JSON o XML - QGIS tiene un bug)
    if model3_files:
        print("═" * 80)
        print("MODELOS .model3 (Pueden ser JSON nuevo o XML antiguo)")
        print("═" * 80)
        
        for i, model_file in enumerate(model3_files, 1):
            print(f"\n{i}. {model_file.name}")
            
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Detectar formato: JSON o XML
                if content.startswith('{'):
                    # JSON format (nuevo)
                    model_data = json.loads(content)
                    
                    name = model_data.get("name", "???")
                    print(f"   Formato: JSON (nuevo)")
                    print(f"   Nombre: {name}")
                    
                    desc = model_data.get("description", "")
                    if desc:
                        print(f"   Descripción: {desc}")
                    
                    inputs = model_data.get("inputs", [])
                    if inputs:
                        print(f"   Parámetros de entrada ({len(inputs)}):")
                        for inp in inputs:
                            inp_name = inp.get("name", "???")
                            inp_type = inp.get("type", "???")
                            print(f"     • {inp_name} ({inp_type})")
                    
                    alg_list = model_data.get("steps", [])
                    print(f"   Algoritmos internos: {len(alg_list)}")
                    
                    outputs = model_data.get("outputs", [])
                    if outputs:
                        print(f"   Salidas ({len(outputs)}):")
                        for out in outputs:
                            out_name = out.get("name", "???")
                            print(f"     • {out_name}")
                
                elif content.startswith('<!DOCTYPE') or content.startswith('<Option'):
                    # XML format (antiguo, bug de QGIS)
                    print(f"   Formato: XML (antiguo - modelo guardado con extension .model3)")
                    print(f"   ⚠ Este es un modelo antiguo en formato XML")
                    
                    try:
                        import xml.etree.ElementTree as ElementTree
                        root = ElementTree.fromstring(content)
                        
                        # Nombre: buscar 'model_name' primero, luego 'name'
                        name_elem = root.find(".//Option[@name='model_name'][@type='QString']")
                        if name_elem is None:
                            name_elem = root.find(".//Option[@name='name'][@type='QString']")
                        
                        name = name_elem.get('value', '???') if name_elem is not None else "???"
                        print(f"   Nombre: {name}")
                        
                        # Descripción (si existe)
                        desc_elem = root.find(".//Option[@name='description'][@type='QString']")
                        if desc_elem is not None:
                            desc = desc_elem.get('value', '')
                            if desc:
                                print(f"   Descripción: {desc}")
                        
                        # Contar algoritmos
                        children = root.find(".//Option[@name='children']")
                        algo_count = len(children) if children is not None else 0
                        print(f"   Algoritmos internos: {algo_count}")
                        
                    except Exception as e_xml:
                        print(f"   Pero no se pudo parsear XML: {str(e_xml)[:60]}")
                
                else:
                    print(f"   ❌ Formato desconocido (no es JSON ni XML válido)")
                    print(f"   Primeros 100 caracteres: {content[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error procesando archivo: {e}")
    
    # Procesar .qgxml (antiguo formato, por compatibilidad)
    if qgxml_files:
        print("\n" + "═" * 80)
        print("MODELOS .qgxml (Formato antiguo - compatibilidad)")
        print("═" * 80)
        
        import xml.etree.ElementTree as ET
        
        for i, qgxml_file in enumerate(qgxml_files, 1):
            print(f"\n{i}. {qgxml_file.name}")
            
            try:
                tree = ET.parse(qgxml_file)
                root = tree.getroot()
                
                # Nombre
                name_elem = root.find(".//name")
                name = name_elem.text if name_elem is not None else "???"
                print(f"   Nombre: {name}")
                
                # Descripción
                desc_elem = root.find(".//description")
                if desc_elem is not None and desc_elem.text:
                    print(f"   Descripción: {desc_elem.text}")
                
                # Inputs
                inputs = root.findall(".//input")
                if inputs:
                    print(f"   Parámetros de entrada ({len(inputs)}):")
                    for inp in inputs:
                        inp_name = inp.get("name", "???")
                        inp_type = inp.get("type", "???")
                        print(f"     • {inp_name} ({inp_type})")
                
                # Algoritmos
                algo_elems = root.findall(".//algorithm")
                print(f"   Algoritmos internos: {len(algo_elems)}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"Total: {total_files} modelos ({len(model3_files)} .model3, {len(qgxml_files)} .qgxml)")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    list_my_models()
