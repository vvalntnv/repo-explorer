import time
from sentence_transformers import CrossEncoder

_model: CrossEncoder | None = None


def get_model():
    global _model

    if _model is None:
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

    return _model


async def rerank(query: str, documents: list[str]) -> list[tuple[str, float]]:
    start = time.monotonic()
    prediction_matrix = [(query, doc) for doc in documents]

    model = get_model()
    scores = model.predict(prediction_matrix)

    print(f"Completed the predictions for: {time.monotonic() - start}")

    # return [(doc, score) for score, doc in zip(scores, documents)]
    return list(zip(documents, scores))
