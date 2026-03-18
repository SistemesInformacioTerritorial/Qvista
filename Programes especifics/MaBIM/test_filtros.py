#!/usr/bin/env python3
"""
Script de prueba para verificar que MaBIM_FilterUtils lee correctamente los .qqf

Ejecutar desde la carpeta Programes especifics/MaBIM/:
    python test_filtros.py
"""

from pathlib import Path
import sys

# Importar el módulo de filtros
try:
    from MaBIM_FilterUtils import MaBIMFilterReader
    print("✓ Módulo MaBIM_FilterUtils importado correctamente\n")
except ImportError as e:
    print(f"✗ Error importando MaBIM_FilterUtils: {e}")
    print("  Asegúrate de ejecutar este script desde la carpeta MaBIM/")
    sys.exit(1)


def test_filter_file(filename):
    """Prueba leer un fichero de filtro"""
    filter_path = Path("filtros") / filename
    
    print(f"Probando: {filename}")
    print(f"  Ruta: {filter_path}")
    print(f"  Existe: {filter_path.exists()}")
    
    if not filter_path.exists():
        print(f"  ✗ Fichero no encontrado\n")
        return False
    
    # Leer contenido bruto
    content = filter_path.read_text(encoding='utf-8').strip()
    print(f"  Contenido: {content[:80]}..." if len(content) > 80 else f"  Contenido: {content}")
    
    # Leer con parser
    expression = MaBIMFilterReader.read_filter_expression(filter_path)
    
    if expression:
        print(f"  ✓ Expresión extraída: {expression}")
        print(f"    Longitud: {len(expression)} caracteres")
        return True
    else:
        print(f"  ✗ No se pudo extraer expresión")
        return False

    print()


def main():
    """Ejecuta pruebas en todos los ficheros"""
    
    print("=" * 80)
    print("PRUEBA DE LECTORA DE FILTROS .QQF")
    print("=" * 80)
    print()
    
    # Ficheros a probar
    test_files = [
        "viviendas_tipo_A.qqf",
        "viviendas_tipo_B.qqf",
        "propiedades_mal_estado.qqf",
        "viviendas_tipos_A_B.qqf",
        "viviendas_grandes.qqf",
        "viviendas_antiguas.qqf",
        "Us.qqf",
    ]
    
    results = {}
    
    for filename in test_files:
        results[filename] = test_filter_file(filename)
        print()
    
    # Resumen
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResultados: {successful}/{total} ficheros leídos correctamente\n")
    
    for filename, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")
    
    print()
    
    if successful == total:
        print("✓ TODOS LOS FICHEROS SE LEYERON CORRECTAMENTE")
        return 0
    else:
        print("✗ ALGUNOS FICHEROS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())
