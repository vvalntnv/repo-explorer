import re

from ._common import resolve_repo_path
from .models import RagResult

TOKEN_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]+")


def ask_rag(
    question: str,
    root: str = ".",
    top_k: int = 10,
    rerank_k: int = 5,
    max_files: int = 200,
) -> RagResult:
    """Run a lightweight local RAG pipeline and return evidence-backed context."""
    if not question.strip():
        raise ValueError("question must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if rerank_k < 1:
        raise ValueError("rerank_k must be >= 1")
    if max_files < 1:
        raise ValueError("max_files must be >= 1")

    try:
        base = resolve_repo_path(root)
    except ValueError as exc:
        raise ValueError(f"Root must stay inside repository: {root}") from exc

    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"Directory not found: {root}")

    raise NotImplementedError("This function is not yet implemented")
