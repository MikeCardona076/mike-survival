"""Tests del renderer con viewport culling (pygame en modo headless)."""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from config import (  # noqa: E402
    CAMERA_START_X,
    CAMERA_START_Y,
    CHUNK_PIXELS,
    CHUNK_SIZE,
    TILE_COLORS,
    TILE_GRASS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from game.entities import Mike, Zombie  # noqa: E402
from game.renderer import Renderer  # noqa: E402


class FakeChunk:
    """Chunk mínimo para probar el renderer sin generación de ruido."""

    def __init__(self, chunk_x: int, chunk_y: int, tiles: tuple[tuple[int, ...], ...]) -> None:
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.tiles = tiles


class FakeWorld:
    """Mundo falso: todos los tiles son hierba."""

    def __init__(self) -> None:
        row = tuple(TILE_GRASS for _ in range(CHUNK_SIZE))
        self._tiles = tuple(row for _ in range(CHUNK_SIZE))

    def get_chunk(self, chunk_x: int, chunk_y: int) -> FakeChunk:
        return FakeChunk(chunk_x, chunk_y, self._tiles)


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    yield surface
    pygame.quit()


def _renderer() -> Renderer:
    return Renderer(pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)))


def test_visible_chunks_centered_on_chunk_zero() -> None:
    assert _renderer().visible_chunks(CAMERA_START_X, CAMERA_START_Y) == [
        (chunk_x, chunk_y) for chunk_y in (-1, 0, 1) for chunk_x in (-1, 0, 1)
    ]


def test_visible_chunks_culls_far_chunks() -> None:
    camera_x = 100 * CHUNK_PIXELS + CAMERA_START_X
    camera_y = 100 * CHUNK_PIXELS + CAMERA_START_Y

    visible = _renderer().visible_chunks(camera_x, camera_y)

    assert {chunk_x for chunk_x, _ in visible} == {99, 100, 101}
    assert {chunk_y for _, chunk_y in visible} == {99, 100, 101}


def test_draw_paints_visible_tiles(screen: pygame.Surface) -> None:
    drawn = Renderer(screen).draw(FakeWorld(), CAMERA_START_X, CAMERA_START_Y)

    assert drawn == 9 * CHUNK_SIZE * CHUNK_SIZE
    center_color = tuple(screen.get_at((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))[:3]
    assert center_color == TILE_COLORS[TILE_GRASS]


def test_draw_culls_before_requesting_chunks(screen: pygame.Surface) -> None:
    class RecordingWorld(FakeWorld):
        def __init__(self) -> None:
            super().__init__()
            self.requested: list[tuple[int, int]] = []

        def get_chunk(self, chunk_x: int, chunk_y: int) -> FakeChunk:
            self.requested.append((chunk_x, chunk_y))
            return super().get_chunk(chunk_x, chunk_y)

    world = RecordingWorld()
    Renderer(screen).draw(world, 10 * CHUNK_PIXELS, 10 * CHUNK_PIXELS)

    assert world.requested
    assert all(8 <= chunk_x <= 12 for chunk_x, _ in world.requested)


def test_draw_entities(screen: pygame.Surface) -> None:
    renderer = Renderer(screen)
    mike = Mike()
    zombie = Zombie.create("walker", 17, 16)

    renderer.draw_entities(CAMERA_START_X, CAMERA_START_Y, mike, [zombie])
