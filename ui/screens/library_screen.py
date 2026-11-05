"""
Pantalla de Biblioteca de Cápsulas para LegadoVivo.
Permite explorar, filtrar, autorizar, editar y eliminar cápsulas de memoria.
"""

from typing import Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from models.capsule import Capsule
from ui.components.dialogs import ConfirmDeleteDialog


class CapsuleCard(BoxLayout):
    """
    Tarjeta visual para representar una cápsula individual en la biblioteca móvil.
    """

    def __init__(
        self,
        capsule: Capsule,
        on_toggle_approval: Callable[[int], None],
        on_edit: Callable[[Capsule], None],
        on_delete: Callable[[Capsule], None],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.capsule = capsule
        self.on_toggle_approval = on_toggle_approval
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.spacing = dp(8)

        # Vincular altura dinámica para adaptarse al contenido en cualquier densidad de pantalla
        self.bind(minimum_height=self.setter("height"))

        # Fondo de tarjeta tipo Material con bordes redondeados
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Blanco puro
            # size=(0,0): el binding bind(size=...) actualiza al tamaño real en el primer frame.
            # Patrón requerido en Android donde el canvas se renderiza antes del layout pass.
            self.bg_rect = RoundedRectangle(size=(0, 0), pos=self.pos, radius=[dp(12)])
        self.bind(size=self._update_bg, pos=self._update_bg)

        # ── Miniatura de fotografía (visible solo si la cápsula tiene foto) ─────────
        import os
        has_photo = bool(capsule.photo_path and os.path.isfile(str(capsule.photo_path)))
        if has_photo:
            photo_thumb = Image(
                source=capsule.photo_path,
                size_hint=(1, None),
                height=dp(140),
                fit_mode="cover",
                allow_stretch=True
            )
            self.add_widget(photo_thumb)

        # Fila superior: Tema y Estado de Aprobación
        header_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26), spacing=dp(8))

        # Pill de Tema
        topic_pill = Label(
            text=f" {capsule.topic} ",
            font_size="10.5sp",
            bold=True,
            color=[0.12, 0.25, 0.55, 1],
            size_hint=(None, 1),
            width=dp(150),
            halign="center",
            valign="middle"
        )
        with topic_pill.canvas.before:
            Color(0.88, 0.93, 1.0, 1)  # Azul claro
            # size=(0,0): el binding topic_pill.bind actualiza al tamaño real
            self.pill_rect = RoundedRectangle(size=(0, 0), pos=topic_pill.pos, radius=[dp(6)])
        topic_pill.bind(size=self._update_pill, pos=self._update_pill)
        topic_pill.bind(size=topic_pill.setter("text_size"))
        header_row.add_widget(topic_pill)

        header_row.add_widget(BoxLayout())  # Espaciador flexible

        # Badge de Aprobación
        status_text = "FUENTE AUTORIZADA" if capsule.is_approved else "BORRADOR PRIVADO"
        badge_bg_color = (0.1, 0.65, 0.3, 0.15) if capsule.is_approved else (0.8, 0.5, 0.1, 0.15)
        badge_fg_color = [0.08, 0.52, 0.24, 1] if capsule.is_approved else [0.75, 0.42, 0.05, 1]

        status_badge = Label(
            text=f" {status_text} ",
            font_size="10sp",
            bold=True,
            color=badge_fg_color,
            size_hint=(None, 1),
            width=dp(150),
            halign="center",
            valign="middle"
        )
        with status_badge.canvas.before:
            Color(*badge_bg_color)
            # size=(0,0): el binding status_badge.bind actualiza al tamaño real
            self.badge_rect = RoundedRectangle(size=(0, 0), pos=status_badge.pos, radius=[dp(6)])
        status_badge.bind(size=self._update_badge, pos=self._update_badge)
        status_badge.bind(size=status_badge.setter("text_size"))
        header_row.add_widget(status_badge)

        self.add_widget(header_row)

        # Título de la cápsula
        title_lbl = Label(
            text=capsule.title,
            font_size="16sp",
            bold=True,
            color=[0.1, 0.15, 0.22, 1],
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))
        self.add_widget(title_lbl)

        # Extracto del contenido
        raw_content = capsule.content.strip()
        excerpt = raw_content if len(raw_content) <= 150 else raw_content[:147] + "..."
        content_lbl = Label(
            text=excerpt,
            font_size="13sp",
            color=[0.3, 0.35, 0.4, 1],
            size_hint_y=None,
            height=dp(54),
            halign="left",
            valign="top"
        )
        content_lbl.bind(size=content_lbl.setter("text_size"))
        self.add_widget(content_lbl)

        # Fecha y referencia ID
        meta_lbl = Label(
            text=f"Ref #{capsule.id} • Modificado: {capsule.updated_at}",
            font_size="10.5sp",
            color=[0.55, 0.6, 0.65, 1],
            size_hint_y=None,
            height=dp(16),
            halign="left"
        )
        meta_lbl.bind(size=meta_lbl.setter("text_size"))
        self.add_widget(meta_lbl)

        # Fila de acciones (Botones móviles)
        actions_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(8),
            padding=[0, dp(4), 0, 0]
        )

        # Botón Toggle Aprobación
        toggle_text = "Retirar Fuente" if capsule.is_approved else "Aprobar Fuente"
        toggle_bg = [0.85, 0.9, 0.95, 1] if capsule.is_approved else [0.12, 0.55, 0.35, 1]
        toggle_fg = [0.15, 0.3, 0.5, 1] if capsule.is_approved else [1, 1, 1, 1]

        btn_toggle = Button(
            text=toggle_text,
            font_size="12sp",
            bold=True,
            background_normal="",
            background_color=toggle_bg,
            color=toggle_fg,
            size_hint_x=0.45
        )
        btn_toggle.bind(on_release=lambda x: self.on_toggle_approval(capsule.id))
        actions_row.add_widget(btn_toggle)

        # Botón Editar
        btn_edit = Button(
            text="Editar",
            font_size="12sp",
            background_normal="",
            background_color=[0.92, 0.94, 0.96, 1],
            color=[0.15, 0.2, 0.3, 1],
            size_hint_x=0.28
        )
        btn_edit.bind(on_release=lambda x: self.on_edit(self.capsule))
        actions_row.add_widget(btn_edit)

        # Botón Eliminar
        btn_delete = Button(
            text="Eliminar",
            font_size="12sp",
            background_normal="",
            background_color=[1, 0.9, 0.9, 1],
            color=[0.8, 0.15, 0.15, 1],
            size_hint_x=0.27
        )
        btn_delete.bind(on_release=lambda x: self.on_delete(self.capsule))
        actions_row.add_widget(btn_delete)

        self.add_widget(actions_row)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_pill(self, instance, value):
        self.pill_rect.pos = instance.pos
        self.pill_rect.size = instance.size

    def _update_badge(self, instance, value):
        self.badge_rect.pos = instance.pos
        self.badge_rect.size = instance.size


