"""Comprobación ligera de conectividad a Internet.

No sustituye a una petición real: solo evita intentar sincronizar cuando el
dispositivo está claramente desconectado. Si la sonda dice que hay red pero
Turso no responde, la sincronización falla y se reintenta en la siguiente
vuelta.
"""

from __future__ import annotations

import socket

# Direcciones públicas con HTTPS. Se prueban en orden y basta con que una
# acepte la conexión TCP.
DESTINOS: tuple[tuple[str, int], ...] = (
    ("1.1.1.1", 443),
    ("8.8.8.8", 443),
)


def hay_internet(timeout: float = 2.0) -> bool:
    """Devuelve ``True`` si se puede abrir una conexión TCP a algún destino."""
    for host, puerto in DESTINOS:
        try:
            with socket.create_connection((host, puerto), timeout=timeout):
                return True
        except OSError:
            continue
    return False
