import xml.etree.ElementTree as ET

model_file = r'C:\Users\de1703\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\models\SalidaExcel_BIMs.model3'

output = []

try:
    with open(model_file) as f:
        tree = ET.parse(f)
        root = tree.getroot()
    
    output.append('XML parseado correctamente')
    
    # Buscar pasos (algoritmos)
    children = root.find(".//Option[@name='children']")
    if children is not None:
        output.append(f'Pasos encontrados: {len(children)}')
        for i, child in enumerate(children):
            algo_elem = child.find(".//Option[@name='alg_id'][@type='QString']")
            if algo_elem is not None:
                algo_id = algo_elem.get('value')
                output.append(f'  {i+1}. {algo_id}')
    else:
        output.append('No se encontraron pasos')
        
except Exception as e:
    output.append(f'Error: {e}')
    import traceback
    output.append(traceback.format_exc())

# Escribir output
with open('analyze_model_output.txt', 'w') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
