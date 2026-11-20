"""Punto de entrada de MIKE: SEÑAL DE SUPERVIVENCIA.

Crea una run nueva y abre la ventana del mundo procedural con el HUD de
Mike. El control del personaje llegará en fases posteriores.
"""

from __future__ import annotations

import logging
import random
import secrets
import sqlite3

import pygame

from agent.client import AgentClient, AgentUnavailable
from config import (
    DEFAULT_TRAIT,
    FPS,
    MAX_FRAME_DELTA,
    RADIO_COST_MAX,
    RADIO_COST_MIN,
    SEED_BITS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from db.database import get_connection, init_db
from db.repositories import AgentStateRepository, Run, RunRepository
from game.loop import GameSession
from game.renderer import Renderer
from game.world import generate_refugio7
from ui.chat import ChatPanel
from ui.hud import Hud

logger = logging.getLogger(__name__)


def _send_operator_message(
    session: GameSession,
    agent: AgentClient,
    chat: ChatPanel,
    text: str,
) -> None:
    """Envía un mensaje de radio, cobra batería y muestra la respuesta."""
    chat.add_message("operator", text)
    if session.is_over:
        chat.add_message("system", "Mike ya no responde.")
        return
    if not agent.available:
        chat.add_message("system", "Radio sin enlace: define DEEPSEEK_API_KEY en .env.")
        return

    cost = random.randint(RADIO_COST_MIN, RADIO_COST_MAX)
    if not session.mike.spend_radio(cost):
        chat.add_message("system", "Batería de radio agotada.")
        return
    session.persist()
    try:
        result = agent.respond(text)
    except AgentUnavailable as error:
        chat.add_message("system", str(error))
        return
    chat.add_message("assistant", result.text)


def create_run(seed: int | None = None) -> Run:
    """Crea una run con su estado inicial de Mike y devuelve la run."""
    actual_seed = secrets.randbits(SEED_BITS) if seed is None else seed
    refugio7_x, refugio7_y = generate_refugio7(actual_seed)
    with get_connection() as connection:
        run = RunRepository(connection).create(
            seed=actual_seed,
            refugio7_x=refugio7_x,
            refugio7_y=refugio7_y,
            trait=DEFAULT_TRAIT,
        )
        AgentStateRepository(connection).create(run.id)
    logger.info("Run %s creada con seed %s", run.id, run.seed)
    return run


def run_game(
    run: Run,
    connection: sqlite3.Connection,
    max_frames: int | None = None,
) -> int:
    """Abre la ventana y ejecuta el bucle de render hasta cerrar."""
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        session = GameSession(run, connection)
        agent = AgentClient(session)
        renderer = Renderer(screen)
        hud = Hud(screen)
        chat = ChatPanel(screen)

        shown_events = 0
        game_over_shown = False
        frames = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                    continue
                submitted = chat.handle_event(event)
                if submitted is not None:
                    _send_operator_message(session, agent, chat, submitted)

            delta_seconds = min(clock.tick(FPS) / 1000.0, MAX_FRAME_DELTA)
            session.update(delta_seconds)
            for text in session.events[shown_events:]:
                chat.add_message("system", text)
            shown_events = len(session.events)
            if session.is_over and not game_over_shown:
                chat.add_message(
                    "system",
                    f"MIKE HA MUERTO ({session.mike.cause_of_death}).",
                )
                game_over_shown = True

            chat.update(delta_seconds)
            renderer.draw(session.world, session.camera_x, session.camera_y)
            hud.draw(session.mike)
            chat.draw()
            pygame.display.flip()

            frames += 1
            if max_frames is not None and frames >= max_frames:
                running = False
    finally:
        pygame.quit()

    return 0


def main() -> int:
    """Inicializa la base de datos, crea una run y abre el juego."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    init_db()
    run = create_run()
    print(
        f"Run #{run.id} creada - seed={run.seed}, "
        f"refugio7=({run.refugio7_x}, {run.refugio7_y}), trait={run.trait}"
    )
    with get_connection() as connection:
        return run_game(run, connection)


if __name__ == "__main__":
    raise SystemExit(main())
