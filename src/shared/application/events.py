"""Temas de eventos compartidos entre dominios y UI."""

TAREAS_CAMBIADAS = "tareas.cambiadas"
DEADLINES_CAMBIADOS = "deadlines.cambiados"
NOTAS_CAMBIADAS = "notas.cambiadas"
DATOS_CAMBIADOS = "datos.cambiados"
# Cambió el estado de sincronización (pendientes, última pasada, etc.).
SYNC_CAMBIADO = "sync.cambiado"

TODOS_LOS_TEMAS = (
    TAREAS_CAMBIADAS,
    DEADLINES_CAMBIADOS,
    NOTAS_CAMBIADAS,
    DATOS_CAMBIADOS,
    SYNC_CAMBIADO,
)
