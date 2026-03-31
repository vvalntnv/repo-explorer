from typing import cast

import numpy as np
from chromadb import AsyncHttpClient, AsyncClientAPI
from chromadb.api.types import Embedding
from vectors.models import ChunkEmbedding

_client: AsyncClientAPI | None = None


async def get_client() -> AsyncClientAPI:
    global _client

    if _client is None:
        _client = await AsyncHttpClient()

    return _client


async def write_embeddings(embeddings: list[ChunkEmbedding]) -> None:
    client = await get_client()

    if not embeddings:
        return

    collection = await client.get_or_create_collection(name="files")
    ids: list[str] = []
    vectors: list[Embedding] = []
    documents: list[str] = []
    metadatas = []

    for chunk in embeddings:
        ids.append(chunk.chunk_id)
        vectors.append(cast(Embedding, np.asarray(chunk.embedding, dtype=np.float32)))
        documents.append(chunk.content)
        metadatas.append(
            {
                "chunk_id": chunk.chunk_id,
                "file_path": chunk.file_path,
                **chunk.metadata,
            }
        )

    await collection.add(
        ids=ids,
        embeddings=vectors,
        documents=documents,
        metadatas=metadatas,  # type: ignore
    )

    print(f"stored {embeddings} in db successfully")
