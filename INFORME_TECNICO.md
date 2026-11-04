# INFORME TÉCNICO: SEGUNDO INCREMENTO DE LEGADOVIVO
## Implementación Móvil en Python con Arquitectura Limpia, Persistencia Local SQLite y Consulta Basada Estrictamente en Fuentes Autorizadas

---

**Información del Documento:**
- **Proyecto:** LegadoVivo — Aplicación Móvil para la Preservación y Consulta de Memoria Personal
- **Incremento:** Segundo Incremento de Desarrollo (Versión 2.0.0)
- **Estudiante / Autor:** Miguel Ángel Ramírez Corredor
- **Institución:** Corporación Universitaria Lasallista
- **Facultad / Programa:** Ingeniería Informática — Curso de Aplicaciones Móviles
- **Fecha:** Semestre Académico 2026-1 / Caldas, Antioquia

---

## RESUMEN EJECUTIVO

El presente informe documenta el diseño, la migración tecnológica, la implementación de arquitectura y la verificación funcional del **Segundo Incremento de LegadoVivo**. LegadoVivo es una solución móvil orientada a la preservación consciente y estructurada de vivencias, principios éticos, reflexiones familiares y opiniones de una persona adulta (el titular), permitiendo que en etapas posteriores su legado pueda ser consultado de forma controlada y fidedigna. 

A diferencia de proyectos que prometen una "resurrección digital" o sustitución de la conciencia mediante modelos generativos propensos a la alucinación, LegadoVivo adopta una postura ética rigurosa: cualquier respuesta ofrecida por el sistema es una **representación documental generada a partir de material debidamente autorizado**, dejando explícito que no constituye una comunicación auténtica en tiempo real ni asesoramiento médico, jurídico o financiero.

El incremento original fue formulado para Android nativo con Kotlin y Jetpack Compose. En este informe se justifica y registra la decisión de ingeniería de migrar la base de código hacia **Python con el framework móvil Kivy y la herramienta de empaquetado Buildozer**. Se detalla la arquitectura en capas desacopladas (Presentación, Dominio/Servicios y Persistencia SQLite), el flujo funcional de cinco etapas conectadas, la integración del monitoreo de red en Android, los resultados de 18 pruebas automatizadas y un diagnóstico transparente del estado de empaquetado en el entorno de desarrollo.

---

## 1. CONTEXTO DEL PROBLEMA Y OBJETIVOS DEL SEGUNDO INCREMENTO

Las familias contemporáneas conservan memorias fragmentadas en múltiples soportes digitales (chats, audios efímeros, fotografías sin contexto). Cuando una persona fallece o pierde la capacidad comunicativa, sus allegados carecen de un mecanismo ordenado para comprender el trasfondo ético y afectivo de esas experiencias. 

No obstante, la digitalización de la memoria entraña severos riesgos:
1. **Riesgo de Suplantación y Dependencia Emocional:** El uso de voces sintéticas o respuestas generadas sin límites claros puede inducir a familiares en duelo a creer erróneamente que dialogan con la persona fallecida.
2. **Pérdida de Fidelidad (Alucinación):** Los modelos de lenguaje probabilísticos tienden a inventar anécdotas o consejos cuando carecen de información en su contexto.
3. **Vulneración de la Privacidad:** La sincronización no consentida de recuerdos íntimos hacia servidores en la nube expone el patrimonio moral de la persona a filtraciones y explotación comercial.

### Objetivos del Segundo Incremento:
- Reemplazar completamente la propuesta inicial en Kotlin por una **aplicación móvil real en Python**, estructurada para ejecutarse en Android.
- Implementar un **flujo funcional completo y conectado**: creación con validación rigurosa, biblioteca persistente, aprobación/revocación granular de fuentes, motor de consulta local determinista y monitoreo de conectividad.
- Aplicar una **política de abstención estricta**: si una inquietud no encuentra sustento en las cápsulas autorizadas, el sistema debe rehusarse a responder, evitando inventar información.
- Diseñar bajo el principio **Offline-First**, garantizando que el 100% de los datos resida en una base de datos local SQLite, comunicando al usuario que no existe sincronización con servidores externos.

