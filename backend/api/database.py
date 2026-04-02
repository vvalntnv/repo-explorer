from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from api.config import config


class DatabaseManager:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or config.database_url

    def get_session() -> Session: ...

    async def get_asession() -> AsyncSession: ...
