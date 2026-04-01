from pathlib import Path

from sentence_transformers import SentenceTransformer

from .models import ChunkEmbedding
from . import store

CHUNK_SIZE = 50

model = SentenceTransformer("perplexity-ai/pplx-embed-v1-0.6b", trust_remote_code=True)


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

        embedded = embed_chunk(chunk_content)

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
    embedded = model.encode(content)
    print(f"[embed_chunk] embedding type: {type(embedded)}")

    if hasattr(embedded, "shape"):
        print(f"[embed_chunk] embedding shape: {embedded.shape}")

    return embedded.tolist()
