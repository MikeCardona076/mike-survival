"""Tests del HUD (pygame en modo headless)."""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from config import HUD_BAR_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH  # noqa: E402
from game.entities import Mike  # noqa: E402
from ui.hud import Hud, bar_width  # noqa: E402


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    yield surface
    pygame.quit()


def test_bar_width_clamps_values() -> None:
    assert bar_width(0, 100, HUD_BAR_WIDTH) == 0
    assert bar_width(50, 100, HUD_BAR_WIDTH) == HUD_BAR_WIDTH // 2
    assert bar_width(150, 100, HUD_BAR_WIDTH) == HUD_BAR_WIDTH
    assert bar_width(-10, 100, HUD_BAR_WIDTH) == 0


def test_bar_width_rejects_invalid_maximum() -> None:
    with pytest.raises(ValueError):
        bar_width(1, 0, HUD_BAR_WIDTH)


def test_hud_draws_without_crashing(screen: pygame.Surface) -> None:
    Hud(screen).draw(Mike())
