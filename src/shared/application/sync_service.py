"""Sincronización bidireccional entre SQLite local y Turso."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from threading import Lock
from typing import Sequence

from src.shared.application.events import (
    DATOS_CAMBIADOS,
    DEADLINES_CAMBIADOS,
    NOTAS_CAMBIADAS,
    SYNC_CAMBIADO,
    TAREAS_CAMBIADAS,
)
from src.shared.domain.errors import TursoNoConfigurado
from src.shared.infrastructure.turso_client import TursoClient

logger = logging.getLogger(__name__)

TURSO_SCHEMA_SENTENCIAS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS deadlines (
        id            TEXT PRIMARY KEY,
        titulo        TEXT NOT NULL,
        descripcion   TEXT NOT NULL DEFAULT '',
        fecha_limite  TEXT,
        area          TEXT NOT NULL DEFAULT 'General',
        completado    INTEGER NOT NULL DEFAULT 0,
        deleted       INTEGER NOT NULL DEFAULT 0,
        synced        INTEGER NOT NULL DEFAULT 0,
        created_at    TEXT NOT NULL,
        updated_at    TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tareas (
        id            TEXT PRIMARY KEY,
        titulo        TEXT NOT NULL,
        descripcion   TEXT NOT NULL DEFAULT '',
        prioridad     INTEGER NOT NULL,
        completada    INTEGER NOT NULL DEFAULT 0,
        deadline_id   TEXT,
        fecha         TEXT,
        deleted       INTEGER NOT NULL DEFAULT 0,
        synced        INTEGER NOT NULL DEFAULT 0,
        created_at    TEXT NOT NULL,
        updated_at    TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS notas (
        id            TEXT PRIMARY KEY,
        titulo        TEXT NOT NULL,
        contenido     TEXT NOT NULL DEFAULT '',
        area          TEXT NOT NULL DEFAULT 'General',
        deadline_id   TEXT,
        deleted       INTEGER NOT NULL DEFAULT 0,
        synced        INTEGER NOT NULL DEFAULT 0,
        created_at    TEXT NOT NULL,
        updated_at    TEXT NOT NULL
    )
    """,
)


def _sentencias_esquema() -> list[tuple[str, Sequence[object]]]:
    return [(sql.strip(), ()) for sql in TURSO_SCHEMA_SENTENCIAS]


# Lecturas para el pull. Incluyen ``deleted`` y ``synced`` para poder aplicar
# borrados lógicos y dejar la fila local como sincronizada.
SELECT_DEADLINES = """
SELECT id, titulo, descripcion, fecha_limite, area, completado,
       deleted, synced, created_at, updated_at
FROM deadlines
"""

SELECT_TAREAS = """
SELECT id, titulo, descripcion, prioridad, completada, deadline_id, fecha,
       deleted, synced, created_at, updated_at
FROM tareas
"""

SELECT_NOTAS = """
SELECT id, titulo, contenido, area, deadline_id,
       deleted, synced, created_at, updated_at
FROM notas
"""


UPSERT_DEADLINE = """
INSERT INTO deadlines
    (id, titulo, descripcion, fecha_limite, area, completado,
     deleted, synced, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo = excluded.titulo,
    descripcion = excluded.descripcion,
    fecha_limite = excluded.fecha_limite,
    area = excluded.area,
    completado = excluded.completado,
    deleted = excluded.deleted,
    synced = 1,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > deadlines.updated_at
"""

UPSERT_TAREA = """
INSERT INTO tareas
    (id, titulo, descripcion, prioridad, completada, deadline_id, fecha,
     deleted, synced, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo = excluded.titulo,
    descripcion = excluded.descripcion,
    prioridad = excluded.prioridad,
    completada = excluded.completada,
    deadline_id = excluded.deadline_id,
    fecha = excluded.fecha,
    deleted = excluded.deleted,
    synced = 1,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > tareas.updated_at
"""

