"""Punto de entrada de MIKE: SEÑAL DE SUPERVIVENCIA.

Crea una run nueva y abre la ventana del mundo procedural con el HUD de
Mike. El control del personaje llegará en fases posteriores.
"""

from __future__ import annotations

import logging
import secrets
import sqlite3

import pygame

from config import (
    DEFAULT_TRAIT,
    FPS,
    MAX_FRAME_DELTA,
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
from ui.hud import Hud

logger = logging.getLogger(__name__)


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
        renderer = Renderer(screen)
        hud = Hud(screen)

        frames = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

            delta_seconds = min(clock.tick(FPS) / 1000.0, MAX_FRAME_DELTA)
            session.update(delta_seconds)
            renderer.draw(session.world, session.camera_x, session.camera_y)
            hud.draw(session.mike)
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
