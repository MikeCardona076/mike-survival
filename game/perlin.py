"""Perlin noise 2D en Python puro.

Fallback para Windows, donde el paquete ``noise`` no tiene wheel y exige
compilador C. La API imita ``noise.pnoise2``. En Linux/Docker se sigue
usando la implementación C de ``noise``.
"""

from __future__ import annotations

import math
import random
from functools import lru_cache

_GRADIENTS = (
    (1.0, 1.0),
    (-1.0, 1.0),
    (1.0, -1.0),
    (-1.0, -1.0),
    (1.0, 0.0),
    (-1.0, 0.0),
    (0.0, 1.0),
    (0.0, -1.0),
)


@lru_cache(maxsize=32)
def _permutation(base: int) -> tuple[int, ...]:
    values = list(range(256))
    random.Random(base).shuffle(values)
    return tuple(values + values)


def _fade(value: float) -> float:
    return value * value * value * (value * (value * 6 - 15) + 10)


def _lerp(start: float, end: float, amount: float) -> float:
    return start + amount * (end - start)


def _gradient_dot(hash_value: int, x: float, y: float) -> float:
    gradient_x, gradient_y = _GRADIENTS[hash_value & 7]
    return gradient_x * x + gradient_y * y


def _perlin2(x: float, y: float, permutation: tuple[int, ...]) -> float:
    cell_x = math.floor(x)
    cell_y = math.floor(y)
    local_x = x - cell_x
    local_y = y - cell_y
    grid_x = cell_x & 255
    grid_y = cell_y & 255

    corner_00 = permutation[permutation[grid_x] + grid_y]
    corner_10 = permutation[permutation[grid_x + 1] + grid_y]
    corner_01 = permutation[permutation[grid_x] + grid_y + 1]
    corner_11 = permutation[permutation[grid_x + 1] + grid_y + 1]

    fade_x = _fade(local_x)
    fade_y = _fade(local_y)

    bottom = _lerp(
        _gradient_dot(corner_00, local_x, local_y),
        _gradient_dot(corner_10, local_x - 1, local_y),
        fade_x,
    )
    top = _lerp(
        _gradient_dot(corner_01, local_x, local_y - 1),
        _gradient_dot(corner_11, local_x - 1, local_y - 1),
        fade_x,
    )
    return _lerp(bottom, top, fade_y)


def pnoise2(
    x: float,
    y: float,
    octaves: int = 1,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    repeatx: int = 1024,
    repeaty: int = 1024,
    base: int = 0,
) -> float:
    """Perlin 2D fractal compatible con ``noise.pnoise2``."""
    permutation = _permutation(int(base))
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0
    for _ in range(max(1, octaves)):
        total += _perlin2(x * frequency, y * frequency, permutation) * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_amplitude
