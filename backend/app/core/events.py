async def create_tables() -> None:
    from app.db.base import engine
    from app.db.models.base import Base
    import app.db.models  # noqa — registers all models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db_connections() -> None:
    from app.db.base import engine
    await engine.dispose()
