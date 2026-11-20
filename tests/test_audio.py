"""Tests de audio procedural con pyfxr."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

pytest.importorskip("pyfxr")

from assets.audio import AudioManager  # noqa: E402


def test_audio_manager_generates_and_plays() -> None:
    pygame.mixer.quit()
    manager = AudioManager()

    assert manager.available is True
    for name in ("pickup", "hit", "radio", "suppressor", "death"):
        manager.play(name)
    manager.play("desconocido")


def test_audio_manager_available_flag() -> None:
    assert isinstance(AudioManager().available, bool)
