"""Casos de uso del módulo de notas."""

from __future__ import annotations

from src.domains.notas.application.ports import NotaRepository
from src.domains.notas.models.nota import SIN_CAMBIO, Nota
from src.shared.application.event_bus import EventBus
from src.shared.application.events import DATOS_CAMBIADOS, NOTAS_CAMBIADAS
from src.shared.domain.errors import NoEncontrado


class NotaService:
    def __init__(self, repositorio: NotaRepository, bus: EventBus) -> None:
        self._repo = repositorio
        self._bus = bus

    # ------------------------------------------------------------- comandos
    def crear(
        self,
        titulo: str,
        *,
        contenido: str = "",
        area: str = "General",
        deadline_id: str | None = None,
    ) -> Nota:
        nota = Nota(
            titulo=titulo,
            contenido=contenido,
            area=area,
            deadline_id=deadline_id,
        )
        self._repo.add(nota)
        self._notificar()
        return nota

    def editar(
        self,
        nota_id: str,
        *,
        titulo: str | object = SIN_CAMBIO,
        contenido: str | object = SIN_CAMBIO,
        area: str | object = SIN_CAMBIO,
        deadline_id: str | None | object = SIN_CAMBIO,
    ) -> Nota:
        nota = self._obtener(nota_id)
        nota.actualizar(
            titulo=titulo,
            contenido=contenido,
            area=area,
            deadline_id=deadline_id,
        )
        self._repo.update(nota)
        self._notificar()
        return nota

    def eliminar(self, nota_id: str) -> None:
        self._obtener(nota_id)
        self._repo.delete(nota_id)
        self._notificar()

    # ------------------------------------------------------------ consultas
    def obtener(self, nota_id: str) -> Nota:
        return self._obtener(nota_id)

    def listar(self, *, buscar: str | None = None) -> list[Nota]:
        return self._repo.list_all(buscar=buscar)

    def listar_por_deadline(self, deadline_id: str) -> list[Nota]:
        return self._repo.list_by_deadline(deadline_id)

    # ------------------------------------------------------------- helpers
    def _obtener(self, nota_id: str) -> Nota:
        nota = self._repo.get(nota_id)
        if nota is None:
            raise NoEncontrado(f"No existe la nota {nota_id}.")
        return nota

    def _notificar(self) -> None:
        self._bus.publicar(NOTAS_CAMBIADAS)
        self._bus.publicar(DATOS_CAMBIADOS)
