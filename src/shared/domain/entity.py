"""Entidad base compartida por todos los bounded contexts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def nuevo_id() -> str:
    """Genera un UUID v4 en la app para poder trabajar 100% offline."""
    return str(uuid4())


def ahora_utc() -> datetime:
    """Marca temporal UTC consciente de zona horaria."""
    return datetime.now(timezone.utc)


@dataclass(kw_only=True)
class Entity:
    """Base para entidades persistibles y sincronizables."""

    id: str = field(default_factory=nuevo_id)
    created_at: datetime = field(default_factory=ahora_utc)
    updated_at: datetime = field(default_factory=ahora_utc)
    # synced=False => el registro está pendiente de subir a Turso.
    synced: bool = False
    # Borrado lógico: permite propagar eliminaciones en la sincronización.
    deleted: bool = False

    def _touch(self) -> None:
        """Marca la entidad como modificada y pendiente de sincronizar."""
        self.updated_at = ahora_utc()
        self.synced = False

    def marcar_eliminada(self) -> None:
        """Aplica borrado lógico (idempotente)."""
        if not self.deleted:
            self.deleted = True
            self._touch()
