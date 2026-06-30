"""Step and step-context models."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from recigraph.model.reference import EntityReference, ReferenceBinding


class StepContext(BaseModel):
    """Optional human and compiler hints for a Step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    notes: str | None = None
    tags: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


class Step(BaseModel):
    """Atomic transformation unit in a procedure."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str | None = Field(default=None, min_length=1)
    action: EntityReference
    inputs: tuple[ReferenceBinding, ...] = ()
    outputs: tuple[EntityReference, ...] = ()
    context: StepContext | None = None

    @model_validator(mode="after")
    def _validate_action_domain(self) -> Self:
        if self.action.domain != "procedure":
            raise ValueError("step action must reference a procedure")
        return self
