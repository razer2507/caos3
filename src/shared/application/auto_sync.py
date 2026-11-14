"""Sincronización automática mientras la app está abierta.

Además del bucle periódico, el sincronizador escucha ``DATOS_CAMBIADOS`` y sube
los cambios locales pocos segundos después de que se produzcan (*debounce*).
También hace una última pasada cuando la app pasa a segundo plano o se cierra:
en escritorio se intercepta el cierre de la ventana para no perder cambios.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Callable

import flet as ft

from src.shared.application.event_bus import EventBus
from src.shared.application.events import DATOS_CAMBIADOS
from src.shared.application.sync_service import (
    ResultadoSync,
    SyncService,
    publicar_resultado,
)
from src.shared.domain.errors import CaosError
from src.shared.infrastructure.connectivity import hay_internet

logger = logging.getLogger(__name__)

INTERVALO_POR_DEFECTO = 120.0
ESPERA_INICIAL_POR_DEFECTO = 1.0
DEBOUNCE_POR_DEFECTO = 2.0
ESPERA_CANDADO_POR_DEFECTO = 10.0

_PLATAFORMAS_ESCRITORIO = frozenset(
    {
        ft.PagePlatform.WINDOWS,
        ft.PagePlatform.LINUX,
        ft.PagePlatform.MACOS,
    }
)


class AutoSync:
    """Ejecuta ``SyncService`` cada cierto tiempo y ante cambios locales."""

    def __init__(
        self,
        sync: SyncService,
        bus: EventBus | None = None,
        *,
        intervalo: float = INTERVALO_POR_DEFECTO,
        espera_inicial: float = ESPERA_INICIAL_POR_DEFECTO,
        debounce: float = DEBOUNCE_POR_DEFECTO,
        espera_candado: float = ESPERA_CANDADO_POR_DEFECTO,
        comprobar_conexion: Callable[[], bool] | None = None,
    ) -> None:
        self._sync = sync
        self._bus = bus
        # Un intervalo demasiado corto solo gastaría batería y datos.
        self._intervalo = max(30.0, intervalo)
        self._espera_inicial = max(0.0, espera_inicial)
        self._debounce = max(0.0, debounce)
        self._espera_candado = max(0.0, espera_candado)
        self._comprobar_conexion = comprobar_conexion or hay_internet
        self._page: ft.Page | None = None
        self._tarea = None
        self._tarea_debounce = None
        self._tarea_final = None
        self._generacion_debounce = 0
        self._cerrando = False

    # ------------------------------------------------------------- ciclo
    def iniciar(self, page: ft.Page) -> None:
        """Arranca el bucle, escucha cambios locales y prepara el cierre."""
        if self._tarea is not None:
            return
        self._page = page
        if self._bus is not None:
            self._bus.suscribir(DATOS_CAMBIADOS, self._on_datos_cambiados)
        page.on_app_lifecycle_state_change = self._on_lifecycle
        self._configurar_cierre(page)
        self._tarea = page.run_task(self._bucle)
        logger.info(
            "Sincronización automática activa cada %s segundos", int(self._intervalo)
        )

    def detener(self) -> None:
        """Cancela el bucle y las tareas pendientes (útil al cerrar o en pruebas)."""
        if self._bus is not None:
            self._bus.desuscribir(DATOS_CAMBIADOS, self._on_datos_cambiados)
        for nombre in ("_tarea", "_tarea_debounce", "_tarea_final"):
            tarea = getattr(self, nombre)
            if tarea is not None:
                tarea.cancel()
                setattr(self, nombre, None)
        self._page = None

    async def _bucle(self) -> None:
        await asyncio.sleep(self._espera_inicial)
        while True:
            await self.sincronizar_ahora()
            await asyncio.sleep(self._intervalo)

    async def sincronizar_ahora(self) -> ResultadoSync | None:
        """Hace una pasada si hay credenciales, red y no hay otra en curso."""
        return await self._pasada(timeout=None, motivo="automática")

    async def _pasada(
        self, *, timeout: float | None, motivo: str
    ) -> ResultadoSync | None:
        if not self._sync.configurado:
            return None

        if not await asyncio.to_thread(self._comprobar_conexion):
            logger.info(
                "Sin Internet; se reintentará en %s segundos", int(self._intervalo)
            )
            return None

        try:
            resultado = await asyncio.to_thread(
                self._sync.sincronizar_si_libre,
                publicar_eventos=False,
                timeout=timeout,
            )
        except CaosError as exc:
            logger.warning("Sincronización %s fallida: %s", motivo, exc)
            return None
        except Exception:  # pragma: no cover - defensa ante fallos inesperados
            logger.exception("Error inesperado en la sincronización %s", motivo)
            return None

        if resultado is None:
            logger.debug(
                "Ya hay una sincronización en curso; se omite la pasada %s", motivo
            )
            return None

        if resultado.hubo_cambios:
            logger.info(
                "Sincronización %s: %s enviados, %s recibidos",
                motivo,
                resultado.enviados,
                resultado.recibidos,
            )
            if self._bus is not None:
                publicar_resultado(self._bus, resultado)

        return resultado

    def solicitar(self) -> None:
        """Pide una pasada inmediata sin bloquear el hilo de la UI."""
        if self._page is None:
            return
        try:
            self._page.run_task(self.sincronizar_ahora)
        except Exception:  # pragma: no cover - la página pudo cerrarse
            logger.debug("No se pudo programar la sincronización inmediata")

    # ------------------------------------------------- cambios locales
    def _on_datos_cambiados(self, _payload=None) -> None:
        """Programa una subida tras un cambio local, reiniciando el debounce."""
        if self._page is None:
            return
        self._generacion_debounce += 1
        generacion = self._generacion_debounce
        if self._tarea_debounce is not None:
            self._tarea_debounce.cancel()
            self._tarea_debounce = None
        try:
            self._tarea_debounce = self._page.run_task(
                self._sincronizar_tras_debounce, generacion
            )
        except Exception:  # pragma: no cover - la página pudo cerrarse
            logger.debug("No se pudo programar la sincronización tras el cambio")

    async def _sincronizar_tras_debounce(self, generacion: int) -> None:
        try:
            if self._debounce:
                await asyncio.sleep(self._debounce)
            # Si llegó otro cambio mientras esperábamos, esa tarea es la válida.
            if generacion != self._generacion_debounce:
                return
            pendientes = await asyncio.to_thread(self._sync.total_pendientes)
            if pendientes:
                # Espera al candado por si el bucle ya está subiendo otra cosa:
                # así el cambio recién hecho no se queda para dentro de 120 s.
                await self._pasada(
                    timeout=self._espera_candado, motivo="por cambio local"
                )
        except asyncio.CancelledError:
            raise
        except Exception:  # pragma: no cover - defensa ante fallos inesperados
            logger.exception("Error en la sincronización tras un cambio local")
        finally:
            if generacion == self._generacion_debounce:
                self._tarea_debounce = None

    # -------------------------------------------------------- cierre
    def _programar_final(self) -> None:
        """Programa una última pasada si la app se oculta o se cierra."""
        if self._page is None or self._tarea_final is not None:
            return
        try:
            self._tarea_final = self._page.run_task(self._sincronizar_final)
        except Exception:  # pragma: no cover - la página pudo cerrarse
            logger.debug("No se pudo programar la sincronización final")

    async def _sincronizar_final(self) -> ResultadoSync | None:
        """Sube los cambios pendientes antes de que la app deje de ejecutarse."""
        try:
            pendientes = await asyncio.to_thread(self._sync.total_pendientes)
            if not pendientes:
                return None
            return await self._pasada(
                timeout=self._espera_candado, motivo="final"
            )
        except asyncio.CancelledError:
            raise
        except Exception:  # pragma: no cover - defensa ante fallos inesperados
            logger.exception("Error en la sincronización final")
            return None
        finally:
            self._tarea_final = None

    # --------------------------------------------------- ciclo de vida
    def _on_lifecycle(self, e: ft.AppLifecycleStateChangeEvent) -> None:
        if e.state in (ft.AppLifecycleState.RESUME, ft.AppLifecycleState.SHOW):
            self.solicitar()
        elif e.state in (
            ft.AppLifecycleState.HIDE,
            ft.AppLifecycleState.PAUSE,
            ft.AppLifecycleState.DETACH,
        ):
            self._programar_final()

    # ------------------------------------------------- cierre de ventana
    def _configurar_cierre(self, page: ft.Page) -> None:
        """En escritorio intercepta el cierre para sincronizar antes de salir."""
        if not self._es_escritorio(page):
            return
        ventana = getattr(page, "window", None)
        if ventana is None:
            return
        try:
            ventana.prevent_close = True
            ventana.on_event = self._on_window_event
            page.update()
        except Exception:  # pragma: no cover - depende de la plataforma
            logger.debug("No se pudo interceptar el cierre de la ventana")

    @staticmethod
    def _es_escritorio(page: ft.Page) -> bool:
        return (
            getattr(page, "platform", None) in _PLATAFORMAS_ESCRITORIO
            and not getattr(page, "web", False)
            and not getattr(page, "embedded", False)
        )

    def _on_window_event(self, e) -> None:
        if getattr(e, "type", None) != ft.WindowEventType.CLOSE:
            return
        if self._cerrando or self._page is None:
            return
        self._cerrando = True
        try:
            self._page.run_task(self._cerrar)
        except Exception:  # pragma: no cover - la página pudo cerrarse
            self._cerrando = False
            logger.debug("No se pudo programar el cierre con sincronización")

    async def _cerrar(self) -> None:
        """Espera la sincronización final y destruye la ventana."""
        try:
            if self._tarea_final is not None:
                try:
                    await self._tarea_final
                except asyncio.CancelledError:
                    raise
                except Exception:  # pragma: no cover - no debe impedir el cierre
                    logger.exception("La sincronización final falló antes de cerrar")
            else:
                await self._sincronizar_final()
        finally:
            page = self._page
            if page is not None:
                try:
                    await page.window.destroy()
                except Exception:  # pragma: no cover - depende de la plataforma
                    logger.debug("No se pudo destruir la ventana")
