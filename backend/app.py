from typing import AsyncIterable
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse

app = FastAPI()


@app.post("/ask", response_class=EventSourceResponse)
async def ask_question() -> AsyncIterable[str]:
    items = ["This is ", "a wa", "rning"]

    for item in items:
        yield item
