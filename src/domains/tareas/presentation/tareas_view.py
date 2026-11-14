"""Vista del módulo de tareas (UI Flet)."""

from __future__ import annotations

import logging

import flet as ft

from src.domains.tareas.models.tarea import Tarea
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.application.events import (
    DEADLINES_CAMBIADOS,
    TAREAS_CAMBIADAS,
)
from src.shared.domain.errors import CaosError
from src.shared.presentation.app_context import AppContext
from src.shared.presentation.theme import (
    COLOR_ACENTO,
    COLOR_ACENTO_2,
    COLOR_EXITO,
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
    pill_prioridad,
    selector,
    tarjeta,
)

logger = logging.getLogger(__name__)


class TareasView(ft.Column):
    """Lista, crea, edita y completa tareas con recompensa inmediata."""

    def __init__(self, ctx: AppContext) -> None:
        super().__init__(expand=True, spacing=14, scroll=ft.ScrollMode.AUTO)
        self.ctx = ctx
        self._filtro = "todas"
        self._celebrando = False

        self._input = campo_texto(
            etiqueta="Nueva tarea",
            pista="¿Qué tienes que hacer?",
            on_submit=self._crear_rapida,
        )
        self._input.expand = True

        self._filtros = ft.SegmentedButton(
            segments=[
                ft.Segment(value="todas", label=ft.Text("Todas")),
                ft.Segment(value="pendientes", label=ft.Text("Pendientes")),
                ft.Segment(value="completadas", label=ft.Text("Hechas")),
            ],
            selected=["todas"],
            allow_empty_selection=False,
            allow_multiple_selection=False,
            on_change=self._cambiar_filtro,
        )

        self._lista = ft.Column(spacing=10)

        self.controls = [
            encabezado(
                "Tareas",
                "Captura, prioriza y cierra el bucle.",
                [
                    ft.IconButton(
                        icon=ft.Icons.TUNE,
                        tooltip="Crear con detalles",
                        icon_color=COLOR_TEXTO_SUAVE,
                        on_click=lambda e: self._abrir_dialogo(),
                    ),
                ],
            ),
            ft.Row(
                spacing=8,
                controls=[
                    self._input,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Añadir tarea",
                        icon_color=ft.Colors.WHITE,
                        bgcolor=COLOR_ACENTO,
                        on_click=self._crear_rapida,
                    ),
                ],
            ),
            self._filtros,
            self._lista,
        ]

        ctx.bus.suscribir(TAREAS_CAMBIADAS, self._on_cambio)
        ctx.bus.suscribir(DEADLINES_CAMBIADOS, self._on_cambio)
        self.refrescar()

    # ------------------------------------------------------------- eventos
    def _on_cambio(self, _payload=None) -> None:
        if not self._celebrando:
            self.refrescar()

    def _cambiar_filtro(self, e: ft.Event[ft.SegmentedButton]) -> None:
        seleccion = e.control.selected
        if seleccion:
            self._filtro = seleccion[0]
            self.refrescar()

    def _crear_rapida(self, _e=None) -> None:
        texto = (self._input.value or "").strip()
        if not texto:
            avisar(self.page, "Escribe un título para la tarea.", error=True)
            return
        try:
            self.ctx.tareas.crear(texto, Prioridad.IMPORTANTE_URGENTE)
        except CaosError as exc:
            avisar(self.page, str(exc), error=True)
            return
        self._input.value = ""
        self._input.update()

    def _alternar(self, tarea: Tarea, valor: bool, contenedor: ft.Container) -> None:
        self._celebrando = True
        try:
            if valor:
                self.ctx.tareas.completar(tarea.id)
            else:
                self.ctx.tareas.reabrir(tarea.id)
        except CaosError as exc:
            avisar(self.page, str(exc), error=True)
            self._celebrando = False
            self.refrescar()
            return

        if valor:
            self.page.run_task(self._celebrar, contenedor)
        else:
            self._celebrando = False
            self.refrescar()

    async def _celebrar(self, contenedor: ft.Container) -> None:
        try:
            await self.ctx.effects.celebrar(contenedor)
        finally:
            self._celebrando = False
            self.refrescar()

    def _eliminar(self, tarea: Tarea) -> None:
        def confirmar(_e) -> None:
            self.page.pop_dialog()
            try:
                self.ctx.tareas.eliminar(tarea.id)
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Eliminar tarea"),
                content=ft.Text(f"¿Seguro que quieres eliminar «{tarea.titulo}»?"),
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

    # -------------------------------------------------------------- render
    def refrescar(self) -> None:
        try:
            tareas = self.ctx.tareas.listar(incluir_completadas=True)
        except Exception:  # pragma: no cover - defensa ante DB bloqueada
            logger.exception("No se pudieron cargar las tareas")
            tareas = []

        if self._filtro == "pendientes":
            tareas = [t for t in tareas if not t.completada]
        elif self._filtro == "completadas":
            tareas = [t for t in tareas if t.completada]

        self._lista.controls.clear()
        if not tareas:
            mensajes = {
                "todas": (ft.Icons.TASK_ALT, "Todo despejado", "Crea tu primera tarea con el campo de arriba."),
                "pendientes": (ft.Icons.CELEBRATION, "Sin pendientes", "Has cerrado todos los bucles. Disfrútalo."),
                "completadas": (ft.Icons.HISTORY, "Nada completado aún", "Marca una tarea y aparecerá aquí."),
            }
            icono, titulo, subtitulo = mensajes[self._filtro]
            self._lista.controls.append(estado_vacio(icono, titulo, subtitulo))
        else:
            self._lista.controls.extend(self._tarjeta(t) for t in tareas)

        self._actualizar()

    def _actualizar(self) -> None:
        try:
            if self.page is not None:
                self._lista.update()
        except Exception:  # pragma: no cover - la vista puede no estar montada
            pass

    def _tarjeta(self, tarea: Tarea) -> ft.Container:
        contenedor = tarjeta(ft.Container(), padding=12)

        checkbox = ft.Checkbox(
            value=tarea.completada,
            active_color=COLOR_EXITO,
            on_change=lambda e, t=tarea, c=contenedor: self._alternar(t, bool(e.control.value), c),
        )

        titulo = ft.Text(
            tarea.titulo,
            size=14.5,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXTO_SUAVE if tarea.completada else COLOR_TEXTO,
            style=(
                ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                if tarea.completada
                else None
            ),
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        metadatos: list[ft.Control] = [pill_prioridad(tarea.prioridad)]
        if tarea.deadline_id:
            deadline = next(
                (d for d in self.ctx.deadlines.listar() if d.id == tarea.deadline_id),
                None,
            )
            if deadline:
                metadatos.append(
                    chip(deadline.titulo, icono=ft.Icons.FOLDER_OUTLINED, color=COLOR_ACENTO_2)
                )

        detalle = [
            titulo,
            ft.Row(spacing=6, wrap=True, run_spacing=4, controls=metadatos),
        ]
        if tarea.descripcion:
            # La descripción va en su propia línea: un control con ``expand``
            # dentro de un Row con ``wrap`` rompe el layout de Flutter.
            detalle.append(
                ft.Text(
                    tarea.descripcion,
                    size=11.5,
                    color=COLOR_TEXTO_SUAVE,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        contenedor.content = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                checkbox,
                ft.Column(
                    expand=True,
                    spacing=5,
                    controls=detalle,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_size=17,
                    tooltip="Editar",
                    icon_color=COLOR_TEXTO_SUAVE,
                    on_click=lambda e, t=tarea: self._abrir_dialogo(t),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=17,
                    tooltip="Eliminar",
                    icon_color=ft.Colors.with_opacity(0.6, COLOR_PELIGRO),
                    on_click=lambda e, t=tarea: self._eliminar(t),
                ),
            ],
        )
        return contenedor

    # ------------------------------------------------------------- diálogo
    def _abrir_dialogo(self, tarea: Tarea | None = None) -> None:
        es_edicion = tarea is not None
        campo_titulo = campo_texto(etiqueta="Título", valor=tarea.titulo if tarea else "")
        campo_desc = campo_texto(
            etiqueta="Descripción",
            valor=tarea.descripcion if tarea else "",
            multilinea=True,
            lineas=3,
        )

        prioridades = [
            (str(p.value), f"{p.codigo} · {p.etiqueta} ({p.descripcion})")
            for p in Prioridad
        ]
        campo_prioridad = selector(
            etiqueta="Prioridad (Eisenhower)",
            opciones=prioridades,
            valor=str(int(tarea.prioridad)) if tarea else "1",
        )

        deadlines = self.ctx.deadlines.listar()
        opciones_deadline = [("", "Sin proyecto")]
        opciones_deadline += [(d.id, d.titulo) for d in deadlines]
        campo_deadline = selector(
            etiqueta="Proyecto / deadline",
            opciones=opciones_deadline,
            valor=(tarea.deadline_id or "") if tarea else "",
        )

        def guardar(_e) -> None:
            try:
                titulo = campo_titulo.value or ""
                prioridad = Prioridad.desde(campo_prioridad.value or 1)
                deadline_id = campo_deadline.value or None
                if es_edicion:
                    self.ctx.tareas.editar(
                        tarea.id,
                        titulo=titulo,
                        descripcion=campo_desc.value or "",
                        prioridad=prioridad,
                        deadline_id=deadline_id,
                    )
                else:
                    self.ctx.tareas.crear(
                        titulo,
                        prioridad,
                        descripcion=campo_desc.value or "",
                        deadline_id=deadline_id,
                    )
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)
                return
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Editar tarea" if es_edicion else "Nueva tarea"),
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    width=340,
                    controls=[campo_titulo, campo_desc, campo_prioridad, campo_deadline],
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
