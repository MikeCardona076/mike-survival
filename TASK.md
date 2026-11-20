# MISIÓN

Construye un videojuego completo, jugable y publicable en GitHub, llamado
"MIKE: SEÑAL DE SUPERVIVENCIA". Es un survival roguelite 2D en pixel art,
mundo abierto procedural, donde el jugador NO controla al personaje:
coordina vía chat a "Mike", un agente autónomo que corre sobre la API de
DeepSeek con function calling.

Trabajas como ingeniero senior. Entregas código funcional, no prototipos.
Cada fase termina con algo ejecutable y verificable. Commits atómicos y
mensajes claros. No avanzas de fase sin cumplir los criterios de
aceptación.

# CONTEXTO NARRATIVO (para que el código refleje la historia)

Mike, 34 años, paramédico. Sobrevive en una ciudad post-apocalíptica.
Su hija Elena, 12 años, fue evacuada al Refugio 7 hace tres meses.
Mike fue mordido el día 47 y resultó inmune, pero el virus "despierta"
en oleadas: si la infección llega a 100, pierde el control 10 segundos.
Necesita supresores para mantenerse estable.

El jugador es el "Operador": un superviviente con acceso a cámaras y
mapas que Mike no puede ver. La comunicación es por radio con batería
limitada. Cada mensaje cuesta 1-3%.

# STACK OBLIGATORIO

- Python 3.12
- pygame-ce (no pygame clásico)
- SQLite vía stdlib `sqlite3` (sin ORMs externos)
- openai SDK (compatible DeepSeek: `base_url="https://api.deepseek.com"`)
- noise (Perlin/Simplex)
- Pillow (sprites procedurales si SpriteKiln no está disponible)
- docker + docker-compose (distribución)
- pytest (tests de lógica pura)
- ruff + black (lint/format)

Modelo de IA: `deepseek-flash` (FIJO, el más barato). Modo non-thinking
por defecto (`reasoning_effort="none"` o
`extra_body={"thinking": {"type": "disabled"}}`). Nunca `deepseek-v4-pro`.

NO uses: Django, Flask, FastAPI, TensorFlow, PyTorch, ORMs, ni
dependencias no listadas. Si dudas, pregunta.

# ESTRUCTURA DEL REPO

mike-survival/
├── README.md
├── LICENSE (MIT)
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── TASK.md
├── PLAN.md
├── main.py
├── config.py
├── db/
│   ├── __init__.py
│   ├── schema.sql
│   ├── database.py
│   └── repositories.py
├── game/
│   ├── __init__.py
│   ├── world.py
│   ├── entities.py
│   ├── combat.py
│   ├── inventory.py
│   ├── loop.py
│   ├── renderer.py
│   └── events.py
├── agent/
│   ├── __init__.py
│   ├── client.py
│   ├── tools.py
│   └── prompts/
│       ├── system_mike.txt
│       └── system_builder.txt
├── assets/
│   ├── __init__.py
│   ├── sprites.py
│   └── audio.py
├── ui/
│   ├── __init__.py
│   ├── chat.py
│   ├── hud.py
│   └── map.py
├── tests/
│   ├── test_world.py
│   ├── test_agent_loop.py
│   └── test_repositories.py
└── data/                       # volumen SQLite (gitignored)

# MODELO DE DATOS (SQLite)

Implementa EXACTAMENTE este esquema. Ya está validado.

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed INTEGER NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at TEXT,
    status TEXT NOT NULL DEFAULT 'alive',
    cause_of_death TEXT,
    refugio7_x INTEGER NOT NULL,
    refugio7_y INTEGER NOT NULL,
    trait TEXT NOT NULL DEFAULT 'neutral'
);

CREATE TABLE world_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    chunk_x INTEGER NOT NULL,
    chunk_y INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    data TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE,
    UNIQUE(run_id, chunk_x, chunk_y)
);

CREATE TABLE agent_state (
    run_id INTEGER PRIMARY KEY,
    health INTEGER NOT NULL DEFAULT 100,
    hunger INTEGER NOT NULL DEFAULT 0,
    thirst INTEGER NOT NULL DEFAULT 0,
    infection INTEGER NOT NULL DEFAULT 0,
    radio_battery INTEGER NOT NULL DEFAULT 100,
    pos_x REAL NOT NULL DEFAULT 0,
    pos_y REAL NOT NULL DEFAULT 0,
    inventory TEXT NOT NULL DEFAULT '[]',
    objective TEXT,
    turn_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    tool_name TEXT,
    tool_args TEXT,
    tool_call_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE SET NULL
);

CREATE TABLE assets_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_key TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    description TEXT NOT NULL,
    params TEXT,
    data BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE meta_progression (
    unlock_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    unlocked_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    runs_played INTEGER NOT NULL DEFAULT 0,
    runs_won INTEGER NOT NULL DEFAULT 0,
    total_deaths INTEGER NOT NULL DEFAULT 0,
    best_distance_to_r7 REAL NOT NULL DEFAULT 999999,
    total_playtime_seconds INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO stats (id) VALUES (1);
```
