"""Combate cuerpo a cuerpo entre Mike y los zombis."""

from __future__ import annotations

from game.entities import Mike, Zombie


def attack_zombie(mike: Mike, zombie: Zombie) -> tuple[str, bool]:
    """Mike golpea a un zombi; devuelve (mensaje, muerto)."""
    if not zombie.alive:
        return "El zombi ya está muerto.", True
    killed = zombie.take_damage(mike.melee_damage)
    if killed:
        return f"Mike derriba al {zombie.kind}.", True
    return (
        f"Mike golpea al {zombie.kind} ({zombie.health}/{zombie.max_health} de vida).",
        False,
    )
