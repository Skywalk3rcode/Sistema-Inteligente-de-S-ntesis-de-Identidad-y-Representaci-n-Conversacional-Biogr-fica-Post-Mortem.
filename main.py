"""
Punto de entrada principal para la aplicación móvil LegadoVivo.
Segundo Incremento: Arquitectura en Python (Kivy) con persistencia local SQLite
y consulta basada estrictamente en fuentes autorizadas.
"""

import sys
import os

# Configuración de dimensiones de pantalla móvil antes de inicializar la ventana Kivy
from kivy.config import Config
from config import MOBILE_WINDOW_WIDTH, MOBILE_WINDOW_HEIGHT, APP_NAME

# En plataformas no móviles (escritorio), configurar viewport para emular smartphone
from kivy.utils import platform

if platform not in ("android", "ios"):
    Config.set("graphics", "width", str(MOBILE_WINDOW_WIDTH))
    Config.set("graphics", "height", str(MOBILE_WINDOW_HEIGHT))
    Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.core.window import Window

from storage.repository import CapsuleRepository
from services.capsule_service import CapsuleService
from services.query_engine import QueryEngine
from services.connectivity_service import ConnectivityService
from ui.app_ui import MainMobileLayout


# NOTA: Window.softinput_mode se configura dentro de build() para garantizar
# que la ventana de Android ya esté completamente inicializada al momento de aplicarlo.


class LegadoVivoApp(App):
    """
    Clase principal de la aplicación móvil LegadoVivo.
    """

    def build(self):
        self.title = f"{APP_NAME} - Preservación de Memoria"

        # Configurar teclado virtual aquí, con la ventana ya inicializada por Kivy
        # (evitar superposición de inputs en Android)
        Window.softinput_mode = "below_target"

        # Icono de aplicación móvil
        if os.path.exists("assets/icon.png"):
            self.icon = "assets/icon.png"
        elif os.path.exists("icon.png"):
            self.icon = "icon.png"

        # Inicialización de la capa de persistencia local (SQLite)
        self.repository = CapsuleRepository()

        # Sembrar datos ficticios de demostración si la base de datos está vacía
        self.repository.seed_initial_data()

        # Inicialización de la capa de lógica de negocio y servicios
        self.capsule_service = CapsuleService(repository=self.repository)
        self.query_engine = QueryEngine(repository=self.repository)
        self.connectivity_service = ConnectivityService()

        # Construir y retornar la jerarquía visual raíz
        self.main_layout = MainMobileLayout(
            capsule_service=self.capsule_service,
            query_engine=self.query_engine,
            connectivity_service=self.connectivity_service
        )

        # Enlazar botón físico y gestos de retroceso en Android (Keycode 27 / Esc)
        Window.bind(on_keyboard=self.on_android_back_button)

        return self.main_layout

    def on_android_back_button(self, window, key, scancode, codepoint, modifier):
        """
        Gestiona el botón físico/gestual de retroceso en Android (keycode 27 / Escape).
        1. Si hay un diálogo modal abierto, lo cierra.
        2. Si el usuario está en Formulario o Consulta, regresa a la Biblioteca.
        3. Si está en la Biblioteca raíz, delega al sistema (minimizar/salir).
        """
        if key == 27:
            # 1. Verificar si hay un diálogo modal abierto
            from kivy.uix.modalview import ModalView
            for child in list(Window.children):
                if isinstance(child, ModalView):
                    child.dismiss()
                    return True

            # 2. Navegar hacia atrás en la jerarquía de pantallas
            if hasattr(self, "main_layout") and hasattr(self.main_layout, "sm"):
                current_screen = self.main_layout.sm.current
                if current_screen in ("form", "query"):
                    self.main_layout.navigate_to_library()
                    return True

            # 3. Retornar False permite la acción nativa de Android (salir o minimizar)
            return False
        return False

    def on_pause(self):
        """Manejo del ciclo de vida en Android: pausar sin destruir estado."""
        return True

    def on_resume(self):
        """Manejo del ciclo de vida en Android: reanudar aplicación."""
        if hasattr(self, "main_layout") and hasattr(self.main_layout, "update_connectivity_status"):
            self.main_layout.update_connectivity_status()


if __name__ == "__main__":
    LegadoVivoApp().run()

