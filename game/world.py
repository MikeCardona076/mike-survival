"""Generación procedural del mundo por chunks con Perlin noise.

Cada chunk es una cuadrícula de ``CHUNK_SIZE`` x ``CHUNK_SIZE`` tiles. Se
combinan dos capas de ruido (elevación y humedad) para clasificar el
terreno. ``World`` cachea los chunks en memoria y los persiste en la tabla
``world_chunks``.
"""

from __future__ import annotations

import json
import random
import sqlite3
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

try:
    from noise import pnoise2
except ImportError:  # Windows sin compilador C: fallback puro
    from game.perlin import pnoise2

from config import (
    CHUNK_SIZE,
    ELEVATION_ROCK_THRESHOLD,
    ELEVATION_SAND_THRESHOLD,
    ELEVATION_SCALE,
    ELEVATION_WATER_THRESHOLD,
    MOISTURE_BASE_OFFSET,
    MOISTURE_FOREST_THRESHOLD,
    MOISTURE_SCALE,
    NOISE_LACUNARITY,
    NOISE_OCTAVES,
    NOISE_PERSISTENCE,
    NOISE_SEED_MASK,
    REFUGIO7_RADIUS,
    TILE_FOREST,
    TILE_GRASS,
    TILE_ROCK,
    TILE_SAND,
    TILE_WATER,
)
from db.repositories import WorldChunkRepository


class TileType(IntEnum):
    """Tipos de terreno posibles en un chunk."""

    WATER = TILE_WATER
    SAND = TILE_SAND
    GRASS = TILE_GRASS
    FOREST = TILE_FOREST
    ROCK = TILE_ROCK


def generate_refugio7(seed: int) -> tuple[int, int]:
    """Deriva las coordenadas del Refugio 7 a partir de la seed de la run."""
    rng = random.Random(seed)
    return (
        rng.randint(-REFUGIO7_RADIUS, REFUGIO7_RADIUS),
        rng.randint(-REFUGIO7_RADIUS, REFUGIO7_RADIUS),
    )


@dataclass(frozen=True, slots=True)
class Chunk:
    """Un chunk generado, con sus tiles en orden ``[y][x]``."""

    chunk_x: int
    chunk_y: int
    seed: int
    tiles: tuple[tuple[TileType, ...], ...]

    def tile_at(self, local_x: int, local_y: int) -> TileType:
        """Devuelve el tile en coordenadas locales del chunk."""
        return self.tiles[local_y][local_x]


def _classify_tile(elevation: float, moisture: float) -> TileType:
    """Clasifica un tile a partir de las dos capas de Perlin."""
    if elevation < ELEVATION_WATER_THRESHOLD:
        return TileType.WATER
    if elevation < ELEVATION_SAND_THRESHOLD:
        return TileType.SAND
    if elevation > ELEVATION_ROCK_THRESHOLD:
        return TileType.ROCK
    if moisture > MOISTURE_FOREST_THRESHOLD:
        return TileType.FOREST
    return TileType.GRASS


def generate_chunk(seed: int, chunk_x: int, chunk_y: int) -> Chunk:
    """Genera un chunk determinista a partir de la seed y sus coordenadas."""
    elevation_base = seed & NOISE_SEED_MASK
    moisture_base = (seed + MOISTURE_BASE_OFFSET) & NOISE_SEED_MASK
    rows: list[tuple[TileType, ...]] = []

    for local_y in range(CHUNK_SIZE):
        world_y = chunk_y * CHUNK_SIZE + local_y
        row: list[TileType] = []
        for local_x in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + local_x
            elevation = pnoise2(
                world_x * ELEVATION_SCALE,
                world_y * ELEVATION_SCALE,
                octaves=NOISE_OCTAVES,
                persistence=NOISE_PERSISTENCE,
                lacunarity=NOISE_LACUNARITY,
                base=elevation_base,
            )
            moisture = pnoise2(
                world_x * MOISTURE_SCALE,
                world_y * MOISTURE_SCALE,
                octaves=NOISE_OCTAVES,
                persistence=NOISE_PERSISTENCE,
                lacunarity=NOISE_LACUNARITY,
                base=moisture_base,
            )
            row.append(_classify_tile(elevation, moisture))
        rows.append(tuple(row))

    return Chunk(
        chunk_x=chunk_x,
        chunk_y=chunk_y,
        seed=seed,
        tiles=tuple(rows),
    )


def chunk_to_json(chunk: Chunk) -> str:
    """Serializa un chunk para la columna ``world_chunks.data``."""
    payload = {"tiles": [[int(tile) for tile in row] for row in chunk.tiles]}
    return json.dumps(payload, separators=(",", ":"))


def chunk_from_json(seed: int, chunk_x: int, chunk_y: int, data: str) -> Chunk:
    """Reconstruye y valida un chunk guardado en SQLite."""
    payload: Any = json.loads(data)
    raw_tiles = payload.get("tiles") if isinstance(payload, dict) else None
    if not isinstance(raw_tiles, list) or len(raw_tiles) != CHUNK_SIZE:
        raise ValueError("Chunk inválido: número de filas incorrecto")

    rows: list[tuple[TileType, ...]] = []
    for raw_row in raw_tiles:
        if not isinstance(raw_row, list) or len(raw_row) != CHUNK_SIZE:
            raise ValueError("Chunk inválido: número de columnas incorrecto")
        try:
            rows.append(tuple(TileType(int(value)) for value in raw_row))
        except (TypeError, ValueError) as error:
            raise ValueError("Chunk inválido: tipo de tile desconocido") from error

    return Chunk(
        chunk_x=chunk_x,
        chunk_y=chunk_y,
        seed=seed,
        tiles=tuple(rows),
    )


class World:
    """Mundo de una run: entrega chunks generados o persistidos."""

    def __init__(self, run_id: int, seed: int, connection: sqlite3.Connection) -> None:
        self._run_id = run_id
        self._seed = seed
        self._repository = WorldChunkRepository(connection)
        self._cache: dict[tuple[int, int], Chunk] = {}

    @property
    def run_id(self) -> int:
        """Id de la run a la que pertenece este mundo."""
        return self._run_id

    @property
    def seed(self) -> int:
        """Seed con la que se generan los chunks."""
        return self._seed

    def get_chunk(self, chunk_x: int, chunk_y: int) -> Chunk:
        """Devuelve un chunk desde caché, SQLite o generándolo."""
        key = (chunk_x, chunk_y)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        stored_data = self._repository.get_data(self._run_id, chunk_x, chunk_y)
        if stored_data is None:
            chunk = generate_chunk(self._seed, chunk_x, chunk_y)
            self._repository.save(
                self._run_id,
                chunk_x,
                chunk_y,
                self._seed,
                chunk_to_json(chunk),
            )
        else:
            chunk = chunk_from_json(self._seed, chunk_x, chunk_y, stored_data)

        self._cache[key] = chunk
        return chunk

    def get_tile(self, world_x: int, world_y: int) -> TileType:
        """Devuelve el tile en coordenadas absolutas, creando el chunk si hace falta."""
        chunk_x, local_x = divmod(world_x, CHUNK_SIZE)
        chunk_y, local_y = divmod(world_y, CHUNK_SIZE)
        return self.get_chunk(chunk_x, chunk_y).tile_at(local_x, local_y)
