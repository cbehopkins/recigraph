"""Procedure model."""

from pydantic import BaseModel, ConfigDict, Field

from recigraph.model.reference import EntityReference
from recigraph.model.step import Step


class Procedure(BaseModel):
    """Deterministic ordered sequence of Steps."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, pattern=r"^procedure\.[a-z0-9_]+(?:@[^@\s]+)?$")
    name: str | None = None
    description: str | None = None
    steps: tuple[Step, ...]
    inputs: tuple[EntityReference, ...] = ()
    outputs: tuple[EntityReference, ...] = ()
    tags: tuple[str, ...] = ()
