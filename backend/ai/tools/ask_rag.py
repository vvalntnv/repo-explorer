import math
from pathlib import Path

from vectors.store import get_client
from vectors import embedder
from vectors import reranker

from ._common import resolve_repo_path
from .models import FileSnippet, RagResult


async def ask_rag(
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

    db_client = await get_client()
    collection = await db_client.get_collection(name="files")

    question_embedding = embedder.embed_query(question)
    retrieval_k = max(top_k, rerank_k)

    matches = await collection.query(
        query_embeddings=question_embedding,
        include=["metadatas", "documents"],
        n_results=max(retrieval_k * 2, 20),
    )

    docs = matches["documents"][0] if matches["documents"] is not None else []
    metadatas = matches["metadatas"][0] if matches["metadatas"] is not None else []

    candidates: list[tuple[str, dict[str, object]]] = []
    seen_files: set[str] = set()
    for doc, metadata in zip(docs, metadatas):
        if not isinstance(doc, str) or not isinstance(metadata, dict):
            continue

        file_path_value = metadata.get("file_path")
        if not isinstance(file_path_value, str):
            continue

        try:
            resolved_file_path = Path(file_path_value).resolve()
            resolved_file_path.relative_to(base)
        except Exception:
            continue

        seen_files.add(str(resolved_file_path))
        if len(seen_files) > max_files:
            break

        candidates.append((doc, metadata))

    if not candidates:
        return RagResult(
            question=question,
            answer="I could not find relevant indexed context under the requested root.",
            sources=[],
            snippets=[],
            confidence=0.0,
        )

    reranked = await reranker.rerank(question, [doc for doc, _ in candidates])

    metadata_by_doc: dict[str, list[dict[str, object]]] = {}
    for doc, metadata in candidates:
        metadata_by_doc.setdefault(doc, []).append(metadata)

    ranked_items: list[tuple[str, dict[str, object], float]] = []
    for doc, score in sorted(reranked, key=lambda item: float(item[1]), reverse=True):
        metadata_list = metadata_by_doc.get(doc)
        if not metadata_list:
            continue
        ranked_items.append((doc, metadata_list.pop(0), float(score)))
        if len(ranked_items) >= rerank_k:
            break

    if not ranked_items:
        return RagResult(
            question=question,
            answer="I could not rerank relevant context for this question.",
            sources=[],
            snippets=[],
            confidence=0.0,
        )

    top_items = ranked_items[:top_k]
    snippets: list[FileSnippet] = []
    sources: list[str] = []
    for doc, metadata, _ in top_items:
        file_path = str(metadata.get("file_path", ""))
        if file_path and file_path not in sources:
            sources.append(file_path)

        start_line = int(metadata.get("start_line", 1))
        end_line = int(metadata.get("end_line", start_line))
        if end_line < start_line:
            end_line = start_line

        snippets.append(
            FileSnippet(
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                text=doc,
            )
        )

    confidence_values = [1.0 / (1.0 + math.exp(-score)) for _, _, score in top_items]
    confidence = sum(confidence_values) / len(confidence_values)
    answer_lines = [f"Top matches for: {question}"]
    for snippet in snippets:
        answer_lines.append(
            f"- {snippet.file_path}:{snippet.line_start}-{snippet.line_end}"
        )

    return RagResult(
        question=question,
        answer="\n".join(answer_lines),
        sources=sources,
        snippets=snippets,
        confidence=confidence,
    )
