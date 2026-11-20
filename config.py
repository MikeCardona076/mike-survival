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
COLOR_BACKGROUND: Final[tuple[int, int, int]] = (10, 13, 16)
TILE_COLORS: Final[dict[int, tuple[int, int, int]]] = {
    TILE_WATER: (40, 86, 128),
    TILE_SAND: (196, 176, 118),
    TILE_GRASS: (94, 128, 68),
    TILE_FOREST: (52, 90, 56),
    TILE_ROCK: (116, 114, 106),
}
TILE_COLOR_VARIANTS: Final[dict[int, tuple[tuple[int, int, int], ...]]] = {
    TILE_WATER: ((34, 76, 116), (40, 86, 128), (46, 94, 138)),
    TILE_SAND: ((186, 166, 108), (196, 176, 118), (204, 184, 126)),
    TILE_GRASS: ((86, 118, 62), (94, 128, 68), (104, 138, 76)),
    TILE_FOREST: ((46, 82, 50), (52, 90, 56), (60, 100, 62)),
    TILE_ROCK: ((104, 102, 96), (116, 114, 106), (126, 124, 114)),
}
DECOR_TREE_DARK: Final[tuple[int, int, int]] = (28, 58, 36)
DECOR_TREE_LIGHT: Final[tuple[int, int, int]] = (68, 110, 62)
DECOR_TRUNK: Final[tuple[int, int, int]] = (86, 64, 42)
DECOR_GRASS: Final[tuple[int, int, int]] = (132, 164, 88)
DECOR_ROCK: Final[tuple[int, int, int]] = (146, 144, 134)
DECOR_SAND: Final[tuple[int, int, int]] = (224, 206, 150)
WATER_SPARKLE: Final[tuple[int, int, int]] = (132, 190, 226)
SHADOW_COLOR: Final[tuple[int, int, int]] = (18, 26, 20)
SHORE_FOAM: Final[tuple[int, int, int]] = (156, 206, 230)
DECOR_RUIN: Final[tuple[int, int, int]] = (96, 92, 84)
MIKE_RING_COLOR: Final[tuple[int, int, int]] = (232, 212, 104)
ZOMBIE_HEALTH_BACKGROUND: Final[tuple[int, int, int]] = (20, 22, 24)
ZOMBIE_HEALTH_COLOR: Final[tuple[int, int, int]] = (196, 64, 58)

# Minimapa.
MINIMAP_MARGIN: Final[int] = 14
MINIMAP_TILE: Final[int] = 7
MINIMAP_TILES: Final[int] = 21
MINIMAP_PAD: Final[int] = 8
MINIMAP_HEADER: Final[int] = 20
MINIMAP_BACKGROUND: Final[tuple[int, int, int]] = (16, 19, 24)
MINIMAP_ALPHA: Final[int] = 218
MINIMAP_BORDER: Final[tuple[int, int, int]] = (92, 110, 96)
MINIMAP_MIKE: Final[tuple[int, int, int]] = (244, 236, 196)
MINIMAP_ZOMBIE: Final[tuple[int, int, int]] = (220, 76, 66)
MINIMAP_REFUGIO: Final[tuple[int, int, int]] = (236, 204, 90)

# Runs.
RUN_STATUS_ALIVE: Final[str] = "alive"
RUN_STATUS_DEAD: Final[str] = "dead"
DEFAULT_TRAIT: Final[str] = "neutral"
SEED_BITS: Final[int] = 31

# Agente DeepSeek.
DEEPSEEK_MODEL: Final[str] = "deepseek-flash"
DEEPSEEK_BASE_URL: Final[str] = "https://api.deepseek.com"
SYSTEM_MIKE_PROMPT_PATH: Final[Path] = PROJECT_ROOT / "agent" / "prompts" / "system_mike.txt"
AGENT_MAX_TOOL_ROUNDS: Final[int] = 2
AGENT_HISTORY_LIMIT: Final[int] = 4
AGENT_TEMPERATURE: Final[float] = 0.7
AGENT_MAX_TOKENS: Final[int] = 180

