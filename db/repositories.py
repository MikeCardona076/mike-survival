"""Repositorios tipados sobre SQLite, sin ORM.

Cada repositorio recibe una conexión abierta y no gestiona transacciones:
eso es responsabilidad de :func:`db.database.get_connection`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from config import DEFAULT_TRAIT, RUN_STATUS_ALIVE


@dataclass(frozen=True, slots=True)
class Run:
    id: int
    seed: int
    started_at: str
    ended_at: str | None
    status: str
    cause_of_death: str | None
    refugio7_x: int
    refugio7_y: int
    trait: str


@dataclass(frozen=True, slots=True)
class AgentState:
    run_id: int
    health: int
    hunger: int
    thirst: int
    infection: int
    radio_battery: int
    pos_x: float
    pos_y: float
    inventory: str
    objective: str | None
    turn_count: int
    updated_at: str


@dataclass(frozen=True, slots=True)
class ChatMessage:
    id: int
    run_id: int
    role: str
    content: str | None
    tool_name: str | None
    tool_args: str | None
    tool_call_id: str | None
    created_at: str


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    id: int
    run_id: int | None
    type: str
    content: str
    importance: int
    created_at: str


@dataclass(frozen=True, slots=True)
class WorldEvent:
    id: int
    run_id: int
    type: str
    content: str
    resolved: int
    created_at: str


@dataclass(frozen=True, slots=True)
class Stats:
    runs_played: int
    runs_won: int
    total_deaths: int
    best_distance_to_r7: float
    total_playtime_seconds: int


def _row_to_run(row: sqlite3.Row) -> Run:
    return Run(
        id=int(row["id"]),
        seed=int(row["seed"]),
        started_at=str(row["started_at"]),
        ended_at=None if row["ended_at"] is None else str(row["ended_at"]),
        status=str(row["status"]),
        cause_of_death=(None if row["cause_of_death"] is None else str(row["cause_of_death"])),
        refugio7_x=int(row["refugio7_x"]),
        refugio7_y=int(row["refugio7_y"]),
        trait=str(row["trait"]),
    )


def _row_to_agent_state(row: sqlite3.Row) -> AgentState:
    return AgentState(
        run_id=int(row["run_id"]),
        health=int(row["health"]),
        hunger=int(row["hunger"]),
        thirst=int(row["thirst"]),
        infection=int(row["infection"]),
        radio_battery=int(row["radio_battery"]),
        pos_x=float(row["pos_x"]),
        pos_y=float(row["pos_y"]),
        inventory=str(row["inventory"]),
        objective=None if row["objective"] is None else str(row["objective"]),
        turn_count=int(row["turn_count"]),
        updated_at=str(row["updated_at"]),
    )


def _row_to_chat_message(row: sqlite3.Row) -> ChatMessage:
    return ChatMessage(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        role=str(row["role"]),
        content=None if row["content"] is None else str(row["content"]),
        tool_name=None if row["tool_name"] is None else str(row["tool_name"]),
        tool_args=None if row["tool_args"] is None else str(row["tool_args"]),
        tool_call_id=(None if row["tool_call_id"] is None else str(row["tool_call_id"])),
        created_at=str(row["created_at"]),
    )


def _row_to_memory_entry(row: sqlite3.Row) -> MemoryEntry:
    return MemoryEntry(
        id=int(row["id"]),
        run_id=None if row["run_id"] is None else int(row["run_id"]),
        type=str(row["type"]),
        content=str(row["content"]),
        importance=int(row["importance"]),
        created_at=str(row["created_at"]),
    )


def _row_to_world_event(row: sqlite3.Row) -> WorldEvent:
    return WorldEvent(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        type=str(row["type"]),
        content=str(row["content"]),
        resolved=int(row["resolved"]),
        created_at=str(row["created_at"]),
    )


class RunRepository:
    """Operaciones sobre la tabla ``runs``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
        self,
        seed: int,
        refugio7_x: int,
        refugio7_y: int,
        trait: str = DEFAULT_TRAIT,
    ) -> Run:
        cursor = self._connection.execute(
            """
            INSERT INTO runs (seed, refugio7_x, refugio7_y, trait, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (seed, refugio7_x, refugio7_y, trait, RUN_STATUS_ALIVE),
        )
        run_id = cursor.lastrowid
        if run_id is None:
            raise RuntimeError("SQLite no devolvió el id de la run creada")
        run = self.get(run_id)
        if run is None:
            raise RuntimeError(f"La run {run_id} no se pudo leer tras crearla")
        return run

    def get(self, run_id: int) -> Run | None:
        row = self._connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return None if row is None else _row_to_run(row)

    def get_latest(self) -> Run | None:
        row = self._connection.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        return None if row is None else _row_to_run(row)

    def list_all(self, limit: int = 50) -> list[Run]:
        rows = self._connection.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [_row_to_run(row) for row in rows]

    def count(self) -> int:
        row = self._connection.execute("SELECT COUNT(*) AS total FROM runs").fetchone()
        if row is None:
            return 0
        return int(row["total"])

    def finish(
        self,
        run_id: int,
        status: str,
        cause_of_death: str | None = None,
    ) -> None:
        cursor = self._connection.execute(
            """
            UPDATE runs
            SET ended_at = datetime('now'), status = ?, cause_of_death = ?
            WHERE id = ?
            """,
            (status, cause_of_death, run_id),
        )
        if cursor.rowcount == 0:
            raise LookupError(f"La run {run_id} no existe")


class AgentStateRepository:
    """Operaciones sobre la tabla ``agent_state``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(self, run_id: int) -> AgentState:
        self._connection.execute("INSERT INTO agent_state (run_id) VALUES (?)", (run_id,))
        state = self.get(run_id)
        if state is None:
            raise RuntimeError(f"No se pudo crear el estado del agente para {run_id}")
        return state

    def get(self, run_id: int) -> AgentState | None:
        row = self._connection.execute(
            "SELECT * FROM agent_state WHERE run_id = ?", (run_id,)
        ).fetchone()
        return None if row is None else _row_to_agent_state(row)

    def update_position(self, run_id: int, pos_x: float, pos_y: float) -> None:
        cursor = self._connection.execute(
            """
            UPDATE agent_state
            SET pos_x = ?, pos_y = ?, updated_at = datetime('now')
            WHERE run_id = ?
            """,
            (pos_x, pos_y, run_id),
        )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe estado del agente para la run {run_id}")

    def update(
        self,
        run_id: int,
        *,
        health: int,
        hunger: int,
        thirst: int,
        infection: int,
        radio_battery: int,
        pos_x: float,
        pos_y: float,
        inventory: str,
        turn_count: int,
        objective: str | None = None,
    ) -> None:
        """Actualiza el estado completo de Mike y la marca de tiempo."""
        cursor = self._connection.execute(
            """
            UPDATE agent_state
            SET health = ?, hunger = ?, thirst = ?, infection = ?,
                radio_battery = ?, pos_x = ?, pos_y = ?, inventory = ?,
                turn_count = ?, objective = COALESCE(?, objective),
                updated_at = datetime('now')
            WHERE run_id = ?
            """,
            (
                health,
                hunger,
                thirst,
                infection,
                radio_battery,
                pos_x,
                pos_y,
                inventory,
                turn_count,
                objective,
                run_id,
            ),
        )
        if cursor.rowcount == 0:
            raise LookupError(f"No existe estado del agente para la run {run_id}")


class ChatRepository:
    """Operaciones sobre la tabla ``chat_history``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(
        self,
        run_id: int,
        role: str,
        content: str | None = None,
        tool_name: str | None = None,
        tool_args: dict[str, Any] | None = None,
        tool_call_id: str | None = None,
    ) -> ChatMessage:
        serialized_args = None if tool_args is None else json.dumps(tool_args, ensure_ascii=False)
        cursor = self._connection.execute(
            """
            INSERT INTO chat_history
                (run_id, role, content, tool_name, tool_args, tool_call_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, role, content, tool_name, serialized_args, tool_call_id),
        )
        message_id = cursor.lastrowid
        if message_id is None:
            raise RuntimeError("SQLite no devolvió el id del mensaje")
        row = self._connection.execute(
            "SELECT * FROM chat_history WHERE id = ?", (message_id,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"El mensaje {message_id} no se pudo leer")
        return _row_to_chat_message(row)

    def list_for_run(self, run_id: int, limit: int = 100) -> list[ChatMessage]:
        rows = self._connection.execute(
            """
            SELECT * FROM chat_history
            WHERE run_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (run_id, limit),
        ).fetchall()
        return [_row_to_chat_message(row) for row in rows]


class MemoryRepository:
    """Operaciones sobre la tabla ``memory``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(
        self,
        run_id: int | None,
        memory_type: str,
        content: str,
        importance: int = 1,
    ) -> MemoryEntry:
        cursor = self._connection.execute(
            """
            INSERT INTO memory (run_id, type, content, importance)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, memory_type, content, importance),
        )
        memory_id = cursor.lastrowid
        if memory_id is None:
            raise RuntimeError("SQLite no devolvió el id del recuerdo")
        row = self._connection.execute("SELECT * FROM memory WHERE id = ?", (memory_id,)).fetchone()
        if row is None:
            raise RuntimeError(f"El recuerdo {memory_id} no se pudo leer")
        return _row_to_memory_entry(row)

    def list_for_run(self, run_id: int, limit: int = 100) -> list[MemoryEntry]:
        rows = self._connection.execute(
            """
            SELECT * FROM memory
            WHERE run_id = ?
            ORDER BY importance DESC, id ASC
            LIMIT ?
            """,
            (run_id, limit),
        ).fetchall()
        return [_row_to_memory_entry(row) for row in rows]

    def list_global(self, limit: int = 5) -> list[MemoryEntry]:
        """Recuerdos compartidos entre runs (run_id NULL)."""
        rows = self._connection.execute(
            """
            SELECT * FROM memory
            WHERE run_id IS NULL
            ORDER BY importance DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_row_to_memory_entry(row) for row in rows]


class EventRepository:
    """Operaciones sobre la tabla ``events``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, run_id: int, event_type: str, content: str) -> WorldEvent:
        cursor = self._connection.execute(
            "INSERT INTO events (run_id, type, content) VALUES (?, ?, ?)",
            (run_id, event_type, content),
        )
        event_id = cursor.lastrowid
        if event_id is None:
            raise RuntimeError("SQLite no devolvió el id del evento")
        row = self._connection.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            raise RuntimeError(f"El evento {event_id} no se pudo leer")
        return _row_to_world_event(row)

    def list_for_run(
        self,
        run_id: int,
        limit: int = 100,
        only_unresolved: bool = False,
    ) -> list[WorldEvent]:
        query = "SELECT * FROM events WHERE run_id = ?"
        if only_unresolved:
            query += " AND resolved = 0"
        query += " ORDER BY id ASC LIMIT ?"
        rows = self._connection.execute(query, (run_id, limit)).fetchall()
        return [_row_to_world_event(row) for row in rows]

    def resolve(self, event_id: int) -> None:
        cursor = self._connection.execute(
            "UPDATE events SET resolved = 1 WHERE id = ?", (event_id,)
        )
        if cursor.rowcount == 0:
            raise LookupError(f"El evento {event_id} no existe")


class StatsRepository:
    """Operaciones sobre la tabla ``stats`` (fila única con id = 1)."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self) -> Stats:
        row = self._connection.execute("SELECT * FROM stats WHERE id = 1").fetchone()
        if row is None:
            raise RuntimeError("La tabla stats no está inicializada")
        return Stats(
            runs_played=int(row["runs_played"]),
            runs_won=int(row["runs_won"]),
            total_deaths=int(row["total_deaths"]),
            best_distance_to_r7=float(row["best_distance_to_r7"]),
            total_playtime_seconds=int(row["total_playtime_seconds"]),
        )

    def increment_runs_played(self) -> None:
        self._connection.execute("UPDATE stats SET runs_played = runs_played + 1 WHERE id = 1")

    def increment_deaths(self) -> int:
        """Suma una muerte y devuelve el total acumulado."""
        self._connection.execute("UPDATE stats SET total_deaths = total_deaths + 1 WHERE id = 1")
        return self.get().total_deaths


class WorldChunkRepository:
    """Persistencia de chunks generados en la tabla ``world_chunks``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_data(self, run_id: int, chunk_x: int, chunk_y: int) -> str | None:
        row = self._connection.execute(
            """
            SELECT data FROM world_chunks
            WHERE run_id = ? AND chunk_x = ? AND chunk_y = ?
            """,
            (run_id, chunk_x, chunk_y),
        ).fetchone()
        return None if row is None else str(row["data"])

    def save(
        self,
        run_id: int,
        chunk_x: int,
        chunk_y: int,
        seed: int,
        data: str,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO world_chunks (run_id, chunk_x, chunk_y, seed, data)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id, chunk_x, chunk_y)
            DO UPDATE SET data = excluded.data, generated_at = datetime('now')
            """,
            (run_id, chunk_x, chunk_y, seed, data),
        )

    def count_for_run(self, run_id: int) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) AS total FROM world_chunks WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        return 0 if row is None else int(row["total"])


