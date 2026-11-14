"""Genera el efecto de sonido de éxito (assets/sounds/success.wav).

Uso: python scripts/generate_sound.py
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

FRECUENCIA_MUESTREO = 44100
DURACION = 0.62
NOTAS = [
    (523.25, 0.00, 0.20),  # C5
    (783.99, 0.13, 0.24),  # G5
    (1046.50, 0.28, 0.30),  # C6
]


def generar(destino: Path) -> None:
    muestras: list[int] = []
    total = int(FRECUENCIA_MUESTREO * DURACION)
    for i in range(total):
        t = i / FRECUENCIA_MUESTREO
        valor = 0.0
        for frecuencia, inicio, duracion in NOTAS:
            if inicio <= t < inicio + duracion:
                local = t - inicio
                envolvente = min(1.0, local / 0.008) * math.exp(-4.0 * local)
                valor += 0.32 * envolvente * math.sin(2 * math.pi * frecuencia * local)
                valor += 0.07 * envolvente * math.sin(4 * math.pi * frecuencia * local)
        valor = max(-1.0, min(1.0, valor))
        muestras.append(int(valor * 32767))

    destino.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destino), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(FRECUENCIA_MUESTREO)
        wav.writeframes(struct.pack("<%dh" % len(muestras), *muestras))


if __name__ == "__main__":
    ruta = Path(__file__).resolve().parent.parent / "assets" / "sounds" / "success.wav"
    generar(ruta)
    print(f"Generado {ruta} ({ruta.stat().st_size} bytes)")
