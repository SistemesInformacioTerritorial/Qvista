#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test: Cargar modelo usando processing.models
"""

import os
import sys

print("Inicializando...")

try:
    # Inicializar QGIS correctamente
    from qgis.core import QgsApplication
    from qgis import processing
    
    qgis_app = QgsApplication([], True)
    QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
    qgis_app.initQgisApplication()
    
    print("✓ QGIS iniciado")
    
    # Usar processing para cargar modelos
    from processing.modeler.models import QgsProcessingModelAlgorithm
    
    model_file = r"C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models\SalidaExcel_BIMs.model3"
    
    print(f"Cargando modelo: {os.path.basename(model_file)}")
    
    try:
        # Intentar cargar con fromFile()
        model = QgsProcessingModelAlgorithm()
        result = model.fromFile(model_file)
        
        print(f"fromFile() = {result}")
        if result:
            print(f"✓ Modelo cargado")
            print(f"  Nombre: {model.displayName()}")
    except AttributeError as ae:
        print(f"✗ fromFile no existe: {ae}")
    except Exception as e:
        print(f"✗ Error: {e}")
        
except Exception as e:
    print(f"✗ Error iniciando QGIS: {e}")
    import traceback
    traceback.print_exc()
