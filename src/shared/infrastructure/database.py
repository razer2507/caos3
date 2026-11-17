"""Conexión SQLite local, esquema y utilidades offline-first."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any, Iterable, Sequence

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

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
);

CREATE TABLE IF NOT EXISTS tareas (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    descripcion   TEXT NOT NULL DEFAULT '',
    prioridad     INTEGER NOT NULL,
    completada    INTEGER NOT NULL DEFAULT 0,
    deadline_id   TEXT REFERENCES deadlines(id) ON DELETE SET NULL,
    fecha         TEXT,
    deleted       INTEGER NOT NULL DEFAULT 0,
    synced        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notas (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    contenido     TEXT NOT NULL DEFAULT '',
    area          TEXT NOT NULL DEFAULT 'General',
    deadline_id   TEXT REFERENCES deadlines(id) ON DELETE SET NULL,
    deleted       INTEGER NOT NULL DEFAULT 0,
    synced        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_tareas_deadline   ON tareas(deadline_id);
CREATE INDEX IF NOT EXISTS idx_tareas_synced     ON tareas(synced);
CREATE INDEX IF NOT EXISTS idx_tareas_completada ON tareas(completada);
CREATE INDEX IF NOT EXISTS idx_deadlines_synced  ON deadlines(synced);
CREATE INDEX IF NOT EXISTS idx_notas_synced      ON notas(synced);
CREATE INDEX IF NOT EXISTS idx_notas_deadline    ON notas(deadline_id);
"""

# Versión actual del esquema local. La gestiona ``Database._migrar``.
VERSION_ESQUEMA = 4


def default_db_path() -> str:
    """Ruta de la base local según plataforma.

    Prioridad:
    1. ``CAOS_DB_PATH`` (útil en desarrollo y pruebas manuales).
    2. ``FLET_APP_STORAGE_DATA`` (directorio privado en Android/iOS).
    3. ``~/.caos/caos_local.db`` en escritorio.
    """
    override = os.getenv("CAOS_DB_PATH")
    if override:
        return str(Path(override).expanduser())

    storage = os.getenv("FLET_APP_STORAGE_DATA")
    if storage:
        return str(Path(storage) / "caos_local.db")

    base = Path.home() / ".caos"
    base.mkdir(parents=True, exist_ok=True)
    return str(base / "caos_local.db")


class Database:
    """Envoltorio fino y thread-safe sobre ``sqlite3``."""

    def __init__(self, path: str) -> None:
        self.path = str(path)
        self._conn: sqlite3.Connection | None = None
        self._lock = RLock()

    # ------------------------------------------------------------------ setup
    def initialize(self) -> None:
        parent = Path(self.path).expanduser().parent
        parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            conn = self._conexion()
            conn.executescript(SCHEMA)
            self._migrar(conn)
            conn.commit()

    @staticmethod
    def _migrar(conn: sqlite3.Connection) -> None:
        """Migra bases creadas con versiones anteriores del esquema.

        ``CREATE TABLE IF NOT EXISTS`` no toca una tabla que ya existe, así que
        una base antigua no recibe las columnas nuevas. Se lee ``user_version``
        **antes** de tocarla y cada paso es idempotente.

        - v3: añade la columna ``fecha`` a ``tareas``.
        - v4: rellena ``fecha`` con la fecha de ``created_at`` en las tareas
          que ya existían (heredan su día de creación).
        """
        version = conn.execute("PRAGMA user_version").fetchone()[0]

        columnas = {fila[1] for fila in conn.execute("PRAGMA table_info(tareas)")}
        if "fecha" not in columnas:
            conn.execute("ALTER TABLE tareas ADD COLUMN fecha TEXT")

        if version < 4:
            conn.execute(
                "UPDATE tareas SET fecha = substr(created_at, 1, 10) "
                "WHERE fecha IS NULL"
            )

        conn.execute(f"PRAGMA user_version = {VERSION_ESQUEMA}")

    def _conexion(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.path,
                check_same_thread=False,
                timeout=30,
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA busy_timeout = 5000")
        return self._conn

    # ------------------------------------------------------------------- API
    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        with self._lock:
            conn = self._conexion()
            cursor = conn.execute(sql, tuple(params))
            conn.commit()
            return int(cursor.lastrowid or 0)

    def executemany(self, sql: str, params: Iterable[Sequence[Any]]) -> None:
        with self._lock:
            conn = self._conexion()
            conn.executemany(sql, [tuple(p) for p in params])
            conn.commit()

    def query(self, sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
        with self._lock:
            conn = self._conexion()
            return list(conn.execute(sql, tuple(params)).fetchall())

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
        with self._lock:
            conn = self._conexion()
            return conn.execute(sql, tuple(params)).fetchone()

    def tabla_existe(self, nombre: str) -> bool:
        row = self.query_one(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (nombre,),
        )
        return row is not None

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def __enter__(self) -> "Database":
        self.initialize()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
