from backend.api.database import DatabaseManager


async def database():
    manager = DatabaseManager()

    async with manager.get_asession() as session:
        yield session
