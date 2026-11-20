# PLAN DE CONSTRUCCIÓN — MIKE: SEÑAL DE SUPERVIVENCIA

Este archivo es el estado vivo del proyecto. El agente lo lee al inicio
de cada turno y lo actualiza al final de cada fase.

## ESTADO ACTUAL

- **Fase en curso:** 2 (pendiente de aprobación del Operador)
- **Tarea actual:** Fase 1 cerrada; esperando aprobación para iniciar Fase 2
- **Última actualización:** 2026-11-19
- **Commit de referencia:** d340dc4

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
- [ ] **Fase 2** — Mundo procedural con chunks y Perlin noise
- [ ] **Fase 3** — Mike, HUD y actualización de estado
- [ ] **Fase 4** — Cliente DeepSeek (`deepseek-flash`) con function calling
- [ ] **Fase 5** — Chat bidireccional Operador ↔ Mike
- [ ] **Fase 6** — Zombis, combate y eventos narrativos
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
