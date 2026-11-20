# PHASE 1 DONE — Esqueleto, BD y repositorios

- **Fecha:** 2026-11-19
- **Commit de cierre de código:** `d340dc4`
- **Estado:** completada y verificada; pendiente de aprobación del Operador
  para iniciar la Fase 2.

## Qué se hizo

- Estructura completa del repo según `TASK.md`, con paquetes `db/`, `game/`,
  `agent/`, `assets/`, `ui/` y `tests/`.
- Tooling: `requirements.txt`, `pyproject.toml` (ruff, black, pytest),
  `Makefile`, `.gitignore`, `.env.example`, `README.md` y `LICENSE` MIT.
- `config.py` con constantes tipadas y rutas `pathlib.Path`.
- Esquema SQLite exacto del brief en `db/schema.sql`.
- `db/database.py`: conexión con `PRAGMA journal_mode=WAL` y
  `PRAGMA foreign_keys=ON`, inicialización idempotente desde el esquema.
- `db/repositories.py`: repositorios tipados para `runs`, `agent_state`,
  `chat_history`, `memory`, `events` y `stats`, sin ORM.
- `main.py`: crea una run, su estado inicial de Mike y la imprime.
- Refugio 7 determinista por seed dentro de un radio de ±500 unidades
  (`game/world.py`, constante en `config.py`).

## Qué funciona (verificación)

Ejecutado el 2026-11-19 en el workspace local con Python 3.12.13:

| Comando | Resultado |
| --- | --- |
| `python -m pytest -q` | 15 tests pasan |
| `python -m ruff check .` | `All checks passed!` |
| `python -m black --check .` | 27 files would be left unchanged |
| `python main.py` | `Run #1 creada - seed=..., refugio7=(...), trait=neutral` |

Verificación adicional en Linux con Docker `python:3.12-slim`, instalando
`requirements.txt` completo (incluida la compilación de `noise`): pytest,
ruff, black y `main.py` dieron el mismo resultado.

## Cómo reproducir

```bash
# Linux / Docker (entorno objetivo)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python -m ruff check .
python -m black --check .
python main.py
```

En este host Windows no hay `make` instalado; los targets `make test` y
`make lint` quedan definidos y se validarán en la Fase 8 (Docker/Linux).
Como equivalente local se ejecutaron los módulos `pytest`, `ruff` y
`black` directamente.

## Pendiente / notas

- La Fase 2 (chunks con Perlin, renderer y ventana pygame) no se ha
  iniciado: espera aprobación explícita.
- El host solo tenía Python 3.14; se instaló Python 3.12.13 con `uv` dentro
  del workspace (`.uv-python/`) para las verificaciones locales.
- La ejecución local de pytest dejó carpetas internas `.pytest_tmp/` y
  `pytest-cache-files-*` inaccesibles por una restricción del sandbox de
  Windows; están en `.gitignore` y no forman parte del proyecto. La suite
  usa un `tmp_path` propio bajo `.test_tmp/` para evitar ese problema.