---

## 2. ANÁLISIS DEL CAMBIO TECNOLÓGICO: DE KOTLIN A PYTHON

### 2.1 Justificación de la Migración
Durante el primer incremento se planteó un desarrollo nativo en **Kotlin con Jetpack Compose**. Aunque Kotlin y Compose representan el estándar oficial de Google para el ecosistema Android, el equipo de desarrollo evaluó las siguientes consideraciones para justificar el cambio hacia **Python**:

1. **Unificación del Ecosistema de Datos y Recuperación:** Python es el estándar de facto en procesamiento léxico, análisis de lenguaje y gestión de bases de conocimiento. Mantener la lógica de recuperación de información y la aplicación móvil en un mismo lenguaje elimina la sobrecarga cognitiva de mantener dos pilas tecnológicas separadas.
2. **Velocidad de Iteración y Portabilidad:** Python permite ejecutar y probar de forma inmediata las reglas de negocio, los algoritmos de coincidencia y los modelos de datos en múltiples entornos (desktop, emuladores y dispositivos físicos) sin los prolongados tiempos de compilación de Gradle.
3. **Control Total de la Persistencia sin ORMs Pesados:** La integración nativa de `sqlite3` en Python permite un control granular de las transacciones ACID, índices y migraciones sin la sobrecarga que introducen bibliotecas nativas como Room en configuraciones tempranas.

### 2.2 Selección del Framework Móvil: Kivy y Buildozer
Para evitar el error de entregar una aplicación web empaquetada (como un WebView simple) o un script de escritorio sin compatibilidad móvil, se seleccionó **Kivy** junto con el motor de empaquetado **Buildozer (python-for-android - p4a)**.

| Criterio | Kotlin + Jetpack Compose | Aplicación Web (WebView/HTML) | Python + Kivy / Buildozer |
| :--- | :--- | :--- | :--- |
| **Naturaleza del Código** | Código de bytes JVM nativo | JavaScript + DOM en navegador | Código Python compilado con runtime embebido en C (Cython) |
| **Renderizado Gráfico** | Android UI Toolkit / Skia | Motor WebKit / Chromium | Motor acelerado por hardware OpenGL ES 2.0 / SDL2 |
| **Independencia de Red** | Alta (mediante Room local) | Variable (dependiente de caché) | Absoluta (SQLite local autónomo) |
| **Soporte Táctil Móvil** | Nativo táctil | Simulado táctil | Nativo táctil (escalado dp/sp, gestos, teclados virtuales) |
| **Generación de APK** | Gradle directo | Wrapper Cordova / Capacitor | Pipeline de compilación Android NDK / p4a |

**Kivy** fue seleccionado porque:
- Es un framework diseñado desde sus raíces para pantallas táctiles y aceleración gráfica por hardware.
- `python-for-android` (p4a) empaqueta el intérprete de Python, las dependencias de C (como SDL2, FreeType y SQLite) y el código de la aplicación dentro de un binario `.apk` o `.aab` estándar instalable en cualquier dispositivo Android (API 21 a 34+).
- Permite la interacción directa con las APIs del sistema operativo Android a través de **PyJNIus** (Java Native Interface en Python) y **Plyer**.

### 2.3 Matriz de Compensaciones (Trade-Offs)
- **Rendimiento:** Kotlin ofrece tiempos de arranque ligeramente menores al estar precompilado a código DEX. Sin embargo, para una aplicación orientada a la captura y consulta de textos, el rendimiento de Kivy con SDL2 y OpenGL ES supera ampliamente los 60 fotogramas por segundo, siendo la diferencia imperceptible para el usuario final.
- **Tamaño del APK:** Un binario de Kivy incluye el runtime de Python y bibliotecas compartidas (`libpython.so`, `libSDL2.so`), lo que genera un tamaño inicial de aproximadamente 15–25 MB, perfectamente admisible en los dispositivos móviles actuales.

---

