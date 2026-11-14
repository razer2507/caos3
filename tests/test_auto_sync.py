"""Pruebas del sincronizador automático."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import flet as ft

from src.domains.tareas.application.tarea_service import TareaService
from src.shared.application.auto_sync import AutoSync
from src.shared.application.event_bus import EventBus
from src.shared.application.events import DATOS_CAMBIADOS
from src.shared.application.sync_service import ResultadoSync, SyncService
from src.shared.domain.errors import ErrorDeSincronizacion


class FakeSync:
    def __init__(
        self, configurado: bool = True, resultado=None, pendientes: int = 1
    ) -> None:
        self.configurado = configurado
        self.resultado = resultado if resultado is not None else ResultadoSync()
        self.pendientes = pendientes
        self.llamadas: list[bool] = []
        self.timeouts: list[float | None] = []

    def total_pendientes(self) -> int:
        return self.pendientes

    def sincronizar_si_libre(
        self, *, publicar_eventos: bool = True, timeout: float | None = None
    ):
        self.llamadas.append(publicar_eventos)
        self.timeouts.append(timeout)
        return self.resultado


class FakeBus:
    def __init__(self) -> None:
        self.temas: list[str] = []
        self.suscritos: dict[str, list] = {}

    def publicar(self, tema: str, payload=None) -> None:
        self.temas.append(tema)
        for callback in list(self.suscritos.get(tema, ())):
            callback(payload)

    def suscribir(self, tema: str, callback) -> None:
        self.suscritos.setdefault(tema, [])
        if callback not in self.suscritos[tema]:
            self.suscritos[tema].append(callback)

    def desuscribir(self, tema: str, callback) -> None:
        if callback in self.suscritos.get(tema, ()):
            self.suscritos[tema].remove(callback)


class FakeFuture:
    def __init__(self) -> None:
        self.cancelada = False

    def cancel(self) -> None:
        self.cancelada = True


class FakeWindow:
    def __init__(self) -> None:
        self.prevent_close = False
        self.on_event = None
        self.destruida = False

    async def destroy(self) -> None:
        self.destruida = True


class FakePage:
    def __init__(self, platform=None) -> None:
        self.tareas = []
        self.on_app_lifecycle_state_change = None
        self.window = FakeWindow()
        self.platform = platform
        self.web = False
        self.embedded = False
        self.actualizada = False

    def run_task(self, handler, *args, **kwargs):
        self.tareas.append((handler, args, kwargs))
        return FakeFuture()

    def update(self) -> None:
        self.actualizada = True


def _auto(sync=None, bus=None, internet=True, **kwargs) -> AutoSync:
    return AutoSync(
        sync or FakeSync(),
        bus,
        comprobar_conexion=lambda: internet,
        **kwargs,
    )


def test_sin_credenciales_no_hace_nada():
    sync = FakeSync(configurado=False)

    assert asyncio.run(_auto(sync).sincronizar_ahora()) is None
    assert sync.llamadas == []


def test_sin_internet_no_llama_a_turso():
    sync = FakeSync()

    assert asyncio.run(_auto(sync, internet=False).sincronizar_ahora()) is None
    assert sync.llamadas == []


def test_sincroniza_y_publica_eventos():
    bus = FakeBus()
    sync = FakeSync(resultado=ResultadoSync(enviados=1, recibidos=2))

    resultado = asyncio.run(_auto(sync, bus).sincronizar_ahora())

    assert resultado is sync.resultado
    # El servicio no publica por su cuenta: lo hace AutoSync en el hilo del bucle.
    assert sync.llamadas == [False]
    assert "sync.cambiado" in bus.temas
    assert "tareas.cambiadas" in bus.temas
    assert "deadlines.cambiados" in bus.temas


def test_sin_cambios_no_publica_eventos():
    bus = FakeBus()

    resultado = asyncio.run(_auto(FakeSync(), bus).sincronizar_ahora())

    assert resultado is not None
    assert resultado.hubo_cambios is False
    assert bus.temas == []


def test_si_otra_sincronizacion_esta_en_curso_no_publica():
    bus = FakeBus()

    class SyncOcupado(FakeSync):
        def sincronizar_si_libre(self, *, publicar_eventos: bool = True, timeout=None):
            self.llamadas.append(publicar_eventos)
            return None

    assert asyncio.run(_auto(SyncOcupado(), bus).sincronizar_ahora()) is None
    assert bus.temas == []


def test_error_de_sincronizacion_se_registra_y_no_propaga():
    class SyncRoto(FakeSync):
        def sincronizar_si_libre(self, *, publicar_eventos: bool = True, timeout=None):
            raise ErrorDeSincronizacion("Turso no responde")

    bus = FakeBus()

    assert asyncio.run(_auto(SyncRoto(), bus).sincronizar_ahora()) is None
    assert bus.temas == []


def test_iniciar_programa_el_bucle_y_escucha_cambios():
    bus = FakeBus()
    page = FakePage()
    auto = _auto(bus=bus, debounce=0)
    auto.iniciar(page)

    assert page.on_app_lifecycle_state_change is not None
    assert len(page.tareas) == 1
    assert DATOS_CAMBIADOS in bus.suscritos

    auto.detener()
    assert DATOS_CAMBIADOS not in bus.suscritos.get(DATOS_CAMBIADOS, [])


def test_reanudar_pide_sincronizar_y_pausar_hace_pasada_final():
    page = FakePage()
    auto = _auto()
    auto.iniciar(page)

    assert len(page.tareas) == 1

    page.on_app_lifecycle_state_change(
        SimpleNamespace(state=ft.AppLifecycleState.RESUME)
    )
    assert len(page.tareas) == 2

    # Pausar u ocultar programa una última pasada.
    page.on_app_lifecycle_state_change(
        SimpleNamespace(state=ft.AppLifecycleState.PAUSE)
    )
    assert len(page.tareas) == 3

    tarea = auto._tarea
    auto.detener()
    assert tarea.cancelada is True
    assert auto._page is None


def test_cambio_local_programa_una_sincronizacion_con_debounce():
    bus = FakeBus()
    sync = FakeSync()
    page = FakePage()
    auto = _auto(sync, bus, debounce=0)
    auto.iniciar(page)

    antes = len(page.tareas)
    bus.publicar(DATOS_CAMBIADOS)

    assert len(page.tareas) == antes + 1
    handler, args, kwargs = page.tareas[-1]
    asyncio.run(handler(*args, **kwargs))

    assert sync.llamadas == [False]
    auto.detener()


def test_cambio_local_sin_pendientes_no_sincroniza():
    bus = FakeBus()
    sync = FakeSync(pendientes=0)
    page = FakePage()
    auto = _auto(sync, bus, debounce=0)
    auto.iniciar(page)

    bus.publicar(DATOS_CAMBIADOS)
    handler, args, kwargs = page.tareas[-1]
    asyncio.run(handler(*args, **kwargs))

    assert sync.llamadas == []
    auto.detener()


def test_varios_cambios_seguidos_reinician_el_debounce():
    bus = FakeBus()
    page = FakePage()
    auto = _auto(bus=bus, debounce=0)
    auto.iniciar(page)

    bus.publicar(DATOS_CAMBIADOS)
    primera = auto._tarea_debounce
    bus.publicar(DATOS_CAMBIADOS)

    assert primera.cancelada is True
    assert auto._tarea_debounce is not primera
    auto.detener()


def test_pasada_final_espera_el_candado():
    sync = FakeSync()
    page = FakePage()
    auto = _auto(sync, espera_candado=7.5)
    auto.iniciar(page)

    page.on_app_lifecycle_state_change(
        SimpleNamespace(state=ft.AppLifecycleState.HIDE)
    )
    handler, args, kwargs = page.tareas[-1]
    assert handler.__name__ == "_sincronizar_final"

    asyncio.run(handler(*args, **kwargs))

    assert sync.llamadas == [False]
    assert sync.timeouts == [7.5]
    auto.detener()


def test_escritorio_intercepta_el_cierre_y_sincroniza_antes_de_destruir():
    bus = FakeBus()
    sync = FakeSync()
    page = FakePage(platform=ft.PagePlatform.WINDOWS)
    auto = _auto(sync, bus)
    auto.iniciar(page)

    assert page.window.prevent_close is True
    assert page.window.on_event is not None
    assert page.actualizada is True

    page.window.on_event(SimpleNamespace(type=ft.WindowEventType.CLOSE))
    handler, args, kwargs = page.tareas[-1]
    assert handler.__name__ == "_cerrar"

    asyncio.run(handler(*args, **kwargs))

    assert sync.llamadas == [False]
    assert page.window.destruida is True
    auto.detener()


def test_movil_no_intercepta_el_cierre_de_ventana():
    page = FakePage(platform=ft.PagePlatform.ANDROID)
    auto = _auto()
    auto.iniciar(page)

    assert page.window.prevent_close is False
    assert page.window.on_event is None
    auto.detener()


def test_solicitar_antes_de_iniciar_no_falla():
    _auto().solicitar()


def test_intervalo_minimo_para_no_gastar_bateria():
    auto = _auto(intervalo=1)

    assert auto._intervalo == 30.0


def test_espera_inicial_corta_para_subir_cambios_pronto():
    assert _auto()._espera_inicial == 1.0


class FakeTurso:
    configurado = True

    def ejecutar(self, sentencias):
        # Tres SELECT finales (deadlines, tareas, notas) sin filas remotas.
        return [[], [], []]


def test_un_cambio_local_real_se_sube_con_el_debounce(
    db, deadlines_repo, tareas_repo, notas_repo
):
    """Integra el bus, el servicio real y el debounce: la tarea queda subida."""
    bus = EventBus()
    sync = SyncService(FakeTurso(), deadlines_repo, tareas_repo, notas_repo, bus)
    servicio = TareaService(tareas_repo, bus)
    page = FakePage()
    auto = AutoSync(
        sync, bus, debounce=0, comprobar_conexion=lambda: True
    )
    auto.iniciar(page)

    servicio.crear("Tarea creada en el PC")
    assert sync.total_pendientes() == 1

    handler, args, kwargs = page.tareas[-1]
    asyncio.run(handler(*args, **kwargs))

    assert sync.total_pendientes() == 0
    auto.detener()
