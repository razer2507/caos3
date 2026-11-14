"""Entidad Nota: conocimiento vinculado a un área o deadline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from src.shared.domain.entity import Entity
from src.shared.domain.value_objects import Titulo

SIN_CAMBIO: Final = object()


@dataclass
class Nota(Entity):
    titulo: str
    contenido: str = ""
    area: str = "General"
    deadline_id: str | None = None

    def __post_init__(self) -> None:
        self.titulo = Titulo(self.titulo).valor
        self.contenido = (self.contenido or "").strip()
        self.area = (self.area or "General").strip() or "General"
        if self.deadline_id is not None:
            self.deadline_id = str(self.deadline_id).strip() or None

    @property
    def resumen(self) -> str:
        texto = " ".join(self.contenido.split())
        if not texto:
            return "Sin contenido"
        return texto if len(texto) <= 160 else texto[:157] + "..."

    def actualizar(
        self,
        *,
        titulo: str | object = SIN_CAMBIO,
        contenido: str | object = SIN_CAMBIO,
        area: str | object = SIN_CAMBIO,
        deadline_id: str | None | object = SIN_CAMBIO,
    ) -> None:
        cambios = False

        if titulo is not SIN_CAMBIO:
            nuevo = Titulo(str(titulo)).valor
            if nuevo != self.titulo:
                self.titulo = nuevo
                cambios = True

        if contenido is not SIN_CAMBIO:
            nuevo_contenido = str(contenido or "").strip()
            if nuevo_contenido != self.contenido:
                self.contenido = nuevo_contenido
                cambios = True

        if area is not SIN_CAMBIO:
            nueva_area = (str(area) if area else "General").strip() or "General"
            if nueva_area != self.area:
                self.area = nueva_area
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
