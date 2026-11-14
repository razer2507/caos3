"""Vista del módulo de notas (UI Flet)."""

from __future__ import annotations

import logging

import flet as ft

from src.domains.notas.models.nota import Nota
from src.shared.application.events import (
    DEADLINES_CAMBIADOS,
    NOTAS_CAMBIADAS,
)
from src.shared.domain.errors import CaosError
from src.shared.presentation.app_context import AppContext
from src.shared.presentation.theme import (
    COLOR_ACENTO,
    COLOR_ACENTO_2,
    COLOR_PELIGRO,
    COLOR_SUPERFICIE,
    COLOR_SUPERFICIE_ALT,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
)
from src.shared.presentation.widgets import (
    avisar,
    campo_texto,
    chip,
    encabezado,
    estado_vacio,
    hace_cuanto,
    selector,
    tarjeta,
)

logger = logging.getLogger(__name__)


class NotasView(ft.Column):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__(expand=True, spacing=14, scroll=ft.ScrollMode.AUTO)
        self.ctx = ctx
        self._busqueda = ""

        self._input_busqueda = campo_texto(
            etiqueta="Buscar",
            pista="Título, contenido o área...",
            on_change=self._cambiar_busqueda,
        )
        self._input_busqueda.prefix_icon = ft.Icons.SEARCH

        self._lista = ft.Column(spacing=10)

        self.controls = [
            encabezado(
                "Notas",
                "Ideas, decisiones y contexto por área.",
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Nueva nota",
                        icon_color=COLOR_ACENTO,
                        on_click=lambda e: self._abrir_dialogo(),
                    )
                ],
            ),
            self._input_busqueda,
            self._lista,
        ]

        ctx.bus.suscribir(NOTAS_CAMBIADAS, self._on_cambio)
        ctx.bus.suscribir(DEADLINES_CAMBIADOS, self._on_cambio)
        self.refrescar()

    # ------------------------------------------------------------- eventos
    def _on_cambio(self, _payload=None) -> None:
        self.refrescar()

    def _cambiar_busqueda(self, e: ft.Event[ft.TextField]) -> None:
        self._busqueda = e.control.value or ""
        self.refrescar()

    def refrescar(self) -> None:
        try:
            notas = self.ctx.notas.listar(buscar=self._busqueda or None)
        except Exception:  # pragma: no cover
            logger.exception("No se pudieron cargar las notas")
            notas = []

        self._lista.controls.clear()
        if not notas:
            self._lista.controls.append(
                estado_vacio(
                    ft.Icons.NOTE_ALT,
                    "Sin notas" if not self._busqueda else "Sin resultados",
                    "Guarda ideas y decisiónalas con contexto.",
                )
            )
        else:
            deadlines = {d.id: d for d in self.ctx.deadlines.listar()}
            self._lista.controls.extend(self._tarjeta(n, deadlines) for n in notas)

        try:
            if self.page is not None:
                self._lista.update()
        except Exception:  # pragma: no cover
            pass

    def _tarjeta(self, nota: Nota, deadlines: dict) -> ft.Container:
        metadatos: list[ft.Control] = [
            chip(nota.area, icono=ft.Icons.LABEL_OUTLINE, color=COLOR_ACENTO)
        ]
        if nota.deadline_id and nota.deadline_id in deadlines:
            metadatos.append(
                chip(
                    deadlines[nota.deadline_id].titulo,
                    icono=ft.Icons.FOLDER_OUTLINED,
                    color=COLOR_ACENTO_2,
                )
            )
        metadatos.append(
            ft.Text(hace_cuanto(nota.updated_at), size=10.5, color=COLOR_TEXTO_SUAVE)
        )

        return tarjeta(
            ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        nota.titulo,
                                        size=15,
                                        weight=ft.FontWeight.W_700,
                                        color=COLOR_TEXTO,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        nota.resumen,
                                        size=12,
                                        color=COLOR_TEXTO_SUAVE,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_size=17,
                                tooltip="Editar",
                                icon_color=COLOR_TEXTO_SUAVE,
                                on_click=lambda e, n=nota: self._abrir_dialogo(n),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=17,
                                tooltip="Eliminar",
                                icon_color=ft.Colors.with_opacity(0.6, COLOR_PELIGRO),
                                on_click=lambda e, n=nota: self._eliminar(n),
                            ),
                        ],
                    ),
                    ft.Row(spacing=6, wrap=True, run_spacing=4, controls=metadatos),
                ],
            )
        )

    def _eliminar(self, nota: Nota) -> None:
        def confirmar(_e) -> None:
            self.page.pop_dialog()
            try:
                self.ctx.notas.eliminar(nota.id)
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Eliminar nota"),
                content=ft.Text(f"¿Eliminar «{nota.titulo}»?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Eliminar",
                        bgcolor=COLOR_PELIGRO,
                        color=ft.Colors.WHITE,
                        on_click=confirmar,
                    ),
                ],
            )
        )

    # ------------------------------------------------------------- diálogo
    def _abrir_dialogo(self, nota: Nota | None = None) -> None:
        es_edicion = nota is not None
        campo_titulo = campo_texto(etiqueta="Título", valor=nota.titulo if nota else "")
        campo_area = campo_texto(etiqueta="Área", valor=nota.area if nota else "General")
        campo_contenido = campo_texto(
            etiqueta="Contenido",
            valor=nota.contenido if nota else "",
            multilinea=True,
            lineas=8,
        )
        opciones_deadline = [("", "Sin proyecto")]
        opciones_deadline += [(d.id, d.titulo) for d in self.ctx.deadlines.listar()]
        campo_deadline = selector(
            etiqueta="Proyecto / deadline",
            opciones=opciones_deadline,
            valor=(nota.deadline_id or "") if nota else "",
        )

        def guardar(_e) -> None:
            try:
                if es_edicion:
                    self.ctx.notas.editar(
                        nota.id,
                        titulo=campo_titulo.value or "",
                        contenido=campo_contenido.value or "",
                        area=campo_area.value or "General",
                        deadline_id=campo_deadline.value or None,
                    )
                else:
                    self.ctx.notas.crear(
                        campo_titulo.value or "",
                        contenido=campo_contenido.value or "",
                        area=campo_area.value or "General",
                        deadline_id=campo_deadline.value or None,
                    )
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)
                return
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Editar nota" if es_edicion else "Nueva nota"),
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    width=360,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        campo_titulo,
                        campo_area,
                        campo_deadline,
                        campo_contenido,
                    ],
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
                    ft.FilledButton(
                        "Guardar",
                        bgcolor=COLOR_ACENTO,
                        color=ft.Colors.WHITE,
                        on_click=guardar,
                    ),
                ],
            )
        )
