"""Captura screenshots de la UI real para revisión de diseño.

Uso:
    python scripts/capture_ui.py

Requiere Pillow y el cliente de escritorio de Flet. Guarda PNGs en ``artifacts/``.
Se usa captura del sistema (no ``page.take_screenshot``) porque el modo de
captura integrado de Flet maximiza la ventana en Windows.
"""

from __future__ import annotations

import asyncio
import ctypes
import os
import sys
import time
from ctypes import wintypes
from datetime import date, timedelta
from pathlib import Path
from tempfile import gettempdir

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import flet as ft
from PIL import ImageGrab

from src.domains.deadlines.application.deadline_service import DeadlineService
from src.domains.deadlines.infrastructure.sqlite_deadline_repository import (
    SqliteDeadlineRepository,
)
from src.domains.notas.application.nota_service import NotaService
from src.domains.notas.infrastructure.sqlite_nota_repository import SqliteNotaRepository
from src.domains.tareas.application.tarea_service import TareaService
from src.domains.tareas.infrastructure.sqlite_tarea_repository import (
    SqliteTareaRepository,
)
from src.domains.tareas.models.value_objects import Prioridad
from src.shared.application.event_bus import EventBus
from src.shared.infrastructure.database import Database

DESTINO = Path(__file__).resolve().parent.parent / "artifacts"
TITULO_VENTANA = "CAOS 3.0"

try:  # Coordenadas físicas en pantallas con escalado (125 %, 150 %, etc.).
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:  # pragma: no cover - depende de Windows
    pass


# --------------------------------------------------------------------- demo
def sembrar_demo(db: Database) -> None:
    bus = EventBus()
    tareas_repo = SqliteTareaRepository(db)
    deadlines_repo = SqliteDeadlineRepository(db)
    notas_repo = SqliteNotaRepository(db)
    deadlines = DeadlineService(deadlines_repo, tareas_repo, bus)
    tareas = TareaService(tareas_repo, bus)
    notas = NotaService(notas_repo, bus)

    hoy = date.today()
    web = deadlines.crear(
        "Lanzamiento web",
        fecha_limite=hoy + timedelta(days=12),
        area="Producto",
        descripcion="Publicar la nueva landing y el onboarding.",
    )
    mudanza = deadlines.crear(
        "Mudanza",
        fecha_limite=hoy + timedelta(days=3),
        area="Personal",
        descripcion="Cerrar cajas, cambiar servicios y limpieza final.",
    )
    deadlines.crear(
        "Curso de inglés",
        fecha_limite=hoy + timedelta(days=40),
        area="Aprendizaje",
    )

    hecha = tareas.crear(
        "Cerrar copy de la landing",
        Prioridad.IMPORTANTE_URGENTE,
        deadline_id=web.id,
    )
    tareas.completar(hecha.id)
    tareas.crear(
        "Revisar responsive en móvil",
        Prioridad.IMPORTANTE_URGENTE,
        deadline_id=web.id,
        descripcion="Probar 360px, 390px y tablet.",
    )
    tareas.crear(
        "Contratar hosting definitivo",
        Prioridad.IMPORTANTE_NO_URGENTE,
        deadline_id=web.id,
    )
    tareas.crear(
        "Comprar cinta y cajas",
        Prioridad.NO_IMPORTANTE_URGENTE,
        deadline_id=mudanza.id,
    )
    tareas.crear(
        "Leer 20 páginas al día",
        Prioridad.IMPORTANTE_NO_URGENTE,
        descripcion="Hábito suelto, sin proyecto.",
    )
    tareas.crear(
        "Ordenar escritorio",
        Prioridad.NO_IMPORTANTE_NO_URGENTE,
    )

    notas.crear(
        "Decisiones de arquitectura",
        contenido=(
            "SQLite local con UUID v4 para poder trabajar offline. "
            "Turso como espejo en la nube cuando haya red."
        ),
        area="Tech",
        deadline_id=web.id,
    )
    notas.crear(
        "Checklist de mudanza",
        contenido="Agua, luz, internet, seguro, llaves y limpieza.",
        area="Casa",
        deadline_id=mudanza.id,
    )
    notas.crear(
        "Ideas sueltas",
        contenido="Probar un modo enfoque de 25 minutos y un resumen semanal.",
        area="Producto",
    )


# ---------------------------------------------------------------- captura
def _rect_ventana() -> tuple[int, int, int, int] | None:
    hwnd = ctypes.windll.user32.FindWindowW(None, TITULO_VENTANA)
    if not hwnd:
        return None
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def _capturar(nombre: str) -> None:
    # Aparta el cursor: un tooltip nativo podría quedar dentro del recorte.
    try:
        ctypes.windll.user32.SetCursorPos(0, 890)
    except Exception:
        pass
    time.sleep(0.35)
    bbox = _rect_ventana()
    if bbox is None:
        print(f"No se encontró la ventana {TITULO_VENTANA!r}; se omite {nombre}")
        return
    time.sleep(0.15)
    imagen = ImageGrab.grab(bbox=bbox, all_screens=True)
    ruta = DESTINO / nombre
    imagen.save(ruta)
    print(f"Guardado {ruta} ({imagen.width}x{imagen.height})", flush=True)


async def capturar(page: ft.Page) -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    await asyncio.sleep(1.5)
    await page.window.to_front()
    await asyncio.sleep(2.5)

    # Primer cuadro de calentamiento: el cliente puede dejar zonas sin pintar
    # justo tras mostrarse la ventana y contaminar la primera captura.
    _rect_ventana()
    time.sleep(0.8)

    shell = page.controls[0]
    await page.window.to_front()
    _capturar("01_tareas.png")

    for indice, nombre in ((1, "02_proyectos.png"), (2, "03_notas.png")):
        shell.ir_a(indice)
        await asyncio.sleep(0.5)
        await page.window.to_front()
        _capturar(nombre)

    shell.ir_a(0)
    await asyncio.sleep(0.3)
    vista = shell._vistas[0]
    vista._abrir_dialogo()
    await asyncio.sleep(0.6)
    await page.window.to_front()
    _capturar("04_dialogo_tarea.png")
    page.pop_dialog()

    shell.ir_a(1)
    await asyncio.sleep(0.3)
    shell._vistas[1]._abrir_dialogo()
    await asyncio.sleep(0.6)
    await page.window.to_front()
    _capturar("05_dialogo_proyecto.png")
    page.pop_dialog()

    shell._abrir_sync()
    await asyncio.sleep(0.5)
    await page.window.to_front()
    _capturar("06_sync.png")
    page.pop_dialog()

    # Cierra la ventana del cliente para no dejar ventanas huérfanas que
    # contaminen la siguiente captura.
    try:
        await page.window.destroy()
    except Exception:
        pass
    await asyncio.sleep(0.4)
    os._exit(0)


def main(page: ft.Page) -> None:
    from main import main as app_main

    app_main(page)
    page.run_task(capturar, page)


if __name__ == "__main__":
    if os.name == "nt":
        # Evita que clientes Flet de ejecuciones anteriores queden encima.
        os.system("taskkill /IM flet.exe /F >nul 2>&1")

    db_path = os.path.join(gettempdir(), "caos_demo_ui.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["CAOS_DB_PATH"] = db_path

    db = Database(db_path)
    db.initialize()
    sembrar_demo(db)
    db.close()

    ft.run(main)
