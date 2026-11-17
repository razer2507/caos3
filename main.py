"""CAOS 3.0 — Punto de entrada de la aplicación Flet."""

from __future__ import annotations

import logging

import flet as ft

from src.shared.infrastructure.database import Database, default_db_path
from src.shared.presentation.app_context import AppContext
from src.shared.presentation.shell import AppShell
from src.shared.presentation.theme import configurar_pagina

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
)
logger = logging.getLogger("caos")


def main(page: ft.Page) -> None:
    """Composition root: construye la base de datos, el contexto y la UI."""
    configurar_pagina(page)

    try:
        db = Database(default_db_path())
        db.initialize()
    except Exception as exc:  # pragma: no cover - arranque defensivo
        logger.exception("No se pudo inicializar la base de datos")
        page.add(
            ft.SafeArea(
                ft.Container(
                    padding=24,
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                color=ft.Colors.RED_400,
                                size=42,
                            ),
                            ft.Text(
                                "No se pudo abrir la base de datos local",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                str(exc),
                                color=ft.Colors.RED_200,
                                selectable=True,
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        )
        return

    context = AppContext.crear(page=page, db=db)
    # Android 15+ dibuja la app de borde a borde (targetSdk 36). SafeArea añade
    # el espacio de la barra de estado, el notch y la barra de gestos para que
    # ningún control quede tapado por el sistema.
    page.add(ft.SafeArea(content=AppShell(context), expand=True))
    page.update()

    # Sincronización automática: revisa Internet y trae/sube cambios sin que
    # el usuario tenga que pulsar el botón. Sigue funcionando el botón manual.
    context.auto_sync.iniciar(page)

    logger.info("CAOS 3.0 iniciado. Base de datos: %s", db.path)


if __name__ == "__main__":
    ft.run(main,assets_dir='assets')
