"""Pruebas de persistencia SQLite (RF03, RF06, RF07)."""

from __future__ import annotations

from datetime import date

from src.domains.deadlines.models.deadline import Deadline
from src.domains.notas.models.nota import Nota
from src.domains.tareas.models.tarea import Tarea
from src.domains.tareas.models.value_objects import Prioridad


def test_roundtrip_de_tarea(tareas_repo):
    tarea = Tarea(titulo="Persistirme", prioridad=Prioridad.NO_IMPORTANTE_URGENTE)

    tareas_repo.add(tarea)
    recuperada = tareas_repo.get(tarea.id)

    assert recuperada is not None
    assert recuperada.titulo == "Persistirme"
    assert recuperada.prioridad is Prioridad.NO_IMPORTANTE_URGENTE
    assert recuperada.created_at == tarea.created_at


def test_roundtrip_de_fecha_de_tarea(tareas_repo):
    con_fecha = Tarea(titulo="Con fecha", fecha=date(2026, 11, 5))
    sin_fecha = Tarea(titulo="Sin fecha")
    tareas_repo.add(con_fecha)
    tareas_repo.add(sin_fecha)

    assert tareas_repo.get(con_fecha.id).fecha == date(2026, 11, 5)
    assert tareas_repo.get(sin_fecha.id).fecha is None


def test_list_all_filtra_completadas_y_ordena_por_prioridad(tareas_repo):
    alta = Tarea(titulo="P1", prioridad=Prioridad.IMPORTANTE_URGENTE)
    baja = Tarea(titulo="P4", prioridad=Prioridad.NO_IMPORTANTE_NO_URGENTE)
    hecha = Tarea(titulo="Hecha", prioridad=Prioridad.IMPORTANTE_URGENTE, completada=True)
    for t in (baja, hecha, alta):
        tareas_repo.add(t)

    todas = tareas_repo.list_all()
    assert [t.titulo for t in todas] == ["P1", "P4", "Hecha"]

    pendientes = tareas_repo.list_all(incluir_completadas=False)
    assert {t.titulo for t in pendientes} == {"P1", "P4"}


def test_list_by_deadline_incluye_tareas_sueltas(tareas_repo, deadlines_repo):
    deadline = Deadline(titulo="Proyecto")
    deadlines_repo.add(deadline)
    vinculada = Tarea(titulo="Vinculada", deadline_id=deadline.id)
    suelta = Tarea(titulo="Suelta")
    tareas_repo.add(vinculada)
    tareas_repo.add(suelta)

    assert [t.titulo for t in tareas_repo.list_by_deadline(deadline.id)] == ["Vinculada"]
    assert [t.titulo for t in tareas_repo.list_by_deadline(None)] == ["Suelta"]


def test_borrado_logico_oculta_pero_queda_pendiente_de_sync(tareas_repo):
    tarea = Tarea(titulo="Para borrar")
    tareas_repo.add(tarea)
    tareas_repo.mark_synced([tarea.id])
    assert tareas_repo.list_pending() == []

    tareas_repo.delete(tarea.id)

    assert tareas_repo.get(tarea.id) is None
    pendientes = tareas_repo.list_pending()
    assert len(pendientes) == 1
    assert pendientes[0].deleted is True
    assert pendientes[0].synced is False


def test_mark_synced(tareas_repo):
    tarea = Tarea(titulo="Subir")
    tareas_repo.add(tarea)
    assert len(tareas_repo.list_pending()) == 1

    tareas_repo.mark_synced([tarea.id])
    assert tareas_repo.list_pending() == []
    assert tareas_repo.get(tarea.id).synced is True


def test_repositorio_deadlines_roundtrip_y_orden(deadlines_repo):
    sin_fecha = Deadline(titulo="Sin fecha")
    con_fecha = Deadline(titulo="Con fecha", fecha_limite="2026-12-31")
    deadlines_repo.add(sin_fecha)
    deadlines_repo.add(con_fecha)

    lista = deadlines_repo.list_all()
    assert [d.titulo for d in lista] == ["Con fecha", "Sin fecha"]
    assert deadlines_repo.get(con_fecha.id).fecha_limite.year == 2026


def test_repositorio_notas_busca_por_titulo_contenido_y_area(notas_repo):
    notas_repo.add(Nota(titulo="Ideas", contenido="usar SQLite", area="Tech"))
    notas_repo.add(Nota(titulo="Personal", contenido="comprar pan", area="Casa"))

    assert [n.titulo for n in notas_repo.list_all(buscar="sqlite")] == ["Ideas"]
    assert [n.titulo for n in notas_repo.list_all(buscar="Casa")] == ["Personal"]
    assert [n.titulo for n in notas_repo.list_all(buscar="nada")] == []


def test_eliminar_nota_es_borrado_logico(notas_repo):
    nota = Nota(titulo="Temporal")
    notas_repo.add(nota)
    notas_repo.delete(nota.id)

    assert notas_repo.get(nota.id) is None
    assert notas_repo.list_pending()[0].deleted is True
