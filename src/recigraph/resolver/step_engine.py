"""Phase 7 step execution engine."""

from recigraph.model import GraphState, Step, StepExecutionRecord
from recigraph.resolver.graph_transformer import DefaultGraphTransformer
from recigraph.resolver.resolver import RegistrySet


def apply_step(
    input_graph: GraphState,
    step: Step,
    *,
    registries: RegistrySet,
    step_index: int,
) -> tuple[GraphState, StepExecutionRecord]:
    """Apply a single Step transformation to produce G(n+1) and a trace record."""

    transformer = DefaultGraphTransformer()
    return transformer.apply_step(
        input_graph,
        step,
        registries=registries,
        step_index=step_index,
    )