# Herramientas del agente.
REST_HEAL: Final[int] = 5
SCAN_MAX_RADIUS: Final[int] = 4
WALKABLE_TILE_IDS: Final[frozenset[int]] = frozenset({TILE_SAND, TILE_GRASS, TILE_FOREST})
TILE_NAMES: Final[dict[int, str]] = {
    TILE_WATER: "agua",
    TILE_SAND: "arena",
    TILE_GRASS: "hierba",
    TILE_FOREST: "bosque",
    TILE_ROCK: "roca",
}

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
ITEM_WOOD: Final[str] = "wood"
ITEM_IRON: Final[str] = "iron"
ITEM_COIN: Final[str] = "coin"
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
SCAVENGE_ITEMS: Final[tuple[str, ...]] = (
    ITEM_FOOD,
    ITEM_WATER,
    ITEM_SUPPRESSOR,
    ITEM_BANDAGE,
    ITEM_SCRAP,
    ITEM_WOOD,
    ITEM_IRON,
)
ITEM_NAMES: Final[dict[str, str]] = {
    ITEM_FOOD: "comida",
    ITEM_WATER: "agua",
    ITEM_SUPPRESSOR: "supresor",
    ITEM_BANDAGE: "venda",
    ITEM_SCRAP: "chatarra",
    ITEM_WOOD: "madera",
    ITEM_IRON: "hierro",
    ITEM_COIN: "monedas",
}

# Economía, refugio y taller.
WOOD_PACK: Final[int] = 2
WOOD_PRICE: Final[int] = 5
IRON_PACK: Final[int] = 1
IRON_PRICE: Final[int] = 8
HEAL_PRICE: Final[int] = 10
SHELTER_MAX_LEVEL: Final[int] = 3
SHELTER_WOOD_COST: Final[int] = 6
SHELTER_IRON_COST: Final[int] = 3
SHELTER_HEALTH_BONUS: Final[int] = 10
WEAPON_MAX_LEVEL: Final[int] = 3
WEAPON_WOOD_COST: Final[int] = 4
WEAPON_IRON_COST: Final[int] = 4
WEAPON_DAMAGE_BONUS: Final[int] = 7
SHELTER_PANEL_WIDTH: Final[int] = 580
SHELTER_PANEL_HEIGHT: Final[int] = 410
SHELTER_PANEL_ALPHA: Final[int] = 240

# HUD.
HUD_MARGIN: Final[int] = 14
HUD_LABEL_WIDTH: Final[int] = 92
HUD_BAR_WIDTH: Final[int] = 190
HUD_BAR_HEIGHT: Final[int] = 14
HUD_ROW_HEIGHT: Final[int] = 22
HUD_FOOTER_HEIGHT: Final[int] = 40
HUD_FONT_SIZE: Final[int] = 18
HUD_PANEL_COLOR: Final[tuple[int, int, int]] = (18, 21, 26)
HUD_PANEL_ALPHA: Final[int] = 218
HUD_BORDER_COLOR: Final[tuple[int, int, int]] = (92, 110, 96)
HUD_TEXT_COLOR: Final[tuple[int, int, int]] = (232, 232, 222)
HUD_OBJECTIVE_COLOR: Final[tuple[int, int, int]] = (196, 208, 156)
HUD_BAR_BACKGROUND: Final[tuple[int, int, int]] = (52, 56, 62)
HEALTH_BAR_COLOR: Final[tuple[int, int, int]] = (212, 72, 72)
HUNGER_BAR_COLOR: Final[tuple[int, int, int]] = (218, 154, 62)
THIRST_BAR_COLOR: Final[tuple[int, int, int]] = (72, 156, 222)
INFECTION_BAR_COLOR: Final[tuple[int, int, int]] = (152, 202, 76)
BATTERY_BAR_COLOR: Final[tuple[int, int, int]] = (236, 212, 82)
HUD_ICON_RADIUS: Final[int] = 4

