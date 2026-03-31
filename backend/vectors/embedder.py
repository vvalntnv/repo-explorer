from pathlib import Path
from sentence_transformers import SentenceTransformer
from .models import ChunkEmbedding
import store

CHUNK_SIZE = 50

model = SentenceTransformer("perplexity-ai/pplx-embed-v1-0.6b", trust_remote_code=True)


async def embed_file(file: Path) -> list[float]:
    lines = []
    with open(file, "r") as handler:
        while line := handler.readline():
            lines.append(line)

            if len(lines) >= CHUNK_SIZE:
                break

    if not lines:
        return []

    content = "\n".join(lines)
    embedded = embed_chunk(content)

    chunk_data = ChunkEmbedding(
        chunk_id="0",
        embedding=embedded,
        file_path=str(file),
        content=content,
    )

    await store.write_embeddings([chunk_data])
    return embedded


def embed_chunk(content: str) -> list[float]:
    embedded = model.encode(content)
    print(f"[embed_chunk] embedding type: {type(embedded)}")

    if hasattr(embedded, "shape"):
        print(f"[embed_chunk] embedding shape: {embedded.shape}")

    return embedded.tolist()
