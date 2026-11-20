"""Cliente de DeepSeek con bucle de function calling para Mike."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agent.tools import TOOL_SPECS, execute_tool
from config import (
    AGENT_HISTORY_LIMIT,
    AGENT_MAX_TOOL_ROUNDS,
    AGENT_TEMPERATURE,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    GLOBAL_MEMORY_LIMIT,
    ITEM_NAMES,
    PROJECT_ROOT,
    SYSTEM_MIKE_PROMPT_PATH,
)

if TYPE_CHECKING:
    from game.loop import GameSession


class AgentUnavailable(RuntimeError):
    """El agente no puede contactar con DeepSeek."""


@dataclass(frozen=True, slots=True)
class AgentTurnResult:
    """Resultado de una intervención de Mike."""

    text: str
    tools_used: tuple[str, ...]


def _load_env_file() -> None:
    """Carga .env sin sobrescribir variables ya presentes."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _assistant_message(message: Any) -> dict[str, Any]:
    tool_calls = getattr(message, "tool_calls", None) or []
    return {
        "role": "assistant",
        "content": getattr(message, "content", None),
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in tool_calls
        ],
    }


class AgentClient:
    """Envía mensajes a DeepSeek y ejecuta las tools que Mike pida."""

    def __init__(
        self,
        session: GameSession,
        *,
        client: Any | None = None,
        model: str = DEEPSEEK_MODEL,
        api_key: str | None = None,
    ) -> None:
        _load_env_file()
        self._session = session
        self._model = model
        self._api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self._client = client
        self._system_prompt = SYSTEM_MIKE_PROMPT_PATH.read_text(encoding="utf-8")

    @property
    def available(self) -> bool:
        """True si hay cliente inyectado o API key configurada."""
        return self._client is not None or bool(self._api_key)

    def _get_client(self) -> Any:
        if self._client is None:
            if not self._api_key:
                raise AgentUnavailable("Falta DEEPSEEK_API_KEY en el entorno")
            from openai import OpenAI

            self._client = OpenAI(api_key=self._api_key, base_url=DEEPSEEK_BASE_URL)
        return self._client

    def _state_prompt(self) -> str:
        mike = self._session.mike
        inventory = ", ".join(
            f"{ITEM_NAMES.get(item, item)} x{quantity}"
            for item, quantity in sorted(mike.inventory.items.items())
        )
        get_memories = getattr(self._session, "global_memories", None)
        memories = get_memories(GLOBAL_MEMORY_LIMIT) if callable(get_memories) else []
        memory_text = "\n".join(f"- {entry.content}" for entry in memories) or "ninguno"
        return (
            "ESTADO ACTUAL DE MIKE:\n"
            f"Turno: {mike.turn_count}\n"
            f"Posición: ({int(mike.pos_x)}, {int(mike.pos_y)})\n"
            f"Rasgo: {mike.trait}\n"
            f"Salud: {mike.health}/100 | Hambre: {mike.hunger}/100 | "
            f"Sed: {mike.thirst}/100 | Infección: {mike.infection}/100 | "
            f"Radio: {mike.radio_battery}%\n"
            f"Inventario: {inventory or 'vacío'}\n"
            f"Estado: {'vivo' if mike.alive else 'muerto'}\n"
            f"Recuerdos de runs anteriores:\n{memory_text}"
        )

    def _history_messages(self, history: list[Any]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        for message in history:
            if message.role == "operator" and message.content:
                messages.append({"role": "user", "content": message.content})
            elif message.role == "assistant" and message.content:
                messages.append({"role": "assistant", "content": message.content})
        return messages

    def respond(self, operator_message: str) -> AgentTurnResult:
        """Procesa un mensaje del Operador y devuelve la respuesta de Mike."""
        client = self._get_client()
        history = self._session.recent_chat(AGENT_HISTORY_LIMIT)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt},
            {"role": "system", "content": self._state_prompt()},
            *self._history_messages(history),
            {"role": "user", "content": operator_message},
        ]
        self._session.record_chat("operator", content=operator_message)
        tools_used: list[str] = []

        for _ in range(AGENT_MAX_TOOL_ROUNDS):
            try:
                response = client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=TOOL_SPECS,
                    tool_choice="auto",
                    temperature=AGENT_TEMPERATURE,
                    extra_body={"thinking": {"type": "disabled"}},
                )
            except Exception as error:
                raise AgentUnavailable(f"Error al llamar a DeepSeek: {error}") from error

            if not response.choices:
                raise AgentUnavailable("DeepSeek devolvió una respuesta vacía")
            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", None) or []
            messages.append(_assistant_message(message))

            if not tool_calls:
                text = getattr(message, "content", None) or "Mike no responde."
                self._session.record_chat("assistant", content=text)
                return AgentTurnResult(text=text, tools_used=tuple(tools_used))

            for call in tool_calls:
                arguments_raw = call.function.arguments or "{}"
                try:
                    arguments = json.loads(arguments_raw)
                except json.JSONDecodeError:
                    arguments = {}
                if not isinstance(arguments, dict):
                    arguments = {}
                result = execute_tool(self._session, call.function.name, arguments)
                tools_used.append(call.function.name)
                self._session.record_chat(
                    "tool",
                    content=result,
                    tool_name=call.function.name,
                    tool_args=arguments,
                    tool_call_id=call.id,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )

        fallback = "Mike se queda en silencio; la radio se corta."
        self._session.record_chat("assistant", content=fallback)
        return AgentTurnResult(text=fallback, tools_used=tuple(tools_used))
