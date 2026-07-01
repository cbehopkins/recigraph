"""Phase 8 procedure compiler loop."""

from recigraph.model import GraphState, Procedure, StepExecutionRecord
from recigraph.resolver.graph_init import initialize_graph_state
from recigraph.resolver.resolver import RegistrySet, ResolvedProcedureReferences
from recigraph.resolver.step_engine import apply_step


def run_procedure_loop(
    procedure: Procedure,
    *,
    initial_graph: GraphState,
    registries: RegistrySet,
) -> tuple[GraphState, tuple[StepExecutionRecord, ...]]:
    """Apply procedure steps in order, returning final graph and full trace."""

    graph = initial_graph
    trace: list[StepExecutionRecord] = []

    for step_index, step in enumerate(procedure.steps):
        graph, record = apply_step(graph, step, registries=registries, step_index=step_index)
        trace.append(record)

    return graph, tuple(trace)


def run_resolved_procedure_loop(
    resolved: ResolvedProcedureReferences,
    *,
    registries: RegistrySet,
) -> tuple[GraphState, tuple[StepExecutionRecord, ...]]:
    """Initialize G0 from resolved inputs, then run the full procedure loop."""

    g0 = initialize_graph_state(resolved)
    return run_procedure_loop(resolved.procedure, initial_graph=g0, registries=registries)
