"""Tests de generación y persistencia del mundo procedural."""

from __future__ import annotations

import sqlite3

import pytest

from config import CHUNK_SIZE, REFUGIO7_RADIUS  # noqa: E402
from db.repositories import RunRepository, WorldChunkRepository  # noqa: E402
from game.world import (  # noqa: E402
    TileType,
    World,
    chunk_from_json,
    chunk_to_json,
    generate_chunk,
    generate_refugio7,
)


def test_generate_refugio7_is_deterministic() -> None:
    assert generate_refugio7(42) == generate_refugio7(42)


def test_generate_refugio7_respects_radius() -> None:
    for seed in range(50):
        x, y = generate_refugio7(seed)
        assert -REFUGIO7_RADIUS <= x <= REFUGIO7_RADIUS
        assert -REFUGIO7_RADIUS <= y <= REFUGIO7_RADIUS


def test_generate_chunk_shape_and_tiles() -> None:
    chunk = generate_chunk(seed=1234, chunk_x=0, chunk_y=0)

    assert chunk.chunk_x == 0
    assert chunk.chunk_y == 0
    assert chunk.seed == 1234
    assert len(chunk.tiles) == CHUNK_SIZE
    for row in chunk.tiles:
        assert len(row) == CHUNK_SIZE
        assert all(isinstance(tile, TileType) for tile in row)


def test_generate_chunk_is_deterministic() -> None:
    first = generate_chunk(seed=99, chunk_x=-2, chunk_y=3)
    second = generate_chunk(seed=99, chunk_x=-2, chunk_y=3)

    assert first == second


def test_chunk_json_roundtrip() -> None:
    chunk = generate_chunk(seed=7, chunk_x=1, chunk_y=-1)
    restored = chunk_from_json(7, 1, -1, chunk_to_json(chunk))

    assert restored == chunk


def test_chunk_from_json_rejects_invalid_payload() -> None:
    with pytest.raises(ValueError):
        chunk_from_json(1, 0, 0, '{"tiles": []}')
    with pytest.raises(ValueError):
        chunk_from_json(1, 0, 0, '{"tiles": [[999]]}')


def test_world_persists_generated_chunk(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=555, refugio7_x=1, refugio7_y=2)
    world = World(run.id, run.seed, connection)
    repository = WorldChunkRepository(connection)

    chunk = world.get_chunk(0, 0)

    assert repository.count_for_run(run.id) == 1
    stored = repository.get_data(run.id, 0, 0)
    assert stored is not None
    assert chunk_from_json(run.seed, 0, 0, stored) == chunk


def test_world_reads_persisted_chunk(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=777, refugio7_x=1, refugio7_y=2)
    first_world = World(run.id, run.seed, connection)
    original = first_world.get_chunk(3, -2)

    second_world = World(run.id, run.seed, connection)
    restored = second_world.get_chunk(3, -2)

    assert restored.tiles == original.tiles
    assert WorldChunkRepository(connection).count_for_run(run.id) == 1


def test_world_caches_chunks(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=888, refugio7_x=1, refugio7_y=2)
    world = World(run.id, run.seed, connection)

    assert world.get_chunk(2, 3) is world.get_chunk(2, 3)


def test_world_tile_lookup_crosses_chunk_boundaries(
    connection: sqlite3.Connection,
) -> None:
    run = RunRepository(connection).create(seed=999, refugio7_x=1, refugio7_y=2)
    world = World(run.id, run.seed, connection)

    assert world.get_tile(CHUNK_SIZE, 0) == world.get_chunk(1, 0).tile_at(0, 0)
    assert world.get_tile(-1, -1) == world.get_chunk(-1, -1).tile_at(
        CHUNK_SIZE - 1,
        CHUNK_SIZE - 1,
    )
    assert isinstance(world.get_tile(0, 0), TileType)
