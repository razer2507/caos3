"""Pruebas del bus de eventos y del progreso compartido."""

from __future__ import annotations

from src.shared.application.event_bus import EventBus


def test_publicar_y_desuscribir():
    bus = EventBus()
    recibidos: list[object] = []

    def listener(payload):
        recibidos.append(payload)

    bus.suscribir("tema", listener)
    bus.publicar("tema", 1)
    bus.publicar("tema", 2)

    bus.desuscribir("tema", listener)
    bus.publicar("tema", 3)

    assert recibidos == [1, 2]


def test_no_duplica_listeners():
    bus = EventBus()
    llamadas: list[int] = []

    def listener(_payload):
        llamadas.append(1)

    bus.suscribir("tema", listener)
    bus.suscribir("tema", listener)
    bus.publicar("tema")

    assert len(llamadas) == 1


def test_un_listener_roto_no_impide_a_los_demas():
    bus = EventBus()
    llamadas: list[str] = []

    def roto(_payload):
        raise RuntimeError("boom")

    bus.suscribir("tema", roto)
    bus.suscribir("tema", lambda _p: llamadas.append("ok"))
    bus.publicar("tema")

    assert llamadas == ["ok"]
