"""Value Objects compartidos (kernel común entre bounded contexts)."""

from __future__ import annotations

from dataclasses import dataclass

from src.shared.domain.errors import ErrorDeValidacion

LONGITUD_MAXIMA_TITULO = 120


@dataclass(frozen=True, slots=True)
class Titulo:
    """Título validado y normalizado."""

    valor: str

    def __post_init__(self) -> None:
        limpio = " ".join(str(self.valor).split())
        if not limpio:
            raise ErrorDeValidacion("El título no puede estar vacío.")
        if len(limpio) > LONGITUD_MAXIMA_TITULO:
            raise ErrorDeValidacion(
                f"El título no puede superar {LONGITUD_MAXIMA_TITULO} caracteres."
            )
        object.__setattr__(self, "valor", limpio)

    def __str__(self) -> str:
        return self.valor
