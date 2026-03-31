from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")


async def rerank(query: str, documents: list[str]) -> list[tuple[str, float]]:
    scores = model.predict([(query, doc) for doc in documents])

    return [(doc, score) for score, doc in zip(scores, documents)]
