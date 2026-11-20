# PHASE 4 DONE — Cliente DeepSeek y herramientas

- **Fecha:** 2026-11-19
- **Commit:** `a6f2c70`
- **Estado:** completada y verificada. Se continúa con la Fase 5.

## Qué se hizo

- `agent/tools.py`: 10 herramientas (`move`, `scan`, `scavenge`, `eat`,
  `drink`, `use_suppressor`, `use_bandage`, `rest`, `attack`, `remember`)
  con esquemas JSON y ejecución sobre la sesión.
- `agent/client.py`: bucle de function calling con `deepseek-flash`,
  `extra_body={"thinking":{"type":"disabled"}}`, historial reciente,
  resumen de estado y persistencia del chat.
- `agent/prompts/system_mike.txt`: personalidad, historia y reglas.
- `GameSession`: registro de chat y memorias.
- Tests con cliente DeepSeek falso (sin red).

## Verificación

- Docker `python:3.12-slim`: **53 tests pasan**, ruff limpio, black 34
  archivos sin cambios.
- Local: 40 tests pasan; 3 módulos con `noise` omitidos.
- Tests clave: tool call → efecto en Mike → respuesta final; sin API key
  el cliente falla de forma controlada.

## Pendiente

- Fase 5: chat en pantalla y envío real desde el Operador.
