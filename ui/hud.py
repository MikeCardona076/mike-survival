"""HUD con las cinco barras de estado de Mike."""

from __future__ import annotations

import pygame

from config import (
    BATTERY_BAR_COLOR,
    HEALTH_BAR_COLOR,
    HUD_BAR_BACKGROUND,
    HUD_BAR_HEIGHT,
    HUD_BAR_WIDTH,
    HUD_BORDER_COLOR,
    HUD_FONT_SIZE,
    HUD_FOOTER_HEIGHT,
    HUD_ICON_RADIUS,
    HUD_LABEL_WIDTH,
    HUD_MARGIN,
    HUD_PANEL_ALPHA,
    HUD_PANEL_COLOR,
    HUD_ROW_HEIGHT,
    HUD_TEXT_COLOR,
    HUNGER_BAR_COLOR,
    INFECTION_BAR_COLOR,
    MAX_HEALTH,
    MAX_HUNGER,
    MAX_INFECTION,
    MAX_RADIO_BATTERY,
    MAX_THIRST,
    THIRST_BAR_COLOR,
)
from game.entities import Mike


def bar_width(value: int, maximum: int, width: int) -> int:
    """Ancho proporcional de una barra, acotado a ``[0, width]``."""
    if maximum <= 0:
        raise ValueError("El máximo debe ser positivo")
    clamped = max(0, min(value, maximum))
    return int(width * clamped / maximum)


class Hud:
    """Dibuja un panel translúcido con el estado de Mike."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._font = pygame.font.Font(None, HUD_FONT_SIZE)

    def _text(self, text: str, position: tuple[int, int], color: tuple[int, int, int]) -> None:
        shadow = self._font.render(text, True, (0, 0, 0))
        self._screen.blit(shadow, (position[0] + 1, position[1] + 1))
        self._screen.blit(self._font.render(text, True, color), position)

    def draw(self, mike: Mike, trait: str = "") -> None:
        """Pinta salud, hambre, sed, infección, batería, turno y rasgo."""
        bars = (
            ("SALUD", mike.health, MAX_HEALTH, HEALTH_BAR_COLOR),
            ("HAMBRE", mike.hunger, MAX_HUNGER, HUNGER_BAR_COLOR),
            ("SED", mike.thirst, MAX_THIRST, THIRST_BAR_COLOR),
            ("INFECCIÓN", mike.infection, MAX_INFECTION, INFECTION_BAR_COLOR),
            ("BATERÍA", mike.radio_battery, MAX_RADIO_BATTERY, BATTERY_BAR_COLOR),
        )
        panel_width = HUD_MARGIN * 2 + 16 + HUD_LABEL_WIDTH + HUD_BAR_WIDTH
        panel_height = HUD_MARGIN * 2 + HUD_ROW_HEIGHT * len(bars) + HUD_FOOTER_HEIGHT
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (*HUD_PANEL_COLOR, HUD_PANEL_ALPHA),
            panel.get_rect(),
            border_radius=10,
        )
        pygame.draw.rect(
            panel,
            (*HUD_BORDER_COLOR, 210),
            panel.get_rect(),
            width=1,
            border_radius=10,
        )
        self._screen.blit(panel, (HUD_MARGIN, HUD_MARGIN))

        y = HUD_MARGIN * 2
        for label, value, maximum, color in bars:
            pygame.draw.circle(
                self._screen,
                color,
                (HUD_MARGIN * 2 + 6, y + HUD_BAR_HEIGHT // 2),
                HUD_ICON_RADIUS,
            )
            self._text(f"{label} {value}", (HUD_MARGIN * 2 + 16, y), HUD_TEXT_COLOR)
            bar_x = HUD_MARGIN * 2 + 16 + HUD_LABEL_WIDTH
            pygame.draw.rect(
                self._screen,
                HUD_BAR_BACKGROUND,
                (bar_x, y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT),
                border_radius=6,
            )
            pygame.draw.rect(
                self._screen,
                color,
                (bar_x, y, bar_width(value, maximum, HUD_BAR_WIDTH), HUD_BAR_HEIGHT),
                border_radius=6,
            )
            if value > 0:
                pygame.draw.line(
                    self._screen,
                    (255, 255, 255),
                    (bar_x + 2, y + 2),
                    (bar_x + max(2, bar_width(value, maximum, HUD_BAR_WIDTH) - 3), y + 2),
                )
            y += HUD_ROW_HEIGHT

        footer = f"TURNO {mike.turn_count}"
        if trait:
            footer += f" · {trait.upper()}"
        self._text(footer, (HUD_MARGIN * 2, y + 3), HUD_TEXT_COLOR)
