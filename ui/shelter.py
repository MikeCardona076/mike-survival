"""Panel del refugio y taller del Operador."""

from __future__ import annotations

import pygame

from config import (
    CHAT_HEIGHT,
    HEAL_PRICE,
    HUD_BORDER_COLOR,
    HUD_PANEL_COLOR,
    HUD_TEXT_COLOR,
    IRON_PACK,
    IRON_PRICE,
    ITEM_COIN,
    ITEM_IRON,
    ITEM_WOOD,
    SHELTER_IRON_COST,
    SHELTER_MAX_LEVEL,
    SHELTER_PANEL_ALPHA,
    SHELTER_PANEL_HEIGHT,
    SHELTER_PANEL_WIDTH,
    SHELTER_WOOD_COST,
    WEAPON_IRON_COST,
    WEAPON_MAX_LEVEL,
    WEAPON_WOOD_COST,
    WOOD_PACK,
    WOOD_PRICE,
)
from db.repositories import Shelter
from game.entities import Mike

_ACTION_KEYS = {
    pygame.K_1: "wood",
    pygame.K_2: "iron",
    pygame.K_3: "shelter",
    pygame.K_4: "weapon",
    pygame.K_5: "heal",
    pygame.K_b: "close",
    pygame.K_TAB: "close",
    pygame.K_ESCAPE: "close",
}


class ShelterPanel:
    """Muestra el estado del refugio y las compras disponibles."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._title_font = pygame.font.Font(None, 30)
        self._font = pygame.font.Font(None, 20)
        self._small_font = pygame.font.Font(None, 17)
        self._message = ""

    def set_message(self, message: str) -> None:
        self._message = message

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None
        return _ACTION_KEYS.get(event.key)

    def draw(self, mike: Mike, shelter: Shelter) -> None:
        screen_width, screen_height = self._screen.get_size()
        panel_x = (screen_width - SHELTER_PANEL_WIDTH) // 2
        panel_y = max(
            10,
            (screen_height - CHAT_HEIGHT - SHELTER_PANEL_HEIGHT) // 2,
        )
        panel = pygame.Surface(
            (SHELTER_PANEL_WIDTH, SHELTER_PANEL_HEIGHT),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            panel,
            (*HUD_PANEL_COLOR, SHELTER_PANEL_ALPHA),
            panel.get_rect(),
            border_radius=14,
        )
        pygame.draw.rect(
            panel,
            (*HUD_BORDER_COLOR, 220),
            panel.get_rect(),
            width=2,
            border_radius=14,
        )
        veil = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 110))
        self._screen.blit(veil, (0, 0))
        self._screen.blit(panel, (panel_x, panel_y))

        title = self._title_font.render("REFUGIO — TALLER", True, (236, 210, 110))
        self._screen.blit(title, (panel_x + 24, panel_y + 18))
        coins = mike.inventory.count(ITEM_COIN)
        wood = mike.inventory.count(ITEM_WOOD)
        iron = mike.inventory.count(ITEM_IRON)
        resources = self._font.render(
            f"Monedas: {coins}   ·   Madera: {wood}   ·   Hierro: {iron}",
            True,
            HUD_TEXT_COLOR,
        )
        self._screen.blit(resources, (panel_x + 24, panel_y + 54))

        levels = self._font.render(
            f"Refugio nivel {shelter.level}/{SHELTER_MAX_LEVEL}   ·   "
            f"Arma nivel {shelter.weapon_level}/{WEAPON_MAX_LEVEL}",
            True,
            (196, 208, 156),
        )
        self._screen.blit(levels, (panel_x + 24, panel_y + 84))

        rows = (
            f"[1] Comprar madera  — {WOOD_PRICE} monedas (+{WOOD_PACK})",
            f"[2] Comprar hierro  — {IRON_PRICE} monedas (+{IRON_PACK})",
            f"[3] Mejorar refugio — {SHELTER_WOOD_COST} madera + {SHELTER_IRON_COST} hierro",
            f"[4] Mejorar arma    — {WEAPON_WOOD_COST} madera + {WEAPON_IRON_COST} hierro",
            f"[5] Curar a Mike    — {HEAL_PRICE} monedas",
        )
        y = panel_y + 124
        for row in rows:
            self._screen.blit(
                self._font.render(row, True, HUD_TEXT_COLOR),
                (panel_x + 30, y),
            )
            y += 34

        if self._message:
            message = self._small_font.render(self._message, True, (236, 222, 150))
            self._screen.blit(message, (panel_x + 24, y + 6))

        hint = self._small_font.render(
            "[Tab]/[B]/[Esc] cerrar   ·   el tiempo se detiene en el refugio",
            True,
            (160, 164, 166),
        )
        self._screen.blit(hint, (panel_x + 24, panel_y + SHELTER_PANEL_HEIGHT - 28))
