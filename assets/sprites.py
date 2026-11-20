"""Sprites procedurales en pixel art de 24x24, cacheados en SQLite."""

from __future__ import annotations

import io
import sqlite3

import pygame
from PIL import Image, ImageDraw

from config import (
    ASSET_TYPE_SPRITE,
    SPRITE_CACHE_VERSION,
    SPRITE_ITEM_PREFIX,
    SPRITE_KEYS,
    SPRITE_MIKE,
    SPRITE_MIKE_HURT,
    SPRITE_SIZE,
    SPRITE_ZOMBIE_PREFIX,
)
from db.repositories import AssetCacheRepository

_OUTLINE = (18, 20, 24)
_SKIN = (216, 176, 132)
_HAIR = (52, 38, 30)
_JACKET = (52, 92, 138)
_JACKET_LIGHT = (72, 116, 166)
_PANTS = (46, 52, 60)
_BOOTS = (28, 30, 34)


def _box(
    draw: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    fill: tuple[int, int, int],
) -> None:
    draw.rectangle(bounds, fill=fill, outline=_OUTLINE)


def _head(
    draw: ImageDraw.ImageDraw,
    skin: tuple[int, int, int],
    hair: tuple[int, int, int],
    *,
    x: int = 8,
    y: int = 2,
    mouth: bool = True,
) -> None:
    _box(draw, (x, y, x + 8, y + 8), skin)
    draw.rectangle((x, y, x + 8, y + 2), fill=hair)
    draw.rectangle((x, y + 2, x + 1, y + 5), fill=hair)
    draw.point((x + 3, y + 5), fill=_OUTLINE)
    draw.point((x + 6, y + 5), fill=_OUTLINE)
    if mouth:
        draw.line((x + 3, y + 7, x + 6, y + 7), fill=(140, 84, 70))


def _draw_mike(draw: ImageDraw.ImageDraw, *, hurt: bool = False) -> None:
    _box(draw, (8, 17, 11, 23), _PANTS)
    _box(draw, (13, 17, 16, 23), _PANTS)
    draw.rectangle((8, 21, 11, 23), fill=_BOOTS)
    draw.rectangle((13, 21, 16, 23), fill=_BOOTS)
    _box(draw, (6, 10, 17, 18), _JACKET)
    draw.rectangle((8, 11, 10, 16), fill=_JACKET_LIGHT)
    draw.line((12, 11, 12, 17), fill=(28, 40, 54))
    _box(draw, (4, 10, 7, 17), _JACKET)
    _box(draw, (17, 10, 20, 17), _JACKET)
    draw.rectangle((4, 15, 7, 18), fill=_SKIN)
    draw.rectangle((17, 15, 20, 18), fill=_SKIN)
    _head(draw, _SKIN, _HAIR)
    draw.rectangle((7, 10, 17, 11), fill=(154, 62, 52))
    if hurt:
        for x, y in ((9, 12), (15, 13), (10, 15), (14, 16)):
            draw.point((x, y), fill=(196, 48, 48))
        draw.line((15, 4, 17, 6), fill=(180, 42, 42))


def _draw_walker(draw: ImageDraw.ImageDraw) -> None:
    skin = (116, 154, 86)
    _box(draw, (8, 17, 11, 23), (58, 54, 46))
    _box(draw, (13, 17, 16, 23), (58, 54, 46))
    _box(draw, (6, 10, 17, 18), (92, 78, 56))
    draw.rectangle((9, 12, 10, 13), fill=(48, 40, 32))
    draw.rectangle((14, 14, 16, 15), fill=(48, 40, 32))
    _box(draw, (4, 11, 7, 17), skin)
    draw.rectangle((4, 16, 7, 18), fill=skin)
    draw.rectangle((17, 12, 19, 17), fill=skin)
    _head(draw, skin, (42, 46, 34))
    draw.point((10, 5), fill=(210, 52, 52))
    draw.line((11, 9, 15, 9), fill=(66, 30, 30))


def _draw_runner(draw: ImageDraw.ImageDraw) -> None:
    skin = (160, 176, 84)
    _box(draw, (9, 17, 11, 23), (54, 50, 44))
    _box(draw, (13, 18, 15, 23), (54, 50, 44))
    _box(draw, (7, 10, 16, 17), (78, 64, 46))
    _box(draw, (3, 10, 6, 16), skin)
    _box(draw, (17, 9, 20, 16), skin)
    _head(draw, skin, (46, 42, 32), x=8, y=1)
    draw.point((10, 4), fill=(230, 220, 120))
    draw.point((14, 4), fill=(230, 220, 120))
    draw.line((10, 8, 14, 8), fill=(60, 34, 30))


