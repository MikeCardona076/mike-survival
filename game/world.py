"""Generación del mundo procedural.

En la Fase 1 solo vive aquí el cálculo determinista de la posición del
Refugio 7. La generación de chunks con Perlin llega en la Fase 2.
"""

from __future__ import annotations

import random

from config import REFUGIO7_RADIUS


def generate_refugio7(seed: int) -> tuple[int, int]:
    """Deriva las coordenadas del Refugio 7 a partir de la seed de la run."""
    rng = random.Random(seed)
    return (
        rng.randint(-REFUGIO7_RADIUS, REFUGIO7_RADIUS),
        rng.randint(-REFUGIO7_RADIUS, REFUGIO7_RADIUS),
    )
