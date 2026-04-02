from collections.abc import AsyncIterable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse

from backend.api.database import DatabaseManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_manager = DatabaseManager()
    try:
        yield
    finally:
        await app.state.database_manager.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/ask", response_class=EventSourceResponse)
async def ask_question() -> AsyncIterable[str]:
    items = ["This is ", "a wa", "rning"]

    for item in items:
        yield item
