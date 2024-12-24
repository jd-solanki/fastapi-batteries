from collections.abc import AsyncGenerator
from contextlib import suppress

import pytest
import pytest_asyncio
from pydantic import BaseModel, EmailStr
from sqlalchemy import String
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from fastapi_batteries.crud import CRUD
from fastapi_batteries.pydantic.schemas import PaginationOffsetLimit
from fastapi_batteries.sa.mixins import MixinId


class Base(DeclarativeBase): ...


# Test Models
class User(Base, MixinId):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(default=False)


# Pydantic Schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserPatch(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserUpsert(UserCreate):
    id: int


# Fixtures
@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
def user_crud() -> CRUD[User, UserCreate, UserPatch, UserUpsert]:
    return CRUD[User, UserCreate, UserPatch, UserUpsert](
        model=User,
        resource_name="User",
    )


@pytest_asyncio.fixture
async def sample_user(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
):
    user = await user_crud.create(
        db,
        UserCreate(email="test@example.com", name="Test User"),
    )

    yield user

    with suppress(PendingRollbackError):
        await db.delete(user)
        await db.commit()


# Tests
@pytest.mark.asyncio
async def test_create_user(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
) -> None:
    user_data = UserCreate(email="new@example.com", name="New User")
    user = await user_crud.create(db, user_data)

    assert user.email == "new@example.com"
    assert user.name == "New User"
    assert user.id is not None

    # TODO: Should we remove this user?
    await user_crud.delete(db, user.id)


@pytest.mark.asyncio
async def test_get_user(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
    sample_user: User,
) -> None:
    user = await user_crud.get(db, sample_user.id)
    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_404(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
) -> None:
    user = await user_crud.get(db, 999)
    assert user is None


@pytest.mark.asyncio
async def test_patch_user(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
    sample_user: User,
) -> None:
    patched_data = UserPatch(name="Updated Name")
    updated_user = await user_crud.patch(db, sample_user, patched_data)

    assert updated_user.name == "Updated Name"
    assert updated_user.email == sample_user.email


@pytest.mark.asyncio
async def test_get_multi(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
) -> None:
    # Create multiple users
    users_data = [UserCreate(email=f"user{i}@example.com", name=f"User {i}") for i in range(5)]
    print(f"users_data: {users_data}", len(users_data))
    for user_data in users_data:
        await user_crud.create(db, user_data)

    pagination = PaginationOffsetLimit(offset=0, limit=3)
    users, total = await user_crud.get_multi(db, pagination=pagination)

    assert len(users) == 3
    assert total == 5


@pytest.mark.asyncio
async def test_soft_delete(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
    sample_user: User,
) -> None:
    deleted_user = await user_crud.soft_delete(db, sample_user.id)
    assert deleted_user.is_deleted is True

    # User should still be retrievable
    user = await user_crud.get(db, sample_user.id)
    assert user is not None
    assert user.is_deleted is True


@pytest.mark.asyncio
async def test_hard_delete(
    db: AsyncSession,
    user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
    sample_user: User,
) -> None:
    await user_crud.delete(db, sample_user.id)

    # User should not be retrievable
    user = await user_crud.get(db, sample_user.id)
    assert user is None


# TODO: Why this test failing? Is our CRUD's upsert needs update?
# @pytest.mark.asyncio
# async def test_upsert(
#     db: AsyncSession,
#     user_crud: CRUD[User, UserCreate, UserPatch, UserUpsert],
#     sample_user: User,
# ) -> None:
#     from pydantic import RootModel

#     users_to_upsert = [
#         UserUpsert(id=sample_user.id, email="updated@example.com", name="Updated User"),
#         UserUpsert(id=999, email="new@example.com", name="New User"),
#     ]

#     await user_crud.upsert(
#         db,
#         upserted_items=RootModel[Sequence[UserUpsert]](users_to_upsert),
#     )

#     # Check updated user
#     updated_user = await user_crud.get(db, sample_user.id)
#     assert updated_user is not None
#     assert updated_user.email == "updated@example.com"

#     # Check new user
#     new_user = await user_crud.get(db, 999)
#     assert new_user is not None
#     assert new_user.email == "new@example.com"
