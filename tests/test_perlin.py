"""Tests del fallback Perlin puro usado en Windows."""

from __future__ import annotations

from game.perlin import pnoise2


def test_pnoise2_is_deterministic() -> None:
    assert pnoise2(1.25, -3.5, octaves=4, base=7) == pnoise2(
        1.25,
        -3.5,
        octaves=4,
        base=7,
    )


def test_pnoise2_range_and_variation() -> None:
    values = [pnoise2(x * 0.3, x * 0.2, octaves=4, base=11) for x in range(50)]

    assert all(-1.0 <= value <= 1.0 for value in values)
    assert len(set(round(value, 6) for value in values)) > 1
