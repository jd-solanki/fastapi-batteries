from collections.abc import Callable, Sequence
from logging import Logger
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, RootModel
from sqlalchemy import Select, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from fastapi_batteries.fastapi.exceptions import APIException
from fastapi_batteries.pydantic.schemas import PaginationOffsetLimit, PaginationPageSize


class CRUD[
    ModelType: DeclarativeBase,
    SchemaCreate: BaseModel,
    SchemaPatch: BaseModel,
    SchemaUpsert: BaseModel,
]:
    def __init__(
        self,
        *,
        model: type[ModelType],
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

    # TODO: Add proper types for refresh_kwargs
    async def create(
        self,
        db: AsyncSession,
        new_item: SchemaCreate,
        *,
        refresh_kwargs: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> ModelType:
        # ! Don't use `jsonable_encoder`` because it can cause issue like converting datetime to string.
        # Converting date to string will cause error when inserting to database.
        item_db = self.model(**new_item.model_dump())
        db.add(item_db)

        if commit:
            await db.commit()
            await db.refresh(item_db, **(refresh_kwargs or {}))
        elif refresh_kwargs and self.logger:
            self.logger.warning("refresh_kwargs is ignored because commit is False")

        return item_db

    # TODO: Check how many insert statements gets executed when inserting multiple items.
    async def create_multi(
        self,
        db: AsyncSession,
        new_items: Sequence[SchemaCreate],
        *,
        refresh_kwargs: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> Sequence[ModelType]:
        items_db = [self.model(**new_item.model_dump()) for new_item in new_items]
        db.add_all(items_db)

        if commit:
            await db.commit()

            # TODO: Improve this to perform all await db.refresh in simultaneously
            for item_db in items_db:
                await db.refresh(item_db, **(refresh_kwargs or {}))
        elif refresh_kwargs and self.logger:
            self.logger.warning("refresh_kwargs is ignored because commit is False")

        return items_db

    async def get(
        self,
        db: AsyncSession,
        item_id: int,
        **kwargs: Any,  # noqa: ANN401
    ) -> ModelType | None:
        return await db.get(self.model, item_id, **kwargs)

    # TODO: Remove Any
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

        # TODO: Allow raising error with specific detail generic like `TypedDict` or `BaseModel`
        raise APIException(
            status=status.HTTP_404_NOT_FOUND,
            title=msg_404 or self.err_messages[404],
        )

    # TODO: Allow to fetch records without pagination
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        pagination: PaginationPageSize | PaginationOffsetLimit | None = None,
        select_statement: Callable[[Select[tuple[ModelType]]], Select[tuple[ModelType]]] = lambda s: s,
    ) -> Sequence[ModelType]:
        pagination = pagination or PaginationOffsetLimit(offset=0, limit=10)

        _select_statement = select_statement(select(self.model))

        # Pagination
        # * Mypy sucks if we try to extract limit & offset from below if-else
        if isinstance(pagination, PaginationOffsetLimit):
            _select_statement = _select_statement.limit(pagination.limit).offset(pagination.offset)
        else:
            limit = pagination.size
            offset = (pagination.page - 1) * limit
            _select_statement = _select_statement.limit(limit).offset(offset)

        result = await db.scalars(_select_statement)
        return result.unique().all()

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

    async def count(self, db: AsyncSession, *, select_statement: Select[tuple[int]]) -> int:
        result = await db.scalars(select_statement)
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
