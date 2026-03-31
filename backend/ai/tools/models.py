from pydantic import BaseModel, Field


class FileSnippet(BaseModel):
    file_path: str
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    text: str


class SearchMatch(BaseModel):
    file_path: str
    line_number: int = Field(ge=1)
    line_text: str


class RagResult(BaseModel):
    question: str
    answer: str
    sources: list[str]
    snippets: list[FileSnippet]
    confidence: float = Field(ge=0.0, le=1.0)
