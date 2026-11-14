"""Errores transversales del sistema CAOS."""

from __future__ import annotations


class CaosError(Exception):
    """Raíz de todos los errores controlados de la aplicación."""


class ErrorDeDominio(CaosError):
    """Violación de una regla de negocio."""


class ErrorDeValidacion(ErrorDeDominio):
    """Un dato no cumple el contrato del dominio."""


class NoEncontrado(ErrorDeDominio):
    """La entidad solicitada no existe o fue eliminada."""


class ErrorDeSincronizacion(CaosError):
    """Fallo al comunicarse con Turso."""


class TursoNoConfigurado(ErrorDeSincronizacion):
    """Faltan las credenciales de Turso en el entorno."""
