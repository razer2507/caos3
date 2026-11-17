"""Vista del módulo de tareas (UI Flet)."""

from __future__ import annotations

import logging
from datetime import date

import flet as ft

from src.domains.tareas.models.tarea import Tarea
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.application.events import (
    DEADLINES_CAMBIADOS,
    TAREAS_CAMBIADAS,
)
from src.shared.domain.errors import CaosError
from src.shared.domain.periodos import Periodo
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
    abrir_selector_rango,
    actualizar_selector_periodo,
    avisar,
    campo_texto,
    chip,
    encabezado,
    estado_vacio,
    fecha_corta,
    pill_prioridad,
    selector,
    selector_fecha,
    selector_periodo,
    tarjeta,
)

logger = logging.getLogger(__name__)


class TareasView(ft.Column):
    """Lista, crea, edita y completa tareas con recompensa inmediata."""

    def __init__(self, ctx: AppContext) -> None:
        super().__init__(expand=True, spacing=14, scroll=ft.ScrollMode.AUTO)
        self.ctx = ctx
        self._periodo: Periodo | None = Periodo.DIARIO
        self._desde: date | None = None
        self._hasta: date | None = None
        self._celebrando = False

        self._selector_periodo = selector_periodo(
            on_change=self._cambiar_periodo,
            valor="diario",
            opciones=[
                ("todas", "Todas"),
                ("diario", "Diaria"),
                ("manana", "Mañana"),
            ],
        )
        self._texto_rango = ft.Text("", size=12, color=COLOR_ACENTO, weight=ft.FontWeight.W_600)
        self._barra_rango = ft.Row(
            visible=False,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.DATE_RANGE, size=14, color=COLOR_ACENTO),
                self._texto_rango,
                ft.IconButton(
                    icon=ft.Icons.CLEAR,
                    icon_size=15,
                    tooltip="Quitar plazo",
                    icon_color=COLOR_TEXTO_SUAVE,
                    on_click=self._limpiar_rango,
                ),
            ],
        )

        self._lista = ft.Column(spacing=10)

        self.controls = [
            encabezado(
                "Tareas",
                "Captura, prioriza y cierra el bucle.",
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Nueva tarea",
                        icon_color=COLOR_ACENTO,
                        on_click=lambda e: self._abrir_dialogo(),
                    ),
                ],
            ),
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.CALENDAR_MONTH, size=16, color=COLOR_TEXTO_SUAVE
                    ),
                    self._selector_periodo,
                    ft.IconButton(
                        icon=ft.Icons.DATE_RANGE,
                        tooltip="Elegir plazo de fechas",
                        icon_color=COLOR_ACENTO,
                        on_click=self._elegir_rango,
                    ),
                ],
            ),
            self._barra_rango,
            self._lista,
        ]

        ctx.bus.suscribir(TAREAS_CAMBIADAS, self._on_cambio)
        ctx.bus.suscribir(DEADLINES_CAMBIADOS, self._on_cambio)
        self.refrescar()

    # ------------------------------------------------------------- eventos
    def _on_cambio(self, _payload=None) -> None:
        if not self._celebrando:
            self.refrescar()

    def _cambiar_periodo(self, valor: str) -> None:
        self._desde = None
        self._hasta = None
        self._barra_rango.visible = False
        if not valor or valor == "todas":
            self._periodo = None
        else:
            self._periodo = Periodo(valor)
        self._actualizar_filtros_ui()
        self.refrescar()

    def _elegir_rango(self, _e) -> None:
        abrir_selector_rango(
            self.page,
            desde=self._desde,
            hasta=self._hasta,
            on_rango=self._aplicar_rango,
        )

    def _aplicar_rango(self, desde: date, hasta: date) -> None:
        self._desde = desde
        self._hasta = hasta
        self._periodo = None
        actualizar_selector_periodo(self._selector_periodo, "todas", texto="Plazo")
        texto = (
            fecha_corta(desde)
            if desde == hasta
            else f"{fecha_corta(desde)} – {fecha_corta(hasta)}"
        )
        self._texto_rango.value = f"Plazo: {texto}"
        self._barra_rango.visible = True
        self._actualizar_filtros_ui()
        self.refrescar()

    def _limpiar_rango(self, _e=None) -> None:
        self._desde = None
        self._hasta = None
        self._periodo = Periodo.DIARIO
        actualizar_selector_periodo(self._selector_periodo, "diario")
        self._barra_rango.visible = False
        self._actualizar_filtros_ui()
        self.refrescar()

    def _actualizar_filtros_ui(self) -> None:
        try:
            if self.page is not None:
                self._barra_rango.update()
        except Exception:  # pragma: no cover
            pass

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
            tareas = self.ctx.tareas.listar(
                incluir_completadas=True,
                periodo=self._periodo,
                desde=self._desde,
                hasta=self._hasta,
            )
        except Exception:  # pragma: no cover - defensa ante DB bloqueada
            logger.exception("No se pudieron cargar las tareas")
            tareas = []

        self._lista.controls.clear()
        if not tareas:
            if self._desde is not None or self._hasta is not None:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.EVENT_BUSY,
                        "Sin tareas en este plazo",
                        "Asigna una fecha a tus tareas o cambia el rango.",
                    )
                )
            elif self._periodo is not None:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.EVENT_BUSY,
                        f"Sin tareas en vista {self._periodo.etiqueta.lower()}",
                        "Asigna una fecha a tus tareas o cambia el periodo.",
                    )
                )
            else:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.TASK_ALT,
                        "Todo despejado",
                        "Crea tu primera tarea con el botón +.",
                    )
                )
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
        if tarea.fecha:
            metadatos.append(
                chip(fecha_corta(tarea.fecha), icono=ft.Icons.EVENT, color=COLOR_TEXTO_SUAVE)
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

        fecha_holder: dict[str, object] = {
            "valor": tarea.fecha if tarea else date.today()
        }
        campo_fecha = selector_fecha(self.page, etiqueta="Fecha", holder=fecha_holder)

        def guardar(_e) -> None:
            try:
                titulo = campo_titulo.value or ""
                prioridad = Prioridad.desde(campo_prioridad.value or 1)
                deadline_id = campo_deadline.value or None
                fecha = fecha_holder["valor"]
                if es_edicion:
                    self.ctx.tareas.editar(
                        tarea.id,
                        titulo=titulo,
                        descripcion=campo_desc.value or "",
                        prioridad=prioridad,
                        deadline_id=deadline_id,
                        fecha=fecha,
                    )
                else:
                    self.ctx.tareas.crear(
                        titulo,
                        prioridad,
                        descripcion=campo_desc.value or "",
                        deadline_id=deadline_id,
                        fecha=fecha,
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
                    controls=[
                        campo_titulo,
                        campo_desc,
                        campo_prioridad,
                        campo_deadline,
                        campo_fecha,
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
