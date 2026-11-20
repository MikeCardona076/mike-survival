"""Renderizado 2D del terreno con viewport culling y zoom.

El renderer calcula qué chunks intersectan la cámara, pinta los tiles con
variaciones de color y decoración procedural, y dibuja entidades con
sprites y sombra para dar profundidad.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame

from config import (
    CHUNK_PIXELS,
    COLOR_BACKGROUND,
    DECOR_GRASS,
    DECOR_ROCK,
    DECOR_RUIN,
    DECOR_SAND,
    DECOR_TREE_DARK,
    DECOR_TREE_LIGHT,
    DECOR_TRUNK,
    ENTITY_DRAW_SIZE,
    MIKE_COLOR,
    MIKE_RING_COLOR,
    RENDER_SCALE,
    RENDER_TILE_SIZE,
    SHADOW_COLOR,
    SHORE_FOAM,
    SPRITE_MIKE,
    SPRITE_MIKE_HURT,
    SPRITE_SIZE,
    SPRITE_ZOMBIE_PREFIX,
    TILE_COLOR_VARIANTS,
    TILE_FOREST,
    TILE_GRASS,
    TILE_ROCK,
    TILE_SAND,
    TILE_SIZE,
    TILE_WATER,
    WATER_SPARKLE,
    ZOMBIE_COLORS,
    ZOMBIE_HEALTH_BACKGROUND,
    ZOMBIE_HEALTH_COLOR,
)

if TYPE_CHECKING:
    from assets.sprites import SpriteSet
    from game.entities import Mike, Zombie
    from game.world import World

_HASH_X = 73856093
_HASH_Y = 19349663
_HASH_MASK = 0x7FFFFFFF


def _tile_hash(world_x: int, world_y: int) -> int:
    return (world_x * _HASH_X ^ world_y * _HASH_Y) & _HASH_MASK


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

    def _decorate(
        self,
        tile: int,
        screen_x: int,
        screen_y: int,
        tile_hash: int,
        tick: int,
    ) -> None:
        size = RENDER_TILE_SIZE
        if tile == TILE_FOREST and tile_hash % 3 == 0:
            pygame.draw.rect(
                self._screen,
                DECOR_TRUNK,
                (screen_x + size // 2 - 1, screen_y + size // 2, 2, size // 2),
            )
            pygame.draw.polygon(
                self._screen,
                DECOR_TREE_DARK,
                (
                    (screen_x + 2, screen_y + size // 2 + 1),
                    (screen_x + size // 2, screen_y + 1),
                    (screen_x + size - 2, screen_y + size // 2 + 1),
                ),
            )
            pygame.draw.polygon(
                self._screen,
                DECOR_TREE_LIGHT,
                (
                    (screen_x + 4, screen_y + size // 2 - 1),
                    (screen_x + size // 2, screen_y + 3),
                    (screen_x + size - 4, screen_y + size // 2 - 1),
                ),
            )
        elif tile == TILE_GRASS and tile_hash % 4 == 0:
            for offset in (1, 4, 7):
                pygame.draw.line(
                    self._screen,
                    DECOR_GRASS,
                    (screen_x + offset, screen_y + size - 2),
                    (screen_x + offset, screen_y + size - 5),
                )
        elif tile == TILE_ROCK and tile_hash % 5 == 0:
            pygame.draw.rect(
                self._screen,
                DECOR_ROCK,
                (screen_x + 3, screen_y + size // 2, 3, 2),
            )
            pygame.draw.rect(
                self._screen,
                DECOR_ROCK,
                (screen_x + size - 5, screen_y + size // 2 + 3, 2, 2),
            )
        elif tile == TILE_SAND and tile_hash % 9 == 0:
            pygame.draw.rect(
                self._screen,
                DECOR_SAND,
                (screen_x + size // 2, screen_y + size - 3, 1, 1),
            )
        elif tile == TILE_WATER and (tile_hash + tick) % 29 == 0:
            pygame.draw.rect(
                self._screen,
                WATER_SPARKLE,
                (screen_x + size // 2 - 2, screen_y + size // 2, 5, 1),
            )

        if tile == TILE_ROCK and tile_hash % 7 == 0:
            pygame.draw.rect(
                self._screen,
                DECOR_RUIN,
                (screen_x + 2, screen_y + 4, 3, 8),
            )
            pygame.draw.rect(
                self._screen,
                DECOR_RUIN,
                (screen_x + 9, screen_y + 2, 3, 6),
            )
            pygame.draw.line(
                self._screen,
                DECOR_RUIN,
                (screen_x + 3, screen_y + 4),
                (screen_x + 10, screen_y + 2),
            )

    def _draw_shore(
        self,
        chunk: object,
        local_x: int,
        local_y: int,
        screen_x: int,
        screen_y: int,
    ) -> None:
        size = RENDER_TILE_SIZE
        row = chunk.tiles[local_y]
        if local_x > 0 and int(row[local_x - 1]) != TILE_WATER:
            pygame.draw.line(
                self._screen,
                SHORE_FOAM,
                (screen_x, screen_y + 1),
                (screen_x, screen_y + size - 2),
            )
        if local_x < len(row) - 1 and int(row[local_x + 1]) != TILE_WATER:
            pygame.draw.line(
                self._screen,
                SHORE_FOAM,
                (screen_x + size - 1, screen_y + 1),
                (screen_x + size - 1, screen_y + size - 2),
            )
        if local_y > 0 and int(chunk.tiles[local_y - 1][local_x]) != TILE_WATER:
            pygame.draw.line(
                self._screen,
                SHORE_FOAM,
                (screen_x + 1, screen_y),
                (screen_x + size - 2, screen_y),
            )
        if local_y < len(chunk.tiles) - 1 and int(chunk.tiles[local_y + 1][local_x]) != TILE_WATER:
            pygame.draw.line(
                self._screen,
                SHORE_FOAM,
                (screen_x + 1, screen_y + size - 1),
                (screen_x + size - 2, screen_y + size - 1),
            )

    def draw(self, world: World, camera_x: float, camera_y: float) -> int:
        """Pinta un frame y devuelve cuántos tiles se dibujaron."""
        self._screen.fill(COLOR_BACKGROUND)
        left, top = self._viewport_origin(camera_x, camera_y)
        tick = pygame.time.get_ticks() // 400
        drawn_tiles = 0

        for chunk_x, chunk_y in self.visible_chunks(camera_x, camera_y):
            chunk = world.get_chunk(chunk_x, chunk_y)
            chunk_left = round((chunk_x * CHUNK_PIXELS - left) * RENDER_SCALE)
            chunk_top = round((chunk_y * CHUNK_PIXELS - top) * RENDER_SCALE)

            for local_y, row in enumerate(chunk.tiles):
                screen_y = chunk_top + local_y * RENDER_TILE_SIZE
                world_y = chunk.chunk_y * len(row) + local_y
                for local_x, tile in enumerate(row):
                    screen_x = chunk_left + local_x * RENDER_TILE_SIZE
                    tile_id = int(tile)
                    world_x = chunk.chunk_x * len(row) + local_x
                    tile_hash = _tile_hash(world_x, world_y)
                    variants = TILE_COLOR_VARIANTS[tile_id]
                    pygame.draw.rect(
                        self._screen,
                        variants[tile_hash % len(variants)],
                        (screen_x, screen_y, RENDER_TILE_SIZE, RENDER_TILE_SIZE),
                    )
                    if tile_id == TILE_WATER:
                        self._draw_shore(
                            chunk,
                            local_x,
                            local_y,
                            screen_x,
                            screen_y,
                        )
                    self._decorate(tile_id, screen_x, screen_y, tile_hash, tick)
                    drawn_tiles += 1

        return drawn_tiles

    def _entity_sprite(self, sprite_key: str) -> pygame.Surface | None:
        if self._sprites is None:
            return None
        cached = self._scaled_sprites.get(sprite_key)
        if cached is not None:
            return cached
        base = self._sprites.get(sprite_key)
        if base.get_width() == SPRITE_SIZE == ENTITY_DRAW_SIZE:
            scaled = base
        else:
            scaled = pygame.transform.scale(
                base,
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
        """Dibuja a Mike y a los zombis con sombra y sprite."""
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
            pygame.draw.ellipse(
                self._screen,
                SHADOW_COLOR,
                (rect.centerx - 8, rect.bottom - 5, 16, 5),
            )
            sprite = self._entity_sprite(f"{SPRITE_ZOMBIE_PREFIX}{zombie.kind}")
            if sprite is None:
                pygame.draw.rect(self._screen, ZOMBIE_COLORS[zombie.kind], rect)
            else:
                self._screen.blit(sprite, rect.topleft)
            if zombie.health < zombie.max_health:
                bar_width = 18
                bar_x = rect.centerx - bar_width // 2
                bar_y = rect.top - 5
                pygame.draw.rect(
                    self._screen,
                    ZOMBIE_HEALTH_BACKGROUND,
                    (bar_x, bar_y, bar_width, 3),
                )
                ratio = zombie.health / zombie.max_health
                pygame.draw.rect(
                    self._screen,
                    ZOMBIE_HEALTH_COLOR,
                    (bar_x, bar_y, int(bar_width * ratio), 3),
                )

        screen_x = round((mike.pos_x * TILE_SIZE - left) * RENDER_SCALE) + offset
        screen_y = round((mike.pos_y * TILE_SIZE - top) * RENDER_SCALE) + offset
        mike_rect = pygame.Rect(screen_x, screen_y, ENTITY_DRAW_SIZE, ENTITY_DRAW_SIZE)
        if not viewport.colliderect(mike_rect):
            return
        pygame.draw.ellipse(
            self._screen,
            SHADOW_COLOR,
            (mike_rect.centerx - 9, mike_rect.bottom - 6, 18, 6),
        )
        pygame.draw.ellipse(
            self._screen,
            MIKE_RING_COLOR,
            (mike_rect.centerx - 13, mike_rect.bottom - 9, 26, 9),
            width=1,
        )
        sprite_key = SPRITE_MIKE_HURT if mike.health <= 30 else SPRITE_MIKE
        sprite = self._entity_sprite(sprite_key)
        if sprite is None:
            pygame.draw.rect(self._screen, MIKE_COLOR, mike_rect)
        else:
            self._screen.blit(sprite, mike_rect.topleft)
