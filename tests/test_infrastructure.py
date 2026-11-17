"""Pruebas del cliente HTTP de Turso y de la base SQLite."""

from __future__ import annotations

from datetime import datetime

import pytest

from src.shared.domain.errors import ErrorDeSincronizacion
from src.shared.infrastructure.database import Database, default_db_path
from src.shared.infrastructure.turso_client import (
    TursoClient,
    _normalizar_url,
    _parametro,
)


# --------------------------------------------------------------- Turso
def test_normalizar_url():
    assert _normalizar_url("libsql://caos.turso.io/") == "https://caos.turso.io"
    assert _normalizar_url("caos.turso.io") == "https://caos.turso.io"
    assert _normalizar_url("https://caos.turso.io") == "https://caos.turso.io"


def test_parametros_tipados():
    assert _parametro(None) == {"type": "null"}
    assert _parametro(True) == {"type": "integer", "value": "1"}
    assert _parametro(False) == {"type": "integer", "value": "0"}
    assert _parametro(7) == {"type": "integer", "value": "7"}
    assert _parametro(1.5) == {"type": "float", "value": "1.5"}
    assert _parametro("hola") == {"type": "text", "value": "hola"}
    assert _parametro(b"ab")["type"] == "blob"


class _Respuesta:
    def __init__(self, cuerpo=None, status_code: int = 200) -> None:
        self._cuerpo = cuerpo or {"results": [{"type": "ok"}]}
        self.status_code = status_code
        self.text = "detalle del error"

    def json(self):
        return self._cuerpo


class _SesionFalsa:
    def __init__(self, respuesta: _Respuesta | None = None) -> None:
        self.respuesta = respuesta or _Respuesta()
        self.url = None
        self.kwargs = None

    def post(self, url, **kwargs):
        self.url = url
        self.kwargs = kwargs
        return self.respuesta


def test_pipeline_payload_y_headers():
    sesion = _SesionFalsa()
    cliente = TursoClient("libsql://caos.turso.io", "token-123", session=sesion)

    cliente.execute_many([("INSERT INTO t VALUES (?, ?)", ("x", 1))])

    assert sesion.url == "https://caos.turso.io/v2/pipeline"
    assert sesion.kwargs["headers"]["Authorization"] == "Bearer token-123"
    peticiones = sesion.kwargs["json"]["requests"]
    assert peticiones[-1] == {"type": "close"}
    stmt = peticiones[0]["stmt"]
    assert stmt["sql"] == "INSERT INTO t VALUES (?, ?)"
    assert stmt["args"] == [
        {"type": "text", "value": "x"},
        {"type": "integer", "value": "1"},
    ]


def test_error_en_resultado_de_turso():
    respuesta = _Respuesta(
        {"results": [{"type": "error", "error": {"message": "tabla inexistente"}}]}
    )
    cliente = TursoClient(
        "https://caos.turso.io", "token", session=_SesionFalsa(respuesta)
    )

    with pytest.raises(ErrorDeSincronizacion, match="tabla inexistente"):
        cliente.execute_many([("SELECT 1", ())])


def test_http_error():
    cliente = TursoClient(
        "https://caos.turso.io",
        "token",
        session=_SesionFalsa(_Respuesta(status_code=401)),
    )
    with pytest.raises(ErrorDeSincronizacion, match="401"):
        cliente.execute_many([("SELECT 1", ())])


def test_cliente_sin_credenciales():
    cliente = TursoClient("", "", session=_SesionFalsa())
    assert cliente.configurado is False


def test_ejecutar_decodifica_filas_tipadas():
    cuerpo = {
        "results": [
            {
                "type": "ok",
                "response": {
                    "type": "execute",
                    "result": {
                        "cols": [
                            {"name": "id"},
                            {"name": "numero"},
                            {"name": "nada"},
                        ],
                        "rows": [
                            [
                                {"type": "text", "value": "abc"},
                                {"type": "integer", "value": "7"},
                                {"type": "null"},
                            ]
                        ],
                    },
                },
            },
            {"type": "ok", "response": {"type": "close"}},
        ]
    }
    cliente = TursoClient(
        "https://caos.turso.io", "token", session=_SesionFalsa(_Respuesta(cuerpo))
    )

    assert cliente.consultar("SELECT id, numero, nada FROM t") == [
        {"id": "abc", "numero": 7, "nada": None}
    ]


