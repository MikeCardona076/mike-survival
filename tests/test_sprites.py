"""Tests de sprites procedurales y caché de assets."""

from __future__ import annotations

import io
import os
import sqlite3
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402
from PIL import Image  # noqa: E402

from assets.sprites import SpriteSet, build_sprite_png  # noqa: E402
from config import ASSET_TYPE_SPRITE, SPRITE_KEYS, SPRITE_SIZE  # noqa: E402
from db.repositories import AssetCacheRepository  # noqa: E402


@pytest.fixture(scope="module")
def screen() -> Iterator[pygame.Surface]:
    pygame.init()
    surface = pygame.display.set_mode((320, 240))
    yield surface
    pygame.quit()


def test_ten_valid_png_sprites() -> None:
    assert len(SPRITE_KEYS) == 10
    for key in SPRITE_KEYS:
        data = build_sprite_png(key)
        assert data.startswith(b"\x89PNG")
        image = Image.open(io.BytesIO(data))
        assert image.size == (SPRITE_SIZE, SPRITE_SIZE)
        assert image.mode == "RGBA"


def test_unknown_sprite_raises() -> None:
    with pytest.raises(ValueError):
        build_sprite_png("no_existe")


def test_asset_cache_roundtrip(connection: sqlite3.Connection) -> None:
    repository = AssetCacheRepository(connection)
    data = build_sprite_png("mike")

    repository.save("mike", ASSET_TYPE_SPRITE, "Mike", data)

    assert repository.get("mike") == data
    assert repository.count() == 1


def test_sprite_set_uses_cache(
    connection: sqlite3.Connection,
    screen: pygame.Surface,
) -> None:
    sprites = SpriteSet(connection)
    repository = AssetCacheRepository(connection)

    assert repository.count() == len(SPRITE_KEYS)
    surface = sprites.get("mike")
    assert surface.get_size() == (SPRITE_SIZE, SPRITE_SIZE)
    assert sprites.get("mike") is surface
