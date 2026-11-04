# LISTA DE CAPTURAS REQUERIDAS PARA LA DEMOSTRACIÓN
## Guía de Verificación Visual — LegadoVivo (Segundo Incremento Móvil)

**Estudiante:** Miguel Ángel Ramírez Corredor  
**Institución:** Corporación Universitaria Lasallista  
**Aplicación:** LegadoVivo (Python + Kivy para Android)  

Conforme a los lineamientos de evaluación del Segundo Incremento, a continuación se detalla la lista de las **8 capturas de pantalla** que deben obtenerse durante la ejecución real de la aplicación en el dispositivo o emulador Android, especificando el objetivo, los datos visuales esperados y los pasos exactos para reproducirla.

---

### Captura 1: Inicio y Estado de Conectividad
- **Identificador:** `CAP-01-INICIO-CONECTIVIDAD`
- **Pantalla:** Pantalla Principal (`Biblioteca`) con cabecera superior y barra de estado.
- **Objetivo:** Demostrar la identidad visual de la aplicación móvil y la detección reactiva del estado de red en Android.
- **Elementos Visuales Clave:**
  - Barra superior (*Top AppBar*) en color azul índigo con el título *"LegadoVivo"* y el subtítulo *"Preservación de Memoria y Valores"*.
  - Botón de acceso al marco ético *"⚖ Ética"*.
  - Franja horizontal indicadora de conectividad con círculo verde y texto:  
    `● En línea • Modo local autónomo (Sin sincronización externa)`.
  - Botón interactivo *"Simular Offline"*.
  - Barra de navegación inferior con las tres pestañas ergonómicas (*Biblioteca*, *Nueva*, *Consultar*).
- **Pasos para Obtenerla:**
  1. Abrir la aplicación con el dispositivo conectado a Wi-Fi o datos móviles.
  2. Tomar la captura del viewport completo de la pantalla inicial.

---

### Captura 2: Formulario de Creación y Validación Reactiva
- **Identificador:** `CAP-02-FORMULARIO-VALIDACION`
- **Pantalla:** Pantalla de Formulario (`Nueva Cápsula`).
- **Objetivo:** Comprobar la obligatoriedad de los campos y los mensajes de error claros cuando no se cumplen los requisitos.
- **Elementos Visuales Clave:**
  - Encabezado *"Nueva Cápsula de Legado"*.
  - Banner de advertencia en color rojo:  
    `⚠ El título es obligatorio y no puede contener solo espacios` (o longitud mínima de contenido).
  - Campo de texto para el título con su texto de sugerencia (*hint*).
  - Selector desplegable (*Spinner*) con la lista de temas predefinidos (*Valores y Principios*, etc.).
  - Área multilínea para el contenido de la vivencia.
  - Interruptor (*Switch*) de autorización inmediata con su texto explicativo.
  - Botones de acción (*Guardar Cápsula*, *Cancelar / Volver*, *Limpiar Formulario*).
- **Pasos para Obtenerla:**
  1. Pulsar la pestaña inferior *"➕ Nueva"*.
  2. Dejar el campo de título vacío o escribir menos de 3 caracteres.
  3. Presionar el botón *"Guardar Cápsula"*.
  4. Capturar la pantalla mostrando la alerta roja de validación.

---

### Captura 3: Biblioteca de Cápsulas con Estados de Autorización
- **Identificador:** `CAP-03-BIBLIOTECA-CAPSULAS`
- **Pantalla:** Pantalla de Biblioteca (`Biblioteca de Cápsulas`).
- **Objetivo:** Visualizar la lista de cápsulas almacenadas en SQLite, sus etiquetas por categoría y la diferenciación entre fuentes autorizadas y borradores privados.
- **Elementos Visuales Clave:**
  - Resumen numérico en la parte superior: `Total: 4 cápsulas registradas • 3 autorizadas como fuente`.
  - Filtros superiores (*Todas*, *Solo Fuentes*, *Solo Borradores*).
  - Tarjetas de cápsulas con bordes redondeados y sombra suave:
    - Tarjeta 1 con insignia verde: `✓ FUENTE AUTORIZADA` y botón *"Retirar Fuente"*.
    - Tarjeta 4 con insignia ámbar: `🔒 BORRADOR PRIVADO` y botón *"Aprobar Fuente"*.
  - Botones individuales *"Editar"* y *"Eliminar"* en cada tarjeta.
- **Pasos para Obtenerla:**
  1. Pulsar la pestaña inferior *"📚 Biblioteca"*.
  2. Asegurarse de que el filtro activo sea *"Todas"*.
  3. Capturar la vista donde se aprecien simultáneamente tarjetas aprobadas y borradores privados.

---

### Captura 4: Consulta Exitosa con Citación Explícita de Fuentes
- **Identificador:** `CAP-04-CONSULTA-CON-FUENTES`
- **Pantalla:** Pantalla de Consulta (`Consulta de Legado Autorizado`).
- **Objetivo:** Demostrar una consulta que encuentra concordancia léxica en las cápsulas autorizadas, presentando la síntesis fundamentada y las referencias exactas de origen.
- **Elementos Visuales Clave:**
  - Banner superior obligatorio de descargo ético/legal en fondo ámbar:  
    `⚖ AVISO IMPORTANTE: Esta consulta es una representación generada exclusivamente a partir del material autorizado...`.
  - Campo de búsqueda con la consulta realizada (ej. `"honestidad en el trabajo"`).
  - Tarjeta de respuesta con encabezado verde: `✓ Respuesta Basada en Material Autorizado`.
  - Cita explícita de los extractos y títulos de las cápsulas utilizadas.
  - Sección inferior: `FUENTES AUTORIZADAS UTILIZADAS (1)` mostrando la tarjeta de la fuente con su `Ref #ID`, tema y fragmento literal.
