"""
Componentes de diálogo modal y notificaciones para LegadoVivo.
"""

from typing import Callable, Optional
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class ConfirmDeleteDialog(ModalView):
    """
    Diálogo modal de confirmación antes de eliminar una cápsula permanentemente.
    """

    def __init__(self, capsule_title: str, on_confirm: Callable[[], None], **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.88, None)
        self.height = dp(250)
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.6]

        container = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(20), dp(20), dp(16)],
            spacing=dp(14)
        )

        with container.canvas.before:
            Color(1, 1, 1, 1)  # Fondo blanco
            self.rect = RoundedRectangle(size=container.size, pos=container.pos, radius=[dp(16)])
        container.bind(size=self._update_rect, pos=self._update_rect)

        # Título
        title_lbl = Label(
            text="¿Eliminar cápsula?",
            font_size="19sp",
            bold=True,
            color=[0.85, 0.15, 0.15, 1],
            size_hint_y=None,
            height=dp(28),
            halign="left"
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))
        container.add_widget(title_lbl)

        # Mensaje descriptivo
        msg_lbl = Label(
            text=f"¿Está seguro de que desea eliminar la cápsula:\n«{capsule_title}»?\nEsta acción no se puede deshacer.",
            font_size="14sp",
            color=[0.2, 0.2, 0.2, 1],
            size_hint_y=None,
            height=dp(70),
            halign="left",
            valign="middle"
        )
        msg_lbl.bind(size=msg_lbl.setter("text_size"))
        container.add_widget(msg_lbl)

        # Botones de acción
        btn_box = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(46))

        btn_cancel = Button(
            text="Cancelar",
            font_size="15sp",
            background_normal="",
            background_color=[0.9, 0.92, 0.94, 1],
            color=[0.2, 0.25, 0.3, 1]
        )
        btn_cancel.bind(on_release=self.dismiss)

        btn_delete = Button(
            text="Eliminar",
            font_size="15sp",
            bold=True,
            background_normal="",
            background_color=[0.85, 0.15, 0.15, 1],
            color=[1, 1, 1, 1]
        )

        def _do_confirm(instance):
            self.dismiss()
            on_confirm()

        btn_delete.bind(on_release=_do_confirm)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_delete)
        container.add_widget(btn_box)

        self.add_widget(container)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class DisclaimerInfoDialog(ModalView):
    """
    Diálogo informativo sobre el marco ético y limitaciones legales de LegadoVivo.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(380)
        self.auto_dismiss = True

        container = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(20), dp(20), dp(16)],
            spacing=dp(12)
        )

        with container.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(size=container.size, pos=container.pos, radius=[dp(16)])
        container.bind(size=self._update_rect, pos=self._update_rect)

        title = Label(
            text="Marco Ético y Transparencia",
            font_size="18sp",
            bold=True,
            color=[0.1, 0.2, 0.5, 1],
            size_hint_y=None,
            height=dp(28),
            halign="left"
        )
        title.bind(size=title.setter("text_size"))
        container.add_widget(title)

        body = Label(
            text=(
                "• Representación Controlada: LegadoVivo no afirma sustituir la conciencia "
                "ni revivir digitalmente a ninguna persona.\n\n"
                "• Fuentes Autorizadas: Las respuestas de consulta se construyen únicamente "
                "a partir de los registros que el titular aprobó explícitamente.\n\n"
                "• Sin Consejo Profesional: Ninguna respuesta debe tomarse como asesoramiento "
                "médico, legal, tributario o financiero.\n\n"
                "• Privacidad Local: Su legado reside exclusivamente en este dispositivo."
            ),
            font_size="13sp",
            color=[0.25, 0.25, 0.25, 1],
            size_hint_y=None,
            height=dp(210),
            halign="left",
            valign="top"
        )
        body.bind(size=body.setter("text_size"))
        container.add_widget(body)

        btn_close = Button(
            text="Entendido",
            font_size="15sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.35, 0.7, 1],
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=dp(44)
        )
        btn_close.bind(on_release=self.dismiss)
        container.add_widget(btn_close)

        self.add_widget(container)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

