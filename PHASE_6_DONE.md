# PHASE 6 DONE — Zombis, combate y eventos

- **Fecha:** 2026-11-19
- **Commit:** `2314ff4`
- **Estado:** completada y verificada. Se continúa con la Fase 7.

## Qué se hizo

- 4 subtipos de zombi (`walker`, `runner`, `brute`, `screecher`) con IA
  idle/chase/attack, cooldown y daño.
- Combate cuerpo a cuerpo (`game/combat.py`) y herramienta `attack`.
- Spawn determinista de zombis y refuerzos por turno.
- `game/events.py`: loot, emboscada, tormenta, radio y susurro del virus,
  persistidos en la tabla `events`.
- `GameSession`: zombis, combate, eventos y game over con causa de muerte.
- Renderer de entidades (Mike y zombis) y mensajes de sistema en el chat.

## Verificación

- Docker `python:3.12-slim`: **68 tests pasan**, ruff limpio, black 37
  archivos sin cambios.
- Local: 53 tests pasan; módulos con `noise` omitidos.
- Smoke `python main.py` 5 s sin crash.
- Tests: persecución, cooldown de ataque, muerte de zombi, spawn válido,
  eventos deterministas y combate integrado en la sesión.

## Pendiente

- Fase 7: sprites y audio procedurales.
