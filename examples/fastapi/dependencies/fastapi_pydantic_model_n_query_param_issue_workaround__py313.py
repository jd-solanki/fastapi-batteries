from typing import Annotated

from fastapi import Depends, FastAPI

from fastapi_batteries.pydantic.schemas import PaginationPageSize

app = FastAPI()


@app.get("/items/")
async def get_items_page_size_pagination(
    pagination: Annotated[PaginationPageSize, Depends()],
    q: str = "",
):
    return {"q": q, "pagination": pagination}
