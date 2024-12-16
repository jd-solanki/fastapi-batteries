from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, PositiveInt, RootModel
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from fastapi_batteries.crud import CRUD
from fastapi_batteries.fastapi.exceptions import get_api_exception_handler
from fastapi_batteries.fastapi.exceptions.api_exception import APIException
from fastapi_batteries.fastapi.middlewares import QueryCountMiddleware
from fastapi_batteries.sa.mixins import MixinId


# --- DB
class Base(DeclarativeBase, MappedAsDataclass): ...


class User(Base, MixinId):
    __tablename__ = "user"

    first_name: Mapped[str | None] = mapped_column(String(30))


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


class UserCreate(BaseModel):
    first_name: str | None = None


class UserPatch(BaseModel):
    first_name: str | None = None


# --- FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    # async with async_session_maker() as db:
    #     # Perform DB operations
    yield


app = FastAPI(
    lifespan=lifespan,
    exception_handlers={
        APIException: get_api_exception_handler(),
    },
)

app.add_middleware(QueryCountMiddleware, engine)

# --- CRUD

user_crud = CRUD[User, UserCreate, UserPatch, BaseModel](model=User)


@app.post("/users/")
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.create(db, user)


@app.post("/users/multi")
async def create_users(users: RootModel[Sequence[UserCreate]], db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.create(db, users)


@app.get("/users/")
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.get_multi(db)


@app.get("/users/{user_id}")
async def get_user(user_id: PositiveInt, db: Annotated[AsyncSession, Depends(get_db)]):
    return await user_crud.get(db, user_id)
    # return await user_crud.get_or_404(db, user_id)


# @app.patch("/users/{user_id}")
# async def patch_user(user_id: PositiveInt, user: UserPatch, db: Annotated[AsyncSession, Depends(get_db)]):
#     return await user_crud.patch(db, user_id, user)
