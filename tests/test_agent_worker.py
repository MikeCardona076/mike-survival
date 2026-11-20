"""Tests del worker asíncrono del agente."""

from __future__ import annotations

import time

from agent.client import AgentTurnResult
from agent.worker import AgentWorker


class FakeAgent:
    def __init__(self, text: str = "eco", delay: float = 0.05) -> None:
        self._text = text
        self._delay = delay

    def respond(self, message: str) -> AgentTurnResult:
        time.sleep(self._delay)
        return AgentTurnResult(text=f"{self._text}:{message}", tools_used=())


def test_submit_does_not_block_and_returns_result() -> None:
    worker = AgentWorker(FakeAgent(delay=0.12))

    started = time.monotonic()
    assert worker.submit("hola") is True
    elapsed = time.monotonic() - started

    assert elapsed < 0.1
    assert worker.busy is True
    assert worker.poll() is None

    result = None
    for _ in range(100):
        result = worker.poll()
        if result is not None:
            break
        time.sleep(0.01)

    assert result is not None
    assert result.ok is True
    assert result.text == "eco:hola"
    assert worker.busy is False


def test_double_submit_is_rejected() -> None:
    worker = AgentWorker(FakeAgent(delay=0.1))

    assert worker.submit("uno") is True
    assert worker.submit("dos") is False

    worker.join(timeout=2.0)


def test_failure_is_returned_to_the_ui() -> None:
    class BrokenAgent:
        def respond(self, message: str) -> AgentTurnResult:
            raise RuntimeError("sin enlace")

    worker = AgentWorker(BrokenAgent())
    assert worker.submit("hola") is True

    result = None
    for _ in range(100):
        result = worker.poll()
        if result is not None:
            break
        time.sleep(0.01)

    assert result is not None
    assert result.ok is False
    assert "sin enlace" in result.text
