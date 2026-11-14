"""Pruebas de la sincronización bidireccional con Turso (RF07)."""

from __future__ import annotations

import threading
import time

import pytest

from src.shared.application.event_bus import EventBus
from src.shared.application.events import SYNC_CAMBIADO, TAREAS_CAMBIADAS
from src.shared.application.sync_service import SyncService, UPSERT_TAREA
from src.shared.domain.errors import TursoNoConfigurado

AHORA = "2026-11-08T12:00:00+00:00"
ANTES = "2020-01-01T00:00:00+00:00"
DESPUES = "2099-01-01T00:00:00+00:00"


class FakeTurso:
    """Doble del cliente: registra el pipeline y devuelve filas prefijadas."""

    def __init__(self, configurado: bool = True, filas: dict | None = None) -> None:
        self.configurado = configurado
        self.llamadas: list[list[tuple[str, tuple]]] = []
        self.filas = filas or {"deadlines": [], "tareas": [], "notas": []}

    def ejecutar(self, sentencias):
        self.llamadas.append([(sql, tuple(params)) for sql, params in sentencias])
        return [
            self.filas["deadlines"],
            self.filas["tareas"],
            self.filas["notas"],
        ]


def _montar(
    db,
    deadlines_repo,
    tareas_repo,
    notas_repo,
    configurado=True,
    filas=None,
    bus=None,
):
    cliente = FakeTurso(configurado, filas)
    servicio = SyncService(cliente, deadlines_repo, tareas_repo, notas_repo, bus)
    return cliente, servicio


def _fila_deadline(**cambios) -> dict:
    fila = {
        "id": "d1",
        "titulo": "Proyecto remoto",
        "descripcion": "",
        "fecha_limite": None,
        "area": "General",
        "completado": 0,
        "deleted": 0,
        "synced": 1,
        "created_at": ANTES,
        "updated_at": AHORA,
    }
    fila.update(cambios)
    return fila


def _fila_tarea(**cambios) -> dict:
    fila = {
        "id": "t1",
        "titulo": "Tarea remota",
        "descripcion": "",
        "prioridad": 1,
        "completada": 0,
        "deadline_id": "d1",
        "deleted": 0,
        "synced": 1,
        "created_at": ANTES,
        "updated_at": AHORA,
    }
    fila.update(cambios)
    return fila


def _fila_nota(**cambios) -> dict:
    fila = {
        "id": "n1",
        "titulo": "Nota remota",
        "contenido": "Contenido",
        "area": "General",
        "deadline_id": "d1",
        "deleted": 0,
        "synced": 1,
        "created_at": ANTES,
        "updated_at": AHORA,
    }
    fila.update(cambios)
    return fila


def test_pendientes_iniciales(deadlines, tareas, notas, deadlines_repo, tareas_repo, notas_repo, db):
    deadlines.crear("Proyecto")
    tareas.crear("Tarea")
    notas.crear("Nota")

    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)

    assert sync.pendientes() == {"deadlines": 1, "tareas": 1, "notas": 1}
    assert sync.total_pendientes() == 3


def test_sincronizar_envia_en_orden_y_marca_synced(
    deadlines, tareas, notas, deadlines_repo, tareas_repo, notas_repo, db
):
    deadlines.crear("Proyecto")
    tareas.crear("Tarea")
    notas.crear("Nota")
    cliente, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)

    resultado = sync.sincronizar()

    assert resultado.enviados == 3
    assert resultado.recibidos == 0
    assert resultado.hubo_cambios is True
    assert resultado.detalle == {"deadlines": 1, "tareas": 1, "notas": 1}
    assert len(cliente.llamadas) == 1

    sentencias = cliente.llamadas[0]
    assert len(sentencias) == 3 + 3 + 3  # esquema + 3 upserts + 3 lecturas
    sqls = [sql for sql, _ in sentencias]
    idx_deadline = next(i for i, s in enumerate(sqls) if "INSERT INTO deadlines" in s)
    idx_tarea = next(i for i, s in enumerate(sqls) if "INSERT INTO tareas" in s)
    idx_nota = next(i for i, s in enumerate(sqls) if "INSERT INTO notas" in s)
    assert idx_deadline < idx_tarea < idx_nota
    assert any("FROM deadlines" in s for s in sqls)
    assert any("FROM tareas" in s for s in sqls)
    assert any("FROM notas" in s for s in sqls)

    assert sync.total_pendientes() == 0
    assert deadlines_repo.list_pending() == []
    assert tareas_repo.list_pending() == []
    assert notas_repo.list_pending() == []


