# MIKE: SEÑAL DE SUPERVIVENCIA

Survival roguelite 2D en pixel art con mundo abierto procedural. El
jugador **no** controla a Mike: es el Operador, que lo coordina por radio
con batería limitada. Mike es un agente autónomo que corre sobre la API
de DeepSeek (`deepseek-flash`) con function calling.

## Estado

Fases 1–7 completas:

- mundo por chunks con dos capas de Perlin y persistencia SQLite;
- Mike con salud, hambre, sed, infección y batería;
- HUD, chat de radio con typewriter y agente DeepSeek con 10 tools;
- 4 subtipos de zombi, combate, eventos narrativos y game over;
- sprites procedurales cacheados y SFX generados con pyfxr.

## Cómo jugar

```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # rellena DEEPSEEK_API_KEY
python main.py
```

Se abre una ventana de 1280×720. Escribe en la barra inferior y pulsa
`Enter` para hablar con Mike; `Esc` o cerrar la ventana termina la
partida. Cada mensaje consume 1–3% de batería de radio. Sin API key el
juego arranca y muestra «Radio sin enlace».

## Docker

En Linux con servidor X11:

```bash
cp .env.example .env
xhost +local:docker
docker compose up --build
```

El volumen `./data` conserva la base de datos SQLite entre ejecuciones.
En Windows/macOS se recomienda ejecutar el juego de forma nativa o usar
un servidor X11 con `DISPLAY` configurado.

## Calidad

```bash
make test          # pytest
make lint          # ruff + black --check
make docker-build  # construye la imagen
make docker-test   # tests dentro del contenedor
```

## Estructura

`db/` persistencia SQLite, `game/` simulación, `agent/` cliente DeepSeek y
herramientas, `ui/` HUD y chat, `assets/` sprites y audio procedural,
`tests/` suite de pytest.

## Hoja de ruta

1. ✅ Esqueleto, BD y repositorios
2. ✅ Mundo procedural con chunks y Perlin
3. ✅ Mike, HUD y estado
4. ✅ Cliente DeepSeek con function calling
5. ✅ Chat bidireccional
6. ✅ Zombis, combate y eventos
7. ✅ Assets y audio procedurales
8. ✅ Docker y distribución
9. Persistencia y meta-progresión

## Licencia

MIT. Ver [LICENSE](LICENSE).
