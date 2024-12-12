from typing import Annotated

import pytest
from fastapi import FastAPI, Query
from httpx import ASGITransport, AsyncClient

from fastapi_batteries.pydantic.schemas import PaginationOffsetLimit


@pytest.mark.asyncio
async def test_pagination_offset_limit_schema(app: FastAPI):
    @app.get("/items")
    async def get_items(offset_limit: Annotated[PaginationOffsetLimit, Query()]):
        return {"offset": offset_limit.offset, "limit": offset_limit.limit}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/items")
        assert response.status_code == 200
        assert response.json() == {"offset": 0, "limit": 10}

        response = await ac.get("/items?offset=10&limit=20")
        assert response.status_code == 200
        assert response.json() == {"offset": 10, "limit": 20}
