"""Tests del panel del refugio."""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from db.repositories import Shelter  # noqa: E402
from game.entities import Mike  # noqa: E402
from ui.shelter import ShelterPanel  # noqa: E402


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((800, 600))
    yield surface
    pygame.quit()


def _key(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode="")


def test_panel_maps_actions(screen: pygame.Surface) -> None:
    panel = ShelterPanel(screen)

    assert panel.handle_event(_key(pygame.K_1)) == "wood"
    assert panel.handle_event(_key(pygame.K_2)) == "iron"
    assert panel.handle_event(_key(pygame.K_3)) == "shelter"
    assert panel.handle_event(_key(pygame.K_4)) == "weapon"
    assert panel.handle_event(_key(pygame.K_5)) == "heal"
    assert panel.handle_event(_key(pygame.K_TAB)) == "close"
    assert panel.handle_event(_key(pygame.K_ESCAPE)) == "close"


def test_panel_draws(screen: pygame.Surface) -> None:
    panel = ShelterPanel(screen)
    panel.set_message("Compras 2 de madera.")
    panel.draw(Mike(), Shelter(level=1, weapon_level=2))
