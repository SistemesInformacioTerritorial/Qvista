================================================================================
NUEVA FUNCIONALIDAD: EJECUTOR DE MODELOS DE PROCESOS QGIS
================================================================================

CONCEPTO:
═════════
Ya no solo construyes cadenas de algoritmos individuales.
Ahora puedes **visualizar y ejecutar modelos pregrabados** que diseñaste en QGIS.

Los modelos son:
  ✓ Procesos complejos guardados como .qgxml
  ✓ Cadenítas de herramientas diseñadas en la UI de QGIS
  ✓ Procesos personalizados con parámetros específicos
  ✓ Procesamiento lógico completo (ej: "Procesar parcelas" = Buffer + Dissolve + Clip)


DIFERENCIA:
═══════════

ANTES (ProcessingChainDock):
  1. Seleccionas algoritmo → Buffer
  2. Configuras parámetros → distancia=100
  3. Añades a cadena
  4. Seleccionas otro → Dissolve
  5. Configuras parámetros
  6. Ejecutas TODO junto

AHORA (ProcessModelsDock):
  1. Seleccionas MODELO pregrabado → "Procesar Parcelas"
  2. El modelo YA incluye: Buffer + Dissolve + Clip + etc.
  3. Configuras solo los parámetros finales (ej: buffer distance)
  4. Ejecutas el MODELO COMPLETO


NUEVOS ARCHIVOS:
════════════════

1. process_models_poc.py (350 líneas)
   ─────────────────────────────────
   Nuevo módulo con:
   
   • ProcessModelsDock(QDockWidget)
     - Lista modelos disponibles en combobox
     - Muestra descripción del modelo
     - Genera UI dinámica para parámetros
     - Ejecuta modelo sin bloquear UI
   
   • ProcessModelExecutorThread(QThread)
     - Ejecuta modelo en thread secundario
     - Emite progreso/mensajes/errores
     - Maneja excepciones
   
   • ModelParameterWidget(QFrame)
     - Widget dinámico para cada parámetro
     - Soporta: capas, números, distancias, booleanos, texto


2. qgs_viewer_advanced.py (200 líneas)
   ───────────────────────────────────
   Nuevo viewer mejorado con:
   
   • DOS docks en pestañas:
     - Pestaña 1: "Cadenas" (ProcessingChainDock original)
     - Pestaña 2: "Modelos" (ProcessModelsDock nuevo)
   
   • Canvas central
   • Botones para cargar/limpiar proyectos
   • Integración de ambos docks


ESTRUCTURA DE ARCHIVOS:
═══════════════════════

ORIGINAL (sin cambios):
  ✓ qgs_viewer_poc.py - Viewer simple
  ✓ processing_chain_poc.py - Cadenas de procesos
  ✓ debug_poc.py - Script de validación

NUEVO (mantener ambos):
  ✓ qgs_viewer_advanced.py - Viewer con ambos docks (RECOMENDADO)
  ✓ process_models_poc.py - Ejecutor de modelos (NUEVO)

PUEDES USAR:
  • qgs_viewer_poc.py → Solo cadenas
  • qgs_viewer_advanced.py → Cadenas + Modelos (MEJOR)


CÓMO ENCONTRAR TUS MODELOS:
═══════════════════════════

Los modelos que diseñaste en QGIS se almacenan en:

Windows:
  %APPDATA%\QGIS\QGIS3\profiles\default\processing\models

Linux:
  ~/.local/share/QGIS/QGIS3/profiles/default/processing/models

Formato:
  • Archivos .qgxml (modelos personalizados)
  • O Scripts .py con @alg decoradores


CÓMO USA EL CÓDIGO TUS MODELOS:
═══════════════════════════════

1. Inicia la aplicación:
   python qgs_viewer_advanced.py

2. Carga un proyecto:
   Botón "Abrir .qgs" → Selecciona proyecto

3. Pulsa pestaña "Modelos" (en lado derecho)

4. Los modelos aparecen en combobox:
   "Procesar Parcelas"
   "Buffer & Dissolve"
   "Clasificación Terrenos"
   etc.

5. Selecciona uno → Aparecen sus parámetros

6. Configura parámetros específicos

7. Pulsa "▶ EJECUTAR MODELO"

8. Verás progreso sin bloqueos en la barra


INTEGRACIÓN EN qVista:
══════════════════════

Para añadir esto a qVista.py:

1. Copiar process_models_poc.py → moduls/ProcessModels.py

