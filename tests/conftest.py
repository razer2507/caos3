"""Fixtures compartidas de pytest."""

from __future__ import annotations

import pytest

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
from src.shared.application.event_bus import EventBus
from src.shared.infrastructure.database import Database


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "caos_test.db"))
    database.initialize()
    yield database
    database.close()


@pytest.fixture
def bus() -> EventBus:
    return EventBus()


@pytest.fixture
def deadlines_repo(db) -> SqliteDeadlineRepository:
    return SqliteDeadlineRepository(db)


@pytest.fixture
def tareas_repo(db) -> SqliteTareaRepository:
    return SqliteTareaRepository(db)


@pytest.fixture
def notas_repo(db) -> SqliteNotaRepository:
    return SqliteNotaRepository(db)


@pytest.fixture
def tareas(tareas_repo, bus) -> TareaService:
    return TareaService(tareas_repo, bus)


@pytest.fixture
def deadlines(deadlines_repo, tareas_repo, bus) -> DeadlineService:
    return DeadlineService(deadlines_repo, tareas_repo, bus)


@pytest.fixture
def notas(notas_repo, bus) -> NotaService:
    return NotaService(notas_repo, bus)
