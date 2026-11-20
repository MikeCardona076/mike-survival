"""Capa de conexión a SQLite.

La base de datos se inicializa desde ``db/schema.sql`` y toda conexión
aplica ``PRAGMA journal_mode=WAL`` y ``PRAGMA foreign_keys=ON``.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from config import DATABASE_PATH, SCHEMA_PATH

logger = logging.getLogger(__name__)


def connect(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Abre una conexión con los PRAGMA obligatorios ya aplicados."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _schema_is_initialized(connection: sqlite3.Connection) -> bool:
    """Comprueba si la tabla ``runs`` ya existe."""
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'runs'"
    ).fetchone()
    return row is not None


@contextmanager
def get_connection(db_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    """Entrega una conexión y confirma o revierte la transacción."""
    connection = connect(db_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db(
    db_path: Path = DATABASE_PATH,
    schema_path: Path = SCHEMA_PATH,
) -> None:
    """Crea el esquema de forma idempotente si aún no está inicializado."""
    schema_sql = schema_path.read_text(encoding="utf-8")
    with get_connection(db_path) as connection:
        if _schema_is_initialized(connection):
            logger.debug("El esquema ya existe en %s", db_path)
            return
        connection.executescript(schema_sql)
        connection.commit()
    logger.info("Base de datos inicializada en %s", db_path)
