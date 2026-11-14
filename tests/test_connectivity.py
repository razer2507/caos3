"""Pruebas de la sonda de conectividad."""

from __future__ import annotations

from src.shared.infrastructure import connectivity
from src.shared.infrastructure.connectivity import hay_internet


class _ConexionFalsa:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_hay_internet_ok(monkeypatch):
    monkeypatch.setattr(
        connectivity.socket,
        "create_connection",
        lambda *_a, **_k: _ConexionFalsa(),
    )

    assert hay_internet() is True


def test_hay_internet_falla_si_no_hay_red(monkeypatch):
    def sin_red(*_a, **_k):
        raise OSError("sin red")

    monkeypatch.setattr(connectivity.socket, "create_connection", sin_red)

    assert hay_internet() is False


def test_hay_internet_prueba_el_segundo_destino(monkeypatch):
    intentos = []

    def conexion(destino, timeout=0):
        intentos.append(destino)
        if len(intentos) == 1:
            raise OSError("primer destino bloqueado")
        return _ConexionFalsa()

    monkeypatch.setattr(connectivity.socket, "create_connection", conexion)

    assert hay_internet() is True
    assert intentos == [connectivity.DESTINOS[0], connectivity.DESTINOS[1]]