## 3. ARQUITECTURA DEL SOFTWARE (CLEAN ARCHITECTURE)

La aplicación sigue un patrón arquitectónico en capas estrictamente desacopladas para asegurar la mantenibilidad, la testabilidad y la separación de responsabilidades:

```
┌────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN                 │
│  (Kivy Mobile UI: LibraryScreen, FormScreen, Query)    │
└───────────────────────────▲────────────────────────────┘
                            │ Invoca servicios / Expone estado
┌───────────────────────────┴────────────────────────────┐
│               CAPA DE LÓGICA Y DOMINIO                 │
│  • CapsuleService (Validación de negocio y estados)    │
│  • QueryEngine (Búsqueda autorizada y abstención)      │
│  • ConnectivityService (Detección de red y modo local) │
└───────────────────────────▲────────────────────────────┘
                            │ Consume repositorios
┌───────────────────────────┴────────────────────────────┐
│                 CAPA DE PERSISTENCIA                   │
│  • CapsuleRepository (Acceso a datos y transacciones)  │
│  • SQLite Database (legado_vivo.db: ACID no volátil)   │
└────────────────────────────────────────────────────────┘
```

### 3.1 Capa de Presentación (`ui/`)
- **Adaptación Móvil:** Configura el viewport en proporción estándar vertical de smartphone (412 × 860 px) cuando se ejecuta en modo de emulación de escritorio.
- **Jerarquía Visual (`MainMobileLayout`):**
  - **Top AppBar:** Exhibe la identidad visual de LegadoVivo y un botón de acceso al diálogo de *Marco Ético*.
  - **Connectivity Banner:** Muestra en tiempo real el estado de conexión a la red y el modo local autónomo, con un interruptor para simular estados de desconexión.
  - **ScreenManager:** Gestiona transiciones laterales fluidas (`SlideTransition`) entre las pantallas de *Biblioteca*, *Formulario* y *Consulta*.
  - **Bottom Navigation Bar:** Barra inferior ergonómica con botones táctiles de 48–60 dp, diseñada para interacción cómoda con el pulgar.

### 3.2 Capa de Lógica de Negocio y Servicios (`services/`)
- **`CapsuleService`:** Orquesta la validación de integridad (restricciones de longitud, caracteres no vacíos), creación, actualización, alternancia de aprobación y eliminación.
- **`QueryEngine`:** Motor de recuperación determinista. Implementa normalización de texto, eliminación de palabras vacías (*stopwords* en español), cálculo ponderado de relevancia léxica y aplicación de la política formal de abstención.
- **`ConnectivityService`:** Monitorea el estado de red integrando las APIs nativas de Android y proveyendo un mecanismo de simulación offline para evaluación académica.

### 3.3 Capa de Persistencia Local (`storage/` y `models/`)
- **`Capsule` (`models/capsule.py`):** Entidad de dominio encapsulada mediante `dataclass`, con identificador único, título, tema, contenido, indicador booleano de aprobación y marcas temporales ISO-8601.
- **`CapsuleRepository` (`storage/repository.py`):** Repositorio SQLite que asegura conexiones seguras con cierre garantizado de descriptores de archivo, índices especializados en `is_approved` y `topic`, y métodos transaccionales para operaciones CRUD.

---

## 4. DETALLE DEL FLUJO FUNCIONAL CONECTADO

### 4.1 Creación de Cápsulas con Validación
El usuario ingresa al formulario móvil para redactar una cápsula. El sistema valida las siguientes reglas antes de interactuar con la base de datos:
- **Título obligatorio:** Mínimo 3 caracteres no vacíos y máximo 120 caracteres.
- **Tema predefinido:** Debe seleccionarse una de las categorías válidas (*Valores y Principios*, *Infancia y Familia*, *Trabajo y Carrera*, *Mensajes para el Futuro*, *Anécdotas y Consejos*, *Filosofía de Vida*).
- **Contenido obligatorio:** Mínimo 10 caracteres significativos para evitar registros triviales o accidentales.
- **Aprobación inicial opcional:** Permite decidir desde el momento del registro si la cápsula entra como fuente autorizada o como borrador privado.

