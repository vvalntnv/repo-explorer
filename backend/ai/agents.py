from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent

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

repo_agent = Agent(
    "groq:openai/gpt-oss-120b",
    tools=ALL_TOOLS,
    instructions=INSTRUCTIONS,
)


def build_repo_prompt(question: str, context: str = "") -> str:
    return PROMPT_TEMPLATE.format(question=question, context=context)
