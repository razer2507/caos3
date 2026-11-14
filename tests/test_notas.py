"""Pruebas del módulo de notas."""

from __future__ import annotations

import pytest

from src.shared.domain.errors import NoEncontrado


def test_crear_listar_y_buscar(notas):
    notas.crear("Arquitectura", contenido="SQLite + UUID", area="Tech")
    notas.crear("Mercado", contenido="pan y café", area="Casa")

    assert len(notas.listar()) == 2
    assert [n.titulo for n in notas.listar(buscar="uuid")] == ["Arquitectura"]
    assert [n.titulo for n in notas.listar(buscar="Casa")] == ["Mercado"]


def test_editar_nota(notas, deadlines):
    deadline = deadlines.crear("Proyecto")
    nota = notas.crear("Idea", contenido="texto", area="General")

    actualizada = notas.editar(
        nota.id,
        titulo="Idea mejorada",
        contenido="texto nuevo",
        area="Producto",
        deadline_id=deadline.id,
    )

    assert actualizada.titulo == "Idea mejorada"
    assert actualizada.contenido == "texto nuevo"
    assert actualizada.area == "Producto"
    assert actualizada.deadline_id == deadline.id


def test_resumen_recorta_contenido(notas):
    nota = notas.crear("Larga", contenido="x" * 500)
    assert len(nota.resumen) <= 160
    assert nota.resumen.endswith("...")


def test_resumen_vacio(notas):
    nota = notas.crear("Vacía")
    assert nota.resumen == "Sin contenido"


def test_eliminar_nota(notas, notas_repo):
    nota = notas.crear("Efímera")

    notas.eliminar(nota.id)

    assert notas.listar() == []
    assert notas_repo.get(nota.id) is None
    assert notas_repo.list_pending()[0].deleted is True


def test_listar_por_deadline(notas, deadlines):
    d1 = deadlines.crear("Proyecto 1")
    d2 = deadlines.crear("Proyecto 2")
    a = notas.crear("A", deadline_id=d1.id)
    notas.crear("B", deadline_id=d2.id)

    assert [n.id for n in notas.listar_por_deadline(d1.id)] == [a.id]


def test_nota_inexistente(notas):
    with pytest.raises(NoEncontrado):
        notas.editar("no-existe", titulo="X")
    with pytest.raises(NoEncontrado):
        notas.eliminar("no-existe")