UPSERT_NOTA = """
INSERT INTO notas
    (id, titulo, contenido, area, deadline_id,
     deleted, synced, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo = excluded.titulo,
    contenido = excluded.contenido,
    area = excluded.area,
    deadline_id = excluded.deadline_id,
    deleted = excluded.deleted,
    synced = 1,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > notas.updated_at
"""


@dataclass(frozen=True)
class ResultadoSync:
    enviados: int = 0
    recibidos: int = 0
    detalle: dict[str, int] = field(default_factory=dict)
    detalle_recibidos: dict[str, int] = field(default_factory=dict)

    @property
    def hubo_cambios(self) -> bool:
        return self.enviados > 0 or self.recibidos > 0


class SyncService:
    """Sube cambios locales y baja los cambios hechos en otros dispositivos.

    La resolución de conflictos es *last-write-wins*: gana el registro con el
    ``updated_at`` más reciente. El filtro se aplica tanto al subir (para no
    pisar una versión más nueva de la nube) como al bajar.
    """

    def __init__(self, cliente: TursoClient, deadlines, tareas, notas, bus=None) -> None:
        self._cliente = cliente
        self._deadlines = deadlines
        self._tareas = tareas
        self._notas = notas
        self._bus = bus
        # Evita que la sincronización manual y la automática se pisen.
        self._lock = Lock()

    @property
    def configurado(self) -> bool:
        return self._cliente.configurado

    def actualizar_credenciales(self, url: str, token: str) -> None:
        """Aplica credenciales nuevas sin reiniciar la aplicación."""
        self._cliente.actualizar_credenciales(url, token)

    def probar_conexion(self, url: str, token: str) -> None:
        """Valida credenciales contra Turso sin guardarlas ni sincronizar."""
        TursoClient(url, token).ping()

    def pendientes(self) -> dict[str, int]:
        return {
            "deadlines": len(self._deadlines.list_pending()),
            "tareas": len(self._tareas.list_pending()),
            "notas": len(self._notas.list_pending()),
        }

    def total_pendientes(self) -> int:
        return sum(self.pendientes().values())

    def sincronizar(self, *, publicar_eventos: bool = True) -> ResultadoSync:
        """Sincroniza esperando a que termine cualquier otra sincronización.

        Es la entrada que usa el botón manual. Si la sincronización automática
        está en curso, esta llamada espera a que libere el candado.
        """
        with self._lock:
            return self._sincronizar(publicar_eventos=publicar_eventos)

    def sincronizar_si_libre(
        self, *, publicar_eventos: bool = True, timeout: float | None = None
    ) -> ResultadoSync | None:
        """Sincroniza solo si no hay otra pasada en curso.

        Devuelve ``None`` cuando ya hay una sincronización ejecutándose. Lo usa
        el sincronizador automático para no encolar peticiones duplicadas.

        ``timeout`` permite esperar hasta esos segundos a que se libere el
        candado; es lo que usa la sincronización final al cerrar la app para no
        perder un cambio que se está subiendo en ese momento. Con ``None`` no
        se espera.
        """
        if timeout is None:
            adquirido = self._lock.acquire(blocking=False)
        else:
            adquirido = self._lock.acquire(timeout=max(0.0, timeout))
        if not adquirido:
            return None
        try:
            return self._sincronizar(publicar_eventos=publicar_eventos)
        finally:
            self._lock.release()

    def _sincronizar(self, *, publicar_eventos: bool) -> ResultadoSync:
        if not self.configurado:
            raise TursoNoConfigurado(
                "Turso no está configurado. Abre el diálogo de sincronización "
                "y escribe la URL y el token."
            )

        deadlines = self._deadlines.list_pending()
        tareas = self._tareas.list_pending()
        notas = self._notas.list_pending()

        sentencias: list[tuple[str, Sequence[object]]] = list(_sentencias_esquema())

        # El orden respeta la FK lógica: primero deadlines, luego tareas/notas.
        for d in deadlines:
            sentencias.append(
                (
                    UPSERT_DEADLINE,
                    (
                        d.id,
                        d.titulo,
                        d.descripcion,
                        d.fecha_limite.isoformat() if d.fecha_limite else None,
                        d.area,
                        int(d.completado),
                        int(d.deleted),
                        d.created_at.isoformat(),
                        d.updated_at.isoformat(),
                    ),
                )
            )
        for t in tareas:
            sentencias.append(
                (
                    UPSERT_TAREA,
                    (
                        t.id,
                        t.titulo,
                        t.descripcion,
                        int(t.prioridad),
                        int(t.completada),
                        t.deadline_id,
                        t.fecha.isoformat() if t.fecha else None,
                        int(t.deleted),
                        t.created_at.isoformat(),
                        t.updated_at.isoformat(),
                    ),
                )
            )
        for n in notas:
            sentencias.append(
                (
                    UPSERT_NOTA,
                    (
                        n.id,
                        n.titulo,
                        n.contenido,
                        n.area,
                        n.deadline_id,
                        int(n.deleted),
                        n.created_at.isoformat(),
                        n.updated_at.isoformat(),
                    ),
                )
            )

        # Las lecturas van al final del mismo pipeline: primero se sube y
        # después se baja, en una sola petición HTTP. El esquema se envía
        # siempre para que una instalación nueva también pueda recibir datos.
        sentencias.append((SELECT_DEADLINES, ()))
        sentencias.append((SELECT_TAREAS, ()))
        sentencias.append((SELECT_NOTAS, ()))

        resultados = self._cliente.ejecutar(sentencias)

        # Solo si todo el pipeline salió bien se marca lo local como subido.
        self._deadlines.mark_synced([d.id for d in deadlines])
        self._tareas.mark_synced([t.id for t in tareas])
        self._notas.mark_synced([nota.id for nota in notas])

        filas_deadlines, filas_tareas, filas_notas = resultados[-3:]
        detalle_recibidos = {
            "deadlines": self._aplicar(self._deadlines, filas_deadlines),
            "tareas": self._aplicar(self._tareas, filas_tareas),
            "notas": self._aplicar(self._notas, filas_notas),
        }

        detalle = {
            "deadlines": len(deadlines),
            "tareas": len(tareas),
            "notas": len(notas),
        }
        enviados = sum(detalle.values())
        recibidos = sum(detalle_recibidos.values())
        resultado = ResultadoSync(enviados, recibidos, detalle, detalle_recibidos)

        if publicar_eventos and self._bus is not None:
            publicar_resultado(self._bus, resultado)

        logger.info(
            "Sincronización completada: %s enviados, %s recibidos",
            enviados,
            recibidos,
        )
        return resultado

    @staticmethod
    def _aplicar(repositorio, filas: Sequence[dict]) -> int:
        """Aplica filas de la nube y devuelve cuántas cambiaron algo."""
        aplicados = 0
        for fila in filas:
            if repositorio.upsert_remoto(fila):
                aplicados += 1
        return aplicados


def publicar_resultado(bus, resultado: ResultadoSync) -> None:
    """Notifica a la UI los cambios producidos por una sincronización.

    Los temas de dominio solo se publican cuando llegaron filas de la nube:
    así una subida normal no refresca las listas ni pierde el scroll. El tema
    ``SYNC_CAMBIADO`` se publica siempre que hubo cambios para actualizar el
    contador de pendientes.
    """
    if resultado.recibidos:
        for tema in (
            DEADLINES_CAMBIADOS,
            TAREAS_CAMBIADAS,
            NOTAS_CAMBIADAS,
            DATOS_CAMBIADOS,
        ):
            bus.publicar(tema)
    if resultado.hubo_cambios:
        bus.publicar(SYNC_CAMBIADO)
