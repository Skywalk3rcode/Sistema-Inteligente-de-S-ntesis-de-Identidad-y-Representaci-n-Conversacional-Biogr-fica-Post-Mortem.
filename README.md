# LegadoVivo - Segundo Incremento (Aplicación Móvil Android en Python)

Aplicación móvil orientada a la preservación consciente de recuerdos, reflexiones y valores en cápsulas temáticas, con un motor de consulta determinista fundamentado estrictamente en fuentes autorizadas.

- **Estudiante:** Miguel Ángel Ramírez Corredor  
- **Institución:** Corporación Universitaria Lasallista  
- **Curso:** Aplicaciones Móviles  
- **Versión:** 2.0.0 (Segundo Incremento)  
- **Tecnología Principal:** Python 3.12 + Kivy + SQLite + Buildozer (Android)

---

## 1. Contexto y Objetivos del Segundo Incremento

El proyecto **LegadoVivo** permite a una persona (titular) registrar sus vivencias, principios morales y consejos en cápsulas temáticas. El titular decide de manera granular cuáles registros están autorizados como fuentes para futuras consultas y cuáles permanecen como borradores privados.

### Principios Fundamentales:
1. **Transparencia y No Suplantación:** La aplicación deja explícito en cada consulta que las respuestas son representaciones derivadas del material autorizado, no una comunicación en tiempo real ni asesoramiento médico, jurídico o financiero.
2. **Fidelidad y Abstención Estricta:** El sistema **no inventa respuestas**. Si una consulta no encuentra coincidencia en el archivo aprobado, el sistema se abstiene de manera transparente.
3. **Privacidad Offline-First:** Toda la información se guarda localmente en SQLite sin depender de backend, servicios en la nube ni sincronizaciones externas.

---

## 2. Migración Tecnológica: De Kotlin/Compose a Python/Kivy

El diseño original del primer incremento fue formulado para Android nativo con Kotlin y Jetpack Compose. Para este segundo incremento, el equipo evaluó y aprobó la migración hacia **Python**:
- **Motivación:** Unificar la lógica de recuperación de información, indexación semántica local y desarrollo de interfaz en un único lenguaje de alto nivel.
- **Framework Móvil Seleccionado:** **Kivy** con **Buildozer / python-for-android (p4a)**.
- **Razón de la Elección:** Kivy es un framework touch-native con aceleración por hardware (OpenGL ES), diseñado específicamente para interfaces móviles en Android e iOS. A diferencia de soluciones híbridas web, Kivy ejecuta Python de forma directa en el dispositivo móvil mediante una máquina virtual embebida, garantizando una aplicación Android real.

---

## 3. Funciones Implementadas en el Flujo

1. **Creación de Cápsulas con Validación:**
   - Campos: Título (mínimo 3 caracteres), Tema (selector de categorías) y Contenido (mínimo 10 caracteres).
   - Validación reactiva: rechaza cadenas vacías o solo espacios y muestra mensajes de error claros.
2. **Biblioteca de Cápsulas, Edición y Eliminación:**
   - Tarjetas móviles con insignias visuales de estado (`✓ FUENTE AUTORIZADA` vs `🔒 BORRADOR PRIVADO`).
   - Edición completa de registros existentes.
   - Eliminación segura mediante diálogo modal de confirmación.
3. **Aprobación y Retiro de Fuentes:**
   - Botón directo para alternar la autorización de cada cápsula.
   - Persistencia inmediata del estado en la base de datos SQLite.
4. **Consulta Determinista con Citas y Abstención:**
   - Búsqueda restringida exclusivamente a cápsulas con aprobación activa.
   - Las cápsulas en borrador jamás son consultadas ni expuestas.
   - Cita explícita de referencias y extractos utilizados.
   - **Abstención:** si no hay coincidencias o no hay cápsulas aprobadas, el sistema se abstiene formalmente.
5. **Monitoreo de Conectividad e Integridad Local:**
   - Detección de conectividad (Android native `ConnectivityManager` vía PyJNIus / agnóstico en escritorio).
   - Interruptor interactivo *"Simular Offline"* para verificar la total autonomía sin Internet.
   - Aviso permanente de que la app funciona 100% offline y sin sincronización remota.

---

## 4. Estructura de la Arquitectura (Clean Architecture)

