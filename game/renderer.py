"""Renderizado 2D del terreno con viewport culling.

El renderer calcula qué chunks intersectan la cámara y solo pide/dibuja
esos chunks. Los tiles se pintan como rectángulos de ``TILE_SIZE`` píxeles.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from config import CHUNK_PIXELS, COLOR_BACKGROUND, TILE_COLORS, TILE_SIZE

if TYPE_CHECKING:
    from game.world import World


class Renderer:
    """Dibuja el mundo en una superficie de pygame."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._width = screen.get_width()
        self._height = screen.get_height()

    def _viewport_origin(self, camera_x: float, camera_y: float) -> tuple[float, float]:
        """Devuelve la esquina superior izquierda de la vista en píxeles."""
        return (
            camera_x - self._width / 2,
            camera_y - self._height / 2,
        )

    def visible_chunks(self, camera_x: float, camera_y: float) -> list[tuple[int, int]]:
        """Coordenadas de los chunks que intersectan el viewport actual."""
        left, top = self._viewport_origin(camera_x, camera_y)
        first_chunk_x = math.floor(left / CHUNK_PIXELS)
        last_chunk_x = math.floor((left + self._width - 1) / CHUNK_PIXELS)
        first_chunk_y = math.floor(top / CHUNK_PIXELS)
        last_chunk_y = math.floor((top + self._height - 1) / CHUNK_PIXELS)

        return [
            (chunk_x, chunk_y)
            for chunk_y in range(first_chunk_y, last_chunk_y + 1)
            for chunk_x in range(first_chunk_x, last_chunk_x + 1)
        ]

    def draw(self, world: World, camera_x: float, camera_y: float) -> int:
        """Pinta un frame y devuelve cuántos tiles se dibujaron."""
        self._screen.fill(COLOR_BACKGROUND)
        left, top = self._viewport_origin(camera_x, camera_y)
        drawn_tiles = 0

        for chunk_x, chunk_y in self.visible_chunks(camera_x, camera_y):
            chunk = world.get_chunk(chunk_x, chunk_y)
            chunk_left = int(chunk_x * CHUNK_PIXELS - left)
            chunk_top = int(chunk_y * CHUNK_PIXELS - top)

            for local_y, row in enumerate(chunk.tiles):
                screen_y = chunk_top + local_y * TILE_SIZE
                for local_x, tile in enumerate(row):
                    screen_x = chunk_left + local_x * TILE_SIZE
                    pygame.draw.rect(
                        self._screen,
                        TILE_COLORS[int(tile)],
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
                    )
                    drawn_tiles += 1

        return drawn_tiles
