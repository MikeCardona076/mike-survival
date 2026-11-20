# PHASE 7 DONE — Sprites y audio procedurales

- **Fecha:** 2026-11-19
- **Commit:** `f778c2e`
- **Estado:** completada y verificada. Se continúa con la Fase 8.

## Qué se hizo

- `assets/sprites.py`: 10 sprites PNG RGBA de 16×16 generados con Pillow
  (Mike, Mike herido, 4 zombis y 4 objetos).
- `AssetCacheRepository`: caché en la tabla `assets_cache` con upsert.
- `SpriteSet`: carga perezosa y reutiliza los sprites cacheados.
- `assets/audio.py`: 5 SFX sintetizados con `pyfxr` (`pickup`, `hit`,
  `radio`, `suppressor`, `death`) reproducidos con `pygame.mixer`.
- Integración en el renderer (entidades con sprites) y en el bucle
  (sonidos según eventos). La música adaptativa se omite, como permite
  el brief si no hay BloodMusic.

## Verificación

- Docker `python:3.12-slim`: **74 tests pasan**, ruff limpio, black 39
  archivos sin cambios, `pyfxr` compilado/instalado desde wheel.
- Local: 59 tests pasan; módulos con `noise` omitidos.
- Tests: 10 PNG válidos, caché persistente, SpriteSet y SFX disponibles.

## Pendiente

- Fase 8: Docker y distribución.