```
legado_vivo/
├── main.py                     # Punto de entrada de la aplicación Kivy
├── config.py                   # Constantes globales, dimensiones móviles y textos legales
├── requirements.txt            # Dependencias del proyecto
├── buildozer.spec              # Especificación para empaquetado de APK en Android
├── models/
│   ├── __init__.py
│   └── capsule.py              # Entidad de dominio Capsule (dataclass)
├── storage/
│   ├── __init__.py
│   └── repository.py           # Repositorio SQLite (CRUD, índices, semillas ficticias)
├── services/
│   ├── __init__.py
│   ├── capsule_service.py      # Lógica de negocio y validación de campos
│   ├── query_engine.py         # Motor de recuperación, citas y abstención estricta
│   └── connectivity_service.py # Monitoreo de conectividad y modo offline
├── ui/
│   ├── __init__.py
│   ├── app_ui.py               # Layout raíz móvil, AppBar, banner de red y BottomNav
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── library_screen.py   # Pantalla de biblioteca con tarjetas y filtros
│   │   ├── form_screen.py      # Pantalla de creación/edición con alertas reactivas
│   │   └── query_screen.py     # Pantalla de consulta con cita de fuentes y abstención
│   └── components/
│       ├── __init__.py
│       └── dialogs.py          # Diálogos modales (confirmación de borrado y aviso ético)
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Pruebas de la entidad
│   ├── test_repository.py      # Pruebas de SQLite, persistencia tras reinicio y CRUD
│   ├── test_capsule_service.py # Pruebas de validación y reglas de negocio
│   ├── test_query_engine.py    # Pruebas de consulta, exclusión de borradores y abstención
│   ├── test_connectivity.py    # Pruebas del servicio de red y simulación offline
│   └── test_ui_smoke.py        # Pruebas de instanciación del árbol de widgets
├── .github/
│   └── workflows/
│       └── build-apk.yml       # Pipeline automatizado de GitHub Actions para generar APK
├── README.md                   # Esta guía
├── INFORME_TECNICO.md          # Informe técnico formal (3-5 páginas)
└── LISTA_CAPTURAS.md           # Guía y lista de capturas requeridas para demostración
```

---

## 5. Requisitos y Pasos de Ejecución

### Requisitos Previos:
- Python 3.10 o superior (verificado y probado en Python 3.12.10).
- `pip` actualizado.

### Paso 1: Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Paso 2: Ejecución de la Suite de Pruebas Automatizadas
Verifica los 18 casos de prueba que certifican la lógica, persistencia SQLite, validación y abstención:
```bash
python -m pytest tests -v
```

### Paso 3: Ejecución de la Aplicación Móvil en Modo Emulado
Al ejecutarse en un entorno de escritorio, Kivy dimensiona automáticamente la ventana a la proporción estándar de un smartphone moderno (412 x 860 px en vertical):
```bash
python main.py
```

---

## 6. Procedimiento para Empaquetar el APK Android (Buildozer)

Buildozer compila el código Python a través de `python-for-android` (p4a), descargando el Android SDK y Android NDK.

> **Nota de Compatibilidad:** Buildozer requiere un entorno Linux nativo o POSIX. En Windows se debe ejecutar a través de **WSL2 (Ubuntu)**, **Docker** o mediante el flujo de integración continua provisto en `.github/workflows/build-apk.yml`.

### Opción A: Compilación en WSL2 / Ubuntu Linux
```bash
# 1. Instalar dependencias del sistema operativo
sudo apt update
sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
    build-essential libsqlite3-dev openjdk-17-jdk

# 2. Instalar Buildozer y Cython
pip install --upgrade buildozer cython virtualenv

# 3. Compilar el APK en modo depuración
buildozer -v android debug
```
El archivo `.apk` resultante se generará en la carpeta `bin/` (ej. `bin/legadovivo-2.0.0-arm64-v8a_armeabi-v7a-debug.apk`).

### Opción B: Compilación Automatizada en GitHub Actions
El proyecto incluye el archivo `.github/workflows/build-apk.yml`. Al realizar `git push` a un repositorio de GitHub, la compilación se ejecuta automáticamente en la nube de GitHub y el archivo APK se descarga desde la sección *Actions > Artifacts*.

### Opción C: Instalación y Ejecución en Dispositivo Android
Conecte el dispositivo Android por USB con la depuración USB habilitada y ejecute:
```bash
buildozer android deploy run logcat
```

---

## 7. Verificación del Entorno y Transparencia Técnica

Conforme al requerimiento de evaluación honesta del entorno:
- **Verificado en el sistema actual:**
  - Intérprete Python: **Python 3.12.10** (operativo).
  - Framework Gráfico: **Kivy 2.3.1** (instalado y probado con backend OpenGL/SDL2).
  - Suite de Pruebas: **18 pruebas unitarias y de integración pasando al 100%** (`tests/`).
  - Base de datos: **SQLite local funcional** con persistencia comprobada tras reinicio.
- **Herramientas de compilación pendientes en la máquina local Windows:**
  - Buildozer no se ejecuta directamente sobre el shell Win32 nativo (requiere Linux/WSL2).
  - WSL no se encuentra instalado actualmente en el host (`wsl --version` reportó no instalado).
  - Android SDK / NDK y `adb` no están configurados en el PATH local.
- **Solución implementada:** Se entregó la configuración exhaustiva `buildozer.spec` y el workflow de GitHub Actions para compilación en la nube sin fricciones, junto con la lista detallada de capturas para la entrega final.

