import asyncio
import json
from collections.abc import AsyncIterator
from typing import AsyncIterable

from fastapi import APIRouter, Depends
from fastapi.responses import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_database
from api.schemas import QuestionPayload

from ai.agents import repo_agent
from backend.repositories.explore_repo_service import ExploreRepositoryService


router = APIRouter()


@router.post("/ask", response_class=EventSourceResponse)
async def question(
    question: QuestionPayload,
    # database: AsyncSession = Depends(get_database),
) -> AsyncIterable[str]:
    yield "Exporing the directory..."

    await ExploreRepositoryService(question.path_to_repo).explore()

    async with repo_agent.run_stream(question.question) as stream:
        async for text in stream.stream_text():
            yield text
