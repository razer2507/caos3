"""Cliente HTTP para la API de Turso (libSQL over HTTP)."""

from __future__ import annotations

import base64
import os
from typing import Any, Sequence

import requests

from src.shared.domain.errors import ErrorDeSincronizacion, TursoNoConfigurado


def _normalizar_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://") :]
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _parametro(valor: Any) -> dict[str, Any]:
    """Convierte un valor Python al formato tipado de la API de Turso."""
    if valor is None:
        return {"type": "null"}
    if isinstance(valor, bool):
        return {"type": "integer", "value": "1" if valor else "0"}
    if isinstance(valor, int):
        return {"type": "integer", "value": str(valor)}
    if isinstance(valor, float):
        return {"type": "float", "value": str(valor)}
    if isinstance(valor, (bytes, bytearray)):
        return {
            "type": "blob",
            "base64": base64.b64encode(bytes(valor)).decode("ascii"),
        }
    return {"type": "text", "value": str(valor)}


def _valor(celda: Any) -> Any:
    """Convierte una celda tipada de Turso al tipo Python equivalente."""
    if not isinstance(celda, dict):
        return celda
    tipo = celda.get("type")
    if tipo == "null":
        return None
    if tipo == "integer":
        return int(celda.get("value", 0))
    if tipo == "float":
        return float(celda.get("value", 0))
    if tipo == "blob":
        return base64.b64decode(celda.get("base64", ""))
    return celda.get("value")


class TursoClient:
    """Ejecuta sentencias contra Turso usando el endpoint ``/v2/pipeline``."""

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        *,
        session: requests.Session | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.url = _normalizar_url(url or os.getenv("TURSO_DATABASE_URL", ""))
        self.token = token or os.getenv("TURSO_AUTH_TOKEN", "")
        self.timeout = timeout
        self._session = session or requests.Session()

    def actualizar_credenciales(self, url: str, token: str) -> None:
        """Cambia las credenciales en caliente (por ejemplo desde Ajustes)."""
        self.url = _normalizar_url(url.strip())
        self.token = token.strip()

    @property
    def configurado(self) -> bool:
        return bool(self.url and self.token)

    def execute_many(self, sentencias: Sequence[tuple[str, Sequence[Any]]]) -> None:
        """Ejecuta varias sentencias en un único pipeline atómico."""
        self.ejecutar(sentencias)

    def ejecutar(
        self, sentencias: Sequence[tuple[str, Sequence[Any]]]
    ) -> list[list[dict[str, Any]]]:
        """Ejecuta sentencias y devuelve las filas de cada una.

        El resultado tiene la misma longitud que ``sentencias``: la posición
        ``i`` contiene las filas que devolvió la sentencia ``i``. Las
        sentencias de escritura devuelven una lista vacía.
        """
        if not self.configurado:
            raise TursoNoConfigurado(
                "Configura TURSO_DATABASE_URL y TURSO_AUTH_TOKEN para sincronizar."
            )

        requests_payload: list[dict[str, Any]] = [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": [_parametro(valor) for valor in params],
                },
            }
            for sql, params in sentencias
        ]
        requests_payload.append({"type": "close"})

        try:
            respuesta = self._session.post(
                f"{self.url}/v2/pipeline",
                json={"requests": requests_payload},
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ErrorDeSincronizacion(f"No se pudo conectar con Turso: {exc}") from exc

        if respuesta.status_code >= 400:
            raise ErrorDeSincronizacion(
                f"Turso respondió HTTP {respuesta.status_code}: {respuesta.text[:300]}"
            )

        try:
            cuerpo = respuesta.json()
        except ValueError as exc:
            raise ErrorDeSincronizacion("Respuesta inválida de Turso.") from exc

        filas_por_sentencia: list[list[dict[str, Any]]] = []
        for resultado in cuerpo.get("results", []):
            if resultado.get("type") == "error":
                mensaje = resultado.get("error", {}).get("message", "error desconocido")
                raise ErrorDeSincronizacion(f"Turso rechazó una sentencia: {mensaje}")

            respuesta_sql = resultado.get("response") or {}
            if respuesta_sql.get("type") != "execute":
                # El cierre del pipeline u otra respuesta no aporta filas.
                continue

            detalle = respuesta_sql.get("result") or {}
            columnas = [col.get("name") for col in detalle.get("cols") or []]
            filas_por_sentencia.append(
                [
                    {
                        columna: _valor(celda)
                        for columna, celda in zip(columnas, fila)
                    }
                    for fila in detalle.get("rows") or []
                ]
            )

        return filas_por_sentencia

    def consultar(
        self, sql: str, params: Sequence[Any] = ()
    ) -> list[dict[str, Any]]:
        """Atajo para ejecutar un único ``SELECT`` y devolver sus filas."""
        resultados = self.ejecutar([(sql, params)])
        return resultados[0] if resultados else []

    def ping(self) -> None:
        """Comprueba credenciales ejecutando una consulta trivial."""
        self.execute_many([("SELECT 1", ())])
