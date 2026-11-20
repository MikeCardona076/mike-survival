"""Tests de rasgos y meta-progresión."""

from __future__ import annotations

import sqlite3

from config import (
    META_UNLOCK_VETERAN,
    TRAIT_NEUTRAL,
    TRAIT_RESILIENT,
    TRAIT_SCOUT,
    TRAIT_VETERAN,
)
from db.repositories import (
    MemoryRepository,
    MetaProgressionRepository,
    StatsRepository,
)
from game.entities import Mike, available_traits, choose_trait


def test_trait_modifiers_are_applied() -> None:
    resilient = Mike.from_trait(TRAIT_RESILIENT)
    assert resilient.trait == TRAIT_RESILIENT
    assert resilient.hunger_rate == 1
    assert resilient.thirst_rate == 2

    scout = Mike.from_trait(TRAIT_SCOUT)
    assert scout.melee_damage == 28

    veteran = Mike.from_trait(TRAIT_VETERAN)
    assert veteran.infection_rate == 0


def test_available_traits_respect_unlocks() -> None:
    assert available_traits() == (TRAIT_NEUTRAL, TRAIT_RESILIENT, TRAIT_SCOUT)
    assert TRAIT_VETERAN in available_traits({TRAIT_VETERAN})


def test_choose_trait_is_deterministic() -> None:
    assert choose_trait(1234) == choose_trait(1234)
    assert choose_trait(1234) in available_traits()
    assert choose_trait(1234, {TRAIT_VETERAN}) in available_traits({TRAIT_VETERAN})


def test_traits_vary_across_seeds() -> None:
    traits = {choose_trait(seed) for seed in range(20)}
    assert len(traits) > 1


def test_stats_track_deaths_and_runs(connection: sqlite3.Connection) -> None:
    repository = StatsRepository(connection)

    repository.increment_runs_played()
    assert repository.get().runs_played == 1
    assert repository.increment_deaths() == 1
    assert repository.increment_deaths() == 2
    assert repository.get().total_deaths == 2


def test_meta_progression_unlock_is_idempotent(
    connection: sqlite3.Connection,
) -> None:
    repository = MetaProgressionRepository(connection)

    assert repository.unlock(META_UNLOCK_VETERAN, "Veterano") is True
    assert repository.unlock(META_UNLOCK_VETERAN, "Veterano") is False
    assert repository.is_unlocked(META_UNLOCK_VETERAN) is True
    assert repository.list_keys() == [META_UNLOCK_VETERAN]


def test_global_memories_are_shared(connection: sqlite3.Connection) -> None:
    repository = MemoryRepository(connection)

    repository.add(None, "global", "Recuerdo entre runs", 3)
    repository.add(None, "global", "Otro recuerdo", 1)

    memories = repository.list_global(limit=5)

    assert [entry.content for entry in memories] == [
        "Recuerdo entre runs",
        "Otro recuerdo",
    ]
