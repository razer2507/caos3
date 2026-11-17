"""Shell principal: cabecera, progreso diario, navegación y sync."""

from __future__ import annotations

import flet as ft

from src.domains.deadlines.presentation.deadlines_view import DeadlinesView
from src.domains.notas.presentation.notas_view import NotasView
from src.domains.tareas.presentation.tareas_view import TareasView
from src.shared.application.events import TODOS_LOS_TEMAS
from src.shared.domain.errors import CaosError
from src.shared.presentation.app_context import AppContext
from src.shared.presentation.theme import (
    COLOR_ACENTO,
    COLOR_ACENTO_2,
    COLOR_FONDO,
    COLOR_PELIGRO,
    COLOR_SUPERFICIE,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
)
from src.shared.presentation.widgets import avisar, campo_texto, fecha_larga


class AppShell(ft.Column):
    """Contenedor de vistas con navegación inferior y feedback global."""

    def __init__(self, ctx: AppContext) -> None:
        super().__init__(expand=True, spacing=0)
        self.ctx = ctx
        self._indice = 0

        self._vistas = [TareasView(ctx), DeadlinesView(ctx), NotasView(ctx)]

        self._barra = ft.ProgressBar(
            value=0,
            height=8,
            border_radius=6,
            color=COLOR_ACENTO_2,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        )
        self._porcentaje = ft.Text("0%", size=20, weight=ft.FontWeight.W_800, color=COLOR_ACENTO_2)
        self._detalle_progreso = ft.Text("", size=11.5, color=COLOR_TEXTO_SUAVE)
        self._btn_sync = ft.IconButton(
            icon=ft.Icons.CLOUD_SYNC,
            icon_color=COLOR_TEXTO_SUAVE,
            tooltip="Sincronizar",
            on_click=self._abrir_sync,
        )

        self._contenido = ft.Container(
            content=self._vistas[0],
            expand=True,
            padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        )

        self._nav = ft.NavigationBar(
            selected_index=0,
            bgcolor=COLOR_SUPERFICIE,
            indicator_color=ft.Colors.with_opacity(0.18, COLOR_ACENTO),
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.CHECKLIST,
                    selected_icon=ft.Icons.DONE_ALL,
                    label="Tareas",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.FLAG_OUTLINED,
                    selected_icon=ft.Icons.FLAG,
                    label="Proyectos",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.NOTE_ALT_OUTLINED,
                    selected_icon=ft.Icons.NOTE_ALT,
                    label="Notas",
                ),
            ],
            on_change=self._cambiar_seccion,
        )

        self.controls = [
            self._cabecera(),
            self._tarjeta_progreso(),
            self._contenido,
            self._nav,
        ]

        for tema in TODOS_LOS_TEMAS:
            ctx.bus.suscribir(tema, self._on_cambio)

        self._actualizar_progreso()

    # -------------------------------------------------------------- layout
    def _cabecera(self) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.only(left=20, right=10, top=16, bottom=8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=1,
                        controls=[
                            ft.Row(
                                spacing=7,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        "CAOS",
                                        size=28,
                                        weight=ft.FontWeight.W_900,
                                        color=COLOR_TEXTO,
                                    ),
                                    ft.Container(
                                        bgcolor=ft.Colors.with_opacity(0.18, COLOR_ACENTO),
                                        border_radius=8,
                                        padding=ft.Padding.symmetric(horizontal=7, vertical=2),
                                        content=ft.Text(
                                            "3.0",
                                            size=11,
                                            weight=ft.FontWeight.W_800,
                                            color=COLOR_ACENTO,
                                        ),
                                    ),
                                ],
                            ),
                            ft.Text(fecha_larga(), size=11.5, color=COLOR_TEXTO_SUAVE),
                        ],
                    ),
                    self._btn_sync,
                ],
            ),
        )

    def _tarjeta_progreso(self) -> ft.Container:
        return ft.Container(
            margin=ft.Margin.only(left=18, right=18, top=4, bottom=8),
            padding=14,
            border_radius=18,
            bgcolor=COLOR_SUPERFICIE,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE)),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=1,
                                controls=[
                                    ft.Text(
                                        "Progreso de hoy",
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=COLOR_TEXTO,
                                    ),
                                    self._detalle_progreso,
                                ],
                            ),
                            self._porcentaje,
                        ],
                    ),
                    self._barra,
                ],
            ),
        )

    # ------------------------------------------------------------- eventos
    def _cambiar_seccion(self, e: ft.Event[ft.NavigationBar]) -> None:
        self.ir_a(e.control.selected_index or 0)

    def ir_a(self, indice: int) -> None:
        """Cambia de sección de forma programática (también útil en tests)."""
        indice = max(0, min(indice, len(self._vistas) - 1))
        self._indice = indice
        self._nav.selected_index = indice
        self._contenido.content = self._vistas[indice]
        self._vistas[indice].refrescar()
        self._contenido.update()
        try:
            self._nav.update()
        except Exception:  # pragma: no cover
            pass

    def _on_cambio(self, _payload=None) -> None:
        self._actualizar_progreso()

    def _actualizar_progreso(self) -> None:
        try:
            progreso = self.ctx.tareas.progreso_diario()
            pendientes = self.ctx.sync.total_pendientes()
        except Exception:  # pragma: no cover
            return

        self._barra.value = progreso.porcentaje
        self._porcentaje.value = f"{round(progreso.porcentaje * 100)}%"
        self._detalle_progreso.value = (
            f"{progreso.completadas_hoy} completadas · {progreso.pendientes} pendientes"
        )
        self._btn_sync.tooltip = (
            f"Sincronizar · {pendientes} pendientes" if pendientes else "Sincronizar · todo al día"
        )

        try:
            if self.page is not None:
                self._barra.update()
                self._porcentaje.update()
                self._detalle_progreso.update()
                self._btn_sync.update()
        except Exception:  # pragma: no cover
            pass

    # ------------------------------------------------------------ sync
    def _abrir_sync(self, _e=None) -> None:
        configurado = self.ctx.sync.configurado
        pendientes = self.ctx.sync.pendientes()
        total = sum(pendientes.values())

        detalle = ft.Text(
            (
                f"{total} registros pendientes\n"
                f"· Proyectos: {pendientes['deadlines']}\n"
                f"· Tareas: {pendientes['tareas']}\n"
                f"· Notas: {pendientes['notas']}"
            ),
            size=12.5,
            color=COLOR_TEXTO_SUAVE,
        )

        estado = ft.Text(
            (
                "Conexión con Turso lista."
                if configurado
                else "Turso no configurado. Escribe la URL y el token abajo."
            ),
            size=12,
            color=COLOR_ACENTO_2 if configurado else COLOR_PELIGRO,
        )

        auto_texto = ft.Text(
            "Sincronización automática activa: comprueba Internet y sincroniza "
            "cada 2 minutos mientras la app está abierta.",
            size=11,
            color=COLOR_TEXTO_SUAVE,
        )

        boton = ft.FilledButton(
            "Sincronizar ahora",
            icon=ft.Icons.CLOUD_SYNC,
            bgcolor=COLOR_ACENTO,
            color=ft.Colors.WHITE,
            disabled=not configurado,
            on_click=lambda e: self._sincronizar(estado, boton, detalle),
        )

        url_actual, token_actual = self.ctx.settings.turso_credenciales()

        campo_url = campo_texto(
            etiqueta="URL de Turso",
            valor=url_actual,
            pista="libsql://tu-base.turso.io",
        )
        campo_token = campo_texto(
            etiqueta="Token de Turso",
            valor=token_actual,
            pista="eyJhbGciOi...",
        )
        campo_token.password = True
        campo_token.can_reveal_password = True

        mensaje_config = ft.Text("", size=11.5, color=COLOR_TEXTO_SUAVE)

        boton_guardar = ft.FilledTonalButton(
            "Guardar",
            icon=ft.Icons.SAVE,
            on_click=lambda e: self._guardar_credenciales(
                campo_url, campo_token, estado, boton, mensaje_config
            ),
        )
        boton_probar = ft.TextButton(
            "Probar conexión",
            icon=ft.Icons.WIFI_TETHERING,
            on_click=lambda e: self._probar_credenciales(
                campo_url, campo_token, mensaje_config
            ),
        )

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Sincronización"),
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    width=400,
                    height=380,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        detalle,
                        ft.Text(
                            f"Base local: {self.ctx.db.path}",
                            size=10.5,
                            color=ft.Colors.with_opacity(0.6, COLOR_TEXTO_SUAVE),
                            selectable=True,
                        ),
                        estado,
                        auto_texto,
                        ft.Divider(height=1),
                        ft.Text(
                            "Conexión con Turso",
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=COLOR_TEXTO,
                        ),
                        ft.Text(
                            "Pega la URL y el token de tu base. Se guardan solo en este dispositivo.",
                            size=11,
                            color=COLOR_TEXTO_SUAVE,
                        ),
                        campo_url,
                        campo_token,
                        mensaje_config,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[boton_probar, boton_guardar],
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: self.page.pop_dialog()),
                    boton,
                ],
            )
        )

    def _guardar_credenciales(
        self,
        campo_url: ft.TextField,
        campo_token: ft.TextField,
        estado: ft.Text,
        boton: ft.FilledButton,
        mensaje: ft.Text,
    ) -> None:
        url = (campo_url.value or "").strip()
        token = (campo_token.value or "").strip()

        if not url or not token:
            mensaje.value = "Escribe la URL y el token antes de guardar."
            mensaje.color = COLOR_PELIGRO
            self.page.update()
            return

        self.ctx.settings.guardar_turso(url, token)
        self.ctx.sync.actualizar_credenciales(url, token)

        configurado = self.ctx.sync.configurado
        estado.value = (
            "Conexión con Turso lista." if configurado else "Faltan datos de Turso."
        )
        estado.color = COLOR_ACENTO_2 if configurado else COLOR_PELIGRO
        boton.disabled = not configurado

        mensaje.value = (
            "Credenciales guardadas. La sincronización automática empezará en breve."
        )
        mensaje.color = COLOR_ACENTO_2
        self.page.update()
        self._actualizar_progreso()
        self.ctx.auto_sync.solicitar()

    def _probar_credenciales(
        self,
        campo_url: ft.TextField,
        campo_token: ft.TextField,
        mensaje: ft.Text,
    ) -> None:
        url = (campo_url.value or "").strip()
        token = (campo_token.value or "").strip()

        if not url or not token:
            mensaje.value = "Escribe la URL y el token para probar."
            mensaje.color = COLOR_PELIGRO
            self.page.update()
            return

        mensaje.value = "Probando conexión con Turso..."
        mensaje.color = COLOR_TEXTO_SUAVE
        self.page.update()

        try:
            self.ctx.sync.probar_conexion(url, token)
        except CaosError as exc:
            mensaje.value = str(exc)
            mensaje.color = COLOR_PELIGRO
            self.page.update()
            return
        except Exception as exc:  # pragma: no cover
            mensaje.value = f"Error inesperado: {exc}"
            mensaje.color = COLOR_PELIGRO
            self.page.update()
            return

        mensaje.value = "Conexión correcta. Guarda para usar estas credenciales."
        mensaje.color = COLOR_ACENTO_2
        self.page.update()

    def _sincronizar(
        self,
        estado: ft.Text,
        boton: ft.FilledButton,
        detalle: ft.Text,
    ) -> None:
        boton.disabled = True
        estado.value = "Sincronizando con Turso..."
        estado.color = COLOR_TEXTO_SUAVE
        self.page.update()

        try:
            resultado = self.ctx.sync.sincronizar()
        except CaosError as exc:
            estado.value = str(exc)
            estado.color = COLOR_PELIGRO
            boton.disabled = False
            self.page.update()
            return
        except Exception as exc:  # pragma: no cover
            estado.value = f"Error inesperado: {exc}"
            estado.color = COLOR_PELIGRO
            boton.disabled = False
            self.page.update()
            return

        if resultado.hubo_cambios:
            partes = []
            if resultado.enviados:
                partes.append(f"{resultado.enviados} enviados")
            if resultado.recibidos:
                partes.append(f"{resultado.recibidos} recibidos")
            estado.value = "Listo. " + " · ".join(partes) + "."
        else:
            estado.value = "Todo estaba al día."

        pendientes = self.ctx.sync.pendientes()
        detalle.value = (
            f"{sum(pendientes.values())} registros pendientes\n"
            f"· Proyectos: {pendientes['deadlines']}\n"
            f"· Tareas: {pendientes['tareas']}\n"
            f"· Notas: {pendientes['notas']}"
        )

        estado.color = COLOR_ACENTO_2
        boton.disabled = False
        self.page.update()
        self._actualizar_progreso()
        avisar(self.page, "Sincronización completada.")
