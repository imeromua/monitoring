import asyncio
from app.db.base import Base, engine

# Import all models so SQLAlchemy registers them
from app.models import user, store, category, product, session, result, stats  # noqa


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
