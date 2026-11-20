"""Eventos narrativos procedurales durante la run."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from config import (
    EVENT_AMBUSH,
    EVENT_CHANCE,
    EVENT_INFECTION_BUMP,
    EVENT_LOOT,
    EVENT_RADIO,
    EVENT_RADIO_BONUS,
    EVENT_STORM,
    EVENT_STORM_DAMAGE,
    EVENT_TYPES,
    EVENT_WHISPER,
    MAX_INFECTION,
    MAX_RADIO_BATTERY,
    SCAVENGE_ITEMS,
)
from game.entities import spawn_zombies

if TYPE_CHECKING:
    from game.loop import GameSession


def _loot(session: GameSession, rng: random.Random) -> str:
    item = rng.choice(SCAVENGE_ITEMS)
    session.mike.inventory.add(item, 1)
    return f"Encuentras provisiones: {item}."


def _ambush(session: GameSession, rng: random.Random) -> str:
    enemies = spawn_zombies(
        session.run.seed + session.mike.turn_count * 17,
        1,
        int(session.mike.pos_x),
        int(session.mike.pos_y),
        session.world,
    )
    session.zombies.extend(enemies)
    return "Una emboscada: un zombi aparece entre los escombros."


def _storm(session: GameSession, rng: random.Random) -> str:
    session.mike.take_damage(EVENT_STORM_DAMAGE, cause="tormenta")
    return f"Una tormenta ácida te hiere ({EVENT_STORM_DAMAGE} de daño)."


def _radio(session: GameSession, rng: random.Random) -> str:
    session.mike.radio_battery = min(
        MAX_RADIO_BATTERY,
        session.mike.radio_battery + EVENT_RADIO_BONUS,
    )
    return "La radio capta una señal lejana y recupera batería."


def _whisper(session: GameSession, rng: random.Random) -> str:
    session.mike.infection = min(
        MAX_INFECTION,
        session.mike.infection + EVENT_INFECTION_BUMP,
    )
    return "El virus susurra en tu cabeza; la infección sube."


_EVENT_HANDLERS = {
    EVENT_LOOT: _loot,
    EVENT_AMBUSH: _ambush,
    EVENT_STORM: _storm,
    EVENT_RADIO: _radio,
    EVENT_WHISPER: _whisper,
}


def maybe_event(session: GameSession) -> tuple[str, str] | None:
    """Devuelve (tipo, texto) si ocurre un evento en este turno."""
    rng = random.Random((session.run.seed << 5) ^ (session.mike.turn_count * 31))
    if rng.random() >= EVENT_CHANCE:
        return None
    event_type = rng.choice(EVENT_TYPES)
    text = _EVENT_HANDLERS[event_type](session, rng)
    return event_type, text
