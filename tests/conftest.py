import pytest
from fastapi import FastAPI


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app with RequestProcessTimeMiddleware for testing."""
    app = FastAPI()

    @app.get("/health")
    async def get_health():
        return {"status": "ok"}

    return app
