"""Pruebas del dominio de deadlines y su integración con tareas."""

from __future__ import annotations

from datetime import date

import pytest

from src.domains.deadlines.models.deadline import Deadline
from src.shared.domain.errors import ErrorDeValidacion, NoEncontrado
from src.shared.domain.periodos import Periodo


HOY = date(2026, 11, 5)


def test_dias_restantes_y_vencimiento():
    futuro = Deadline(titulo="Futuro", fecha_limite=date(2026, 11, 10))
    pasado = Deadline(titulo="Pasado", fecha_limite=date(2026, 10, 30))
    sin_fecha = Deadline(titulo="Sin fecha")

    assert futuro.dias_restantes(HOY) == 5
    assert futuro.esta_vencido(HOY) is False
    assert pasado.dias_restantes(HOY) == -6
    assert pasado.esta_vencido(HOY) is True
    assert sin_fecha.dias_restantes(HOY) is None


def test_un_proyecto_completado_no_se_considera_vencido():
    deadline = Deadline(
        titulo="Cerrado", fecha_limite=date(2026, 1, 1), completado=True
    )
    assert deadline.esta_vencido(HOY) is False


def test_fecha_iso_se_convierte():
    deadline = Deadline(titulo="ISO", fecha_limite="2026-12-24")
    assert deadline.fecha_limite == date(2026, 12, 24)


def test_titulo_vacio_es_invalido():
    with pytest.raises(ErrorDeValidacion):
        Deadline(titulo="")


def test_crear_y_editar_deadline(deadlines):
    deadline = deadlines.crear(
        "Lanzamiento",
        fecha_limite=date(2026, 12, 1),
        area="Producto",
        descripcion="v1",
    )

    assert deadlines.obtener(deadline.id).area == "Producto"

    actualizado = deadlines.editar(deadline.id, titulo="Lanzamiento v2", area="Producto")
    assert actualizado.titulo == "Lanzamiento v2"

    deadlines.editar(deadline.id, fecha_limite=None)
    assert deadlines.obtener(deadline.id).fecha_limite is None


def test_progreso_de_un_deadline(deadlines, tareas):
    deadline = deadlines.crear("Web", fecha_limite=date(2026, 12, 1))
    a = tareas.crear("Diseño", deadline_id=deadline.id)
    tareas.crear("Backend", deadline_id=deadline.id)

    progreso = deadlines.progreso(deadline.id)
    assert (progreso.hechas, progreso.total) == (0, 2)

    tareas.completar(a.id)
    progreso = deadlines.progreso(deadline.id)
    assert (progreso.hechas, progreso.total) == (1, 2)
    assert progreso.porcentaje == pytest.approx(0.5)


def test_resumen_incluye_progreso(deadlines, tareas):
    deadline = deadlines.crear("App")
    tarea = tareas.crear("Tarea", deadline_id=deadline.id)
    tareas.completar(tarea.id)

    resumen = deadlines.resumen()
    assert len(resumen) == 1
    assert resumen[0].progreso.hechas == 1
    assert resumen[0].progreso.total == 1


def test_eliminar_deadline_desvincula_tareas(deadlines, tareas):
    deadline = deadlines.crear("Proyecto")
    tarea = tareas.crear("Vinculada", deadline_id=deadline.id)

    deadlines.eliminar(deadline.id)

    assert tareas.obtener(tarea.id).deadline_id is None
    assert deadlines.listar() == []


def test_completar_deadline(deadlines):
    deadline = deadlines.crear("Proyecto")
    assert deadlines.completar(deadline.id).completado is True
    assert deadlines.reabrir(deadline.id).completado is False


def test_operar_sobre_deadline_inexistente(deadlines):
    with pytest.raises(NoEncontrado):
        deadlines.completar("no-existe")
    with pytest.raises(NoEncontrado):
        deadlines.eliminar("no-existe")


def test_resumen_filtra_por_periodo(deadlines):
    hoy = date(2026, 11, 5)  # jueves
    deadlines.crear("Hoy", fecha_limite=hoy)
    deadlines.crear("Semana", fecha_limite=date(2026, 11, 3))
    deadlines.crear("Otro mes", fecha_limite=date(2026, 12, 1))
    deadlines.crear("Sin fecha")

    diario = deadlines.resumen(periodo=Periodo.DIARIO, hoy=hoy)
    semanal = deadlines.resumen(periodo=Periodo.SEMANAL, hoy=hoy)
    mensual = deadlines.resumen(periodo=Periodo.MENSUAL, hoy=hoy)

    assert [r.deadline.titulo for r in diario] == ["Hoy"]
    assert len(semanal) == 2
    assert len(mensual) == 2


def test_resumen_sin_periodo_devuelve_todos(deadlines):
    deadlines.crear("Con fecha", fecha_limite=date(2026, 11, 5))
    deadlines.crear("Sin fecha")
    assert len(deadlines.resumen()) == 2


def test_resumen_filtra_por_rango_de_fechas(deadlines):
    deadlines.crear("Antes", fecha_limite=date(2026, 11, 1))
    deadlines.crear("Dentro", fecha_limite=date(2026, 11, 7))
    deadlines.crear("Después", fecha_limite=date(2026, 11, 20))
    deadlines.crear("Sin fecha")

    en_plazo = deadlines.resumen(desde=date(2026, 11, 5), hasta=date(2026, 11, 10))
    assert [r.deadline.titulo for r in en_plazo] == ["Dentro"]
