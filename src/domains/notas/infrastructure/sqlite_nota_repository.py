"""Repositorio SQLite de notas."""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Sequence

from src.domains.notas.application.ports import NotaRepository
from src.domains.notas.models.nota import Nota
from src.shared.infrastructure.database import Database

_COLUMNAS = (
    "id, titulo, contenido, area, deadline_id, "
    "deleted, synced, created_at, updated_at"
)

_UPSERT = f"""
INSERT INTO notas ({_COLUMNAS})
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    titulo      = excluded.titulo,
    contenido   = excluded.contenido,
    area        = excluded.area,
    deadline_id = excluded.deadline_id,
    deleted     = excluded.deleted,
    synced      = excluded.synced,
    updated_at  = excluded.updated_at
"""


class SqliteNotaRepository(NotaRepository):
    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------- escritura
    def add(self, nota: Nota) -> None:
        self._db.execute(_UPSERT, self._params(nota))

    def update(self, nota: Nota) -> None:
        self._db.execute(_UPSERT, self._params(nota))

    def delete(self, nota_id: str) -> None:
        nota = self.get(nota_id)
        if nota is None:
            return
        nota.marcar_eliminada()
        self.update(nota)

    def mark_synced(self, ids: Sequence[str]) -> None:
        if not ids:
            return
        marcadores = ", ".join("?" for _ in ids)
        self._db.execute(
            f"UPDATE notas SET synced = 1 WHERE id IN ({marcadores})",
            tuple(ids),
        )

    def upsert_remoto(self, fila: Mapping[str, object]) -> bool:
        """Aplica una fila de Turso si es más reciente que la local."""
        existente = self._db.query_one(
            "SELECT updated_at FROM notas WHERE id = ?", (fila["id"],)
        )
        if existente is not None and existente["updated_at"] >= str(
            fila["updated_at"]
        ):
            return False
        nota = self._fila_a_entidad(fila)
        nota.synced = True
        self._db.execute(_UPSERT, self._params(nota))
        return True

    # -------------------------------------------------------------- lectura
    def get(self, nota_id: str) -> Nota | None:
        row = self._db.query_one(
            f"SELECT {_COLUMNAS} FROM notas WHERE id = ? AND deleted = 0",
            (nota_id,),
        )
        return self._fila_a_entidad(row) if row else None

    def list_all(self, *, buscar: str | None = None) -> list[Nota]:
        sql = f"SELECT {_COLUMNAS} FROM notas WHERE deleted = 0"
        params: list[object] = []
        if buscar and buscar.strip():
            patron = f"%{buscar.strip()}%"
            sql += " AND (titulo LIKE ? OR contenido LIKE ? OR area LIKE ?)"
            params.extend([patron, patron, patron])
        sql += " ORDER BY updated_at DESC"
        return [self._fila_a_entidad(row) for row in self._db.query(sql, params)]

    def list_by_deadline(self, deadline_id: str) -> list[Nota]:
        rows = self._db.query(
            f"SELECT {_COLUMNAS} FROM notas "
            "WHERE deleted = 0 AND deadline_id = ? ORDER BY updated_at DESC",
            (deadline_id,),
        )
        return [self._fila_a_entidad(row) for row in rows]

    def list_pending(self) -> list[Nota]:
        rows = self._db.query(
            f"SELECT {_COLUMNAS} FROM notas WHERE synced = 0 ORDER BY updated_at ASC"
        )
        return [self._fila_a_entidad(row) for row in rows]

    # -------------------------------------------------------------- mapeo
    @staticmethod
    def _params(nota: Nota) -> tuple[object, ...]:
        return (
            nota.id,
            nota.titulo,
            nota.contenido,
            nota.area,
            nota.deadline_id,
            int(nota.deleted),
            int(nota.synced),
            nota.created_at.isoformat(),
            nota.updated_at.isoformat(),
        )

    @staticmethod
    def _fila_a_entidad(row) -> Nota:
        return Nota(
            id=row["id"],
            titulo=row["titulo"],
            contenido=row["contenido"],
            area=row["area"],
            deadline_id=row["deadline_id"],
            deleted=bool(row["deleted"]),
            synced=bool(row["synced"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
