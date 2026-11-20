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
CHUNK_PIXELS: Final[int] = CHUNK_SIZE * TILE_SIZE

# Cámara inicial: centro del chunk (0, 0).
START_CHUNK_X: Final[int] = 0
START_CHUNK_Y: Final[int] = 0
CAMERA_START_X: Final[float] = (START_CHUNK_X + 0.5) * CHUNK_PIXELS
CAMERA_START_Y: Final[float] = (START_CHUNK_Y + 0.5) * CHUNK_PIXELS

# Estado inicial de Mike.
MAX_HEALTH: Final[int] = 100
MAX_HUNGER: Final[int] = 100
MAX_THIRST: Final[int] = 100
MAX_INFECTION: Final[int] = 100
MAX_RADIO_BATTERY: Final[int] = 100
STARTING_HEALTH: Final[int] = 100

# Mundo.
REFUGIO7_RADIUS: Final[int] = 500

# Tipos de tile (los valores se guardan en world_chunks.data).
TILE_WATER: Final[int] = 0
TILE_SAND: Final[int] = 1
TILE_GRASS: Final[int] = 2
TILE_FOREST: Final[int] = 3
TILE_ROCK: Final[int] = 4

# Ruido Perlin: dos capas (elevación y humedad).
NOISE_OCTAVES: Final[int] = 4
NOISE_PERSISTENCE: Final[float] = 0.5
NOISE_LACUNARITY: Final[float] = 2.0
NOISE_SEED_MASK: Final[int] = 0xFFFF
ELEVATION_SCALE: Final[float] = 0.03
MOISTURE_SCALE: Final[float] = 0.05
MOISTURE_BASE_OFFSET: Final[int] = 7919

# Umbrales de clasificación del terreno.
ELEVATION_WATER_THRESHOLD: Final[float] = -0.18
ELEVATION_SAND_THRESHOLD: Final[float] = -0.08
ELEVATION_ROCK_THRESHOLD: Final[float] = 0.45
MOISTURE_FOREST_THRESHOLD: Final[float] = 0.0

# Paleta de terreno.
COLOR_BACKGROUND: Final[tuple[int, int, int]] = (8, 10, 12)
TILE_COLORS: Final[dict[int, tuple[int, int, int]]] = {
    TILE_WATER: (31, 58, 82),
    TILE_SAND: (156, 143, 98),
    TILE_GRASS: (72, 96, 56),
    TILE_FOREST: (42, 66, 44),
    TILE_ROCK: (94, 92, 88),
}

# Runs.
RUN_STATUS_ALIVE: Final[str] = "alive"
RUN_STATUS_DEAD: Final[str] = "dead"
DEFAULT_TRAIT: Final[str] = "neutral"
SEED_BITS: Final[int] = 31

# Agente DeepSeek.
DEEPSEEK_MODEL: Final[str] = "deepseek-flash"
DEEPSEEK_BASE_URL: Final[str] = "https://api.deepseek.com"

# Simulación por turnos.
TURN_SECONDS: Final[float] = 5.0
MAX_FRAME_DELTA: Final[float] = 0.25
HUNGER_PER_TURN: Final[int] = 2
THIRST_PER_TURN: Final[int] = 3
INFECTION_PER_TURN: Final[int] = 1
HUNGER_CRITICAL: Final[int] = 80
THIRST_CRITICAL: Final[int] = 80
STARVATION_DAMAGE: Final[int] = 2
DEHYDRATION_DAMAGE: Final[int] = 3
INFECTION_DAMAGE: Final[int] = 2

# Objetos e inventario.
ITEM_FOOD: Final[str] = "food"
ITEM_WATER: Final[str] = "water"
ITEM_SUPPRESSOR: Final[str] = "suppressor"
ITEM_BANDAGE: Final[str] = "bandage"
ITEM_SCRAP: Final[str] = "scrap"
FOOD_HUNGER_RELIEF: Final[int] = 45
WATER_THIRST_RELIEF: Final[int] = 55
BANDAGE_HEAL: Final[int] = 25
SUPPRESSOR_RELIEF: Final[int] = 40
STARTING_INVENTORY: Final[dict[str, int]] = {
    ITEM_FOOD: 2,
    ITEM_WATER: 2,
    ITEM_SUPPRESSOR: 1,
    ITEM_BANDAGE: 1,
}

# HUD.
HUD_MARGIN: Final[int] = 14
HUD_LABEL_WIDTH: Final[int] = 92
HUD_BAR_WIDTH: Final[int] = 190
HUD_BAR_HEIGHT: Final[int] = 14
HUD_ROW_HEIGHT: Final[int] = 22
HUD_FONT_SIZE: Final[int] = 18
HUD_PANEL_COLOR: Final[tuple[int, int, int]] = (18, 20, 24)
HUD_TEXT_COLOR: Final[tuple[int, int, int]] = (225, 225, 215)
HUD_BAR_BACKGROUND: Final[tuple[int, int, int]] = (52, 54, 58)
HEALTH_BAR_COLOR: Final[tuple[int, int, int]] = (190, 58, 58)
HUNGER_BAR_COLOR: Final[tuple[int, int, int]] = (200, 142, 54)
THIRST_BAR_COLOR: Final[tuple[int, int, int]] = (62, 142, 205)
INFECTION_BAR_COLOR: Final[tuple[int, int, int]] = (132, 184, 64)
BATTERY_BAR_COLOR: Final[tuple[int, int, int]] = (222, 200, 68)
