"""Inventario de Mike y objetos básicos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from config import STARTING_INVENTORY


@dataclass
class Inventory:
    """Cantidades de objetos por identificador."""

    items: dict[str, int] = field(default_factory=dict)

    @classmethod
    def starting(cls) -> Inventory:
        """Inventario inicial de una run."""
        return cls(dict(STARTING_INVENTORY))

    def count(self, item: str) -> int:
        """Cantidad disponible de un objeto."""
        return self.items.get(item, 0)

    def add(self, item: str, quantity: int = 1) -> None:
        """Añade unidades de un objeto."""
        if quantity < 1:
            raise ValueError("La cantidad debe ser positiva")
        self.items[item] = self.count(item) + quantity

    def remove(self, item: str, quantity: int = 1) -> bool:
        """Quita unidades; devuelve False si no hay suficientes."""
        if quantity < 1:
            raise ValueError("La cantidad debe ser positiva")
        available = self.count(item)
        if available < quantity:
            return False
        remaining = available - quantity
        if remaining == 0:
            self.items.pop(item, None)
        else:
            self.items[item] = remaining
        return True

    def to_json(self) -> str:
        """Serializa el inventario para SQLite."""
        return json.dumps(self.items, sort_keys=True)

    @classmethod
    def from_json(cls, data: str) -> Inventory:
        """Reconstruye y valida un inventario guardado."""
        payload = json.loads(data)
        if not isinstance(payload, dict):
            raise ValueError("Inventario inválido")
        items: dict[str, int] = {}
        for key, value in payload.items():
            if not isinstance(key, str) or not isinstance(value, int) or value < 0:
                raise ValueError("Inventario inválido")
            if value > 0:
                items[key] = value
        return cls(items)
