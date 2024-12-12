from collections.abc import Sequence

from pydantic import BaseModel, NonNegativeInt, PositiveInt, RootModel

PlaceholderSchema = BaseModel
PlaceholderRootModel = RootModel


class _PaginatedMeta(BaseModel):
    total: NonNegativeInt


class Paginated[T](BaseModel):
    data: Sequence[T] | RootModel[Sequence[T]]
    meta: _PaginatedMeta


class PaginationPageSize(BaseModel):
    """We can use this as a query parameter schema for pagination.

    If you're using this schema along with other query param then you might need to abuse Depends to use this schema.
    Please refer to this existing issue: https://github.com/fastapi/fastapi/issues/12402

    Example:
        >>> async def get_items(page_size: Annotated[PaginationPageSize, Query()]): ...
        >>> async def get_items(
        >>>     q: q: str | None = None, # Specific to this endpoint
        >>>     page_size: Annotated[PaginationPageSize, Depends(PaginationPageSize)] # Abuse Depends to use this schema
        >>> ): ...

    """

    page: PositiveInt = 1
    size: PositiveInt = 10


class PaginationOffsetLimit(BaseModel):
    """We can use this as a query parameter schema for pagination.

    If you're using this schema along with other query param then you might need to abuse Depends to use this schema.
    Please refer to this existing issue: https://github.com/fastapi/fastapi/issues/12402

    Example:
        >>> async def get_items(offset_limit: Annotated[PaginationOffsetLimit, Query()]): ...
        >>> async def get_items(
        >>>     q: q: str | None = None, # Specific to this endpoint
        >>>     offset_limit: Annotated[PaginationOffsetLimit, Depends(PaginationOffsetLimit)] # Use Depends to use this schema
        >>> ): ...

    """

    offset: NonNegativeInt = 0
    limit: PositiveInt = 10
