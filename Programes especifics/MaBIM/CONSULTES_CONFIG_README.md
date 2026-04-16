# Configuración de Consultas - MaBIM

## Descripción

El archivo `consultes_config.json` define los botones de consultas que aparecen en el panel "Consultes" de la aplicación MaBIM. Permite agregar, modificar o eliminar consultas sin necesidad de cambiar el código Python.

Existen tres tipos de consultas:
1. **Consultas QLR**: Cargan capas desde archivos `.qlr`
2. **Consultas Personalizadas**: Ejecutan funciones Python personalizadas
3. **Filtros QQF**: Aplican expresiones de filtro a las capas existentes desde archivos `.qqf`

## Estructura del archivo

```json
{
  "consultas": [
    {
      "id": "consulta1",
      "nombre": "Consulta1",
      "texto": "Consulta1",
      "funcion": "executarConsulta1",
      "archivo_qlr": "BimsSenseGeometria.qlr",
      "descripcion": "Carga la capa BimsSenseGeometria.qlr y la muestra en una tabla de atributos"
    }
  ]
}
```

## Campos Comunes

- **id** (string, obligatorio): Identificador único de la consulta.
- **texto** (string, obligatorio): Texto que aparece en el botón (lo que ve el usuario).
- **descripcion** (string, opcional): Descripción de la consulta para documentación.

## Tipos de Consultas

### 1. Consulta QLR (Cargar capas)

Carga una capa desde un archivo `.qlr` y muestra sus datos en una tabla de atributos.

Campos específicos:
- **nombre** (string, obligatorio): Nombre de la pestaña que se mostrará.
- **funcion** (string, requerido): Debe ser `executarConsulta1` o un método personalizado.
- **archivo_qlr** (string, obligatorio): Nombre del archivo `.qlr` en la misma carpeta que `qMaBIM.py`.

```json
{
  "id": "consulta1",
  "nombre": "Bims sin geometría",
  "texto": "Cargar Bims",
  "funcion": "executarConsulta1",
  "archivo_qlr": "BimsSenseGeometria.qlr",
  "descripcion": "Carga la capa BimsSenseGeometria.qlr"
}
```

### 2. Consulta Personalizada (Función Python)

Ejecuta una función Python personalizada cuando se hace clic en el botón.

Campos específicos:
- **funcion** (string, obligatorio): Nombre del método en la clase `QMaBIM`.

```json
{
  "id": "filtra_csv_bim",
  "texto": "Filtrar PV/PH por CSV",
  "funcion": "filtraPVPH_desdeCSV",
  "descripcion": "Abre un diálogo para seleccionar un CSV y filtra las capas"
}
```

### 3. Filtro QQF (Aplicar filtros)

Aplica una expresión de filtro desde un archivo `.qqf` a capas específicas.

Campos específicos:
- **action_type** (string, obligatorio): Debe ser `filter_qqf`.
- **filter_file** (string, obligatorio): Ruta relativa del archivo `.qqf` desde la carpeta de MaBIM.
- **target_layers** (array, obligatorio): Lista de nombres de capas a las que aplicar el filtro.

```json
{
  "id": "filtro_qqf_viviendas_a",
  "texto": "Filtrar Viviendas Tipo A",
  "action_type": "filter_qqf",
  "filter_file": "filtros/viviendas_tipo_A.qqf",
  "target_layers": ["Entitats en PV", "Entitats en PH"],
  "descripcion": "Aplica filtro de viviendas tipo A"
}
```

## Ejemplos Prácticos

### Ejemplo 1: Agregar una consulta QLR

Para cargar una nueva capa desde un archivo `.qlr`:

```json
{
  "id": "consulta2",
  "nombre": "Otra Consulta",
  "texto": "Cargar Otra Capa",
  "funcion": "executarConsulta1",
  "archivo_qlr": "OtraCapa.qlr",
  "descripcion": "Carga otra capa y la muestra"
}
```

### Ejemplo 2: Agregar un filtro simple de viviendas

Crea el archivo `filtros/viviendas_tipo_A.qqf`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"TIPUS_VIVENDA" = 'A'</subset>
</layerdefinition>
```

Y agrega a `consultes_config.json`:

```json
{
  "id": "filtro_viviendas_a",
  "texto": "Viviendas Tipo A",
  "action_type": "filter_qqf",
  "filter_file": "filtros/viviendas_tipo_A.qqf",
  "target_layers": ["Entitats en PV", "Entitats en PH"],
  "descripcion": "Muestra solo viviendas tipo A"
}
```

### Ejemplo 3: Filtro complejo con múltiples condiciones

Crea el archivo `filtros/viviendas_modernas_grandes.qqf`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>("ANY_CONSTRUCCIO" >= 1990) AND ("SUPERFICIE" > 100)</subset>
</layerdefinition>
```

Agrega a `consultes_config.json`:

```json
{
  "id": "filtro_modernas_grandes",
  "texto": "Viviendas modernas >100m²",
  "action_type": "filter_qqf",
  "filter_file": "filtros/viviendas_modernas_grandes.qqf",
  "target_layers": ["Entitats en PV", "Entitats en PH"],
  "descripcion": "Viviendas construidas después de 1990 y >100m²"
}
```

### Ejemplo 4: Archivo completo con todos los tipos

