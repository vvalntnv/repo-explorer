from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import DatabaseManager


async def get_database(request: Request) -> AsyncIterator[AsyncSession]:
    manager: DatabaseManager = request.app.state.database_manager

    async with manager.get_asession() as session:
        yield session
