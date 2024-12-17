from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status
from pydantic import BaseModel, PositiveInt, RootModel
from sqlalchemy import String, select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from fastapi_batteries.crud import CRUD
from fastapi_batteries.fastapi.exceptions import APIException, get_api_exception_handler
from fastapi_batteries.fastapi.middlewares import QueryCountMiddleware
from fastapi_batteries.pydantic.schemas import Paginated, PaginationOffsetLimit
from fastapi_batteries.sa.mixins import MixinId


# --- DB
class Base(DeclarativeBase, MappedAsDataclass): ...


class User(Base, MixinId):
    __tablename__ = "user"

    first_name: Mapped[str] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(default=True)


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("--- creating tables...")
        await conn.run_sync(Base.metadata.create_all)


# --- Schemas


class UserBase(BaseModel):
    first_name: str


class UserBasePartial(BaseModel):
    first_name: str | None = None


class UserCreate(UserBase): ...


class UserPatch(UserBasePartial): ...


class UserRead(UserBase):
    id: PositiveInt


# --- FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    async with async_session_maker() as db:
        db.add_all(
            [
                User(first_name="John"),
                User(first_name="Jane"),
                User(first_name="Alice"),
                User(first_name="Bob"),
                User(first_name="Charlie"),
            ],
        )
        await db.commit()
    yield


app = FastAPI(
    lifespan=lifespan,
    exception_handlers={
        APIException: get_api_exception_handler(),
    },
)

app.add_middleware(QueryCountMiddleware, engine)

# --- CRUD

user_crud = CRUD[User, UserCreate, UserPatch, BaseModel](model=User, resource_name="User")


@app.post("/users/")
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.create(db, user)


@app.post("/users/multi")
async def create_users(users: RootModel[Sequence[UserCreate]], db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.create(db, users)


@app.get("/users/", response_model=Paginated[UserRead])
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationOffsetLimit, Depends(PaginationOffsetLimit)],
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User)

    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    db_users, total = await user_crud.get_multi(
        db,
        pagination=pagination,
        select_statement=lambda _: select_statement,
    )

    return {
        "data": db_users,
        "meta": {"total": total},
    }


@app.get("/users/with-first-name-and-is-active")
async def get_users_with_cols(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationOffsetLimit, Depends(PaginationOffsetLimit)],
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User.first_name, User.is_active)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    db_users, total = await user_crud.get_multi_for_cols(
        db,
        pagination=pagination,
        select_statement=select_statement,
        as_mappings=True,
    )

    return {
        "data": db_users,
        "meta": {"total": total},
    }


@app.get("/users/count")
async def get_users_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    return await user_crud.count(db, select_statement=lambda _: select_statement)


@app.get("/users/one")
async def get_one_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: PositiveInt | None = None,
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User)
    if user_id:
        select_statement = select_statement.where(User.id == user_id)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    try:
        return await user_crud.get_one_or_404(
            db,
            select_statement=lambda _: select_statement,
            msg_multiple_results_exc="Multiple users found",
        )
    except MultipleResultsFound as e:
        raise APIException(
            title="Multiple results found",
            status=status.HTTP_400_BAD_REQUEST,
        ) from e


@app.get("/users/one/with-first-name-and-is-active", response_model=UserRead)
async def get_user_with_cols(
    db: Annotated[AsyncSession, Depends(get_db)],
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User.first_name, User.id)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    return await user_crud.get_one_for_cols(
        db,
        select_statement=select_statement,
        as_mappings=True,
    )


@app.get("/users/exist")
async def user_exist(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: PositiveInt | None = None,
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User)
    if user_id:
        select_statement = select_statement.where(User.id == user_id)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    return await user_crud.exist(db, select_statement=lambda _: select_statement)


@app.get("/users/exist_n")
async def user_exist_n(
    db: Annotated[AsyncSession, Depends(get_db)],
    n: int,
    user_id: PositiveInt | None = None,
    first_name: str = "",
    first_name__contains: str = "",
):
    select_statement = select(User)
    if user_id:
        select_statement = select_statement.where(User.id == user_id)
    if first_name:
        select_statement = select_statement.where(User.first_name == first_name)
    if first_name__contains:
        select_statement = select_statement.where(User.first_name.contains(first_name__contains))

    return await user_crud.exist_n(db, select_statement=lambda _: select_statement, n=n)


@app.get("/users/{user_id}")
async def get_user(user_id: PositiveInt, db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.get_or_404(db, user_id)


# @app.patch("/users/{user_id}")
# async def patch_user(user_id: PositiveInt, user: UserPatch, db: Annotated[AsyncSession, Depends(get_db)]):
#     return await user_crud.patch(db, user_id, user)