# Chat / radio.
CHAT_HEIGHT: Final[int] = 180
CHAT_MARGIN: Final[int] = 14
CHAT_FONT_SIZE: Final[int] = 18
CHAT_MAX_INPUT: Final[int] = 180
CHAT_VISIBLE_MESSAGES: Final[int] = 6
CHAT_TYPEWRITER_CPS: Final[float] = 70.0
CHAT_MAX_ENTRIES: Final[int] = 60
RADIO_COST_MIN: Final[int] = 1
RADIO_COST_MAX: Final[int] = 3
CHAT_BACKGROUND: Final[tuple[int, int, int]] = (14, 17, 21)
CHAT_PANEL_ALPHA: Final[int] = 236
CHAT_BORDER_COLOR: Final[tuple[int, int, int]] = (58, 76, 68)
CHAT_OPERATOR_COLOR: Final[tuple[int, int, int]] = (128, 194, 250)
CHAT_MIKE_COLOR: Final[tuple[int, int, int]] = (218, 226, 188)
CHAT_SYSTEM_COLOR: Final[tuple[int, int, int]] = (160, 164, 166)
CHAT_INPUT_COLOR: Final[tuple[int, int, int]] = (244, 244, 234)
CHAT_INPUT_BACKGROUND: Final[tuple[int, int, int]] = (30, 35, 41)
CHAT_HEADER_COLOR: Final[tuple[int, int, int]] = (120, 200, 148)

# Game over.
GAME_OVER_OVERLAY: Final[tuple[int, int, int, int]] = (0, 0, 0, 150)
GAME_OVER_COLOR: Final[tuple[int, int, int]] = (224, 88, 78)
GAME_OVER_TEXT: Final[tuple[int, int, int]] = (224, 224, 214)

# Zombis y combate.
ZOMBIE_WALKER: Final[str] = "walker"
ZOMBIE_RUNNER: Final[str] = "runner"
ZOMBIE_BRUTE: Final[str] = "brute"
ZOMBIE_SCREECHER: Final[str] = "screecher"
ZOMBIE_KINDS: Final[tuple[str, ...]] = (
    ZOMBIE_WALKER,
    ZOMBIE_RUNNER,
    ZOMBIE_BRUTE,
    ZOMBIE_SCREECHER,
)
ZOMBIE_STATS: Final[dict[str, dict[str, int]]] = {
    ZOMBIE_WALKER: {"health": 30, "damage": 5, "speed": 1, "chase_range": 5},
    ZOMBIE_RUNNER: {"health": 20, "damage": 4, "speed": 2, "chase_range": 8},
    ZOMBIE_BRUTE: {"health": 60, "damage": 12, "speed": 1, "chase_range": 4},
    ZOMBIE_SCREECHER: {"health": 25, "damage": 3, "speed": 1, "chase_range": 7},
}
ZOMBIE_COIN_REWARDS: Final[dict[str, int]] = {
    ZOMBIE_WALKER: 3,
    ZOMBIE_RUNNER: 4,
    ZOMBIE_BRUTE: 8,
    ZOMBIE_SCREECHER: 3,
}
ZOMBIE_ATTACK_COOLDOWN: Final[int] = 2
INITIAL_ZOMBIES: Final[int] = 2
MAX_ZOMBIES: Final[int] = 8
ZOMBIE_SPAWN_CHANCE: Final[float] = 0.22
ZOMBIE_SPAWN_RADIUS: Final[int] = 6
MIKE_MELEE_DAMAGE: Final[int] = 22
MIKE_COLOR: Final[tuple[int, int, int]] = (228, 228, 214)
ZOMBIE_COLORS: Final[dict[str, tuple[int, int, int]]] = {
    ZOMBIE_WALKER: (110, 160, 90),
    ZOMBIE_RUNNER: (190, 124, 62),
    ZOMBIE_BRUTE: (132, 70, 70),
    ZOMBIE_SCREECHER: (152, 102, 180),
}

