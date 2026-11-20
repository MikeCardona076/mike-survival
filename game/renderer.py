"""Renderizado 2D del terreno con viewport culling y zoom.

El renderer calcula qué chunks intersectan la cámara, pinta los tiles a
``RENDER_TILE_SIZE`` píxeles y dibuja a las entidades más grandes que un
tile para que se vean bien.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from config import (
    CHUNK_PIXELS,
    COLOR_BACKGROUND,
    ENTITY_DRAW_SIZE,
    MIKE_COLOR,
    RENDER_SCALE,
    RENDER_TILE_SIZE,
    SPRITE_MIKE,
    SPRITE_MIKE_HURT,
    SPRITE_ZOMBIE_PREFIX,
    TILE_COLORS,
    TILE_SIZE,
    ZOMBIE_COLORS,
)

if TYPE_CHECKING:
    from assets.sprites import SpriteSet
    from game.entities import Mike, Zombie
    from game.world import World


class Renderer:
    """Dibuja el mundo en una superficie de pygame."""

    def __init__(self, screen: pygame.Surface, sprites: SpriteSet | None = None) -> None:
        self._screen = screen
        self._width = screen.get_width()
        self._height = screen.get_height()
        self._sprites = sprites
        self._scaled_sprites: dict[str, pygame.Surface] = {}

    def _viewport_origin(self, camera_x: float, camera_y: float) -> tuple[float, float]:
        """Esquina superior izquierda de la vista, en píxeles del mundo."""
        return (
            camera_x - (self._width / RENDER_SCALE) / 2,
            camera_y - (self._height / RENDER_SCALE) / 2,
        )

    def visible_chunks(self, camera_x: float, camera_y: float) -> list[tuple[int, int]]:
        """Coordenadas de los chunks que intersectan el viewport actual."""
        left, top = self._viewport_origin(camera_x, camera_y)
        world_width = self._width / RENDER_SCALE
        world_height = self._height / RENDER_SCALE
        first_chunk_x = math.floor(left / CHUNK_PIXELS)
        last_chunk_x = math.floor((left + world_width - 1) / CHUNK_PIXELS)
        first_chunk_y = math.floor(top / CHUNK_PIXELS)
        last_chunk_y = math.floor((top + world_height - 1) / CHUNK_PIXELS)

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
            chunk_left = round((chunk_x * CHUNK_PIXELS - left) * RENDER_SCALE)
            chunk_top = round((chunk_y * CHUNK_PIXELS - top) * RENDER_SCALE)

            for local_y, row in enumerate(chunk.tiles):
                screen_y = chunk_top + local_y * RENDER_TILE_SIZE
                for local_x, tile in enumerate(row):
                    screen_x = chunk_left + local_x * RENDER_TILE_SIZE
                    pygame.draw.rect(
                        self._screen,
                        TILE_COLORS[int(tile)],
                        (screen_x, screen_y, RENDER_TILE_SIZE, RENDER_TILE_SIZE),
                    )
                    drawn_tiles += 1

        return drawn_tiles

    def _entity_sprite(self, sprite_key: str) -> pygame.Surface | None:
        if self._sprites is None:
            return None
        cached = self._scaled_sprites.get(sprite_key)
        if cached is not None:
            return cached
        scaled = pygame.transform.scale(
            self._sprites.get(sprite_key),
            (ENTITY_DRAW_SIZE, ENTITY_DRAW_SIZE),
        )
        self._scaled_sprites[sprite_key] = scaled
        return scaled

    def draw_entities(
        self,
        camera_x: float,
        camera_y: float,
        mike: Mike,
        zombies: list[Zombie],
    ) -> None:
        """Dibuja a Mike y a los zombis visibles encima del terreno."""
        left, top = self._viewport_origin(camera_x, camera_y)
        viewport = self._screen.get_rect()
        offset = (RENDER_TILE_SIZE - ENTITY_DRAW_SIZE) // 2

        for zombie in zombies:
            if not zombie.alive:
                continue
            screen_x = round((zombie.x * TILE_SIZE - left) * RENDER_SCALE) + offset
            screen_y = round((zombie.y * TILE_SIZE - top) * RENDER_SCALE) + offset
            rect = pygame.Rect(screen_x, screen_y, ENTITY_DRAW_SIZE, ENTITY_DRAW_SIZE)
            if not viewport.colliderect(rect):
                continue
            sprite = self._entity_sprite(f"{SPRITE_ZOMBIE_PREFIX}{zombie.kind}")
            if sprite is None:
                pygame.draw.rect(
                    self._screen,
                    ZOMBIE_COLORS[zombie.kind],
                    rect,
                )
            else:
                self._screen.blit(sprite, rect.topleft)

        screen_x = round((mike.pos_x * TILE_SIZE - left) * RENDER_SCALE) + offset
        screen_y = round((mike.pos_y * TILE_SIZE - top) * RENDER_SCALE) + offset
        mike_rect = pygame.Rect(screen_x, screen_y, ENTITY_DRAW_SIZE, ENTITY_DRAW_SIZE)
        if not viewport.colliderect(mike_rect):
            return
        sprite_key = SPRITE_MIKE_HURT if mike.health <= 30 else SPRITE_MIKE
        sprite = self._entity_sprite(sprite_key)
        if sprite is None:
            pygame.draw.rect(self._screen, MIKE_COLOR, mike_rect)
        else:
            self._screen.blit(sprite, mike_rect.topleft)
