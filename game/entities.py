"""Entidad de Mike: estado vital, posición e inventario."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from config import (
    BANDAGE_HEAL,
    CHUNK_SIZE,
    DEHYDRATION_DAMAGE,
    FOOD_HUNGER_RELIEF,
    HUNGER_CRITICAL,
    HUNGER_PER_TURN,
    INFECTION_DAMAGE,
    INFECTION_PER_TURN,
    ITEM_BANDAGE,
    ITEM_FOOD,
    ITEM_SUPPRESSOR,
    ITEM_WATER,
    MAX_HEALTH,
    MAX_HUNGER,
    MAX_INFECTION,
    MAX_RADIO_BATTERY,
    MAX_THIRST,
    MIKE_MELEE_DAMAGE,
    STARTING_HEALTH,
    STARVATION_DAMAGE,
    SUPPRESSOR_RELIEF,
    THIRST_CRITICAL,
    THIRST_PER_TURN,
    WALKABLE_TILE_IDS,
    WATER_THIRST_RELIEF,
    ZOMBIE_ATTACK_COOLDOWN,
    ZOMBIE_KINDS,
    ZOMBIE_SPAWN_RADIUS,
    ZOMBIE_STATS,
)
from game.inventory import Inventory

if TYPE_CHECKING:
    from game.world import World


@dataclass
class Mike:
    """Estado completo de Mike durante una run."""

    health: int = STARTING_HEALTH
    hunger: int = 0
    thirst: int = 0
    infection: int = 0
    radio_battery: int = MAX_RADIO_BATTERY
    pos_x: float = CHUNK_SIZE / 2
    pos_y: float = CHUNK_SIZE / 2
    inventory: Inventory = field(default_factory=Inventory.starting)
    turn_count: int = 0
    alive: bool = True
    cause_of_death: str | None = None
    melee_damage: int = MIKE_MELEE_DAMAGE

    def advance_turn(self) -> list[str]:
        """Avanza un turno de simulación y devuelve los eventos relevantes."""
        if not self.alive:
            return []

        self.turn_count += 1
        self.hunger = min(MAX_HUNGER, self.hunger + HUNGER_PER_TURN)
        self.thirst = min(MAX_THIRST, self.thirst + THIRST_PER_TURN)
        self.infection = min(MAX_INFECTION, self.infection + INFECTION_PER_TURN)

        damage = 0
        causes: list[str] = []
        if self.hunger >= HUNGER_CRITICAL:
            damage += STARVATION_DAMAGE
            causes.append("inanición")
        if self.thirst >= THIRST_CRITICAL:
            damage += DEHYDRATION_DAMAGE
            causes.append("deshidratación")
        if self.infection >= MAX_INFECTION:
            damage += INFECTION_DAMAGE
            causes.append("infección")

        events: list[str] = []
        if damage:
            events.append(f"Mike sufre {damage} de daño ({', '.join(causes)}).")
            self.take_damage(damage, cause=" + ".join(causes))
        return events

    def take_damage(self, amount: int, cause: str = "heridas") -> None:
        """Aplica daño y marca la muerte si la salud llega a cero."""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.health = max(0, self.health - amount)
        if self.health == 0 and self.alive:
            self.alive = False
            self.cause_of_death = cause

    def heal(self, amount: int) -> None:
        """Recupera salud sin superar el máximo."""
        if amount < 0:
            raise ValueError("La curación no puede ser negativa")
        self.health = min(MAX_HEALTH, self.health + amount)

    def eat(self) -> bool:
        """Consume comida y reduce el hambre."""
        if not self.inventory.remove(ITEM_FOOD):
            return False
        self.hunger = max(0, self.hunger - FOOD_HUNGER_RELIEF)
        return True

    def drink(self) -> bool:
        """Consume agua y reduce la sed."""
        if not self.inventory.remove(ITEM_WATER):
            return False
        self.thirst = max(0, self.thirst - WATER_THIRST_RELIEF)
        return True

    def use_suppressor(self) -> bool:
        """Consume un supresor y reduce la infección."""
        if not self.inventory.remove(ITEM_SUPPRESSOR):
            return False
        self.infection = max(0, self.infection - SUPPRESSOR_RELIEF)
        return True

    def use_bandage(self) -> bool:
        """Consume una venda y recupera salud."""
        if not self.inventory.remove(ITEM_BANDAGE):
            return False
        self.heal(BANDAGE_HEAL)
        return True

    def spend_radio(self, amount: int = 1) -> bool:
        """Gasta batería de radio; devuelve False si no queda suficiente."""
        if amount < 0:
            raise ValueError("El coste no puede ser negativo")
        if self.radio_battery < amount:
            return False
        self.radio_battery -= amount
        return True


@dataclass
class Zombie:
    """Zombi con IA simple: idle, persecución y ataque."""

    kind: str
    x: int
    y: int
    health: int
    max_health: int
    damage: int
    speed: int
    chase_range: int
    state: str = "idle"
    cooldown: int = 0
    alive: bool = True

    @classmethod
    def create(cls, kind: str, x: int, y: int) -> Zombie:
        """Crea un zombi con las estadísticas de su subtipo."""
        stats = ZOMBIE_STATS[kind]
        return cls(
            kind=kind,
            x=x,
            y=y,
            health=stats["health"],
            max_health=stats["health"],
            damage=stats["damage"],
            speed=stats["speed"],
            chase_range=stats["chase_range"],
        )

    def distance_to(self, mike: Mike) -> int:
        """Distancia Chebyshev en tiles."""
        return max(abs(self.x - int(mike.pos_x)), abs(self.y - int(mike.pos_y)))

    def take_damage(self, amount: int) -> bool:
        """Aplica daño; devuelve True si el zombi muere."""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.alive = False
            return True
        return False

    def update(self, mike: Mike) -> list[str]:
        """Un turno de IA. Devuelve eventos de ataque."""
        if not self.alive or not mike.alive:
            return []
        if self.cooldown > 0:
            self.cooldown -= 1

        distance = self.distance_to(mike)
        if distance <= 1:
            self.state = "attack"
            if self.cooldown == 0:
                mike.take_damage(self.damage, cause=f"zombi {self.kind}")
                self.cooldown = ZOMBIE_ATTACK_COOLDOWN
                return [f"Un {self.kind} ataca a Mike ({self.damage} de daño)."]
            return []

        if distance <= self.chase_range:
            self.state = "chase"
            self._step_toward(mike)
        else:
            self.state = "idle"
        return []

    def _step_toward(self, mike: Mike) -> None:
        delta_x = int(mike.pos_x) - self.x
        delta_y = int(mike.pos_y) - self.y
        step_x = 0 if delta_x == 0 else (1 if delta_x > 0 else -1)
        step_y = 0 if delta_y == 0 else (1 if delta_y > 0 else -1)
        for _ in range(self.speed):
            if step_x:
                self.x += step_x
            if step_y:
                self.y += step_y


def spawn_zombies(
    seed: int,
    count: int,
    center_x: int,
    center_y: int,
    world: World,
) -> list[Zombie]:
    """Genera zombis deterministas en tiles transitables alrededor de un punto."""
    rng = random.Random(seed)
    zombies: list[Zombie] = []
    occupied: set[tuple[int, int]] = set()
    for _ in range(count):
        for _attempt in range(30):
            kind = rng.choice(ZOMBIE_KINDS)
            x = center_x + rng.randint(-ZOMBIE_SPAWN_RADIUS, ZOMBIE_SPAWN_RADIUS)
            y = center_y + rng.randint(-ZOMBIE_SPAWN_RADIUS, ZOMBIE_SPAWN_RADIUS)
            if (x, y) == (center_x, center_y) or (x, y) in occupied:
                continue
            if int(world.get_tile(x, y)) not in WALKABLE_TILE_IDS:
                continue
            zombies.append(Zombie.create(kind, x, y))
            occupied.add((x, y))
            break
    return zombies
