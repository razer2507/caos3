# Guía completa de CAOS 3.0

> **Para quién es esta guía:** para alguien que sabe muy poco de Python, Flet o bases de datos y quiere entender **todo** el proyecto: qué hace cada archivo, por qué está separado así y qué significa cada bloque de código.
>
> **Cómo leerla:** no hace falta memorizarla. Léela en orden la primera vez y vuelve a las secciones que necesites. Cada explicación indica el archivo y las líneas exactas (`archivo.py:12-20`) para que puedas abrir el código al lado.

---

## Índice

- [Cómo aprender este proyecto (ruta sugerida)](#cómo-aprender-este-proyecto-ruta-sugerida)
1. [Qué es CAOS 3.0](#1-qué-es-caos-30)
2. [Puesta en marcha en 5 minutos](#2-puesta-en-marcha-en-5-minutos)
3. [Glosario para principiantes](#3-glosario-para-principiantes)
4. [Estructura del proyecto, carpeta por carpeta](#4-estructura-del-proyecto-carpeta-por-carpeta)
5. [La arquitectura explicada con una servilleta](#5-la-arquitectura-explicada-con-una-servilleta)
6. [Recorridos completos: qué pasa al usar la app](#6-recorridos-completos-qué-pasa-al-usar-la-app)
7. [Convenciones del código](#7-convenciones-del-código)
8. [Código explicado archivo por archivo](#8-código-explicado-archivo-por-archivo)
9. [El esquema SQL explicado](#9-el-esquema-sql-explicado)
10. [La sincronización con Turso paso a paso](#10-la-sincronización-con-turso-paso-a-paso)
11. [Cómo añadir una funcionalidad nueva](#11-cómo-añadir-una-funcionalidad-nueva)
12. [Problemas conocidos y cómo depurarlos](#12-problemas-conocidos-y-cómo-depurarlos)
13. [Mapa rápido de archivos y líneas](#13-mapa-rápido-de-archivos-y-líneas)
14. [Ejercicios para practicar](#14-ejercicios-para-practicar)

---

## Cómo aprender este proyecto (ruta sugerida)

No leas los archivos en orden alfabético ni intentes memorizar Flet. El proyecto está hecho de **rebanadas verticales**: una misma funcionalidad (crear una tarea, crear una nota) atraviesa las cuatro capas. Si entiendes una rebanada completa, las demás se vuelven casi iguales.

### Fase 1 — Usar y ejecutar la app (una tarde)

1. Arranca la app y crea una tarea, un proyecto y una nota.
2. Ejecuta las pruebas con `.\.venv\Scripts\python.exe -m pytest`.
3. Lee los capítulos 2 y 3 (puesta en marcha y glosario). No sigas hasta tener claro qué es una clase, una función, un módulo y una base de datos.

### Fase 2 — Seguir una tarea de punta a punta (semana 1)

Este es el corazón del aprendizaje. Abre estos archivos **en este orden** y sigue el recorrido del capítulo 6.1:

| Orden | Archivo | Qué mirar |
|---|---|---|
| 1 | `main.py:21-71` | Cómo arranca la app, se crea el contexto, se aplica `SafeArea` y arranca el auto-sync. |
| 2 | `src/shared/presentation/app_context.py:46-79` | Dónde se conectan repositorios, servicios, bus, sync y auto-sync. |
| 3 | `src/domains/tareas/presentation/tareas_view.py:44-103` | Construcción de la pantalla. |
| 4 | `src/domains/tareas/presentation/tareas_view.py:116-127` | Qué pasa al pulsar "añadir". |
| 5 | `src/domains/tareas/application/tarea_service.py:45-61` | Caso de uso `crear()`. |
| 6 | `src/domains/tareas/models/tarea.py:15-32` | Validaciones del modelo. |
| 7 | `src/domains/tareas/infrastructure/sqlite_tarea_repository.py:40-52` | Cómo se escribe en SQLite. |
| 8 | `src/shared/infrastructure/database.py` | Conexión, esquema y migraciones. |

Al terminar deberías poder responder: ¿quién valida el título?, ¿quién genera el UUID?, ¿quién avisa a la UI de que hay una tarea nueva?

### Fase 3 — Las piezas compartidas (semana 2)

Ahora lee `src/shared/` con calma: `domain/entity.py`, `domain/errors.py`, `domain/value_objects.py`, `application/event_bus.py` y `presentation/widgets.py`. Son archivos cortos y los usan los tres dominios. Después lee las pruebas de `tests/test_event_bus.py` y `tests/test_tarea_service.py`: son la mejor documentación ejecutable del proyecto.

### Fase 4 — Comparar dominios (semana 3)

Abre `deadlines` y `notas` al lado de `tareas` y busca las diferencias, no las repeticiones:

- `src/domains/*/application/*_service.py`: mismos métodos, reglas distintas.
- `src/domains/*/infrastructure/sqlite_*_repository.py`: mismo patrón de SQL.
- `src/domains/*/presentation/*_view.py`: mismos widgets, distinta pantalla.

Cuando puedas explicar en voz alta en qué se diferencian los tres flujos, ya dominas la arquitectura.

### Fase 5 — Turso y sincronización (semana 4)

Déjala para el final. Lee `src/shared/infrastructure/turso_client.py`, `src/shared/application/sync_service.py`, `src/shared/application/auto_sync.py`, `src/shared/infrastructure/connectivity.py` y el capítulo 10. Antes de eso no la necesitas para entender la app.

### Técnicas que de verdad funcionan

- **Sigue un dato**: escribe "Comprar pan" y persíguelo desde el `TextField` hasta la fila de SQLite. Después hazlo al revés al arrancar la app.
- **Usa las pruebas como documentación**: abre un test, intenta predecir qué comprueba y ejecútalo con `.\.venv\Scripts\python.exe -m pytest tests/test_tarea_service.py -v`.
- **Rompe el código a propósito**: borra una validación o cambia un color y observa qué falla. Aprenderás más del error que del acierto.
- **Usa el depurador**: pon un punto de interrupción en `TareaService.crear` y en `TareasView.refrescar`, y avanza paso a paso.
- **Mira la base de datos**: abre `caos_local.db` con un visor de SQLite y comprueba la fila que acabas de crear.
- **Cuaderno de 3 preguntas**: al final de cada sesión anota qué entendiste, qué no y qué quieres probar mañana.

### Primeros retos, en orden de dificultad

1. Ejercicio 1: cambia el color de acento en `theme.py:11` y mira toda la app.
2. Ejercicio 3: muestra el área en la tarjeta de tarea (`tareas_view.py:213-262`).
3. Ejercicio 4: añade un filtro "P1" (`tareas_view.py:57-67` y `187-200`).
4. Ejercicio 5: escribe una prueba nueva en `tests/test_tarea_service.py`.
5. Ejercicios 6 y 7: simula un fallo de red y añade una nota rápida.

Regla de oro: **una mejora pequeña, ejecutarla, ejecutar las pruebas y recién entonces pasar a la siguiente**. Así se aprende un sistema grande sin ahogarse.

---

## 1. Qué es CAOS 3.0

CAOS 3.0 es una aplicación de productividad personal. Sirve para tres cosas:

- **Tareas:** anotar cosas que hay que hacer, con una prioridad obligatoria de la matriz de Eisenhower (importante/urgente).
- **Proyectos o deadlines:** agrupar tareas alrededor de un objetivo con fecha límite.
- **Notas:** guardar ideas, decisiones y contexto, opcionalmente ligadas a un proyecto.

La aplicación está pensada para funcionar **sin internet**:

1. Todo se guarda primero en un archivo **SQLite** local (`caos_local.db`).
2. Cada registro recibe un **UUID v4** generado en el propio dispositivo, así no hay choques de identificadores aunque estés desconectado.
3. Cuando tú quieras, pulsas el icono de la nube y la app **empuja** los cambios pendientes a **Turso** (una base de datos SQLite en la nube).

Además, al completar una tarea la app da **feedback inmediato**: un sonido, una pequeña animación en la tarjeta y una barra de progreso diaria que se actualiza.

### Las tres capas que debes distinguir desde el principio

| Capa | En este proyecto | Qué hace | Qué NO debe hacer |
|---|---|---|---|
| **Dominio / modelos** | `models/` | Reglas del negocio: validar un título, saber si un proyecto venció, cambiar el estado de una tarea. | No importa Flet ni SQLite. |
| **Aplicación / casos de uso** | `application/` | Coordinar: "crear tarea = crear entidad + guardarla + avisar a la UI". | No escribe SQL. |
| **Infraestructura** | `infrastructure/` | Hablar con SQLite y con Turso. | No decide reglas del negocio. |
| **Presentación / UI** | `presentation/` | Mostrar pantallas, capturar clics y llamar a los casos de uso. | No toca la base de datos directamente. |

Esto es **DDD modular** (Domain-Driven Design): cada módulo (`tareas`, `deadlines`, `notas`) tiene sus cuatro carpetas y solo comparte un pequeño "kernel" en `src/shared/`.

---

## 2. Puesta en marcha en 5 minutos

> La guía detallada de Windows está en [`docs.txt`](docs.txt). Aquí tienes lo esencial.

```powershell
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activarlo (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias de escritorio + desarrollo
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# 4. Ejecutar la app
.\.venv\Scripts\python.exe main.py

# 5. Ejecutar las pruebas
.\.venv\Scripts\python.exe -m pytest
```

Resultado esperado de las pruebas: **106 passed**.

### Dónde se guardan tus datos

La ruta se decide en `src/shared/infrastructure/database.py:64-82`, en este orden:

1. Si existe la variable `CAOS_DB_PATH`, se usa esa ruta.
2. Si existe `FLET_APP_STORAGE_DATA` (Android/iOS), se usa `caos_local.db` dentro de esa carpeta.
3. En escritorio, `~/.caos/caos_local.db`.

Para usar una base desechable:

```powershell
$env:CAOS_DB_PATH = "$env:TEMP\caos_demo.db"
.\.venv\Scripts\python.exe main.py
```

### Configurar Turso (escritorio y Android)

Tienes dos formas:

**1. Desde la propia app (recomendada, funciona en Android):**

1. Abre la app y pulsa el icono de nube en la cabecera.
2. Pega la **URL** de tu base Turso (por ejemplo `libsql://tu-base.turso.io`) y el **token**.
3. Pulsa **Probar conexión**. Si responde bien, pulsa **Guardar**.
4. La sincronización automática empezará en ~1 segundo. También puedes pulsar **Sincronizar ahora** para no esperar.

Los datos se guardan en la tabla `settings` de tu base local (`src/shared/infrastructure/settings_repository.py`), así que no tienes que escribirlos otra vez al reiniciar. La sincronización automática sube cada cambio local unos 2 segundos después de hacerlo, revisa Internet cada 2 minutos mientras la app está abierta, hace una última pasada al pasar a segundo plano o cerrar y también al volver a la app.

**2. Con variables de entorno (solo escritorio):**

```powershell
$env:TURSO_DATABASE_URL = "libsql://tu-base.turso.io"
$env:TURSO_AUTH_TOKEN = "tu-token"
```

Si no configuras nada, la app funciona igual; solo el botón de sincronizar quedará desactivado.

> En Android no hay variables de entorno: usa siempre la opción 1.

---

## 3. Glosario para principiantes

Antes de leer código, conviene tener claros estos términos.

### Python

- **Módulo:** un archivo `.py`.
- **Paquete:** una carpeta con un `__init__.py` dentro. Aquí casi todos los `__init__.py` están vacíos: solo sirven para que Python trate la carpeta como paquete.
- **Import:** traer código de otro archivo. Ejemplo: `from src.shared.domain.entity import Entity`.
- **`from __future__ import annotations`:** hace que las anotaciones de tipos se guarden como texto y no se evalúen al importar. Permite escribir `str | None` incluso en versiones antiguas de Python y evita problemas de importaciones circulares.
- **Anotación de tipo:** `def crear(titulo: str) -> Tarea:` significa "recibe un `str` y devuelve una `Tarea`". Python **no** lo comprueba al ejecutar; sirve para que el editor y las personas entiendan el contrato.
- **`dataclass`:** decorador que genera automáticamente `__init__`, `__repr__` y comparaciones a partir de los campos de la clase.
- **`field(default_factory=...)`:** indica cómo crear un valor por defecto **nuevo** para cada instancia (por ejemplo, un UUID distinto por tarea).
- **`@property`:** convierte un método en algo que se lee como un atributo (`tarea.resumen` en vez de `tarea.resumen()`).
- **`Protocol`:** describe un contrato ("cualquier objeto que tenga estos métodos"). No hace falta heredar de él; sirve para tipar y para poder sustituir SQLite por un doble de prueba.
- **`Enum` / `IntEnum`:** un conjunto cerrado de valores con nombre. `IntEnum` además se comporta como entero, lo que permite guardarlo directamente en SQLite.
- **`Final`:** marca una constante que no debería reasignarse.
- **`RLock`:** un candado reentrante; evita que dos hilos modifiquen la misma estructura a la vez.

### Arquitectura y datos

- **Entidad:** objeto con identidad propia (una tarea concreta). Se compara por `id`.
- **Value Object:** objeto sin identidad, definido solo por su valor (un título normalizado). Si cambia el valor, es otro objeto. Aquí `Titulo` es inmutable (`frozen=True`).
- **Caso de uso:** una operación que la app ofrece, por ejemplo `crear`, `completar`, `eliminar`.
- **Puerto:** interfaz que declara lo que la aplicación necesita (`TareaRepository`). La infraestructura proporciona el **adaptador** (`SqliteTareaRepository`).
- **Repositorio:** objeto que traduce entidades a filas de base de datos y viceversa.
- **Composition root:** el único lugar donde se construyen todas las piezas y se conectan. Aquí está en `src/shared/presentation/app_context.py`.
- **Event bus:** publicador/suscriptor interno. Un caso de uso publica "las tareas cambiaron" y las vistas que escuchan se refrescan sin conocerse entre sí.
- **Offline-first:** la app funciona completa sin red; la nube es una copia secundaria.
- **UUID v4:** identificador aleatorio de 128 bits, prácticamente imposible de repetir. Se genera en la app para poder crear registros sin conexión.
- **Soft delete / borrado lógico:** en vez de borrar la fila, se marca `deleted = 1`. Así la eliminación también puede viajar a la nube.
- **Upsert:** `INSERT ... ON CONFLICT(id) DO UPDATE`. Inserta si no existe; actualiza si ya existe.
- **WAL:** modo de SQLite que escribe primero en un diario (`-wal`) y luego consolida. Mejora la concurrencia.
- **Pipeline (Turso):** una petición HTTP que contiene varias sentencias SQL y se ejecuta en orden.
- **`synced`:** `0` significa "este registro tiene cambios que aún no están en la nube"; `1` significa "ya se subió".

### Flet

- **`ft.Page`:** la ventana/raíz de la aplicación.
- **Control:** cualquier elemento visual (`ft.Text`, `ft.Row`, `ft.Column`, `ft.Container`...).
- **`page.add(...)`:** agrega el control raíz a la página.
- **`page.update()`:** envía los cambios al cliente que dibuja la interfaz. Sin `update()` el cambio existe en Python pero no se ve.
- **`page.show_dialog(...)` / `page.pop_dialog()`:** abren y cierran diálogos (API de Flet 1.x).
- **`page.run_task(...)`:** ejecuta una función asíncrona sin bloquear la interfaz.
- **`expand=True`:** le dice a un control que ocupe el espacio disponible dentro de su padre.
- **`ft.Padding` / `ft.Margin`:** objetos de espaciado; en Flet 1.x no se usan los antiguos `padding=10` genéricos para todo.

---

## 4. Estructura del proyecto, carpeta por carpeta

```
Proyecto predeterminado/
├── main.py                         Punto de entrada de la app
├── pytest.ini                      Configuración de pytest
├── requirements.txt                Dependencias mínimas (flet, audio, requests)
├── requirements-desktop.txt        Añade flet-desktop
├── requirements-dev.txt            Añade pytest y Pillow
├── requirements.md                 Documento de requisitos original
├── README.md                       Presentación y uso
├── docs.txt                        Guía paso a paso de Windows
├── guide.md                        Esta guía
├── .gitignore
│
├── src/
│   ├── shared/                     Código común a todos los dominios
│   │   ├── domain/
│   │   │   ├── entity.py           Base de toda entidad (id, fechas, deleted, synced)
│   │   │   ├── errors.py           Jerarquía de errores controlados
│   │   │   └── value_objects.py    Value Object Titulo
│   │   ├── application/
│   │   │   ├── event_bus.py        Publicador/suscriptor síncrono
│   │   │   ├── events.py           Nombres de los temas de eventos
│   │   │   ├── sync_service.py     Subida + bajada de datos con Turso
│   │   │   └── auto_sync.py        Bucle de sincronización automática
│   │   ├── infrastructure/
│   │   │   ├── database.py         Conexión SQLite + esquema local
│   │   │   ├── connectivity.py     Sonda rápida de Internet
│   │   │   ├── settings_repository.py  Credenciales guardadas en el dispositivo
│   │   │   └── turso_client.py     Cliente HTTP de Turso
│   │   └── presentation/
│   │       ├── theme.py            Paleta y configuración de la página
│   │       ├── widgets.py          Componentes visuales reutilizables
│   │       ├── effects.py          Sonido + animación de recompensa
│   │       ├── app_context.py      Composition root
│   │       └── shell.py            Cabecera, progreso, navegación y sync
│   │
│   └── domains/
│       ├── tareas/
│       │   ├── models/
│       │   │   ├── tarea.py        Entidad Tarea y reglas de estado
│       │   │   └── value_objects.py Prioridad (Eisenhower)
│       │   ├── application/
│       │   │   ├── ports.py        Contrato TareaRepository
│       │   │   └── tarea_service.py Casos de uso y progreso diario
│       │   ├── infrastructure/
│       │   │   └── sqlite_tarea_repository.py
│       │   └── presentation/
│       │       └── tareas_view.py  Pantalla de tareas
│       ├── deadlines/              Misma estructura vertical
│       └── notas/                  Misma estructura vertical
│
├── tests/                          Pruebas con pytest
│   ├── conftest.py                 Fixtures compartidas
│   ├── test_tarea_model.py
│   ├── test_tarea_service.py
│   ├── test_deadlines.py
│   ├── test_notas.py
│   ├── test_repositories.py
│   ├── test_infrastructure.py
│   ├── test_sync_service.py
│   ├── test_auto_sync.py
│   ├── test_connectivity.py
│   ├── test_settings_repository.py
│   └── test_event_bus.py
│
├── scripts/
│   ├── capture_ui.py               Captura las pantallas reales
│   └── generate_sound.py           Genera success.wav
│
├── assets/sounds/success.wav       Sonido de éxito
└── artifacts/                      Capturas PNG de referencia
```

### Regla de oro de las dependencias

El proyecto depende **hacia dentro**:

```
presentation  →  application  →  models
      │               │
      └───────────────┴──→  infrastructure (solo al construir, en el composition root)
```

- `models` no importa nada de Flet ni de SQLite.
- `application` importa modelos, puertos y el bus de eventos; nunca SQL.
- `infrastructure` implementa los puertos usando SQLite/HTTP.
- `presentation` importa los casos de uso y el bus; nunca ejecuta SQL.

Si respetas esa dirección, puedes probar el negocio sin abrir una ventana y cambiar la base de datos sin tocar la UI.

---

## 5. La arquitectura explicada con una servilleta

Imagina un restaurante:

- **Modelos (cocina):** conocen las recetas. Una tarea sabe validarse y completarse; un proyecto sabe calcular sus días restantes.
- **Casos de uso (jefe de sala):** reciben el pedido del cliente, piden a la cocina lo que corresponde, lo guardan y avisan a los camareros.
- **Puertos (el menú):** dicen qué se puede pedir ("guardar tarea", "listar pendientes") sin decir cómo se cocina.
- **Repositorios (proveedores):** traen y llevan datos a SQLite o Turso.
- **UI (sala):** muestra el menú y toma el pedido; no entra a la cocina.
- **Composition root (gerente):** contrata a todos y los presenta.

### Las piezas clave

| Pieza | Archivo | Idea |
|---|---|---|
| `Entity` | `src/shared/domain/entity.py` | Todo registro tiene `id`, `created_at`, `updated_at`, `synced`, `deleted`. |
| `Titulo` | `src/shared/domain/value_objects.py` | Un título nunca es vacío ni gigante, y siempre está limpio. |
| `Prioridad` | `src/domains/tareas/models/value_objects.py` | Solo existen cuatro prioridades válidas (1–4). |
| `EventBus` | `src/shared/application/event_bus.py` | Las vistas se enteran de los cambios sin acoplarse. |
| `Database` | `src/shared/infrastructure/database.py` | Una sola conexión SQLite protegida por un candado. |
| `TursoClient` | `src/shared/infrastructure/turso_client.py` | Traduce Python al protocolo HTTP de Turso. |
| `SyncService` | `src/shared/application/sync_service.py` | Decide qué subir y en qué orden. |
| `AppContext` | `src/shared/presentation/app_context.py` | Construye y conecta todo. |
| `AppShell` | `src/shared/presentation/shell.py` | Marco visual: cabecera, progreso, navegación. |

### ¿Por qué un event bus y no llamadas directas?

Sin bus, al completar una tarea la vista de tareas tendría que avisar a mano a la barra de progreso, a la vista de proyectos y a los contadores. Eso crea dependencias en todas las direcciones.

Con bus:

1. `TareaService` publica `TAREAS_CAMBIADAS` y `DATOS_CAMBIADOS`.
2. `TareasView` escucha `TAREAS_CAMBIADAS` y se refresca.
3. `DeadlinesView` escucha `TAREAS_CAMBIADAS` para recalcular el avance de sus proyectos.
4. `AppShell` escucha todos los temas y recalcula el progreso diario.

Nadie necesita saber quién más está escuchando.

---

## 6. Recorridos completos: qué pasa al usar la app

Estos recorridos son la mejor forma de entender cómo encajan las piezas.

### 6.1 Crear una tarea rápida

1. El usuario escribe en el campo y pulsa Enter o el botón `+` (`tareas_view.py:50-55`, `84-96`).
2. `_crear_rapida` (`tareas_view.py:116-127`) lee el texto, comprueba que no esté vacío y llama a `self.ctx.tareas.crear(...)`.
3. `TareaService.crear` (`tarea_service.py:45-60`) crea una `Tarea`.
4. El constructor de `Tarea` (`tarea.py:24-30`) valida el título con `Titulo`, normaliza la prioridad y la descripción.
5. `Entity` ya le dio un `id` UUID v4, `created_at`, `updated_at`, `synced=False` y `deleted=False` (`entity.py:20-30`).
6. El servicio llama a `repo.add(tarea)`.
7. `SqliteTareaRepository.add` ejecuta el `_UPSERT` (`sqlite_tarea_repository.py:18-30`, `40-41`).
8. El servicio publica `TAREAS_CAMBIADAS` y `DATOS_CAMBIADOS` (`tarea_service.py:144-146`).
9. Las vistas suscritas se refrescan. La barra de progreso se actualiza.
10. La UI limpia el campo (`tareas_view.py:126-127`).

### 6.2 Completar una tarea y ver la recompensa

1. El usuario marca el checkbox (`tareas_view.py:216-220`).
2. `_alternar` (`tareas_view.py:129-146`) activa `_celebrando = True` y llama a `completar(tarea.id)`.
3. `TareaService.completar` (`tarea_service.py:82-87`) obtiene la tarea y llama a `tarea.completar()`.
4. `Tarea.completar` (`tarea.py:33-39`) comprueba que no estuviera ya completada; si había transición, pone `completada=True`, actualiza `updated_at` y marca `synced=False` con `_touch()`.
5. El servicio guarda y publica eventos. La vista de tareas **ignora** ese refresco mientras `_celebrando` es `True` (`tareas_view.py:106-108`), para que la animación no se corte.
6. La UI lanza `_celebrar` como tarea asíncrona (`tareas_view.py:142-143`).
7. `Effects.celebrar` (`effects.py:41-63`) reproduce el sonido y anima la tarjeta: escala a `1.025`, cambia el fondo, espera 0,22 s, vuelve a su sitio.
8. Al terminar, `_celebrando` vuelve a `False` y la vista se refresca (`tareas_view.py:148-153`).
9. `AppShell` recalcula el progreso: la tarea completada hoy suma al numerador; las pendientes forman parte del denominador.

### 6.3 Crear un proyecto y vincular una tarea

1. En la vista de proyectos, el botón `+` abre el diálogo (`deadlines_view.py:229-343`).
2. La fecha se elige con un `DatePicker`; se guarda en `fecha_holder["valor"]` porque las funciones internas necesitan **mutar** una variable capturada.
3. Al guardar, se llama a `DeadlineService.crear` (`deadline_service.py:50-66`).
4. `Deadline.__post_init__` (`deadline.py:23-29`) valida el título, normaliza el área, limpia la descripción y convierte una fecha ISO de texto a `date` si hace falta.
5. El repositorio guarda con upsert (`sqlite_deadline_repository.py:17-29`).
6. En el diálogo de tarea, el desplegable de proyecto lista los deadlines (`tareas_view.py:313-320`). Al guardar, `TareaService.editar` recibe `deadline_id`.
7. `Tarea.actualizar` (`tarea.py:58-96`) detecta el cambio, actualiza el campo y marca la tarea como pendiente de sync.

### 6.4 Eliminar un proyecto

1. `DeadlinesView._eliminar` muestra un diálogo de confirmación (`deadlines_view.py:202-226`).
2. Al confirmar, llama a `DeadlineService.eliminar` (`deadline_service.py:109-116`).
3. El servicio busca todas las tareas del proyecto y las desvincula (`deadline_id=None`), guardando cada una.
4. Luego marca el proyecto como eliminado (soft delete) y publica eventos de deadlines y de tareas.
5. Las tareas siguen existiendo como tareas sueltas. Esto se probó en `test_deadlines.py:87-94`.

### 6.5 Buscar notas

1. El usuario escribe en el campo de búsqueda (`notas_view.py:45-50`).
2. `_cambiar_busqueda` guarda el texto y refresca (`notas_view.py:79-81`).
3. `NotaService.listar(buscar=...)` llama al repositorio (`nota_service.py:65-66`).
4. El repositorio construye un `LIKE %texto%` sobre título, contenido y área (`sqlite_nota_repository.py:84-87`).
5. La vista reconstruye las tarjetas (`notas_view.py:83-107`).

### 6.6 Sincronizar con Turso

Hay dos caminos que terminan en el mismo sitio: el botón manual y el sincronizador automático.

**Camino manual**

1. El usuario pulsa la nube de la cabecera (`shell.py:44-49`).
2. `_abrir_sync` (`shell.py:216-335`) consulta si Turso está configurado y cuántos registros pendientes hay por dominio.
3. Si hay credenciales, el botón "Sincronizar ahora" se habilita.
4. `_sincronizar` (`shell.py:408-456`) deshabilita el botón, muestra "Sincronizando..." y llama a `SyncService.sincronizar`.
5. `SyncService.sincronizar` (`sync_service.py:194-201`) espera a que no haya otra pasada en curso y llama a `_sincronizar` (`sync_service.py:227-330`): lee los pendientes, construye las sentencias (esquema + deadlines + tareas + notas), añade las tres lecturas del *pull* y las envía en un solo pipeline.
6. Solo si Turso responde bien, marca `synced = 1` en local (`sync_service.py:301-304`).
7. Aplica las filas recibidas con `upsert_remoto`, publica eventos y la UI muestra enviados/recibidos y refresca el contador de pendientes.

**Camino automático**

1. Al arrancar, `main.py:69` llama a `AutoSync.iniciar` (`auto_sync.py:73-85`), que se suscribe a `DATOS_CAMBIADOS`, registra el ciclo de vida, prepara la intercepción del cierre en escritorio y programa el bucle con `page.run_task`.
2. El bucle (`auto_sync.py:98-101`) espera 1 segundo y luego repite cada 120 segundos.
3. En cada vuelta, `sincronizar_ahora` (`auto_sync.py:104-106`) delega en `_pasada` (`auto_sync.py:108-149`): comprueba que Turso esté configurado, lanza la sonda de red en un hilo aparte (`connectivity.py:21-29`) y, si hay Internet, ejecuta `SyncService.sincronizar_si_libre` en otro hilo para no congelar la UI.
4. Si ya hay una sincronización manual en curso, el candado compartido hace que la automática se omita en esa vuelta (`sync_service.py:203-225`).
5. Cuando creas, editas o borras algo, los servicios publican `DATOS_CAMBIADOS`. `_on_datos_cambiados` (`auto_sync.py:161-175`) reinicia un temporizador de 2 segundos y `_sincronizar_tras_debounce` (`auto_sync.py:177-197`) sube los pendientes. Así no hay que esperar al siguiente ciclo de 120 segundos.
6. Al recibir filas de la nube, `publicar_resultado` (`sync_service.py:342-359`) avisa a las vistas y al contador de pendientes.
7. Al pasar a segundo plano o cerrar (`HIDE`, `PAUSE`, `DETACH`), `_programar_final` (`auto_sync.py:200-207`) y `_sincronizar_final` (`auto_sync.py:209-224`) hacen una última pasada si quedan pendientes, esperando hasta 10 segundos a que se libere el candado.
8. En escritorio, `_configurar_cierre` (`auto_sync.py:238-251`) activa `prevent_close` y escucha `WindowEventType.CLOSE`; `_cerrar` (`auto_sync.py:272-290`) sincroniza y después destruye la ventana. En móvil no se intercepta nada: bastan `PAUSE`/`DETACH`.
9. Al volver a la app desde segundo plano (`auto_sync.py:227-235`), se pide una pasada inmediata sin esperar los 120 segundos.


---

## 7. Convenciones del código

Antes de entrar archivo por archivo, estas convenciones te ayudarán a leerlo:

- **Nombres en español:** `Tarea`, `Deadline`, `Nota`, `crear`, `editar`, `eliminar`, `listar`. Los términos técnicos universales se quedan en inglés (`EventBus`, `Repository`, `Protocol`).
- **Guion bajo delante:** `_repo`, `_notificar`, `_obtener`. Es una convención de Python para decir "esto es interno; no lo uses desde fuera".
- **`self`:** la instancia actual de la clase.
- **Constantes en mayúsculas:** `SCHEMA`, `UPSERT_TAREA`, `COLOR_ACENTO`.
- **Docstrings con triples comillas:** texto que explica qué hace un módulo, clase o función.
- **Comentarios de sección:** líneas como `# -------- comandos`. No cambian el comportamiento; ordenan la lectura.
- **Type hints en todas las firmas:** ayudan a detectar errores antes de ejecutar.
- **`raise ... from exc`:** conserva el error original como causa al lanzar uno propio.
- **`try/except` amplios solo en la UI:** si falla el audio o una animación, la app no debe romperse. En el dominio, los errores se lanzan con precisión.
- **Sentinel `SIN_CAMBIO`:** permite distinguir "no me pasaron este campo" de "me pasaron `None`". Sin él, no se podría desvincular un deadline.
---

## 8. Código explicado archivo por archivo

En esta sección recorremos **todos** los archivos. Para cada uno verás:

- su propósito,
- sus imports y por qué están,
- una explicación de cada bloque con las líneas exactas,
- y las trampas o decisiones importantes.

Los archivos `__init__.py` están vacíos a propósito: solo convierten la carpeta en un paquete importable. No aportan lógica, así que no se explican uno por uno.

---

### 8.1 `main.py` — el arranque

**Propósito:** crear la base de datos, construir el contexto de la app y montar la interfaz. Es el primer archivo que se ejecuta.

| Líneas | Qué ocurre |
|---|---|
| 1 | Docstring del módulo. |
| 3 | `from __future__ import annotations`: anotaciones perezosas. |
| 5 | `import logging`: registro de mensajes. |
| 7 | `import flet as ft`: alias corto de Flet. |
| 9-12 | Importa `Database`/`default_db_path`, `AppContext`, `AppShell` y `configurar_pagina`. |
| 14-17 | Configura el logging global: nivel INFO y formato con fecha, nivel y nombre del logger. |
| 18 | Crea el logger llamado `"caos"`. |
| 21-22 | Define `main(page)`, la función que Flet llama al abrir la ventana. |
| 23 | Aplica tema, tamaños y colores. |
| 25-27 | `try`: crea `Database` con la ruta resuelta e inicializa el esquema. |
| 28-29 | `except Exception`: si falla el arranque de la base, se registra el error. |
| 30-57 | Muestra una pantalla de error amigable con icono, título y el texto de la excepción, también dentro de `SafeArea`. `selectable=True` permite copiar el mensaje. |
| 58 | `return`: no sigue arrancando la app. |
| 60 | Construye el `AppContext` (repositorios, servicios, bus, sync, auto-sync, efectos). |
| 61-63 | Comentario que explica el *edge-to-edge* de Android 15+. |
| 64 | Agrega `AppShell` a la página envuelto en `ft.SafeArea(expand=True)`. |
| 65 | `page.update()`: ordena al cliente dibujar. |
| 67-69 | Arranca la sincronización automática con `context.auto_sync.iniciar(page)`. |
| 71 | Log informativo con la ruta de la base. |
| 74-75 | Si se ejecuta directamente (`python main.py`), llama a `ft.run(main)`. |

**Por qué la base se crea antes que la UI:** si no se puede abrir SQLite, no tiene sentido construir vistas que van a fallar. El `try/except` convierte un fallo técnico en un mensaje comprensible.

**Por qué `SafeArea`:** con `targetSdk 36`, Android 15 y superior dibujan la app de borde a borde. Sin `SafeArea`, la cabecera queda debajo de la barra de notificaciones y la navegación inferior puede chocar con la barra de gestos. `SafeArea` consulta los márgenes del sistema y desplaza el contenido lo necesario; en escritorio esos márgenes son cero, así que no cambia nada.

**Detalle:** `main(page)` no abre la ventana por sí solo. `ft.run(main)` es quien crea la página y llama a `main`. En los tests no se ejecuta `main`; se prueban las capas de abajo.

---

### 8.2 Archivos de configuración

#### `pytest.ini` (4 líneas)

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = -q
```

- `testpaths = tests`: por defecto, pytest busca pruebas solo en `tests/`.
- `pythonpath = .`: añade la raíz del proyecto al `PYTHONPATH`, para que `import src...` funcione sin instalar el paquete.
- `addopts = -q`: modo silencioso (menos ruido). Por eso, si quieres ver el resumen `106 passed`, ejecuta `python -m pytest` sin `-q` (la opción del archivo ya está puesta, pero el resumen se imprime igual al no añadir otra `-q`).

#### `requirements.txt` (3 líneas)

- `flet==1.1.0`: framework de UI.
- `flet-audio==1.1.0`: reproducción del sonido.
- `requests>=2.31.0`: cliente HTTP para Turso.

#### `requirements-desktop.txt` (2 líneas)

- `-r requirements.txt`: incluye las anteriores.
- `flet-desktop==1.1.0`: cliente nativo de escritorio. No se usa en Android.

#### `requirements-dev.txt` (3 líneas)

- `-r requirements-desktop.txt`: todo lo de escritorio.
- `pytest>=8.0.0`: pruebas.
- `pillow>=10.0.0`: solo para `scripts/capture_ui.py`.

#### `.gitignore`

Ignora `__pycache__`, `.venv`, bases `.db` y sus diarios `-wal`/`-shm`, carpetas de build de Flet (`build/`, `dist/`, `.flet/`) y `.env`. Así no se suben datos personales ni binarios generados.

#### `requirements.md`

Es el documento de requisitos original: describe RF01–RF07 y RNF01–RNF03. No se ejecuta; sirve para entender **por qué** existe cada módulo. Por ejemplo, RF03 exige UUID generados en la app y RF07 pide la estructura de sincronización.

#### `README.md` y `docs.txt`

- `README.md`: presentación, características, arquitectura, instalación, pruebas y limitaciones.
- `docs.txt`: guía extensa de Windows con comprobaciones y solución de problemas.

Esta `guide.md` es el complemento didáctico: explica el código línea a línea.

---

### 8.3 `src/shared/domain/entity.py` — la base de toda entidad

**Propósito:** que tareas, deadlines y notas compartan identidad, fechas y banderas de sincronización sin repetir código.

| Líneas | Explicación |
|---|---|
| 1 | Docstring: "Entidad base compartida por todos los bounded contexts". |
| 3 | Anotaciones perezosas. |
| 5-7 | Importa `dataclass`, `field`, `datetime`, `timezone` y `uuid4`. |
| 10-12 | `nuevo_id()` devuelve `str(uuid4())`. Se genera **en la app**, no en la base, para poder crear registros offline. |
| 15-17 | `ahora_utc()` devuelve `datetime.now(timezone.utc)`: fecha consciente de zona horaria. |
| 20 | `@dataclass(kw_only=True)`: todos los campos de la base se pasan por nombre (`Tarea(titulo=...)`), lo que evita conflictos de orden al heredar. |
| 21-22 | `class Entity`: base de la que heredan las tres entidades. |
| 24 | `id`: por defecto llama a `nuevo_id` para cada instancia. |
| 25-26 | `created_at` y `updated_at`: por defecto, el momento actual UTC. |
| 27-28 | `synced = False`: todo registro nuevo nace pendiente de subir. |
| 29-30 | `deleted = False`: todo registro nuevo está visible. |
| 32-35 | `_touch()`: actualiza `updated_at` y vuelve a marcar `synced=False`. Se llama cada vez que algo cambia. |
| 37-41 | `marcar_eliminada()`: si no estaba borrada, pone `deleted=True` y llama a `_touch()`. Es idempotente: llamarla dos veces no cambia la fecha. |

**Por qué `kw_only=True`:** al heredar, los campos de la clase base se colocan antes que los de la hija. Si todos fueran posicionales, `Tarea("Comprar pan")` podría intentar rellenar `id` en vez de `titulo`. Con `kw_only`, los campos heredados solo se pasan por nombre.

**Por qué se usa UTC:** evita ambigüedades si el dispositivo cambia de zona horaria. La UI convierte a hora local solo para mostrar (`hace_cuanto` y `progreso_diario`).

**Lo que `Entity` no hace:** no valida el título ni conoce prioridades. Eso es responsabilidad de cada dominio.

---

### 8.4 `src/shared/domain/errors.py` — errores controlados

**Propósito:** tener una jerarquía clara para distinguir errores de negocio de errores técnicos.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 6-7 | `CaosError`: raíz de todos los errores previstos. La UI puede capturar solo esta clase. |
| 10-11 | `ErrorDeDominio`: violación de una regla del negocio. |
| 14-15 | `ErrorDeValidacion`: un dato no cumple el contrato (título vacío, prioridad 9...). Hereda de `ErrorDeDominio`. |
| 18-19 | `NoEncontrado`: la entidad no existe o está eliminada. Hereda de `ErrorDeDominio`. |
| 22-23 | `ErrorDeSincronizacion`: fallo al hablar con Turso. Hereda directamente de `CaosError`. |
| 26-27 | `TursoNoConfigurado`: faltan URL o token. Hereda de `ErrorDeSincronizacion`. |

**Cómo se usa:** las vistas hacen `except CaosError as exc` y muestran `str(exc)` en un snackbar. Así no se filtran trazas técnicas al usuario. En cambio, si ocurre un `RuntimeError` inesperado, la vista deja que suba (o lo registra) porque es un bug que hay que investigar, no un error de negocio.

**Jerarquía resultante:**

```
Exception
└── CaosError
    ├── ErrorDeDominio
    │   ├── ErrorDeValidacion
    │   └── NoEncontrado
    └── ErrorDeSincronizacion
        └── TursoNoConfigurado
```

---

### 8.5 `src/shared/domain/value_objects.py` — el título válido

**Propósito:** centralizar la regla de qué es un título aceptable.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 5 | Importa `dataclass`. |
| 7 | Importa `ErrorDeValidacion`. |
| 9 | `LONGITUD_MAXIMA_TITULO = 120`. |
| 12 | `@dataclass(frozen=True, slots=True)`: inmutable y ligero. |
| 13-14 | `class Titulo` con un único campo `valor`. |
| 18-26 | `__post_init__`: se ejecuta justo después de construir el objeto. Limpia espacios con `" ".join(str(valor).split())`, rechaza vacío, rechaza más de 120 caracteres y guarda el valor limpio con `object.__setattr__`. |
| 28-29 | `__str__`: permite imprimir el título directamente. |

**Por qué `object.__setattr__`:** en un dataclass `frozen=True`, Python bloquea `self.valor = ...`. `object.__setattr__` es la forma controlada de modificar el valor **dentro de la inicialización**, antes de que el objeto quede congelado.

**Qué consigue `" ".join(texto.split())`:** convierte saltos de línea y tabulaciones en espacios y colapsa espacios repetidos. `"  escribir   el    informe "` se convierte en `"escribir el informe"`.

**Este Value Object se reutiliza en los tres dominios:** tareas, deadlines y notas importan `Titulo` desde aquí. Una sola regla para todos.

---

### 8.6 `src/shared/application/events.py` — nombres de eventos

**Propósito:** evitar "strings mágicos" repartidos por el código.

| Líneas | Explicación |
|---|---|
| 3 | `TAREAS_CAMBIADAS = "tareas.cambiadas"`. |
| 4 | `DEADLINES_CAMBIADOS = "deadlines.cambiados"`. |
| 5 | `NOTAS_CAMBIADAS = "notas.cambiadas"`. |
| 6 | `DATOS_CAMBIADOS = "datos.cambiados"`: evento genérico que indica "algo cambió". |
| 8 | `SYNC_CAMBIADO = "sync.cambiado"`: cambió el estado de sincronización (pendientes, última pasada). |
| 10-16 | `TODOS_LOS_TEMAS`: tupla con los cinco. `AppShell` la recorre para suscribirse a todo. |

**Por qué importa:** si escribes `"tareas.cambiada"` (sin la `s`) en la vista, el evento nunca llegará. Al usar constantes, un error de escritura se detecta al importar y el editor puede autocompletar.

---

### 8.7 `src/shared/application/event_bus.py` — el pub/sub interno

**Propósito:** que los casos de uso avisen a la UI sin conocerla.

| Líneas | Explicación |
|---|---|
| 1 | Docstring: bus síncrono e in-process. |
| 5-8 | Importa `logging`, `defaultdict`, `RLock` y tipos. |
| 10 | Logger del módulo. |
| 12 | `Callback = Callable[[Any], None]`: un suscriptor es una función que recibe un payload y no devuelve nada. |
| 15-16 | `class EventBus`. |
| 18-20 | `__init__`: `_suscriptores` es un diccionario tema → lista de callbacks. `defaultdict(list)` crea la lista automáticamente al suscribirse. `_lock` protege el acceso desde varios hilos. |
| 22-25 | `suscribir`: añade el callback solo si no estaba ya (evita duplicados). |
| 27-30 | `desuscribir`: lo quita si existe. |
| 32-40 | `publicar`: copia la lista bajo el candado, suelta el candado y ejecuta cada callback. Si uno lanza una excepción, se registra y se continúa con los demás. |

**Detalle importante — copiar la lista:** si un callback se desuscribe mientras se está publicando, modificar la lista original durante la iteración daría un error. Por eso se copia con `list(...)` antes de recorrer.

**Detalle importante — ejecutar fuera del candado:** si un callback intentara suscribirse o publicar otro evento, con un `Lock` normal se bloquearía a sí mismo. Además, `RLock` permite reentrar, pero ejecutar callbacks fuera del candado evita retenerlo durante trabajo de UI.

**Es síncrono:** `publicar` no crea hilos ni colas. El callback termina antes de que `publicar` devuelva. Para esta app es suficiente y hace el comportamiento predecible.

**Un listener roto no tumba la app:** el `try/except Exception` con `logger.exception` garantiza que un error de refresco en una vista no impida que las demás se enteren.

---

### 8.8 `src/shared/infrastructure/database.py` — SQLite local

**Propósito:** abrir una sola conexión SQLite, crear el esquema y ofrecer métodos seguros para ejecutar consultas.

#### Constante `SCHEMA` (líneas 11-61)

| Líneas | Explicación |
|---|---|
| 12 | `PRAGMA journal_mode = WAL`: modo write-ahead log. |
| 13 | `PRAGMA foreign_keys = ON`: activa las claves foráneas. En SQLite hay que activarlo en **cada** conexión. |
| 15-26 | Tabla `deadlines`: id, título, descripción, fecha límite, área, completado, deleted, synced, created_at, updated_at. |
| 28-39 | Tabla `tareas`: añade `prioridad` y `deadline_id` con `REFERENCES deadlines(id) ON DELETE SET NULL`. |
| 41-51 | Tabla `notas`: contenido y `deadline_id`. |
| 53-58 | Índices para acelerar búsquedas por deadline, por `synced` y por `completada`. |
| 60 | `PRAGMA user_version = 1`: versión del esquema, útil para futuras migraciones. |

**Sobre `ON DELETE SET NULL`:** si algún día se borrara físicamente un deadline, SQLite pondría `NULL` en sus tareas. En esta app el borrado es lógico (`deleted=1`), así que ese `ON DELETE` casi nunca se dispara; por eso `DeadlineService.eliminar` desvincula las tareas manualmente.

#### `default_db_path()` (líneas 64-82)

| Líneas | Explicación |
|---|---|
| 67-71 | Docstring con el orden de prioridad. |
| 72-74 | Si `CAOS_DB_PATH` existe, se expande `~` y se devuelve. |
| 76-78 | Si `FLET_APP_STORAGE_DATA` existe, se usa esa carpeta + `caos_local.db`. |
| 80-82 | En escritorio, crea `~/.caos` y devuelve la ruta. |

`Path(...).expanduser()` convierte `~` en la carpeta del usuario. `mkdir(parents=True, exist_ok=True)` crea la carpeta si no existe y no falla si ya está.

#### Clase `Database` (líneas 85-156)

| Líneas | Explicación |
|---|---|
| 85-86 | Docstring: envoltorio fino y thread-safe. |
| 88-91 | `__init__`: guarda la ruta, deja la conexión en `None` (se abre de forma perezosa) y crea un `RLock`. |
| 94-100 | `initialize`: crea la carpeta padre, ejecuta `SCHEMA` completo con `executescript` y hace commit. |
| 102-112 | `_conexion`: si no hay conexión, la crea con `check_same_thread=False` (porque Flet puede llamar desde hilos distintos), `timeout=30`, `row_factory=sqlite3.Row` (permite `row["columna"]`) y los PRAGMA de claves foráneas y `busy_timeout`. |
| 115-120 | `execute`: ejecuta una sentencia con parámetros, hace commit y devuelve `lastrowid`. |
| 122-126 | `executemany`: varias filas para la misma sentencia; hace commit una vez. |
| 128-131 | `query`: devuelve todas las filas como lista. |
| 133-136 | `query_one`: devuelve la primera fila o `None`. |
| 138-143 | `tabla_existe`: consulta `sqlite_master`. Se usa en las pruebas. |
| 145-149 | `close`: cierra y deja `_conn = None`. |
| 151-156 | `__enter__`/`__exit__`: permite `with Database(ruta) as db:`. |

**Por qué `check_same_thread=False`:** por defecto SQLite prohíbe usar una conexión desde un hilo distinto al que la creó. Flet puede ejecutar callbacks en otros hilos, así que se desactiva esa protección y se compensa con `RLock`.

**Por qué se hace commit en cada `execute`:** simplicidad y durabilidad. Cada operación de la app es pequeña; no se necesita agrupar transacciones complejas.

**Qué es `busy_timeout`:** si otro proceso tiene la base bloqueada, SQLite espera hasta 5 segundos antes de dar error, en vez de fallar inmediatamente.
---

### 8.9 `src/shared/infrastructure/turso_client.py` — hablar con la nube

**Propósito:** enviar sentencias SQL a Turso mediante su API HTTP `/v2/pipeline`, sin depender de un driver especial.

#### `_normalizar_url()` (líneas 14-20)

| Líneas | Explicación |
|---|---|
| 15 | Quita espacios y la barra final. |
| 16-17 | Si empieza por `libsql://`, lo cambia por `https://`. |
| 18-19 | Si no empieza por `http://` ni `https://`, añade `https://`. |
| 20 | Devuelve la URL normalizada. |

Ejemplos:

- `libsql://caos.turso.io/` → `https://caos.turso.io`
- `caos.turso.io` → `https://caos.turso.io`
- `https://caos.turso.io` → sin cambios

#### `_parametro()` (líneas 23-38)

Convierte un valor de Python al formato tipado que exige Turso:

| Líneas | Tipo | Resultado |
|---|---|---|
| 25-26 | `None` | `{"type": "null"}` |
| 27-28 | `bool` | entero `"1"` o `"0"` |
| 29-30 | `int` | `{"type": "integer", "value": "..."}` |
| 31-32 | `float` | `{"type": "float", "value": "..."}` |
| 33-37 | `bytes` | `{"type": "blob", "base64": "..."}` |
| 38 | todo lo demás | `{"type": "text", "value": str(valor)}` |

**Trampa clásica:** en Python `bool` es subclase de `int`. Por eso la comprobación de `bool` va **antes** que la de `int`; si no, `True` se enviaría como `"True"` en vez de `"1"`.

**Fechas:** este cliente no convierte `datetime` ni `date`. El `SyncService` ya las envía como texto ISO (`isoformat()`). Si añades un campo de fecha nuevo, conviértelo antes de llegar aquí.

#### `_valor()` (líneas 41-53)

Hace lo contrario que `_parametro`: traduce las celdas **que devuelve** Turso a tipos de Python. Es lo que permite leer filas para el *pull*.

| Líneas | Tipo recibido | Resultado Python |
|---|---|---|
| 42-43 | cualquier cosa que no sea diccionario | se devuelve tal cual |
| 44-45 | `null` | `None` |
| 46-47 | `integer` | `int` |
| 48-49 | `float` | `float` |
| 50-51 | `blob` | `bytes` (base64 decodificado) |
| 52-53 | `text` | `str` |

Sin esta función, `completada` llegaría como `"0"` (texto) y `bool("0")` sería `True`. Ese es el tipo de error silencioso que conviene evitar.

#### Clase `TursoClient` (líneas 57-169)

| Líneas | Explicación |
|---|---|
| 57-58 | Docstring: usa `/v2/pipeline`. |
| 60-71 | `__init__`: acepta URL y token; si no se los pasan, lee `TURSO_DATABASE_URL` y `TURSO_AUTH_TOKEN`. Normaliza la URL, guarda timeout (15 s) y crea o recibe una `requests.Session`. |
| 73-76 | `actualizar_credenciales`: cambia URL y token en caliente, sin reiniciar. |
| 78-80 | `configurado`: `True` solo si hay URL **y** token. |
| 82-84 | `execute_many`: envía sentencias y descarta las filas. Se mantiene por comodidad para escrituras y `ping()`. |
| 86-158 | `ejecutar`: envía el pipeline y devuelve **una lista de filas por sentencia**. Es la base del *pull*. |
| 95-98 | Si no está configurado, lanza `TursoNoConfigurado`. |
| 100-110 | Construye `requests`: por cada sentencia crea `{"type": "execute", "stmt": {"sql": ..., "args": [...]}}` y añade `{"type": "close"}`. |
| 112-123 | Hace `POST` a `{url}/v2/pipeline` con JSON y cabecera `Authorization: Bearer <token>`. Si falla la red, lanza `ErrorDeSincronizacion`. |
| 125-128 | Si el HTTP es 400 o más, lanza error con el código y los primeros 300 caracteres. |
| 130-133 | Intenta parsear el JSON; si no es válido, lanza error. |
| 135-139 | Recorre `results` y, si alguno tiene `type == "error"`, lanza `ErrorDeSincronizacion`. |
| 141-144 | Ignora el `close` del pipeline: no aporta filas. |
| 146-156 | Lee `cols` y `rows`, decodifica cada celda con `_valor` y arma diccionarios `columna -> valor`. |
| 160-165 | `consultar`: atajo para un único `SELECT`; devuelve solo sus filas. |
| 167-169 | `ping()`: ejecuta `SELECT 1` para comprobar credenciales. |

**Por qué se inyecta `session`:** en las pruebas se pasa una sesión falsa (`tests/test_infrastructure.py:45-54`) y así no se hace red real. Es un ejemplo de **inyección de dependencias**.

**Por qué se revisan los `results`:** que el HTTP sea 200 no garantiza que la sentencia se haya ejecutado. Turso puede devolver un error SQL dentro de un resultado. Este chequeo evita marcar `synced=1` cuando en realidad la fila no se guardó.

**Por qué `ejecutar` devuelve una lista por sentencia:** el *pull* necesita saber qué filas corresponden a `deadlines`, cuáles a `tareas` y cuáles a `notas`. Mantener la alineación por posición evita mezclar resultados.

---

### 8.10 `src/shared/infrastructure/settings_repository.py` — credenciales guardadas en el teléfono

**Propósito:** guardar ajustes pequeños (por ahora, la URL y el token de Turso) dentro de la base SQLite local. Así puedes configurar la sincronización desde el propio Android, donde no existen las variables de entorno.

#### Claves (líneas 14-15)

| Líneas | Explicación |
|---|---|
| 14 | `CLAVE_TURSO_URL = "turso_url"`: nombre con el que se guarda la URL. |
| 15 | `CLAVE_TURSO_TOKEN = "turso_token"`: nombre con el que se guarda el token. |

#### Clase `SettingsRepository` (líneas 18-62)

| Líneas | Explicación |
|---|---|
| 21-22 | `__init__`: recibe la `Database` y la guarda. No abre conexiones propias. |
| 25-32 | `get`: busca una clave en la tabla `settings`; si no existe, devuelve el valor por defecto. |
| 34-41 | `set`: inserta o actualiza (`ON CONFLICT ... DO UPDATE`). Es un *upsert*. |
| 43-44 | `eliminar`: borra una clave. |
| 47-55 | `turso_credenciales`: devuelve `(url, token)`. Primero busca lo guardado; si falta, cae a `TURSO_DATABASE_URL` y `TURSO_AUTH_TOKEN`. |
| 57-59 | `guardar_turso`: guarda ambas credenciales. |
| 61-62 | `borrar_turso`: elimina ambas. |

**Por qué existe este archivo:** en Android no hay una consola para definir variables de entorno. La tabla `settings` vive en el mismo `caos_local.db` privado de la app y sobrevive a reinicios.

**Seguridad:** el token se guarda en texto plano dentro de la base local privada. Para un uso personal es aceptable; si el teléfono se comparte, borra las credenciales al terminar.

**Dónde se crea la tabla:** `database.py:53-56`, dentro de `SCHEMA`. Al arrancar, `initialize()` ejecuta el esquema completo y crea la tabla si no existe.

**Cómo se conecta todo:** `app_context.py:50-51` crea el repositorio y lee las credenciales; `app_context.py:57-63` las pasa a `TursoClient` y a `SyncService`. El diálogo de sincronización (`shell.py:216-456`) permite escribir, probar y guardar los valores en caliente, sin reiniciar la app.

---

### 8.11 `src/shared/application/sync_service.py` — subir y bajar cambios

**Propósito:** decidir qué registros están pendientes, subirlos, bajar los cambios hechos en otros dispositivos y resolver conflictos. La sincronización es **bidireccional** y puede lanzarse de dos formas: con el icono de nube (manual) o con el sincronizador automático (`auto_sync.py`, sección 8.11.1).

#### Esquema remoto (líneas 22-68)

| Líneas | Explicación |
|---|---|
| 22-64 | `TURSO_SCHEMA_SENTENCIAS`: tres `CREATE TABLE IF NOT EXISTS`, uno por tabla. |
| 67-68 | `_sentencias_esquema()`: convierte cada SQL en una tupla `(sql.strip(), ())`. |

Diferencias con el esquema local:

- En Turso **no** se declaran claves foráneas. Así el orden de subida es una precaución lógica, no una restricción que pueda rechazar filas.
- Los índices no se crean en remoto; para esta versión no son necesarios.
- `IF NOT EXISTS` hace que se pueda sincronizar contra una base vacía: la primera vez crea las tablas.
- El esquema se envía **siempre**, incluso cuando no hay nada pendiente. Gracias a eso un teléfono recién instalado puede crear las tablas y bajar los datos.

#### Lecturas del pull (líneas 71-89)

| Constante | Líneas | Qué trae |
|---|---|---|
| `SELECT_DEADLINES` | 73-77 | Todas las columnas de `deadlines`, incluidas `deleted` y `synced`. |
| `SELECT_TAREAS` | 79-83 | Ídem para `tareas`, con `prioridad`, `completada` y `deadline_id`. |
| `SELECT_NOTAS` | 85-89 | Ídem para `notas`, con `contenido`. |

**Por qué se incluyen `deleted` y `synced`:** el *pull* necesita saber si un registro se borró en otro dispositivo y debe dejar la fila local como sincronizada para no volver a subirla.

#### Upserts remotos (líneas 92-140)

| Constante | Líneas | Detalle |
|---|---|---|
| `UPSERT_DEADLINE` | 92-107 | Inserta 10 columnas; `synced` va fijo a `1`; en conflicto actualiza todo menos `created_at`, solo si la versión entrante es más nueva. |
| `UPSERT_TAREA` | 109-124 | Igual, con `prioridad`, `completada` y `deadline_id`. |
| `UPSERT_NOTA` | 126-140 | Igual, con `contenido`. |

**Por qué `synced = 1` directamente en el SQL remoto:** la columna existe en el esquema remoto por compatibilidad, pero para la nube todos los registros que llegan están, por definición, sincronizados. El valor `0/1` que importa para la app es el **local**.

**Por qué no se actualiza `created_at` en el conflicto:** la fecha de creación original no debe cambiar cuando editas un registro. Solo se actualiza `updated_at`.

**Por qué termina en `WHERE excluded.updated_at > ...`:** es la regla *last-write-wins*. Si otro dispositivo guardó una versión más nueva en la nube, el `UPSERT` local **no la pisa**. Después, el *pull* bajará esa versión más nueva. Así dos dispositivos no se sobrescriben a ciegas.

#### `ResultadoSync` (líneas 143-152)

| Líneas | Explicación |
|---|---|
| 143-144 | `@dataclass(frozen=True) class ResultadoSync`: resultado inmutable. |
| 145 | `enviados: int = 0`. |
| 146 | `recibidos: int = 0`: filas de la nube que cambiaron algo en local. |
| 147 | `detalle: dict[str, int]` con los enviados por dominio. |
| 148 | `detalle_recibidos: dict[str, int]` con los recibidos por dominio. |
| 150-152 | `hubo_cambios`: `True` si se envió **o** se recibió algo. |

#### Clase `SyncService` (líneas 155-330)

| Líneas | Explicación |
|---|---|
| 163-170 | `__init__`: guarda el cliente, los tres repositorios, el `EventBus` opcional y crea un `Lock`. No conoce SQLite directamente: usa los puertos. |
| 172-174 | `configurado`: delega en el cliente. |
| 176-178 | `actualizar_credenciales`: aplica URL y token nuevos sin reiniciar la app. |
| 180-182 | `probar_conexion`: crea un `TursoClient` temporal y ejecuta `ping()`; no guarda nada. |
| 184-189 | `pendientes()`: cuenta `list_pending()` de cada repositorio. |
| 191-192 | `total_pendientes()`: suma los tres valores. |
| 194-201 | `sincronizar()`: entrada del botón manual. Adquiere el candado y espera si la sincronización automática está en curso. |
| 203-225 | `sincronizar_si_libre()`: entrada de la automática. Intenta el candado sin bloquear; si está ocupado devuelve `None` y no encola otra pasada. Con `timeout` espera hasta esos segundos, que es lo que usa la pasada final al cerrar. |
| 227-232 | `_sincronizar()`: si no hay credenciales, lanza `TursoNoConfigurado`. |
| 234-236 | Lee las listas de pendientes (incluye registros con `deleted=1`). |
| 238 | Empieza la lista de sentencias con el esquema. |
| 240-257 | Añade primero los deadlines. El comentario recuerda que así se respeta la FK lógica. |
| 258-274 | Después las tareas. |
| 275-290 | Al final las notas. |
| 292-297 | Añade las tres lecturas del *pull* al final del mismo pipeline. |
| 299 | Ejecuta **todo** en una sola petición HTTP: esquema, subida y lecturas. Si algo falla, la excepción sube. |
| 301-304 | Solo tras el éxito marca `synced=1` en local para cada dominio. |
| 306-311 | Separa las tres últimas respuestas (los `SELECT`) y aplica cada fila con `upsert_remoto`. |
| 313-320 | Suma enviados y recibidos y construye el `ResultadoSync`. |
| 322-323 | Si `publicar_eventos` es `True` y hay bus, llama a `publicar_resultado`. |
| 325-330 | Registra en el log y devuelve el resultado. |
| 333-339 | `_aplicar`: recorre las filas y cuenta cuántas cambiaron algo de verdad. |

**La propiedad más importante:** el orden de las líneas 290-295. Si la red falla, la excepción sube y **nunca** se ejecuta `mark_synced`. Eso significa que los registros siguen pendientes y se reintentarán en la próxima sincronización. La prueba `test_error_de_red_no_marca_synced` lo verifica.

**Por qué hay un `Lock`:** la sincronización manual y la automática pueden coincidir. El candado garantiza que solo una habla con Turso a la vez, sin bloquear el hilo de la UI: la automática espera en un hilo aparte (`asyncio.to_thread`) y la manual espera dentro de `sincronizar()`.

**Por qué `publicar_eventos` es un parámetro:** la automática llama con `publicar_eventos=False` y publica ella misma al final, ya en el hilo del bucle de Flet. Así los callbacks de la UI se ejecutan en el hilo correcto y no desde el hilo de trabajo.

**Qué pasa con los borrados:** como `list_pending()` no filtra por `deleted`, un registro borrado lógicamente sigue pendiente hasta que se sube con `deleted=1`. En el *pull*, un `deleted=1` remoto se aplica en local y el registro desaparece de las vistas.

**Cómo se resuelve un conflicto:** gana el `updated_at` más reciente (UTC). Se aplica en los dos sentidos:

1. Al **subir**, el `WHERE` del `UPSERT` impide pisar una fila remota más nueva.
2. Al **bajar**, `upsert_remoto` compara el `updated_at` local y solo escribe si la fila remota es más nueva.

#### `publicar_resultado` (líneas 333-350)

| Líneas | Explicación |
|---|---|
| 333-340 | Docstring: explica qué eventos se publican y por qué. |
| 341-348 | Si llegaron filas de la nube (`recibidos`), publica los cuatro temas de dominio para refrescar listas y progreso. |
| 349-350 | Si hubo cualquier cambio, publica `SYNC_CAMBIADO` para actualizar el contador de pendientes. |

**Por qué no se publican los temas de dominio al subir:** una subida normal no cambia los datos locales. Refrescar las listas en ese momento haría perder el scroll sin motivo. Solo se refrescan cuando el *pull* trae algo.

**Qué ve el usuario:** el diálogo manual muestra cuántos registros se enviaron y cuántos se recibieron. Si no hubo nada en ningún sentido, dice "Todo estaba al día". La automática trabaja en silencio: solo registra en el log y avisa a la UI cuando hay cambios.

#### 8.11.1 `src/shared/application/auto_sync.py` — el sincronizador automático

**Propósito:** sincronizar sin que el usuario pulse nada. Combina tres disparadores: un bucle periódico, los cambios locales (con *debounce*) y el paso a segundo plano/cierre. No hay servicio Android en segundo plano: si Android mata la app sin avisar, el trabajo pendiente se sube en el siguiente arranque.

| Líneas | Explicación |
|---|---|
| 1-6 | Docstring: bucle periódico, cambios locales con debounce y pasada final al cerrar. |
| 10-23 | Imports: `asyncio`, `logging`, `flet`, el bus, `DATOS_CAMBIADOS`, `SyncService`/`publicar_resultado`, `CaosError` y `hay_internet`. |
| 29-32 | Constantes: intervalo 120 s, espera inicial 1 s, debounce 2 s y espera máxima del candado 10 s. |
| 34-41 | `_PLATAFORMAS_ESCRITORIO`: Windows, Linux y macOS; en el resto no se intercepta el cierre. |
| 46-70 | `__init__`: guarda servicio, bus, sonda y tiempos; `_intervalo` nunca baja de 30 s (`max(30.0, ...)`) para no gastar batería. |
| 73-85 | `iniciar(page)`: evita arrancar dos veces, se suscribe a `DATOS_CAMBIADOS`, registra el ciclo de vida, configura el cierre de escritorio y lanza `_bucle` con `page.run_task`. |
| 87-96 | `detener()`: se desuscribe del bus, cancela el bucle y las tareas de debounce/final, y suelta la página. |
| 98-101 | `_bucle()`: espera 1 segundo, sincroniza y duerme el intervalo, en bucle infinito. |
| 104-106 | `sincronizar_ahora()`: pasada normal del bucle, sin esperar el candado. |
| 108-149 | `_pasada()`: comprueba configuración y red, ejecuta `sincronizar_si_libre` en un hilo y publica los eventos si hubo cambios. `timeout` solo se usa en la pasada final. |
| 151-158 | `solicitar()`: pide una pasada inmediata con `page.run_task` sin bloquear la UI. Se usa al guardar credenciales y al reanudar. |
| 161-175 | `_on_datos_cambiados()`: cada cambio local incrementa una generación, cancela el debounce anterior y programa uno nuevo. |
| 177-197 | `_sincronizar_tras_debounce()`: espera 2 s, comprueba que siga siendo la generación válida, cuenta pendientes y sincroniza solo si hay algo que subir; espera el candado por si el bucle está ocupado. |
| 200-207 | `_programar_final()`: al ocultarse o cerrarse la app programa `_sincronizar_final` una sola vez. |
| 209-224 | `_sincronizar_final()`: si hay pendientes, llama a `_pasada` con `timeout=10` para esperar a que termine una sincronización en curso. |
| 227-235 | `_on_lifecycle()`: `RESUME`/`SHOW` piden una pasada; `HIDE`/`PAUSE`/`DETACH` programan la final. |
| 238-251 | `_configurar_cierre()`: en escritorio activa `prevent_close`, registra `on_event` y actualiza la página. |
| 253-258 | `_es_escritorio()`: comprueba plataforma, `web` y `embedded` para no tocar ventanas que no son propias. |
| 260-270 | `_on_window_event()`: al recibir `WindowEventType.CLOSE` programa `_cerrar` una sola vez. |
| 272-290 | `_cerrar()`: espera la pasada final (o la lanza si no existe) y destruye la ventana con `page.window.destroy()`. |

**Por qué la espera inicial es 1 s:** la ventana ya está montada cuando `main.py` llama a `iniciar`, así que basta un segundo para que la base local termine de abrirse. Antes eran 6 s y un cierre rápido podía dejar el cambio sin subir.

**Por qué hay *debounce* de 2 s:** cada pulsación o guardado publica `DATOS_CAMBIADOS`; sin debounce se lanzaría una petición por cada tecla. Con 2 s se agrupan los cambios seguidos y se sube una sola vez. Si llega otro cambio antes de que termine la espera, se cancela la tarea anterior y empieza otra.

**Por qué la pasada final solo mira pendientes:** cerrar la app no necesita bajar cambios de la nube; solo asegurar que lo local llegue a Turso. Si no hay pendientes, la ventana se cierra sin hacer red.

**Por qué `timeout` en el candado:** si el debounce está subiendo justo cuando pulsas la X, la pasada final espera hasta 10 s a que termine en vez de rendirse y perder el cambio. Pasado ese tiempo, el registro sigue pendiente y se reintenta en el siguiente arranque.

**Por qué se comprueba Internet antes de Turso:** si el teléfono está en modo avión, la sonda falla en milisegundos y se evita una petición HTTP que tardaría más en fallar. La sonda abre un TCP a `1.1.1.1:443` o `8.8.8.8:443`; si hay red pero Turso no responde, la sincronización falla y se reintenta en la siguiente vuelta.

**Por qué `asyncio.to_thread`:** `SyncService` y la sonda usan `requests`/`socket`, que son bloqueantes. Ejecutarlos en un hilo aparte mantiene la interfaz fluida. El resultado se publica después, de vuelta en el hilo del bucle de Flet.

**Límite importante:** en escritorio el cierre puede tardar unos segundos si hay pendientes y la red va lenta; es el precio de no perder datos. En móvil, Android puede pausar la app al pasar a segundo plano: `PAUSE` lanza la pasada final y `RESUME` fuerza otra al volver.

#### 8.11.2 `src/shared/infrastructure/connectivity.py` — ¿hay Internet?

**Propósito:** evitar intentos de red cuando el dispositivo está claramente desconectado.

| Líneas | Explicación |
|---|---|
| 1-8 | Docstring: es una sonda ligera, no sustituye a una petición real. |
| 10-12 | Importa `socket`. |
| 14-18 | `DESTINOS`: dos direcciones públicas con HTTPS (`1.1.1.1:443`, `8.8.8.8:443`). Basta con que una acepte la conexión. |
| 21-29 | `hay_internet(timeout=2.0)`: prueba cada destino con `socket.create_connection`; devuelve `True` al primero que responda y `False` si todos fallan con `OSError`. |

**Por qué dos destinos:** un solo servidor puede estar bloqueado en una red corporativa o de un país. Probar dos reduce los falsos negativos.

**Por qué no se usa `requests`:** abrir un TCP es más rápido y no descarga nada. La comprobación real la hace Turso cuando se ejecuta el pipeline.

**Cómo se prueba:** `tests/test_connectivity.py` sustituye `socket.create_connection` por dobles, así que las pruebas no tocan la red.


---

### 8.12 `src/shared/presentation/theme.py` — colores y ventana

**Propósito:** centralizar la identidad visual.

| Líneas | Explicación |
|---|---|
| 8-17 | Paleta: fondo casi negro, superficies gris azulado, acento violeta, acento secundario verde, texto claro, texto suave, peligro rojo, éxito verde. |
| 20-21 | `configurar_pagina(page)`: firma y docstring. |
| 22 | Título de la ventana: `"CAOS 3.0"`. |
| 23 | `page.theme_mode = ft.ThemeMode.DARK`. |
| 24-26 | Fondo, padding y spacing a cero (la app controla sus márgenes). |
| 27 | `ft.Theme(color_scheme_seed=ft.Colors.INDIGO)`: tema base de Flet con semilla índigo. |
| 31-35 | Tamaño de ventana de escritorio: 460×620, mínimo 340×520, no maximizada. |
| 36 | Fondo de la ventana. |

**Por qué 460×620:** la app está diseñada como una columna compacta, similar a un móvil, para que se vea bien tanto en escritorio como en Android. En móvil, Flet ignora los tamaños de ventana.

**Separación de responsabilidades:** los widgets no escriben colores literales; importan estas constantes. Si cambias `COLOR_ACENTO`, cambia toda la app.

---

### 8.13 `src/shared/presentation/widgets.py` — piezas visuales reutilizables

**Propósito:** evitar repetir el mismo `Container` con bordes, colores y padding en las tres vistas.

| Líneas | Explicación |
|---|---|
| 20-33 | `MESES`: nombres en español, índice 0 = enero. |
| 34-42 | `DIAS`: lunes = índice 0, que coincide con `date.weekday()`. |
| 44-49 | `COLORES_PRIORIDAD`: un color por cada valor de `Prioridad`. |
| 52-54 | `fecha_larga()`: "jueves, 5 de noviembre". Usa `weekday()` y `month - 1` porque las listas empiezan en 0. |
| 57-58 | `fecha_corta()`: formato `DD/MM/AAAA` con ceros a la izquierda (`:02d`). |
| 61-70 | `hace_cuanto()`: calcula la diferencia entre ahora y un momento. Devuelve "ahora", "hace N min", "hace N h" o "hace N d". |
| 73-80 | `avisar()`: muestra un `SnackBar`; rojo si `error=True`, gris si no; dura 2600 ms. |
| 83-98 | `encabezado()`: fila con título/subtítulo a la izquierda y acciones a la derecha. `SPACE_BETWEEN` empuja los extremos. |
| 101-114 | `pill_prioridad()`: etiqueta compacta `P1`–`P4` con color y tooltip explicativo. |
| 117-127 | `chip()`: etiqueta con icono opcional, fondo translúcido y texto del color indicado. |
| 130-148 | `estado_vacio()`: icono grande, título y subtítulo centrados, con padding vertical 44. |
| 151-158 | `tarjeta()`: contenedor con fondo, radio 16, borde sutil y padding configurable (14 por defecto). |
| 161-194 | `campo_texto()`: `TextField` con label, valor, hint, multilínea, estilos de foco y colores del tema. |
| 197-221 | `selector()`: `Dropdown` con las mismas convenciones visuales. |

**Detalle de `hace_cuanto` (línea 62):** `datetime.now(momento.tzinfo)` crea un "ahora" con la **misma zona horaria** que el momento recibido. Si hicieras `datetime.now()` sin argumento y el momento tiene `tzinfo`, Python lanzaría `TypeError: can't subtract offset-naive and offset-aware datetimes`.

**Detalle de `campo_texto` (líneas 180-189):** `border` es un diccionario por estado. `DEFAULT` tiene borde transparente; `FOCUSED` lo pinta con el color de acento. Es la forma de hacer un foco visual sin cambiar el tamaño del control.

**Detalle de `multilinea` (líneas 175-177):** si `multilinea=True`, `min_lines` es el número pedido y `max_lines` al menos 4; si no, ambos son 1. Así una descripción puede crecer sin romper el layout.

**Por qué `ft.Padding.symmetric(...)` y `ft.Alignment.CENTER`:** en Flet 1.x estas son las clases correctas. Usar la API antigua (`padding=10`) puede fallar o ignorarse.

---

### 8.14 `src/shared/presentation/effects.py` — la recompensa

**Propósito:** sonido + animación al completar una tarea, sin que un fallo de audio rompa la operación.

| Líneas | Explicación |
|---|---|
| 1 | Docstring: estímulos dopaminérgicos (RF05). |
| 5-8 | Importa `asyncio`, `logging`, `os` y `threading`. |
| 16 | `RUTA_SONIDO = "sounds/success.wav"`: ruta relativa dentro de `assets/`. |
| 19-24 | Docstring de la clase: tolerante a fallos. |
| 26-28 | `__init__`: guarda la página y deja `_audio = None`. |
| 29-34 | Intenta importar `flet_audio.Audio`, lo crea con volumen 0.65 y lo añade a `page.services`. |
| 35-38 | Si falla (plataforma sin audio, paquete ausente), registra un warning y sigue. |
| 41-43 | `celebrar()`: reproduce el sonido primero. |
| 45-46 | Si no se pasó tarjeta, termina (solo sonido). |
| 48 | Guarda el color de fondo original para restaurarlo. |
| 50-54 | Activa animaciones, escala a 1.025, pone fondo verde suave y actualiza. |
| 56 | Espera 0,22 s sin bloquear la UI (es `async`). |
| 58-61 | Vuelve a escala 1 y al color original, actualiza y espera 0,08 s. |
| 62-63 | Si algo falla, lo registra en debug; la app sigue. |
| 66-73 | `_reproducir_sonido()`: si hay audio, lo reproduce con `page.run_task`; si falla, cae al pitido. |
| 75-91 | `_pitido()`: crea un hilo daemon que, en Windows, hace dos `winsound.Beep` (880 Hz y 1320 Hz); en otros sistemas imprime el carácter de campana `\a`. |

**Por qué `page.services.append(self._audio)`:** en Flet 1.x los servicios (audio, etc.) se registran en la vista raíz, no se añaden como controles visuales.

**Por qué el pitido va en un hilo:** `winsound.Beep` bloquea durante ~180 ms. Si se ejecutara en el hilo de la UI, la animación se congelaría. Un hilo `daemon` no impide cerrar la app.

**Por qué `try/except` en la animación:** el feedback es un extra. La tarea ya se guardó antes de animar; si la animación falla, el usuario no pierde datos.

---

### 8.15 `src/shared/presentation/app_context.py` — el composition root

**Propósito:** construir todas las dependencias en un solo lugar y pasarlas a las vistas.

| Líneas | Explicación |
|---|---|
| 28-29 | `@dataclass class AppContext`: agrupa las dependencias compartidas. |
| 32 | `page`: la página de Flet. |
| 33 | `db`: la base SQLite. |
| 34 | `bus`: el event bus. |
| 35 | `settings`: repositorio de credenciales y ajustes. |
| 36-38 | Los tres repositorios concretos. |
| 39-41 | Los tres servicios de casos de uso. |
| 42 | `sync`: el servicio de sincronización. |
| 43 | `auto_sync`: el bucle de sincronización automática. |
| 44 | `effects`: sonido y animación. |
| 46-47 | `crear(...)`: método de clase que devuelve un `AppContext` ya armado. |
| 48 | Crea **un** bus compartido por todos. |
| 50-55 | Crea `SettingsRepository`, lee las credenciales y construye los tres repositorios sobre la misma `Database`. |
| 57-63 | Crea el `SyncService` con el cliente Turso, los tres repos y el bus. |
| 65-79 | Devuelve el contexto: `DeadlineService` recibe deadlines + tareas (porque calcula progreso y desvincula), `TareaService` y `NotaService` reciben su repo y el bus, `AutoSync` recibe el mismo `SyncService` y el mismo bus, `Effects` recibe la página. |

**Por qué existe este archivo:** sin él, cada vista tendría que construir sus propios repositorios y servicios, y dejarían de compartir el bus y la base. Aquí se decide una sola vez qué implementación concreta se usa. Si mañana quisieras una base en memoria para una demo, cambiarías solo este punto.

**Inyección de dependencias manual:** no hay framework (como `dependency-injector`). Se pasan los objetos por constructor. Para este tamaño es más claro y no añade magia.

---

### 8.16 `src/shared/presentation/shell.py` — el marco de la app

**Propósito:** contener las tres vistas, la cabecera, la barra de progreso, la navegación inferior y el diálogo de sincronización.

| Líneas | Explicación |
|---|---|
| 25-26 | `class AppShell(ft.Column)`: el shell es una columna. |
| 28-29 | `__init__`: `expand=True` para ocupar toda la ventana; `spacing=0`. |
| 30-31 | Guarda el contexto y el índice de sección actual. |
| 33 | Crea **una vez** las tres vistas. No se recrean al navegar; solo se cambia cuál se muestra. |
| 35-41 | Barra de progreso (altura 8, verde). |
| 42 | Texto del porcentaje (`"0%"`). |
| 43 | Texto de detalle ("X completadas · Y pendientes"). |
| 44-49 | Botón de nube que abre el diálogo de sync. |
| 51-55 | `_contenido`: contenedor que muestra la vista activa, con padding horizontal 18 y vertical 10. |
| 57-80 | `NavigationBar` con tres destinos: Tareas, Proyectos, Notas. `on_change` apunta a `_cambiar_seccion`. |
| 82-87 | `self.controls`: cabecera, tarjeta de progreso, contenido y navegación. |
| 89-90 | Se suscribe a **todos** los temas para mantener el progreso al día. |
| 92 | Calcula el progreso inicial. |
| 95-134 | `_cabecera()`: fila con "CAOS" + badge "3.0", fecha larga y botón de sync. |
| 136-168 | `_tarjeta_progreso()`: tarjeta con título, detalle, porcentaje y barra. |
| 171-172 | `_cambiar_seccion()`: toma el índice seleccionado y llama a `ir_a`. |
| 174-185 | `ir_a()`: limita el índice al rango válido, actualiza la barra, cambia el contenido, refresca la vista destino y actualiza la UI. |
| 187-188 | `_on_cambio()`: cuando llega cualquier evento, recalcula el progreso. |
| 190-213 | `_actualizar_progreso()`: pide `progreso_diario()` y `total_pendientes()`, actualiza barra, porcentaje, detalle y tooltip; luego actualiza cada control si la página está montada. |
| 216-335 | `_abrir_sync()`: lee configuración y pendientes, construye los textos (incluido el aviso de sincronización automática), deshabilita el botón si no hay credenciales y muestra el diálogo. |
| 337-370 | `_guardar_credenciales()`: valida, guarda en `settings`, actualiza el cliente en caliente y pide una pasada inmediata con `auto_sync.solicitar()`. |
| 372-406 | `_probar_credenciales()`: prueba la conexión sin guardar y muestra el resultado. |
| 408-456 | `_sincronizar()`: deshabilita el botón, muestra estado, llama al servicio, maneja errores, escribe el resultado, reactiva y avisa. |

**Detalle de `ir_a` (líneas 176-177):** `max(0, min(indice, len(self._vistas) - 1))` evita índices negativos o fuera de rango. Es una defensa sencilla y útil si otro código llama a `ir_a(99)`.

**Detalle de `_actualizar_progreso` (líneas 197-204):** la barra usa `progreso.porcentaje` (0.0–1.0). El tooltip del botón cambia según haya pendientes o no: "Sincronizar · 3 pendientes" vs "Sincronizar · todo al día".

**Detalle del diálogo de sync (líneas 249-256):** el `boton` se pasa por referencia a `_sincronizar`. Al deshabilitarlo dentro de esa función, el mismo objeto que está en el diálogo se actualiza. Es un patrón habitual en Flet: los controles son objetos mutables.

**Sincronización en el hilo de la UI:** el botón manual llama a `self.ctx.sync.sincronizar()` de forma síncrona; para pocos registros es aceptable y muestra el resultado en el propio diálogo. La sincronización automática, en cambio, usa `asyncio.to_thread` y `page.run_task` (`auto_sync.py:108-149`) para no congelar la ventana mientras responde la red.
---

### 8.17 Dominio `tareas`: modelos

#### 8.17.1 `src/domains/tareas/models/value_objects.py` — Prioridad Eisenhower

**Propósito:** representar las cuatro prioridades posibles y validar que solo lleguen valores 1–4.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 5 | Importa `IntEnum`. |
| 7 | Importa `ErrorDeValidacion`. |
| 8-11 | Reexporta `Titulo` y `LONGITUD_MAXIMA_TITULO` desde el kernel compartido. El `# noqa: F401` evita que un linter marque el import como "no usado". |
| 14-15 | `class Prioridad(IntEnum)`: cada valor es a la vez número y etiqueta. |
| 17 | `IMPORTANTE_URGENTE = 1`. |
| 18 | `IMPORTANTE_NO_URGENTE = 2`. |
| 19 | `NO_IMPORTANTE_URGENTE = 3`. |
| 20 | `NO_IMPORTANTE_NO_URGENTE = 4`. |
| 22-24 | `codigo`: devuelve `"P1"`, `"P2"`, etc. |
| 26-28 | `etiqueta`: texto largo ("Importante y urgente"). |
| 30-32 | `descripcion`: consejo de acción ("Hazlo ahora"). |
| 34-43 | `desde()`: si ya es `Prioridad`, la devuelve; si es número o texto, intenta `int(valor)` y construye el enum; si falla, lanza `ErrorDeValidacion` con un mensaje claro. |
| 46-51 | `_ETIQUETAS`: diccionario prioridad → texto. |
| 53-58 | `_DESCRIPCIONES`: diccionario prioridad → recomendación. |

**Por qué `IntEnum`:** permite guardar `int(tarea.prioridad)` en SQLite y ordenar por prioridad en SQL (`ORDER BY prioridad ASC`). Además, `Prioridad.desde("3")` acepta texto, lo que resulta útil cuando el valor viene de un `Dropdown` de Flet (que devuelve strings).

**Cómo se relaciona con la matriz de Eisenhower:**

| Código | Importante | Urgente | Acción |
|---|---|---|---|
| P1 | Sí | Sí | Hazlo ahora |
| P2 | Sí | No | Planifícalo |
| P3 | No | Sí | Delégalo |
| P4 | No | No | Elimínalo o hazlo después |

#### 8.17.2 `src/domains/tareas/models/tarea.py` — la entidad Tarea

**Propósito:** contener las reglas de una tarea: título válido, prioridad válida, estado completado/pendiente, vínculo opcional a un proyecto y actualización selectiva de campos.

| Líneas | Explicación |
|---|---|
| 1 | Docstring: RF01–RF04. |
| 5 | Importa `dataclass`. |
| 6 | Importa `Final`. |
| 8 | Importa `Prioridad` y `Titulo`. |
| 9 | Importa `Entity`. |
| 11 | `SIN_CAMBIO = object()`: centinela único. |
| 14-15 | `@dataclass class Tarea(Entity)`: hereda id, fechas, synced y deleted. |
| 18 | `titulo: str`. |
| 19 | `prioridad: Prioridad = Prioridad.IMPORTANTE_URGENTE`. |
| 20 | `descripcion: str = ""`. |
| 21 | `completada: bool = False`. |
| 22 | `deadline_id: str | None = None`. |
| 24-30 | `__post_init__`: valida el título (`Titulo(...).valor`), limpia la descripción, normaliza la prioridad, convierte completada a `bool` y limpia el deadline (si queda vacío, `None`). |
| 33-39 | `completar()`: si ya estaba completada, devuelve `False` (no hay transición). Si no, marca, toca la entidad y devuelve `True`. |
| 41-47 | `reabrir()`: lo contrario; también idempotente. |
| 49-55 | `alternar()`: invierte el estado y devuelve el nuevo valor. |
| 58-96 | `actualizar(...)`: recibe los cuatro campos editables con `SIN_CAMBIO` por defecto. Solo modifica los que se pasaron. Compara el valor nuevo con el actual; si es distinto, lo asigna y marca `cambios = True`. Al final, si hubo algún cambio, llama a `_touch()`. |
| 98-99 | `vincular_deadline(id)`: atajo de `actualizar(deadline_id=id)`. |
| 101-102 | `desvincular_deadline()`: atajo de `actualizar(deadline_id=None)`. |

**El patrón `SIN_CAMBIO` explicado con un ejemplo:**

```python
tarea.actualizar(titulo="Nuevo")          # cambia el título, deja lo demás igual
tarea.actualizar(deadline_id=None)        # desvincula el proyecto
```

Si el valor por defecto de `deadline_id` fuera `None`, no se podría distinguir "no quiero cambiar el proyecto" de "quiero quitarlo". `SIN_CAMBIO` es un objeto único que significa "no me han pasado este campo". Es una técnica muy común en actualizaciones parciales.

**Por qué se comprueba antes de asignar:** si llamas a `actualizar(titulo="Igual")`, no se toca `updated_at` ni se marca `synced=False`. Esto evita sincronizaciones innecesarias y se prueba en `test_tarea_model.py:85-89`.

**Por qué `Tarea` no es `frozen`:** necesita mutar su estado (`completar`, `actualizar`). El Value Object `Titulo` sí es inmutable porque representa un valor, no una entidad.

---

### 8.18 Dominio `tareas`: puertos

#### `src/domains/tareas/application/ports.py` (29 líneas)

**Propósito:** declarar el contrato que debe cumplir cualquier repositorio de tareas.

| Líneas | Explicación |
|---|---|
| 5 | Importa `Protocol` y `Sequence`. |
| 7 | Importa `Tarea`. |
| 10-11 | `class TareaRepository(Protocol)`: no se instancia; describe métodos. |
| 13 | `add(tarea)`: guardar una nueva. |
| 15 | `update(tarea)`: guardar cambios. |
| 17 | `get(id)`: obtener o `None`. |
| 19 | `list_all(incluir_completadas=True)`: listar todas, con opción de filtrar. |
| 21-23 | `list_by_deadline(deadline_id, incluir_completadas=True)`: listar las de un proyecto, o las sueltas si `deadline_id=None`. |
| 25 | `delete(id)`: eliminar (lógicamente). |
| 27 | `list_pending()`: las que tienen `synced=0`, **incluidas las borradas**. |
| 29 | `mark_synced(ids)`: marcar varias como sincronizadas. |

**Qué es un `Protocol`:** Python usa tipado estructural. Cualquier clase que tenga esos métodos "encaja", aunque no herede explícitamente. `SqliteTareaRepository` hereda de `TareaRepository` solo para dejar clara la intención; el tipado funcionaría igual sin heredar.

**Por qué esto importa para las pruebas:** el servicio depende del protocolo, no de SQLite. En `tests/test_sync_service.py` se usa un `FakeTurso` y repositorios reales sobre una base temporal; en otros proyectos podrías usar un repositorio en memoria sin cambiar el servicio.

---

### 8.19 Dominio `tareas`: casos de uso

#### `src/domains/tareas/application/tarea_service.py` (146 líneas)

**Propósito:** ofrecer las operaciones que la UI necesita y coordinar modelo, repositorio y eventos.

##### `ProgresoDiario` (líneas 16-34)

| Líneas | Explicación |
|---|---|
| 16 | `@dataclass(frozen=True)`: valor inmutable. |
| 18 | `completadas_hoy`. |
| 19 | `pendientes`. |
| 20 | `total`. |
| 22-24 | `denominador`: completadas hoy + pendientes. |
| 26-30 | `porcentaje`: si el denominador es 0, devuelve 0.0; si no, `completadas_hoy / denominador`, limitado a 1.0 con `min`. |
| 32-34 | `texto`: `"X de Y hoy"`. |

**Por qué el denominador no es `total`:** si ayer completaste 10 tareas y hoy tienes 2 pendientes, usar `total` daría un porcentaje altísimo que no refleja el día actual. La fórmula `completadas_hoy / (completadas_hoy + pendientes)` mide solo el trabajo de hoy.

**Efecto secundario esperado:** si creas una tarea nueva, el denominador sube y el porcentaje baja. Es correcto: tienes más trabajo pendiente.

##### Clase `TareaService` (líneas 37-146)

| Líneas | Explicación |
|---|---|
| 40-42 | `__init__`: recibe el repositorio y el bus; los guarda como `_repo` y `_bus`. |
| 45-60 | `crear`: construye `Tarea`, la guarda, notifica y la devuelve. |
| 62-80 | `editar`: obtiene la tarea (lanza `NoEncontrado` si no existe), llama a `actualizar`, guarda, notifica y devuelve. |
| 82-87 | `completar`: si `tarea.completar()` devuelve `True` (hubo transición), guarda y notifica. Si ya estaba completada, no hace nada. |
| 89-94 | `reabrir`: análogo. |
| 96-101 | `alternar`: siempre guarda y notifica, porque el estado cambia. |
| 103-106 | `eliminar`: comprueba que exista y llama a `repo.delete` (soft delete). |
| 109-110 | `obtener`: devuelve la tarea o lanza `NoEncontrado`. |
| 112-113 | `listar`: delega en el repo. |
| 115-120 | `listar_por_deadline`: delega. |
| 122-135 | `progreso_diario`: lista todas, cuenta las completadas cuyo `updated_at` convertido a hora local cae en `hoy`, cuenta las pendientes y devuelve `ProgresoDiario`. |
| 138-142 | `_obtener`: helper que lanza `NoEncontrado` con un mensaje claro. |
| 144-146 | `_notificar`: publica `TAREAS_CAMBIADAS` y luego `DATOS_CAMBIADOS`. |

**Detalle de `progreso_diario` (línea 128):** `t.updated_at.astimezone().date() == hoy` convierte la marca UTC a la zona local del sistema antes de comparar. Si no se hiciera, una tarea completada a las 23:00 hora local podría contar como del día siguiente en UTC.

**Detalle de `_notificar` (líneas 144-146):** se publican dos eventos. El específico permite que las vistas de tareas hagan un refresco propio; el genérico permite que el shell actualice el progreso y el contador de sincronización. Podría haberse usado solo `DATOS_CAMBIADOS`, pero el evento específico deja claro qué cambió y permite suscripciones más selectivas.

**Idempotencia:** `completar` dos veces no genera dos escrituras ni dos eventos. Esto se prueba en `test_tarea_service.py:29-35`.

**No hay SQL aquí:** el servicio no sabe si los datos están en SQLite, en memoria o en un archivo. Solo usa el contrato del puerto.

---

### 8.20 Dominio `tareas`: repositorio SQLite

#### `src/domains/tareas/infrastructure/sqlite_tarea_repository.py` (141 líneas)

**Propósito:** implementar el puerto con SQLite.

##### Constantes (líneas 13-30)

| Líneas | Explicación |
|---|---|
| 13-16 | `_COLUMNAS`: lista de columnas en el orden exacto que usarán `SELECT` y los parámetros. |
| 18-30 | `_UPSERT`: inserta 10 valores; si el `id` ya existe, actualiza título, descripción, prioridad, completada, deadline, deleted, synced y updated_at. **No** actualiza `created_at`. |

**Por qué `_UPSERT` se usa tanto para `add` como para `update`:** simplifica el código. En ambos casos el estado final es "esta fila debe quedar así". La base decide si inserta o actualiza. Para una app pequeña es más robusto que mantener dos sentencias separadas.

##### Clase `SqliteTareaRepository` (líneas 33-141)

| Líneas | Explicación |
|---|---|
| 36-37 | `__init__`: guarda la `Database`. |
| 40-41 | `add`: ejecuta el upsert con `_params(tarea)`. |
| 43-44 | `update`: idéntico. |
| 46-51 | `delete`: lee la tarea; si no existe, no hace nada; si existe, llama a `marcar_eliminada()` y guarda. |
| 53-60 | `mark_synced`: si la lista está vacía, sale; si no, genera tantos `?` como ids y ejecuta un `UPDATE ... WHERE id IN (...)`. |
| 62-74 | `upsert_remoto`: aplica una fila del *pull*. Compara `updated_at`; si la local es igual o más nueva, no escribe y devuelve `False`. Si escribe, fuerza `synced=True` y devuelve `True`. |
| 77-82 | `get`: busca por id y `deleted=0`; devuelve entidad o `None`. |
| 84-89 | `list_all`: filtra `deleted=0`; si no se incluyen completadas, añade `completada=0`; ordena por completada, prioridad y creación descendente. |
| 91-104 | `list_by_deadline`: si `deadline_id is None`, filtra `deadline_id IS NULL`; si no, `deadline_id = ?`. Añade el filtro de completadas y el mismo orden. |
| 106-111 | `list_pending`: **no** filtra por `deleted`, para que los borrados también se suban. Ordena por `updated_at` ascendente. |
| 114-127 | `_params`: convierte la entidad a tupla. Prioridad y booleanos van como enteros; fechas como ISO. |
| 129-141 | `_fila_a_entidad`: convierte una fila SQLite (o un diccionario del *pull*) en `Tarea`, reconstruyendo enums, booleanos y fechas. |

**Seguridad contra inyección SQL:** los valores siempre van como parámetros (`?`), no concatenados en el texto. Los únicos fragmentos dinámicos son los marcadores de `mark_synced`, generados a partir de la **cantidad** de ids, no de su contenido.

**Detalle de `mark_synced`:** se podría hacer un `UPDATE` por id, pero sería más lento. El `IN (?, ?, ...)` actualiza todos en una sola sentencia.

**Detalle del orden (línea 74):** `completada ASC` pone primero las pendientes (0) y luego las hechas (1); `prioridad ASC` pone P1 antes que P4; `created_at DESC` muestra lo más reciente primero entre iguales.

**Detalle de `_fila_a_entidad`:** `bool(row["completada"])` porque SQLite no tiene booleanos nativos: guarda 0/1. `datetime.fromisoformat(...)` reconstruye la fecha consciente de zona horaria porque el texto incluía el offset.

**Qué pasa con una tarea borrada:** `get` y `list_all` la ocultan (`deleted=0`), pero `list_pending` la sigue viendo para poder propagar la eliminación. Esa aparente contradicción es intencional.

---

### 8.21 Dominio `tareas`: la vista

#### `src/domains/tareas/presentation/tareas_view.py` (366 líneas)

**Propósito:** mostrar la lista, permitir crear/editar/eliminar/completar y disparar la celebración.

##### Imports y clase (líneas 1-48)

- `logging` para registrar fallos de carga.
- `flet as ft` para la UI.
- `Tarea` y `Prioridad` para tipos y opciones.
- `DEADLINES_CAMBIADOS` y `TAREAS_CAMBIADAS` para suscribirse.
- `CaosError` para capturar errores de negocio.
- `AppContext` para acceder a los servicios.
- Colores del tema.
- Widgets reutilizables.
- `class TareasView(ft.Column)`: la vista es una columna con scroll.

##### Constructor (líneas 44-103)

| Líneas | Explicación |
|---|---|
| 45 | `super().__init__(expand=True, spacing=14, scroll=ft.ScrollMode.AUTO)`: ocupa el espacio y permite desplazarse. |
| 46 | Guarda el contexto. |
| 47 | `_filtro = "todas"`. |
| 48 | `_celebrando = False`: evita refrescos durante la animación. |
| 50-54 | Crea el campo de nueva tarea con `on_submit=self._crear_rapida` (Enter). |
| 55 | `self._input.expand = True`: el campo ocupa el ancho disponible. |
| 57-67 | `SegmentedButton` con tres filtros; no permite selección vacía ni múltiple. |
| 69 | `_lista`: columna donde se van a insertar las tarjetas. |
| 71-99 | `controls`: encabezado, fila de input + botón, filtros y lista. |
| 101-102 | Se suscribe a cambios de tareas y de deadlines (si cambia un proyecto, hay que refrescar los chips). |
| 103 | Primer refresco. |

**Detalle de `self._input.expand = True` (línea 55):** se asigna después de crear el campo porque `campo_texto` devuelve un `TextField` ya configurado; modificar `expand` fuera del constructor es válido.

**Detalle de `on_submit`:** en Flet, `on_submit` se dispara al pulsar Enter en un `TextField`. `_crear_rapida` acepta `_e=None`, así que sirve tanto para el botón como para el submit.

##### Eventos (líneas 106-177)

| Líneas | Explicación |
|---|---|
| 106-108 | `_on_cambio`: si **no** se está celebrando, refresca. Si se está celebrando, ignora el evento para no cortar la animación. |
| 110-114 | `_cambiar_filtro`: lee la selección y refresca. |
| 116-127 | `_crear_rapida`: lee y limpia el texto; si está vacío, avisa; intenta crear; captura `CaosError` y muestra el mensaje; si todo va bien, limpia el input y actualiza. |
| 129-146 | `_alternar`: activa `_celebrando`; llama a `completar` o `reabrir`; si hay error, avisa, desactiva la celebración y refresca; si se completó, lanza `_celebrar` como tarea; si se reabrió, desactiva y refresca. |
| 148-153 | `_celebrar`: `await` de la animación; en `finally` desactiva la celebración y refresca, pase lo que pase. |
| 155-177 | `_eliminar`: define `confirmar`, que cierra el diálogo y llama a `eliminar`; muestra un `AlertDialog` con Cancelar y Eliminar. |

**Por qué `_celebrando`:** al completar, el servicio publica eventos y la vista se refrescaría de inmediato, reconstruyendo las tarjetas y perdiendo la referencia al `Container` que se está animando. La bandera bloquea ese refresco hasta que la animación termina.

**Por qué `finally` (línea 151):** si `effects.celebrar` lanza una excepción no controlada, la bandera quedaría en `True` para siempre y la vista dejaría de refrescarse. `finally` garantiza la limpieza.

**Por qué se usa `self.page.run_task` (línea 143):** `_celebrar` es `async`. Flet necesita que las corrutinas se ejecuten a través de su bucle de eventos. `run_task` las agenda sin bloquear.

##### Render (líneas 180-211)

| Líneas | Explicación |
|---|---|
| 180-185 | `refrescar`: intenta listar todas; si falla, registra y usa lista vacía. |
| 187-190 | Aplica el filtro en memoria. |
| 192 | Limpia la lista de controles. |
| 193-200 | Si no hay tareas, elige un mensaje según el filtro y añade `estado_vacio`. |
| 201-202 | Si hay tareas, crea una tarjeta por cada una. |
| 206-211 | `_actualizar`: si `self.page` existe, actualiza solo la lista. |

**Por qué se filtra en memoria y no en SQL:** ya se cargan todas las tareas para el progreso y para la lista; filtrar en Python evita consultas extra y mantiene el repositorio simple. Con miles de tareas habría que mover el filtro a SQL.

**Por qué `if self.page is not None`:** una vista puede construirse antes de estar montada en la página. Llamar a `update()` sin página lanzaría un error. Es una defensa habitual en Flet.

##### Tarjeta de tarea (líneas 213-290)

| Líneas | Explicación |
|---|---|
| 214 | Crea el contenedor con `tarjeta(ft.Container(), padding=12)`. Se rellena después. |
| 216-220 | Checkbox con el estado actual; `on_change` captura `t=tarea` y `c=contenedor` con valores por defecto. |
| 222-234 | Título: tamaño 14.5, seminegrita; si está completada, color suave y tachado. |
| 236 | Metadatos empiezan con la píldora de prioridad. |
| 237-245 | Si tiene deadline, busca su título y añade un chip con icono de carpeta. |
| 247-250 | `detalle`: título + fila de metadatos con `wrap=True` (los chips pasan a otra línea si no caben). |
| 251-262 | Si hay descripción, se añade **en su propia línea** con `max_lines=1` y elipsis. |
| 264-289 | Fila principal: checkbox, columna expandible con el detalle, botón editar y botón eliminar. |
| 290 | Devuelve el contenedor. |

**El bug importante que se corrigió (líneas 251-262):** antes, la descripción era un `Text` con `expand=True` dentro de un `Row(wrap=True)`. En Flutter, un hijo expandible dentro de un `Row` con `wrap` rompe las restricciones de layout y provoca el temido rectángulo gris de error. La solución fue sacar la descripción del `Row` y ponerla como una línea más de la columna. El comentario del código lo explica para que nadie lo vuelva a meter.

**Por qué las lambdas usan `lambda e, t=tarea:`:** si escribieras `lambda e: self._alternar(tarea, ...)`, todas las lambdas del bucle capturarían la **última** `tarea` de la iteración. El valor por defecto `t=tarea` congela el valor de esa iteración. Es un error clásico de Python.

##### Diálogo de creación/edición (líneas 293-366)

| Líneas | Explicación |
|---|---|
| 294 | `es_edicion = tarea is not None`. |
| 295 | Campo título, precargado si se edita. |
| 296-301 | Campo descripción multilínea de 3 líneas. |
| 303-306 | Genera opciones de prioridad: valor numérico y texto `"P1 · Importante y urgente (Hazlo ahora)"`. |
| 307-311 | Selector de prioridad, con `"1"` por defecto. |
| 313-320 | Carga deadlines y crea opciones; la primera es `("", "Sin proyecto")`. |
| 322-345 | `guardar`: lee los campos, convierte prioridad y deadline, llama a `editar` o `crear`, captura `CaosError` y cierra el diálogo si todo va bien. |
| 347-366 | Muestra el `AlertDialog` con los campos y los botones Cancelar/Guardar. |

**Detalle de `deadline_id = campo_deadline.value or None`:** el desplegable usa `""` para "sin proyecto". Al convertir a `None`, la entidad guarda `NULL` en SQLite.

**Detalle de `Prioridad.desde(campo_prioridad.value or 1)`:** el valor del dropdown es un string (`"2"`); `desde` lo convierte a enum. Si por alguna razón viene vacío, se usa 1.

**Por qué se captura `CaosError` dentro de `guardar`:** si el título está vacío, `Titulo` lanza `ErrorDeValidacion`, que es un `CaosError`. Así el diálogo no se cierra y el usuario ve el mensaje.
---

### 8.22 Dominio `deadlines`: modelo

#### `src/domains/deadlines/models/deadline.py` (103 líneas)

**Propósito:** representar un proyecto o hito con fecha límite, área, descripción y estado completado.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 5-7 | Importa `dataclass`, `date` y `Final`. |
| 9-10 | Importa `Entity` y `Titulo`. |
| 12 | `SIN_CAMBIO = object()`: mismo patrón que en tareas. |
| 15-16 | `@dataclass class Deadline(Entity)`. |
| 17 | `titulo: str`. |
| 18 | `fecha_limite: date | None = None`. |
| 19 | `area: str = "General"`. |
| 20 | `descripcion: str = ""`. |
| 21 | `completado: bool = False`. |
| 23-29 | `__post_init__`: valida el título, limpia descripción, normaliza área (vacía → "General"), convierte `completado` a bool y, si `fecha_limite` viene como string, la convierte con `date.fromisoformat`. |
| 32-37 | `completar()`: idempotente; devuelve si hubo transición. |
| 39-44 | `reabrir()`: idempotente. |
| 46-51 | `alternar()`: invierte y devuelve el nuevo estado. |
| 54-57 | `dias_restantes(hoy=None)`: si no hay fecha, `None`; si hay, diferencia en días entre la fecha límite y hoy. |
| 59-61 | `esta_vencido(hoy=None)`: `True` solo si hay fecha, quedan días negativos y **no** está completado. |
| 64-103 | `actualizar(...)`: igual que en tareas, con los campos título, descripción, fecha y área. Convierte strings ISO a `date`, normaliza área y solo toca la entidad si algo cambió. |

**Diferencia con `Tarea`:** un deadline no tiene prioridad ni vínculo a otro proyecto. Su estado es binario (`completado`) y su información temporal es una fecha, no una marca de creación.

**`esta_vencido` y proyectos completados:** un proyecto terminado no se considera vencido aunque su fecha haya pasado. Es una regla de negocio deliberada y se prueba en `test_deadlines.py:28-32`.

**Fechas ISO:** `date.fromisoformat("2026-12-24")` produce `date(2026, 12, 24)`. El formato es `AAAA-MM-DD`, que es el que SQLite guarda como texto.

---

### 8.23 Dominio `deadlines`: puertos

#### `src/domains/deadlines/application/ports.py` (23 líneas)

| Líneas | Explicación |
|---|---|
| 10-11 | `class DeadlineRepository(Protocol)`. |
| 11 | `add`. |
| 13 | `update`. |
| 15 | `get`. |
| 17 | `list_all(incluir_completados=True)`. |
| 19 | `delete`. |
| 21 | `list_pending`. |
| 23 | `mark_synced(ids)`. |

Es más pequeño que el de tareas porque un deadline no se filtra por otro deadline ni necesita listar "sueltos". La vista de proyectos solo necesita listar y calcular progreso.

---

### 8.24 Dominio `deadlines`: casos de uso

#### `src/domains/deadlines/application/deadline_service.py` (147 líneas)

**Propósito:** gestionar proyectos y, además, calcular su avance a partir de las tareas vinculadas y desvincular tareas al eliminar.

##### Estructuras de resultado (líneas 20-35)

| Líneas | Explicación |
|---|---|
| 20-21 | `@dataclass(frozen=True) class ProgresoDeadline`. |
| 22 | `hechas`: tareas completadas. |
| 23 | `total`: tareas del proyecto. |
| 25-29 | `porcentaje`: 0.0 si no hay tareas; si no, `hechas/total`, limitado a 1.0. |
| 32-35 | `ResumenDeadline`: agrupa un `Deadline` con su `ProgresoDeadline` para que la vista reciba todo junto. |

##### Clase `DeadlineService` (líneas 38-147)

| Líneas | Explicación |
|---|---|
| 39-47 | `__init__`: recibe el repositorio de deadlines, el de tareas y el bus. |
| 50-66 | `crear`: construye el `Deadline`, guarda, notifica y devuelve. |
| 68-86 | `editar`: obtiene, actualiza, guarda, notifica y devuelve. |
| 88-93 | `completar`: si hay transición, guarda y notifica **incluyendo tareas** (porque el progreso mostrado puede cambiar). |
| 95-100 | `reabrir`: igual. |
| 102-107 | `alternar`: igual. |
| 109-116 | `eliminar`: obtiene el deadline; recorre las tareas vinculadas, las desvincula y las guarda; luego hace soft delete del deadline; notifica deadlines y tareas. |
| 119-120 | `obtener`: helper con `NoEncontrado`. |
| 122-123 | `listar`: delega. |
| 125-128 | `progreso(deadline_id)`: lista las tareas del proyecto, cuenta completadas y total. |
| 130-134 | `resumen()`: recorre todos los deadlines y devuelve una lista de `ResumenDeadline`. |
| 137-141 | `_obtener`: lanza `NoEncontrado` si no existe. |
| 143-147 | `_notificar`: publica `DEADLINES_CAMBIADOS`; si se pidió, también `TAREAS_CAMBIADAS`; y siempre `DATOS_CAMBIADOS`. |

**Por qué `DeadlineService` conoce `TareaRepository`:** el progreso de un proyecto depende de sus tareas. Esta lectura cruza dominios, pero se hace en la **capa de aplicación**, no en el modelo ni en la vista. Es una decisión pragmática: el módulo de deadlines necesita saber cuántas tareas tiene asociadas.

**Por qué se desvinculan las tareas antes de borrar:** aunque el esquema tenga `ON DELETE SET NULL`, el borrado es lógico (`deleted=1`), no físico, así que la clave foránea no se activaría. Hacerlo explícito garantiza que las tareas queden sueltas y se sincronicen con `deadline_id=NULL`.

**Complejidad del resumen:** por cada deadline se hace una consulta a tareas. Con pocos proyectos es aceptable. Si hubiera cientos, se podría hacer una sola consulta agrupada. Es una mejora anotada, no un bug.

**Detalle de `incluir_tareas` (líneas 143-147):** editar un proyecto no cambia sus tareas, así que no hace falta avisar a la vista de tareas. Completar o eliminar sí, porque el checkbox o el vínculo cambian.

---

### 8.25 Dominio `deadlines`: repositorio SQLite

#### `src/domains/deadlines/infrastructure/sqlite_deadline_repository.py` (129 líneas)

| Líneas | Explicación |
|---|---|
| 12-15 | `_COLUMNAS`: 10 columnas. |
| 17-29 | `_UPSERT`: inserta y, en conflicto, actualiza todo menos `created_at`. |
| 32-34 | `class SqliteDeadlineRepository(DeadlineRepository)` con `__init__(db)`. |
| 37-38 | `add`: upsert. |
| 40-41 | `update`: upsert. |
| 43-48 | `delete`: lectura + `marcar_eliminada()` + update. |
| 50-57 | `mark_synced`: `UPDATE ... WHERE id IN (...)`. |
| 59-71 | `upsert_remoto`: aplica una fila de la nube solo si su `updated_at` es más reciente. |
| 74-79 | `get`: filtra `deleted=0`. |
| 81-90 | `list_all`: filtra, opcionalmente completados, y ordena. |
| 92-98 | `list_pending`: `synced=0`, sin filtrar `deleted`. |
| 100-113 | `_params`: fechas a ISO o `None`; booleanos a enteros. |
| 115-129 | `_fila_a_entidad`: reconstruye `Deadline`. |

**El orden de `list_all` (líneas 71-75) es interesante:**

```sql
ORDER BY completado ASC,
         CASE WHEN fecha_limite IS NULL THEN 1 ELSE 0 END,
         fecha_limite ASC,
         created_at DESC
```

1. Pendientes antes que completados.
2. Los que tienen fecha antes que los que no.
3. Fecha más próxima primero.
4. Si empatan, el más reciente primero.

**Por qué `CASE WHEN ... THEN 1 ELSE 0 END`:** en SQLite, `NULL` se ordena antes que cualquier valor en un `ORDER BY ASC`. Eso pondría los proyectos sin fecha al principio, que no es lo deseado. El `CASE` convierte "sin fecha" en 1 y "con fecha" en 0, forzando que los que tienen fecha vayan primero.

**Fecha en la base:** se guarda como `TEXT` ISO (`"2026-12-24"`), legible y ordenable alfabéticamente porque el formato es fijo.

---

### 8.26 Dominio `deadlines`: la vista

#### `src/domains/deadlines/presentation/deadlines_view.py` (343 líneas)

**Propósito:** listar proyectos con su avance, permitir crear/editar/completar/eliminar y elegir fecha con un calendario.

##### Constructor (líneas 38-62)

| Líneas | Explicación |
|---|---|
| 39-40 | `class DeadlinesView(ft.Column)`; `expand=True`, `spacing=14`, scroll automático. |
| 41-42 | Guarda el contexto y crea la columna de la lista. |
| 44-58 | `controls`: encabezado con botón `+` y la lista. |
| 60-61 | Se suscribe a deadlines y tareas (el avance depende de ambas). |
| 62 | Primer refresco. |

##### Refresco y tarjeta (líneas 65-194)

| Líneas | Explicación |
|---|---|
| 65-66 | `_on_cambio`: refresca. |
| 68-73 | `refrescar`: pide `resumen()`; si falla, registra y usa lista vacía. |
| 75-83 | Limpia y, si no hay proyectos, muestra estado vacío. |
| 84-88 | Si hay, crea una tarjeta por cada `ResumenDeadline`. |
| 90-94 | Actualiza la lista si la página está montada. |
| 96-97 | `_tarjeta`: calcula `dias` con `dias_restantes()`. |
| 98-107 | Elige el chip de estado: Completado, Sin fecha, Vencido, Vence hoy o N días restantes. |
| 109-112 | Metadatos: área, fecha corta (si hay) y estado. |
| 114-120 | Barra de progreso con el porcentaje; verde si está completado, violeta si no. |
| 122-180 | Columna con fila superior (checkbox, título, metadatos, editar, eliminar) y fila inferior (barra + "hechas/total"). |
| 182-192 | Si hay descripción, la inserta en la posición 1 (debajo del título). |
| 194 | Envuelve todo en `tarjeta(contenido)`. |

**Detalle del chip de vencimiento (líneas 98-107):** el orden importa. Primero se comprueba si está completado (aunque la fecha haya pasado); después si no tiene fecha; después si `dias < 0`; después si `dias == 0`; y si no, los días restantes. Si se comprobara `dias < 0` antes que `completado`, un proyecto terminado aparecería como vencido.

**Detalle de `contenido.controls.insert(1, ...)` (líneas 182-192):** la lista original es `[fila_superior, fila_progreso]`; insertar en el índice 1 coloca la descripción entre ambas. Es más simple que reconstruir la columna.

**`ft.ProgressBar`:** `value` debe estar entre 0 y 1. `progreso.porcentaje` ya lo garantiza.

##### Alternar y eliminar (líneas 196-226)

| Líneas | Explicación |
|---|---|
| 196-200 | `_alternar`: llama a `deadlines.alternar`; captura `CaosError` y avisa. |
| 202-226 | `_eliminar`: diálogo de confirmación; el texto avisa de que las tareas quedarán sueltas; al confirmar, cierra y elimina. |

**Por qué no se refresca a mano tras `alternar`:** el servicio publica `DEADLINES_CAMBIADOS` y la propia vista está suscrita, así que se refresca sola. Si se refrescara también a mano, habría dos reconstrucciones innecesarias.

##### Diálogo con selector de fecha (líneas 229-343)

| Líneas | Explicación |
|---|---|
| 230 | `es_edicion`. |
| 231-238 | Campos título, descripción y área. |
| 240-242 | `fecha_holder`: diccionario con la fecha seleccionada. Se usa un diccionario porque las funciones internas pueden mutar su contenido sin necesidad de `nonlocal`. |
| 243-249 | Campo de fecha con `fecha_corta` o vacío; `read_only=True` evita escribir a mano. |
| 252-273 | `elegir_fecha`: define `al_cambiar` (convierte `datetime` a `date`, guarda en el holder, actualiza el campo) y abre un `DatePicker` con límites 2000–2100. |
| 275-278 | `quitar_fecha`: pone `None`, vacía el campo y actualiza. |
| 280-300 | `guardar`: llama a `editar` o `crear`; captura `CaosError`; cierra si todo va bien. |
| 302-343 | Diálogo con los campos y una fila para la fecha con botones de calendario y borrar. |

**Por qué `fecha_holder` y no `nonlocal`:** dentro de `guardar` y `al_cambiar` se necesita leer y escribir la fecha. Un diccionario es mutable, así que se puede modificar sin redeclarar. También se podría usar `nonlocal fecha`, pero el diccionario es explícito y funciona igual.

**Detalle de `DatePicker` (líneas 263-273):** en Flet 1.x el selector de fecha se muestra con `page.show_dialog`. `on_change` recibe `ev.control.value`, que puede ser `datetime` o `date` según la plataforma; por eso se normaliza con `isinstance(valor, datetime)`.

**Detalle de `first_date`/`last_date`:** limitan el calendario a un rango razonable (2000–2100) y evitan fechas absurdas por error de tecleo.
---

### 8.27 Dominio `notas`: modelo

#### `src/domains/notas/models/nota.py` (72 líneas)

**Propósito:** guardar conocimiento (título + contenido) clasificado por área y, opcionalmente, vinculado a un proyecto.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 5-6 | Importa `dataclass` y `Final`. |
| 8-9 | Importa `Entity` y `Titulo`. |
| 11 | `SIN_CAMBIO`. |
| 14-15 | `@dataclass class Nota(Entity)`. |
| 16 | `titulo: str`. |
| 17 | `contenido: str = ""`. |
| 18 | `area: str = "General"`. |
| 19 | `deadline_id: str | None = None`. |
| 21-26 | `__post_init__`: valida título, limpia contenido, normaliza área y limpia deadline. |
| 28-33 | `resumen`: colapsa espacios del contenido. Si está vacío, "Sin contenido". Si tiene más de 160 caracteres, recorta a 157 y añade "...". |
| 35-72 | `actualizar(...)`: mismo patrón de actualización parcial que tareas y deadlines. |

**Por qué la nota no tiene estado completado:** una nota es información, no una acción. No se "termina"; se edita o se elimina.

**Detalle de `resumen`:** `" ".join(self.contenido.split())` elimina saltos de línea para que la tarjeta no crezca. `texto[:157] + "..."` mantiene el resultado en 160 caracteres exactos.

**Validación del título:** una nota sin título no se permite. Si quieres una nota rápida sin título, tendrías que cambiar la regla en `Titulo`, pero afectaría a tareas y proyectos también. Es una decisión consciente del kernel compartido.

---

### 8.28 Dominio `notas`: puertos

#### `src/domains/notas/application/ports.py` (25 líneas)

| Líneas | Explicación |
|---|---|
| 10-11 | `class NotaRepository(Protocol)`. |
| 11 | `add`. |
| 13 | `update`. |
| 15 | `get`. |
| 17 | `list_all(buscar=None)`: búsqueda opcional por texto. |
| 19 | `list_by_deadline(deadline_id)`: notas de un proyecto. |
| 21 | `delete`. |
| 23 | `list_pending`. |
| 25 | `mark_synced`. |

**Diferencia con los otros puertos:** `list_all` recibe un criterio de búsqueda. Eso permite que la implementación decida cómo buscar (LIKE en SQLite, por ejemplo) sin que el servicio conozca SQL.

---

### 8.29 Dominio `notas`: casos de uso

#### `src/domains/notas/application/nota_service.py` (80 líneas)

| Líneas | Explicación |
|---|---|
| 12-15 | `class NotaService` con repositorio y bus. |
| 18-34 | `crear`: construye la nota, guarda, notifica y devuelve. |
| 36-54 | `editar`: obtiene, actualiza, guarda, notifica y devuelve. |
| 56-59 | `eliminar`: comprueba que exista y hace soft delete. |
| 62-63 | `obtener`: helper. |
| 65-66 | `listar(buscar=None)`: delega la búsqueda en el repositorio. |
| 68-69 | `listar_por_deadline`: delega. |
| 72-76 | `_obtener`: lanza `NoEncontrado`. |
| 78-80 | `_notificar`: publica `NOTAS_CAMBIADAS` y `DATOS_CAMBIADOS`. |

**Por qué no hay `completar`:** las notas no tienen ciclo de vida de acción. Su ciclo es crear, editar y eliminar.

**El servicio no recorta el resumen:** eso es una propiedad del modelo (`Nota.resumen`). La vista la usa directamente. Así la regla de presentación del resumen vive en el dominio y se puede probar sin UI.

---

### 8.30 Dominio `notas`: repositorio SQLite

#### `src/domains/notas/infrastructure/sqlite_nota_repository.py` (131 líneas)

| Líneas | Explicación |
|---|---|
| 12-15 | `_COLUMNAS`: 9 columnas. |
| 17-28 | `_UPSERT`: inserta y actualiza todo menos `created_at`. |
| 31-33 | Clase y `__init__(db)`. |
| 36-37 | `add`: upsert. |
| 39-40 | `update`: upsert. |
| 42-47 | `delete`: soft delete. |
| 49-56 | `mark_synced`. |
| 58-70 | `upsert_remoto`: aplica una fila de la nube solo si su `updated_at` es más reciente. |
| 73-78 | `get`: por id y `deleted=0`. |
| 80-88 | `list_all`: filtra por búsqueda y ordena por `updated_at DESC`. |
| 90-96 | `list_by_deadline`: por deadline, sin borradas, más recientes primero. |
| 98-104 | `list_pending`: `synced=0`, sin filtrar deleted. |
| 106-118 | `_params`: tupla de valores. |
| 120-131 | `_fila_a_entidad`: reconstruye `Nota`. |

**La búsqueda (líneas 84-87) en detalle:**

```python
if buscar and buscar.strip():
    patron = f"%{buscar.strip()}%"
    sql += " AND (titulo LIKE ? OR contenido LIKE ? OR area LIKE ?)"
    params.extend([patron, patron, patron])
```

- `buscar.strip()` evita que un espacio en blanco active una búsqueda inútil.
- `%` significa "cualquier cosa antes y después".
- Se aplica a tres columnas con `OR`.
- El patrón va como **parámetro**, no concatenado. Aunque el usuario escriba `%` o `'`, SQLite lo trata como texto dentro del patrón; no se ejecuta SQL arbitrario.

**Sensibilidad a mayúsculas:** `LIKE` en SQLite es insensible a mayúsculas para ASCII por defecto. Por eso `buscar="uuid"` encuentra `"SQLite + UUID"` (probado en `test_notas.py:10-16`).

**Orden por `updated_at DESC`:** la nota editada más recientemente aparece arriba. Es útil para un cuaderno de ideas.

---

### 8.31 Dominio `notas`: la vista

#### `src/domains/notas/presentation/notas_view.py` (265 líneas)

**Propósito:** listar notas, buscarlas en vivo y crear/editar/eliminar.

##### Constructor (líneas 39-73)

| Líneas | Explicación |
|---|---|
| 40-41 | `class NotasView(ft.Column)` con scroll. |
| 42-43 | Contexto y texto de búsqueda vacío. |
| 45-50 | Campo de búsqueda con icono de lupa; `on_change` refresca en cada tecla. |
| 52 | Columna de tarjetas. |
| 54-69 | Encabezado con botón `+`, campo de búsqueda y lista. |
| 71-72 | Se suscribe a notas y deadlines. |
| 73 | Primer refresco. |

**Búsqueda en vivo:** `on_change` se dispara con cada cambio del `TextField`. El repositorio hace `LIKE`; para pocas notas es instantáneo. Si la lista creciera mucho, convendría un retraso (debounce) para no consultar en cada tecla.

##### Refresco (líneas 76-107)

| Líneas | Explicación |
|---|---|
| 76-77 | `_on_cambio`: refresca. |
| 79-81 | `_cambiar_busqueda`: guarda el texto y refresca. |
| 83-88 | `refrescar`: lista con búsqueda; si falla, registra y usa lista vacía. |
| 90-98 | Si no hay notas, muestra estado vacío; el título cambia según haya búsqueda o no. |
| 100-101 | Si hay, construye un diccionario `id → deadline` **una sola vez** y crea las tarjetas. |
| 103-107 | Actualiza si la página está montada. |

**Por qué el diccionario de deadlines (línea 100):** sin él, cada tarjeta recorrería la lista completa de proyectos para encontrar el suyo (O(n×m)). Con el diccionario, cada búsqueda es O(1). Es una optimización sencilla y didáctica.

##### Tarjeta (líneas 109-173)

| Líneas | Explicación |
|---|---|
| 110-112 | Metadatos empiezan con el área. |
| 113-120 | Si la nota tiene deadline y existe, añade un chip con su título. |
| 121-123 | Añade el texto "hace cuánto" se editó. |
| 125-173 | Tarjeta con fila principal (título + resumen + botones) y fila de metadatos con wrap. |

**Detalle de la condición `nota.deadline_id in deadlines` (línea 113):** si el proyecto fue eliminado, la nota podría conservar el id. El diccionario solo contiene proyectos visibles, así que simplemente no se muestra el chip. No se rompe nada.

**`nota.resumen` vs `nota.contenido`:** la tarjeta muestra el resumen recortado; el diálogo muestra el contenido completo.

##### Eliminar y diálogo (líneas 175-265)

| Líneas | Explicación |
|---|---|
| 175-197 | `_eliminar`: confirmación y soft delete. |
| 200-216 | `_abrir_dialogo`: campos título, área, contenido multilínea (8 líneas) y selector de proyecto. |
| 218-238 | `guardar`: crea o edita; captura `CaosError`; cierra si va bien. |
| 240-265 | Diálogo con `scroll=ft.ScrollMode.AUTO` para que el contenido largo no desborde. |

**Detalle de `scroll` en el diálogo (línea 247):** una nota puede tener mucho texto. Sin scroll, el diálogo crecería más que la pantalla y los botones quedarían inaccesibles en móvil.

**Detalle de `campo_contenido` (líneas 204-209):** `multilinea=True` y `lineas=8`. En `campo_texto`, `max_lines` será `max(8, 4) = 8`, así que el campo muestra 8 líneas y permite desplazarse dentro.
---

### 8.32 Pruebas: `tests/conftest.py` — las fixtures

**Propósito:** crear una base de datos temporal y los servicios reales para cada prueba, de forma aislada.

| Líneas | Explicación |
|---|---|
| 1 | Docstring. |
| 5 | Importa `pytest`. |
| 7-18 | Importa servicios, repositorios, bus y `Database`. |
| 21-26 | `db`: crea `caos_test.db` dentro de `tmp_path` (carpeta temporal única por prueba), inicializa, entrega con `yield` y cierra al terminar. |
| 29-31 | `bus`: un `EventBus` nuevo por prueba. |
| 34-36 | `deadlines_repo`: repositorio sobre la base temporal. |
| 39-41 | `tareas_repo`. |
| 44-46 | `notas_repo`. |
| 49-51 | `tareas`: `TareaService` con su repo y el bus. |
| 54-56 | `deadlines`: `DeadlineService` con repo de deadlines, repo de tareas y bus. |
| 59-61 | `notas`: `NotaService`. |

**Qué es una fixture:** una función que prepara algo que varias pruebas necesitan. Si una prueba declara `def test_x(tareas):`, pytest ejecuta la fixture `tareas` y le pasa el valor. Las fixtures pueden depender de otras: `tareas` depende de `tareas_repo` y `bus`; `tareas_repo` depende de `db`.

**Por qué `tmp_path`:** cada prueba recibe una carpeta temporal distinta y se limpia sola. No se contamina la base real del usuario ni se comparte estado entre pruebas.

**Por qué `yield`:** todo lo anterior al `yield` es preparación; lo posterior es limpieza. Aunque la prueba falle, pytest ejecuta el código después del `yield` y cierra la conexión.

**Servicios reales, no mocks:** las pruebas usan SQLite de verdad. Eso detecta errores de SQL, de mapeo y de claves foráneas. Solo el cliente de Turso se sustituye por un doble en `test_sync_service.py`.

---

### 8.33 `tests/test_tarea_model.py` — reglas del modelo (13 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 14-16 | `test_id_es_uuid_v4_generado_en_la_app` | `UUID(tarea.id).version == 4`; el id se genera localmente. |
| 19-21 | `test_titulo_se_normaliza` | Los espacios repetidos se colapsan. |
| 24-26 | `test_titulo_vacio_es_invalido` | Un título de solo espacios lanza `ErrorDeValidacion`. |
| 29-31 | `test_titulo_demasiado_largo_es_invalido` | 121 caracteres se rechazan. |
| 34-36 | `test_prioridad_por_defecto_es_eisenhower_1` | Sin prioridad, se usa P1. |
| 39-41 | `test_prioridad_invalida_es_rechazada` | `prioridad=9` lanza error. |
| 44-46 | `test_prioridad_se_convierte_desde_entero_y_texto` | `desde(2)` y `desde("4")` funcionan. |
| 49-61 | `test_completar_y_reabrir_gestionan_estado_y_sincronizacion` | Las transiciones son idempotentes y `synced` vuelve a `False`. |
| 64-67 | `test_alternar_devuelve_el_nuevo_estado` | `alternar` devuelve el estado resultante. |
| 70-82 | `test_actualizar_valida_y_normaliza` | Actualizar valida, normaliza y marca pendiente. |
| 85-89 | `test_actualizar_sin_cambios_no_toca_updated_at` | Si el valor es igual, no hay escritura ni cambio de fecha. |
| 92-100 | `test_vincular_y_desvincular_deadline` | Los atajos de vínculo funcionan. |
| 103-110 | `test_borrado_logico_es_idempotente` | Marcar dos veces no cambia la fecha. |

**Qué NO prueban estas pruebas:** no tocan SQLite ni Flet. Son pruebas puras del modelo, rápidas y deterministas.

---

### 8.34 `tests/test_tarea_service.py` — casos de uso (11 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 17-26 | `test_crear_publica_eventos_y_persiste` | Se guarda y se publican `TAREAS_CAMBIADAS` y `DATOS_CAMBIADOS`, en ese orden. |
| 29-35 | `test_completar_es_idempotente_y_persiste` | Completar dos veces no rompe y el estado queda guardado. |
| 38-40 | `test_reabrir_una_tarea_pendiente_no_falla` | Reabrir algo ya pendiente es seguro. |
| 43-46 | `test_alternar` | Alterna en ambos sentidos. |
| 49-56 | `test_editar_campos_parciales` | Editar solo el título conserva prioridad y descripción. |
| 59-67 | `test_editar_permite_vincular_y_desvincular_deadline` | `deadline_id` se puede poner y quitar. |
| 70-78 | `test_eliminar_usa_borrado_logico` | La tarea desaparece de `listar` pero sigue pendiente de sync con `deleted=True`. |
| 81-87 | `test_operar_sobre_id_inexistente_lanza_no_encontrado` | Los tres comandos lanzan `NoEncontrado`. |
| 90-102 | `test_progreso_diario` | 1 completada, 2 pendientes, 3 totales, 33 %. |
| 105-108 | `test_progreso_sin_tareas_es_cero` | Sin tareas, 0 % y "0 de 0 hoy". |
| 111-121 | `test_progreso_ignora_tareas_completadas_otro_dia` | Modifica `updated_at` a 2020 y comprueba que no cuenta para hoy. |

**Detalle de la última prueba (líneas 114-118):** accede a `tareas._repo._db` para modificar la fecha directamente. Es una prueba de integración que necesita saltarse la API para simular un dato antiguo. En código de producción no se debe tocar `_db`.

**Lo que confirma la prueba de eventos:** el orden `["tareas", "datos"]` demuestra que `_notificar` publica primero el evento específico y luego el genérico.

---

### 8.35 `tests/test_deadlines.py` — proyectos (10 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 16-25 | `test_dias_restantes_y_vencimiento` | Fechas futuras, pasadas y ausentes. |
| 28-32 | `test_un_proyecto_completado_no_se_considera_vencido` | Completado gana sobre vencido. |
| 35-37 | `test_fecha_iso_se_convierte` | Un string ISO se convierte a `date`. |
| 40-42 | `test_titulo_vacio_es_invalido` | Validación compartida. |
| 45-59 | `test_crear_y_editar_deadline` | Crear, editar y quitar fecha. |
| 62-73 | `test_progreso_de_un_deadline` | 0/2 y luego 1/2 con 50 %. |
| 76-84 | `test_resumen_incluye_progreso` | El resumen agrupa deadline + progreso. |
| 87-94 | `test_eliminar_deadline_desvincula_tareas` | La tarea queda con `deadline_id=None`. |
| 97-100 | `test_completar_deadline` | Completar y reabrir. |
| 103-107 | `test_operar_sobre_deadline_inexistente` | `NoEncontrado`. |

**Fecha fija `HOY = date(2026, 11, 5)` (línea 13):** las pruebas de días restantes usan una fecha fija para no depender del día real en que se ejecutan. Es una buena práctica: una prueba no debe cambiar de resultado según el calendario.

---

### 8.36 `tests/test_notas.py` — notas (7 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 10-16 | `test_crear_listar_y_buscar` | Busca por contenido y por área. |
| 19-34 | `test_editar_nota` | Edita todos los campos, incluido el deadline. |
| 37-40 | `test_resumen_recorta_contenido` | Un contenido de 500 caracteres se recorta a ≤160 y termina en "...". |
| 43-45 | `test_resumen_vacio` | Sin contenido devuelve "Sin contenido". |
| 48-55 | `test_eliminar_nota` | Soft delete y pendiente de sync. |
| 58-64 | `test_listar_por_deadline` | Solo devuelve las notas del proyecto pedido. |
| 67-71 | `test_nota_inexistente` | Editar o eliminar un id falso lanza `NoEncontrado`. |

---

### 8.37 `tests/test_repositories.py` — persistencia (8 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 11-20 | `test_roundtrip_de_tarea` | Guardar y recuperar conserva todos los campos y la fecha. |
| 23-34 | `test_list_all_filtra_completadas_y_ordena_por_prioridad` | Orden P1, P4, Hecha; filtro de pendientes. |
| 37-46 | `test_list_by_deadline_incluye_tareas_sueltas` | `deadline_id` real vs `None`. |
| 49-61 | `test_borrado_logico_oculta_pero_queda_pendiente_de_sync` | `get` devuelve `None`, pero `list_pending` ve la fila borrada. |
| 64-71 | `test_mark_synced` | Tras marcar, la lista de pendientes queda vacía y `synced=True`. |
| 74-82 | `test_repositorio_deadlines_roundtrip_y_orden` | Orden por fecha y recuperación de fecha. |
| 85-91 | `test_repositorio_notas_busca_por_titulo_contenido_y_area` | Los tres campos participan en la búsqueda. |
| 94-100 | `test_eliminar_nota_es_borrado_logico` | Borrado lógico de notas. |

**La prueba clave es la 49-61:** explica visualmente la diferencia entre "visible para el usuario" (`get`/`list_all` filtran `deleted`) y "pendiente para la nube" (`list_pending` no filtra). Es el corazón del offline-first.

---

### 8.38 `tests/test_infrastructure.py` — Turso y SQLite (11 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 19-22 | `test_normalizar_url` | `libsql://`, dominio sin esquema y `https://`. |
| 25-32 | `test_parametros_tipados` | `None`, bool, int, float, str y bytes se traducen bien. |
| 57-72 | `test_pipeline_payload_y_headers` | La sesión falsa captura URL, header Bearer, `close` y args tipados. |
| 75-84 | `test_error_en_resultado_de_turso` | Un `type: error` dentro de `results` lanza `ErrorDeSincronizacion`. |
| 87-94 | `test_http_error` | HTTP 401 lanza error con el código. |
| 97-99 | `test_cliente_sin_credenciales` | Sin URL ni token, `configurado=False`. |
| 102-134 | `test_ejecutar_decodifica_filas_tipadas` | `consultar` traduce celdas `text`, `integer` y `null` a Python. |
| 137-167 | `test_ejecutar_alinea_resultados_por_sentencia` | Cada sentencia del pipeline tiene su propia lista de filas. |
| 170-172 | `test_esquema_creado` | Existen las cuatro tablas (incluida `settings`). |
| 175-183 | `test_default_db_path_respeta_variables` | Prioridad de `CAOS_DB_PATH` y `FLET_APP_STORAGE_DATA`. |
| 185-197 | `test_datetime_iso_se_conserva` | Al recuperar, `updated_at` es `datetime` y tiene `tzinfo`. |

**Cómo se evita la red:** `_SesionFalsa` implementa solo `post`, que devuelve una respuesta prefabricada. `TursoClient` acepta `session=...`, así que no se instancia `requests.Session` real. Es inyección de dependencias aplicada a las pruebas.

**`_Respuesta`:** simula `status_code`, `text` y `json()`. Con eso se pueden probar los tres caminos: éxito, error HTTP y error dentro del cuerpo.

---

### 8.39 `tests/test_sync_service.py` — sincronización (14 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 98-106 | `test_pendientes_iniciales` | Un registro de cada tipo da 1/1/1 y total 3. |
| 109-139 | `test_sincronizar_envia_en_orden_y_marca_synced` | Se envían esquema + 3 upserts + 3 lecturas; deadlines antes que tareas y notas; luego todo queda sincronizado. |
| 142-155 | `test_segunda_sincronizacion_solo_lee` | Sin pendientes no se sube nada, pero **sí** se consulta la nube para bajar cambios. |
| 158-174 | `test_borrado_logico_se_propaga` | El parámetro `deleted` del upsert vale 1. |
| 177-180 | `test_sin_configuracion_lanza_error` | `TursoNoConfigurado`. |
| 183-197 | `test_error_de_red_no_marca_synced` | Si `ejecutar` falla, la tarea sigue pendiente. |
| 200-216 | `test_actualizar_credenciales_delega_en_el_cliente` | `actualizar_credenciales` pasa la URL y el token al cliente. |
| 219-248 | `test_instalacion_nueva_baja_datos_de_la_nube` | Un dispositivo vacío recibe deadlines, tareas y notas; una segunda pasada no reescribe. |
| 251-266 | `test_pull_no_pisa_un_cambio_local_mas_nuevo` | Si la fila remota es más vieja, se conserva la local. |
| 269-295 | `test_pull_aplica_un_borrado_remoto` | Un `deleted=1` remoto hace desaparecer la fila local. |
| 298-330 | `test_upsert_remoto_conserva_la_version_mas_nueva` | El `WHERE excluded.updated_at > ...` del SQL de subida no pisa una versión más nueva. |
| 333-347 | `test_subida_publica_solo_el_evento_de_estado` | Al subir no se refrescan las listas: solo se publica `SYNC_CAMBIADO`. |
| 350-370 | `test_pull_publica_eventos_de_dominio_y_de_estado` | Al recibir filas se publican los eventos de dominio y el de estado. |
| 373-381 | `test_sincronizar_si_libre_devuelve_none_si_esta_ocupado` | Si el candado está tomado, la automática no arranca otra pasada. |

**`FakeTurso` (líneas 15-30):** no hereda de `TursoClient`; solo necesita `configurado` y `ejecutar`. `ejecutar` registra el pipeline y devuelve las filas prefijadas en `filas` (`deadlines`, `tareas`, `notas`). Gracias al tipado estructural y a la inyección, el servicio funciona igual.

**La prueba 109-139 es la más completa:** verifica el tamaño del pipeline, el orden de las sentencias y que `mark_synced` se ejecutó. Si alguien cambiara el orden (por ejemplo, notas antes que deadlines), la prueba fallaría.

**La prueba 183-197 protege la propiedad más importante:** un fallo de red no debe hacer creer que los datos están en la nube. Si `mark_synced` se ejecutara antes de `ejecutar`, esta prueba lo detectaría.

**Las pruebas 219-295 cubren el *pull*:** instalación nueva, conflicto con cambio local y borrado remoto. Son las que garantizan que la sincronización sirve para varios dispositivos y no solo para subir.

**Las pruebas 333-381 cubren la convivencia con la automática:** qué eventos se publican y qué pasa cuando el candado está ocupado.

---

### 8.40 `tests/test_settings_repository.py` — credenciales y ajustes (7 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 13-14 | `test_esquema_incluye_settings` | `initialize()` crea la tabla `settings`. |
| 17-30 | `test_guardar_y_leer` | `set` inserta, actualiza y `eliminar` borra. |
| 33-43 | `test_turso_usa_lo_guardado` | Sin variables de entorno, devuelve lo guardado. |
| 46-51 | `test_turso_cae_al_entorno_si_no_hay_guardado` | Las variables de entorno siguen funcionando en escritorio. |
| 54-60 | `test_lo_guardado_gana_al_entorno` | Lo guardado en el dispositivo tiene prioridad. |
| 63-70 | `test_borrar_turso` | `borrar_turso` deja ambas claves vacías. |
| 73-86 | `test_cliente_actualiza_credenciales_en_caliente` | `TursoClient.actualizar_credenciales` normaliza la URL y activa/desactiva la conexión. |

**Qué cubre:** el camino que usa Android para guardar las credenciales, sin depender de variables de entorno ni de red.

---

### 8.41 `tests/test_event_bus.py` — bus (3 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 8-22 | `test_publicar_y_desuscribir` | Publica dos veces, desuscribe y la tercera publicación no llega. |
| 25-36 | `test_no_duplica_listeners` | Suscribir dos veces la misma función solo llama una vez. |
| 39-50 | `test_un_listener_roto_no_impide_a_los_demas` | Un callback que lanza `RuntimeError` no impide que el siguiente reciba el evento. |

**Cómo ejecutar una sola prueba:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_event_bus.py -v
```

**Cómo ejecutar las que contengan una palabra:**

```powershell
.\.venv\Scripts\python.exe -m pytest -k sincron -v
```

---

### 8.42 `scripts/generate_sound.py` — generar el WAV

**Propósito:** crear `assets/sounds/success.wav` sin depender de un archivo externo.

| Líneas | Explicación |
|---|---|
| 13 | Frecuencia de muestreo: 44 100 Hz. |
| 14 | Duración: 0.62 s. |
| 15-19 | Tres notas: C5 (523.25 Hz), G5 (783.99 Hz) y C6 (1046.50 Hz), con sus tiempos de inicio y duración. |
| 22-23 | `generar(destino)`: acumula muestras. |
| 24 | `total`: muestras totales. |
| 25-35 | Bucle por muestra: suma cada nota activa con una envolvente de ataque rápido (`min(1, local/0.008)`) y caída exponencial (`exp(-4*local)`); añade un armónico al doble de frecuencia; limita a [-1, 1] y convierte a entero de 16 bits. |
| 37-42 | Crea la carpeta, abre el WAV, configura mono, 16 bits, 44.1 kHz y escribe las muestras con `struct.pack("<%dh")` (little-endian, enteros con signo). |
| 45-48 | Punto de entrada: ruta final y mensaje con el tamaño. |

**Qué es una envolvente:** una función que sube y baja el volumen. Sin ella, el sonido empezaría y terminaría con un clic (salto brusco). La envolvente de ataque de 8 ms y la caída exponencial hacen que suene como una campana suave.

**Por qué tres notas:** forman un arpegio ascendente (C5–G5–C6) que suena "de éxito". La tercera dura más y se solapa con las anteriores.

**Formato:** PCM mono de 16 bits. Es el más compatible con `flet-audio` y con cualquier reproductor.

---

### 8.43 `scripts/capture_ui.py` — capturas de la interfaz real

**Propósito:** sembrar una base de demostración, abrir la app, navegar por las pantallas y guardar seis PNG en `artifacts/`. Es una herramienta de desarrollo, no parte de la app.

| Líneas | Explicación |
|---|---|
| 1-9 | Docstring con uso y advertencia: se usa captura del sistema porque el modo de captura de Flet maximiza la ventana en Windows. |
| 13-25 | Imports y ajuste de `sys.path` para poder importar `src` al ejecutar el script desde cualquier carpeta. |
| 27-28 | `flet` y `PIL.ImageGrab`. |
| 30-42 | Imports de servicios, repositorios, prioridad, bus y base. |
| 44-45 | `DESTINO = artifacts/` y título de la ventana. |
| 47-50 | Activa DPI awareness en Windows para que las coordenadas de la ventana coincidan con los píxeles reales en pantallas escaladas. |
| 54-133 | `sembrar_demo(db)`: crea un bus y los servicios; crea tres proyectos (lanzamiento web, mudanza, curso); crea seis tareas (una completada); crea tres notas. |
| 137-144 | `_rect_ventana()`: busca la ventana por título, la trae al frente y obtiene su rectángulo. |
| 147-162 | `_capturar(nombre)`: mueve el cursor fuera (para que un tooltip no salga en la foto), espera, obtiene el rectángulo, captura con `ImageGrab` y guarda. |
| 165-216 | `capturar(page)`: espera a que la ventana esté lista, trae al frente, captura tareas, navega a proyectos y notas, abre diálogos, captura y cierra la ventana. |
| 219-223 | `main(page)`: llama al `main` real de la app y agenda `capturar`. |
| 226-241 | Punto de entrada: en Windows mata procesos `flet.exe` viejos; usa una base temporal `caos_demo_ui.db`; la borra si existe; siembra; cierra; ejecuta Flet. |

**Por qué se mata `flet.exe`:** si quedó una ventana de una ejecución anterior, `FindWindowW` podría encontrar la ventana equivocada y capturar una pantalla vieja.

**Por qué se usa una base temporal:** no se debe llenar la base real del usuario con datos de demostración. `CAOS_DB_PATH` apunta a `%TEMP%\caos_demo_ui.db`.

**Por qué `os._exit(0)` (línea 216):** tras cerrar la ventana, el proceso de Flet podría quedarse vivo. `os._exit` fuerza la salida para que el script termine y no deje procesos colgados. Es agresivo, pero adecuado para una herramienta de captura.

**Limitación:** usa `ctypes` y `ImageGrab`, así que está pensado para Windows. En macOS/Linux habría que adaptar la detección de ventana.

---

### 8.44 `tests/test_auto_sync.py` — sincronizador automático (18 pruebas)

**Propósito:** comprobar el bucle automático, el debounce por cambios locales, la pasada final al cerrar y la integración real con `SyncService`, sin abrir Flet y sin red real ni Turso.

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 104-108 | `test_sin_credenciales_no_hace_nada` | Sin URL/token no se intenta sincronizar. |
| 111-115 | `test_sin_internet_no_llama_a_turso` | Si la sonda dice que no hay red, no se llama al servicio. |
| 118-129 | `test_sincroniza_y_publica_eventos` | Sincroniza con `publicar_eventos=False` y publica los eventos desde el propio `AutoSync`. |
| 132-139 | `test_sin_cambios_no_publica_eventos` | Una pasada sin cambios no ensucia el bus. |
| 142-151 | `test_si_otra_sincronizacion_esta_en_curso_no_publica` | Si el candado está ocupado (`None`), no publica nada. |
| 154-162 | `test_error_de_sincronizacion_se_registra_y_no_propaga` | Un `CaosError` se registra y no tumba la app. |
| 165-176 | `test_iniciar_programa_el_bucle_y_escucha_cambios` | `iniciar` programa el bucle, registra el lifecycle y se suscribe a `DATOS_CAMBIADOS`; `detener` se desuscribe. |
| 179-200 | `test_reanudar_pide_sincronizar_y_pausar_hace_pasada_final` | `RESUME` pide otra pasada y `PAUSE` programa la final. |
| 203-218 | `test_cambio_local_programa_una_sincronizacion_con_debounce` | Publicar `DATOS_CAMBIADOS` programa una tarea que sube los pendientes. |
| 221-233 | `test_cambio_local_sin_pendientes_no_sincroniza` | Si no hay pendientes, el debounce no llama a Turso. |
| 236-249 | `test_varios_cambios_seguidos_reinician_el_debounce` | Un segundo cambio cancela la tarea anterior y programa otra. |
| 251-267 | `test_pasada_final_espera_el_candado` | La pasada final llama a `sincronizar_si_libre` con `timeout=7.5`. |
| 270-289 | `test_escritorio_intercepta_el_cierre_y_sincroniza_antes_de_destruir` | En Windows activa `prevent_close`, escucha `CLOSE`, sincroniza y destruye la ventana. |
| 292-299 | `test_movil_no_intercepta_el_cierre_de_ventana` | En Android no toca `prevent_close` ni `on_event`. |
| 302-303 | `test_solicitar_antes_de_iniciar_no_falla` | `solicitar()` es seguro aunque la página aún no exista. |
| 306-309 | `test_intervalo_minimo_para_no_gastar_bateria` | Un intervalo de 1 s se eleva al mínimo de 30 s. |
| 312-313 | `test_espera_inicial_corta_para_subir_cambios_pronto` | La espera inicial es 1 s, no 6. |
| 324-344 | `test_un_cambio_local_real_se_sube_con_el_debounce` | Integración real: `TareaService` crea una tarea, el bus publica `DATOS_CAMBIADOS`, el debounce ejecuta `SyncService` y el pendiente baja a 0. |

**`FakePage` (líneas 77-92):** implementa `run_task` (guarda las corrutinas en una lista y devuelve un `FakeFuture` con `cancel()`), `update()` y una `FakeWindow` con `prevent_close`, `on_event` y `destroy()` asíncrono. Así se verifica la programación y el cierre sin un bucle de eventos real.

**`FakeSync` (líneas 18-36):** registra si se pidió publicar eventos, los `timeout` usados, los pendientes y devuelve un `ResultadoSync` prefijado. `FakeBus` (39-56) apunta los temas publicados y permite suscribir/desuscribir. `FakeTurso` (316-322) devuelve tres listas vacías para el *pull*. Con estos dobles, las pruebas son rápidas y deterministas; la última usa la base SQLite temporal de `conftest.py` para comprobar el camino completo.

---

### 8.45 `tests/test_connectivity.py` — sonda de Internet (3 pruebas)

| Líneas | Prueba | Qué demuestra |
|---|---|---|
| 17-24 | `test_hay_internet_ok` | Si el primer destino acepta la conexión, devuelve `True`. |
| 27-33 | `test_hay_internet_falla_si_no_hay_red` | Si todos los destinos lanzan `OSError`, devuelve `False`. |
| 36-48 | `test_hay_internet_prueba_el_segundo_destino` | Si el primero falla, prueba el segundo y lo registra en orden. |

**Cómo se evita la red real:** `monkeypatch.setattr(connectivity.socket, "create_connection", ...)` sustituye la función por un doble. No se abre ningún socket de verdad.

---

## 9. El esquema SQL explicado

El esquema local está en `src/shared/infrastructure/database.py:11-61`. Vamos a leerlo como si fuera la primera vez que ves SQL.

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
```

- **`PRAGMA`**: instrucción especial de SQLite (no es SQL estándar).
- **`journal_mode = WAL`**: en vez de escribir directamente sobre el archivo principal, SQLite escribe en `caos_local.db-wal` y luego consolida. Permite leer mientras se escribe y es más seguro ante cierres inesperados.
- **`foreign_keys = ON`**: activa la comprobación de claves foráneas. Sin esto, `deadline_id` podría apuntar a un proyecto inexistente.

### Tabla `deadlines`

```sql
CREATE TABLE IF NOT EXISTS deadlines (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    descripcion   TEXT NOT NULL DEFAULT '',
    fecha_limite  TEXT,
    area          TEXT NOT NULL DEFAULT 'General',
    completado    INTEGER NOT NULL DEFAULT 0,
    deleted       INTEGER NOT NULL DEFAULT 0,
    synced        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
```

| Columna | Tipo | Por qué |
|---|---|---|
| `id` | `TEXT PRIMARY KEY` | UUID v4 como texto. `PRIMARY KEY` impide duplicados. |
| `titulo` | `TEXT NOT NULL` | Obligatorio. |
| `descripcion` | `TEXT NOT NULL DEFAULT ''` | Nunca `NULL`; vacío por defecto. |
| `fecha_limite` | `TEXT` | Puede ser `NULL`; si existe, es `AAAA-MM-DD`. |
| `area` | `TEXT NOT NULL DEFAULT 'General'` | Siempre hay área. |
| `completado` | `INTEGER NOT NULL DEFAULT 0` | SQLite no tiene booleanos; 0 = no, 1 = sí. |
| `deleted` | `INTEGER NOT NULL DEFAULT 0` | Borrado lógico. |
| `synced` | `INTEGER NOT NULL DEFAULT 0` | 0 = pendiente de subir. |
| `created_at` | `TEXT NOT NULL` | ISO 8601 con zona horaria. |
| `updated_at` | `TEXT NOT NULL` | Se actualiza en cada cambio. |

### Tabla `tareas`

```sql
CREATE TABLE IF NOT EXISTS tareas (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    descripcion   TEXT NOT NULL DEFAULT '',
    prioridad     INTEGER NOT NULL,
    completada    INTEGER NOT NULL DEFAULT 0,
    deadline_id   TEXT REFERENCES deadlines(id) ON DELETE SET NULL,
    deleted       INTEGER NOT NULL DEFAULT 0,
    synced        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
```

| Columna | Detalle |
|---|---|
| `prioridad` | `INTEGER NOT NULL`: 1–4. El modelo valida el rango antes de guardar. |
| `completada` | 0/1. |
| `deadline_id` | `NULL` = tarea suelta; si tiene valor, debe existir en `deadlines.id`. `ON DELETE SET NULL` pondría `NULL` si se borrara físicamente el proyecto. |

### Tabla `notas`

```sql
CREATE TABLE IF NOT EXISTS notas (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    contenido     TEXT NOT NULL DEFAULT '',
    area          TEXT NOT NULL DEFAULT 'General',
    deadline_id   TEXT REFERENCES deadlines(id) ON DELETE SET NULL,
    deleted       INTEGER NOT NULL DEFAULT 0,
    synced        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
```

Es similar a tareas, pero sin estado ni prioridad, y con `contenido` en vez de `descripcion`.

### Índices

```sql
CREATE INDEX IF NOT EXISTS idx_tareas_deadline   ON tareas(deadline_id);
CREATE INDEX IF NOT EXISTS idx_tareas_synced     ON tareas(synced);
CREATE INDEX IF NOT EXISTS idx_tareas_completada ON tareas(completada);
CREATE INDEX IF NOT EXISTS idx_deadlines_synced  ON deadlines(synced);
CREATE INDEX IF NOT EXISTS idx_notas_synced      ON notas(synced);
CREATE INDEX IF NOT EXISTS idx_notas_deadline    ON notas(deadline_id);
```

Un **índice** es como el índice de un libro: permite encontrar filas sin recorrer toda la tabla.

- `idx_tareas_deadline`: acelera `list_by_deadline`.
- `idx_tareas_synced`: acelera `list_pending`.
- `idx_tareas_completada`: acelera el filtro de pendientes.
- `idx_deadlines_synced` y `idx_notas_synced`: aceleran el conteo de pendientes.
- `idx_notas_deadline`: acelera las notas de un proyecto.

**Coste:** cada índice ocupa espacio y hace un poco más lenta la escritura. Para esta app, el beneficio en lectura es mayor.

### `PRAGMA user_version = 1`

Guarda un número de versión del esquema. No se usa todavía, pero es la base para futuras migraciones:

```python
version = db.query_one("PRAGMA user_version")[0]
if version < 2:
    db.execute("ALTER TABLE tareas ADD COLUMN etiquetas TEXT NOT NULL DEFAULT ''")
    db.execute("PRAGMA user_version = 2")
```

### Mapa entidad → tabla

| Entidad | Tabla | Campos propios |
|---|---|---|
| `Deadline` | `deadlines` | título, descripción, fecha_límite, área, completado |
| `Tarea` | `tareas` | título, descripción, prioridad, completada, deadline_id |
| `Nota` | `notas` | título, contenido, área, deadline_id |
| `Entity` (común) | las tres | id, deleted, synced, created_at, updated_at |

### Reglas de conversión

| Python | SQLite | Al recuperar |
|---|---|---|
| `str` | `TEXT` | `row["..."]` |
| `int` | `INTEGER` | `int(...)` |
| `bool` | `INTEGER` 0/1 | `bool(...)` |
| `date` | `TEXT` ISO | `date.fromisoformat(...)` |
| `datetime` | `TEXT` ISO | `datetime.fromisoformat(...)` |
| `None` | `NULL` | `None` |

**Por qué no se usan tipos nativos de fecha:** SQLite no tiene un tipo `DATE` real; acepta texto, números o `NULL`. Guardar ISO es portable, legible y ordenable.

---

## 10. La sincronización con Turso paso a paso

### 10.1 El viaje completo de una fila

1. **La creas offline.** `Tarea` nace con `synced=False`.
2. **Se guarda en SQLite.** El repositorio escribe `synced=0`.
3. **Editas o completas.** `_touch()` pone `synced=0` otra vez.
4. **Pulsas la nube, cambias algo o llega el turno automático.** `SyncService.sincronizar()` llama a `list_pending()` en los tres repositorios; la automática hace lo mismo con `sincronizar_si_libre()` tras el debounce, en el bucle o en la pasada final.
5. **Se construye el pipeline.** Primero las tres sentencias de esquema, luego deadlines, luego tareas, luego notas.
6. **Se envía una sola petición HTTP** a `https://<tu-base>/v2/pipeline`.
7. **Turso ejecuta en orden.** Si todo va bien, responde con resultados `ok`.
8. **Se marca `synced=1` en local** para los ids enviados.
9. **Se aplican las filas del pull** y se avisa a la UI.
10. **La UI muestra "Listo. N registros sincronizados."** (manual) o actualiza el contador en silencio (automática).

### 10.2 Ejemplo simplificado del payload

```json
{
  "requests": [
    {
      "type": "execute",
      "stmt": {
        "sql": "INSERT INTO tareas (id, titulo, ...) VALUES (?, ?, ...) ON CONFLICT(id) DO UPDATE SET ...",
        "args": [
          {"type": "text", "value": "550e8400-e29b-41d4-a716-446655440000"},
          {"type": "text", "value": "Comprar pan"},
          {"type": "integer", "value": "1"},
          {"type": "null"}
        ]
      }
    },
    {"type": "close"}
  ]
}
```

La cabecera incluye:

```
Authorization: Bearer <TURSO_AUTH_TOKEN>
Content-Type: application/json
```

### 10.3 Garantías del código actual

- **No se marca nada como sincronizado si la petición falla.** `mark_synced` está después de `ejecutar`.
- **Los borrados viajan en ambos sentidos.** `list_pending` incluye `deleted=1` y el *pull* aplica los borrados remotos.
- **El orden respeta la dependencia lógica.** Deadlines antes que tareas y notas, tanto al subir como al bajar.
- **Siempre se consulta la nube.** Aunque no haya pendientes, el pipeline incluye las tres lecturas del *pull*.
- **La primera sincronización crea las tablas.** El pipeline incluye `CREATE TABLE IF NOT EXISTS`.

### 10.4 Limitaciones que debes conocer

- **Solo con la app abierta:** la sincronización automática sube cada cambio local unos 2 segundos después, revisa la red cada 120 segundos (mínimo 30) y hace una pasada final al pasar a segundo plano o cerrar. No hay un servicio Android que siga funcionando con la app cerrada: si Android la mata sin avisar, los cambios pendientes se suben en el siguiente arranque.
- **Sonda de red aproximada:** `connectivity.py` solo comprueba que se pueda abrir un TCP a `1.1.1.1:443` o `8.8.8.8:443`. Una red cautiva puede dejar pasar esa conexión y bloquear Turso; en ese caso la sincronización falla y se reintenta en la vuelta siguiente.
- **Last-write-wins:** si dos dispositivos editan la misma fila, gana la que tenga el `updated_at` más reciente. No hay fusión campo por campo ni detección de ediciones simultáneas.
- **Relojes:** la comparación de fechas asume que los dispositivos tienen la hora razonablemente correcta. Un reloj muy desfasado puede hacer que una versión vieja parezca nueva.
- **Un pipeline grande:** si tienes miles de pendientes, el cuerpo de la petición puede crecer mucho. Para esta versión se asume un uso personal.
- **Sin `BEGIN`/`COMMIT` explícito:** el pipeline se envía como una sola petición y se interpreta como una unidad. Si quisieras atomicidad estricta ante fallos parciales, podrías envolver las sentencias en una transacción y hacer `COMMIT` al final. Es una mejora posible, no algo que el código actual garantice al 100 %.

### 10.5 Cómo probar la sincronización sin Turso

Las pruebas usan `FakeTurso`:

```python
class FakeTurso:
    def __init__(self, configurado=True, filas=None):
        self.configurado = configurado
        self.llamadas = []
        self.filas = filas or {"deadlines": [], "tareas": [], "notas": []}

    def ejecutar(self, sentencias):
        self.llamadas.append([(sql, tuple(params)) for sql, params in sentencias])
        return [self.filas["deadlines"], self.filas["tareas"], self.filas["notas"]]
```

Así se verifica el orden, los parámetros, el marcado y el *pull* sin hacer red. Si quieres probar contra Turso real, configura las variables de entorno (o las credenciales desde el diálogo) y pulsa el botón; revisa el log `Sincronización completada: N enviados, M recibidos`.

**Probar la automática sin esperar:** `tests/test_auto_sync.py` usa `FakeSync`, `FakeBus`, `FakePage` y `FakeWindow` para verificar el bucle, el debounce, la pasada final, el cierre de escritorio, la sonda y la publicación de eventos. `tests/test_connectivity.py` sustituye `socket.create_connection` por dobles. Para una prueba manual, abre la app con credenciales, espera ~1 segundo y mira el log: debe aparecer `Sincronización automática activa cada 120 segundos`. Después crea una tarea y, sin tocar nada, debería subirse en ~2 segundos.

---

## 11. Cómo añadir una funcionalidad nueva

### 11.1 Añadir un campo a una entidad existente

Ejemplo: añadir `etiquetas` a `Tarea`.

1. **Modelo** (`src/domains/tareas/models/tarea.py`):
   - añade el campo en la dataclass,
   - normalízalo en `__post_init__`,
   - añádelo a `actualizar` con `SIN_CAMBIO`.
2. **Esquema local** (`database.py`):
   - añade la columna al `CREATE TABLE` (para bases nuevas),
   - y una migración para bases existentes (`ALTER TABLE ... ADD COLUMN`).
3. **Repositorio** (`sqlite_tarea_repository.py`):
   - añade la columna a `_COLUMNAS` y al `_UPSERT`,
   - añade el valor en `_params`,
   - recupéralo en `_fila_a_entidad`.
4. **Sincronización** (`sync_service.py`):
   - añade la columna al esquema remoto y al `UPSERT_TAREA`,
   - añade el valor en la tupla de parámetros.
5. **Vista** (`tareas_view.py`):
   - añade el campo al diálogo y pásalo a `crear`/`editar`.
6. **Pruebas**:
   - modelo: valor por defecto, normalización,
   - repositorio: roundtrip,
   - sync: el parámetro llega en la posición correcta.

> **Cuidado con el orden de los parámetros.** `_params`, el `_UPSERT` y el esquema remoto deben tener exactamente el mismo orden. Un desfase guarda datos en la columna equivocada sin lanzar error. Las pruebas de roundtrip y de sync son tu red de seguridad.

### 11.2 Añadir un dominio nuevo (por ejemplo, `habitos`)

1. Crea `src/domains/habitos/` con `models/`, `application/`, `infrastructure/`, `presentation/` y sus `__init__.py`.
2. Define la entidad heredando de `Entity`.
3. Define el puerto `HabitoRepository(Protocol)`.
4. Implementa `SqliteHabitoRepository`.
5. Crea `HabitoService` con sus casos de uso y publica `HABITOS_CAMBIADOS` + `DATOS_CAMBIADOS`.
6. Añade el tema de evento en `events.py` y a `TODOS_LOS_TEMAS`.
7. Crea la tabla en `database.py` y en el esquema remoto de `sync_service.py`.
8. Añade el repositorio al `AppContext`.
9. Crea `HabitosView` y añádela a `AppShell._vistas` y a la `NavigationBar`.
10. Añade pruebas y actualiza el README.

### 11.3 Añadir una validación

Si la regla es común a tareas, deadlines y notas, va en `Titulo` o en `Entity`. Si es específica, va en el `__post_init__` o en `actualizar` de esa entidad.

Ejemplo: impedir títulos que empiecen por un espacio. En `Titulo.__post_init__`, después de limpiar:

```python
if limpio != limpio.lstrip():
    raise ErrorDeValidacion("El título no puede empezar con espacios.")
```

Pero como ya limpias con `split/join`, esa condición nunca se cumpliría. La limpieza normaliza en vez de rechazar, que suele ser más amable.

### 11.4 Añadir una acción a la UI

1. Añade el botón en el constructor de la vista.
2. Crea el método que llama al servicio.
3. Captura `CaosError` y muestra `avisar(...)`.
4. No refresques a mano si el servicio publica eventos; la vista se actualizará sola.
5. Añade una prueba del caso de uso.

---

## 12. Problemas conocidos y cómo depurarlos

### La app no arranca y muestra "No se pudo abrir la base de datos local"

- Revisa que la carpeta de `CAOS_DB_PATH` exista o que puedas crearla.
- Comprueba permisos de escritura.
- Si la base está corrupta, renómbrala y arranca de nuevo (perderás los datos locales).
- En Windows, verifica que no haya otro proceso bloqueando el archivo.

### `database is locked`

- SQLite espera hasta 5 segundos (`busy_timeout`). Si persiste, otro proceso está escribiendo.
- Cierra otras instancias de la app.
- No uses la misma base desde dos procesos a la vez.

### El audio no suena

- `flet-audio` puede no estar disponible en la plataforma; el código cae a `winsound.Beep` en Windows.
- En macOS/Linux el fallback imprime `\a` (campana del terminal), que puede estar silenciada.
- Verifica que `assets/sounds/success.wav` exista. Si falta, regenera con `python scripts/generate_sound.py`.
- En Android, revisa que el paquete `flet-audio` esté incluido en el build.

### Aparece un rectángulo gris en las tarjetas de tarea

Era el bug de `expand=True` dentro de un `Row(wrap=True)`. Ya está corregido en `tareas_view.py:251-262`: la descripción va en su propia línea, no dentro del `Row` de metadatos. Si vuelve a aparecer, revisa que ningún control expandible esté dentro de una fila con `wrap`.

También puede aparecer un rectángulo gris si un `ft.Icon` recibe un texto en vez de una constante. En Flet 1.1, `ft.Icon("task_alt")` **no lanza un error en Python**, pero el cliente Flutter no puede interpretarlo y dibuja su marcador gris de error en lugar del contenido. Usa siempre `ft.Icons.TASK_ALT` (o `ft.CupertinoIcons.*`), nunca el nombre como string. Ocurrió justo eso en los estados vacíos de tareas, proyectos y notas; se corrigió en `tareas_view.py:194-200`, `deadlines_view.py:77-83` y `notas_view.py:92-98`.

### `can't subtract offset-naive and offset-aware datetimes`

Ocurre al restar un `datetime` con zona horaria y otro sin ella. La solución está en `widgets.py:62`: `datetime.now(momento.tzinfo)`. Si añades código de fechas, mantén siempre `tzinfo` o usa `date` para comparaciones de día.

### `page` es `None` al llamar a `update()`

La vista se construyó antes de estar montada. El código defensivo `if self.page is not None` evita el error. Si escribes una vista nueva, usa el mismo patrón.

### La sincronización dice "Turso no configurado"

Abre el diálogo de sincronización (icono de nube) y escribe la URL y el token en los campos de abajo. Pulsa **Probar conexión** y luego **Guardar**.

- En Android esta es la única forma: no existen variables de entorno.
- En escritorio también puedes definirlas **antes** de abrir la app:

```powershell
$env:TURSO_DATABASE_URL = "libsql://..."
$env:TURSO_AUTH_TOKEN = "..."
```

`TURSO_DATABASE_URL` acepta `libsql://` o `https://`; se normaliza sola.

Si ya las guardaste y sigue apareciendo el mensaje, revisa que no hayas dejado un campo vacío y vuelve a pulsar **Guardar**. Las credenciales quedan en la tabla `settings` de la base local, no en la nube.

### Turso responde HTTP 401

El token es inválido, expiró o no corresponde a esa base. Genera uno nuevo en el panel de Turso.

### La sincronización automática no hace nada

Revisa en este orden:

1. **Credenciales:** abre el icono de nube. Si dice "Turso no configurado", guarda URL y token.
2. **Internet:** la sonda abre un TCP a `1.1.1.1:443` y `8.8.8.8:443`. En una red que bloquee esas IPs, la automática se salta la pasada aunque Turso fuera accesible. Puedes probar el botón manual para confirmar que Turso responde.
3. **Log:** con la app abierta deben aparecer `Sincronización automática activa cada 120 segundos` y, si no hay red, `Sin Internet; se reintentará...`. En Android, revisa el log con `adb logcat`.
4. **Tiempo:** la primera pasada espera 1 segundo y luego hay que esperar hasta 120. Además, crear/editar/borrar dispara una subida ~2 segundos después. Guardar credenciales o volver del segundo plano fuerza una pasada inmediata.
5. **Cierre:** si creaste algo y cerraste la app de inmediato, la pasada final lo sube antes de salir. Si el cierre se quedó sin red, el cambio sigue pendiente y se sube al volver a abrir.

La automática no corre con la app cerrada: no es un servicio Android en segundo plano. Si Android mata la app sin avisar, el cambio pendiente se sube en el siguiente arranque.

### `flet build apk` falla compilando PyYAML

Es un problema del toolchain en Python muy nuevo (por ejemplo 3.15) sin compilador de C++. Opciones:

- instalar Python 3.12/3.13 para compilar el APK,
- instalar Microsoft C++ Build Tools,
- o usar la app de escritorio, que no necesita `flet-cli`.

### Las pruebas fallan por una base contaminada

Las fixtures usan `tmp_path`, así que no deberían. Si ejecutas pruebas manuales con `CAOS_DB_PATH`, asegúrate de que apunte a una base temporal, no a la real.

### Quiero ver qué SQL se ejecuta

Añade temporalmente:

```python
import logging
logging.getLogger("caos").setLevel(logging.DEBUG)
```

O revisa el archivo con una herramienta como DB Browser for SQLite. La base está en `~/.caos/caos_local.db` (o la ruta que hayas configurado).

### Quiero reiniciar la app desde cero

Cierra la app y borra `caos_local.db`, `caos_local.db-wal` y `caos_local.db-shm`. Al arrancar se crean de nuevo. **Esto borra todos tus datos locales.**

---

## 13. Mapa rápido de archivos y líneas

| Archivo | Líneas clave | Para qué |
|---|---|---|
| `main.py` | 21-71 | Arranque, base, contexto, `SafeArea`, shell y auto-sync. |
| `src/shared/domain/entity.py` | 20-41 | UUID, fechas, `synced`, `deleted`. |
| `src/shared/domain/errors.py` | 6-27 | Jerarquía de errores. |
| `src/shared/domain/value_objects.py` | 12-29 | Título válido. |
| `src/shared/application/event_bus.py` | 15-40 | Pub/sub. |
| `src/shared/application/events.py` | 3-16 | Temas, incluido `SYNC_CAMBIADO`. |
| `src/shared/application/sync_service.py` | 22-140, 194-359 | Esquema, upserts, pull, candado, conflictos y eventos. |
| `src/shared/application/auto_sync.py` | 29-290 | Bucle, debounce, pasada final, cierre de escritorio, sonda y eventos. |
| `src/shared/infrastructure/database.py` | 11-66, 69-87, 90-161 | Esquema, ruta y conexión. |
| `src/shared/infrastructure/connectivity.py` | 14-29 | Sonda TCP de Internet. |
| `src/shared/infrastructure/settings_repository.py` | 14-62 | Credenciales guardadas en el dispositivo. |
| `src/shared/infrastructure/turso_client.py` | 41-169 | Pipeline HTTP y lectura de filas. |
| `src/shared/presentation/theme.py` | 20-36 | Tema y ventana. |
| `src/shared/presentation/widgets.py` | 52-221 | Componentes visuales. |
| `src/shared/presentation/effects.py` | 26-91 | Sonido y animación. |
| `src/shared/presentation/app_context.py` | 28-79 | Composition root. |
| `src/shared/presentation/shell.py` | 174-213, 216-456 | Navegación, progreso, sync manual y credenciales. |
| `src/domains/tareas/models/tarea.py` | 24-102 | Reglas de tarea. |
| `src/domains/tareas/models/value_objects.py` | 14-58 | Eisenhower. |
| `src/domains/tareas/application/tarea_service.py` | 45-146 | Casos de uso. |
| `src/domains/tareas/infrastructure/sqlite_tarea_repository.py` | 18-141 | SQL de tareas. |
| `src/domains/tareas/presentation/tareas_view.py` | 44-366 | UI de tareas. |
| `src/domains/deadlines/models/deadline.py` | 23-103 | Reglas de proyecto. |
| `src/domains/deadlines/application/deadline_service.py` | 50-147 | Casos de uso y progreso. |
| `src/domains/deadlines/infrastructure/sqlite_deadline_repository.py` | 17-129 | SQL de proyectos. |
| `src/domains/deadlines/presentation/deadlines_view.py` | 68-343 | UI de proyectos. |
| `src/domains/notas/models/nota.py` | 21-72 | Reglas de nota. |
| `src/domains/notas/application/nota_service.py` | 18-80 | Casos de uso. |
| `src/domains/notas/infrastructure/sqlite_nota_repository.py` | 17-131 | SQL de notas. |
| `src/domains/notas/presentation/notas_view.py` | 40-265 | UI de notas. |
| `tests/conftest.py` | 21-61 | Fixtures. |
| `scripts/capture_ui.py` | 54-241 | Capturas. |
| `scripts/generate_sound.py` | 13-48 | Sonido. |

---

## 14. Ejercicios para practicar

### Ejercicio 1: cambia el color de acento

Abre `src/shared/presentation/theme.py:11` y cambia `COLOR_ACENTO` por otro hexadecimal. Ejecuta la app. Observa cuántos sitios cambian sin tocar nada más. **Objetivo:** entender la ventaja de centralizar constantes.

### Ejercicio 2: añade una prioridad por defecto distinta

En `Tarea.__post_init__`, cambia la prioridad por defecto. ¿Qué pruebas fallan? Ajusta `test_prioridad_por_defecto_es_eisenhower_1` para que refleje la nueva regla. **Objetivo:** entender que las pruebas documentan el comportamiento esperado.

### Ejercicio 3: muestra el área en la tarjeta de tarea

En `tareas_view.py`, añade un chip con el área del proyecto vinculado. Pista: ya tienes `deadline` en las líneas 237-245; usa `deadline.area`. **Objetivo:** practicar la composición de widgets y el acceso a datos ya cargados.

### Ejercicio 4: añade un filtro "P1"

En `tareas_view.py`, añade un cuarto segmento al `SegmentedButton` y filtra por `tarea.prioridad is Prioridad.IMPORTANTE_URGENTE`. **Objetivo:** practicar estado de UI y filtrado en memoria.

### Ejercicio 5: escribe una prueba nueva

Crea en `tests/test_tarea_model.py` una prueba que verifique que una descripción con espacios se limpia. Pista: `Tarea(titulo="X", descripcion="  hola  ").descripcion == "hola"`. **Objetivo:** perder el miedo a pytest y a las fixtures.

### Ejercicio 6: simula un fallo de red

En `tests/test_sync_service.py`, crea un `FakeTurso` cuyo `ejecutar` lance `RuntimeError` y comprueba que `list_pending()` sigue teniendo el registro. Ya existe una prueba así; escríbela desde cero sin mirar. **Objetivo:** interiorizar la garantía "no marcar si falla".

### Ejercicio 7: añade una nota rápida

En `NotasView`, añade un botón que cree una nota con título "Idea rápida" y contenido vacío. ¿Qué capa tocaste? Solo presentación y caso de uso. **Objetivo:** comprobar que la arquitectura permite añadir acciones sin tocar SQL.

---

## Resumen final

Ya conoces el proyecto completo:

- **`models/`** contiene las reglas y no sabe nada de Flet ni SQLite.
- **`application/`** orquesta casos de uso, valida existencia y publica eventos.
- **`infrastructure/`** implementa los puertos con SQLite y Turso.
- **`presentation/`** dibuja la UI y llama a los casos de uso.
- **`AppContext`** es el único lugar donde se ensambla todo.
- **`EventBus`** desacopla las vistas.
- **`synced` y `deleted`** hacen posible el offline-first.
- **Turso** recibe un pipeline ordenado y solo se marca `synced=1` si todo salió bien.

Si entiendes el recorrido "clic → caso de uso → modelo → repositorio → SQLite → evento → vista", entiendes el 80 % de la app. El resto son detalles de Flet y de SQL que ya puedes consultar en las secciones anteriores.

**Siguiente paso recomendado:** abre `src/domains/tareas/presentation/tareas_view.py` junto a este documento y sigue el recorrido de la sección 6.1 señalando cada línea. Después haz el ejercicio 5. Aprenderás más escribiendo una prueba pequeña que leyendo diez páginas.
