import os
from pathlib import Path

from sentence_transformers import SentenceTransformer
import torch

from .models import ChunkEmbedding
from . import store

CHUNK_SIZE = 50
MAX_CHUNK_CHARACTERS = 4_000
DEFAULT_MAX_SEQ_LENGTH = 1_024
DEFAULT_EMBEDDER_DEVICE = "cpu"

_model: SentenceTransformer | None = None


def get_model():
    global _model

    if _model is None:
        device = os.getenv("EMBEDDING_DEVICE", DEFAULT_EMBEDDER_DEVICE)
        _model = SentenceTransformer(
            "perplexity-ai/pplx-embed-v1-0.6b",
            trust_remote_code=True,
            device=device,
        )

        max_seq_length = int(
            os.getenv("EMBEDDING_MAX_SEQ_LENGTH", str(DEFAULT_MAX_SEQ_LENGTH))
        )
        _model.max_seq_length = max_seq_length

        print(
            "[embedder] loaded model on "
            f"device={device} max_seq_length={_model.max_seq_length}"
        )

    return _model


def embed_query(query: str) -> list[float]:
    return embed_chunk(query)


async def embed_file(file: Path) -> list[ChunkEmbedding]:
    lines = file.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []

    chunk_embeddings: list[ChunkEmbedding] = []

    chunk_index = 0

    start = 0
    end = len(lines)
    step = CHUNK_SIZE
    for chunk_start in range(start, end, step):
        chunk_lines = lines[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_content = "\n".join(chunk_lines).strip()
        if not chunk_content:
            continue

        if len(chunk_content) > MAX_CHUNK_CHARACTERS:
            chunk_content = chunk_content[:MAX_CHUNK_CHARACTERS]

        try:
            embedded = embed_chunk(chunk_content)
        except RuntimeError as exc:
            if _is_out_of_memory_error(exc):
                _clear_torch_caches()
                print(
                    f"[embed_file] skipping chunk due to OOM: "
                    f"{file}:{chunk_index} ({exc})"
                )
                continue

            raise

        chunk_embeddings.append(
            ChunkEmbedding(
                chunk_id=f"{file}:{chunk_index}",
                embedding=embedded,
                file_path=str(file),
                content=chunk_content,
                metadata={
                    "chunk_index": chunk_index,
                    "start_line": chunk_start + 1,
                    "end_line": chunk_start + len(chunk_lines),
                },
            )
        )
        chunk_index += 1

    if not chunk_embeddings:
        return []

    await store.write_embeddings(chunk_embeddings)
    return chunk_embeddings


def embed_chunk(content: str) -> list[float]:
    model = get_model()

    embedded = model.encode(content, convert_to_numpy=True)

    if hasattr(embedded, "shape"):
        print(f"[embed_chunk] embedding shape: {embedded.shape}")

    return embedded.tolist()


def _is_out_of_memory_error(exc: RuntimeError) -> bool:
    lowered = str(exc).lower()
    return "out of memory" in lowered or "mps backend out of memory" in lowered


def _clear_torch_caches() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
