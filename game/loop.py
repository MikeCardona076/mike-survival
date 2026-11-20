"""Sesión de juego: Mike, mundo, reloj de turnos y persistencia."""

from __future__ import annotations

import random
import sqlite3

from config import (
    INITIAL_ZOMBIES,
    MAX_ZOMBIES,
    RUN_STATUS_DEAD,
    TILE_SIZE,
    TURN_SECONDS,
    ZOMBIE_SPAWN_CHANCE,
)
from db.repositories import (
    AgentStateRepository,
    ChatMessage,
    ChatRepository,
    EventRepository,
    MemoryEntry,
    MemoryRepository,
    Run,
    RunRepository,
)
from game.combat import attack_zombie
from game.entities import Mike, Zombie, spawn_zombies
from game.events import maybe_event
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
        self._chat_repository = ChatRepository(connection)
        self._memory_repository = MemoryRepository(connection)
        self._event_repository = EventRepository(connection)
        self._finished = False
        if self._state_repository.get(run.id) is None:
            self._state_repository.create(run.id)
        self.zombies: list[Zombie] = spawn_zombies(
            run.seed,
            INITIAL_ZOMBIES,
            int(self.mike.pos_x),
            int(self.mike.pos_y),
            self.world,
        )
        self.persist()

    def record_chat(
        self,
        role: str,
        content: str | None = None,
        tool_name: str | None = None,
        tool_args: dict[str, object] | None = None,
        tool_call_id: str | None = None,
    ) -> ChatMessage:
        """Guarda un mensaje del historial de radio."""
        return self._chat_repository.add(
            self.run.id,
            role,
            content=content,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_call_id=tool_call_id,
        )

    def recent_chat(self, limit: int = 8) -> list[ChatMessage]:
        """Devuelve los últimos mensajes de radio de la run."""
        return self._chat_repository.list_for_run(self.run.id, limit=limit)

    def remember(self, content: str, importance: int = 1) -> MemoryEntry:
        """Guarda un recuerdo persistente de Mike."""
        return self._memory_repository.add(self.run.id, "agent", content, importance)

    def add_event(self, text: str) -> None:
        """Añade una línea al log de eventos visible en la interfaz."""
        self.events.append(text)

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
        """Ejecuta un turno: desgaste, zombis y eventos; guarda el estado."""
        events = self.mike.advance_turn()
        events.extend(self._update_zombies())
        if self.mike.alive:
            rolled = maybe_event(self)
            if rolled is not None:
                event_type, text = rolled
                self._event_repository.add(self.run.id, event_type, text)
                events.append(text)
        self.events.extend(events)
        self.persist()
        if self.is_over:
            self._finish_run()

    def _update_zombies(self) -> list[str]:
        events: list[str] = []
        for zombie in self.zombies:
            events.extend(zombie.update(self.mike))
            if not self.mike.alive:
                return events

        alive_count = sum(1 for zombie in self.zombies if zombie.alive)
        rng = random.Random((self.run.seed << 7) ^ (self.mike.turn_count * 131))
        if rng.random() < ZOMBIE_SPAWN_CHANCE and alive_count < MAX_ZOMBIES:
            new_zombies = spawn_zombies(
                self.run.seed + self.mike.turn_count * 17,
                1,
                int(self.mike.pos_x),
                int(self.mike.pos_y),
                self.world,
            )
            if new_zombies:
                self.zombies.extend(new_zombies)
                events.append("Se oyen pasos: otro zombi se acerca.")
        return events

    def attack_nearest_zombie(self) -> str:
        """Ataca al zombi adyacente más cercano y devuelve el resultado."""
        if not self.mike.alive:
            return "Mike ya no puede luchar."
        alive = [zombie for zombie in self.zombies if zombie.alive]
        if not alive:
            return "No hay ningún zombi al alcance."
        nearest = min(alive, key=lambda zombie: zombie.distance_to(self.mike))
        if nearest.distance_to(self.mike) > 1:
            return "El zombi más cercano está demasiado lejos; acércate."
        message, killed = attack_zombie(self.mike, nearest)
        if killed:
            self.zombies.remove(nearest)
            self._event_repository.add(self.run.id, "combat", message)
        self.events.append(message)
        self.persist()
        return message

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
