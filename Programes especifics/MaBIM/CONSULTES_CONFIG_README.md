# Configuración de Consultas - MaBIM

## Descripción

El archivo `consultes_config.json` define los botones de consultas que aparecen en el panel "Consultes" de la aplicación MaBIM. Permite agregar, modificar o eliminar consultas sin necesidad de cambiar el código Python.

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

## Campos

- **id** (string, obligatorio): Identificador único de la consulta. Se utiliza para identificar la configuración en el código.
- **nombre** (string, obligatorio): Nombre de la pestaña que se mostrará cuando se ejecute la consulta.
- **texto** (string, obligatorio): Texto que aparece en el botón (lo que ve el usuario).
- **funcion** (string, obligatorio): Nombre de la función Python que se ejecutará al hacer clic en el botón. Debe ser un método de la clase `QMaBIM`.
- **archivo_qlr** (string, obligatorio): Nombre del archivo QLR a cargar. Debe estar en la misma carpeta que `qMaBIM.py`.
- **descripcion** (string, opcional): Descripción de la consulta para documentación.

## Ejemplos

### Agregar una nueva consulta

Para agregar una nueva consulta llamada "Consulta2" que carga un archivo diferente, agregue un nuevo objeto al array `consultas`:

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
    },
    {
      "id": "consulta2",
      "nombre": "Consulta2",
      "texto": "Consulta2",
      "funcion": "executarConsulta2",
      "archivo_qlr": "OtrasCapa.qlr",
      "descripcion": "Carga la capa OtrasCapa.qlr"
    }
  ]
}
```

### Modificar texto de un botón

Para cambiar el texto del botón "Consulta1" de "Consulta1" a "Mi Consulta":

```json
{
  "consultas": [
    {
      "id": "consulta1",
      "nombre": "Consulta1",
      "texto": "Mi Consulta",
      "funcion": "executarConsulta1",
      "archivo_qlr": "BimsSenseGeometria.qlr",
      "descripcion": "Carga la capa BimsSenseGeometria.qlr y la muestra en una tabla de atributos"
    }
  ]
}
```

## Funcionamiento

1. Cuando se inicia la aplicación, `qMaBIM.py` lee el archivo `consultes_config.json`.
2. Por cada entrada en el array `consultas`, se crea un botón en el panel de Consultes.
3. Cuando el usuario hace clic en un botón, se ejecuta la función especificada en el campo `funcion`.
4. La función genérica `_ejecutar_consulta()` carga el archivo QLR especificado y muestra los datos en una tabla.

## Validación

- El archivo debe ser JSON válido.
- Todos los campos obligatorios deben estar presentes.
- El archivo QLR especificado debe existir en la misma carpeta que `qMaBIM.py`.
- La función especificada debe existir en la clase `QMaBIM`.

## Notas

- Los cambios realizados al archivo `consultes_config.json` se cargan automáticamente en el siguiente inicio de la aplicación.
- Si hay errores al cargar la configuración, se mostrará un mensaje de error y no se crearán los botones.
