"""Tests de zombis, IA y combate."""

from __future__ import annotations

from config import TILE_GRASS, TILE_WATER, ZOMBIE_ATTACK_COOLDOWN
from game.combat import attack_zombie
from game.entities import Mike, Zombie, spawn_zombies


class FakeWorld:
    def __init__(self) -> None:
        self.water = {(18, 16)}

    def get_tile(self, world_x: int, world_y: int) -> int:
        return TILE_WATER if (world_x, world_y) in self.water else TILE_GRASS


def test_zombie_chases_mike() -> None:
    mike = Mike()
    zombie = Zombie.create("walker", 20, 16)

    events = zombie.update(mike)

    assert zombie.state == "chase"
    assert zombie.x == 19
    assert events == []


def test_runner_moves_two_tiles() -> None:
    mike = Mike()
    zombie = Zombie.create("runner", 20, 16)

    zombie.update(mike)

    assert zombie.x == 18


def test_zombie_attacks_with_cooldown() -> None:
    mike = Mike()
    zombie = Zombie.create("walker", 17, 16)

    first = zombie.update(mike)
    assert "ataca" in first[0]
    assert mike.health == 95
    assert zombie.cooldown == ZOMBIE_ATTACK_COOLDOWN

    second = zombie.update(mike)
    assert second == []
    assert mike.health == 95

    third = zombie.update(mike)
    assert "ataca" in third[0]
    assert mike.health == 90


def test_attack_zombie_can_kill() -> None:
    mike = Mike()
    zombie = Zombie.create("walker", 17, 16)

    message, killed = attack_zombie(mike, zombie)
    assert "golpea" in message
    assert killed is False

    message, killed = attack_zombie(mike, zombie)
    assert "derriba" in message
    assert killed is True
    assert zombie.alive is False


def test_spawn_zombies_avoid_water_and_center() -> None:
    world = FakeWorld()
    zombies = spawn_zombies(seed=5, count=5, center_x=16, center_y=16, world=world)

    assert zombies
    for zombie in zombies:
        assert (zombie.x, zombie.y) != (16, 16)
        assert (zombie.x, zombie.y) not in world.water
        assert zombie.kind in {"walker", "runner", "brute", "screecher"}
