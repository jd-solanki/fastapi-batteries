# TODO: Move generic utils that are not related to fastapi batteries to a separate package "pytils-jd"
from typing import Annotated, Any, Literal

from pydantic import Field

type Environment = Literal["development", "staging", "production", "testing"]
type TODO = Any

# * You can also get same type via pydantic's JSONValue (https://docs.pydantic.dev/latest/api/types/#pydantic.types.JsonValue)
type JSONType = str | int | float | bool | None | dict[str, "JSONType"] | list["JSONType"]
type DictJSON = dict[str, JSONType]
type ListJSON = list[JSONType]


# DB-Pydantic Types
type PostgresSmallInt = Annotated[int, Field(ge=-32768, le=32767)]
type PostgresPositiveSmallInt = Annotated[int, Field(ge=1, le=32767)]
