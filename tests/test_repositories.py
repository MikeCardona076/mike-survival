"""Tests de la capa de repositorios SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from config import DEFAULT_TRAIT, RUN_STATUS_ALIVE, RUN_STATUS_DEAD, SCHEMA_PATH
from db.database import get_connection, init_db
from db.repositories import (
    AgentStateRepository,
    ChatRepository,
    EventRepository,
    MemoryRepository,
    RunRepository,
    StatsRepository,
)


def test_create_run_persists_seed_and_refugio(connection: sqlite3.Connection) -> None:
    repository = RunRepository(connection)
    run = repository.create(seed=1234, refugio7_x=10, refugio7_y=-20)

    assert run.id == 1
    assert run.seed == 1234
    assert (run.refugio7_x, run.refugio7_y) == (10, -20)
    assert run.status == RUN_STATUS_ALIVE
    assert run.trait == DEFAULT_TRAIT
    assert run.ended_at is None
    assert run.cause_of_death is None
    assert repository.count() == 1


def test_get_missing_run_returns_none(connection: sqlite3.Connection) -> None:
    repository = RunRepository(connection)
    assert repository.get(999) is None
    assert repository.get_latest() is None


def test_finish_run_records_death(connection: sqlite3.Connection) -> None:
    repository = RunRepository(connection)
    run = repository.create(seed=7, refugio7_x=0, refugio7_y=0)

    repository.finish(run.id, status=RUN_STATUS_DEAD, cause_of_death="infección")
    finished = repository.get(run.id)

    assert finished is not None
    assert finished.status == RUN_STATUS_DEAD
    assert finished.cause_of_death == "infección"
    assert finished.ended_at is not None


def test_finish_missing_run_raises(connection: sqlite3.Connection) -> None:
    with pytest.raises(LookupError):
        RunRepository(connection).finish(999, status=RUN_STATUS_DEAD)


def test_agent_state_defaults(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=1, refugio7_x=5, refugio7_y=5)
    state = AgentStateRepository(connection).create(run.id)

    assert state.run_id == run.id
    assert state.health == 100
    assert state.hunger == 0
    assert state.thirst == 0
    assert state.infection == 0
    assert state.radio_battery == 100
    assert (state.pos_x, state.pos_y) == (0.0, 0.0)
    assert state.inventory == "[]"
    assert state.turn_count == 0


def test_agent_state_update_position(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=2, refugio7_x=0, refugio7_y=0)
    repository = AgentStateRepository(connection)
    repository.create(run.id)

    repository.update_position(run.id, 12.5, -3.25)
    state = repository.get(run.id)

    assert state is not None
    assert (state.pos_x, state.pos_y) == (12.5, -3.25)


def test_chat_history_roundtrip(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=3, refugio7_x=0, refugio7_y=0)
    repository = ChatRepository(connection)

    repository.add(run.id, role="operator", content="Mike, ¿me escuchas?")
    tool_message = repository.add(
        run.id,
        role="assistant",
        tool_name="scan_area",
        tool_args={"radius": 3},
        tool_call_id="call_1",
    )
    messages = repository.list_for_run(run.id)

    assert [message.role for message in messages] == ["operator", "assistant"]
    assert messages[0].content == "Mike, ¿me escuchas?"
    assert tool_message.tool_name == "scan_area"
    assert tool_message.tool_call_id == "call_1"
    assert json.loads(tool_message.tool_args or "{}") == {"radius": 3}


def test_events_and_memory(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=4, refugio7_x=0, refugio7_y=0)
    events = EventRepository(connection)
    memories = MemoryRepository(connection)

    event = events.add(run.id, "loot", "Encontró un botiquín")
    memories.add(run.id, "fact", "El refugio está al norte", importance=3)

    assert events.list_for_run(run.id) == [event]
    assert events.list_for_run(run.id, only_unresolved=True) == [event]
    events.resolve(event.id)
    assert events.list_for_run(run.id, only_unresolved=True) == []
    assert len(memories.list_for_run(run.id)) == 1


def test_deleting_run_cascades_related_rows(connection: sqlite3.Connection) -> None:
    repository = RunRepository(connection)
    run = repository.create(seed=5, refugio7_x=0, refugio7_y=0)
    AgentStateRepository(connection).create(run.id)
    ChatRepository(connection).add(run.id, role="operator", content="hola")
    event = EventRepository(connection).add(run.id, "noise", "Un ruido")
    memory = MemoryRepository(connection).add(run.id, "fact", "recuerdo")
    connection.execute(
        """
        INSERT INTO world_chunks (run_id, chunk_x, chunk_y, seed, data)
        VALUES (?, 0, 0, 5, '{}')
        """,
        (run.id,),
    )

    connection.execute("DELETE FROM runs WHERE id = ?", (run.id,))

    for table in ("agent_state", "chat_history", "events", "world_chunks"):
        total = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert total == 0
    memory_row = connection.execute(
        "SELECT run_id FROM memory WHERE id = ?", (memory.id,)
    ).fetchone()
    assert memory_row is not None
    assert memory_row["run_id"] is None
    assert event.id > 0


def test_foreign_keys_are_enforced(connection: sqlite3.Connection) -> None:
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO agent_state (run_id) VALUES (999)")


def test_wal_mode_is_enabled(connection: sqlite3.Connection) -> None:
    mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
    assert str(mode).lower() == "wal"


def test_stats_singleton_and_counter(connection: sqlite3.Connection) -> None:
    repository = StatsRepository(connection)
    stats = repository.get()

    assert stats.runs_played == 0
    assert stats.runs_won == 0
    assert stats.total_deaths == 0

    repository.increment_runs_played()
    assert repository.get().runs_played == 1


def test_init_db_is_idempotent(db_path: Path) -> None:
    init_db(db_path=db_path, schema_path=SCHEMA_PATH)
    with get_connection(db_path=db_path) as connection:
        total = connection.execute("SELECT COUNT(*) FROM stats").fetchone()[0]
    assert total == 1
