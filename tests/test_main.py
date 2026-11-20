"""Smoke test del bucle principal de ventana en modo headless."""

from __future__ import annotations

import os
import sqlite3

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest  # noqa: E402

pytest.importorskip("noise")

import main  # noqa: E402
from db.repositories import RunRepository  # noqa: E402


def test_run_game_headless_smoke(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=2024, refugio7_x=3, refugio7_y=-4)

    assert main.run_game(run, connection, max_frames=1) == 0
