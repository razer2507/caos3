"""Casos de uso del módulo de tareas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.domains.tareas.application.ports import TareaRepository
from src.domains.tareas.models.tarea import SIN_CAMBIO, Tarea
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.application.event_bus import EventBus
from src.shared.application.events import DATOS_CAMBIADOS, TAREAS_CAMBIADAS
from src.shared.domain.errors import NoEncontrado
from src.shared.domain.periodos import Periodo, en_rango


@dataclass(frozen=True)
class ProgresoDiario:
    completadas_hoy: int
    pendientes: int
    total: int

    @property
    def denominador(self) -> int:
        return self.completadas_hoy + self.pendientes

    @property
    def porcentaje(self) -> float:
        if self.denominador == 0:
            return 0.0
        return min(1.0, self.completadas_hoy / self.denominador)

    @property
    def texto(self) -> str:
        return f"{self.completadas_hoy} de {self.denominador} hoy"


class TareaService:
    """Orquesta reglas de negocio, persistencia y notificación a la UI."""

    def __init__(self, repositorio: TareaRepository, bus: EventBus) -> None:
        self._repo = repositorio
        self._bus = bus

    # ------------------------------------------------------------- comandos
    def crear(
        self,
        titulo: str,
        prioridad: Prioridad | int | str = Prioridad.IMPORTANTE_URGENTE,
        descripcion: str = "",
        deadline_id: str | None = None,
        fecha: date | None = None,
    ) -> Tarea:
        tarea = Tarea(
            titulo=titulo,
            prioridad=Prioridad.desde(prioridad),
            descripcion=descripcion,
            deadline_id=deadline_id,
            fecha=fecha,
        )
        self._repo.add(tarea)
        self._notificar()
        return tarea

    def editar(
        self,
        tarea_id: str,
        *,
        titulo: str | object = SIN_CAMBIO,
        descripcion: str | object = SIN_CAMBIO,
        prioridad: Prioridad | int | str | object = SIN_CAMBIO,
        deadline_id: str | None | object = SIN_CAMBIO,
        fecha: date | None | object = SIN_CAMBIO,
    ) -> Tarea:
        tarea = self._obtener(tarea_id)
        tarea.actualizar(
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            deadline_id=deadline_id,
            fecha=fecha,
        )
        self._repo.update(tarea)
        self._notificar()
        return tarea

    def completar(self, tarea_id: str) -> Tarea:
        tarea = self._obtener(tarea_id)
        if tarea.completar():
            self._repo.update(tarea)
            self._notificar()
        return tarea

    def reabrir(self, tarea_id: str) -> Tarea:
        tarea = self._obtener(tarea_id)
        if tarea.reabrir():
            self._repo.update(tarea)
            self._notificar()
        return tarea

    def alternar(self, tarea_id: str) -> Tarea:
        tarea = self._obtener(tarea_id)
        tarea.alternar()
        self._repo.update(tarea)
        self._notificar()
        return tarea

    def eliminar(self, tarea_id: str) -> None:
        self._obtener(tarea_id)
        self._repo.delete(tarea_id)
        self._notificar()

    # ------------------------------------------------------------ consultas
    def obtener(self, tarea_id: str) -> Tarea:
        return self._obtener(tarea_id)

    def listar(
        self,
        *,
        incluir_completadas: bool = True,
        periodo: Periodo | None = None,
        hoy: date | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[Tarea]:
        """Lista tareas; filtra por ``[desde, hasta]`` o por ``periodo``."""
        tareas = self._repo.list_all(incluir_completadas=incluir_completadas)
        if desde is not None or hasta is not None:
            return [t for t in tareas if en_rango(t.fecha, desde, hasta)]
        if periodo is None:
            return tareas
        return [t for t in tareas if t.en_periodo(periodo, hoy)]

    def listar_por_deadline(
        self, deadline_id: str | None, *, incluir_completadas: bool = True
    ) -> list[Tarea]:
        return self._repo.list_by_deadline(
            deadline_id, incluir_completadas=incluir_completadas
        )

    def progreso_diario(self, hoy: date | None = None) -> ProgresoDiario:
        hoy = hoy or date.today()
        tareas = self._repo.list_all(incluir_completadas=True)
        completadas_hoy = sum(
            1
            for t in tareas
            if t.completada and t.updated_at.astimezone().date() == hoy
        )
        pendientes = sum(1 for t in tareas if not t.completada)
        return ProgresoDiario(
            completadas_hoy=completadas_hoy,
            pendientes=pendientes,
            total=len(tareas),
        )

    # ------------------------------------------------------------- helpers
    def _obtener(self, tarea_id: str) -> Tarea:
        tarea = self._repo.get(tarea_id)
        if tarea is None:
            raise NoEncontrado(f"No existe la tarea {tarea_id}.")
        return tarea

    def _notificar(self) -> None:
        self._bus.publicar(TAREAS_CAMBIADAS)
        self._bus.publicar(DATOS_CAMBIADOS)
