"""Fixtures compartidas de la suite de tests."""

from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest

from config import SCHEMA_PATH
from db.database import get_connection, init_db

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_TMP_ROOT = PROJECT_ROOT / ".test_tmp"


@pytest.fixture()
def tmp_path() -> Iterator[Path]:
    """Sustituye el ``tmp_path`` de pytest.

    pytest crea sus temporales con permisos 0o700, que el sandbox de
    Windows de este entorno convierte en inaccesibles. Creamos la carpeta
    bajo el workspace con permisos heredados normales.
    """
    path = TEST_TMP_ROOT / uuid4().hex
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    """Crea una base de datos temporal con el esquema real."""
    path = tmp_path / "mike_test.db"
    init_db(db_path=path, schema_path=SCHEMA_PATH)
    return path


@pytest.fixture()
def connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Entrega una conexión a la base de datos temporal."""
    with get_connection(db_path=db_path) as conn:
        yield conn
