"""
Configuración global de Pytest para LegadoVivo.
Garantiza que las variables de entorno de Kivy se inicialicen antes de cualquier importación de prueba.
"""

import os
import sys

# Configurar Kivy en modo no interactivo y silencioso para CI/CD
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
