from chromadb import AsyncHttpClient, AsyncClientAPI
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
    vectors = []
    metadatas = []
    documents = []
    ids = []

    for id, embedding in enumerate(embeddings):
        vectors.append(embedding.embedding)
        metadatas.append(
            {
                "file_path": embedding.file_path,
                "chunk_id": embedding.chunk_id,
            }
        )
        ids.append(str(id))
        documents.append(embedding.content)

    await collection.add(
        ids=ids,
        embeddings=vectors,
        documents=documents,
        metadatas=metadatas,  # type: ignore
    )

    print(f"stored {embeddings} in db successfully")
