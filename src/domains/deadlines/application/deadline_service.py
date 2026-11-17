"""Casos de uso de proyectos / deadlines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.domains.deadlines.application.ports import DeadlineRepository
from src.domains.deadlines.models.deadline import SIN_CAMBIO, Deadline
from src.domains.tareas.application.ports import TareaRepository
from src.shared.application.event_bus import EventBus
from src.shared.application.events import (
    DATOS_CAMBIADOS,
    DEADLINES_CAMBIADOS,
    TAREAS_CAMBIADAS,
)
from src.shared.domain.errors import NoEncontrado
from src.shared.domain.periodos import Periodo, dentro, en_rango


@dataclass(frozen=True)
class ProgresoDeadline:
    hechas: int
    total: int

    @property
    def porcentaje(self) -> float:
        if self.total == 0:
            return 0.0
        return min(1.0, self.hechas / self.total)


@dataclass(frozen=True)
class ResumenDeadline:
    deadline: Deadline
    progreso: ProgresoDeadline


class DeadlineService:
    def __init__(
        self,
        repositorio: DeadlineRepository,
        tareas: TareaRepository,
        bus: EventBus,
    ) -> None:
        self._repo = repositorio
        self._tareas = tareas
        self._bus = bus

    # ------------------------------------------------------------- comandos
    def crear(
        self,
        titulo: str,
        *,
        fecha_limite: date | None = None,
        area: str = "General",
        descripcion: str = "",
    ) -> Deadline:
        deadline = Deadline(
            titulo=titulo,
            fecha_limite=fecha_limite,
            area=area,
            descripcion=descripcion,
        )
        self._repo.add(deadline)
        self._notificar()
        return deadline

    def editar(
        self,
        deadline_id: str,
        *,
        titulo: str | object = SIN_CAMBIO,
        descripcion: str | object = SIN_CAMBIO,
        fecha_limite: date | None | object = SIN_CAMBIO,
        area: str | object = SIN_CAMBIO,
    ) -> Deadline:
        deadline = self._obtener(deadline_id)
        deadline.actualizar(
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite,
            area=area,
        )
        self._repo.update(deadline)
        self._notificar()
        return deadline

    def completar(self, deadline_id: str) -> Deadline:
        deadline = self._obtener(deadline_id)
        if deadline.completar():
            self._repo.update(deadline)
            self._notificar(incluir_tareas=True)
        return deadline

    def reabrir(self, deadline_id: str) -> Deadline:
        deadline = self._obtener(deadline_id)
        if deadline.reabrir():
            self._repo.update(deadline)
            self._notificar(incluir_tareas=True)
        return deadline

    def alternar(self, deadline_id: str) -> Deadline:
        deadline = self._obtener(deadline_id)
        deadline.alternar()
        self._repo.update(deadline)
        self._notificar(incluir_tareas=True)
        return deadline

    def eliminar(self, deadline_id: str) -> None:
        self._obtener(deadline_id)
        # Desvincula las tareas para que queden sueltas (RF01).
        for tarea in self._tareas.list_by_deadline(deadline_id, incluir_completadas=True):
            tarea.actualizar(deadline_id=None)
            self._tareas.update(tarea)
        self._repo.delete(deadline_id)
        self._notificar(incluir_tareas=True)

    # ------------------------------------------------------------ consultas
    def obtener(self, deadline_id: str) -> Deadline:
        return self._obtener(deadline_id)

    def listar(self, *, incluir_completados: bool = True) -> list[Deadline]:
        return self._repo.list_all(incluir_completados=incluir_completados)

    def progreso(self, deadline_id: str) -> ProgresoDeadline:
        tareas = self._tareas.list_by_deadline(deadline_id, incluir_completadas=True)
        hechas = sum(1 for t in tareas if t.completada)
        return ProgresoDeadline(hechas=hechas, total=len(tareas))

    def resumen(
        self,
        *,
        incluir_completados: bool = True,
        periodo: Periodo | None = None,
        hoy: date | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[ResumenDeadline]:
        """Resúmenes de proyectos; filtra por ``[desde, hasta]`` o ``periodo``."""
        deadlines = self._repo.list_all(incluir_completados=incluir_completados)
        if desde is not None or hasta is not None:
            deadlines = [
                d for d in deadlines if en_rango(d.fecha_limite, desde, hasta)
            ]
        elif periodo is not None:
            deadlines = [d for d in deadlines if dentro(d.fecha_limite, periodo, hoy)]
        return [ResumenDeadline(d, self.progreso(d.id)) for d in deadlines]

    # ------------------------------------------------------------- helpers
    def _obtener(self, deadline_id: str) -> Deadline:
        deadline = self._repo.get(deadline_id)
        if deadline is None:
            raise NoEncontrado(f"No existe el deadline {deadline_id}.")
        return deadline

    def _notificar(self, *, incluir_tareas: bool = False) -> None:
        self._bus.publicar(DEADLINES_CAMBIADOS)
        if incluir_tareas:
            self._bus.publicar(TAREAS_CAMBIADAS)
        self._bus.publicar(DATOS_CAMBIADOS)
