"""SFX procedurales con pyfxr y reproducción con pygame.mixer."""

from __future__ import annotations

import logging

import pyfxr
import pygame

from config import AUDIO_SAMPLE_RATE, AUDIO_VOLUME

logger = logging.getLogger(__name__)


class AudioManager:
    """Genera y reproduce efectos de sonido sintetizados."""

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(
                    frequency=AUDIO_SAMPLE_RATE,
                    size=-16,
                    channels=1,
                )
            except pygame.error:
                logger.warning("No se pudo inicializar el audio")
                return
        self._build()

    @property
    def available(self) -> bool:
        """True si hay al menos un sonido cargado."""
        return bool(self._sounds)

    def _build(self) -> None:
        generators = {
            "pickup": pyfxr.pickup,
            "hit": pyfxr.hurt,
            "radio": pyfxr.laser,
            "suppressor": pyfxr.powerup,
            "death": pyfxr.explosion,
        }
        for name, generator in generators.items():
            try:
                sound = pygame.mixer.Sound(buffer=generator())
            except (pygame.error, TypeError, ValueError):
                logger.warning("No se pudo generar el SFX %s", name)
                continue
            sound.set_volume(AUDIO_VOLUME)
            self._sounds[name] = sound

    def play(self, name: str) -> None:
        """Reproduce un SFX si está disponible."""
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()
