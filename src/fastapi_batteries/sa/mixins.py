from datetime import datetime
from typing import ClassVar, Literal

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.sql import false


class MixinId(MappedAsDataclass):
    id: Mapped[int] = mapped_column(primary_key=True, kw_only=True, default=None)


class MixinCreatedAt(MappedAsDataclass):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.now()),
        default=None,
        kw_only=True,
    )


class MixinUpdatedAt(MappedAsDataclass):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
        default=None,
        kw_only=True,
    )


class MixinIsDeleted(MappedAsDataclass):
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default=false(), kw_only=True)


type Mixin = Literal["created_at", "updated_at", "is_deleted"]


class MixinFactory:
    """Factory mixin to create instances of the model.

    Examples:
        >>> MixinStartedAt = MixinFactory.get_renamed("created_at", "started_at")
        <class '__main__.MixinRenamed'> # This is dummy class having "started_at" database column
        >>> MixinModifiedAt = MixinFactory.get_renamed("updated_at", "modified_at")
        <class '__main__.MixinRenamed'> # This is dummy class having "modified_at" database column
        >>> class NewTable(Base, MixinStartedAt): ...

    """

    _mixin_map: ClassVar[dict[Mixin, object]] = {
        "created_at": MixinCreatedAt,
        "updated_at": MixinUpdatedAt,
        "is_deleted": MixinIsDeleted,
    }

    @staticmethod
    def get_renamed(mixin_name: Mixin, renamed_col: str):  # noqa: ANN205
        """Get the mixin with the renamed column.

        Args:
            mixin_name: Original mixin name to use as template
            renamed_col: New column name to use

        Returns:
            A new mixin class with the renamed column

        Raises:
            ValueError: If mixin_name is not valid

        """
        source_mixin = MixinFactory._mixin_map[mixin_name]
        original_col = next(iter(source_mixin.__annotations__))
        column_def = getattr(source_mixin, original_col)
        type_annotation = source_mixin.__annotations__[original_col]

        # Create new mixin class with proper type annotation
        return type(
            "_RenamedMixin",
            (MappedAsDataclass,),
            {
                renamed_col: column_def,
                "__annotations__": {renamed_col: type_annotation},
            },
        )
