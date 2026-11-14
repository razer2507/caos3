"""Pruebas del almacenamiento local de ajustes y credenciales de Turso."""

from __future__ import annotations

from src.shared.infrastructure.settings_repository import (
    CLAVE_TURSO_TOKEN,
    CLAVE_TURSO_URL,
    SettingsRepository,
)
from src.shared.infrastructure.turso_client import TursoClient


def test_esquema_incluye_settings(db):
    assert db.tabla_existe("settings")


def test_guardar_y_leer(db):
    repo = SettingsRepository(db)

    assert repo.get("inexistente") == ""
    assert repo.get("inexistente", "por defecto") == "por defecto"

    repo.set("clave", "valor")
    assert repo.get("clave") == "valor"

    repo.set("clave", "otro")
    assert repo.get("clave") == "otro"

    repo.eliminar("clave")
    assert repo.get("clave") == ""


def test_turso_usa_lo_guardado(db, monkeypatch):
    monkeypatch.delenv("TURSO_DATABASE_URL", raising=False)
    monkeypatch.delenv("TURSO_AUTH_TOKEN", raising=False)

    repo = SettingsRepository(db)
    assert repo.turso_credenciales() == ("", "")

    repo.guardar_turso("libsql://caos.turso.io", "token-123")
    assert repo.turso_credenciales() == ("libsql://caos.turso.io", "token-123")
    assert repo.get(CLAVE_TURSO_URL) == "libsql://caos.turso.io"
    assert repo.get(CLAVE_TURSO_TOKEN) == "token-123"


def test_turso_cae_al_entorno_si_no_hay_guardado(db, monkeypatch):
    monkeypatch.setenv("TURSO_DATABASE_URL", "https://env.turso.io")
    monkeypatch.setenv("TURSO_AUTH_TOKEN", "env-token")

    repo = SettingsRepository(db)
    assert repo.turso_credenciales() == ("https://env.turso.io", "env-token")


def test_lo_guardado_gana_al_entorno(db, monkeypatch):
    monkeypatch.setenv("TURSO_DATABASE_URL", "https://env.turso.io")
    monkeypatch.setenv("TURSO_AUTH_TOKEN", "env-token")

    repo = SettingsRepository(db)
    repo.guardar_turso("https://movil.turso.io", "token-movil")
    assert repo.turso_credenciales() == ("https://movil.turso.io", "token-movil")


def test_borrar_turso(db, monkeypatch):
    monkeypatch.delenv("TURSO_DATABASE_URL", raising=False)
    monkeypatch.delenv("TURSO_AUTH_TOKEN", raising=False)

    repo = SettingsRepository(db)
    repo.guardar_turso("https://caos.turso.io", "token")
    repo.borrar_turso()
    assert repo.turso_credenciales() == ("", "")


def test_cliente_actualiza_credenciales_en_caliente(monkeypatch):
    monkeypatch.delenv("TURSO_DATABASE_URL", raising=False)
    monkeypatch.delenv("TURSO_AUTH_TOKEN", raising=False)

    cliente = TursoClient("", "")
    assert cliente.configurado is False

    cliente.actualizar_credenciales("libsql://caos.turso.io/", " token ")
    assert cliente.url == "https://caos.turso.io"
    assert cliente.token == "token"
    assert cliente.configurado is True

    cliente.actualizar_credenciales("", "")
    assert cliente.configurado is False
