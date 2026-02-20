================================================================================
VISOR QGS MÍNIMO CON PROCESSINGCHAIN POC
================================================================================

Este es un Proof of Concept mínimo y funcional que demuestra:
  ✓ Cargador de ficheros .qgs
  ✓ Canvas de visualización QGIS
  ✓ DockWidget lateral con encadenamiento de procesos
  ✓ Ejecución de procesos en thread (sin bloqueos)
  ✓ Panel dinámico de parámetros

================================================================================
ARCHIVOS
================================================================================

1. qgs_viewer_poc.py
   - Ventana principal con canvas QGIS
   - Botones para abrir/limpiar proyectos
   - Integración del DockWidget de procesos

2. processing_chain_poc.py
   - ProcessingChainDock (DockWidget lateral)
   - ProcessingStep (representa un paso)
   - ProcessingExecutorThread (ejecuta sin bloquear)
   - ParameterWidget (crea UI dinámicamente)


================================================================================
CÓMO USAR
================================================================================

REQUISITOS:
  • QGIS 3.16+ instalado
  • PyQGIS disponible
  • Python 3.6+

OPCIÓN 1: Desde línea de comandos

  cd d:\qVista\Codi
  python qgs_viewer_poc.py
  
  O con fichero inicial:
  
  python qgs_viewer_poc.py mapesOffline/qVista\ default\ map.qgs

OPCIÓN 2: Desde QGIS Python Console

  import sys
  sys.path.insert(0, 'd:\\qVista\\Codi')
  exec(open('qgs_viewer_poc.py').read())

OPCIÓN 3: Integrar en qVista actual (futuro)

  from processing_chain_poc import ProcessingChainDock
  
  En la clase principal de qVista:
    self.processing_dock = ProcessingChainDock(self)
    self.addDockWidget(Qt.RightDockWidgetArea, self.processing_dock)


================================================================================
FUNCIONALIDADES
================================================================================

PANEL PRINCIPAL (izquierda):
  ✓ Botón "Abrir .qgs" - Carga un proyecto QGIS
  ✓ Botón "Limpiar" - Limpia proyecto actual
  ✓ Canvas - Visualiza capas del proyecto
  ✓ Zoom automático al cargar

DOCKWIDGET LATERAL (derecha):

  1. SELECTOR DE ALGORITMO
     - Combobox con ~100 algoritmos QGIS disponibles
     - Se actualiza automáticamente
     - Ejemplo: Buffer, Dissolve, Centroid, Clip, etc.

  2. PANEL DINÁMICO DE PARÁMETROS
     - Se crea automáticamente según algoritmo
     - Tipos soportados:
       ✓ Capas (vector/raster) → ComboBox
       ✓ Números → SpinBox
       ✓ Distancias → DoubleSpinBox
       ✓ Texto → LineEdit

  3. CONTROLES DE CADENA
     - Botón "➕ Añadir paso" - Añade algoritmo a cadena
     - Botón "➖ Quitar paso" - Elimina último paso
     - Lista visual - Muestra pasos en orden

  4. EJECUCIÓN
     - Botón "▶ EJECUTAR CADENA" - Ejecuta todos pasos
     - Barra de progreso - Muestra avance
     - Mensaje de estado - Actualiza en tiempo real


================================================================================
FLUJO DE USO TÍPICO
================================================================================

1. Ejecutar:
   python qgs_viewer_poc.py

2. Hacer clic en "Abrir .qgs"
   - Navegar a mapesOffline/
   - Seleccionar un .qgs (ej: qVista default map.qgs)

3. Verás:
   - Canvas con capas cargadas
   - Status: "Proyecto: qVista default map.qgs"
   - Dock lateral listo

4. En el Dock, crear cadena:
   a) Seleccionar "Buffer" en combobox
   b) Elegir capa en "Capa de entrada"
   c) Especificar distancia (ej: 100)
   d) Clic en "➕ Añadir paso"
   
   e) Seleccionar "Dissolve" en combobox
   f) Clic en "➕ Añadir paso"
   
   g) Seleccionar "Centroid" en combobox
   h) Clic en "➕ Añadir paso"

5. Ver cadena:
   #1 - Buffer
   #2 - Dissolve
   #3 - Centroid

6. Clic en "▶ EJECUTAR CADENA"
   - Verás barra de progreso
   - Status actualizándose
   - Al final: "✓ Cadena completada"


================================================================================
LIMITACIONES CONOCIDAS (POC)
================================================================================

❌ COSAS QUE NO FUNCIONAN AÚN:

1. Referencias entre pasos
   - Paso 1 genera "output_1"
   - Paso 2 debería recibir "output_1"
   - Falta implementar la lógica de reemplazar referencias

