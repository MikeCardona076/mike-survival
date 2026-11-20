# PHASE 5 DONE — Chat bidireccional

- **Fecha:** 2026-11-19
- **Commit:** `06915c2`
- **Estado:** completada y verificada. Se continúa con la Fase 6.

## Qué se hizo

- `ui/chat.py`: historial de radio, entrada de una línea, backspace,
  límite de caracteres, typewriter y panel inferior.
- `main.py`: captura de teclado, envío al agente, coste de batería
  (1–3%), mensajes de sistema si no hay enlace o batería, muerte de Mike.
- `AgentClient` integrado en el bucle real de la ventana.
- El historial de chat se persiste en `chat_history`.

## Verificación

- Docker `python:3.12-slim`: **58 tests pasan**, ruff limpio, black 35
  archivos sin cambios.
- Local: 45 tests pasan; 3 módulos con `noise` omitidos.
- Smoke `python main.py` headless 5 s sin crash (timeout 124 esperado).
- Tests de chat: escritura, envío, límite, backspace, typewriter y dibujo
  con todos los roles.

## Pendiente

- Fase 6: zombis, combate y eventos.
