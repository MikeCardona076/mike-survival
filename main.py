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

from agent.client import AgentClient
from agent.worker import AgentWorker
from assets.audio import AudioManager
from assets.sprites import SpriteSet
from config import (
    AUDIO_SAMPLE_RATE,
    CHAT_HEIGHT,
    FPS,
    GAME_OVER_COLOR,
    GAME_OVER_OVERLAY,
    GAME_OVER_TEXT,
    MAX_FRAME_DELTA,
    RADIO_COST_MAX,
    RADIO_COST_MIN,
    SEED_BITS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from db.database import get_connection, init_db
from db.repositories import (
    AgentStateRepository,
    MetaProgressionRepository,
    Run,
    RunRepository,
    StatsRepository,
)
from game.entities import choose_trait
from game.loop import GameSession
from game.renderer import Renderer
from game.world import generate_refugio7
from ui.chat import ChatPanel
from ui.hud import Hud
from ui.map import Minimap

logger = logging.getLogger(__name__)


def _play_event_sound(audio: AudioManager, text: str) -> None:
    lower = text.lower()
    if "muerto" in lower or "ha muerto" in lower:
        audio.play("death")
    elif "ataca" in lower or "golpea" in lower or "derriba" in lower:
        audio.play("hit")
    elif "supresor" in lower:
        audio.play("suppressor")
    elif "encuentra" in lower or "provisiones" in lower:
        audio.play("pickup")


def _draw_game_over(
    screen: pygame.Surface,
    overlay: pygame.Surface,
    title_font: pygame.font.Font,
    small_font: pygame.font.Font,
    cause: str | None,
) -> None:
    screen.blit(overlay, (0, 0))
    title = title_font.render("MIKE HA MUERTO", True, GAME_OVER_COLOR)
    subtitle = small_font.render(
        f"Causa: {cause or 'desconocida'} · Pulsa Esc",
        True,
        GAME_OVER_TEXT,
    )
    center_y = (WINDOW_HEIGHT - CHAT_HEIGHT) // 2
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, center_y)))
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, center_y + 44)))


def _queue_operator_message(
    session: GameSession,
    agent: AgentClient,
    worker: AgentWorker,
    chat: ChatPanel,
    text: str,
) -> bool:
    """Prepara el mensaje y lo lanza en segundo plano; devuelve si quedó pendiente."""
    chat.add_message("operator", text)
    if session.is_over:
        chat.add_message("system", "Mike ya no responde.")
        return False
    if not agent.available:
        chat.add_message("system", "Radio sin enlace: define DEEPSEEK_API_KEY en .env.")
        return False
    if worker.busy:
        chat.add_message("system", "Mike todavía está respondiendo.")
        return False

    cost = random.randint(RADIO_COST_MIN, RADIO_COST_MAX)
    if not session.mike.spend_radio(cost):
        chat.add_message("system", "Batería de radio agotada.")
        return False
    session.persist()
    chat.set_waiting(True)
    if not worker.submit(text):
        chat.set_waiting(False)
        chat.add_message("system", "No se pudo enviar el mensaje.")
        return False
    return True


def create_run(seed: int | None = None) -> Run:
    """Crea una run con su estado inicial de Mike y devuelve la run."""
    actual_seed = secrets.randbits(SEED_BITS) if seed is None else seed
    refugio7_x, refugio7_y = generate_refugio7(actual_seed)
    with get_connection() as connection:
        unlocked = set(MetaProgressionRepository(connection).list_keys())
        trait = choose_trait(actual_seed, unlocked)
        run = RunRepository(connection).create(
            seed=actual_seed,
            refugio7_x=refugio7_x,
            refugio7_y=refugio7_y,
            trait=trait,
        )
        AgentStateRepository(connection).create(run.id)
        StatsRepository(connection).increment_runs_played()
    logger.info("Run %s creada con seed %s", run.id, run.seed)
    return run


def run_game(
    run: Run,
    connection: sqlite3.Connection,
    max_frames: int | None = None,
) -> int:
    """Abre la ventana y ejecuta el bucle de render hasta cerrar."""
    pygame.mixer.pre_init(AUDIO_SAMPLE_RATE, -16, 1)
    pygame.init()
    worker: AgentWorker | None = None
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        session = GameSession(run, connection)
        agent = AgentClient(session)
        worker = AgentWorker(agent)
        sprites = SpriteSet(connection)
        audio = AudioManager()
        renderer = Renderer(screen, sprites)
        hud = Hud(screen)
        minimap = Minimap(screen)
        chat = ChatPanel(screen)
        game_over_font = pygame.font.Font(None, 56)
        game_over_small = pygame.font.Font(None, 24)
        game_over_panel = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT - CHAT_HEIGHT),
            pygame.SRCALPHA,
        )
        game_over_panel.fill(GAME_OVER_OVERLAY)

        shown_events = 0
        game_over_shown = False
        frames = 0
        running = True
        pending_response = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                    continue
                if pending_response:
                    continue
                submitted = chat.handle_event(event)
                if submitted is not None:
                    audio.play("radio")
                    pending_response = _queue_operator_message(
                        session,
                        agent,
                        worker,
                        chat,
                        submitted,
                    )

            if pending_response:
                result = worker.poll()
                if result is not None:
                    pending_response = False
                    chat.set_waiting(False)
                    chat.add_message(
                        "assistant" if result.ok else "system",
                        result.text,
                    )

            delta_seconds = min(clock.tick(FPS) / 1000.0, MAX_FRAME_DELTA)
            if not pending_response:
                session.update(delta_seconds)
                for text in session.events[shown_events:]:
                    chat.add_message("system", text)
                    _play_event_sound(audio, text)
                shown_events = len(session.events)
            if session.is_over and not game_over_shown:
                chat.add_message(
                    "system",
                    f"MIKE HA MUERTO ({session.mike.cause_of_death}).",
                )
                audio.play("death")
                game_over_shown = True

            chat.update(delta_seconds)
            renderer.draw(session.world, session.camera_x, session.camera_y)
            renderer.draw_entities(
                session.camera_x,
                session.camera_y,
                session.mike,
                session.zombies,
            )
            hud.draw(session.mike, session.run.trait)
            if not pending_response:
                minimap.draw(
                    session.world,
                    session.mike,
                    session.zombies,
                    session.run,
                )
            if session.is_over:
                _draw_game_over(
                    screen,
                    game_over_panel,
                    game_over_font,
                    game_over_small,
                    session.mike.cause_of_death,
                )
            chat.draw()
            pygame.display.flip()

            frames += 1
            if max_frames is not None and frames >= max_frames:
                running = False
    finally:
        if worker is not None:
            worker.join()
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