class LibraryScreen(Screen):
    """
    Pantalla principal con el listado de cápsulas registradas y opciones de filtrado.
    """

    def __init__(self, capsule_service, on_navigate_form, **kwargs):
        super().__init__(**kwargs)
        self.service = capsule_service
        self.on_navigate_form = on_navigate_form
        self.current_filter = "all"  # 'all', 'approved', 'draft'

        main_layout = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(12), dp(10), dp(12), dp(10)])

        # Barra de control superior con filtros y botón nueva cápsula
        controls_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(84), spacing=dp(6))

        header_title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        lbl_screen = Label(
            text="Biblioteca de Cápsulas",
            font_size="20sp",
            bold=True,
            color=[0.1, 0.15, 0.25, 1],
            halign="left",
            valign="middle"
        )
        lbl_screen.bind(size=lbl_screen.setter("text_size"))
        header_title_row.add_widget(lbl_screen)

        btn_new = Button(
            text="+ Nueva",
            font_size="13sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.38, 0.72, 1],
            color=[1, 1, 1, 1],
            size_hint=(None, 1),
            width=dp(90)
        )
        btn_new.bind(on_release=lambda x: self.on_navigate_form(None))
        header_title_row.add_widget(btn_new)
        controls_box.add_widget(header_title_row)

        # Fila de Chips de Filtro
        filter_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36), spacing=dp(6))

        self.btn_filter_all = Button(
            text="Todas",
            font_size="12sp",
            bold=True,
            background_normal="",
            background_color=[0.15, 0.4, 0.75, 1],
            color=[1, 1, 1, 1]
        )
        self.btn_filter_all.bind(on_release=lambda x: self.set_filter("all"))

        self.btn_filter_approved = Button(
            text="Solo Fuentes",
            font_size="12sp",
            background_normal="",
            background_color=[0.9, 0.92, 0.95, 1],
            color=[0.2, 0.25, 0.35, 1]
        )
        self.btn_filter_approved.bind(on_release=lambda x: self.set_filter("approved"))

        self.btn_filter_drafts = Button(
            text="Solo Borradores",
            font_size="12sp",
            background_normal="",
            background_color=[0.9, 0.92, 0.95, 1],
            color=[0.2, 0.25, 0.35, 1]
        )
        self.btn_filter_drafts.bind(on_release=lambda x: self.set_filter("draft"))

        filter_row.add_widget(self.btn_filter_all)
        filter_row.add_widget(self.btn_filter_approved)
        filter_row.add_widget(self.btn_filter_drafts)
        controls_box.add_widget(filter_row)

        main_layout.add_widget(controls_box)

        # Contador de resumen
        self.summary_lbl = Label(
            text="Cargando biblioteca...",
            font_size="12sp",
            color=[0.45, 0.5, 0.55, 1],
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )
        self.summary_lbl.bind(size=self.summary_lbl.setter("text_size"))
        main_layout.add_widget(self.summary_lbl)

        # Área de desplazamiento para la lista de cápsulas
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.cards_container = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(4), 0, dp(12)]
        )
        self.cards_container.bind(minimum_height=self.cards_container.setter("height"))
        self.scroll.add_widget(self.cards_container)
        main_layout.add_widget(self.scroll)

        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        """Se ejecuta al entrar a la pantalla: recarga la lista desde SQLite."""
        self.refresh_capsules()

    def set_filter(self, filter_type: str):
        """Aplica un filtro de visualización a la biblioteca."""
        self.current_filter = filter_type

        # Estilo visual de los botones de filtro
        active_bg = [0.15, 0.4, 0.75, 1]
        active_fg = [1, 1, 1, 1]
        inactive_bg = [0.9, 0.92, 0.95, 1]
        inactive_fg = [0.2, 0.25, 0.35, 1]

        self.btn_filter_all.background_color = active_bg if filter_type == "all" else inactive_bg
        self.btn_filter_all.color = active_fg if filter_type == "all" else inactive_fg

        self.btn_filter_approved.background_color = active_bg if filter_type == "approved" else inactive_bg
        self.btn_filter_approved.color = active_fg if filter_type == "approved" else inactive_fg

        self.btn_filter_drafts.background_color = active_bg if filter_type == "draft" else inactive_bg
        self.btn_filter_drafts.color = active_fg if filter_type == "draft" else inactive_fg

        self.refresh_capsules()

    def refresh_capsules(self):
        """Lee los registros más recientes de SQLite y actualiza el árbol de widgets."""
        self.cards_container.clear_widgets()
        all_capsules = self.service.list_capsules()
        total_count = len(all_capsules)
        approved_count = sum(1 for c in all_capsules if c.is_approved)

        self.summary_lbl.text = (
            f"Total: {total_count} cápsulas registradas • {approved_count} autorizadas como fuente"
        )

        # Filtrar según la selección actual
        if self.current_filter == "approved":
            display_list = [c for c in all_capsules if c.is_approved]
        elif self.current_filter == "draft":
            display_list = [c for c in all_capsules if not c.is_approved]
        else:
            display_list = all_capsules

        if not display_list:
            empty_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(180),
                padding=[dp(20), dp(30), dp(20), dp(20)],
                spacing=dp(12)
            )
            lbl_empty = Label(
                text="No hay cápsulas en esta sección.",
                font_size="15sp",
                bold=True,
                color=[0.4, 0.45, 0.5, 1],
                halign="center"
            )
            empty_box.add_widget(lbl_empty)

            btn_empty_create = Button(
                text="Crear una cápsula ahora",
                font_size="14sp",
                bold=True,
                background_normal="",
                background_color=[0.12, 0.45, 0.75, 1],
                color=[1, 1, 1, 1],
                size_hint=(None, None),
                size=(dp(220), dp(42)),
                pos_hint={"center_x": 0.5}
            )
            btn_empty_create.bind(on_release=lambda x: self.on_navigate_form(None))
            empty_box.add_widget(btn_empty_create)
            self.cards_container.add_widget(empty_box)
            return

        for cap in display_list:
            card = CapsuleCard(
                capsule=cap,
                on_toggle_approval=self.handle_toggle_approval,
                on_edit=self.handle_edit,
                on_delete=self.handle_delete
            )
            self.cards_container.add_widget(card)

    def handle_toggle_approval(self, capsule_id: int):
        """Alterna la aprobación de la cápsula y refresca la vista."""
        self.service.toggle_approval(capsule_id)
        self.refresh_capsules()

    def handle_edit(self, capsule: Capsule):
        """Abre el formulario en modo de edición con los datos de la cápsula."""
        self.on_navigate_form(capsule)

    def handle_delete(self, capsule: Capsule):
        """Muestra el diálogo de confirmación para eliminar la cápsula."""
        def confirm():
            self.service.delete_capsule(capsule.id)
            self.refresh_capsules()

        dialog = ConfirmDeleteDialog(capsule_title=capsule.title, on_confirm=confirm)
        dialog.open()

