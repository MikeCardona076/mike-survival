# PHASE 2 DONE — Mundo procedural, persistencia y renderer

- **Fecha:** 2026-11-19
- **Commit de cierre de código:** `faf6980`
- **Estado:** completada y verificada; pendiente de aprobación del Operador
  para iniciar la Fase 3.

## Qué se hizo

- `config.py`: constantes de cámara, tipos de tile, paleta, parámetros de
  las dos capas de Perlin y umbrales de clasificación de terreno.
- `game/world.py`:
  - `TileType` (`water`, `sand`, `grass`, `forest`, `rock`) y `Chunk`.
  - `generate_chunk()` determinista con dos capas de Perlin (elevación y
    humedad) y seed por run.
  - Serialización JSON validada (`chunk_to_json` / `chunk_from_json`).
  - `World` con caché en memoria y lectura/escritura de chunks en SQLite.
- `db/repositories.py`: `WorldChunkRepository` con upsert por
  `(run_id, chunk_x, chunk_y)`.
- `game/renderer.py`: renderer de tiles 16×16 con viewport culling por
  chunks; solo pide al mundo los chunks que intersectan la cámara.
- `main.py`: crea la run y abre una ventana pygame de 1280×720 centrada
  en el chunk (0,0); `Esc` o cerrar la ventana termina el bucle.
- Tests nuevos: generación/persistencia de chunks, culling, pintado de
  tiles y smoke headless del bucle de ventana.

## Qué funciona (verificación)

Ejecutado en Docker `python:3.12-slim` con `requirements.txt` completo
(`noise` compilado) y SDL en modo dummy:

| Comprobación | Resultado |
| --- | --- |
| `python -m pytest -q` | 28 tests pasan |
| `python -m ruff check .` | `All checks passed!` |
| `python -m black --check .` | 29 files would be left unchanged |
| `python main.py` | Ventana creada y bucle activo 4 s hasta el timeout esperado (124) |
| Captura del frame | 1280×720 con terreno por chunks (`data/phase2_preview.png`) |

En local (Windows, Python 3.12.13) pasan 17 tests y se omiten los dos
módulos que importan `noise`, porque este host no tiene MSVC para
compilarlo. `ruff` y `black` pasan en local. La verificación completa de
`noise` + pygame se hace en Docker.

## Cómo reproducir

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python -m ruff check .
python -m black --check .
python main.py   # abre la ventana; Esc para salir
```

## Pendiente / notas

- La Fase 3 (Mike, HUD y actualización de estado) no se ha iniciado:
  espera aprobación explícita.
- La calidad visual del terreno (sprites, texturas, bordes) corresponde a
  la Fase 7; aquí solo se valida la generación y el render de tiles.
- `make` sigue sin estar instalado en el host Windows; los targets se
  validarán en la Fase 8.
