from collections.abc import Callable, Sequence
from logging import Logger
from typing import Any, Literal, overload

from fastapi import status
from pydantic import BaseModel, RootModel
from sqlalchemy import ScalarResult, Select, delete, func, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from fastapi_batteries.fastapi.exceptions import APIException
from fastapi_batteries.pydantic.schemas import PaginationOffsetLimit, PaginationPageSize
from fastapi_batteries.utils.pagination import page_size_to_offset_limit


class CRUD[
    ModelType: DeclarativeBase,
    SchemaCreate: BaseModel,
    SchemaPatch: BaseModel,
    SchemaUpsert: BaseModel,
]:
    """CRUD operations for SQLAlchemy models.

    Args:
        model: SQLAlchemy model
        soft_delete_col_name: Column name that represents soft delete
        resource_name: Resource name for error messages
        logger: Logger instance to log messages

    """

    def __init__(
        self,
        model: type[ModelType],
        *,
        soft_delete_col_name: str = "is_deleted",
        resource_name: str = "Resource",
        logger: Logger | None = None,
    ) -> None:
        self.model = model
        self.soft_delete_col_name = soft_delete_col_name
        self.resource_name = resource_name

        self.err_messages = {
            404: f"{self.resource_name} not found",
        }
        self.logger = logger

    @overload
    async def create(
        self,
        db: AsyncSession,
        new_data: SchemaCreate,
        *,
        commit: bool = True,
        returning: Literal[True] = True,
    ) -> ModelType: ...

    @overload
    async def create(
        self,
        db: AsyncSession,
        new_data: SchemaCreate,
        *,
        commit: bool = True,
        returning: Literal[False],
    ) -> None: ...

    @overload
    async def create(
        self,
        db: AsyncSession,
        new_data: RootModel[Sequence[SchemaCreate]],
        *,
        commit: bool = True,
        returning: Literal[True] = True,
    ) -> Sequence[ModelType]: ...

    @overload
    async def create(
        self,
        db: AsyncSession,
        new_data: RootModel[Sequence[SchemaCreate]],
        *,
        commit: bool = True,
        returning: Literal[False],
    ) -> None: ...

    async def create(
        self,
        db: AsyncSession,
        new_data: SchemaCreate | RootModel[Sequence[SchemaCreate]],
        *,
        commit: bool = True,
        returning: bool = True,
    ) -> Sequence[ModelType] | ModelType | None:
        """Create single or multiple items using insert statement.

        Args:
            db: SQLAlchemy AsyncSession
            new_data: New data to insert in the database
            commit: Whether to commit the transaction
            returning: Whether to return the inserted item(s) via `returning` clause

        Returns:
            Inserted item(s) if `returning` is True else None

        """
        # ! Don't use `jsonable_encoder`` because it can cause issue like converting datetime to string.
        # Converting date to string will cause error when inserting to database.
        statement = insert(self.model).values(new_data.model_dump())

        if returning:
            statement = statement.returning(self.model)

            # If multiple items are provided use `scalars` else use `scalar`
            if isinstance(new_data, RootModel):
                result = await db.scalars(statement)
            else:
                result = await db.scalar(statement)

            if commit:
                await db.commit()

            """
            If result is `ScalarResult` then we need to call `all()` to get the list of items.
            If result is not `ScalarResult` then we can return the result as it is.

            NOTE: We can determine same thing via `isinstance(new_data, RootModel)`
                  but mypy won't be aware of result type.
            """
            if isinstance(result, ScalarResult):
                return result.all()
            return result

        # If returning is False
        await db.execute(statement)
        if commit:
            await db.commit()
        return None

    # TODO: Type hint Any
    async def get(
        self,
        db: AsyncSession,
        item_id: int,
        **kwargs: Any,  # noqa: ANN401
    ) -> ModelType | None:
        return await db.get(self.model, item_id, **kwargs)

    # TODO: Type hint Any
    async def get_or_404(
        self,
        db: AsyncSession,
        item_id: int,
        *,
        msg_404: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> ModelType:
        if result := await db.get(self.model, item_id, **kwargs):
            return result

        raise APIException(
            status=status.HTTP_404_NOT_FOUND,
            title=msg_404 or self.err_messages[404],
        )

    # TODO: Add overload for pagination conditional return
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        pagination: PaginationPageSize | PaginationOffsetLimit | None = None,
        select_statement: Callable[[Select[tuple[ModelType]]], Select[tuple[ModelType]]] = lambda s: s,
    ) -> Sequence[ModelType] | tuple[Sequence[ModelType], int]:
        _select_statement = select_statement(select(self.model))
        paginated_statement: Select[tuple[ModelType]] | None = None

        # Pagination
        if pagination:
            if isinstance(pagination, PaginationPageSize):
                offset, limit = page_size_to_offset_limit(page=pagination.page, size=pagination.size)
            else:
                offset, limit = pagination.offset, pagination.limit

            paginated_statement = _select_statement.limit(limit).offset(offset)

        result = await db.scalars(
            paginated_statement if paginated_statement is not None else _select_statement,
        )
        records = result.unique().all()

        if pagination:
            total = await self.count(db, select_statement=_select_statement)
            return records, total
        return records

    # TODO: Can we fetch TypedDict from SchemaPatch? Using `dict[str, Any]` is not good.
    async def patch(
        self,
        db: AsyncSession,
        item_db: ModelType,
        patched_item: SchemaPatch | dict[str, Any],
        *,
        commit: bool = True,
    ) -> ModelType:
        # Get the patched data based on received item
        patched_data = patched_item if isinstance(patched_item, dict) else patched_item.model_dump(exclude_unset=True)

        for field_to_patch, field_val in patched_data.items():
            setattr(item_db, field_to_patch, field_val)

        db.add(item_db)

        if commit:
            await db.commit()
            await db.refresh(item_db)

        return item_db

    async def soft_delete(self, db: AsyncSession, item_id: int, *, commit: bool = True) -> ModelType:
        item_db = await self.get_or_404(db, item_id)

        setattr(item_db, self.soft_delete_col_name, True)

        db.add(item_db)

        if commit:
            await db.commit()
            await db.refresh(item_db)

        return item_db

    async def delete(self, db: AsyncSession, item_id: int, *, commit: bool = True) -> int:
        """Delete an item by ID. Returns the number of rows deleted.

        Args:
            db: SQLAlchemy AsyncSession
            item_id: Item ID
            commit: Whether to commit the transaction. Defaults to False.

        Returns:
            Number of rows deleted

        Raises:
            AttributeError: If model does not have `id` attribute

        """
        if not hasattr(self.model, "id"):
            msg = f"Model {self.model.__name__} must have 'id' attribute"
            raise AttributeError(msg)

        statement = delete(self.model).where(
            self.model.id == item_id,  # type: ignore We already checked if model has `id` attribute
        )

        result = await db.execute(statement)

        if commit:
            await db.commit()

        return result.rowcount

    async def count(self, db: AsyncSession, *, select_statement: Select[tuple[ModelType]] | None = None) -> int:
        count_select_from = select_statement.subquery() if select_statement is not None else self.model
        count_statement = select(func.count()).select_from(count_select_from)

        result = await db.scalars(count_statement)
        return result.first() or 0

    async def upsert(
        self,
        db: AsyncSession,
        *,
        upserted_items: RootModel[Sequence[SchemaUpsert]],
        commit: bool = True,
    ):
        """Perform batch upsert for SQLAlchemy model.

        Args:
            db (AsyncSession): SQLAlchemy AsyncSession
            upserted_items (Sequence[SchemaCreate]): List of items to upsert
            commit (bool, optional): Whether to commit the transaction. Defaults to False.

        """
        pk_columns = [col.key for col in self.model.__mapper__.primary_key]

        # Get updatable columns (excluding PKs)
        updatable_columns = [col.key for col in self.model.__mapper__.columns if col.key not in pk_columns]

        # Create upsert statement
        statement = pg_insert(self.model).values(upserted_items.model_dump())

        set_dict = {col: getattr(statement.excluded, col) for col in updatable_columns}

        statement = statement.on_conflict_do_update(index_elements=pk_columns, set_=set_dict)

        await db.execute(statement)

        if commit:
            await db.commit()
