"""Tests de economía, refugio y recompensas."""

from __future__ import annotations

import sqlite3

from config import (
    ITEM_COIN,
    ITEM_IRON,
    ITEM_WOOD,
    SHELTER_HEALTH_BONUS,
    WEAPON_DAMAGE_BONUS,
)
from db.repositories import RunRepository, Shelter, ShelterRepository
from game.entities import Zombie
from game.loop import GameSession


def test_shelter_persists_levels(connection: sqlite3.Connection) -> None:
    repository = ShelterRepository(connection)

    assert repository.get() == Shelter(level=0, weapon_level=0)
    repository.update(Shelter(level=2, weapon_level=1))
    assert repository.get() == Shelter(level=2, weapon_level=1)


def test_buy_resources_and_upgrade(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=7001, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.mike.inventory.add(ITEM_COIN, 40)
    session.mike.inventory.add(ITEM_WOOD, 20)
    session.mike.inventory.add(ITEM_IRON, 10)
    base_health = session.mike.max_health
    base_damage = session.mike.melee_damage

    assert "madera" in session.buy_wood()
    assert session.mike.inventory.count(ITEM_WOOD) == 22
    assert "hierro" in session.buy_iron()
    assert session.mike.inventory.count(ITEM_IRON) == 11

    assert "Refugio nivel 1" in session.upgrade_shelter()
    assert session.mike.max_health == base_health + SHELTER_HEALTH_BONUS
    assert session.mike.health == session.mike.max_health

    assert "Arma nivel 1" in session.upgrade_weapon()
    assert session.mike.melee_damage == base_damage + WEAPON_DAMAGE_BONUS

    stored = ShelterRepository(connection).get()
    assert stored.level == 1
    assert stored.weapon_level == 1


def test_shop_requires_resources(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=7002, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)

    assert "Faltan monedas" in session.buy_wood()
    assert "Faltan materiales" in session.upgrade_shelter()
    session.mike.health = 50
    assert "Faltan monedas" in session.heal_at_shelter()


def test_killing_zombie_rewards_coins(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=7003, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.zombies = [
        Zombie.create("walker", int(session.mike.pos_x) + 1, int(session.mike.pos_y))
    ]

    while session.zombies:
        session.attack_nearest_zombie()

    assert session.mike.inventory.count(ITEM_COIN) == 3
    assert any("monedas" in event for event in session.events)


def test_objective_changes_with_context(connection: sqlite3.Connection) -> None:
    run = RunRepository(connection).create(seed=7004, refugio7_x=0, refugio7_y=0)
    session = GameSession(run, connection)
    session.mike.health = 10

    assert session.objective == "Curarse"
