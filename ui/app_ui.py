"""
Contenedor principal de interfaz de usuario para LegadoVivo.
Integra la barra de estado superior, el gestor de pantallas y la barra de navegación móvil.
"""

from typing import Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp

from ui.screens.library_screen import LibraryScreen
from ui.screens.form_screen import FormScreen
from ui.screens.query_screen import QueryScreen
from ui.components.dialogs import DisclaimerInfoDialog
from config import APP_NAME, OFFLINE_NOTICE


class MainMobileLayout(BoxLayout):
    """
    Layout raíz de la aplicación móvil LegadoVivo.
    Coordina la barra de navegación inferior, barra superior y transición entre pantallas.
    """

    def __init__(self, capsule_service, query_engine, connectivity_service, **kwargs):
        super().__init__(**kwargs)
        self.service = capsule_service
        self.engine = query_engine
        self.connectivity = connectivity_service

        self.orientation = "vertical"

        # Fondo general de la app (gris claro suave estilo Android Slate 50)
        with self.canvas.before:
            Color(0.96, 0.97, 0.98, 1)
            # Inicializar con size=(0,0): los bindings de abajo actualizarán al tamaño real
            # en el primer evento de resize. Esto evita el artefacto visual en Android
            # donde el canvas se renderiza ANTES de que el layout haya asignado tamaños.
            self.bg_rect = Rectangle(size=(0, 0), pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # 1. Barra de Aplicación Superior (Top AppBar)
        self._build_top_bar()

        # 2. Barra Informativa de Conectividad y Privacidad Local
        self._build_connectivity_banner()

        # 3. Gestor de Pantallas (ScreenManager)
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))

        self.screen_library = LibraryScreen(
            capsule_service=self.service,
            on_navigate_form=self.navigate_to_form,
            name="library"
        )
        self.screen_form = FormScreen(
            capsule_service=self.service,
            on_save_success=self.on_form_save_success,
            on_cancel=self.navigate_to_library,
            name="form"
        )
        self.screen_query = QueryScreen(
            query_engine=self.engine,
            name="query"
        )

        self.sm.add_widget(self.screen_library)
        self.sm.add_widget(self.screen_form)
        self.sm.add_widget(self.screen_query)

        self.add_widget(self.sm)

        # 4. Barra de Navegación Inferior (Bottom Navigation)
        self._build_bottom_nav()

        # Programar verificación periódica de conectividad cada 3 segundos
        Clock.schedule_interval(lambda dt: self.update_connectivity_status(), 3.0)
        # Actualización inicial inmediata
        Clock.schedule_once(lambda dt: self.update_connectivity_status(), 0.1)
        # Forzar un pase de layout en el primer frame para garantizar que todos
        # los widgets reciban sus tamaños y posiciones correctas en Android.
        # En escritorio esto es un no-op seguro; en Android evita el bug de (0,0).
        Clock.schedule_once(self._force_layout, 0)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _force_layout(self, dt):
        """Fuerza la propagación de tamaño y posición en el primer frame.
        Crítico en Android: el motor de layout puede no emitir un evento 'size'
        antes del primer render si el widget raíz recibe su tamaño desde la JVM.
        Al disparar size/pos manualmente, todos los callbacks de canvas.before
        se ejecutan con los valores reales de la ventana.
        """
        self._update_bg(self, self.size)
        for child in self.children:
            # Disparar actualización de tamaño en hijos directos para propagar
            if hasattr(child, 'size'):
                child._trigger_layout()

    def _build_top_bar(self):
        """Construye la barra superior con identidad visual y botón de información ética."""
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(10)
        )
        with top_bar.canvas.before:
            Color(0.1, 0.22, 0.45, 1)  # Azul Índigo Profundo
            # size=(0,0): los bindings actualizarán en el primer evento de tamaño
            self.top_rect = Rectangle(size=(0, 0), pos=top_bar.pos)
        top_bar.bind(
            size=lambda inst, v: setattr(self.top_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.top_rect, "pos", inst.pos)
        )

        title_box = BoxLayout(orientation="vertical")
        app_title = Label(
            text=APP_NAME,
            font_size="18sp",
            bold=True,
            color=[1, 1, 1, 1],
            halign="left"
        )
        app_title.bind(size=app_title.setter("text_size"))

        sub_title = Label(
            text="Preservación de Memoria y Valores",
            font_size="10.5sp",
            color=[0.8, 0.88, 1.0, 1],
            halign="left"
        )
        sub_title.bind(size=sub_title.setter("text_size"))

        title_box.add_widget(app_title)
        title_box.add_widget(sub_title)
        top_bar.add_widget(title_box)

        # Botón para desplegar marco ético y aviso de representación
        btn_info = Button(
            text="Ética",
            font_size="12sp",
            bold=True,
            background_normal="",
            background_color=[0.18, 0.35, 0.65, 1],
            color=[1, 1, 1, 1],
            size_hint=(None, None),
            size=(dp(76), dp(36))
        )
        btn_info.bind(on_release=lambda x: DisclaimerInfoDialog().open())
        top_bar.add_widget(btn_info)

        self.add_widget(top_bar)

    def _build_connectivity_banner(self):
        """Construye la barra indicadora de estado de red y modo local autónomo."""
        self.banner_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(34),
            padding=[dp(14), dp(4), dp(14), dp(4)],
            spacing=dp(8)
        )
        with self.banner_box.canvas.before:
            self.banner_color = Color(0.92, 0.96, 0.92, 1)
            # size=(0,0): los bindings actualizarán en el primer evento de tamaño
            self.banner_rect = Rectangle(size=(0, 0), pos=self.banner_box.pos)
        self.banner_box.bind(
            size=lambda inst, v: setattr(self.banner_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.banner_rect, "pos", inst.pos)
        )

        self.lbl_conn_status = Label(
            text="Comprobando conectividad...",
            font_size="11.5sp",
            bold=True,
            color=[0.1, 0.45, 0.2, 1],
            halign="left",
            valign="middle"
        )
        self.lbl_conn_status.bind(size=self.lbl_conn_status.setter("text_size"))
        self.banner_box.add_widget(self.lbl_conn_status)

        # Botón para alternar simulación de desconexión (Demostración y verificación)
        self.btn_toggle_sim = Button(
            text="Simular Offline",
            font_size="10.5sp",
            background_normal="",
            background_color=[0.85, 0.88, 0.92, 1],
            color=[0.2, 0.25, 0.35, 1],
            size_hint=(None, 1),
            width=dp(115)
        )
        self.btn_toggle_sim.bind(on_release=self.toggle_offline_simulation)
        self.banner_box.add_widget(self.btn_toggle_sim)

        self.add_widget(self.banner_box)

    def _build_bottom_nav(self):
        """Construye la barra inferior de navegación por pestañas móviles."""
        nav_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(62),
            padding=[dp(12), dp(6), dp(12), dp(6)],
            spacing=dp(8)
        )
        with nav_box.canvas.before:
            Color(1, 1, 1, 1)  # Blanco puro
            # size=(0,0): los bindings actualizarán en el primer evento de tamaño
            self.nav_rect = Rectangle(size=(0, 0), pos=nav_box.pos)
        nav_box.bind(
            size=lambda inst, v: setattr(self.nav_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.nav_rect, "pos", inst.pos)
        )

        self.btn_nav_library = Button(
            text="Biblioteca",
            font_size="13.5sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.38, 0.72, 1],
            color=[1, 1, 1, 1]
        )
        self.btn_nav_library.bind(on_release=lambda x: self.navigate_to_library())

        self.btn_nav_form = Button(
            text="+ Nueva",
            font_size="13.5sp",
            background_normal="",
            background_color=[0.94, 0.95, 0.97, 1],
            color=[0.3, 0.35, 0.45, 1]
        )
        self.btn_nav_form.bind(on_release=lambda x: self.navigate_to_form(None))

        self.btn_nav_query = Button(
            text="Consultar",
            font_size="13.5sp",
            background_normal="",
            background_color=[0.94, 0.95, 0.97, 1],
            color=[0.3, 0.35, 0.45, 1]
        )
        self.btn_nav_query.bind(on_release=lambda x: self.navigate_to_query())

        nav_box.add_widget(self.btn_nav_library)
        nav_box.add_widget(self.btn_nav_form)
        nav_box.add_widget(self.btn_nav_query)

        self.add_widget(nav_box)

    def update_connectivity_status(self):
        """Actualiza el texto y colores de la barra de conectividad."""
        summary = self.connectivity.get_status_summary()
        is_conn = summary["is_connected"]
        is_sim = summary["is_simulated"]

        if is_conn:
            self.banner_color.rgba = [0.92, 0.97, 0.92, 1]  # Verde claro suave
            self.lbl_conn_status.color = [0.08, 0.48, 0.2, 1]
            self.lbl_conn_status.text = "• En línea • Modo local autónomo (Sin sincronización externa)"
            self.btn_toggle_sim.text = "Simular Offline"
            self.btn_toggle_sim.background_color = [0.9, 0.92, 0.95, 1]
        else:
            self.banner_color.rgba = [0.98, 0.94, 0.9, 1]  # Ámbar suave
            self.lbl_conn_status.color = [0.75, 0.4, 0.05, 1]
            sim_str = " (Simulado)" if is_sim else ""
            self.lbl_conn_status.text = f"• Sin conexión{sim_str} • Operación 100% local activa"
            self.btn_toggle_sim.text = "Restaurar Red"
            self.btn_toggle_sim.background_color = [0.98, 0.88, 0.8, 1]

    def toggle_offline_simulation(self, instance):
        """Alterna el modo simulado de desconexión."""
        self.connectivity.toggle_simulation()
        self.update_connectivity_status()

    def _set_active_nav_button(self, active_name: str):
        """Actualiza los estilos visuales de la barra de navegación según la pantalla activa."""
        active_bg = [0.12, 0.38, 0.72, 1]
        active_fg = [1, 1, 1, 1]
        inactive_bg = [0.94, 0.95, 0.97, 1]
        inactive_fg = [0.3, 0.35, 0.45, 1]

        self.btn_nav_library.background_color = active_bg if active_name == "library" else inactive_bg
        self.btn_nav_library.color = active_fg if active_name == "library" else inactive_fg

        self.btn_nav_form.background_color = active_bg if active_name == "form" else inactive_bg
        self.btn_nav_form.color = active_fg if active_name == "form" else inactive_fg

        self.btn_nav_query.background_color = active_bg if active_name == "query" else inactive_bg
        self.btn_nav_query.color = active_fg if active_name == "query" else inactive_fg

    def navigate_to_library(self):
        """Navega hacia la biblioteca."""
        self.sm.transition.direction = "right"
        self.sm.current = "library"
        self._set_active_nav_button("library")

    def navigate_to_form(self, capsule: Optional[object] = None):
        """Navega hacia el formulario (nuevo o editar)."""
        self.screen_form.load_capsule(capsule)
        self.sm.transition.direction = "left" if self.sm.current == "library" else "right"
        self.sm.current = "form"
        self._set_active_nav_button("form")

    def navigate_to_query(self):
        """Navega hacia la pantalla de consulta."""
        self.sm.transition.direction = "left"
        self.sm.current = "query"
        self._set_active_nav_button("query")

    def on_form_save_success(self):
        """Retorna a la biblioteca tras guardar una cápsula exitosamente."""
        self.navigate_to_library()

