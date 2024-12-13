# WrapWithAI

## Description

It provides

- Workflow automation like zapier & n8n
- AI Workforce via AI Agents which can intelligently call appropriate APIs, perform actions, AI Tools, etc.

### Workflows

- Our workflows run using celery tasks in background
- We log each workflow execution via celery signals. We store the execution info of workflow run & its node run in the database.
- We store various info like node output, errors, etc in the database for node run.

## Writing Code

- Use python 3.13 syntax & features
- Always raise exception via `ApiException` class & pass `exc_note` if required to log the internal error message for debugging.
- Use SQLAlchemy 2.0 declarative syntax for all database operations
  - Always use SQLAlchemy 2.0 syntax using `select()`, `scalar()`, `scalars()`, etc.
  - Prefer using `db.scalars()` & `db.scalar()` instead of `db.execute().scalars()`
  - Always use `mapped_column` & `Mapped` instead of `Column` & `Table` to make code modern & 100% type annotated.
- Ensure your code is 100% typed/annotated including generics and return types
- Use latest python typing features like `TypedDict`, `Literal`, `Protocols`, etc.
- Prefer using short-hand typing like `str | None` instead of `Optional[str]`
- Use newer type syntax like `list[int]` or `Sequence[int]` over `List[int]`
- Prefer using `pathlib` module over `os.path` for file operations
- Use "httpx" to make HTTP requests instead of "requests" library

### Pydantic Schema Naming Conventions for FastAPI Operations

| **Schema Name**          | **Purpose**                                                                                   |
|---------------------------|-----------------------------------------------------------------------------------------------|
| `ProductCreate`          | Public-facing schema for **creating products**.                                              |
| `ProductCreateDB?`       | Internal schema for **database operations** (e.g., auto-assigning `owner_id`).                |
| `ProductListItem`        | Schema for **individual product items** in a list (e.g., `GET /products`).                  |
| `ProductList`            | Root model schema for **the entire list** of products.                                       |
| `ProductDetails`         | Schema for **detailed view** of a product (e.g., `GET /products/{product_id}`).                     |
| `ProductUpdate?`         | Schema for **full updates** (via PUT, replacing the entire product).                         |
| `ProductUpdateDB?`       | Internal schema for **database operations** during full updates.                              |
| `ProductPatch`           | Public-facing schema for **partial updates** (via PATCH).                                     |
| `ProductPatchDB?`        | Internal schema for **database operations** during partial updates.                           |

The **`?`** indicates that the schema is optional and only needed in certain cases. For example, `ProductCreateDB` might be used if you need to assign internal fields like `owner_id` or `last_updated_by` during creation, but if such fields aren’t required, you can skip defining this schema.

### Naming Conventions

#### Resource Name in FastAPI Operations

Use below prefixes to resource name schema for different operations.

- `new_` for `post` operations
- `updated_` for `put` operations
- `patched_` for `patch` operations

Don't use suffixes like `_in` or `_out`.

```py
@app.post(
    "/items",
    response_model=schemas.ItemDetails,
)
async def create_item(
    item_in: schemas.ItemCreate, // [!code --]
    new_item: schemas.ItemCreate, // [!code ++]
    db: AsyncSession = Depends(get_db),
):
    return await item_crud.create(db, new_item)

@app.patch(
    "/items/{item_id}",
    response_model=schemas.ItemDetails,
)
async def patch_item(
    item_id: PositiveInt,
    item_in: schemas.ItemPatch, // [!code --]
    patched_item: schemas.ItemPatch, // [!code ++]
    db: AsyncSession = Depends(get_db),
):
    db_item = await item_crud.get_or_404(db, item_id)
    return await item_crud.patch(db, db_item, patched_item)
```

#### Naming DB records in FastAPI Operations

Use `db_` prefix for retrieved record from DB

```py
@app.patch(
    "/items/{item_id}",
    response_model=schemas.ItemDetails,
)
async def patch_item(
    item_id: PositiveInt,
    patched_item: schemas.ItemPatch,
    db: AsyncSession = Depends(get_db),
):
    db_item = await item_crud.get_or_404(db, item_id)
    return await item_crud.patch(db, db_item, patched_item)
```

#### Provide valid types for `id` parameters

Use `PositiveInt` for integer based `id` parameters instead of `int`

```py
@app.get(
    "/items/{item_id}",
    response_model=schemas.ItemDetails,
)
async def get_item(
    item_id: int, // [!code --]
    item_id: PositiveInt, // [!code ++]
    db: AsyncSession = Depends(get_db),
):
    return await item_crud.get_or_404(db, item_id)
```

## Code Quality

- Ensure your code/solution is
  - ROBUST, CLEAN, SCALABLE, PERFORMANT & EFFICIENT
  - Not over complicated
  - performant and doesn't have any performance bottlenecks.
  - well commented
  - 100% type annotated
- Avoid things like unwanted loops, nested loops, etc to make code faster

## Notes

- Our most of the users will be using
  - Postgres (asyncpg)
  - SQLAlchemy 2.0 + Declarative Syntax
  - FastAPI latest version
  - Pydantic latest version
