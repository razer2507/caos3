"""Puerto de persistencia del dominio de tareas (RNF02/RNF03)."""

from __future__ import annotations

from typing import Mapping, Protocol, Sequence

from src.domains.tareas.models.tarea import Tarea


class TareaRepository(Protocol):
    """Contrato que debe cumplir cualquier repositorio de tareas."""

    def add(self, tarea: Tarea) -> None: ...

    def update(self, tarea: Tarea) -> None: ...

    def get(self, tarea_id: str) -> Tarea | None: ...

    def list_all(self, *, incluir_completadas: bool = True) -> list[Tarea]: ...

    def list_by_deadline(
        self, deadline_id: str | None, *, incluir_completadas: bool = True
    ) -> list[Tarea]: ...

    def delete(self, tarea_id: str) -> None: ...

    def list_pending(self) -> list[Tarea]: ...

    def mark_synced(self, ids: Sequence[str]) -> None: ...

    def upsert_remoto(self, fila: Mapping[str, object]) -> bool: ...