2. Persistencia
   - No guarda/carga cadenas en JSON
   - Se pierden al cerrar

3. Validación completa
   - No valida tipos de capas al encadenar
   - No avisa si tipos son incompatibles

4. UI avanzada
   - No permite reordenar pasos
   - No permite editar pasos
   - No muestra resultados intermedios

5. Manejo avanzado de errores
   - Algunos algoritmos generan errores silenciosos
   - Falta captura de output de algoritmos


✅ COSAS QUE SÍ FUNCIONAN:

- Cargar proyectos .qgs
- Visualizar capas en canvas
- Listar algoritmos disponibles
- Crear UI dinámica de parámetros
- Ejecutar algoritmos simples
- No bloquear UI durante ejecución
- Mostrar progreso


================================================================================
CÓMO EXTENDER
================================================================================

Para hacer un v1.0 funcional, necesitarías:

1. IMPLEMENTAR REFERENCIAS (2 horas)
   - Crear cache de resultados
   - En ProcessingStep._replace_references()
   - Mapear 'output_1' → resultado de paso anterior

2. AGREGAR PERSISTENCIA (1 hora)
   - Guardar cadena en JSON
   - Cargar desde JSON
   - En ProcessingChainDock

3. VALIDACIÓN DE TIPOS (1 hora)
   - Validar tipos antes de encadenar
   - Avisar si incompatibles
   - En ProcessingChainDock.add_step()

4. RESULTADOS FINALES (1 hora)
   - Agregar capas al proyecto
   - Actualizar canvas
   - En ProcessingExecutorThread.run()

5. UI MEJORADA (2 horas)
   - Reordenar pasos (drag&drop)
   - Editar pasos
   - Ver/eliminar resultados intermedios

TOTAL: ~7 horas para v1.0 completa


================================================================================
ARQUITECTURA
================================================================================

QgsViewerPOC (MainWindow)
  ├─ canvas (QgsMapCanvas)
  ├─ project (QgsProject)
  └─ processing_dock (ProcessingChainDock)
       ├─ combo_algorithms (QComboBox)
       ├─ parameter_widgets (Dict[str, ParameterWidget])
       ├─ steps_list (QListWidget)
       ├─ steps (List[ProcessingStep])
       └─ executor_thread (ProcessingExecutorThread)


================================================================================
DEBUGGING
================================================================================

Si algo no funciona:

1. Verifica que QGIS está bien instalado
   python -c "from qgis.core import QgsApplication; print('OK')"

2. Verifica que los ficheros están en lugar correcto
   ls -la d:\qVista\Codi\qgs_viewer_poc.py
   ls -la d:\qVista\Codi\processing_chain_poc.py

3. Ejecuta con verbose
   python -v qgs_viewer_poc.py

4. Mira la salida en terminal
   Los mensajes de debug aparecen en stdout

5. Prueba cargando un .qgs simple
   Usa uno de mapesOffline/

6. Intenta un algoritmo simple
   Prueba con "Buffer" primero


================================================================================
SIGUIENTE PASO
================================================================================

Una vez que tengas esto funcionando y validado:

1. Convertir POC en módulo completo
   processing_chain_poc.py → moduls/ProcessingChain.py

2. Integrar en qVista real
   - Añadir a moduls/eines/
   - Conectar con capas existentes
   - Agregar a menú Eines

3. Agregar v1.0 features
   - Referencias entre pasos
   - Persistencia
   - Validación completa

4. Testing exhaustivo
   - Con 20+ algoritmos
   - Con capas de diferentes tipos
   - Con casos edge


================================================================================
NOTAS TÉCNICAS
================================================================================

Imports:
  • qgis.core: QgsApplication, QgsProject, QgsProcessing
  • qgis.gui: QgsMapCanvas
  • PyQt5: Widgets, Threading, Signals/Slots

Threading:
  • ProcessingExecutorThread hereda de QThread
  • Usa signals para comunicación thread-safe
  • UI no se bloquea

Signals:
  • progress: int (0-100)
  • message: str (estado)
  • finished: bool (éxito/fallo)
  • error: str (mensaje error)

Performance:
  • Canvas actualiza automáticamente
  • Algoritmos ejecutan en thread
  • UI responsiva durante ejecución


================================================================================
CONTACTO/SOPORTE
================================================================================

Si encuentras problemas:

1. Revisa el terminal (stdout/stderr)
2. Verifica paths y permisos
3. Intenta con proyecto simple primero
4. Consulta documentación QGIS Processing


================================================================================
FIN DEL README
================================================================================

¡Listo para probar! 🚀

Ejecuta:
  python qgs_viewer_poc.py

Y verás funcionar un visor QGS mínimo con ProcessingChain.

