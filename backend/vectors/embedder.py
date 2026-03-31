from pathlib import Path

from sentence_transformers import SentenceTransformer

from .models import ChunkEmbedding
from . import store

CHUNK_SIZE = 50

model = SentenceTransformer("perplexity-ai/pplx-embed-v1-0.6b", trust_remote_code=True)


def embed_query(query: str) -> list[float]:
    return embed_chunk(query)


async def embed_file(file: Path) -> list[float]:
    lines = file.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []

    chunk_embeddings: list[ChunkEmbedding] = []
    first_embedding: list[float] = []

    for chunk_index, chunk_start in enumerate(range(0, len(lines), CHUNK_SIZE)):
        chunk_lines = lines[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_content = "\n".join(chunk_lines).strip()
        if not chunk_content:
            continue

        embedded = embed_chunk(chunk_content)
        if not first_embedding:
            first_embedding = embedded

        chunk_embeddings.append(
            ChunkEmbedding(
                chunk_id=f"{file}:{chunk_index}",
                embedding=embedded,
                file_path=str(file),
                metadata={
                    "chunk_index": chunk_index,
                    "start_line": chunk_start + 1,
                    "end_line": chunk_start + len(chunk_lines),
                    "content": chunk_content,
                },
            )
        )

    if not chunk_embeddings:
        return []

    await store.write_embeddings(chunk_embeddings)
    return first_embedding


def embed_chunk(content: str) -> list[float]:
    embedded = model.encode(content)
    print(f"[embed_chunk] embedding type: {type(embedded)}")

    if hasattr(embedded, "shape"):
        print(f"[embed_chunk] embedding shape: {embedded.shape}")

    return embedded.tolist()
