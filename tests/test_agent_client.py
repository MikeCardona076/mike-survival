"""Tests del cliente DeepSeek con un cliente falso."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from agent.client import AgentClient, AgentUnavailable
from config import DEEPSEEK_MODEL
from game.entities import Mike


class FakeCompletions:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses: list[Any]) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


class FakeSession:
    def __init__(self) -> None:
        self.run = SimpleNamespace(seed=7)
        self.mike = Mike()
        self.chat: list[Any] = []
        self.persisted = 0
        self.events: list[str] = []

    def recent_chat(self, limit: int = 8) -> list[Any]:
        return []

    def record_chat(
        self,
        role: str,
        content: str | None = None,
        tool_name: str | None = None,
        tool_args: dict[str, Any] | None = None,
        tool_call_id: str | None = None,
    ) -> Any:
        message = SimpleNamespace(
            role=role,
            content=content,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_call_id=tool_call_id,
        )
        self.chat.append(message)
        return message

    def persist(self) -> None:
        self.persisted += 1

    def add_event(self, text: str) -> None:
        self.events.append(text)


def _tool_response(name: str, arguments: dict[str, Any], call_id: str = "call_1") -> Any:
    call = SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[call]))]
    )


def _text_response(text: str) -> Any:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text, tool_calls=None))]
    )


def test_client_executes_tool_and_returns_final_text() -> None:
    session = FakeSession()
    fake = FakeClient([_tool_response("eat", {}), _text_response("He comido.")])
    client = AgentClient(session, client=fake)

    result = client.respond("Come algo")

    assert result.text == "He comido."
    assert result.tools_used == ("eat",)
    assert session.mike.inventory.count("food") == 1
    assert [message.role for message in session.chat] == ["operator", "tool", "assistant"]
    assert fake.chat.completions.calls[0]["model"] == DEEPSEEK_MODEL
    assert fake.chat.completions.calls[0]["extra_body"] == {"thinking": {"type": "disabled"}}
    assert fake.chat.completions.calls[0]["tool_choice"] == "auto"


def test_client_without_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    client = AgentClient(FakeSession())

    assert client.available is False
    with pytest.raises(AgentUnavailable):
        client.respond("Mike, ¿me escuchas?")


def test_client_handles_empty_response() -> None:
    session = FakeSession()
    fake = FakeClient([_text_response("")])
    client = AgentClient(session, client=fake)

    result = client.respond("Hola")

    assert result.text == "Mike no responde."
