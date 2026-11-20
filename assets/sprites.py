"""Sprites procedurales en pixel art, cacheados en SQLite."""

from __future__ import annotations

import io
import sqlite3

import pygame
from PIL import Image, ImageDraw

from config import (
    ASSET_TYPE_SPRITE,
    SPRITE_ITEM_PREFIX,
    SPRITE_KEYS,
    SPRITE_MIKE,
    SPRITE_MIKE_HURT,
    SPRITE_SIZE,
    SPRITE_ZOMBIE_PREFIX,
)
from db.repositories import AssetCacheRepository


def _humanoid(
    draw: ImageDraw.ImageDraw,
    skin: tuple[int, int, int],
    clothes: tuple[int, int, int],
    pants: tuple[int, int, int],
    hair: tuple[int, int, int],
    *,
    broad: bool = False,
) -> None:
    left = 3 if broad else 4
    right = 12 if broad else 11
    draw.rectangle((5, 2, 10, 7), fill=skin)
    draw.rectangle((4, 1, 11, 3), fill=hair)
    draw.rectangle((left, 8, right, 12), fill=clothes)
    draw.rectangle((left - 1, 8, left, 11), fill=skin)
    draw.rectangle((right, 8, right + 1, 11), fill=skin)
    draw.rectangle((left + 1, 13, left + 3, 15), fill=pants)
    draw.rectangle((right - 3, 13, right - 1, 15), fill=pants)
    draw.point((6, 5), fill=(20, 20, 20))
    draw.point((9, 5), fill=(20, 20, 20))


def _draw_mike(draw: ImageDraw.ImageDraw) -> None:
    _humanoid(
        draw,
        skin=(214, 174, 132),
        clothes=(54, 92, 138),
        pants=(46, 52, 60),
        hair=(52, 38, 30),
    )


def _draw_mike_hurt(draw: ImageDraw.ImageDraw) -> None:
    _draw_mike(draw)
    for point in ((6, 9), (9, 10), (8, 12), (5, 11)):
        draw.point(point, fill=(190, 40, 40))


def _draw_walker(draw: ImageDraw.ImageDraw) -> None:
    _humanoid(
        draw,
        skin=(116, 152, 84),
        clothes=(92, 78, 56),
        pants=(58, 54, 46),
        hair=(40, 44, 32),
    )
    draw.point((8, 6), fill=(210, 60, 60))


def _draw_runner(draw: ImageDraw.ImageDraw) -> None:
    _humanoid(
        draw,
        skin=(156, 170, 82),
        clothes=(78, 62, 44),
        pants=(52, 48, 42),
        hair=(46, 42, 32),
    )
    draw.rectangle((4, 13, 11, 14), fill=(98, 70, 46))


def _draw_brute(draw: ImageDraw.ImageDraw) -> None:
    _humanoid(
        draw,
        skin=(122, 88, 72),
        clothes=(72, 50, 44),
        pants=(44, 40, 38),
        hair=(36, 30, 28),
        broad=True,
    )
    draw.rectangle((3, 9, 12, 10), fill=(100, 38, 38))


def _draw_screecher(draw: ImageDraw.ImageDraw) -> None:
    _humanoid(
        draw,
        skin=(132, 96, 156),
        clothes=(64, 50, 76),
        pants=(48, 42, 54),
        hair=(40, 30, 48),
    )
    draw.rectangle((7, 6, 8, 7), fill=(230, 220, 255))


def _draw_food(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((5, 4, 10, 12), fill=(140, 148, 152))
    draw.rectangle((5, 6, 10, 9), fill=(188, 196, 190))
    draw.rectangle((6, 3, 9, 4), fill=(92, 98, 100))


def _draw_water(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((6, 2, 9, 4), fill=(60, 110, 160))
    draw.rectangle((5, 4, 10, 13), fill=(88, 162, 210))
    draw.rectangle((6, 7, 9, 8), fill=(210, 235, 245))


def _draw_suppressor(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((7, 2, 8, 7), fill=(210, 214, 218))
    draw.rectangle((6, 7, 9, 11), fill=(180, 190, 200))
    draw.rectangle((6, 11, 9, 13), fill=(220, 60, 60))
    draw.point((7, 2), fill=(230, 240, 250))


def _draw_bandage(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((4, 5, 11, 11), fill=(232, 230, 220))
    draw.rectangle((6, 7, 9, 9), fill=(190, 60, 60))
    draw.point((7, 7), fill=(240, 240, 235))
    draw.point((8, 8), fill=(240, 240, 235))


_BUILDERS = {
    SPRITE_MIKE: _draw_mike,
    SPRITE_MIKE_HURT: _draw_mike_hurt,
    f"{SPRITE_ZOMBIE_PREFIX}walker": _draw_walker,
    f"{SPRITE_ZOMBIE_PREFIX}runner": _draw_runner,
    f"{SPRITE_ZOMBIE_PREFIX}brute": _draw_brute,
    f"{SPRITE_ZOMBIE_PREFIX}screecher": _draw_screecher,
    f"{SPRITE_ITEM_PREFIX}food": _draw_food,
    f"{SPRITE_ITEM_PREFIX}water": _draw_water,
    f"{SPRITE_ITEM_PREFIX}suppressor": _draw_suppressor,
    f"{SPRITE_ITEM_PREFIX}bandage": _draw_bandage,
}


def build_sprite_png(asset_key: str) -> bytes:
    """Genera un PNG RGBA de 16x16 para la clave pedida."""
    builder = _BUILDERS.get(asset_key)
    if builder is None:
        raise ValueError(f"Sprite desconocido: {asset_key}")
    image = Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    builder(draw)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class SpriteSet:
    """Carga perezosa de sprites, usando ``assets_cache`` como caché."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._repository = AssetCacheRepository(connection)
        self._surfaces: dict[str, pygame.Surface] = {}
        for key in SPRITE_KEYS:
            self.get(key)

    def get(self, asset_key: str) -> pygame.Surface:
        """Devuelve la superficie pygame de un sprite."""
        cached = self._surfaces.get(asset_key)
        if cached is not None:
            return cached
        data = self._repository.get(asset_key)
        if data is None:
            data = build_sprite_png(asset_key)
            self._repository.save(
                asset_key,
                ASSET_TYPE_SPRITE,
                f"Sprite procedural {asset_key}",
                data,
                "{}",
            )
        surface = pygame.image.load(io.BytesIO(data)).convert_alpha()
        self._surfaces[asset_key] = surface
        return surface
