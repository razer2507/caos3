"""Paleta y configuración visual de CAOS 3.0."""

from __future__ import annotations

import flet as ft

# ------------------------------------------------------------------ paleta
COLOR_FONDO = "#0B0D12"
COLOR_SUPERFICIE = "#141824"
COLOR_SUPERFICIE_ALT = "#1C2130"
COLOR_ACENTO = "#7C5CFF"
COLOR_ACENTO_2 = "#22D3A6"
COLOR_TEXTO = "#F2F4FA"
COLOR_TEXTO_SUAVE = "#98A0B6"
COLOR_PELIGRO = "#FF5C7A"
COLOR_EXITO = "#22D3A6"
COLOR_EXITO_SUAVE = "#173F35"


def configurar_pagina(page: ft.Page) -> None:
    """Aplica tema oscuro, tamaños y comportamiento multiplataforma."""
    page.title = "CAOS 3.0"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.spacing = 0
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    # En escritorio abre una ventana cómoda; en móvil Flet ignora estos valores.
    # Tamaño de escritorio cómodo que cabe en pantallas pequeñas (1280x720).
    page.window.width = 460
    page.window.height = 620
    page.window.min_width = 340
    page.window.min_height = 520
    page.window.maximized = False
    page.window.bgcolor = COLOR_FONDO
