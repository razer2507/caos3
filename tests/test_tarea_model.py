"""Pruebas de las reglas de negocio de Tarea (RF01–RF04)."""

from __future__ import annotations

from datetime import date
from uuid import UUID

import pytest

from src.domains.tareas.models.tarea import Tarea
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.domain.errors import ErrorDeValidacion
from src.shared.domain.periodos import Periodo


def test_id_es_uuid_v4_generado_en_la_app():
    tarea = Tarea(titulo="Comprar café")
    assert UUID(tarea.id).version == 4


def test_titulo_se_normaliza():
    tarea = Tarea(titulo="   escribir   el    informe  ")
    assert tarea.titulo == "escribir el informe"


def test_titulo_vacio_es_invalido():
    with pytest.raises(ErrorDeValidacion):
        Tarea(titulo="   ")


def test_titulo_demasiado_largo_es_invalido():
    with pytest.raises(ErrorDeValidacion):
        Tarea(titulo="x" * 121)


def test_prioridad_por_defecto_es_eisenhower_1():
    tarea = Tarea(titulo="Llamar al banco")
    assert tarea.prioridad is Prioridad.IMPORTANTE_URGENTE


def test_prioridad_invalida_es_rechazada():
    with pytest.raises(ErrorDeValidacion):
        Tarea(titulo="X", prioridad=9)


def test_prioridad_se_convierte_desde_entero_y_texto():
    assert Prioridad.desde(2) is Prioridad.IMPORTANTE_NO_URGENTE
    assert Prioridad.desde("4") is Prioridad.NO_IMPORTANTE_NO_URGENTE


def test_completar_y_reabrir_gestionan_estado_y_sincronizacion():
    tarea = Tarea(titulo="Publicar release", synced=True)

    assert tarea.completar() is True
    assert tarea.completada is True
    assert tarea.synced is False

    assert tarea.completar() is False  # idempotente

    assert tarea.reabrir() is True
    assert tarea.completada is False

    assert tarea.reabrir() is False


def test_alternar_devuelve_el_nuevo_estado():
    tarea = Tarea(titulo="Revisar PR")
    assert tarea.alternar() is True
    assert tarea.alternar() is False


def test_actualizar_valida_y_normaliza():
    tarea = Tarea(titulo="Original", synced=True)

    tarea.actualizar(
        titulo="  Nuevo título  ",
        descripcion="  detalle  ",
        prioridad=3,
    )

    assert tarea.titulo == "Nuevo título"
    assert tarea.descripcion == "detalle"
    assert tarea.prioridad is Prioridad.NO_IMPORTANTE_URGENTE
    assert tarea.synced is False


def test_actualizar_sin_cambios_no_toca_updated_at():
    tarea = Tarea(titulo="Igual")
    original = tarea.updated_at
    tarea.actualizar(titulo="Igual")
    assert tarea.updated_at == original


def test_vincular_y_desvincular_deadline():
    tarea = Tarea(titulo="Tarea de proyecto")
    assert tarea.deadline_id is None

    tarea.vincular_deadline("deadline-123")
    assert tarea.deadline_id == "deadline-123"

    tarea.desvincular_deadline()
    assert tarea.deadline_id is None


def test_borrado_logico_es_idempotente():
    tarea = Tarea(titulo="Efímera")
    tarea.marcar_eliminada()
    primera_fecha = tarea.updated_at

    tarea.marcar_eliminada()
    assert tarea.deleted is True
    assert tarea.updated_at == primera_fecha


def test_fecha_iso_se_convierte():
    tarea = Tarea(titulo="Con fecha", fecha="2026-12-24")
    assert tarea.fecha == date(2026, 12, 24)


def test_actualizar_fecha_marca_sincronizacion():
    tarea = Tarea(titulo="Planificar", synced=True)
    tarea.actualizar(fecha=date(2026, 11, 5))
    assert tarea.fecha == date(2026, 11, 5)
    assert tarea.synced is False


def test_en_periodo_sin_fecha_siempre_falso():
    tarea = Tarea(titulo="Sin fecha")
    assert tarea.en_periodo(Periodo.DIARIO, date(2026, 11, 5)) is False


def test_en_periodo_detecta_el_dia():
    tarea = Tarea(titulo="Hoy", fecha=date(2026, 11, 5))
    assert tarea.en_periodo(Periodo.DIARIO, date(2026, 11, 5)) is True
    assert tarea.en_periodo(Periodo.DIARIO, date(2026, 11, 6)) is False
