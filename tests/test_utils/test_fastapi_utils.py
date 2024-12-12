import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import PositiveInt

from fastapi_batteries.fastapi.utils import use_route_path_as_operation_ids


@pytest.mark.asyncio
async def test_use_route_path_as_operation_ids(app: FastAPI):  # noqa: C901
    # Items
    @app.post("/items")
    async def create_item(): ...

    @app.get("/items")
    async def get_items(): ...

    @app.get("/items/{item_id}")
    async def get_item(item_id: PositiveInt): ...

    @app.put("/items/{item_id}")
    async def put_item(item_id: PositiveInt): ...

    @app.patch("/items/{item_id}")
    async def patch_item(item_id: PositiveInt): ...

    @app.delete("/items/{item_id}")
    async def delete_item(item_id: PositiveInt): ...

    # Sub items
    @app.get("/items/{item_id}/subitems")
    async def get_item_subitems(item_id: PositiveInt): ...

    use_route_path_as_operation_ids(app)

    for route in app.routes:
        if isinstance(route, APIRoute):
            # Health
            if route.path_format == "/health" and route.methods == {"GET"}:
                assert route.operation_id == "get_health"

            # Items
            if route.path_format == "/items" and route.methods == {"POST"}:
                assert route.operation_id == "post_items"

            if route.path_format == "/items" and route.methods == {"GET"}:
                assert route.operation_id == "get_items"

            if route.path_format == "/items/{item_id}" and route.methods == {"GET"}:
                assert route.operation_id == "get_items__item_id"

            if route.path_format == "/items/{item_id}" and route.methods == {"PUT"}:
                assert route.operation_id == "put_items__item_id"

            if route.path_format == "/items/{item_id}" and route.methods == {"PATCH"}:
                assert route.operation_id == "patch_items__item_id"

            if route.path_format == "/items/{item_id}" and route.methods == {"DELETE"}:
                assert route.operation_id == "delete_items__item_id"

            # Sub items
            if route.path_format == "/items/{item_id}/subitems" and route.methods == {"GET"}:
                assert route.operation_id == "get_items__item_id__subitems"
