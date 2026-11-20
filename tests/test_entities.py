"""Tests de Mike, inventario y desgaste por turnos."""

from __future__ import annotations

import pytest

from config import (
    BANDAGE_HEAL,
    FOOD_HUNGER_RELIEF,
    ITEM_BANDAGE,
    ITEM_FOOD,
    ITEM_SUPPRESSOR,
    ITEM_WATER,
    SUPPRESSOR_RELIEF,
    WATER_THIRST_RELIEF,
)
from game.entities import Mike
from game.inventory import Inventory


def test_mike_dies_after_100_turns_without_supplies() -> None:
    mike = Mike()

    for _ in range(100):
        mike.advance_turn()

    assert not mike.alive
    assert mike.health == 0
    assert mike.cause_of_death is not None


def test_eat_reduces_hunger_and_consumes_food() -> None:
    mike = Mike()
    mike.hunger = 90
    before = mike.inventory.count(ITEM_FOOD)

    assert mike.eat() is True
    assert mike.hunger == 90 - FOOD_HUNGER_RELIEF
    assert mike.inventory.count(ITEM_FOOD) == before - 1


def test_drink_reduces_thirst_and_consumes_water() -> None:
    mike = Mike()
    mike.thirst = 90

    assert mike.drink() is True
    assert mike.thirst == 90 - WATER_THIRST_RELIEF
    assert mike.inventory.count(ITEM_WATER) == 1


def test_suppressor_reduces_infection() -> None:
    mike = Mike()
    mike.infection = 90

    assert mike.use_suppressor() is True
    assert mike.infection == 90 - SUPPRESSOR_RELIEF
    assert mike.inventory.count(ITEM_SUPPRESSOR) == 0


def test_bandage_heals_without_exceeding_max() -> None:
    mike = Mike()
    mike.health = 50
    mike.inventory.add(ITEM_BANDAGE, 1)

    assert mike.use_bandage() is True
    assert mike.health == 50 + BANDAGE_HEAL

    mike.health = 95
    mike.inventory.add(ITEM_BANDAGE, 1)
    mike.use_bandage()
    assert mike.health == 100


def test_actions_fail_without_items() -> None:
    mike = Mike()
    mike.inventory = Inventory()

    assert mike.eat() is False
    assert mike.drink() is False
    assert mike.use_suppressor() is False
    assert mike.use_bandage() is False


def test_damage_and_radio_battery() -> None:
    mike = Mike()
    mike.take_damage(30, cause="zombi")
    assert mike.health == 70
    assert mike.spend_radio(3) is True
    assert mike.radio_battery == 97
    assert mike.spend_radio(1000) is False


def test_inventory_roundtrip() -> None:
    inventory = Inventory.starting()
    inventory.add(ITEM_FOOD, 2)

    restored = Inventory.from_json(inventory.to_json())

    assert restored.count(ITEM_FOOD) == inventory.count(ITEM_FOOD)
    assert restored.count(ITEM_WATER) == inventory.count(ITEM_WATER)


def test_inventory_rejects_invalid_payloads() -> None:
    with pytest.raises(ValueError):
        Inventory.from_json("[]")
    with pytest.raises(ValueError):
        Inventory.from_json('{"food": -1}')
    with pytest.raises(ValueError):
        Inventory.from_json('{"food": "mucho"}')
