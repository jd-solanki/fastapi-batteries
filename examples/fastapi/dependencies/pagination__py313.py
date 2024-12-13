from typing import Annotated

from fastapi import FastAPI, Query

from fastapi_batteries.pydantic.schemas import PaginationOffsetLimit, PaginationPageSize

app = FastAPI()


@app.get("/items/")
async def get_items_page_size_pagination(pagination: Annotated[PaginationPageSize, Query()]):
    return pagination


@app.get("/products/")
async def get_products_offset_limit_pagination(pagination: Annotated[PaginationOffsetLimit, Query()]):
    return pagination
