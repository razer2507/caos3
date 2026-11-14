"""Bus de eventos síncrono e in-process para desacoplar las vistas."""

from __future__ import annotations

import logging
from collections import defaultdict
from threading import RLock
from typing import Any, Callable

logger = logging.getLogger(__name__)

Callback = Callable[[Any], None]


class EventBus:
    """Publicador/suscriptor minimalista y thread-safe."""

    def __init__(self) -> None:
        self._suscriptores: dict[str, list[Callback]] = defaultdict(list)
        self._lock = RLock()

    def suscribir(self, tema: str, callback: Callback) -> None:
        with self._lock:
            if callback not in self._suscriptores[tema]:
                self._suscriptores[tema].append(callback)

    def desuscribir(self, tema: str, callback: Callback) -> None:
        with self._lock:
            if callback in self._suscriptores[tema]:
                self._suscriptores[tema].remove(callback)

    def publicar(self, tema: str, payload: Any = None) -> None:
        with self._lock:
            callbacks = list(self._suscriptores.get(tema, ()))

        for callback in callbacks:
            try:
                callback(payload)
            except Exception:  # pragma: no cover - un listener roto no debe tumbar la app
                logger.exception("Error en suscriptor del tema %s", tema)
