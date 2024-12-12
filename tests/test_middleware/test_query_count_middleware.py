import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from fastapi_batteries.fastapi.middlewares.query_count import QueryCountMiddleware

# Test database URL - using SQLite for simplicity
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.mark.asyncio
async def test_single_query_count(app: FastAPI, async_engine: AsyncEngine):
    app.add_middleware(QueryCountMiddleware, engine=async_engine)

    @app.get("/test-single-query")
    async def test_single_query():
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.commit()
        return {"message": "ok"}

    @app.get("/test-multiple-queries")
    async def test_multiple_queries():
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.execute(text("SELECT 2"))
            await conn.execute(text("SELECT 3"))
            await conn.commit()
        return {"message": "ok"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert "X-DB-Query-Count" in response.headers
        assert response.headers["X-DB-Query-Count"] == "0"

        response = await ac.get("/test-single-query")
        assert response.status_code == 200
        assert "X-DB-Query-Count" in response.headers
        assert response.headers["X-DB-Query-Count"] == "1"

        response = await ac.get("/test-multiple-queries")
        assert response.status_code == 200
        assert "X-DB-Query-Count" in response.headers
        assert response.headers["X-DB-Query-Count"] == "3"