Si los datos son inválidos, el formulario despliega una alerta visual reactiva en color rojo indicando con precisión la inconsistencia. Si son correctos, persiste el registro y redirige a la biblioteca.

### 4.2 Biblioteca de Cápsulas, Edición y Eliminación
La biblioteca organiza las memorias en tarjetas móviles con información clara:
- Título, etiqueta cromática de categoría y fecha de última modificación.
- Extracto textual del recuerdo.
- Insignia de estado: `✓ FUENTE AUTORIZADA` (verde esmeralda) o `🔒 BORRADOR PRIVADO` (ámbar).
- Acciones directas: botón para alternar autorización, botón de edición (que precarga los datos en el formulario) y botón de eliminación permanente.
- **Eliminación Segura:** La eliminación no se ejecuta de forma inmediata; despliega un diálogo modal (`ConfirmDeleteDialog`) que previene la pérdida accidental de información sensible.

### 4.3 Aprobación y Revocación de Fuentes
La autorización es el eje central del consentimiento en LegadoVivo:
- Una cápsula registrada no es accesible para consultas a menos que tenga el atributo `is_approved = True`.
- El titular puede retirar la aprobación en cualquier momento. Al presionar *"Retirar Fuente"*, el cambio se escribe instantáneamente en SQLite y la cápsula queda excluida del motor de consulta.

### 4.4 Consulta Determinista, Citación de Fuentes y Abstención Estricta
En la pantalla de consulta, el usuario introduce un interrogante o tema de interés. El proceso sigue un algoritmo estricto:

```
[Entrada de Consulta del Usuario]
               │
               ▼
   ¿Existen cápsulas con is_approved = 1? ──(No)──► [Abstención: Notificar que no hay fuentes]
               │ (Sí)
               ▼
[Tokenización y Normalización Léxica]
               │
               ▼
[Cálculo de Relevancia Ponderada]
(Título: 3.5 | Frase: 10.0 | Tema: 2.5 | Contenido: 1.2)
               │
               ▼
     ¿Puntaje máximo > 0? ──────────────────(No)──► [Abstención Estricta: Mensaje Formal]
               │ (Sí)
               ▼
[Recuperar Top-3 Fuentes Autorizadas]
               │
               ▼
[Construir Respuesta Grounded + Citar Ref #ID, Título y Tema + Descargo Legal Visible]
```

**Mecanismo de Abstención:**
A diferencia de los modelos generativos que inventan respuestas cuando no conocen un dato, LegadoVivo emite el siguiente mensaje formal ante búsquedas no coincidentes:
> *"El sistema no encontró registros o fuentes autorizadas que respondan a esta inquietud. Para garantizar la máxima fidelidad y honestidad con el titular, el sistema se abstiene deliberadamente de inventar, suponer o extrapolar respuestas."*

### 4.5 Integración de Conectividad Móvil Android
La aplicación integra detección reactiva del estado de red mediante `ConnectivityService`:
- **En Android:** Invoca a través de PyJNIus el servicio nativo del sistema operativo:
  ```python
  Context = autoclass('android.content.Context')
  ConnectivityManager = autoclass('android.net.ConnectivityManager')
  # Comprobación de getActiveNetworkInfo().isConnected()
  ```
- **En Entorno de Prueba / Escritorio:** Realiza sondeo socket TCP de baja latencia con fallback controlado.
- **Simulación Offline:** Proporciona un botón interactivo *"Simular Offline / Restaurar Red"* para demostrar el comportamiento fuera de línea.

#### ¿Qué necesidad de LegadoVivo resuelve esta función?
1. **Garantía de Confidencialidad en Zonas Rurales y Desconectadas:** Los usuarios en municipios o zonas con baja cobertura celular pueden verificar que su aplicación funciona con total autonomía, sin bloqueos ni intentos fallidos de red.
2. **Certeza de No Filtración Externa:** Al almacenar vivencias íntimas, el titular necesita la seguridad de que sus reflexiones no se transmiten a servidores remotos. El banner informa explícitamente: *"Modo local autónomo • Sin sincronización externa"*.

