from typing import AsyncIterable

from fastapi import APIRouter
from fastapi.responses import EventSourceResponse

from api.schemas import QuestionPayload

from ai.agents import build_repo_prompt, repo_agent
from ai.tools._common import use_repo_root
from repositories.explore_repo_service import ExploreRepositoryService


router = APIRouter()


@router.post("/ask", response_class=EventSourceResponse)
async def question(
    question: QuestionPayload,
    # database: AsyncSession = Depends(get_database),
) -> AsyncIterable[str]:
    yield "Exploring the directory..."

    with use_repo_root(question.path_to_repo):
        await ExploreRepositoryService(question.path_to_repo).explore()
        prompt = build_repo_prompt(
            question=question.question,
            context=f"Repository root: {question.path_to_repo}",
        )

        async with repo_agent.run_stream(prompt) as stream:
            async for text in stream.stream_text():
                yield text
