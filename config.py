"""Configuración central de MIKE: SEÑAL DE SUPERVIVENCIA.

Todas las constantes del juego viven aquí para evitar números mágicos.
Las rutas se construyen siempre con :class:`pathlib.Path`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
DATABASE_PATH: Final[Path] = Path(os.environ.get("MIKE_DATABASE_PATH", DATA_DIR / "mike.db"))
SCHEMA_PATH: Final[Path] = PROJECT_ROOT / "db" / "schema.sql"

# Ventana y render.
WINDOW_WIDTH: Final[int] = 1280
WINDOW_HEIGHT: Final[int] = 720
WINDOW_TITLE: Final[str] = "MIKE: SEÑAL DE SUPERVIVENCIA"
FPS: Final[int] = 60
TILE_SIZE: Final[int] = 16
CHUNK_SIZE: Final[int] = 32

# Estado inicial de Mike.
MAX_HEALTH: Final[int] = 100
MAX_HUNGER: Final[int] = 100
MAX_THIRST: Final[int] = 100
MAX_INFECTION: Final[int] = 100
MAX_RADIO_BATTERY: Final[int] = 100
STARTING_HEALTH: Final[int] = 100

# Mundo.
REFUGIO7_RADIUS: Final[int] = 500

# Runs.
RUN_STATUS_ALIVE: Final[str] = "alive"
RUN_STATUS_DEAD: Final[str] = "dead"
DEFAULT_TRAIT: Final[str] = "neutral"
SEED_BITS: Final[int] = 31

# Agente DeepSeek.
DEEPSEEK_MODEL: Final[str] = "deepseek-flash"
DEEPSEEK_BASE_URL: Final[str] = "https://api.deepseek.com"