# Eventos narrativos.
EVENT_CHANCE: Final[float] = 0.18
EVENT_LOOT: Final[str] = "loot"
EVENT_AMBUSH: Final[str] = "ambush"
EVENT_STORM: Final[str] = "storm"
EVENT_RADIO: Final[str] = "radio"
EVENT_WHISPER: Final[str] = "whisper"
EVENT_TYPES: Final[tuple[str, ...]] = (
    EVENT_LOOT,
    EVENT_AMBUSH,
    EVENT_STORM,
    EVENT_RADIO,
    EVENT_WHISPER,
)
EVENT_STORM_DAMAGE: Final[int] = 4
EVENT_RADIO_BONUS: Final[int] = 12
EVENT_INFECTION_BUMP: Final[int] = 5

# Assets procedurales.
SPRITE_SIZE: Final[int] = 24
SPRITE_CACHE_VERSION: Final[str] = "v2"
SPRITE_MIKE: Final[str] = "mike"
SPRITE_MIKE_HURT: Final[str] = "mike_hurt"
SPRITE_ZOMBIE_PREFIX: Final[str] = "zombie_"
SPRITE_ITEM_PREFIX: Final[str] = "item_"
SPRITE_KEYS: Final[tuple[str, ...]] = (
    SPRITE_MIKE,
    SPRITE_MIKE_HURT,
    "zombie_walker",
    "zombie_runner",
    "zombie_brute",
    "zombie_screecher",
    "item_food",
    "item_water",
    "item_suppressor",
    "item_bandage",
)
ASSET_TYPE_SPRITE: Final[str] = "sprite"
AUDIO_SAMPLE_RATE: Final[int] = 44100
AUDIO_VOLUME: Final[float] = 0.35

# Rasgos y meta-progresión.
TRAIT_NEUTRAL: Final[str] = "neutral"
TRAIT_RESILIENT: Final[str] = "resiliente"
TRAIT_SCOUT: Final[str] = "explorador"
TRAIT_VETERAN: Final[str] = "veterano"
BASE_TRAITS: Final[tuple[str, ...]] = (
    TRAIT_NEUTRAL,
    TRAIT_RESILIENT,
    TRAIT_SCOUT,
)
UNLOCKABLE_TRAITS: Final[tuple[str, ...]] = (TRAIT_VETERAN,)
TRAIT_MODIFIERS: Final[dict[str, dict[str, int]]] = {
    TRAIT_NEUTRAL: {},
    TRAIT_RESILIENT: {
        "hunger_reduction": 1,
        "thirst_reduction": 1,
    },
    TRAIT_SCOUT: {
        "melee_bonus": 6,
    },
    TRAIT_VETERAN: {
        "melee_bonus": 4,
        "infection_reduction": 1,
    },
}
TRAIT_DESCRIPTIONS: Final[dict[str, str]] = {
    TRAIT_NEUTRAL: "Sin ventajas ni desventajas.",
    TRAIT_RESILIENT: "Aguanta mejor el hambre y la sed.",
    TRAIT_SCOUT: "Golpea más fuerte y empieza con más salud.",
    TRAIT_VETERAN: "Veterano: mucha salud y resistencia al virus.",
}
TRAIT_UNLOCK_DEATHS: Final[int] = 10
META_UNLOCK_VETERAN: Final[str] = "trait_veteran"
GLOBAL_MEMORY_IMPORTANCE: Final[int] = 3
GLOBAL_MEMORY_LIMIT: Final[int] = 3

# Comportamiento autónomo local (no consume tokens de API).
INSTINCT_HUNGER_THRESHOLD: Final[int] = 60
INSTINCT_THIRST_THRESHOLD: Final[int] = 60
INSTINCT_INFECTION_THRESHOLD: Final[int] = 65
INSTINCT_HEAL_THRESHOLD: Final[int] = 45
INSTINCT_FLEE_HEALTH: Final[int] = 30
INSTINCT_SCAVENGE_CHANCE: Final[float] = 0.22
INSTINCT_SCAVENGE_LOW_CHANCE: Final[float] = 0.45
INSTINCT_LOW_SUPPLIES: Final[int] = 2

# Zoom de cámara y tamaño de entidades.
RENDER_SCALE: Final[float] = 0.875
RENDER_TILE_SIZE: Final[int] = 14
ENTITY_DRAW_SIZE: Final[int] = 24
