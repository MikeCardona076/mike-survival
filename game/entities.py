"""Entidad de Mike: estado vital, posición e inventario."""

from __future__ import annotations

from dataclasses import dataclass, field

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
    STARTING_HEALTH,
    STARVATION_DAMAGE,
    SUPPRESSOR_RELIEF,
    THIRST_CRITICAL,
    THIRST_PER_TURN,
    WATER_THIRST_RELIEF,
)
from game.inventory import Inventory


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
