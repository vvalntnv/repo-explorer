import time
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")


async def rerank(query: str, documents: list[str]) -> list[tuple[str, float]]:
    start = time.monotonic()
    prediction_matrix = [(query, doc) for doc in documents]

    scores = model.predict(prediction_matrix)

    print(f"Completed the predictions for: {time.monotonic() - start}")

    # return [(doc, score) for score, doc in zip(scores, documents)]
    return list(zip(documents, scores))