2. En qVista.__init__(), añadir:
   
   from moduls.ProcessModels import ProcessModelsDock
   
   self.models_dock = ProcessModelsDock(self)
   self.addDockWidget(Qt.RightDockWidgetArea, self.models_dock)
   self.tabifyDockWidget(self.processing_dock, self.models_dock)

3. Conectar signals:
   
   self.models_dock.status_changed.connect(self.showLblFlotant)
   self.project_changed.connect(self.models_dock.update_layers)


PARÁMETROS SOPORTADOS:
══════════════════════

El widget genera UI automáticamente para:

✓ Capas (vector/raster)
  → QComboBox con capas del proyecto

✓ Números enteros
  → QSpinBox (-999999 a 999999)

✓ Números decimales / Distancias
  → QDoubleSpinBox

✓ Booleanos (True/False)
  → QCheckBox

✓ Texto
  → QLineEdit

✓ Ficheros/Output
  → QLineEdit (o dialog si lo necesitas)


FLUJO DE EJECUCIÓN:
═══════════════════

Usuario selecciona modelo
        ↓
on_model_changed()
        ↓
Lee parámetros del modelo
        ↓
Genera widgets dinámicos
        ↓
Usuario configura parámetros
        ↓
Pulsa "EJECUTAR MODELO"
        ↓
execute_model()
        ↓
ProcessModelExecutorThread(model_id, params)
        ↓
thread.run()
  • Obtiene modelo del registry
  • Crea QgsProcessingContext
  • Crea QgsProcessingFeedback
  • Ejecuta: algorithm.run(params, context, feedback)
        ↓
Emite signals:
  • progress(0-100) → progressBar
  • message(str) → status_label
  • finished(bool) → OK/Error
        ↓
UI se actualiza sin bloqueos


DEBUGGING:
══════════

Si los modelos no aparecen:

1. Ejecuta debug_poc.py para validar Processing:
   python debug_poc.py

2. Busca "modelos específicos" en output
   Si dice "No hay modelos específicos", verás todos los algoritmos

3. Los modelos personalizados pueden estar en:
   • Carpeta de modelos de QGIS (predeterminada)
   • Carpeta de scripts Python
   • Como plugins de QGIS

4. Para crear un modelo:
   • Abre QGIS
   • Diseña tu proceso con herramientas
   • Processing → Guardar como modelo
   • Aparecerá en "Modelos" del POC


DIFERENCIAS CON CADENAS:
════════════════════════

                    Cadenas     | Modelos
  ──────────────────────────────┼─────────────────
  Construir proceso             | Ya construido
  Pasos individuales            | Pasos integrados
  Flexible / Cada vez distinto  | Fijo / Reutilizable
  Más pasos = más clicks        | Un click = proceso completo
  Enseña cómo funciona          | Automatiza tareas


VENTAJAS DE MODELOS:
════════════════════

✓ Reutilizable: Una vez diseñado, se usa siempre igual
✓ Consistente: Garantiza mismo resultado siempre
✓ Rápido: Un click = todo el proceso
✓ Documentable: Guardas toda la lógica
✓ Versionable: Cambias el modelo, se actualiza automáticamente
✓ Testeable: Diseñas una vez, probado múltiples veces
✓ Transferible: Compartes .qgxml con colegas


PRÓXIMOS PASOS:
═══════════════

v2.0 MEJORAS:
  □ Auto-detectar modelos de carpeta específica
  □ Mostrar modelo en árbol (pasos internos)
  □ Guardar outputs del modelo
  □ Validación pre-ejecución
  □ Histórico de ejecuciones
  □ Exportar resultados a fichero

INTEGRACIÓN QVISTA:
  □ Mover a moduls/
  □ Conectar con system de herramientas
  □ Guardar favorites
  □ Configurar accesos directos


================================================================================
AHORA TIENES DOS OPCIONES:

1. PRUEBA RÁPIDA:
   python qgs_viewer_advanced.py
   
   Tendrás AMBOS docks en pestañas.
   Puedes construir cadenas O ejecutar modelos.

2. SOLO MODELOS:
   Edita qgs_viewer_advanced.py para quitar ProcessingChainDock
   (Si solo necesitas modelos, sin cadenas)

3. MANTENER AMBOS ORIGINALES:
   qgs_viewer_poc.py (solo cadenas)
   + El nuevo qgs_viewer_advanced.py (cadenas + modelos)

================================================================================
