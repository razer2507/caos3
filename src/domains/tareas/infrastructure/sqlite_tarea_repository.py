"""Repositorio SQLite del módulo de tareas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Mapping, Sequence

from src.domains.tareas.application.ports import TareaRepository
from src.domains.tareas.models.tarea import Tarea
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.infrastructure.database import Database

_COLUMNAS = (
    "id, titulo, descripcion, prioridad, completada, deadline_id, fecha, "
    "deleted, synced, created_at, updated_at"
)

_UPSERT = f"""
INSERT INTO tareas ({_COLUMNAS})
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo       = excluded.titulo,
    descripcion  = excluded.descripcion,
    prioridad    = excluded.prioridad,
    completada   = excluded.completada,
    deadline_id  = excluded.deadline_id,
    fecha        = excluded.fecha,
    deleted      = excluded.deleted,
    synced       = excluded.synced,
    updated_at   = excluded.updated_at
"""


class SqliteTareaRepository(TareaRepository):
    """Implementación concreta sobre la base local (RF03, RF06)."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------- escritura
    def add(self, tarea: Tarea) -> None:
        self._db.execute(_UPSERT, self._params(tarea))

    def update(self, tarea: Tarea) -> None:
        self._db.execute(_UPSERT, self._params(tarea))

    def delete(self, tarea_id: str) -> None:
        tarea = self.get(tarea_id)
        if tarea is None:
            return
        tarea.marcar_eliminada()
        self.update(tarea)

    def mark_synced(self, ids: Sequence[str]) -> None:
        if not ids:
            return
        marcadores = ", ".join("?" for _ in ids)
        self._db.execute(
            f"UPDATE tareas SET synced = 1 WHERE id IN ({marcadores})",
            tuple(ids),
        )

    def upsert_remoto(self, fila: Mapping[str, object]) -> bool:
        """Aplica una fila de Turso si es más reciente que la local."""
        existente = self._db.query_one(
            "SELECT updated_at FROM tareas WHERE id = ?", (fila["id"],)
        )
        if existente is not None and existente["updated_at"] >= str(
            fila["updated_at"]
        ):
            return False
        tarea = self._fila_a_entidad(fila)
        tarea.synced = True
        self._db.execute(_UPSERT, self._params(tarea))
        return True

    # -------------------------------------------------------------- lectura
    def get(self, tarea_id: str) -> Tarea | None:
        row = self._db.query_one(
            f"SELECT {_COLUMNAS} FROM tareas WHERE id = ? AND deleted = 0",
            (tarea_id,),
        )
        return self._fila_a_entidad(row) if row else None

    def list_all(self, *, incluir_completadas: bool = True) -> list[Tarea]:
        sql = f"SELECT {_COLUMNAS} FROM tareas WHERE deleted = 0"
        if not incluir_completadas:
            sql += " AND completada = 0"
        sql += " ORDER BY completada ASC, prioridad ASC, created_at DESC"
        return [self._fila_a_entidad(row) for row in self._db.query(sql)]

    def list_by_deadline(
        self, deadline_id: str | None, *, incluir_completadas: bool = True
    ) -> list[Tarea]:
        sql = f"SELECT {_COLUMNAS} FROM tareas WHERE deleted = 0"
        params: list[object] = []
        if deadline_id is None:
            sql += " AND deadline_id IS NULL"
        else:
            sql += " AND deadline_id = ?"
            params.append(deadline_id)
        if not incluir_completadas:
            sql += " AND completada = 0"
        sql += " ORDER BY completada ASC, prioridad ASC, created_at DESC"
        return [self._fila_a_entidad(row) for row in self._db.query(sql, params)]

    def list_pending(self) -> list[Tarea]:
        rows = self._db.query(
            f"SELECT {_COLUMNAS} FROM tareas WHERE synced = 0 ORDER BY updated_at ASC"
        )
        return [self._fila_a_entidad(row) for row in rows]

    # -------------------------------------------------------------- mapeo
    @staticmethod
    def _params(tarea: Tarea) -> tuple[object, ...]:
        return (
            tarea.id,
            tarea.titulo,
            tarea.descripcion,
            int(tarea.prioridad),
            int(tarea.completada),
            tarea.deadline_id,
            tarea.fecha.isoformat() if tarea.fecha else None,
            int(tarea.deleted),
            int(tarea.synced),
            tarea.created_at.isoformat(),
            tarea.updated_at.isoformat(),
        )

    @staticmethod
    def _fila_a_entidad(row) -> Tarea:
        return Tarea(
            id=row["id"],
            titulo=row["titulo"],
            descripcion=row["descripcion"],
            prioridad=Prioridad.desde(row["prioridad"]),
            completada=bool(row["completada"]),
            deadline_id=row["deadline_id"],
            fecha=date.fromisoformat(row["fecha"]) if row["fecha"] else None,
            deleted=bool(row["deleted"]),
            synced=bool(row["synced"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
