from __future__ import annotations

from pydantic import BaseModel, Field


class ChunkEmbedding(BaseModel):
    """Represents one embedded chunk and its provenance metadata."""

    chunk_id: str
    file_path: str
    embedding: list[float] = Field(..., description="Embedding vector for the chunk")
    content: str
    metadata: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict,
        description="Additional chunk metadata, including custom keys when needed",
    )
