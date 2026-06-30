"""Core reference models for the ReciGraph DSL."""

import re
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

REFERENCE_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9_]+$")
PROCEDURE_REFERENCE_PATTERN = re.compile(r"^procedure\.[a-z0-9_]+(?:@[^@\s]+)?$")


class EntityReference(BaseModel):
    """Stable identity link between entities in the DSL."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    domain: Literal["ingredient", "procedure", "equipment", "container"]
    identifier: str = Field(min_length=1, pattern=REFERENCE_IDENTIFIER_PATTERN.pattern)
    version: str | int | None = None

    @property
    def reference_text(self) -> str:
        """Return the dotted DSL syntax for the reference."""

        if self.version is None:
            return f"{self.domain}.{self.identifier}"
        return f"{self.domain}.{self.identifier}@{self.version}"

    def __str__(self) -> str:
        return self.reference_text

    @model_validator(mode="after")
    def _validate_version(self) -> Self:
        if isinstance(self.version, str) and not self.version:
            raise ValueError("version must not be empty")
        return self


class Adjustment(BaseModel):
    """Step-local composition adjustment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["add", "remove", "scale"]
    target: EntityReference
    value: float | int | None = None


class Composition(BaseModel):
    """Step-local composition payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ingredients: tuple[EntityReference, ...]
    adjustments: tuple[Adjustment, ...] = ()


class Substitution(BaseModel):
    """Local replacement of an entity within a Step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    from_: EntityReference = Field(alias="from")
    to: EntityReference | Composition


class OverrideSet(BaseModel):
    """Collection of Step-local substitutions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    substitutions: tuple[Substitution, ...] = ()


class ReferenceBinding(BaseModel):
    """Binding scoped to a single Step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target: EntityReference
    override: OverrideSet | None = None
