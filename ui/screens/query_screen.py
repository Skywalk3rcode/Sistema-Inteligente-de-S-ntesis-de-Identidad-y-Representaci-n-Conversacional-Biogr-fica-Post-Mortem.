"""
Pantalla de Consulta del Legado para LegadoVivo.
Implementa consulta determinista sobre fuentes autorizadas, cita explícita
de referencias, abstención estricta ante falta de material y advertencia legal visible.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from config import DISCLAIMER_TEXT, ABSTENTION_MESSAGE


class QueryScreen(Screen):
    """
    Pantalla interactiva para realizar preguntas o búsquedas temáticas sobre el legado autorizado.
    """

    def __init__(self, query_engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = query_engine

        main_box = BoxLayout(orientation="vertical", spacing=dp(8), padding=[dp(14), dp(10), dp(14), dp(10)])

        # Encabezado
        lbl_header = Label(
            text="Consulta de Legado Autorizado",
            font_size="20sp",
            bold=True,
            color=[0.1, 0.15, 0.25, 1],
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle"
        )
        lbl_header.bind(size=lbl_header.setter("text_size"))
        main_box.add_widget(lbl_header)

        # Banner de Descargo Legal y Ético (Siempre visible y prominente)
        disclaimer_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(74),
            padding=[dp(12), dp(8), dp(12), dp(8)]
        )
        with disclaimer_box.canvas.before:
            Color(0.98, 0.94, 0.85, 1)  # Fondo ámbar suave
            # size=(0,0): el binding actualizará al tamaño real en el primer frame
            self.disclaimer_rect = RoundedRectangle(size=(0, 0), pos=disclaimer_box.pos, radius=[dp(8)])
        disclaimer_box.bind(
            size=lambda inst, v: setattr(self.disclaimer_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.disclaimer_rect, "pos", inst.pos)
        )

        lbl_disclaimer = Label(
            text=DISCLAIMER_TEXT,
            font_size="10.5sp",
            color=[0.6, 0.35, 0.05, 1],
            halign="left",
            valign="middle"
        )
        lbl_disclaimer.bind(size=lbl_disclaimer.setter("text_size"))
        disclaimer_box.add_widget(lbl_disclaimer)
        main_box.add_widget(disclaimer_box)

        # Barra de Entrada de Consulta
        search_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))
        self.txt_query = TextInput(
            hint_text="¿Qué principio o recuerdo deseas consultar?...",
            multiline=False,
            font_size="14sp",
            size_hint_x=0.72,
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        self.txt_query.bind(on_text_validate=lambda x: self.execute_query())
        search_row.add_widget(self.txt_query)

        btn_search = Button(
            text="Consultar",
            font_size="14sp",
            bold=True,
            background_normal="",
            background_color=[0.12, 0.45, 0.78, 1],
            color=[1, 1, 1, 1],
            size_hint_x=0.28
        )
        btn_search.bind(on_release=lambda x: self.execute_query())
        search_row.add_widget(btn_search)
        main_box.add_widget(search_row)

        # Fila de Sugerencias Rápidas para pruebas y demostración
        suggestions_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32), spacing=dp(6))
        sug_label = Label(
            text="Ejemplos:",
            font_size="11sp",
            bold=True,
            color=[0.4, 0.45, 0.5, 1],
            size_hint=(None, 1),
            width=dp(58)
        )
        suggestions_box.add_widget(sug_label)

        sug1 = Button(
            text="Honestidad",
            font_size="11sp",
            background_normal="",
            background_color=[0.9, 0.93, 0.97, 1],
            color=[0.15, 0.3, 0.5, 1]
        )
        sug1.bind(on_release=lambda x: self.quick_search("honestidad en el trabajo"))

        sug2 = Button(
            text="Familia",
            font_size="11sp",
            background_normal="",
            background_color=[0.9, 0.93, 0.97, 1],
            color=[0.15, 0.3, 0.5, 1]
        )
        sug2.bind(on_release=lambda x: self.quick_search("familia y café"))

        sug3 = Button(
            text="Probar Abstención",
            font_size="11sp",
            background_normal="",
            background_color=[0.96, 0.9, 0.9, 1],
            color=[0.7, 0.2, 0.2, 1]
        )
        sug3.bind(on_release=lambda x: self.quick_search("viaje espacial a Marte y astrofísica"))

        suggestions_box.add_widget(sug1)
        suggestions_box.add_widget(sug2)
        suggestions_box.add_widget(sug3)
        main_box.add_widget(suggestions_box)

        # Área de Desplazamiento de Respuestas y Fuentes
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.results_container = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(6), 0, dp(16)]
        )
        self.results_container.bind(minimum_height=self.results_container.setter("height"))
        self.scroll.add_widget(self.results_container)
        main_box.add_widget(self.scroll)

        self.add_widget(main_box)

        # Mostrar estado inicial informativo
        self.show_initial_state()

    def quick_search(self, query_text: str):
        """Asigna un texto predefinido y ejecuta la consulta automáticamente."""
        self.txt_query.text = query_text
        self.execute_query()

    def show_initial_state(self):
        """Muestra una tarjeta explicativa sobre el funcionamiento de la consulta."""
        self.results_container.clear_widgets()
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            spacing=dp(8)
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            # size=(0,0): el binding actualizará al tamaño real en el primer frame
            self.initial_rect = RoundedRectangle(size=(0, 0), pos=card.pos, radius=[dp(12)])
        card.bind(
            size=lambda inst, v: setattr(self.initial_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.initial_rect, "pos", inst.pos)
        )

        t_lbl = Label(
            text="Consulta Responsable sin IA Generativa",
            font_size="15sp",
            bold=True,
            color=[0.15, 0.2, 0.35, 1],
            size_hint_y=None,
            height=dp(24),
            halign="left"
        )
        t_lbl.bind(size=t_lbl.setter("text_size"))
        card.add_widget(t_lbl)

        d_lbl = Label(
            text=(
                "Las consultas en LegadoVivo recuperan estrictamente el contenido de las cápsulas "
                "que el titular aprobó como fuente.\n\n"
                "• Si existe concordancia: se presentará el fragmento exacto y sus fuentes citadas.\n"
                "• Si no hay coincidencias: el sistema se abstiene para no inventar hechos."
            ),
            font_size="13sp",
            color=[0.35, 0.4, 0.45, 1],
            halign="left",
            valign="top"
        )
        d_lbl.bind(size=d_lbl.setter("text_size"))
        card.add_widget(d_lbl)

        self.results_container.add_widget(card)

    def execute_query(self):
        """Ejecuta la consulta léxica sobre las fuentes autorizadas."""
        query_text = self.txt_query.text.strip()
        result = self.engine.query(query_text)
        self.results_container.clear_widgets()

        if not result.has_matches:
            # Estado de Abstención o Sin Coincidencia
            abstention_card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(220),
                padding=[dp(16), dp(16), dp(16), dp(16)],
                spacing=dp(10)
            )
            with abstention_card.canvas.before:
                Color(0.98, 0.94, 0.94, 1)  # Fondo rojizo muy suave
                # size=(0,0): el binding actualizará al tamaño real en el primer frame
                self.abs_rect = RoundedRectangle(size=(0, 0), pos=abstention_card.pos, radius=[dp(12)])
            abstention_card.bind(
                size=lambda inst, v: setattr(self.abs_rect, "size", inst.size),
                pos=lambda inst, v: setattr(self.abs_rect, "pos", inst.pos)
            )

            abs_title = Label(
                text="ABSTENCIÓN DE RESPUESTA",
                font_size="15sp",
                bold=True,
                color=[0.8, 0.15, 0.15, 1],
                size_hint_y=None,
                height=dp(26),
                halign="left"
            )
            abs_title.bind(size=abs_title.setter("text_size"))
            abstention_card.add_widget(abs_title)

            abs_body = Label(
                text=result.answer,
                font_size="13sp",
                color=[0.25, 0.25, 0.25, 1],
                halign="left",
                valign="top"
            )
            abs_body.bind(size=abs_body.setter("text_size"))
            abstention_card.add_widget(abs_body)

            abs_hint = Label(
                text=(
                    f"Cápsulas autorizadas en la base de datos local: {result.total_approved_available}.\n"
                    "Para incluir este tema, registre y apruebe una nueva cápsula en la Biblioteca."
                ),
                font_size="11sp",
                color=[0.55, 0.55, 0.6, 1],
                size_hint_y=None,
                height=dp(32),
                halign="left"
            )
            abs_hint.bind(size=abs_hint.setter("text_size"))
            abstention_card.add_widget(abs_hint)

            self.results_container.add_widget(abstention_card)
            return

        # Estado con Coincidencias: Mostrar respuesta sustentada
        answer_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(230),
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(8)
        )
        with answer_card.canvas.before:
            Color(1, 1, 1, 1)
            # size=(0,0): el binding actualizará al tamaño real en el primer frame
            self.ans_rect = RoundedRectangle(size=(0, 0), pos=answer_card.pos, radius=[dp(12)])
        answer_card.bind(
            size=lambda inst, v: setattr(self.ans_rect, "size", inst.size),
            pos=lambda inst, v: setattr(self.ans_rect, "pos", inst.pos)
        )

        ans_title = Label(
            text="Respuesta Basada en Material Autorizado",
            font_size="16sp",
            bold=True,
            color=[0.08, 0.52, 0.24, 1],
            size_hint_y=None,
            height=dp(26),
            halign="left"
        )
        ans_title.bind(size=ans_title.setter("text_size"))
        answer_card.add_widget(ans_title)

        ans_body = Label(
            text=result.answer,
            font_size="13sp",
            color=[0.2, 0.22, 0.26, 1],
            halign="left",
            valign="top"
        )
        ans_body.bind(size=ans_body.setter("text_size"))
        answer_card.add_widget(ans_body)
        self.results_container.add_widget(answer_card)

        # Sección: Fuentes Utilizadas
        sources_header = Label(
            text=f"FUENTES AUTORIZADAS UTILIZADAS ({len(result.sources)})",
            font_size="13sp",
            bold=True,
            color=[0.35, 0.4, 0.5, 1],
            size_hint_y=None,
            height=dp(26),
            halign="left"
        )
        sources_header.bind(size=sources_header.setter("text_size"))
        self.results_container.add_widget(sources_header)

        for src in result.sources:
            src_card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(125),
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4)
            )
            with src_card.canvas.before:
                Color(0.95, 0.97, 1.0, 1)  # Azul claro tenue
                # BUG CORREGIDO: 'self.src_rect' se sobreescribía en cada iteración del bucle,
                # lo que hacía que los bindings de tarjetas previas apuntaran al último rect.
                # Solución: capturar el rect como variable local en el closure (rect=rect).
                src_rect = RoundedRectangle(size=(0, 0), pos=src_card.pos, radius=[dp(8)])
            src_card.bind(
                size=lambda inst, v, rect=src_rect: setattr(rect, "size", inst.size),
                pos=lambda inst, v, rect=src_rect: setattr(rect, "pos", inst.pos)
            )

            st_lbl = Label(
                text=f"Ref #{src['id']} — {src['title']} ({src['topic']})",
                font_size="13sp",
                bold=True,
                color=[0.1, 0.25, 0.55, 1],
                size_hint_y=None,
                height=dp(36),
                halign="left",
                valign="middle"
            )
            st_lbl.bind(size=st_lbl.setter("text_size"))
            src_card.add_widget(st_lbl)

            ex_lbl = Label(
                text=f"«{src['excerpt']}»",
                font_size="12sp",
                italic=True,
                color=[0.3, 0.35, 0.4, 1],
                halign="left",
                valign="top"
            )
            ex_lbl.bind(size=ex_lbl.setter("text_size"))
            src_card.add_widget(ex_lbl)

            self.results_container.add_widget(src_card)

