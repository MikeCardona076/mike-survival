"""Tests de la sesión de juego y la persistencia de turnos."""

from __future__ import annotations

import sqlite3

import pytest

pytest.importorskip("noise")

from config import RUN_STATUS_DEAD, TURN_SECONDS  # noqa: E402
from db.repositories import (  # noqa: E402
    AgentStateRepository,
    RunRepository,
)
from game.loop import GameSession  # noqa: E402


def test_session_advances_turns_and_persists(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=1010, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)

    session.update(TURN_SECONDS * 3)

    assert session.mike.turn_count == 3
    state = AgentStateRepository(connection).get(run.id)
    assert state is not None
    assert state.turn_count == 3
    assert state.inventory != "[]"


def test_session_death_finishes_run(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=2020, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)

    for _ in range(100):
        session.advance_turn()

    assert session.is_over
    finished = RunRepository(connection).get(run.id)
    assert finished is not None
    assert finished.status == RUN_STATUS_DEAD
    assert finished.cause_of_death is not None
