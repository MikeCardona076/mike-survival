# PHASE 8 DONE — Docker y distribución

- **Fecha:** 2026-11-19
- **Commit:** `c453f49`
- **Estado:** completada y verificada. Se continúa con la Fase 9.

## Qué se hizo

- `Dockerfile` con Python 3.12, librerías SDL, compilación de `noise`,
  `pyfxr` y arranque de `main.py`.
- `docker-compose.yml` con X11, volumen `./data` y variables de entorno.
- `.dockerignore` y targets `docker-build`, `docker-test`, `compose-up`
  y `compose-down` en el `Makefile`.
- README con instalación nativa, Docker y controles.

## Verificación

- `docker build -t mike-survival:phase8 .` → exit 0.
- Dentro de la imagen: **74 tests pasan**.
- `docker compose config --quiet` → exit 0.
- La imagen exporta correctamente y el `CMD` apunta a `python main.py`.

## Pendiente

- Fase 9: rasgos, memoria global y meta-progresión.
