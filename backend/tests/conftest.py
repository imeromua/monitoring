import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.db.base import get_db

@pytest.fixture(autouse=True)
def mock_redis():
    with pytest.MonkeyPatch.context() as mp:
        mock = AsyncMock()
        mock.incr.return_value = 1
        mock.expire.return_value = True
        
        # Patch the redis_client in the middleware module
        mp.setattr("app.api.middleware.rate_limit.redis_client", mock)
        yield mock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    # Mocking the database session
    session = MagicMock(spec=AsyncSession)
    yield session

@pytest.fixture
async def client(db_session):
    # Override get_db to return our mock session
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
