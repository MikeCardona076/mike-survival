"""Herramientas que Mike puede invocar mediante function calling."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from config import (
    ITEM_NAMES,
    REST_HEAL,
    SCAN_MAX_RADIUS,
    SCAVENGE_ITEMS,
    TILE_NAMES,
    WALKABLE_TILE_IDS,
)

if TYPE_CHECKING:
    from game.loop import GameSession


def _move(session: GameSession, dx: int, dy: int) -> str:
    target_x = int(session.mike.pos_x) + dx
    target_y = int(session.mike.pos_y) + dy
    tile = int(session.world.get_tile(target_x, target_y))
    if tile not in WALKABLE_TILE_IDS:
        return f"No puedo avanzar a ({target_x}, {target_y}): {TILE_NAMES[tile]}."
    session.mike.pos_x = float(target_x)
    session.mike.pos_y = float(target_y)
    session.persist()
    session.add_event(f"Mike se mueve a ({target_x}, {target_y}).")
    return f"Mike está en ({target_x}, {target_y}), sobre {TILE_NAMES[tile]}."


def _scan(session: GameSession, radius: int = 2) -> str:
    radius = max(1, min(int(radius), SCAN_MAX_RADIUS))
    center_x = int(session.mike.pos_x)
    center_y = int(session.mike.pos_y)
    counts: dict[str, int] = {}
    for offset_y in range(-radius, radius + 1):
        for offset_x in range(-radius, radius + 1):
            tile = int(session.world.get_tile(center_x + offset_x, center_y + offset_y))
            name = TILE_NAMES[tile]
            counts[name] = counts.get(name, 0) + 1

    summary = ", ".join(f"{amount} {name}" for name, amount in sorted(counts.items()))
    zombies = getattr(session, "zombies", [])
    close = [
        zombie
        for zombie in zombies
        if abs(float(getattr(zombie, "x", 0)) - center_x) <= radius
        and abs(float(getattr(zombie, "y", 0)) - center_y) <= radius
    ]
    threat = f" Zombis cerca: {len(close)}." if close else " Sin zombis a la vista."
    return f"Terreno en radio {radius}: {summary}.{threat}"


def _scavenge(session: GameSession) -> str:
    seed = (
        (session.run.seed << 8)
        ^ (int(session.mike.pos_x) * 31 + int(session.mike.pos_y) * 131)
        ^ session.mike.turn_count
    )
    rng = random.Random(seed)
    item = rng.choice(SCAVENGE_ITEMS)
    quantity = rng.randint(1, 2)
    session.mike.inventory.add(item, quantity)
    session.persist()
    message = f"Mike encuentra {quantity} {ITEM_NAMES[item]}."
    session.add_event(message)
    return message


def _eat(session: GameSession) -> str:
    if not session.mike.eat():
        return "No queda comida."
    session.persist()
    return "Mike come y recupera fuerzas."


def _drink(session: GameSession) -> str:
    if not session.mike.drink():
        return "No queda agua."
    session.persist()
    return "Mike bebe agua."


def _use_suppressor(session: GameSession) -> str:
    if not session.mike.use_suppressor():
        return "No quedan supresores."
    session.persist()
    return "Mike usa un supresor; la infección baja."


def _use_bandage(session: GameSession) -> str:
    if not session.mike.use_bandage():
        return "No quedan vendas."
    session.persist()
    return "Mike se venda las heridas."


def _rest(session: GameSession) -> str:
    session.mike.heal(REST_HEAL)
    session.persist()
    return f"Mike descansa y recupera {REST_HEAL} de salud."


def _attack(session: GameSession) -> str:
    attack = getattr(session, "attack_nearest_zombie", None)
    if attack is None:
        return "No hay ningún zombi al alcance."
    result: str = attack()
    return result


def _remember(session: GameSession, content: str, importance: int = 1) -> str:
    importance = max(1, min(int(importance), 5))
    session.remember(content, importance)
    return "Recuerdo guardado."


_HANDLERS = {
    "move": _move,
    "scan": _scan,
    "scavenge": _scavenge,
    "eat": _eat,
    "drink": _drink,
    "use_suppressor": _use_suppressor,
    "use_bandage": _use_bandage,
    "rest": _rest,
    "attack": _attack,
    "remember": _remember,
}

TOOL_SPECS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "move",
            "description": "Mueve a Mike una casilla en horizontal o vertical.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dx": {"type": "integer", "minimum": -1, "maximum": 1},
                    "dy": {"type": "integer", "minimum": -1, "maximum": 1},
                },
                "required": ["dx", "dy"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scan",
            "description": "Examina el terreno y las amenazas alrededor de Mike.",
            "parameters": {
                "type": "object",
                "properties": {
                    "radius": {"type": "integer", "minimum": 1, "maximum": SCAN_MAX_RADIUS}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scavenge",
            "description": "Busca objetos en la posición actual de Mike.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "eat",
            "description": "Come una ración para reducir el hambre.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "drink",
            "description": "Bebe agua para reducir la sed.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "use_suppressor",
            "description": "Usa un supresor para bajar la infección.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "use_bandage",
            "description": "Usa una venda para recuperar salud.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rest",
            "description": "Descansa brevemente para recuperar salud.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "attack",
            "description": "Ataca al zombi más cercano.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Guarda un recuerdo importante para futuras runs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "importance": {"type": "integer", "minimum": 1, "maximum": 5},
                },
                "required": ["content"],
            },
        },
    },
]


def execute_tool(session: GameSession, name: str, arguments: dict[str, Any]) -> str:
    """Ejecuta una herramienta por nombre y devuelve el resultado textual."""
    handler = _HANDLERS.get(name)
    if handler is None:
        return f"Herramienta desconocida: {name}."
    try:
        return handler(session, **arguments)
    except (TypeError, ValueError) as error:
        return f"Error en {name}: {error}"
