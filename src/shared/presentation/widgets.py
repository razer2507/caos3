"""Utilidades de presentación reutilizables."""

from __future__ import annotations

from datetime import date, datetime

import flet as ft

from src.domains.tareas.models.value_objects import Prioridad
from src.shared.presentation.theme import (
    COLOR_ACENTO,
    COLOR_ACENTO_2,
    COLOR_PELIGRO,
    COLOR_SUPERFICIE,
    COLOR_SUPERFICIE_ALT,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
)

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)
DIAS = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

COLORES_PRIORIDAD = {
    Prioridad.IMPORTANTE_URGENTE: COLOR_PELIGRO,
    Prioridad.IMPORTANTE_NO_URGENTE: "#F5B942",
    Prioridad.NO_IMPORTANTE_URGENTE: "#4AA8FF",
    Prioridad.NO_IMPORTANTE_NO_URGENTE: "#8B93A7",
}


def fecha_larga(dia: date | None = None) -> str:
    dia = dia or date.today()
    return f"{DIAS[dia.weekday()]}, {dia.day} de {MESES[dia.month - 1]}"


def fecha_corta(dia: date) -> str:
    return f"{dia.day:02d}/{dia.month:02d}/{dia.year}"


def hace_cuanto(momento: datetime) -> str:
    delta = datetime.now(momento.tzinfo) - momento
    segundos = int(delta.total_seconds())
    if segundos < 60:
        return "ahora"
    if segundos < 3600:
        return f"hace {segundos // 60} min"
    if segundos < 86400:
        return f"hace {segundos // 3600} h"
    return f"hace {segundos // 86400} d"


def avisar(page: ft.Page, mensaje: str, *, error: bool = False) -> None:
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=COLOR_PELIGRO if error else COLOR_SUPERFICIE_ALT,
            duration=2600,
        )
    )


def encabezado(titulo: str, subtitulo: str, acciones: list[ft.Control] | None = None) -> ft.Row:
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=2,
                expand=True,
                controls=[
                    ft.Text(titulo, size=24, weight=ft.FontWeight.W_800, color=COLOR_TEXTO),
                    ft.Text(subtitulo, size=12.5, color=COLOR_TEXTO_SUAVE),
                ],
            ),
            ft.Row(spacing=2, controls=acciones or []),
        ],
    )


def pill_prioridad(prioridad: Prioridad) -> ft.Container:
    color = COLORES_PRIORIDAD[prioridad]
    return ft.Container(
        bgcolor=ft.Colors.with_opacity(0.16, color),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        tooltip=f"{prioridad.codigo} · {prioridad.etiqueta} ({prioridad.descripcion})",
        content=ft.Text(
            prioridad.codigo,
            size=11,
            weight=ft.FontWeight.W_700,
            color=color,
        ),
    )


def chip(texto: str, *, icono: ft.IconData | None = None, color: str = COLOR_ACENTO) -> ft.Container:
    controles: list[ft.Control] = []
    if icono:
        controles.append(ft.Icon(icono, size=12, color=color))
    controles.append(ft.Text(texto, size=11, color=color, weight=ft.FontWeight.W_500))
    return ft.Container(
        bgcolor=ft.Colors.with_opacity(0.12, color),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        content=ft.Row(controls=controles, spacing=4, tight=True),
    )


def estado_vacio(icono: ft.IconData, titulo: str, subtitulo: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(vertical=44, horizontal=20),
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icono, size=44, color=ft.Colors.with_opacity(0.35, COLOR_ACENTO_2)),
                ft.Text(titulo, size=16, weight=ft.FontWeight.W_600, color=COLOR_TEXTO),
                ft.Text(
                    subtitulo,
                    size=12.5,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )


def tarjeta(contenido: ft.Control, *, padding: int = 14) -> ft.Container:
    return ft.Container(
        bgcolor=COLOR_SUPERFICIE,
        border_radius=16,
        padding=padding,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE)),
        content=contenido,
    )


def campo_texto(
    *,
    etiqueta: str,
    valor: str = "",
    pista: str | None = None,
    multilinea: bool = False,
    lineas: int = 1,
    on_change=None,
    on_submit=None,
) -> ft.TextField:
    return ft.TextField(
        label=etiqueta,
        value=valor,
        hint_text=pista,
        multiline=multilinea,
        min_lines=lineas if multilinea else 1,
        max_lines=max(lineas, 4) if multilinea else 1,
        filled=True,
        bgcolor=COLOR_SUPERFICIE_ALT,
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=12,
                side=ft.BorderSide(width=1, color="transparent"),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=12,
                side=ft.BorderSide(width=1, color=COLOR_ACENTO),
            ),
        },
        color=COLOR_TEXTO,
        label_style=ft.TextStyle(color=COLOR_TEXTO_SUAVE, size=12),
        on_change=on_change,
        on_submit=on_submit,
    )


def selector(
    *,
    etiqueta: str,
    opciones: list[tuple[str, str]],
    valor: str | None = None,
) -> ft.Dropdown:
    return ft.Dropdown(
        label=etiqueta,
        value=valor,
        options=[ft.DropdownOption(key=k, text=v) for k, v in opciones],
        filled=True,
        bgcolor=COLOR_SUPERFICIE_ALT,
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=12,
                side=ft.BorderSide(width=1, color="transparent"),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=12,
                side=ft.BorderSide(width=1, color=COLOR_ACENTO),
            ),
        },
        text_style=ft.TextStyle(color=COLOR_TEXTO, size=14),
        label_style=ft.TextStyle(color=COLOR_TEXTO_SUAVE, size=12),
    )