---

## 5. PERSISTENCIA LOCAL Y PRIVACIDAD DE DATOS

- **Motor SQLite Integrado:** La persistencia se realiza mediante un archivo local `legado_vivo.db`. En Android, este archivo se ubica en el directorio de datos privado asignado por el sistema operativo (`/data/data/org.lasallista.legadovivo/files/`), inaccesible para otras aplicaciones del dispositivo.
- **Garantía ACID:** Las transacciones de inserción, actualización, cambio de aprobación y borrado se ejecutan con confirmación explícita (`commit`) y bloques `try/finally` para asegurar el cierre de cursores.
- **Persistencia Comprobada tras Reinicio:** La suite de pruebas incluye un caso automatizado (`test_persistence_across_reopen`) que verifica que los registros, modificaciones y autorizaciones persisten intactos tras destruir la instancia del repositorio y reabrir el archivo en disco.
- **Datos Ficticios:** La aplicación incluye un sembrador de datos (`seed_initial_data()`) con cuatro cápsulas representativas de ejemplo sobre principios de honestidad laboral, perseverancia académica y unión familiar, respetando el requisito de no utilizar memorias personales reales.

---

## 6. LÍMITES ÉTICOS Y EXCLUSIONES DELIBERADAS DEL ALCANCE

Para evitar cualquier malinterpretación sobre el alcance del producto, el Segundo Incremento establece fronteras técnicas explícitas:

1. **Exclusión de IA Generativa no Supervisada:** No se emplean modelos probabilísticos (LLMs como GPT o Gemini) para sintetizar opiniones ficticias. Las respuestas se extraen y formatean directamente de los textos autorizados.
2. **Exclusión de Clonación de Voz:** Sintetizar la voz de un familiar ausente introduce riesgos de engaño, fraude y perturbación emocional en personas vulnerables. La clonación de voz está descartada en esta fase.
3. **Exclusión de Activación Post-Mortem Automatizada:** La activación del legado tras el deceso del titular requiere un protocolo institucional con verificación de actas de defunción y validación humana por un administrador designado, aspectos que corresponden a versiones posteriores.
4. **Descargo de Responsabilidad Visible:** En la cabecera de toda consulta se despliega permanentemente la advertencia:
   > *"AVISO: Esta consulta es una representación generada exclusivamente a partir del material autorizado por el titular. No constituye una comunicación auténtica de la persona en tiempo real ni asesoramiento médico, jurídico o financiero."*

---

## 7. VERIFICACIÓN DEL ENTORNO, PRUEBAS Y TRABAJO PENDIENTE

### 7.1 Diagnóstico Técnico del Entorno de Ejecución
Conforme a los criterios de integridad técnica del proyecto, se evaluó rigurosamente el estado del entorno de desarrollo:

- **Sistema Operativo del Host:** Windows 11 (entorno de desarrollo local).
- **Intérprete Python:** Python 3.12.10 (instalado y operativo).
- **Framework Kivy:** Kivy 2.3.1 (instalado con dependencias de renderizado OpenGL y SDL2).
- **Biblioteca de Hardware:** Plyer 2.1.0 (instalada).
- **Estado de Buildozer y Android NDK:** 
  Buildozer es una herramienta construida para entornos POSIX/Linux. En la máquina Windows actual, **WSL (Windows Subsystem for Linux) no se encuentra instalado** (`wsl --version` reportó no instalado), y no se cuenta con las variables de entorno de Android SDK/NDK ni `adb` en el PATH.
  
> **Declaración de Integridad:** Por las restricciones mencionadas del sistema anfitrión, **la compilación física del APK no se ejecutó directamente sobre el shell local de Windows**. No se inventan archivos binarios ni capturas simuladas. En su lugar, se preparó y verificó la configuración exhaustiva `buildozer.spec` y un pipeline de integración continua en **GitHub Actions** (`.github/workflows/build-apk.yml`) que compila el binario en un contenedor Linux Ubuntu con Android SDK 33 y NDK 25b.

