import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from fastapi_batteries.fastapi.exceptions.api_exception import APIException, get_api_exception_handler


@pytest.mark.asyncio
async def test_use_route_path_as_operation_ids(app: FastAPI):
    app.add_exception_handler(APIException, get_api_exception_handler())

    @app.get("/raises-exception")
    async def raises_exception():
        # TODO: How we'll test the exc_note param 🤔
        raise APIException(
            title="Test exception",
            status=400,
            exc_note="This is a test exception note",
        )

    # TODO: We should also handle Pydantic validation errors and convert them to RFC 7807 compliant JSON response
    # class ItemCreate(BaseModel):
    #     qty: NonNegativeInt

    # @app.post("/items")
    # async def create_item(item: ItemCreate):
    #     return {"qty": item.qty}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/raises-exception")

        assert response.status_code == 400
        assert response.json() == {"title": "Test exception", "status": 400}

        # response = await ac.post("/items", json={"qty": "abc"})
        # assert response.status_code == 422
        # assert response.json() == {"qty": 10}
