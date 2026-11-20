"""Ejecuta los turnos de Mike fuera del hilo de render.

Así la ventana sigue respondiendo mientras DeepSeek tarda en contestar.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Any

from agent.client import AgentUnavailable


@dataclass(frozen=True, slots=True)
class AgentJobResult:
    """Resultado de una petición lanzada al agente."""

    ok: bool
    text: str


class AgentWorker:
    """Worker de un solo hilo para no bloquear pygame."""

    def __init__(self, agent: Any) -> None:
        self._agent = agent
        self._results: queue.Queue[AgentJobResult] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._busy = False

    @property
    def busy(self) -> bool:
        """True mientras hay una petición en curso."""
        return self._busy

    def submit(self, text: str) -> bool:
        """Lanza una petición; devuelve False si ya hay una en curso."""
        if self._busy:
            return False
        self._busy = True

        def run() -> None:
            try:
                result = self._agent.respond(text)
            except AgentUnavailable as error:
                self._results.put(AgentJobResult(False, str(error)))
            except Exception as error:  # se informa en la UI, no se pierde
                self._results.put(AgentJobResult(False, f"Error inesperado: {error}"))
            else:
                self._results.put(AgentJobResult(True, result.text))
            finally:
                self._busy = False

        self._thread = threading.Thread(target=run, name="mike-agent", daemon=True)
        self._thread.start()
        return True

    def poll(self) -> AgentJobResult | None:
        """Devuelve el resultado si ya está listo, sin bloquear."""
        try:
            return self._results.get_nowait()
        except queue.Empty:
            return None

    def join(self, timeout: float = 1.0) -> None:
        """Espera brevemente al hilo (útil al cerrar)."""
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=timeout)
