"""Repositorio SQLite de deadlines."""

from __future__ import annotations

from datetime import date, datetime
from typing import Mapping, Sequence

from src.domains.deadlines.application.ports import DeadlineRepository
from src.domains.deadlines.models.deadline import Deadline
from src.shared.infrastructure.database import Database

_COLUMNAS = (
    "id, titulo, descripcion, fecha_limite, area, completado, "
    "deleted, synced, created_at, updated_at"
)

_UPSERT = f"""
INSERT INTO deadlines ({_COLUMNAS})
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo       = excluded.titulo,
    descripcion  = excluded.descripcion,
    fecha_limite = excluded.fecha_limite,
    area         = excluded.area,
    completado   = excluded.completado,
    deleted      = excluded.deleted,
    synced       = excluded.synced,
    updated_at   = excluded.updated_at
"""


class SqliteDeadlineRepository(DeadlineRepository):
    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------- escritura
    def add(self, deadline: Deadline) -> None:
        self._db.execute(_UPSERT, self._params(deadline))

    def update(self, deadline: Deadline) -> None:
        self._db.execute(_UPSERT, self._params(deadline))

    def delete(self, deadline_id: str) -> None:
        deadline = self.get(deadline_id)
        if deadline is None:
            return
        deadline.marcar_eliminada()
        self.update(deadline)

    def mark_synced(self, ids: Sequence[str]) -> None:
        if not ids:
            return
        marcadores = ", ".join("?" for _ in ids)
        self._db.execute(
            f"UPDATE deadlines SET synced = 1 WHERE id IN ({marcadores})",
            tuple(ids),
        )

    def upsert_remoto(self, fila: Mapping[str, object]) -> bool:
        """Aplica una fila de Turso si es más reciente que la local."""
        existente = self._db.query_one(
            "SELECT updated_at FROM deadlines WHERE id = ?", (fila["id"],)
        )
        if existente is not None and existente["updated_at"] >= str(
            fila["updated_at"]
        ):
            return False
        deadline = self._fila_a_entidad(fila)
        deadline.synced = True
        self._db.execute(_UPSERT, self._params(deadline))
        return True

    # -------------------------------------------------------------- lectura
    def get(self, deadline_id: str) -> Deadline | None:
        row = self._db.query_one(
            f"SELECT {_COLUMNAS} FROM deadlines WHERE id = ? AND deleted = 0",
            (deadline_id,),
        )
        return self._fila_a_entidad(row) if row else None

    def list_all(self, *, incluir_completados: bool = True) -> list[Deadline]:
        sql = f"SELECT {_COLUMNAS} FROM deadlines WHERE deleted = 0"
        if not incluir_completados:
            sql += " AND completado = 0"
        sql += (
            " ORDER BY completado ASC, "
            " CASE WHEN fecha_limite IS NULL THEN 1 ELSE 0 END, "
            " fecha_limite ASC, created_at DESC"
        )
        return [self._fila_a_entidad(row) for row in self._db.query(sql)]

    def list_pending(self) -> list[Deadline]:
        rows = self._db.query(
            f"SELECT {_COLUMNAS} FROM deadlines WHERE synced = 0 ORDER BY updated_at ASC"
        )
        return [self._fila_a_entidad(row) for row in rows]

    # -------------------------------------------------------------- mapeo
    @staticmethod
    def _params(deadline: Deadline) -> tuple[object, ...]:
        return (
            deadline.id,
            deadline.titulo,
            deadline.descripcion,
            deadline.fecha_limite.isoformat() if deadline.fecha_limite else None,
            deadline.area,
            int(deadline.completado),
            int(deadline.deleted),
            int(deadline.synced),
            deadline.created_at.isoformat(),
            deadline.updated_at.isoformat(),
        )

    @staticmethod
    def _fila_a_entidad(row) -> Deadline:
        return Deadline(
            id=row["id"],
            titulo=row["titulo"],
            descripcion=row["descripcion"],
            fecha_limite=(
                date.fromisoformat(row["fecha_limite"]) if row["fecha_limite"] else None
            ),
            area=row["area"],
            completado=bool(row["completado"]),
            deleted=bool(row["deleted"]),
            synced=bool(row["synced"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
