from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic_ai import Agent

from .event_stream import log_agent_events
from .tools import ALL_TOOLS

_BASE_DIR = Path(__file__).resolve().parents[1]
_INSTRUCTIONS_PATH = _BASE_DIR / "agent_instructions.md"
_PROMPT_PATH = _BASE_DIR / "agent_prompt.md"


def _load_agent_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")

    return path.read_text(encoding="utf-8").strip()


INSTRUCTIONS = _load_agent_text(_INSTRUCTIONS_PATH)
PROMPT_TEMPLATE = _load_agent_text(_PROMPT_PATH)

DEFAULT_REPO_AGENT_MODEL = "groq:openai/gpt-oss-120b"
REPO_AGENT_MODEL = os.getenv("REPO_AGENT_MODEL", DEFAULT_REPO_AGENT_MODEL)

_repo_agent = Agent(
    REPO_AGENT_MODEL,
    tools=ALL_TOOLS,
    instructions=INSTRUCTIONS,
)


class AgentWithEventLogging:
    def __init__(self, agent: Agent[Any, Any]) -> None:
        self._agent = agent

    def __getattr__(self, item: str) -> Any:
        return getattr(self._agent, item)

    def run_stream(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("event_stream_handler", log_agent_events)
        return self._agent.run_stream(*args, **kwargs)


repo_agent = AgentWithEventLogging(_repo_agent)


def build_repo_prompt(question: str, context: str = "") -> str:
    return PROMPT_TEMPLATE.format(question=question, context=context)
