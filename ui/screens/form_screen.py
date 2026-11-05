"""
Pantalla de Creación y Edición de Cápsulas para LegadoVivo.
Incluye validación exhaustiva de campos y retroalimentación reactiva.
"""

from typing import Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import platform
from models.capsule import Capsule
from config import AVAILABLE_TOPICS
from services import photo_service


class FormScreen(Screen):
    """
    Formulario móvil para crear o modificar cápsulas temáticas del legado.
    """

    def __init__(self, capsule_service, on_save_success: Callable[[], None], on_cancel: Callable[[], None], **kwargs):
        super().__init__(**kwargs)
        self.service = capsule_service
        self.on_save_success = on_save_success
        self.on_cancel = on_cancel
        self.editing_capsule: Optional[Capsule] = None
        # Ruta de la foto pendiente de guardar (None = sin foto nueva)
        self._pending_photo_path: Optional[str] = None
        # True si el usuario pulsó "Quitar Foto" para eliminar la foto actual
        self._pending_clear_photo: bool = False

        main_box = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(16), dp(12), dp(16), dp(12)])

        # Encabezado del Formulario
        self.header_lbl = Label(
            text="Nueva Cápsula de Legado",
            font_size="20sp",
            bold=True,
            color=[0.1, 0.15, 0.25, 1],
            size_hint_y=None,
            height=dp(32),
            halign="left",
            valign="middle"
        )
        self.header_lbl.bind(size=self.header_lbl.setter("text_size"))
        main_box.add_widget(self.header_lbl)

        # Banner reactivo de Validación / Error
        self.feedback_banner = Label(
            text="",
            font_size="13sp",
            bold=True,
            color=[0.85, 0.15, 0.15, 1],
            size_hint_y=None,
            height=0,
            halign="left",
            valign="middle"
        )
        self.feedback_banner.bind(size=self.feedback_banner.setter("text_size"))
        main_box.add_widget(self.feedback_banner)

        # Formulario deslizable
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        form_content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[0, dp(4), 0, dp(16)])
        form_content.bind(minimum_height=form_content.setter("height"))

        # Campo: Título
        lbl_title = Label(
            text="Título de la cápsula *",
            font_size="14sp",
            bold=True,
            color=[0.2, 0.25, 0.3, 1],
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )
        lbl_title.bind(size=lbl_title.setter("text_size"))
        form_content.add_widget(lbl_title)

        self.txt_title = TextInput(
            hint_text="Ej: La honestidad en el trabajo familiar",
            multiline=False,
            font_size="15sp",
            size_hint_y=None,
            height=dp(44),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_content.add_widget(self.txt_title)

        # Campo: Tema o Categoría
        lbl_topic = Label(
            text="Tema o categoría *",
            font_size="14sp",
            bold=True,
            color=[0.2, 0.25, 0.3, 1],
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )
        lbl_topic.bind(size=lbl_topic.setter("text_size"))
        form_content.add_widget(lbl_topic)

        self.spinner_topic = Spinner(
            text=AVAILABLE_TOPICS[0],
            values=AVAILABLE_TOPICS,
            font_size="14sp",
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_color=[0.92, 0.94, 0.97, 1],
            color=[0.15, 0.2, 0.3, 1]
        )
        form_content.add_widget(self.spinner_topic)

        # Campo: Contenido
        lbl_content = Label(
            text="Contenido del recuerdo o valor * (mínimo 10 caracteres)",
            font_size="14sp",
            bold=True,
            color=[0.2, 0.25, 0.3, 1],
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )
        lbl_content.bind(size=lbl_content.setter("text_size"))
        form_content.add_widget(lbl_content)

        self.txt_content = TextInput(
            hint_text="Describe aquí la vivencia, anécdota, enseñanza o principio ético que deseas preservar en este legado...",
            multiline=True,
            font_size="14sp",
            size_hint_y=None,
            height=dp(140),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_content.add_widget(self.txt_content)

        # Fila: Switch de Aprobación Inmediata
        approval_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(10))
        lbl_switch = Label(
            text="Aprobar inmediatamente como fuente autorizada",
            font_size="13sp",
            color=[0.15, 0.2, 0.25, 1],
            halign="left",
            valign="middle"
        )
        lbl_switch.bind(size=lbl_switch.setter("text_size"))
        approval_row.add_widget(lbl_switch)

        self.switch_approved = Switch(active=True, size_hint=(None, 1), width=dp(65))
        approval_row.add_widget(self.switch_approved)
        form_content.add_widget(approval_row)

        lbl_switch_hint = Label(
            text="Las cápsulas aprobadas son las únicas que responderán a consultas del legado.",
            font_size="11sp",
            color=[0.5, 0.55, 0.6, 1],
            size_hint_y=None,
            height=dp(18),
            halign="left"
        )
        lbl_switch_hint.bind(size=lbl_switch_hint.setter("text_size"))
        form_content.add_widget(lbl_switch_hint)

        # ── Sección: Fotografía de Recuerdo ──────────────────────────────────────
        lbl_photo_section = Label(
            text="Fotografía de Recuerdo (opcional)",
            font_size="14sp",
            bold=True,
            color=[0.2, 0.25, 0.3, 1],
            size_hint_y=None,
            height=dp(22),
            halign="left"
        )
        lbl_photo_section.bind(size=lbl_photo_section.setter("text_size"))
        form_content.add_widget(lbl_photo_section)

        # Contenedor de la sección de foto (fondo sutil)
        self.photo_section_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),   # Se expande a dp(240) cuando hay foto
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(4)]
        )

        # Miniatura de la imagen seleccionada (oculta hasta que haya foto)
        self.photo_preview = Image(
            source="",
            size_hint=(1, None),
            height=dp(0),    # Se expande a dp(180) cuando hay foto
            fit_mode="contain",
            allow_stretch=True
        )
        self.photo_section_box.add_widget(self.photo_preview)

        # Fila de botones de cámara
        photo_btns_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8)
        )

        # El texto del botón se adapta según la plataforma
        cam_label = (
            "\U0001f4f7  Tomar Foto"
            if platform in ("android", "ios")
            else "\U0001f5bc  Seleccionar Imagen"
        )
        self.btn_camera = Button(
            text=cam_label,
            font_size="13sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.38, 0.72, 1],
            color=[1, 1, 1, 1],
            size_hint_x=0.65
        )
        self.btn_camera.bind(on_release=self._on_camera_pressed)
        photo_btns_row.add_widget(self.btn_camera)

        self.btn_clear_photo = Button(
            text="\U0001f5d1  Quitar",
            font_size="12sp",
            background_normal="",
            background_color=[1, 0.9, 0.9, 1],
            color=[0.8, 0.15, 0.15, 1],
            size_hint_x=0.35,
            opacity=0,       # Oculto hasta que haya foto
            disabled=True
        )
        self.btn_clear_photo.bind(on_release=self._on_clear_photo)
        photo_btns_row.add_widget(self.btn_clear_photo)

        self.photo_section_box.add_widget(photo_btns_row)
        form_content.add_widget(self.photo_section_box)

        # Botones de Acción
        actions_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(140), padding=[0, dp(10), 0, 0])

        btn_save = Button(
            text="Guardar Cápsula",
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.45, 0.78, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=dp(46)
        )
        btn_save.bind(on_release=self.save_capsule)
        actions_box.add_widget(btn_save)

        btn_cancel = Button(
            text="Cancelar / Volver",
            font_size="14sp",
            background_normal="",
            background_color=[0.9, 0.92, 0.95, 1],
            color=[0.25, 0.3, 0.35, 1],
            size_hint_y=None,
            height=dp(40)
        )
        btn_cancel.bind(on_release=lambda x: self.on_cancel())
        actions_box.add_widget(btn_cancel)

        btn_clear = Button(
            text="Limpiar Formulario",
            font_size="12sp",
            background_normal="",
            background_color=[1, 1, 1, 0],
            color=[0.45, 0.5, 0.55, 1],
            size_hint_y=None,
            height=dp(30)
        )
        btn_clear.bind(on_release=lambda x: self.clear_fields())
        actions_box.add_widget(btn_clear)

        form_content.add_widget(actions_box)
        scroll.add_widget(form_content)
        main_box.add_widget(scroll)

        self.add_widget(main_box)

    def load_capsule(self, capsule: Optional[Capsule]):
        """Carga una cápsula para edición o restablece para nueva creación."""
        self.clear_feedback()
        self.editing_capsule = capsule
        self._pending_photo_path = None
        self._pending_clear_photo = False
        if capsule:
            self.header_lbl.text = f"Editar Cápsula #{capsule.id}"
            self.txt_title.text = capsule.title
            self.spinner_topic.text = capsule.topic if capsule.topic in AVAILABLE_TOPICS else AVAILABLE_TOPICS[0]
            self.txt_content.text = capsule.content
            self.switch_approved.active = capsule.is_approved
            # Cargar foto existente si la tiene
            self._show_photo_preview(capsule.photo_path)
        else:
            self.header_lbl.text = "Nueva Cápsula de Legado"
            self.clear_fields()

    def clear_fields(self):
        """Limpia los campos del formulario."""
        self.txt_title.text = ""
        self.spinner_topic.text = AVAILABLE_TOPICS[0]
        self.txt_content.text = ""
        self.switch_approved.active = True
        self._pending_photo_path = None
        self._pending_clear_photo = False
        self._show_photo_preview(None)
        self.clear_feedback()

    def _show_photo_preview(self, path: Optional[str]) -> None:
        """Actualiza la miniatura de la foto y la visibilidad del botón 'Quitar'."""
        import os
        has_photo = bool(path and os.path.isfile(path))

        if has_photo:
            self.photo_preview.source = path
            self.photo_preview.height = dp(180)
            self.photo_section_box.height = dp(240)
            self.btn_clear_photo.opacity = 1
            self.btn_clear_photo.disabled = False
        else:
            self.photo_preview.source = ""
            self.photo_preview.height = dp(0)
            self.photo_section_box.height = dp(56)
            self.btn_clear_photo.opacity = 0
            self.btn_clear_photo.disabled = True

    def _on_camera_pressed(self, instance) -> None:
        """Inicia la captura de foto mediante el PhotoService."""
        self.btn_camera.text = "Abriendo..."
        self.btn_camera.disabled = True

        def _on_photo_complete(final_path: Optional[str]) -> None:
            # Restaurar botón
            cam_label = (
                "\U0001f4f7  Tomar Foto"
                if platform in ("android", "ios")
                else "\U0001f5bc  Seleccionar Imagen"
            )
            self.btn_camera.text = cam_label
            self.btn_camera.disabled = False

            if final_path:
                self._pending_photo_path = final_path
                self._pending_clear_photo = False
                self._show_photo_preview(final_path)

        photo_service.capture_photo(on_complete=_on_photo_complete)

    def _on_clear_photo(self, instance) -> None:
        """Marca la foto para ser eliminada al guardar."""
        self._pending_photo_path = None
        self._pending_clear_photo = True
        self._show_photo_preview(None)

    def show_error(self, message: str):
        """Muestra un mensaje de error en el banner."""
        self.feedback_banner.text = f"Atención: {message}"
        self.feedback_banner.color = [0.85, 0.15, 0.15, 1]
        self.feedback_banner.height = dp(32)

    def clear_feedback(self):
        """Oculta el banner de validación."""
        self.feedback_banner.text = ""
        self.feedback_banner.height = 0

    def save_capsule(self, instance):
        """Ejecuta la validación y persiste la cápsula."""
        title = self.txt_title.text
        topic = self.spinner_topic.text
        content = self.txt_content.text
        is_approved = self.switch_approved.active

        if self.editing_capsule and self.editing_capsule.id:
            # Modo Actualización
            success, msg, _ = self.service.update_capsule(
                capsule_id=self.editing_capsule.id,
                title=title,
                topic=topic,
                content=content,
                is_approved=is_approved,
                photo_path=self._pending_photo_path,
                clear_photo=self._pending_clear_photo
            )
        else:
            # Modo Creación
            success, msg, _ = self.service.create_capsule(
                title=title,
                topic=topic,
                content=content,
                is_approved=is_approved,
                photo_path=self._pending_photo_path
            )

        if not success:
            self.show_error(msg)
        else:
            self.clear_fields()
            self.on_save_success()

