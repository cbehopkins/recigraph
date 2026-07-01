"""Phase 6 graph-state initializer."""

from recigraph.model import GraphState
from recigraph.resolver.resolver import ResolvedProcedureReferences

_INITIAL_SNAPSHOT_ID = "G0"


def initialize_graph_state(resolved: ResolvedProcedureReferences) -> GraphState:
    """Create the initial immutable graph state (G0) from resolved procedure inputs."""

    input_paths = {
        f"procedure.inputs[{index}]" for index, _ in enumerate(resolved.procedure.inputs)
    }
    input_resolved = tuple(item for item in resolved.references if item.path in input_paths)

    entities = tuple(item.reference for item in input_resolved)
    resolved_entities = tuple(item.identity for item in input_resolved)
    metadata = (
        ("snapshot", _INITIAL_SNAPSHOT_ID),
        ("source_procedure_id", resolved.procedure.id),
        ("input_count", str(len(entities))),
        (
            "entity_map",
            ",".join(f"{item.reference.reference_text}={item.entity}" for item in input_resolved),
        ),
    )

    return GraphState(
        snapshot_id=_INITIAL_SNAPSHOT_ID,
        entities=entities,
        derived_entities=(),
        resolved_entities=resolved_entities,
        metadata=metadata,
    )
