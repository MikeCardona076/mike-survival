# PLAN DE CONSTRUCCIÓN — MIKE: SEÑAL DE SUPERVIVENCIA

Este archivo es el estado vivo del proyecto. El agente lo lee al inicio
de cada turno y lo actualiza al final de cada fase.

## ESTADO ACTUAL

- **Fase en curso:** 6
- **Tarea actual:** Zombis, combate y eventos narrativos
- **Última actualización:** 2026-11-19
- **Commit de referencia:** 06915c2

## PLAN DE FASE 1 (COMPLETADO)

1. Crear el esqueleto de `mike-survival/` y el tooling: `pyproject.toml`,
   `requirements.txt`, `.gitignore`, `.env.example` y `Makefile`.
2. Implementar `config.py` con constantes tipadas y rutas `pathlib.Path`
   (cero números mágicos; `DATABASE_PATH` bajo `data/`).
3. Implementar `db/schema.sql` exacto y `db/database.py` (conexión que
   aplica `PRAGMA journal_mode=WAL` y `PRAGMA foreign_keys=ON`, é init
   idempotente desde el schema).
4. Implementar `db/repositories.py` con repositorios tipados para runs,
   agent_state, chat_history, memory, events y stats, sin ORM.
5. Escribir `main.py` (crea Run #1 y la imprime) y ≥4 tests de
   repositorios; validar con `pytest`, `ruff` y `black`; commit atómico.

## PLAN DE FASE 2 (COMPLETADO)

1. Añadir a `config.py` las constantes de terreno, ruido Perlin, paleta
   de tiles y tamaño de chunk en píxeles.
2. Implementar `TileType`, `Chunk`, `generate_chunk()` (2 capas Perlin:
   elevación y humedad), serialización JSON y la clase `World` con caché.
3. Añadir `WorldChunkRepository` y persistir/recuperar chunks en
   `world_chunks` por `(run_id, chunk_x, chunk_y)`.
4. Implementar `Renderer` con viewport culling por chunks y pintado de
   tiles a 16 px.
5. Conectar `main.py` a una ventana pygame 1280×720 centrada en el chunk
   (0,0); tests headless, verificación Docker y cierre de fase.

## PLAN DE FASE 3

1. Implementar `Inventory` y la entidad `Mike` con salud, hambre, sed,
   infección, batería y posición.
2. Implementar `advance_turn()` con desgaste y muerte por inanición, más
   acciones de comer, beber, usar supresor y venda.
3. Añadir `GameSession` en `loop.py` con reloj de turnos y persistencia
   del estado en `agent_state`.
4. Dibujar las 5 barras en `ui/hud.py` e integrarlas en `main.py`.
5. Tests: 100 turnos sin comer → muerte, inventario, HUD headless.

## PLAN DE FASE 4

1. Implementar `agent/tools.py` con las 10 herramientas y sus esquemas.
2. Implementar `agent/client.py` con bucle de function calling sobre
   `deepseek-flash`, pensamiento desactivado y carga del system prompt.
3. Añadir a `GameSession` el registro de chat y memorias.
4. Escribir el system prompt de Mike con su historia y reglas de tools.
5. Tests con cliente falso: tool call → ejecución → respuesta final.

## PLAN DE FASE 5

1. Implementar `ui/chat.py`: historial, entrada de texto y typewriter.
2. Integrar el chat en `main.py` con envío a DeepSeek y coste de radio.
3. Mostrar errores de enlace y muerte de Mike en el chat.
4. Tests headless del panel y del flujo de entrada.

## PLAN DE FASE 6

1. Implementar 4 subtipos de zombi con IA idle/chase/attack.
2. Implementar combate cuerpo a cuerpo y muerte de Mike.
3. Implementar eventos procedurales (loot, emboscada, tormenta, radio).
4. Integrar zombis y eventos en `GameSession` y dibujarlos.
5. Tests de IA, combate, eventos y game over.

## REGLAS DE ESTE ARCHIVO

1. Antes de empezar una tarea atómica, el agente escribe debajo de
   "## REGISTRO DE TAREAS" una línea con: `[F<N>] <descripción> — INICIO`
2. Al terminarla con test verde, escribe: `[F<N>] <descripción> — OK (<commit hash>)`
3. Al completar una fase entera, marca la fase como `✅` abajo y crea
   un `PHASE_N_DONE.md` con el resumen.
4. Si la fase falla o se atasca, escribe `[F<N>] <descripción> — BLOQUEADA (<razón>)`
   y llama a `ask_human` para destrabar.

## ROADMAP DE FASES

- [x] **Fase 1** — Esqueleto, BD y repositorios SQLite ✅
- [x] **Fase 2** — Mundo procedural con chunks y Perlin noise ✅
- [x] **Fase 3** — Mike, HUD y actualización de estado ✅
- [x] **Fase 4** — Cliente DeepSeek (`deepseek-flash`) con function calling ✅
- [x] **Fase 5** — Chat bidireccional Operador ↔ Mike ✅
- [ ] **Fase 6** — Zombis, combate y eventos narrativos — EN CURSO
- [ ] **Fase 7** — Assets procedurales (sprites + SFX + música)
- [ ] **Fase 8** — Docker, Makefile y distribución
- [ ] **Fase 9** — Persistencia entre runs, meta-progresión y balanceo

## DETALLE POR FASE

### Fase 1 — Esqueleto, BD y repositorios
**Objetivo:** Base sólida donde todo lo demás se apoya.
**Entregables:**
- Estructura de carpetas completa del TASK.md.
- `db/schema.sql`, `db/database.py`, `db/repositories.py`.
- `main.py` que crea una run y la imprime.
- `pytest` pasando con al menos 4 tests.
**Verificación:** `make test` + `python main.py` muestra "Run #1 creada".

### Fase 2 — Mundo procedural
**Objetivo:** Chunks generados, persistentes y visualizables.
**Entregables:**
- `game/world.py` con Perlin en 2 capas.
- `game/renderer.py` con viewport culling.
- Ventana pygame abierta mostrando el chunk (0,0).
**Verificación:** `python main.py` abre ventana 1280x720 con terreno.

### Fase 3 — Mike y HUD
**Objetivo:** Mike existe, tiene estado, se mueve y las barras cambian.
**Entregables:**
- `game/entities.py` con clase Mike.
- `ui/hud.py` con barras de salud, hambre, sed, infección, batería.
- Actualización de estado por turno.
**Verificación:** Simular 100 turnos sin comer → Mike muere.

### Fase 4 — Cliente DeepSeek
**Objetivo:** Mike autónomo que usa tools vía `deepseek-flash`.
**Entregables:**
- `agent/client.py` con bucle de function calling.
- `agent/tools.py` con las 10 herramientas.
- `agent/prompts/system_mike.txt` cargado.
**Verificación:** Mike explora y reporta mensajes que aparecen en UI.

### Fase 5 — Chat bidireccional
**Objetivo:** El humano escribe, Mike responde y el mundo cambia.
**Entregables:**
- `ui/chat.py` con input de texto y typewriter.
- Flujo completo Operador → DeepSeek → tools → mundo.
**Verificación:** Partida de 5 minutos sin crash.

### Fase 6 — Zombis, combate y eventos
**Objetivo:** El mundo es peligroso y narrativo.
**Entregables:**
- 4 subtipos de zombi con IA (idle/chase/attack).
- Combate cuerpo a cuerpo.
- `game/events.py` con eventos procedurales.
**Verificación:** Mike puede morir y el juego termina correctamente.

### Fase 7 — Assets y audio
**Objetivo:** El juego se ve y suena a pixel art post-apocalíptico.
**Entregables:**
- Sprites procedurales cacheados en `assets_cache`.
- SFX con pyfxr.
- Música adaptativa con BloodMusic (o skip si falla).
**Verificación:** 10 sprites válidos + audio audible.

### Fase 8 — Docker y distribución
**Objetivo:** `docker compose up --build` y a jugar.
**Entregables:**
- Dockerfile, docker-compose.yml, Makefile, README, `.env.example`.
**Verificación:** Build exitoso en Linux limpio + ventana abierta.

### Fase 9 — Persistencia y balanceo
**Objetivo:** Dos runs seguidas se sienten diferentes.
**Entregables:**
- `memory` entre runs.
- Meta-progresión (10 muertes → desbloqueo).
- Rasgos aleatorios en Mike.
**Verificación:** Jugar 2 runs, comparar experiencias.

## REGISTRO DE TAREAS

[F1] Scaffold, tooling y estructura de paquetes — OK (04258e6)
[F1] Esquema SQLite, conexión WAL/FK y repositorios — OK (e196d03)
[F1] Run inicial, Refugio 7 determinista y tests — OK (d340dc4)
[F1] Verificación final: 15 tests, ruff, black y `main.py` — OK (d340dc4)
[F2] Generación de chunks con 2 capas Perlin y persistencia — OK (a1f1a43)
[F2] Renderer con viewport culling y ventana pygame — OK (faf6980)
[F2] Verificación Docker: 28 tests, ruff, black y smoke de ventana — OK (faf6980)
[F3] Mike, inventario, turnos y HUD — OK (338207e)
[F4] Cliente DeepSeek con function calling y 10 tools — OK (a6f2c70)
[F5] Chat bidireccional y typewriter — OK (06915c2)
[F6] Zombis, combate y eventos — INICIO
