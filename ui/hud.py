"""HUD con las cinco barras de estado de Mike."""

from __future__ import annotations

import pygame

from config import (
    BATTERY_BAR_COLOR,
    HEALTH_BAR_COLOR,
    HUD_BAR_BACKGROUND,
    HUD_BAR_HEIGHT,
    HUD_BAR_WIDTH,
    HUD_FONT_SIZE,
    HUD_LABEL_WIDTH,
    HUD_MARGIN,
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
    """Dibuja el panel de estado en la esquina superior izquierda."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._font = pygame.font.Font(None, HUD_FONT_SIZE)

    def draw(self, mike: Mike) -> None:
        """Pinta salud, hambre, sed, infección, batería y turno."""
        bars = (
            ("SALUD", mike.health, MAX_HEALTH, HEALTH_BAR_COLOR),
            ("HAMBRE", mike.hunger, MAX_HUNGER, HUNGER_BAR_COLOR),
            ("SED", mike.thirst, MAX_THIRST, THIRST_BAR_COLOR),
            ("INFECCIÓN", mike.infection, MAX_INFECTION, INFECTION_BAR_COLOR),
            ("BATERÍA", mike.radio_battery, MAX_RADIO_BATTERY, BATTERY_BAR_COLOR),
        )
        panel_width = HUD_MARGIN * 2 + HUD_LABEL_WIDTH + HUD_BAR_WIDTH
        panel_height = HUD_MARGIN * 2 + HUD_ROW_HEIGHT * (len(bars) + 1)
        pygame.draw.rect(
            self._screen,
            HUD_PANEL_COLOR,
            (0, 0, panel_width, panel_height),
        )

        y = HUD_MARGIN
        for label, value, maximum, color in bars:
            self._screen.blit(
                self._font.render(f"{label} {value}", True, HUD_TEXT_COLOR),
                (HUD_MARGIN, y),
            )
            bar_x = HUD_MARGIN + HUD_LABEL_WIDTH
            pygame.draw.rect(
                self._screen,
                HUD_BAR_BACKGROUND,
                (bar_x, y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT),
            )
            pygame.draw.rect(
                self._screen,
                color,
                (bar_x, y, bar_width(value, maximum, HUD_BAR_WIDTH), HUD_BAR_HEIGHT),
            )
            y += HUD_ROW_HEIGHT

        turn_text = self._font.render(f"TURNO {mike.turn_count}", True, HUD_TEXT_COLOR)
        self._screen.blit(turn_text, (HUD_MARGIN, y))