class AssetCacheRepository:
    """Caché de assets procedurales en la tabla ``assets_cache``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self, asset_key: str) -> bytes | None:
        row = self._connection.execute(
            "SELECT data FROM assets_cache WHERE asset_key = ?",
            (asset_key,),
        ).fetchone()
        return None if row is None else bytes(row["data"])

    def save(
        self,
        asset_key: str,
        asset_type: str,
        description: str,
        data: bytes,
        params: str | None = None,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO assets_cache (asset_key, asset_type, description, params, data)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(asset_key) DO UPDATE SET
                asset_type = excluded.asset_type,
                description = excluded.description,
                params = excluded.params,
                data = excluded.data
            """,
            (asset_key, asset_type, description, params, data),
        )

    def count(self) -> int:
        row = self._connection.execute("SELECT COUNT(*) AS total FROM assets_cache").fetchone()
        return 0 if row is None else int(row["total"])


class MetaProgressionRepository:
    """Desbloqueos persistentes entre runs."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def unlock(self, unlock_key: str, description: str) -> bool:
        """Desbloquea una clave; devuelve True si era nueva."""
        cursor = self._connection.execute(
            """
            INSERT OR IGNORE INTO meta_progression (unlock_key, description)
            VALUES (?, ?)
            """,
            (unlock_key, description),
        )
        return cursor.rowcount > 0

    def is_unlocked(self, unlock_key: str) -> bool:
        row = self._connection.execute(
            "SELECT 1 FROM meta_progression WHERE unlock_key = ?",
            (unlock_key,),
        ).fetchone()
        return row is not None

    def list_keys(self) -> list[str]:
        rows = self._connection.execute(
            "SELECT unlock_key FROM meta_progression ORDER BY unlocked_at ASC"
        ).fetchall()
        return [str(row["unlock_key"]) for row in rows]


@dataclass(frozen=True, slots=True)
class Shelter:
    """Mejoras persistentes del refugio/taller."""

    level: int
    weapon_level: int


class ShelterRepository:
    """Lee y guarda el nivel del refugio y del arma."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get(self) -> Shelter:
        row = self._connection.execute(
            "SELECT level, weapon_level FROM shelter WHERE id = 1"
        ).fetchone()
        if row is None:
            raise RuntimeError("La tabla shelter no está inicializada")
        return Shelter(
            level=int(row["level"]),
            weapon_level=int(row["weapon_level"]),
        )

    def update(self, shelter: Shelter) -> None:
        cursor = self._connection.execute(
            "UPDATE shelter SET level = ?, weapon_level = ? WHERE id = 1",
            (shelter.level, shelter.weapon_level),
        )
        if cursor.rowcount == 0:
            raise RuntimeError("No se pudo actualizar el refugio")
