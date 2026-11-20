"""Tests de las herramientas de Mike."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from agent.tools import TOOL_SPECS, execute_tool
from config import (
    ITEM_FOOD,
    TILE_GRASS,
    TILE_WATER,
)
from game.entities import Mike


class FakeWorld:
    def __init__(self, tiles: dict[tuple[int, int], int] | None = None) -> None:
        self.tiles = tiles or {}

    def get_tile(self, world_x: int, world_y: int) -> int:
        return self.tiles.get((world_x, world_y), TILE_GRASS)


class FakeSession:
    def __init__(self) -> None:
        self.run = SimpleNamespace(seed=123)
        self.mike = Mike()
        self.world = FakeWorld({(16, 17): TILE_WATER})
        self.events: list[str] = []
        self.memories: list[tuple[str, int]] = []
        self.persisted = 0

    def persist(self) -> None:
        self.persisted += 1

    def add_event(self, text: str) -> None:
        self.events.append(text)

    def remember(self, content: str, importance: int = 1) -> Any:
        self.memories.append((content, importance))
        return SimpleNamespace(content=content, importance=importance)


def test_there_are_ten_tools() -> None:
    assert len(TOOL_SPECS) == 10


def test_move_blocks_water_and_updates_position() -> None:
    session = FakeSession()

    blocked = execute_tool(session, "move", {"dx": 0, "dy": 1})
    assert "No puedo avanzar" in blocked
    assert (session.mike.pos_x, session.mike.pos_y) == (16.0, 16.0)

    moved = execute_tool(session, "move", {"dx": 1, "dy": 0})
    assert "Mike está en (17, 16)" in moved
    assert (session.mike.pos_x, session.mike.pos_y) == (17.0, 16.0)
    assert session.persisted == 1


def test_scan_summarizes_terrain() -> None:
    session = FakeSession()

    result = execute_tool(session, "scan", {"radius": 1})

    assert "Terreno en radio 1" in result
    assert "agua" in result


def test_scavenge_adds_items() -> None:
    session = FakeSession()
    before = sum(session.mike.inventory.items.values())

    result = execute_tool(session, "scavenge", {})

    assert "Mike encuentra" in result
    assert sum(session.mike.inventory.items.values()) > before


def test_consume_actions() -> None:
    session = FakeSession()
    session.mike.hunger = 90
    session.mike.thirst = 90
    session.mike.infection = 90

    assert "come" in execute_tool(session, "eat", {}).lower()
    assert "bebe" in execute_tool(session, "drink", {}).lower()
    assert "supresor" in execute_tool(session, "use_suppressor", {}).lower()
    assert execute_tool(session, "use_bandage", {}) == "Mike se venda las heridas."
    assert session.persisted == 4


def test_rest_and_remember() -> None:
    session = FakeSession()
    session.mike.health = 60

    assert "salud" in execute_tool(session, "rest", {})
    assert session.mike.health == 65

    assert execute_tool(session, "remember", {"content": "Elena está en R7"}) == (
        "Recuerdo guardado."
    )
    assert session.memories == [("Elena está en R7", 1)]


def test_unknown_tool_and_bad_arguments() -> None:
    session = FakeSession()

    assert "desconocida" in execute_tool(session, "fly", {})
    assert "Error en move" in execute_tool(session, "move", {"dx": "norte"})


def test_attack_without_zombies() -> None:
    session = FakeSession()

    assert "zombi" in execute_tool(session, "attack", {}).lower()
    assert session.mike.inventory.count(ITEM_FOOD) == 2
