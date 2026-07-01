"""Graph state model."""

from pydantic import BaseModel, ConfigDict, Field

from recigraph.model.reference import EntityReference


class GraphState(BaseModel):
    """Immutable materialised graph snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_id: str = Field(min_length=1)
    entities: tuple[EntityReference, ...] = ()
    derived_entities: tuple[EntityReference, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()
