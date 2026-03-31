import asyncio
import tempfile
from pathlib import Path

from vectors import embedder, store


def _default_text() -> str:
    return (
        "This file is a quick smoke test for the local embedder.\n"
        "It should load the sentence-transformer model and create vectors.\n"
        "The output prints shape and sample values for inspection.\n"
    )


async def _assert_inserted(file_path: Path, expected_vector: list[float]) -> None:
    client = await store.get_client()
    collection = await client.get_or_create_collection(name="files")

    response = await collection.get(
        where={"file_path": str(file_path)}, include=["embeddings", "metadatas"]
    )
    print("[LA RESPONSADA]: ", response)

    breakpoint()
    ids = response.get("ids", [])
    assert ids is not None and len(ids) == 1, f"Expected 1 inserted record, got: {ids}"

    metadatas = response.get("metadatas", [])
    embeddings = response.get("embeddings", [])
    assert metadatas and embeddings

    metadata = metadatas[0]
    stored_vector = embeddings[0]

    assert metadata["file_path"] == str(file_path)
    assert metadata["chunk_id"] == "0"
    assert len(stored_vector) == len(expected_vector)
    assert stored_vector[:5] == expected_vector[:5]
    print(f"[test_embedder] Chroma insert verified for id={ids[0]}")


async def _run_smoke(file_path: Path) -> list[float]:
    vector = await embedder.embed_file(file_path)
    assert vector, "No embedding vectors were returned"

    print(f"Embedded vector length: {len(vector)}")
    print(f"Embedded vector sample: {vector[:5]}")

    await _assert_inserted(file_path, vector)
    return vector


def main() -> None:
    text = _default_text()
    print("No file provided, creating a temporary file for smoke test")
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        prefix="embedder-smoke-",
        delete=False,
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)

    try:
        print(f"Temporary file created: {temp_path}")
        asyncio.run(_run_smoke(temp_path))
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    main()
