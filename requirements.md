# 🚀 Documento de Requisitos y Especificaciones Técnicas: CAOS 3.0

## 1. Descripción General del Proyecto
**CAOS 3.0** es un sistema de productividad personal offline-first (estilo "Notion propio"), diseñado para PC y dispositivos móviles (Android). Combina una arquitectura limpia basada en **DDD (Domain-Driven Design) modular por dominios**, persistencia local con **SQLite y UUIDs**, sincronización remota con **Turso**, y estímulos de diseño **dopaminérgicos** (feedback visual y sonoro) para gamificar el cumplimiento de tareas.

---

## 2. Stack Tecnológico
* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica (UI):** Flet (Multiplataforma: Escritorio y Android)
* **Base de Datos Local:** SQLite nativo (`sqlite3`) con manejo de IDs mediante `uuid4` (para evitar colisiones offline).
* **Sincronización Cloud:** Turso (vía API HTTP REST / libSQL).
* **Pruebas:** `pytest`

---

## 3. Arquitectura del Software (DDD Modular)
El proyecto debe seguir estrictamente una estructura por dominios verticales para aislar la lógica de negocio de la interfaz y la persistencia:

```
caos_system/
│
├── main.py                     # Punto de entrada de Flet
├── requirements.txt            # Dependencias (flet, requests, etc.)
│
├── src/                        # Código fuente
│   ├── shared/                 # Recursos transversales
│   │   ├── infrastructure/     # Conexión SQLite local
│   │   └── presentation/       # Efectos de audio y animación dopaminérgica
│   │
│   └── domains/                # Bounded Contexts / Módulos de dominio
│       ├── tareas/             # Módulo Tareas (Sueltas o vinculadas a Deadlines)
│       │   ├── models/         # Entidades de dominio (dataclasses) y Value Objects
│       │   ├── application/    # Casos de uso (orquestadores de negocio)
│       │   ├── infrastructure/ # Repositorios SQLite + UUIDs
│       │   └── presentation/   # Vistas Flet (UI)
│       ├── deadlines/          # Módulo de Proyectos / Hitos con fecha límite
│       └── notas/              # Módulo de Notas vinculadas a áreas y deadlines
│
└── tests/                      # Pruebas unitarias e integración con pytest
```

---

## 4. Requisitos Funcionales (RF)

### 📌 Módulo de Tareas (`tareas`)
* **RF01:** Creación de tareas con soporte para tareas sueltas (`deadline_id = NULL`) o vinculadas a un proyecto (`deadline_id = 'xyz'`).
* **RF02:** Asignación obligatoria de prioridades basadas en la Matriz de Eisenhower (ej. `1(IMPORTANTE Y URGENTE)`, `2(...)`).
* **RF03:** Identificadores únicos universales (`UUID v4`) generados en la aplicación (Python) antes de persistir, permitiendo operación 100% offline sin colisiones de claves primarias al sincronizar.
* **RF04:** Cambio de estado (completado/pendiente) gestionado mediante reglas de negocio en el Modelo (`dataclass`), coordinado por un Caso de Uso y persistido por el Repositorio.

### 🎯 Estímulos Dopaminérgicos (Gamificación)
* **RF05:** Al marcar una tarea como completada, la UI debe disparar de forma concurrente:
  1. Un efecto de sonido de éxito (`ft.Audio`).
  2. Una microanimación visual o cambio temporal de color en la tarjeta.
  3. Una barra de progreso diaria que actualice su porcentaje en tiempo real.

### 🔄 Persistencia y Sincronización Offline-First
* **RF06:** Lectura y escritura directa sobre un archivo SQLite local (`caos_local.db`) en el dispositivo del usuario.
* **RF07:** Estructura preparada para enviar los registros pendientes de sincronización hacia la base de datos en la nube (Turso) mediante peticiones HTTP.

---

## 5. Requisitos No Funcionales (RNF)
* **RNF01 (Multiplataforma):** El código de UI en Flet debe renderizarse correctamente tanto en pantallas de escritorio como en móviles (Android).
* **RNF02 (Testeabilidad):** La capa de Dominio y Casos de Uso debe estar completamente desacoplada de Flet y SQLite, permitiendo pruebas unitarias instantáneas con `pytest`.
* **RNF03 (Mantenibilidad):** Principios SOLID aplicados en la separación de responsabilidades (UI no toca base de datos, Casos de Uso no implementan SQL crudo).
