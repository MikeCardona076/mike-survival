"""Sesión de juego: Mike, mundo, reloj de turnos y persistencia."""

from __future__ import annotations

import sqlite3

from config import RUN_STATUS_DEAD, TILE_SIZE, TURN_SECONDS
from db.repositories import AgentStateRepository, Run, RunRepository
from game.entities import Mike
from game.world import World


class GameSession:
    """Estado vivo de una run y avance del tiempo por turnos."""

    def __init__(
        self,
        run: Run,
        connection: sqlite3.Connection,
        mike: Mike | None = None,
    ) -> None:
        self.run = run
        self.connection = connection
        self.world = World(run.id, run.seed, connection)
        self.mike = Mike() if mike is None else mike
        self.elapsed_seconds = 0.0
        self.events: list[str] = []
        self._state_repository = AgentStateRepository(connection)
        self._run_repository = RunRepository(connection)
        self._finished = False
        if self._state_repository.get(run.id) is None:
            self._state_repository.create(run.id)
        self.persist()

    @property
    def is_over(self) -> bool:
        """True cuando Mike ya no está vivo."""
        return not self.mike.alive

    @property
    def camera_x(self) -> float:
        """Coordenada X de la cámara en píxeles, centrada en Mike."""
        return (self.mike.pos_x + 0.5) * TILE_SIZE

    @property
    def camera_y(self) -> float:
        """Coordenada Y de la cámara en píxeles, centrada en Mike."""
        return (self.mike.pos_y + 0.5) * TILE_SIZE

    def update(self, delta_seconds: float) -> None:
        """Acumula tiempo y ejecuta los turnos completos que correspondan."""
        if self.is_over:
            return
        self.elapsed_seconds += delta_seconds
        while self.elapsed_seconds >= TURN_SECONDS and not self.is_over:
            self.elapsed_seconds -= TURN_SECONDS
            self.advance_turn()

    def advance_turn(self) -> None:
        """Ejecuta un turno de simulación y guarda el estado."""
        events = self.mike.advance_turn()
        self.events.extend(events)
        self.persist()
        if self.is_over:
            self._finish_run()

    def persist(self) -> None:
        """Guarda el estado de Mike en ``agent_state``."""
        self._state_repository.update(
            self.run.id,
            health=self.mike.health,
            hunger=self.mike.hunger,
            thirst=self.mike.thirst,
            infection=self.mike.infection,
            radio_battery=self.mike.radio_battery,
            pos_x=self.mike.pos_x,
            pos_y=self.mike.pos_y,
            inventory=self.mike.inventory.to_json(),
            turn_count=self.mike.turn_count,
        )

    def _finish_run(self) -> None:
        if self._finished:
            return
        self._finished = True
        self._run_repository.finish(
            self.run.id,
            RUN_STATUS_DEAD,
            self.mike.cause_of_death or "causa desconocida",
        )
