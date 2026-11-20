"""Tests de la sesión de juego y la persistencia de turnos."""

from __future__ import annotations

import sqlite3

from config import (
    META_UNLOCK_VETERAN,
    RUN_STATUS_DEAD,
    TRAIT_UNLOCK_DEATHS,
    TURN_SECONDS,
)  # noqa: E402
from db.repositories import (  # noqa: E402
    AgentStateRepository,
    MemoryRepository,
    MetaProgressionRepository,
    RunRepository,
    StatsRepository,
)
from game.entities import Zombie  # noqa: E402
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
    session = GameSession(run, connection, instincts=False)

    for _ in range(100):
        session.advance_turn()

    assert session.is_over
    finished = RunRepository(connection).get(run.id)
    assert finished is not None
    assert finished.status == RUN_STATUS_DEAD
    assert finished.cause_of_death is not None


def test_instinct_attacks_adjacent_zombie(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=2121, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.zombies = [
        Zombie.create("walker", int(session.mike.pos_x) + 1, int(session.mike.pos_y))
    ]

    session.advance_turn()

    assert any("instinto" in event for event in session.events)


def test_session_spawns_zombies(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=3030, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)

    assert session.zombies
    for zombie in session.zombies:
        assert zombie.alive
        assert (zombie.x, zombie.y) != (int(session.mike.pos_x), int(session.mike.pos_y))


def test_session_combat_kills_adjacent_zombie(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=4040, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.zombies = [
        Zombie.create("walker", int(session.mike.pos_x) + 1, int(session.mike.pos_y))
    ]

    first = session.attack_nearest_zombie()
    assert "golpea" in first
    second = session.attack_nearest_zombie()

    assert "derriba" in second
    assert session.zombies == []


def test_death_saves_global_memory_and_stats(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=5050, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.mike.take_damage(1000, cause="prueba")
    session._finish_run()

    assert StatsRepository(connection).get().total_deaths == 1
    memories = MemoryRepository(connection).list_global()
    assert any("morí" in entry.content.lower() for entry in memories)


def test_ten_deaths_unlock_veteran(connection: sqlite3.Connection) -> None:
    meta = MetaProgressionRepository(connection)

    for index in range(TRAIT_UNLOCK_DEATHS):
        run = RunRepository(connection).create(
            seed=6000 + index,
            refugio7_x=0,
            refugio7_y=0,
        )
        session = GameSession(run, connection)
        session.mike.take_damage(1000, cause="prueba")
        session._finish_run()

    assert StatsRepository(connection).get().total_deaths == TRAIT_UNLOCK_DEATHS
    assert meta.is_unlocked(META_UNLOCK_VETERAN)
