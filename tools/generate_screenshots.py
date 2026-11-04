"""
Script de generación automatizada de capturas visuales de escritorio para LegadoVivo.
Utiliza Window.screenshot de Kivy para registrar evidencia del flujo de interfaz.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import MOBILE_WINDOW_WIDTH, MOBILE_WINDOW_HEIGHT
from kivy.config import Config
Config.set("graphics", "width", str(MOBILE_WINDOW_WIDTH))
Config.set("graphics", "height", str(MOBILE_WINDOW_HEIGHT))
Config.set("graphics", "resizable", "0")

from kivy.clock import Clock
from kivy.core.window import Window
from main import LegadoVivoApp

OUTPUT_DIR = ROOT / "docs" / "capturas_desktop"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ScreenshotApp(LegadoVivoApp):
    def on_start(self):
        super().on_start()
        layout = self.root

        # 1. Captura de Inicio / Conectividad en Biblioteca (dar 3s para inicio y buffer swap de OpenGL)
        Clock.schedule_once(lambda dt: self._shot("01_inicio_conectividad"), 3.0)

        # 2. Captura de Formulario con Validación de Error
        Clock.schedule_once(lambda dt: layout.navigate_to_form(None), 4.0)
        Clock.schedule_once(lambda dt: self._trigger_validation_error(layout), 4.5)
        Clock.schedule_once(lambda dt: self._shot("02_formulario_validacion"), 5.5)

        # 3. Captura de Biblioteca con tarjetas
        Clock.schedule_once(lambda dt: layout.navigate_to_library(), 6.5)
        Clock.schedule_once(lambda dt: self._shot("03_biblioteca_capsulas"), 7.5)

        # 4. Captura de Consulta con Fuente Aprobada
        Clock.schedule_once(lambda dt: layout.navigate_to_query(), 8.5)
        Clock.schedule_once(lambda dt: layout.screen_query.quick_search("honestidad"), 9.0)
        Clock.schedule_once(lambda dt: self._shot("04_consulta_con_fuente"), 10.0)

        # 5. Captura de Consulta con Abstención Estricta
        Clock.schedule_once(lambda dt: layout.screen_query.quick_search("viaje a Marte y física cuántica"), 11.0)
        Clock.schedule_once(lambda dt: self._shot("05_abstencion_estricta"), 12.0)

        # 6. Captura de Modo Offline (Sin Conexión)
        Clock.schedule_once(lambda dt: layout.toggle_offline_simulation(None), 13.0)
        Clock.schedule_once(lambda dt: layout.navigate_to_library(), 13.5)
        Clock.schedule_once(lambda dt: self._shot("06_modo_offline"), 14.5)

        # 7. Finalizar ejecución
        Clock.schedule_once(lambda dt: self.stop(), 15.5)

    def _trigger_validation_error(self, layout):
        layout.screen_form.txt_title.text = ""
        layout.screen_form.txt_content.text = ""
        layout.screen_form.save_capsule(None)

    def _shot(self, name: str):
        shot_path = Window.screenshot(name=str(OUTPUT_DIR / f"{name}.png"))
        target = OUTPUT_DIR / f"{name}.png"
        if Path(shot_path) != target:
            if target.exists():
                target.unlink()
            Path(shot_path).replace(target)
        print(f"[CAPTURA REGISTRADA] {target}")


if __name__ == "__main__":
    ScreenshotApp().run()
