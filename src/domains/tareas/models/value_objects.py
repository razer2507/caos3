"""Value Objects del dominio de tareas."""

from __future__ import annotations

from enum import IntEnum

from src.shared.domain.errors import ErrorDeValidacion
from src.shared.domain.value_objects import (  # noqa: F401  (re-export del kernel)
    LONGITUD_MAXIMA_TITULO,
    Titulo,
)


class Prioridad(IntEnum):
    """Matriz de Eisenhower: obligatoria en toda tarea (RF02)."""

    IMPORTANTE_URGENTE = 1
    IMPORTANTE_NO_URGENTE = 2
    NO_IMPORTANTE_URGENTE = 3
    NO_IMPORTANTE_NO_URGENTE = 4

    @property
    def codigo(self) -> str:
        return f"P{self.value}"

    @property
    def etiqueta(self) -> str:
        return _ETIQUETAS[self]

    @property
    def descripcion(self) -> str:
        return _DESCRIPCIONES[self]

    @classmethod
    def desde(cls, valor: "Prioridad | int | str") -> "Prioridad":
        if isinstance(valor, cls):
            return valor
        try:
            return cls(int(valor))
        except (TypeError, ValueError) as exc:
            raise ErrorDeValidacion(
                f"Prioridad inválida: {valor!r}. Usa 1, 2, 3 o 4."
            ) from exc


_ETIQUETAS = {
    Prioridad.IMPORTANTE_URGENTE: "Importante y urgente",
    Prioridad.IMPORTANTE_NO_URGENTE: "Importante, no urgente",
    Prioridad.NO_IMPORTANTE_URGENTE: "Urgente, no importante",
    Prioridad.NO_IMPORTANTE_NO_URGENTE: "Ni importante ni urgente",
}

_DESCRIPCIONES = {
    Prioridad.IMPORTANTE_URGENTE: "Hazlo ahora",
    Prioridad.IMPORTANTE_NO_URGENTE: "Planifícalo",
    Prioridad.NO_IMPORTANTE_URGENTE: "Delégalo",
    Prioridad.NO_IMPORTANTE_NO_URGENTE: "Elimínalo o hazlo después",
}
