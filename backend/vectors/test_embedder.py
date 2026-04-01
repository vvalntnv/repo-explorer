import asyncio
from pathlib import Path

from chromadb.errors import NotFoundError
from ai.tools import ask_rag

from vectors import embedder, store

COLLECTION_NAME = "files"
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "node_modules",
    "chroma",
    "db",
}
MAX_FILE_SIZE_BYTES = 512_000


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _iter_repository_files(root: Path) -> list[Path]:
    files: list[Path] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in SKIP_DIRS for part in file_path.parts):
            continue
        if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            continue
        if not _is_probably_utf8_text(file_path):
            continue
        files.append(file_path)

    return sorted(files)


def _is_probably_utf8_text(file_path: Path) -> bool:
    sample = file_path.read_bytes()[:4096]
    if b"\x00" in sample:
        return False

    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False

    return True


async def _delete_collection_if_exists() -> None:
    client = await store.get_client()
    try:
        await client.delete_collection(name=COLLECTION_NAME)
    except NotFoundError:
        return


async def _run_repository_embedding_smoke_test() -> None:
    root = _repo_root()
    files = _iter_repository_files(root)

    assert files, "No files found in repository"

    await _delete_collection_if_exists()

    embedded_files = 0
    skipped_files = 0
    total_chunks = 0

    try:
        for file_path in files:
            try:
                chunks = await embedder.embed_file(file_path)
            except UnicodeDecodeError:
                skipped_files += 1
                continue

            if chunks:
                embedded_files += 1
                total_chunks += len(chunks)

        assert embedded_files > 0, "No repository files were embedded"

        rag_result = await ask_rag(
            question=("Where is the rag embedding handled?"),
            root="backend",
            top_k=3,
            rerank_k=3,
            max_files=50,
        )

        assert rag_result.sources, "ask_rag returned no sources"
        assert rag_result.snippets, "ask_rag returned no snippets"

        has_backend_app_match = any(
            source.endswith("backend/app.py") for source in rag_result.sources
        )
        has_expected_content = any(
            '"/ask"' in snippet.text and "EventSourceResponse" in snippet.text
            for snippet in rag_result.snippets
        )

        assert has_backend_app_match, (
            "Expected at least one hit from backend/app.py in top retrieval results"
        )
        assert has_expected_content, (
            "Expected retrieved content mentioning /ask and EventSourceResponse"
        )

        print(
            "[test_embedder] embedded "
            f"{embedded_files} files, skipped {skipped_files}, stored {total_chunks} chunks"
        )
    finally:
        await _delete_collection_if_exists()


def main() -> None:
    asyncio.run(_run_repository_embedding_smoke_test())


if __name__ == "__main__":
    main()
