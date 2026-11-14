"""Estímulos dopaminérgicos: sonido + microanimación (RF05)."""

from __future__ import annotations

import asyncio
import logging
import os
import threading

import flet as ft

from src.shared.presentation.theme import COLOR_EXITO_SUAVE

logger = logging.getLogger(__name__)

RUTA_SONIDO = "sounds/success.wav"


class Effects:
    """Feedback multisensorial tolerante a fallos.

    Si ``flet-audio`` no está disponible o el dispositivo no puede reproducir
    audio, cae a un pitido del sistema sin romper la interacción.
    """

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self._audio = None
        try:
            from flet_audio import Audio

            self._audio = Audio(src=RUTA_SONIDO, volume=0.65)
            # En Flet 1.x los servicios se adjuntan a la vista raíz.
            page.services.append(self._audio)
        except Exception:  # pragma: no cover - depende de la plataforma
            logger.warning(
                "Audio no disponible; se usará un pitido del sistema.", exc_info=True
            )

    # -------------------------------------------------------------- público
    async def celebrar(self, control: ft.Control | None = None) -> None:
        """Dispara sonido y animación de forma concurrente."""
        self._reproducir_sonido()

        if control is None:
            return

        original_bg = getattr(control, "bgcolor", None)
        try:
            control.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT)
            control.animate_scale = ft.Animation(190, ft.AnimationCurve.EASE_OUT_BACK)
            control.scale = 1.025
            control.bgcolor = COLOR_EXITO_SUAVE
            self.page.update()

            await asyncio.sleep(0.22)

            control.scale = 1.0
            control.bgcolor = original_bg
            self.page.update()
            await asyncio.sleep(0.08)
        except Exception:  # pragma: no cover - la animación nunca debe romper la UI
            logger.debug("No se pudo animar la tarjeta", exc_info=True)

    # -------------------------------------------------------------- privado
    def _reproducir_sonido(self) -> None:
        if self._audio is not None:
            try:
                self.page.run_task(self._audio.play)
                return
            except Exception:  # pragma: no cover
                logger.debug("Fallo al reproducir audio", exc_info=True)
        self._pitido()

    @staticmethod
    def _pitido() -> None:
        """Fallback nativo en un hilo para no bloquear la UI."""

        def _emitir() -> None:
            try:
                if os.name == "nt":
                    import winsound

                    winsound.Beep(880, 70)
                    winsound.Beep(1320, 110)
                else:
                    print("\a", end="", flush=True)
            except Exception:  # pragma: no cover
                logger.debug("Sin dispositivo de audio para el pitido")

        threading.Thread(target=_emitir, daemon=True).start()
