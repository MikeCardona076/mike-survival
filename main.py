"""Punto de entrada de MIKE: SEÑAL DE SUPERVIVENCIA.

En la Fase 1 crea una run nueva, su estado inicial y la imprime por
pantalla. El bucle de juego llegará en fases posteriores.
"""

from __future__ import annotations

import logging
import secrets

from config import DEFAULT_TRAIT, SEED_BITS
from db.database import get_connection, init_db
from db.repositories import AgentStateRepository, Run, RunRepository
from game.world import generate_refugio7

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


def main() -> int:
    """Inicializa la base de datos y arranca una run."""
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