def _draw_brute(draw: ImageDraw.ImageDraw) -> None:
    skin = (128, 92, 76)
    _box(draw, (7, 18, 11, 23), (44, 40, 38))
    _box(draw, (14, 18, 18, 23), (44, 40, 38))
    _box(draw, (4, 9, 20, 19), (74, 52, 44))
    _box(draw, (2, 10, 5, 17), skin)
    _box(draw, (19, 10, 22, 17), skin)
    _head(draw, skin, (36, 30, 28), x=6, y=0)
    draw.rectangle((5, 15, 19, 16), fill=(104, 38, 38))
    draw.line((8, 5, 10, 7), fill=(170, 40, 40))
    draw.line((14, 3, 12, 6), fill=(170, 40, 40))


def _draw_screecher(draw: ImageDraw.ImageDraw) -> None:
    skin = (138, 100, 164)
    _box(draw, (9, 17, 11, 23), (48, 42, 54))
    _box(draw, (13, 18, 15, 23), (48, 42, 54))
    _box(draw, (8, 10, 16, 18), (64, 50, 76))
    _box(draw, (4, 9, 7, 17), skin)
    _box(draw, (17, 9, 20, 17), skin)
    draw.rectangle((4, 16, 7, 19), fill=skin)
    draw.rectangle((17, 16, 20, 19), fill=skin)
    _head(draw, skin, (40, 30, 48), x=8, y=1)
    draw.rectangle((10, 6, 14, 9), fill=(22, 18, 26))
    draw.rectangle((11, 7, 13, 8), fill=(236, 230, 246))


def _draw_food(draw: ImageDraw.ImageDraw) -> None:
    _box(draw, (6, 5, 18, 20), (148, 156, 160))
    draw.rectangle((8, 7, 16, 12), fill=(198, 206, 196))
    draw.rectangle((8, 13, 16, 18), fill=(120, 70, 54))
    draw.ellipse((8, 3, 16, 7), fill=(186, 194, 196), outline=_OUTLINE)
    draw.point((10, 15), fill=(230, 220, 180))
    draw.point((14, 17), fill=(230, 220, 180))


def _draw_water(draw: ImageDraw.ImageDraw) -> None:
    _box(draw, (9, 4, 15, 21), (94, 170, 220))
    draw.rectangle((9, 1, 15, 5), fill=(196, 220, 230))
    draw.rectangle((8, 6, 10, 8), fill=(134, 198, 236))
    draw.rectangle((8, 12, 10, 18), fill=(134, 198, 236))
    draw.rectangle((9, 9, 15, 10), fill=(220, 238, 246))


def _draw_suppressor(draw: ImageDraw.ImageDraw) -> None:
    _box(draw, (9, 5, 15, 17), (206, 212, 218))
    draw.rectangle((10, 7, 14, 9), fill=(240, 244, 248))
    _box(draw, (10, 17, 14, 21), (198, 72, 72))
    draw.rectangle((11, 2, 13, 6), fill=(150, 190, 210))
    draw.line((12, 0, 12, 3), fill=(210, 226, 236))
    draw.point((12, 19), fill=(240, 240, 236))


def _draw_bandage(draw: ImageDraw.ImageDraw) -> None:
    _box(draw, (5, 6, 19, 19), (232, 230, 220))
    draw.ellipse((8, 8, 16, 17), fill=(206, 204, 194), outline=_OUTLINE)
    draw.rectangle((11, 9, 13, 16), fill=(190, 66, 66))
    draw.rectangle((9, 11, 15, 13), fill=(190, 66, 66))


_BUILDERS = {
    SPRITE_MIKE: _draw_mike,
    SPRITE_MIKE_HURT: lambda draw: _draw_mike(draw, hurt=True),
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
    """Genera un PNG RGBA de 24x24 para la clave pedida."""
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
    """Carga sprites, usando ``assets_cache`` con clave versionada."""

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
        cache_key = f"{SPRITE_CACHE_VERSION}:{asset_key}"
        data = self._repository.get(cache_key)
        if data is None:
            data = build_sprite_png(asset_key)
            self._repository.save(
                cache_key,
                ASSET_TYPE_SPRITE,
                f"Sprite procedural {asset_key}",
                data,
                "{}",
            )
        surface = pygame.image.load(io.BytesIO(data)).convert_alpha()
        self._surfaces[asset_key] = surface
        return surface