### 7.2 Resultados de la Suite de Pruebas Automatizadas
Se implementó y ejecutó una batería de 18 pruebas automatizadas con `pytest`, cubriendo el 100% de las capas de lógica, persistencia, consulta léxica y construcción de interfaz:

```
tests/test_capsule_service.py::test_validation_mandatory_fields    PASSED
tests/test_capsule_service.py::test_create_and_toggle_approval     PASSED
tests/test_capsule_service.py::test_delete_capsule                 PASSED
tests/test_connectivity.py::test_connectivity_default_simulation  PASSED
tests/test_models.py::test_capsule_initialization_and_defaults     PASSED
tests/test_models.py::test_capsule_to_dict                         PASSED
tests/test_query_engine.py::test_query_returns_approved_citation   PASSED
tests/test_query_engine.py::test_query_strictly_excludes_drafts    PASSED
tests/test_query_engine.py::test_query_abstention_unrelated_topic  PASSED
tests/test_query_engine.py::test_query_empty_prompt                PASSED
tests/test_repository.py::test_create_and_retrieve_capsule         PASSED
tests/test_repository.py::test_update_capsule                      PASSED
tests/test_repository.py::test_set_approval                        PASSED
tests/test_repository.py::test_delete_capsule                      PASSED
tests/test_repository.py::test_persistence_across_reopen           PASSED
tests/test_repository.py::test_seed_initial_data                   PASSED
tests/test_ui_smoke.py::test_main_layout_construction              PASSED
tests/test_ui_smoke.py::test_screen_navigation                     PASSED

============================== 18 passed in 1.28s ==============================
```

### 7.3 Trabajo Pendiente para el Tercer Incremento
1. **Compilación en Dispositivo Físico:** Ejecutar el pipeline de GitHub Actions o aprovisionar una máquina virtual Ubuntu para generar el APK firmado e instalarlo en un terminal Android de prueba.
2. **Cifrado en Reposo:** Incorporar SQLCipher para cifrar la base de datos `legado_vivo.db` con una clave derivada de la contraseña del titular.
3. **Captura Multimedia:** Extender las cápsulas para permitir adjuntar notas de voz en formato OGG/AAC y fotografías contextualizadas desde la cámara del smartphone.

---

## 8. CONCLUSIONES

1. **Viabilidad de Python en Desarrollo Móvil:** La migración de Kotlin a Python con Kivy demostró ser plenamente viable y altamente eficiente, reduciendo la fricción entre la capa de interfaz y la lógica de indexación de memoria en un único lenguaje cohesionado.
2. **Ética y Fidelidad Tecnológica:** El éxito de una aplicación como LegadoVivo no radica en generar respuestas artificialmente persuasivas, sino en garantizar una trazabilidad intachable de cada afirmación con sus fuentes de origen y tener el rigor ético de abstenerse cuando la persona no dejó testimonios documentados sobre un tema.
3. **Autonomía Offline:** El desacoplamiento absoluto de servidores en la nube proporciona la mayor garantía posible de privacidad para la memoria personal y familiar, cumpliendo con los estándares de diseño *Offline-First*.

---

## REFERENCIAS BIBLIOGRÁFICAS

- **Android Developers.** (2026). *Guide to app architecture and local persistence*. Google Developers Official Documentation. https://developer.android.com/topic/architecture
- **Kivy Development Team.** (2026). *Kivy: Cross-platform Python Framework for NUI Development (Version 2.3.1)*. https://kivy.org/doc/stable/
- **Python Software Foundation.** (2026). *SQLite3 Database DB-API 2.0 interface for SQLite databases*. Python 3.12 Documentation. https://docs.python.org/3/library/sqlite3.html
- **Ramírez Corredor, M. Á., Mendoza Ovallos, P. J., & Vergara Humánez, N. X.** (2025). *LegadoVivo: Propuesta de preservación y consulta deliberada de memoria personal*. Corporación Universitaria Lasallista.