```json
{
  "consultas": [
    {
      "id": "consulta1",
      "nombre": "Bims sin geometría",
      "texto": "Cargar Bims",
      "funcion": "executarConsulta1",
      "archivo_qlr": "BimsSenseGeometria.qlr",
      "descripcion": "Carga la capa BimsSenseGeometria.qlr"
    },
    {
      "id": "filtra_csv_bim",
      "texto": "Filtrar por CSV",
      "funcion": "filtraPVPH_desdeCSV",
      "descripcion": "Abre CSV para filtrar BIMs"
    },
    {
      "id": "filtro_tipos_a_b",
      "texto": "Viviendas A y B",
      "action_type": "filter_qqf",
      "filter_file": "filtros/viviendas_A_B.qqf",
      "target_layers": ["Entitats en PV", "Entitats en PH"],
      "descripcion": "Muestra solo viviendas tipo A o B"
    }
  ]
}
```

## Cómo Crear Filtros .QQF

### Paso 1: Identificar la expresión de filtro

Determina qué expresión de filtro quieres aplicar. Por ejemplo:
- `"TIPUS_VIVENDA" = 'A'` - solo viviendas tipo A
- `("ESTAT" = 'Ruinoso') OR ("ESTAT" = 'Deteriorado')` - propiedades en mal estado
- `"SUPERFICIE" > 150` - propiedades grandes

### Paso 2: Crear el archivo .QQF

1. Abre un editor de texto (Notepad, VS Code, etc.)
2. Crea un archivo con este contenido:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>TU_EXPRESIÓN_AQUÍ</subset>
</layerdefinition>
```

3. Reemplaza `TU_EXPRESIÓN_AQUÍ` con tu filtro
4. Guarda como `nombre_filtro.qqf` en la carpeta `filtros/`

### Paso 3: Agregar a consultes_config.json

Agrega una nueva entrada en el array `consultas`:

```json
{
  "id": "mi_filtro",
  "texto": "Mi Filtro",
  "action_type": "filter_qqf",
  "filter_file": "filtros/nombre_filtro.qqf",
  "target_layers": ["Entitats en PV", "Entitats en PH"],
  "descripcion": "Descripción del filtro"
}
```

### Paso 4: Probar en QGIS

Antes de usar en MaBIM:

1. Abre el mapa en QGIS
2. Selecciona la capa "Entitats en PV" o "Entitats en PH"
3. Clic derecho → Filtro
4. Pega tu expresión de filtro
5. Si funciona en QGIS, funcionará en MaBIM

## Expresiones de Filtro Comunes

### Filtrar por tipo de vivienda

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"TIPUS_VIVENDA" = 'A'</subset>
</layerdefinition>
```

### Filtrar por múltiples tipos

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"TIPUS_VIVENDA" IN ('A', 'B', 'C')</subset>
</layerdefinition>
```

### Filtrar por antigüedad mínima

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"ANY_CONSTRUCCIO" >= 1990</subset>
</layerdefinition>
```

### Filtrar por superficie mínima

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"SUPERFICIE" > 100</subset>
</layerdefinition>
```

### Filtrar por estado de conservación

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>"ESTAT" IN ('Ruinoso', 'Deteriorado')</subset>
</layerdefinition>
```

### Filtro complejo: viviendas grandes modernas en buen estado

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layerdefinition>
  <subset>(("TIPUS_VIVENDA" = 'A') OR ("TIPUS_VIVENDA" = 'B')) AND ("ANY_CONSTRUCCIO" >= 1980) AND ("SUPERFICIE" > 80) AND ("ESTAT" NOT IN ('Ruinoso', 'Deteriorado'))</subset>
</layerdefinition>
```

## Funcionamiento

### Consultas QLR
1. Se carga el archivo `.qlr` especificado
2. Se crea una nueva pestaña con la capa cargada
3. Se muestra una tabla de atributos con los datos

### Consultas Personalizadas
1. Se ejecuta la función Python especificada
2. La función puede hacer cualquier operación: abrir diálogos, aplicar filtros, etc.

### Filtros QQF
1. Se lee el fichero `.qqf` de la carpeta `filtros/`
2. Se extrae la expresión de filtro
3. Se aplica a las capas especificadas en `target_layers`
4. Las capas se filtran inmediatamente (sin crear nuevas capas)
5. Se muestra un mensaje confirmando la aplicación del filtro

## Validación

- El archivo debe ser JSON válido.
- Para consultas QLR:
  - El archivo `.qlr` debe existir en la misma carpeta que `qMaBIM.py`
  - La función especificada debe existir en la clase `QMaBIM`
- Para filtros QQF:
  - El archivo `.qqf` debe existir en la carpeta `filtros/`
  - Las capas especificadas en `target_layers` deben existir en el proyecto
  - La expresión de filtro debe ser válida en QGIS

## Depuración

### Si los botones no aparecen
- Verifica que `consultes_config.json` es JSON válido (usa JSONLint)
- Verifica que el archivo está en la misma carpeta que `qMaBIM.py`
- Revisa la consola de Python para mensajes de error

### Si un filtro no funciona
- Abre QGIS y prueba tu expresión directamente en la capa
- Verifica que los nombres de campos son exactos (con comillas dobles)
- Verifica que los nombres de capas en `target_layers` son exactos
- Revisa los mensajes de error en la consola

### Ver expresión de filtro actual
En la consola de QGIS:
```python
layer = QgsProject.instance().mapLayersByName("Entitats en PV")[0]
print(layer.subsetString())  # Muestra la expresión actual
```

## Notas Importantes

- Los cambios al archivo `consultes_config.json` se cargan después de reiniciar la aplicación
- Un fichero `.qqf` puede contener solo una expresión de filtro
- Los nombres de campos en expresiones de filtro van entre comillas dobles: `"CAMPO"`
- Los valores de texto van entre comillas simples: `'valor'`
- Los números no llevan comillas: `123`
- Usa paréntesis para mayor claridad en expresiones complejas
- Para obtener ayuda sobre sintaxis de filtros, ver `filtros/EJEMPLO_EXPRESIONES_FILTROS.txt`

