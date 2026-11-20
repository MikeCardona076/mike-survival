"""Tests del minimapa (pygame headless)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from config import TILE_GRASS  # noqa: E402
from ui.map import Minimap  # noqa: E402


class FakeWorld:
    def get_tile(self, world_x: int, world_y: int) -> int:
        return TILE_GRASS


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((640, 480))
    yield surface
    pygame.quit()


def test_minimap_draws(screen: pygame.Surface) -> None:
    mike = SimpleNamespace(pos_x=16, pos_y=16)
    run = SimpleNamespace(refugio7_x=0, refugio7_y=0)

    Minimap(screen).draw(FakeWorld(), mike, [], run)
