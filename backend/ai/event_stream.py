from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Any

from pydantic_ai import (
    AgentStreamEvent,
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    RunContext,
    TextPartDelta,
    ThinkingPartDelta,
    ToolCallPartDelta,
)


async def log_agent_events(
    ctx: RunContext[Any],
    event_stream: AsyncIterable[AgentStreamEvent],
) -> None:
    """Print streamed model reasoning/tool events during an agent run."""
    del ctx

    async for event in event_stream:
        if isinstance(event, PartDeltaEvent):
            if isinstance(event.delta, ThinkingPartDelta):
                delta = event.delta.content_delta
                if delta:
                    print(f"[agent:thinking] {delta}", flush=True)
            elif isinstance(event.delta, ToolCallPartDelta):
                print(f"[agent:tool-args-delta] {event.delta.args_delta}", flush=True)
            elif isinstance(event.delta, TextPartDelta):
                continue
        elif isinstance(event, FunctionToolCallEvent):
            print(
                "[agent:tool-call] "
                f"name={event.part.tool_name} "
                f"id={event.part.tool_call_id} "
                f"args={event.part.args}",
                flush=True,
            )
        elif isinstance(event, FunctionToolResultEvent):
            print(
                "[agent:tool-result] "
                f"id={event.tool_call_id} "
                f"result={event.result.content}",
                flush=True,
            )
        elif isinstance(event, FinalResultEvent):
            print(
                f"[agent:final-result-start] tool_name={event.tool_name}",
                flush=True,
            )
