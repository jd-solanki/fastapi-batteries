# Mixins

You might have created some mixins which you use through out the project and also across multiple projects.

Here are some common mixins which you can reuse without building your own along with feature to rename column names.

!!! note

    All mixins inherit from [`MappedAsDataclass`](https://docs.sqlalchemy.org/en/20/orm/dataclasses.html) to get maximum type hints while using SQLAlchemy 2.x

    If you don't know what is `MappedAsDataclass`, This is similar to adding type hints features of SQLModel to our regular SQLAlchemy

All of the mixins are self explanatory so here's list of all:

- `MixinId`
- `MixinCreatedAt`
- `MixinUpdatedAt`
- `MixinIsDeleted`

Using all of the mixin is straight forward so here's minimal example for all of them:

```py hl_lines="1 3"
from fastapi_battries.sa.mixins import MixinId

class Product(Base, MixinId):
    __tablename__ = "product"

    title: Mapped[str]
```

You can view source code of all mixins [here](https://github.com/jd-solanki/fastapi-batteries/blob/main/src/fastapi_batteries/sa/mixins.py).

## `MixinFactory`

Sometime, You might want renamed column for example when using `MixinUpdatedAt` you'll get `updated_at` column but you want column name as `last_modified_at` or `started_at` to make it more meaningful according to your model. For this, `MixinFactory` allows you to generate renamed column from existing mixins.

```py
from fastapi_batteries.sa.mixins import MixinFactory, MixinId

MixinStartedAt = MixinFactory.get_renamed("created_at", "started_at")

class Workflow(Base, MixinId, MixinStartedAt):
    __tablename__ = "workflow"

    title: Mapped[str]
```
