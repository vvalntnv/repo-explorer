import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_database
from api.schemas import QuestionPayload


router = APIRouter()


@router.post("/ask", response_class=EventSourceResponse)
async def question(
    question: QuestionPayload, database: AsyncSession = Depends(get_database)
) -> EventSourceResponse:
    ...
