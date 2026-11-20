"""Minimapa circular del Operador."""

from __future__ import annotations

import math

import pygame

from config import (
    MINIMAP_ALPHA,
    MINIMAP_BACKGROUND,
    MINIMAP_BORDER,
    MINIMAP_HEADER,
    MINIMAP_MARGIN,
    MINIMAP_MIKE,
    MINIMAP_PAD,
    MINIMAP_REFUGIO,
    MINIMAP_TILE,
    MINIMAP_TILES,
    MINIMAP_ZOMBIE,
    TILE_COLORS,
)


class Minimap:
    """Muestra el terreno cercano, zombis, Mike y la dirección del Refugio."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._font = pygame.font.Font(None, 18)
        self._map_size = MINIMAP_TILES * MINIMAP_TILE
        self._panel_size = self._map_size + MINIMAP_PAD * 2

    def draw(
        self,
        world: object,
        mike: object,
        zombies: list[object],
        run: object,
    ) -> None:
        """Pinta el minimapa en la esquina superior derecha."""
        screen_width = self._screen.get_width()
        panel_x = screen_width - MINIMAP_MARGIN - self._panel_size
        panel_y = MINIMAP_MARGIN
        panel_height = self._panel_size + MINIMAP_HEADER
        panel = pygame.Surface((self._panel_size, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (*MINIMAP_BACKGROUND, MINIMAP_ALPHA),
            panel.get_rect(),
            border_radius=10,
        )
        pygame.draw.rect(
            panel,
            (*MINIMAP_BORDER, 200),
            panel.get_rect(),
            width=1,
            border_radius=10,
        )
        self._screen.blit(panel, (panel_x, panel_y))

        title = self._font.render("MAPA", True, (200, 214, 196))
        self._screen.blit(title, (panel_x + MINIMAP_PAD, panel_y + 4))

        map_x = panel_x + MINIMAP_PAD
        map_y = panel_y + MINIMAP_HEADER + 2
        half = MINIMAP_TILES // 2
        center_x = map_x + self._map_size // 2
        center_y = map_y + self._map_size // 2
        mike_x = int(mike.pos_x)
        mike_y = int(mike.pos_y)

        for local_y in range(MINIMAP_TILES):
            for local_x in range(MINIMAP_TILES):
                world_x = mike_x + local_x - half
                world_y = mike_y + local_y - half
                tile = int(world.get_tile(world_x, world_y))
                pygame.draw.rect(
                    self._screen,
                    TILE_COLORS[tile],
                    (
                        map_x + local_x * MINIMAP_TILE,
                        map_y + local_y * MINIMAP_TILE,
                        MINIMAP_TILE,
                        MINIMAP_TILE,
                    ),
                )

        for zombie in zombies:
            if not getattr(zombie, "alive", False):
                continue
            offset_x = int(zombie.x) - mike_x
            offset_y = int(zombie.y) - mike_y
            if abs(offset_x) > half or abs(offset_y) > half:
                continue
            pygame.draw.circle(
                self._screen,
                MINIMAP_ZOMBIE,
                (
                    center_x + offset_x * MINIMAP_TILE + MINIMAP_TILE // 2,
                    center_y + offset_y * MINIMAP_TILE + MINIMAP_TILE // 2,
                ),
                3,
            )

        delta_x = run.refugio7_x - mike_x
        delta_y = run.refugio7_y - mike_y
        distance = max(abs(delta_x), abs(delta_y))
        if distance > 0:
            scale = min(1.0, (half - 1) / distance)
            pygame.draw.circle(
                self._screen,
                MINIMAP_REFUGIO,
                (
                    int(center_x + delta_x * scale * MINIMAP_TILE),
                    int(center_y + delta_y * scale * MINIMAP_TILE),
                ),
                4,
            )
            if distance > half:
                angle = math.atan2(delta_y, delta_x)
                pygame.draw.line(
                    self._screen,
                    MINIMAP_REFUGIO,
                    (center_x, center_y),
                    (
                        int(center_x + math.cos(angle) * (half - 1) * MINIMAP_TILE),
                        int(center_y + math.sin(angle) * (half - 1) * MINIMAP_TILE),
                    ),
                    1,
                )

        pygame.draw.circle(self._screen, (20, 22, 24), (center_x, center_y), 5)
        pygame.draw.circle(self._screen, MINIMAP_MIKE, (center_x, center_y), 3)
