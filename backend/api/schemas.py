from datetime import datetime
from typing import Mapping, Optional

from pydantic import BaseModel, Field


class QuestionPayload(BaseModel):
    question: str = Field(..., min_length=1, description="The user's prompt")
    conversation_id: Optional[str] = Field(
        None, description="Optional identifier for threading follow-up questions"
    )
    top_k: int = Field(
        5, ge=1, le=20, description="Number of context chunks to retrieve"
    )
    include_sources: bool = Field(
        False, description="Return source citations with the response"
    )
    metadata: Mapping[str, str] = Field(
        default_factory=dict,
        description="Arbitrary context metadata (e.g. user, locale)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the question was issued"
    )
