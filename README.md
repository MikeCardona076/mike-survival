# MIKE: SEÑAL DE SUPERVIVENCIA

Survival roguelite 2D en pixel art con mundo abierto procedural. El
jugador **no** controla a Mike: es el Operador, que lo coordina por radio
con batería limitada. Mike es un agente autónomo que corre sobre la API
de DeepSeek (`deepseek-flash`) con function calling.

## Estado

**Fase 1 completa:** esqueleto del proyecto, esquema SQLite, capa de
conexión y repositorios, más una run de prueba ejecutable.

## Stack

- Python 3.12
- pygame-ce
- SQLite (stdlib `sqlite3`, sin ORM)
- `openai` SDK contra `https://api.deepseek.com`
- `noise`, Pillow
- pytest, ruff, black
- Docker (fases posteriores)

## Puesta en marcha

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # rellena DEEPSEEK_API_KEY
python main.py
```

En Windows, activa el entorno con `.venv\Scripts\activate`.

## Calidad

```bash
make test   # pytest
make lint   # ruff + black --check
make run    # crea una run y la imprime
```

## Estructura

`db/` persistencia SQLite, `game/` simulación, `agent/` cliente DeepSeek y
herramientas, `ui/` HUD y chat, `assets/` sprites y audio procedural,
`tests/` suite de pytest.

## Hoja de ruta

1. Esqueleto, BD y repositorios
2. Mundo procedural con chunks
3. Mike, HUD y estado
4. Cliente DeepSeek con function calling
5. Chat bidireccional
6. Zombis, combate y eventos
7. Assets y audio procedurales
8. Docker y distribución
9. Persistencia y meta-progresión

## Licencia

MIT. Ver [LICENSE](LICENSE).
