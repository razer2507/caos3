"""Pruebas de los casos de uso de tareas."""

from __future__ import annotations

from datetime import date

import pytest

from src.domains.tareas.models.value_objects import Prioridad
from src.shared.application.events import (
    DATOS_CAMBIADOS,
    TAREAS_CAMBIADAS,
)
from src.shared.domain.errors import NoEncontrado
from src.shared.domain.periodos import Periodo


def test_crear_publica_eventos_y_persiste(tareas, tareas_repo, bus):
    eventos: list[str] = []
    bus.suscribir(TAREAS_CAMBIADAS, lambda _p: eventos.append("tareas"))
    bus.suscribir(DATOS_CAMBIADOS, lambda _p: eventos.append("datos"))

    tarea = tareas.crear("  Escribir tests  ", Prioridad.IMPORTANTE_NO_URGENTE)

    assert tarea.titulo == "Escribir tests"
    assert tareas_repo.get(tarea.id) is not None
    assert eventos == ["tareas", "datos"]


def test_completar_es_idempotente_y_persiste(tareas, tareas_repo):
    tarea = tareas.crear("Cerrar bucle")

    tareas.completar(tarea.id)
    tareas.completar(tarea.id)

    assert tareas_repo.get(tarea.id).completada is True


def test_reabrir_una_tarea_pendiente_no_falla(tareas):
    tarea = tareas.crear("Pendiente")
    assert tareas.reabrir(tarea.id).completada is False


def test_alternar(tareas):
    tarea = tareas.crear("Alternar")
    assert tareas.alternar(tarea.id).completada is True
    assert tareas.alternar(tarea.id).completada is False


def test_editar_campos_parciales(tareas):
    tarea = tareas.crear("Vieja", Prioridad.NO_IMPORTANTE_NO_URGENTE, "desc")

    actualizada = tareas.editar(tarea.id, titulo="Nueva")

    assert actualizada.titulo == "Nueva"
    assert actualizada.prioridad is Prioridad.NO_IMPORTANTE_NO_URGENTE
    assert actualizada.descripcion == "desc"


def test_editar_permite_vincular_y_desvincular_deadline(tareas, deadlines):
    deadline = deadlines.crear("Proyecto")
    tarea = tareas.crear("Proyecto")

    tareas.editar(tarea.id, deadline_id=deadline.id)
    assert tareas.obtener(tarea.id).deadline_id == deadline.id

    tareas.editar(tarea.id, deadline_id=None)
    assert tareas.obtener(tarea.id).deadline_id is None


def test_eliminar_usa_borrado_logico(tareas, tareas_repo):
    tarea = tareas.crear("Efímera")

    tareas.eliminar(tarea.id)

    assert tareas.listar() == []
    assert tareas_repo.get(tarea.id) is None
    pendiente = tareas_repo.list_pending()[0]
    assert pendiente.id == tarea.id and pendiente.deleted is True


def test_operar_sobre_id_inexistente_lanza_no_encontrado(tareas):
    with pytest.raises(NoEncontrado):
        tareas.completar("no-existe")
    with pytest.raises(NoEncontrado):
        tareas.editar("no-existe", titulo="X")
    with pytest.raises(NoEncontrado):
        tareas.eliminar("no-existe")


def test_progreso_diario(tareas):
    a = tareas.crear("A")
    tareas.crear("B")
    tareas.crear("C")
    tareas.completar(a.id)

    progreso = tareas.progreso_diario(hoy=date.today())

    assert progreso.completadas_hoy == 1
    assert progreso.pendientes == 2
    assert progreso.total == 3
    assert progreso.denominador == 3
    assert progreso.porcentaje == pytest.approx(1 / 3)


def test_progreso_sin_tareas_es_cero(tareas):
    progreso = tareas.progreso_diario()
    assert progreso.porcentaje == 0.0
    assert progreso.texto == "0 de 0 hoy"


def test_progreso_ignora_tareas_completadas_otro_dia(tareas):
    tarea = tareas.crear("Antigua")
    tareas.completar(tarea.id)
    tareas_repo = tareas._repo
    tareas_repo._db.execute(
        "UPDATE tareas SET updated_at = ? WHERE id = ?",
        ("2020-01-01T10:00:00+00:00", tarea.id),
    )

    progreso = tareas.progreso_diario(hoy=date.today())
    assert progreso.completadas_hoy == 0


def test_crear_con_fecha_y_editar_fecha(tareas):
    tarea = tareas.crear("Con fecha", fecha=date(2026, 11, 5))
    assert tarea.fecha == date(2026, 11, 5)

    tareas.editar(tarea.id, fecha=None)
    assert tareas.obtener(tarea.id).fecha is None


def test_listar_filtra_por_periodo(tareas):
    hoy = date(2026, 11, 5)  # jueves
    dentro = tareas.crear("Del día", fecha=hoy)
    tareas.crear("De la semana", fecha=date(2026, 11, 3))
    tareas.crear("De otro mes", fecha=date(2026, 12, 1))
    tareas.crear("Sin fecha")

    diario = tareas.listar(periodo=Periodo.DIARIO, hoy=hoy)
    semanal = tareas.listar(periodo=Periodo.SEMANAL, hoy=hoy)
    mensual = tareas.listar(periodo=Periodo.MENSUAL, hoy=hoy)

    assert [t.id for t in diario] == [dentro.id]
    assert len(semanal) == 2
    assert len(mensual) == 2


def test_listar_sin_periodo_devuelve_todas(tareas):
    tareas.crear("Con fecha", fecha=date(2026, 11, 5))
    tareas.crear("Sin fecha")
    assert len(tareas.listar()) == 2


def test_listar_filtra_por_manana_y_por_rango(tareas):
    hoy = date(2026, 11, 5)
    t_hoy = tareas.crear("Hoy", fecha=hoy)
    t_manana = tareas.crear("Mañana", fecha=date(2026, 11, 6))
    t_lejos = tareas.crear("Lejos", fecha=date(2026, 11, 15))
    tareas.crear("Sin fecha")

    assert [t.id for t in tareas.listar(periodo=Periodo.MANANA, hoy=hoy)] == [
        t_manana.id
    ]
    en_plazo = tareas.listar(desde=date(2026, 11, 5), hasta=date(2026, 11, 10))
    assert {t.id for t in en_plazo} == {t_hoy.id, t_manana.id}
    assert t_lejos.id not in {t.id for t in en_plazo}
