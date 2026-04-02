from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import DatabaseManager
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_manager = DatabaseManager()
    try:
        yield
    finally:
        await app.state.database_manager.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


# @app.post("/ask", response_class=EventSourceResponse)
# async def ask_question() -> AsyncIterable[str]:
#     items = ["This is ", "a wa", "rning"]
#
#     for item in items:
#         yield item
