"""Panel de chat de radio entre el Operador y Mike."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from config import (
    CHAT_BACKGROUND,
    CHAT_BORDER_COLOR,
    CHAT_FONT_SIZE,
    CHAT_HEADER_COLOR,
    CHAT_HEIGHT,
    CHAT_INPUT_BACKGROUND,
    CHAT_INPUT_COLOR,
    CHAT_MARGIN,
    CHAT_MAX_ENTRIES,
    CHAT_MAX_INPUT,
    CHAT_MIKE_COLOR,
    CHAT_OPERATOR_COLOR,
    CHAT_PANEL_ALPHA,
    CHAT_SYSTEM_COLOR,
    CHAT_TYPEWRITER_CPS,
    CHAT_VISIBLE_MESSAGES,
)


@dataclass(slots=True)
class ChatEntry:
    """Una línea del historial de radio."""

    role: str
    text: str


class ChatPanel:
    """Historial con typewriter y campo de entrada de una línea."""

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        self._font = pygame.font.Font(None, CHAT_FONT_SIZE)
        self._entries: list[ChatEntry] = []
        self._input = ""
        self._typing_progress = 0.0
        self._waiting = False

    def set_waiting(self, waiting: bool) -> None:
        """Muestra u oculta el estado «Mike está respondiendo»."""
        self._waiting = waiting

    @property
    def input_text(self) -> str:
        """Texto que el Operador está escribiendo."""
        return self._input

    def add_message(self, role: str, text: str) -> None:
        """Añade un mensaje al historial."""
        if not text:
            return
        self._entries.append(ChatEntry(role, text))
        if len(self._entries) > CHAT_MAX_ENTRIES:
            self._entries = self._entries[-CHAT_MAX_ENTRIES:]
        self._typing_progress = 0.0 if role == "assistant" else float(len(text))

    def update(self, delta_seconds: float) -> None:
        """Avanza el efecto typewriter del último mensaje de Mike."""
        if not self._entries:
            return
        last = self._entries[-1]
        if last.role != "assistant":
            return
        total = len(last.text)
        if self._typing_progress < total:
            self._typing_progress = min(
                total,
                self._typing_progress + delta_seconds * CHAT_TYPEWRITER_CPS,
            )

    def visible_entries(self) -> list[ChatEntry]:
        """Mensajes visibles, con el typewriter aplicado al último."""
        visible = [
            ChatEntry(entry.role, entry.text) for entry in self._entries[-CHAT_VISIBLE_MESSAGES:]
        ]
        if visible and visible[-1].role == "assistant":
            visible[-1].text = visible[-1].text[: int(self._typing_progress)]
        return visible

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Procesa una tecla; devuelve el texto enviado, si lo hay."""
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_RETURN:
            text = self._input.strip()
            if not text:
                return None
            self._input = ""
            return text
        if event.key == pygame.K_BACKSPACE:
            self._input = self._input[:-1]
            return None
        if event.key == pygame.K_ESCAPE:
            return None
        character = getattr(event, "unicode", "")
        if character and character.isprintable() and len(self._input) < CHAT_MAX_INPUT:
            self._input += character
        return None

    def _wrap(self, text: str, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if self._font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def draw(self) -> None:
        """Pinta el panel en la parte inferior de la pantalla."""
        screen_width, screen_height = self._screen.get_size()
        panel_rect = pygame.Rect(0, screen_height - CHAT_HEIGHT, screen_width, CHAT_HEIGHT)
        panel = pygame.Surface((screen_width, CHAT_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (*CHAT_BACKGROUND, CHAT_PANEL_ALPHA),
            panel.get_rect(),
            border_radius=12,
        )
        pygame.draw.rect(
            panel,
            (*CHAT_BORDER_COLOR, 190),
            panel.get_rect(),
            width=1,
            border_radius=12,
        )
        self._screen.blit(panel, panel_rect.topleft)

        line_height = self._font.get_linesize()
        inner_width = screen_width - CHAT_MARGIN * 2
        header_y = panel_rect.top + 10
        pygame.draw.circle(
            self._screen,
            CHAT_HEADER_COLOR,
            (CHAT_MARGIN + 4, header_y + 6),
            4,
        )
        header_text = "RADIO · ENLACE CON MIKE"
        if self._waiting:
            dots = "." * (pygame.time.get_ticks() // 400 % 4)
            header_text = f"MIKE ESTÁ RESPONDIENDO{dots}"
        header = self._font.render(header_text, True, CHAT_HEADER_COLOR)
        self._screen.blit(header, (CHAT_MARGIN + 14, header_y))

        input_height = line_height + 8
        input_rect = pygame.Rect(
            CHAT_MARGIN,
            panel_rect.bottom - CHAT_MARGIN - input_height,
            screen_width - CHAT_MARGIN * 2,
            input_height,
        )
        pygame.draw.rect(
            self._screen,
            CHAT_INPUT_BACKGROUND,
            input_rect,
            border_radius=8,
        )
        pygame.draw.rect(
            self._screen,
            CHAT_BORDER_COLOR,
            input_rect,
            width=1,
            border_radius=8,
        )

        messages_top = panel_rect.top + 10 + line_height + 6
        available_lines = max(1, (input_rect.top - messages_top - 4) // line_height)
        colored_lines: list[tuple[str, tuple[int, int, int]]] = []
        prefixes = {"operator": "TÚ> ", "assistant": "MIKE> ", "system": "· "}
        colors = {
            "operator": CHAT_OPERATOR_COLOR,
            "assistant": CHAT_MIKE_COLOR,
            "system": CHAT_SYSTEM_COLOR,
        }
        for entry in self.visible_entries():
            prefix = prefixes.get(entry.role, "")
            for line in self._wrap(prefix + entry.text, inner_width):
                colored_lines.append((line, colors.get(entry.role, CHAT_INPUT_COLOR)))

        for line, color in colored_lines[-available_lines:]:
            self._screen.blit(
                self._font.render(line, True, color),
                (CHAT_MARGIN, messages_top),
            )
            messages_top += line_height

        text_surface = self._font.render(
            f"> {self._input}",
            True,
            CHAT_INPUT_COLOR,
        )
        self._screen.blit(text_surface, (input_rect.x + 8, input_rect.y + 4))
        if pygame.time.get_ticks() // 500 % 2 == 0:
            cursor_x = input_rect.x + 8 + text_surface.get_width()
            pygame.draw.line(
                self._screen,
                CHAT_INPUT_COLOR,
                (cursor_x + 2, input_rect.y + 5),
                (cursor_x + 2, input_rect.bottom - 6),
            )