- **Pasos para Obtenerla:**
  1. Pulsar la pestaña inferior *"🔍 Consultar"*.
  2. Escribir `"honestidad"` o presionar el botón de sugerencia rápida *"Honestidad"*.
  3. Presionar *"Consultar"*.
  4. Capturar el resultado mostrando la respuesta y la sección de fuentes citadas.

---

### Captura 5: Consulta con Abstención Estricta (Sin Invención de Respuestas)
- **Identificador:** `CAP-05-ABSTENCION-ESTRICTA`
- **Pantalla:** Pantalla de Consulta (`Consulta de Legado Autorizado`).
- **Objetivo:** Comprobar que el sistema **se abstiene deliberadamente** de responder cuando el tema consultado no tiene respaldo en las fuentes aprobadas (no inventa ni alucina).
- **Elementos Visuales Clave:**
  - Campo de búsqueda con un tema ajeno o no documentado (ej. `"viaje espacial a Marte y astrofísica"`).
  - Tarjeta destacada con borde rojo suave y título en negrita: `⛔ ABSTENCIÓN DE RESPUESTA`.
  - Texto formal de abstención:  
    `"El sistema no encontró registros o fuentes autorizadas que respondan a esta inquietud. Para garantizar la máxima fidelidad y honestidad con el titular, el sistema se abstiene deliberadamente de inventar, suponer o extrapolar respuestas."`
  - Indicador de cápsulas autorizadas disponibles en la base de datos local y recomendación de registrar el tema en la biblioteca.
- **Pasos para Obtenerla:**
  1. En la pantalla de consulta, presionar el botón de ejemplo *"Probar Abstención"* o escribir `"viaje a marte"`.
  2. Presionar el botón *"Consultar"*.
  3. Capturar la pantalla completa exhibiendo la tarjeta de abstención.

---

### Captura 6: Funcionamiento sin Conexión (Modo Offline)
- **Identificador:** `CAP-06-FUNCIONAMIENTO-OFFLINE`
- **Pantalla:** Pantalla de Biblioteca o Consulta en estado desconectado.
- **Objetivo:** Evidenciar que la aplicación continúa operando con absoluta normalidad sin depender de acceso a Internet.
- **Elementos Visuales Clave:**
  - Franja horizontal indicadora de estado en color ámbar con texto:  
    `● Sin conexión • Operación 100% local activa` (o con la marca `(Simulado)`).
  - El botón superior muestra ahora *"Restaurar Red"*.
  - Las cápsulas de la biblioteca se despliegan intactas y las consultas se resuelven de forma instantánea mediante la base de datos SQLite interna.
- **Pasos para Obtenerla:**
  1. Activar el modo avión en el dispositivo Android o pulsar el botón *"Simular Offline"*.
  2. Observar el cambio cromático a ámbar en la barra superior.
  3. Realizar una consulta o explorar la biblioteca para evidenciar plena funcionalidad.
  4. Tomar la captura de pantalla.

---

### Captura 7: Persistencia de Datos tras Reiniciar la Aplicación
- **Identificador:** `CAP-07-PERSISTENCIA-REINICIO`
- **Pantalla:** Biblioteca de Cápsulas tras forzar el cierre y relanzar la aplicación.
- **Objetivo:** Probar que las adiciones, ediciones, eliminaciones y cambios en la aprobación de fuentes sobreviven al cierre forzado del proceso y apagado del dispositivo.
- **Elementos Visuales Clave:**
  - Nueva cápsula personalizada previamente creada visible en la biblioteca (ej. *"Cápsula de prueba de persistencia"*).
  - La cápsula conserva su estado de aprobación o modificación exacto.
  - La cantidad total de registros en el contador refleja las modificaciones previas.
- **Pasos para Obtenerla:**
  1. Crear una nueva cápsula en el formulario (ej. Título: *"Recuerdo del primer empleo"*).
  2. Modificar o autorizar una cápsula existente.
  3. Cerrar por completo la aplicación desde el administrador de tareas de Android (forzar detención).
  4. Volver a abrir LegadoVivo desde el menú de aplicaciones.
  5. Capturar la biblioteca mostrando que los datos persisten íntegros.

---

### Captura 8: Aplicación Abierta en Entorno Móvil Android
- **Identificador:** `CAP-08-APP-ANDROID-REAL`
- **Pantalla:** Vista general del smartphone o emulador Android ejecutando el APK empaquetado.
- **Objetivo:** Demostrar que se trata de una aplicación Android auténtica ejecutándose sobre el sistema operativo móvil, no una página web ni una ventana de escritorio.
- **Elementos Visuales Clave:**
  - Barra de estado superior de Android (reloj del sistema, batería, señal Wi-Fi/celular).
  - Barra de navegación nativa del sistema operativo (botones atrás, inicio y multitarea o barra de gestos).
  - Teclado virtual táctil nativo de Android desplegado al interactuar con los campos de entrada de texto.
  - Integración armónica de los controles táctiles de Kivy con la densidad de píxeles del dispositivo.
- **Pasos para Obtenerla:**
  1. Ejecutar el archivo `.apk` instalado en el emulador de Android Studio o en un teléfono Android físico conectado por USB.
  2. Abrir la pantalla de creación e interactuar con el teclado virtual de Android.
  3. Tomar una captura de pantalla completa del dispositivo móvil.

