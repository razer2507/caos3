"""Entidad Deadline: proyecto o hito con fecha límite."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Final

from src.shared.domain.entity import Entity
from src.shared.domain.value_objects import Titulo

SIN_CAMBIO: Final = object()


@dataclass
class Deadline(Entity):
    titulo: str
    fecha_limite: date | None = None
    area: str = "General"
    descripcion: str = ""
    completado: bool = False

    def __post_init__(self) -> None:
        self.titulo = Titulo(self.titulo).valor
        self.descripcion = (self.descripcion or "").strip()
        self.area = (self.area or "General").strip() or "General"
        self.completado = bool(self.completado)
        if isinstance(self.fecha_limite, str):
            self.fecha_limite = date.fromisoformat(self.fecha_limite)

    # ------------------------------------------------------------- estado
    def completar(self) -> bool:
        if self.completado:
            return False
        self.completado = True
        self._touch()
        return True

    def reabrir(self) -> bool:
        if not self.completado:
            return False
        self.completado = False
        self._touch()
        return True

    def alternar(self) -> bool:
        if self.completado:
            self.reabrir()
        else:
            self.completar()
        return self.completado

    # ----------------------------------------------------------- tiempo
    def dias_restantes(self, hoy: date | None = None) -> int | None:
        if self.fecha_limite is None:
            return None
        return (self.fecha_limite - (hoy or date.today())).days

    def esta_vencido(self, hoy: date | None = None) -> bool:
        dias = self.dias_restantes(hoy)
        return dias is not None and dias < 0 and not self.completado

    # ---------------------------------------------------------- edición
    def actualizar(
        self,
        *,
        titulo: str | object = SIN_CAMBIO,
        descripcion: str | object = SIN_CAMBIO,
        fecha_limite: date | None | object = SIN_CAMBIO,
        area: str | object = SIN_CAMBIO,
    ) -> None:
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

        if fecha_limite is not SIN_CAMBIO:
            nueva_fecha = (
                date.fromisoformat(fecha_limite)
                if isinstance(fecha_limite, str)
                else fecha_limite
            )
            if nueva_fecha != self.fecha_limite:
                self.fecha_limite = nueva_fecha
                cambios = True

        if area is not SIN_CAMBIO:
            nueva_area = (str(area) if area else "General").strip() or "General"
            if nueva_area != self.area:
                self.area = nueva_area
                cambios = True

        if cambios:
            self._touch()
