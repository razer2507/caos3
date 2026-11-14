"""Composition root de la aplicación: ensambla dominios e infraestructura."""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft

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
from src.shared.application.auto_sync import AutoSync
from src.shared.application.event_bus import EventBus
from src.shared.application.sync_service import SyncService
from src.shared.infrastructure.database import Database
from src.shared.infrastructure.settings_repository import SettingsRepository
from src.shared.infrastructure.turso_client import TursoClient
from src.shared.presentation.effects import Effects


@dataclass
class AppContext:
    """Dependencias compartidas por todas las vistas."""

    page: ft.Page
    db: Database
    bus: EventBus
    settings: SettingsRepository
    deadlines_repo: SqliteDeadlineRepository
    tareas_repo: SqliteTareaRepository
    notas_repo: SqliteNotaRepository
    deadlines: DeadlineService
    tareas: TareaService
    notas: NotaService
    sync: SyncService
    auto_sync: AutoSync
    effects: Effects

    @classmethod
    def crear(cls, *, page: ft.Page, db: Database) -> "AppContext":
        bus = EventBus()

        settings = SettingsRepository(db)
        turso_url, turso_token = settings.turso_credenciales()

        deadlines_repo = SqliteDeadlineRepository(db)
        tareas_repo = SqliteTareaRepository(db)
        notas_repo = SqliteNotaRepository(db)

        sync = SyncService(
            TursoClient(turso_url, turso_token),
            deadlines_repo,
            tareas_repo,
            notas_repo,
            bus,
        )

        return cls(
            page=page,
            db=db,
            bus=bus,
            settings=settings,
            deadlines_repo=deadlines_repo,
            tareas_repo=tareas_repo,
            notas_repo=notas_repo,
            deadlines=DeadlineService(deadlines_repo, tareas_repo, bus),
            tareas=TareaService(tareas_repo, bus),
            notas=NotaService(notas_repo, bus),
            sync=sync,
            auto_sync=AutoSync(sync, bus),
            effects=Effects(page),
        )