def test_segunda_sincronizacion_solo_lee(
    deadlines_repo, tareas_repo, notas_repo, db
):
    cliente, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)

    resultado = sync.sincronizar()

    assert resultado.enviados == 0
    assert resultado.recibidos == 0
    # Aunque no haya nada que subir, hay que preguntar a la nube.
    assert len(cliente.llamadas) == 1
    sqls = [sql for sql, _ in cliente.llamadas[0]]
    assert not any("INSERT INTO" in sql for sql in sqls)
    assert any("FROM tareas" in sql for sql in sqls)


def test_borrado_logico_se_propaga(
    tareas, deadlines_repo, tareas_repo, notas_repo, db
):
    tarea = tareas.crear("Se va a borrar")
    cliente, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)
    sync.sincronizar()

    tareas.eliminar(tarea.id)
    assert len(tareas_repo.list_pending()) == 1

    sync.sincronizar()

    sentencias = cliente.llamadas[-1]
    upsert = next(s for s in sentencias if "INSERT INTO tareas" in s[0])
    params = upsert[1]
    # Orden: id, titulo, descripcion, prioridad, completada, deadline_id, deleted, ...
    assert params[6] == 1


def test_sin_configuracion_lanza_error(deadlines_repo, tareas_repo, notas_repo, db):
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo, configurado=False)
    with pytest.raises(TursoNoConfigurado):
        sync.sincronizar()


def test_error_de_red_no_marca_synced(tareas, deadlines_repo, tareas_repo, notas_repo, db):
    tareas.crear("Pendiente")

    class TursoRoto(FakeTurso):
        def ejecutar(self, sentencias):
            raise RuntimeError("boom")

    servicio = SyncService(
        TursoRoto(), deadlines_repo, tareas_repo, notas_repo
    )

    with pytest.raises(RuntimeError):
        servicio.sincronizar()

    assert len(tareas_repo.list_pending()) == 1


def test_actualizar_credenciales_delega_en_el_cliente(
    deadlines_repo, tareas_repo, notas_repo, db
):
    class TursoConCredenciales(FakeTurso):
        def __init__(self) -> None:
            super().__init__(True)
            self.credenciales: tuple[str, str] | None = None

        def actualizar_credenciales(self, url: str, token: str) -> None:
            self.credenciales = (url, token)

    cliente = TursoConCredenciales()
    servicio = SyncService(cliente, deadlines_repo, tareas_repo, notas_repo)

    servicio.actualizar_credenciales("https://caos.turso.io", "token")

    assert cliente.credenciales == ("https://caos.turso.io", "token")


def test_instalacion_nueva_baja_datos_de_la_nube(
    deadlines_repo, tareas_repo, notas_repo, db
):
    """Un teléfono recién instalado debe recibir todo lo que ya está en Turso."""
    filas = {
        "deadlines": [_fila_deadline()],
        "tareas": [_fila_tarea()],
        "notas": [_fila_nota()],
    }
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo, filas=filas)

    resultado = sync.sincronizar()

    assert resultado.enviados == 0
    assert resultado.recibidos == 3
    assert resultado.detalle_recibidos == {
        "deadlines": 1,
        "tareas": 1,
        "notas": 1,
    }
    assert resultado.hubo_cambios is True

    assert [d.id for d in deadlines_repo.list_all()] == ["d1"]
    assert [t.id for t in tareas_repo.list_all()] == ["t1"]
    assert [n.id for n in notas_repo.list_all()] == ["n1"]
    assert sync.total_pendientes() == 0

    # Una segunda pasada con las mismas filas no vuelve a escribir.
    resultado2 = sync.sincronizar()
    assert resultado2.recibidos == 0


