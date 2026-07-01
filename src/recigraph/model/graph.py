"""Graph state model."""

from pydantic import BaseModel, ConfigDict, Field

from recigraph.model.reference import EntityReference


class GraphEntityIdentity(BaseModel):
    """Internal stable identity for materialized graph entities."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    domain: str = Field(min_length=1)
    identifier: str = Field(min_length=1)
    version: str | int | None = None

    @classmethod
    def from_reference(cls, reference: EntityReference) -> "GraphEntityIdentity":
        """Create a GraphEntityIdentity from a public DSL EntityReference."""

        return cls(
            domain=reference.domain,
            identifier=reference.identifier,
            version=reference.version,
        )


class GraphEdge(BaseModel):
    """Directed relationship edge between two internal graph identities."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: GraphEntityIdentity
    target: GraphEntityIdentity
    kind: str = Field(min_length=1)


class GraphState(BaseModel):
    """Immutable materialised graph snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_id: str = Field(min_length=1)
    entities: tuple[EntityReference, ...] = ()
    derived_entities: tuple[EntityReference, ...] = ()
    resolved_entities: tuple[GraphEntityIdentity, ...] = ()
    relationships: tuple[GraphEdge, ...] = ()
    provenance: tuple[tuple[str, str], ...] = ()
    diagnostics: tuple[str, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()
