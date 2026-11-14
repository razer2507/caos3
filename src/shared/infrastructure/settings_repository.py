"""Ajustes persistentes de la aplicación (credenciales de Turso, etc.).

Los valores se guardan en la tabla ``settings`` de la base SQLite local. Eso
permite configurar la sincronización desde el propio teléfono, sin depender de
variables de entorno (que en Android no se pueden definir).
"""

from __future__ import annotations

import os

from src.shared.infrastructure.database import Database

CLAVE_TURSO_URL = "turso_url"
CLAVE_TURSO_TOKEN = "turso_token"


class SettingsRepository:
    """Lee y guarda pares clave/valor en la tabla ``settings``."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------------ API
    def get(self, clave: str, default: str = "") -> str:
        fila = self._db.query_one(
            "SELECT valor FROM settings WHERE clave = ?", (clave,)
        )
        if fila is None:
            return default
        valor = fila["valor"]
        return default if valor is None else str(valor)

    def set(self, clave: str, valor: str) -> None:
        self._db.execute(
            """
            INSERT INTO settings (clave, valor) VALUES (?, ?)
            ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor
            """,
            (clave, valor),
        )

    def eliminar(self, clave: str) -> None:
        self._db.execute("DELETE FROM settings WHERE clave = ?", (clave,))

    # --------------------------------------------------------------- Turso
    def turso_credenciales(self) -> tuple[str, str]:
        """Devuelve ``(url, token)`` guardados o, si faltan, del entorno.

        Las variables de entorno siguen funcionando en escritorio; en Android
        lo normal es que el usuario las escriba en la pantalla de ajustes.
        """
        url = self.get(CLAVE_TURSO_URL) or os.getenv("TURSO_DATABASE_URL", "")
        token = self.get(CLAVE_TURSO_TOKEN) or os.getenv("TURSO_AUTH_TOKEN", "")
        return url.strip(), token.strip()

    def guardar_turso(self, url: str, token: str) -> None:
        self.set(CLAVE_TURSO_URL, url.strip())
        self.set(CLAVE_TURSO_TOKEN, token.strip())

    def borrar_turso(self) -> None:
        self.eliminar(CLAVE_TURSO_URL)
        self.eliminar(CLAVE_TURSO_TOKEN)
