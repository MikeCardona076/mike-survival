"""Tests del panel de chat (pygame headless)."""

from __future__ import annotations

import os
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from config import CHAT_MAX_INPUT, WINDOW_HEIGHT, WINDOW_WIDTH  # noqa: E402
from ui.chat import ChatPanel  # noqa: E402


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    yield surface
    pygame.quit()


def _key(key: int, unicode: str = "") -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)


def _panel(screen: pygame.Surface) -> ChatPanel:
    return ChatPanel(screen)


def test_typing_and_submit(screen: pygame.Surface) -> None:
    panel = _panel(screen)
    for character in "hola":
        panel.handle_event(_key(ord(character), character))

    assert panel.input_text == "hola"
    assert panel.handle_event(_key(pygame.K_RETURN)) == "hola"
    assert panel.input_text == ""


def test_backspace_and_empty_submit(screen: pygame.Surface) -> None:
    panel = _panel(screen)
    panel.handle_event(_key(ord("a"), "a"))
    panel.handle_event(_key(pygame.K_BACKSPACE))

    assert panel.input_text == ""
    assert panel.handle_event(_key(pygame.K_RETURN)) is None


def test_input_is_limited(screen: pygame.Surface) -> None:
    panel = _panel(screen)
    for _ in range(CHAT_MAX_INPUT + 20):
        panel.handle_event(_key(ord("x"), "x"))

    assert len(panel.input_text) == CHAT_MAX_INPUT


def test_typewriter_reveals_assistant_text(screen: pygame.Surface) -> None:
    panel = _panel(screen)
    panel.add_message("assistant", "Estoy al norte del refugio.")

    assert panel.visible_entries()[-1].text == ""
    panel.update(0.1)
    assert 0 < len(panel.visible_entries()[-1].text) < 26
    panel.update(10.0)
    assert panel.visible_entries()[-1].text == "Estoy al norte del refugio."


def test_draw_with_all_roles(screen: pygame.Surface) -> None:
    panel = _panel(screen)
    panel.add_message("system", "Radio sin enlace.")
    panel.add_message("operator", "Mike, ¿me escuchas?")
    panel.add_message("assistant", "Algo débil, pero te escucho.")
    panel.update(1.0)

    panel.draw()
