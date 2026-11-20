"""Tests de la generación del mundo (Fase 1: posición del Refugio 7)."""

from __future__ import annotations

from config import REFUGIO7_RADIUS
from game.world import generate_refugio7


def test_generate_refugio7_is_deterministic() -> None:
    assert generate_refugio7(42) == generate_refugio7(42)


def test_generate_refugio7_respects_radius() -> None:
    for seed in range(50):
        x, y = generate_refugio7(seed)
        assert -REFUGIO7_RADIUS <= x <= REFUGIO7_RADIUS
        assert -REFUGIO7_RADIUS <= y <= REFUGIO7_RADIUS
