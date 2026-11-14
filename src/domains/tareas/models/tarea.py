"""Entidad Tarea con sus reglas de negocio (RF01–RF04)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from src.domains.tareas.models.value_objects import Prioridad, Titulo
from src.shared.domain.entity import Entity

SIN_CAMBIO: Final = object()


@dataclass
class Tarea(Entity):
    """Tarea suelta (``deadline_id=None``) o vinculada a un proyecto."""

    titulo: str
    prioridad: Prioridad = Prioridad.IMPORTANTE_URGENTE
    descripcion: str = ""
    completada: bool = False
    deadline_id: str | None = None

    def __post_init__(self) -> None:
        self.titulo = Titulo(self.titulo).valor
        self.descripcion = (self.descripcion or "").strip()
        self.prioridad = Prioridad.desde(self.prioridad)
        self.completada = bool(self.completada)
        if self.deadline_id is not None:
            self.deadline_id = str(self.deadline_id).strip() or None

    # ------------------------------------------------------------- estado
    def completar(self) -> bool:
        """Marca como completada. Devuelve True si hubo transición."""
        if self.completada:
            return False
        self.completada = True
        self._touch()
        return True

    def reabrir(self) -> bool:
        """Vuelve a pendiente. Devuelve True si hubo transición."""
        if not self.completada:
            return False
        self.completada = False
        self._touch()
        return True

    def alternar(self) -> bool:
        """Invierte el estado y devuelve el nuevo valor."""
        if self.completada:
            self.reabrir()
        else:
            self.completar()
        return self.completada

    # ------------------------------------------------------------ edición
    def actualizar(
        self,
        *,
        titulo: str | object = SIN_CAMBIO,
        descripcion: str | object = SIN_CAMBIO,
        prioridad: Prioridad | int | str | object = SIN_CAMBIO,
        deadline_id: str | None | object = SIN_CAMBIO,
    ) -> None:
        """Actualiza campos validando las invariantes del dominio."""
        cambios = False

        if titulo is not SIN_CAMBIO:
            nuevo = Titulo(str(titulo)).valor
            if nuevo != self.titulo:
                self.titulo = nuevo
                cambios = True

        if descripcion is not SIN_CAMBIO:
            nueva = str(descripcion or "").strip()
            if nueva != self.descripcion:
                self.descripcion = nueva
                cambios = True

        if prioridad is not SIN_CAMBIO:
            nueva_prioridad = Prioridad.desde(prioridad)
            if nueva_prioridad != self.prioridad:
                self.prioridad = nueva_prioridad
                cambios = True

        if deadline_id is not SIN_CAMBIO:
            nuevo_deadline = (
                None if deadline_id is None else (str(deadline_id).strip() or None)
            )
            if nuevo_deadline != self.deadline_id:
                self.deadline_id = nuevo_deadline
                cambios = True

        if cambios:
            self._touch()

    def vincular_deadline(self, deadline_id: str | None) -> None:
        self.actualizar(deadline_id=deadline_id)

    def desvincular_deadline(self) -> None:
        self.actualizar(deadline_id=None)
