"""Sesión de juego: Mike, mundo, reloj de turnos y persistencia."""

from __future__ import annotations

import random
import sqlite3

from config import (
    GLOBAL_MEMORY_IMPORTANCE,
    INITIAL_ZOMBIES,
    INSTINCT_FLEE_HEALTH,
    INSTINCT_HEAL_THRESHOLD,
    INSTINCT_HUNGER_THRESHOLD,
    INSTINCT_INFECTION_THRESHOLD,
    INSTINCT_LOW_SUPPLIES,
    INSTINCT_SCAVENGE_CHANCE,
    INSTINCT_SCAVENGE_LOW_CHANCE,
    INSTINCT_THIRST_THRESHOLD,
    ITEM_FOOD,
    ITEM_NAMES,
    ITEM_WATER,
    MAX_ZOMBIES,
    META_UNLOCK_VETERAN,
    RUN_STATUS_DEAD,
    SCAVENGE_ITEMS,
    TILE_SIZE,
    TRAIT_UNLOCK_DEATHS,
    TURN_SECONDS,
    WALKABLE_TILE_IDS,
    ZOMBIE_SPAWN_CHANCE,
)
from db.repositories import (
    AgentStateRepository,
    ChatMessage,
    ChatRepository,
    EventRepository,
    MemoryEntry,
    MemoryRepository,
    MetaProgressionRepository,
    Run,
    RunRepository,
    StatsRepository,
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
        *,
        instincts: bool = True,
    ) -> None:
        self.run = run
        self.connection = connection
        self.world = World(run.id, run.seed, connection)
        self.mike = Mike.from_trait(run.trait) if mike is None else mike
        self._instincts_enabled = instincts
        self.elapsed_seconds = 0.0
        self.events: list[str] = []
        self._state_repository = AgentStateRepository(connection)
        self._run_repository = RunRepository(connection)
        self._chat_repository = ChatRepository(connection)
        self._memory_repository = MemoryRepository(connection)
        self._event_repository = EventRepository(connection)
        self._stats_repository = StatsRepository(connection)
        self._meta_repository = MetaProgressionRepository(connection)
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

    def remember_global(self, content: str, importance: int = 3) -> MemoryEntry:
        """Guarda un recuerdo compartido entre todas las runs."""
        return self._memory_repository.add(None, "global", content, importance)

    def global_memories(self, limit: int = 5) -> list[MemoryEntry]:
        """Recuerdos de runs anteriores para el prompt de Mike."""
        return self._memory_repository.list_global(limit)

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
        """Ejecuta un turno: desgaste, instinto, zombis y eventos; guarda."""
        events = self.mike.advance_turn()
        events.extend(self._instinct_action())
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

    def _instinct_action(self) -> list[str]:
        """Comportamiento autónomo local de Mike, sin consumir tokens."""
        mike = self.mike
        events: list[str] = []
        if not self._instincts_enabled or not mike.alive:
            return events

        if mike.health <= INSTINCT_HEAL_THRESHOLD and mike.use_bandage():
            events.append("Mike se venda las heridas por instinto.")
        if mike.infection >= INSTINCT_INFECTION_THRESHOLD and mike.use_suppressor():
            events.append("Mike usa un supresor al notar el virus.")
        if mike.hunger >= INSTINCT_HUNGER_THRESHOLD and mike.eat():
            events.append("Mike come una ración por su cuenta.")
        if mike.thirst >= INSTINCT_THIRST_THRESHOLD and mike.drink():
            events.append("Mike bebe agua por su cuenta.")
        if events:
            return events

        alive = [zombie for zombie in self.zombies if zombie.alive]
        if alive:
            nearest = min(alive, key=lambda zombie: zombie.distance_to(mike))
            distance = nearest.distance_to(mike)
            if distance <= 1:
                message, killed = attack_zombie(mike, nearest)
                events.append(f"Mike ataca por instinto. {message}")
                if killed:
                    self.zombies.remove(nearest)
                    self._event_repository.add(self.run.id, "combat", message)
                return events
            if distance <= 3 and mike.health <= INSTINCT_FLEE_HEALTH:
                if self._step_away(nearest):
                    events.append("Mike retrocede para ganar distancia.")
                return events

        found = self._maybe_scavenge()
        if found is not None:
            events.append(found)
        self._step_toward_refugio()
        return events

    def _step_toward_refugio(self) -> bool:
        """Avanza un tile hacia el Refugio 7 si el terreno lo permite."""
        delta_x = self.run.refugio7_x - int(self.mike.pos_x)
        delta_y = self.run.refugio7_y - int(self.mike.pos_y)
        steps = sorted(
            (
                ((1 if delta_x > 0 else -1), 0) if delta_x else (0, 0),
                (0, (1 if delta_y > 0 else -1)) if delta_y else (0, 0),
            ),
            key=lambda step: abs(step[0]) + abs(step[1]),
            reverse=True,
        )
        for step_x, step_y in steps:
            if step_x == 0 and step_y == 0:
                continue
            target_x = int(self.mike.pos_x) + step_x
            target_y = int(self.mike.pos_y) + step_y
            if int(self.world.get_tile(target_x, target_y)) not in WALKABLE_TILE_IDS:
                continue
            self.mike.pos_x = float(target_x)
            self.mike.pos_y = float(target_y)
            return True
        return False

    def _step_away(self, zombie: Zombie) -> bool:
        delta_x = int(self.mike.pos_x) - zombie.x
        delta_y = int(self.mike.pos_y) - zombie.y
        candidates = (
            ((1 if delta_x > 0 else -1), 0),
            (0, (1 if delta_y > 0 else -1)),
        )
        for step_x, step_y in candidates:
            target_x = int(self.mike.pos_x) + step_x
            target_y = int(self.mike.pos_y) + step_y
            if int(self.world.get_tile(target_x, target_y)) not in WALKABLE_TILE_IDS:
                continue
            self.mike.pos_x = float(target_x)
            self.mike.pos_y = float(target_y)
            return True
        return False

    def _maybe_scavenge(self) -> str | None:
        if not self.mike.alive:
            return None
        supplies = self.mike.inventory.count(ITEM_FOOD) + self.mike.inventory.count(ITEM_WATER)
        chance = (
            INSTINCT_SCAVENGE_LOW_CHANCE
            if supplies <= INSTINCT_LOW_SUPPLIES
            else INSTINCT_SCAVENGE_CHANCE
        )
        rng = random.Random((self.run.seed << 11) ^ (self.mike.turn_count * 53))
        if rng.random() >= chance:
            return None
        item = rng.choice(SCAVENGE_ITEMS)
        self.mike.inventory.add(item, 1)
        return f"Mike rebusca y encuentra {ITEM_NAMES[item]}."

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
        cause = self.mike.cause_of_death or "causa desconocida"
        self._run_repository.finish(self.run.id, RUN_STATUS_DEAD, cause)
        deaths = self._stats_repository.increment_deaths()
        self.remember_global(
            (
                f"En la run {self.run.id} morí en el turno "
                f"{self.mike.turn_count} por {cause}. Debo evitarlo."
            ),
            GLOBAL_MEMORY_IMPORTANCE,
        )
        if deaths >= TRAIT_UNLOCK_DEATHS:
            newly_unlocked = self._meta_repository.unlock(
                META_UNLOCK_VETERAN,
                "Rasgo veterano desbloqueado tras 10 muertes.",
            )
            if newly_unlocked:
                self.remember_global(
                    "Diez muertes después, el virus ya no me asusta igual.",
                    5,
                )