def test_pull_no_pisa_un_cambio_local_mas_nuevo(
    tareas, tareas_repo, deadlines_repo, notas_repo, db
):
    local = tareas.crear("Versión local")
    filas = {
        "deadlines": [],
        "tareas": [_fila_tarea(id=local.id, titulo="Versión vieja", deadline_id=None, updated_at=ANTES)],
        "notas": [],
    }
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo, filas=filas)

    resultado = sync.sincronizar()

    assert resultado.recibidos == 0
    assert tareas_repo.get(local.id).titulo == "Versión local"
    assert sync.total_pendientes() == 0


def test_pull_aplica_un_borrado_remoto(
    tareas, deadlines_repo, tareas_repo, notas_repo, db
):
    local = tareas.crear("Se borró en otro dispositivo")
    cliente, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)
    sync.sincronizar()

    cliente.filas = {
        "deadlines": [],
        "tareas": [
            _fila_tarea(
                id=local.id,
                titulo=local.titulo,
                deadline_id=None,
                deleted=1,
                updated_at=DESPUES,
            )
        ],
        "notas": [],
    }

    resultado = sync.sincronizar()

    assert resultado.recibidos == 1
    assert tareas_repo.get(local.id) is None
    assert tareas_repo.list_all() == []
    assert sync.total_pendientes() == 0


def test_upsert_remoto_conserva_la_version_mas_nueva(db):
    """El SQL de subida solo actualiza si la marca de tiempo es más reciente."""
    db.execute(
        UPSERT_TAREA,
        (
            "t1",
            "Nueva",
            "",
            1,
            0,
            None,
            0,
            ANTES,
            DESPUES,
        ),
    )
    db.execute(
        UPSERT_TAREA,
        (
            "t1",
            "Vieja",
            "",
            1,
            0,
            None,
            0,
            ANTES,
            ANTES,
        ),
    )

    fila = db.query_one("SELECT titulo FROM tareas WHERE id = ?", ("t1",))
    assert fila["titulo"] == "Nueva"


def test_subida_publica_solo_el_evento_de_estado(
    tareas, deadlines_repo, tareas_repo, notas_repo, db
):
    """Al subir no hay que refrescar las listas, solo el contador de pendientes."""
    bus = EventBus()
    eventos: list[str] = []
    bus.suscribir(SYNC_CAMBIADO, lambda _p: eventos.append(SYNC_CAMBIADO))
    bus.suscribir(TAREAS_CAMBIADAS, lambda _p: eventos.append(TAREAS_CAMBIADAS))

    tareas.crear("Tarea")
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo, bus=bus)

    sync.sincronizar()

    assert eventos == [SYNC_CAMBIADO]


def test_pull_publica_eventos_de_dominio_y_de_estado(
    deadlines_repo, tareas_repo, notas_repo, db
):
    bus = EventBus()
    eventos: list[str] = []
    bus.suscribir(SYNC_CAMBIADO, lambda _p: eventos.append(SYNC_CAMBIADO))
    bus.suscribir(TAREAS_CAMBIADAS, lambda _p: eventos.append(TAREAS_CAMBIADAS))

    filas = {
        "deadlines": [],
        "tareas": [_fila_tarea(deadline_id=None)],
        "notas": [],
    }
    _, sync = _montar(
        db, deadlines_repo, tareas_repo, notas_repo, filas=filas, bus=bus
    )

    sync.sincronizar()

    assert TAREAS_CAMBIADAS in eventos
    assert SYNC_CAMBIADO in eventos


def test_sincronizar_si_libre_devuelve_none_si_esta_ocupado(
    deadlines_repo, tareas_repo, notas_repo, db
):
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)
    sync._lock.acquire()
    try:
        assert sync.sincronizar_si_libre() is None
    finally:
        sync._lock.release()


def test_sincronizar_si_libre_con_timeout_espera_el_candado(
    deadlines_repo, tareas_repo, notas_repo, db
):
    _, sync = _montar(db, deadlines_repo, tareas_repo, notas_repo)
    sync._lock.acquire()
    liberado = threading.Event()

    def liberar() -> None:
        time.sleep(0.05)
        sync._lock.release()
        liberado.set()

    hilo = threading.Thread(target=liberar)
    hilo.start()
    try:
        resultado = sync.sincronizar_si_libre(timeout=1.0)
    finally:
        hilo.join()

    assert liberado.is_set()
    assert resultado is not None
