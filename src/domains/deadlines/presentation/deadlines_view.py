"""Vista de proyectos / deadlines (UI Flet)."""

from __future__ import annotations

import logging
from datetime import date

import flet as ft

from src.domains.deadlines.models.deadline import Deadline
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
    selector_fecha,
    selector_periodo,
    tarjeta,
)

logger = logging.getLogger(__name__)


class DeadlinesView(ft.Column):
    def __init__(self, ctx: AppContext) -> None:
        super().__init__(expand=True, spacing=14, scroll=ft.ScrollMode.AUTO)
        self.ctx = ctx
        self._periodo: Periodo | None = Periodo.SEMANAL
        self._desde: date | None = None
        self._hasta: date | None = None
        self._lista = ft.Column(spacing=10)

        self._selector_periodo = selector_periodo(
            on_change=self._cambiar_periodo,
            valor="semanal",
        )
        self._texto_rango = ft.Text(
            "", size=12, color=COLOR_ACENTO, weight=ft.FontWeight.W_600
        )
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

        self.controls = [
            encabezado(
                "Proyectos",
                "Hitos con fecha límite y su avance real.",
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Nuevo proyecto",
                        icon_color=COLOR_ACENTO,
                        on_click=lambda e: self._abrir_dialogo(),
                    )
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

        ctx.bus.suscribir(DEADLINES_CAMBIADOS, self._on_cambio)
        ctx.bus.suscribir(TAREAS_CAMBIADAS, self._on_cambio)
        self.refrescar()

    # ------------------------------------------------------------- eventos
    def _on_cambio(self, _payload=None) -> None:
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
        self._periodo = Periodo.SEMANAL
        actualizar_selector_periodo(self._selector_periodo, "semanal")
        self._barra_rango.visible = False
        self._actualizar_filtros_ui()
        self.refrescar()

    def _actualizar_filtros_ui(self) -> None:
        try:
            if self.page is not None:
                self._barra_rango.update()
        except Exception:  # pragma: no cover
            pass

    def refrescar(self) -> None:
        try:
            resumenes = self.ctx.deadlines.resumen(
                periodo=self._periodo,
                desde=self._desde,
                hasta=self._hasta,
            )
        except Exception:  # pragma: no cover
            logger.exception("No se pudieron cargar los deadlines")
            resumenes = []

        self._lista.controls.clear()
        if not resumenes:
            if self._desde is not None or self._hasta is not None:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.EVENT_BUSY,
                        "Sin proyectos en este plazo",
                        "Ajusta las fechas límite o cambia el rango.",
                    )
                )
            elif self._periodo is not None:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.EVENT_BUSY,
                        f"Sin proyectos en vista {self._periodo.etiqueta.lower()}",
                        "Ajusta las fechas límite o cambia el periodo.",
                    )
                )
            else:
                self._lista.controls.append(
                    estado_vacio(
                        ft.Icons.FLAG,
                        "Sin proyectos todavía",
                        "Crea un hito con fecha límite y agrúpale tareas.",
                    )
                )
        else:
            self._lista.controls.extend(
                self._tarjeta(d, progreso) for d, progreso in
                ((r.deadline, r.progreso) for r in resumenes)
            )

        try:
            if self.page is not None:
                self._lista.update()
        except Exception:  # pragma: no cover
            pass

    def _tarjeta(self, deadline: Deadline, progreso) -> ft.Container:
        dias = deadline.dias_restantes()
        if deadline.completado:
            estado = chip("Completado", icono=ft.Icons.CHECK_CIRCLE, color=COLOR_EXITO)
        elif dias is None:
            estado = chip("Sin fecha", icono=ft.Icons.EVENT, color=COLOR_TEXTO_SUAVE)
        elif dias < 0:
            estado = chip(f"Vencido {abs(dias)} d", icono=ft.Icons.WARNING_AMBER, color=COLOR_PELIGRO)
        elif dias == 0:
            estado = chip("Vence hoy", icono=ft.Icons.LOCAL_FIRE_DEPARTMENT, color=COLOR_PELIGRO)
        else:
            estado = chip(f"{dias} d restantes", icono=ft.Icons.SCHEDULE, color=COLOR_ACENTO_2)

        metadatos: list[ft.Control] = [chip(deadline.area, icono=ft.Icons.LABEL_OUTLINE, color=COLOR_ACENTO)]
        if deadline.fecha_limite:
            metadatos.append(chip(fecha_corta(deadline.fecha_limite), icono=ft.Icons.CALENDAR_MONTH, color=COLOR_TEXTO_SUAVE))
        metadatos.append(estado)

        barra = ft.ProgressBar(
            value=progreso.porcentaje,
            height=6,
            border_radius=4,
            color=COLOR_EXITO if deadline.completado else COLOR_ACENTO,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        )

        contenido = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Checkbox(
                            value=deadline.completado,
                            active_color=COLOR_EXITO,
                            on_change=lambda e, d=deadline: self._alternar(d),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=4,
                            controls=[
                                ft.Text(
                                    deadline.titulo,
                                    size=15,
                                    weight=ft.FontWeight.W_700,
                                    color=COLOR_TEXTO_SUAVE if deadline.completado else COLOR_TEXTO,
                                    style=(
                                        ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                                        if deadline.completado
                                        else None
                                    ),
                                ),
                                ft.Row(spacing=6, wrap=True, run_spacing=4, controls=metadatos),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_size=17,
                            tooltip="Editar",
                            icon_color=COLOR_TEXTO_SUAVE,
                            on_click=lambda e, d=deadline: self._abrir_dialogo(d),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=17,
                            tooltip="Eliminar",
                            icon_color=ft.Colors.with_opacity(0.6, COLOR_PELIGRO),
                            on_click=lambda e, d=deadline: self._eliminar(d),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(expand=True, content=barra),
                        ft.Text(
                            f"{progreso.hechas}/{progreso.total}",
                            size=11,
                            color=COLOR_TEXTO_SUAVE,
                        ),
                    ],
                ),
            ],
        )

        if deadline.descripcion:
            contenido.controls.insert(
                1,
                ft.Text(
                    deadline.descripcion,
                    size=12,
                    color=COLOR_TEXTO_SUAVE,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            )

        return tarjeta(contenido)

    def _alternar(self, deadline: Deadline) -> None:
        try:
            self.ctx.deadlines.alternar(deadline.id)
        except CaosError as exc:
            avisar(self.page, str(exc), error=True)

    def _eliminar(self, deadline: Deadline) -> None:
        def confirmar(_e) -> None:
            self.page.pop_dialog()
            try:
                self.ctx.deadlines.eliminar(deadline.id)
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Eliminar proyecto"),
                content=ft.Text(
                    f"¿Eliminar «{deadline.titulo}»? Las tareas vinculadas quedarán sueltas."
                ),
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
    def _abrir_dialogo(self, deadline: Deadline | None = None) -> None:
        es_edicion = deadline is not None
        campo_titulo = campo_texto(etiqueta="Nombre del proyecto", valor=deadline.titulo if deadline else "")
        campo_desc = campo_texto(
            etiqueta="Descripción",
            valor=deadline.descripcion if deadline else "",
            multilinea=True,
            lineas=3,
        )
        campo_area = campo_texto(etiqueta="Área", valor=deadline.area if deadline else "General")

        fecha_holder: dict[str, date | None] = {
            "valor": deadline.fecha_limite if deadline else None
        }
        campo_fecha = selector_fecha(
            self.page, etiqueta="Fecha límite", holder=fecha_holder,
            ayuda="Elige la fecha límite",
        )

        def guardar(_e) -> None:
            try:
                if es_edicion:
                    self.ctx.deadlines.editar(
                        deadline.id,
                        titulo=campo_titulo.value or "",
                        descripcion=campo_desc.value or "",
                        area=campo_area.value or "General",
                        fecha_limite=fecha_holder["valor"],
                    )
                else:
                    self.ctx.deadlines.crear(
                        campo_titulo.value or "",
                        descripcion=campo_desc.value or "",
                        area=campo_area.value or "General",
                        fecha_limite=fecha_holder["valor"],
                    )
            except CaosError as exc:
                avisar(self.page, str(exc), error=True)
                return
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Editar proyecto" if es_edicion else "Nuevo proyecto"),
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    width=340,
                    controls=[
                        campo_titulo,
                        campo_desc,
                        campo_area,
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
