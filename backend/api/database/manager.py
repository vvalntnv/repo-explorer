from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from api.config import config


class DatabaseManager:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or config.database_url
        if not self.database_url:
            raise ValueError("database_url must be provided")

        self._engine = create_engine(self.database_url)
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
        )

        self._async_engine = create_async_engine(self.database_url)
        self._async_session_factory = async_sessionmaker(
            bind=self._async_engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            with session.begin():
                yield session

    @asynccontextmanager
    async def get_asession(self) -> AsyncIterator[AsyncSession]:
        async with self._async_session_factory() as session:
            async with session.begin():
                yield session

    async def dispose(self) -> None:
        self._engine.dispose()
        await self._async_engine.dispose()
