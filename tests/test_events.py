"""Tests de eventos narrativos procedurales."""

from __future__ import annotations

from types import SimpleNamespace

from config import EVENT_TYPES, TILE_GRASS
from game.entities import Mike
from game.events import maybe_event


class FakeWorld:
    def get_tile(self, world_x: int, world_y: int) -> int:
        return TILE_GRASS


class FakeSession:
    def __init__(self) -> None:
        self.run = SimpleNamespace(seed=777)
        self.mike = Mike()
        self.world = FakeWorld()
        self.zombies: list[object] = []


def test_events_occur_and_are_well_formed() -> None:
    session = FakeSession()
    seen: set[str] = set()

    for turn in range(300):
        session.mike.turn_count = turn
        result = maybe_event(session)
        if result is not None:
            event_type, text = result
            assert event_type in EVENT_TYPES
            assert text
            seen.add(event_type)

    assert seen


def test_no_event_on_deterministic_turn() -> None:
    session = FakeSession()
    session.mike.turn_count = 0

    first = maybe_event(session)
    second = maybe_event(session)

    assert first == second