def test_ejecutar_alinea_resultados_por_sentencia():
    cuerpo = {
        "results": [
            {
                "type": "ok",
                "response": {
                    "type": "execute",
                    "result": {
                        "cols": [{"name": "a"}],
                        "rows": [[{"type": "integer", "value": "1"}]],
                    },
                },
            },
            {
                "type": "ok",
                "response": {
                    "type": "execute",
                    "result": {"cols": [{"name": "b"}], "rows": []},
                },
            },
            {"type": "ok", "response": {"type": "close"}},
        ]
    }
    cliente = TursoClient(
        "https://caos.turso.io", "token", session=_SesionFalsa(_Respuesta(cuerpo))
    )

    resultados = cliente.ejecutar([("SELECT 1", ()), ("SELECT 2", ())])

    assert resultados == [[{"a": 1}], []]


# -------------------------------------------------------------- SQLite
def test_esquema_creado(db: Database):
    for tabla in ("tareas", "deadlines", "notas", "settings"):
        assert db.tabla_existe(tabla)


def test_default_db_path_respeta_variables(monkeypatch, tmp_path):
    monkeypatch.setenv("CAOS_DB_PATH", str(tmp_path / "custom.db"))
    assert default_db_path() == str(tmp_path / "custom.db")

    monkeypatch.delenv("CAOS_DB_PATH")
    monkeypatch.setenv("FLET_APP_STORAGE_DATA", str(tmp_path / "storage"))
    assert default_db_path().endswith("caos_local.db")
    assert str(tmp_path / "storage") in default_db_path()


def test_datetime_iso_se_conserva(db: Database):
    from src.domains.tareas.models.tarea import Tarea
    from src.domains.tareas.infrastructure.sqlite_tarea_repository import (
        SqliteTareaRepository,
    )

    repo = SqliteTareaRepository(db)
    tarea = Tarea(titulo="Con fecha")
    repo.add(tarea)

    recuperada = repo.get(tarea.id)
    assert isinstance(recuperada.updated_at, datetime)
    assert recuperada.updated_at.tzinfo is not None


def _crear_base_antigua(ruta, *, con_fecha: bool, version: int) -> None:
    import sqlite3

    columna_fecha = "fecha TEXT," if con_fecha else ""
    conexion = sqlite3.connect(ruta)
    conexion.execute(
        f"""
        CREATE TABLE tareas (
            id            TEXT PRIMARY KEY,
            titulo        TEXT NOT NULL,
            descripcion   TEXT NOT NULL DEFAULT '',
            prioridad     INTEGER NOT NULL,
            completada    INTEGER NOT NULL DEFAULT 0,
            deadline_id   TEXT,
            {columna_fecha}
            deleted       INTEGER NOT NULL DEFAULT 0,
            synced        INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT NOT NULL,
            updated_at    TEXT NOT NULL
        )
        """
    )
    conexion.execute(
        "INSERT INTO tareas (id, titulo, prioridad, created_at, updated_at) "
        "VALUES ('t1', 'Vieja', 1, ?, ?)",
        ("2020-01-01T00:00:00+00:00", "2020-01-01T00:00:00+00:00"),
    )
    conexion.execute(f"PRAGMA user_version = {version}")
    conexion.commit()
    conexion.close()


def test_migracion_anade_columna_y_hereda_fecha(tmp_path):
    ruta = tmp_path / "viejo.db"
    _crear_base_antigua(ruta, con_fecha=False, version=2)

    db = Database(str(ruta))
    db.initialize()
    try:
        columnas = {fila["name"] for fila in db.query("PRAGMA table_info(tareas)")}
        assert "fecha" in columnas
        assert db.query_one("SELECT fecha FROM tareas WHERE id = 't1'")["fecha"] == (
            "2020-01-01"
        )
        assert db.query_one("PRAGMA user_version")[0] == 4
    finally:
        db.close()


def test_migracion_rellena_fecha_aunque_la_columna_ya_exista(tmp_path):
    ruta = tmp_path / "v3.db"
    _crear_base_antigua(ruta, con_fecha=True, version=3)

    db = Database(str(ruta))
    db.initialize()
    try:
        assert db.query_one("SELECT fecha FROM tareas WHERE id = 't1'")["fecha"] == (
            "2020-01-01"
        )
        assert db.query_one("PRAGMA user_version")[0] == 4
    finally:
        db.close()


def test_migracion_no_pisa_una_fecha_ya_puesta(tmp_path):
    ruta = tmp_path / "v3b.db"
    _crear_base_antigua(ruta, con_fecha=True, version=3)
    import sqlite3

    conexion = sqlite3.connect(ruta)
    conexion.execute("UPDATE tareas SET fecha = '2030-05-05' WHERE id = 't1'")
    conexion.commit()
    conexion.close()

    db = Database(str(ruta))
    db.initialize()
    try:
        assert db.query_one("SELECT fecha FROM tareas WHERE id = 't1'")["fecha"] == (
            "2030-05-05"
        )
    finally:
        db.close()
