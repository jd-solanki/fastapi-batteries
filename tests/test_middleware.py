import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from fastapi_batteries.fastapi.middlewares import RequestProcessTimeMiddleware

# TODO: Write tests for QueryCountMiddleware


@pytest.mark.asyncio
async def test_process_time_header(app: FastAPI):
    """Test that the middleware adds X-Process-Time header to responses."""
    app.add_middleware(RequestProcessTimeMiddleware)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")

        # Verify response is successful
        assert response.status_code == 200

        print(f"response.headers: {response.headers}")

        # Verify X-Process-Time header exists
        assert "x-process-time" in response.headers
        # Verify header format (should end with "ms")
        assert response.headers["x-process-time"].endswith("ms")

        # Verify header value is a valid float (removing "ms" suffix)
        process_time = float(response.headers["x-process-time"][:-2])
        assert process_time > 0
