from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.base import Base


class Database:
    def __init__(self, db_url: str, engine_kwargs: dict | None = None):
        self._engine = create_async_engine(db_url, **(engine_kwargs or {}))
        self._session_factory = async_sessionmaker(
            bind=self._engine, class_=AsyncSession, expire_on_commit=False,
            autoflush=False, autocommit=False,
        )

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def create_tables(self) -> None:
        # Import models before create_all so SQLAlchemy metadata is populated.
        from src.infrastructure.db.models import prediction  # noqa: F401
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self._engine.dispose()
