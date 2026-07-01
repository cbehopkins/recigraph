"""Phase 7 step execution engine."""

from recigraph.model import (
    Composition,
    EntityReference,
    GraphState,
    ReferenceBinding,
    Step,
    StepExecutionRecord,
)
from recigraph.resolver.resolver import RegistrySet, resolve_reference


def _next_snapshot_id(snapshot_id: str) -> str:
    if snapshot_id.startswith("G") and snapshot_id[1:].isdigit():
        return f"G{int(snapshot_id[1:]) + 1}"
    return f"{snapshot_id}_next"


def _append_unique(
    existing: tuple[EntityReference, ...],
    additions: tuple[EntityReference, ...],
) -> tuple[EntityReference, ...]:
    items = list(existing)
    seen = set(existing)
    for item in additions:
        if item in seen:
            continue
        items.append(item)
        seen.add(item)
    return tuple(items)


def _binding_rewrite_targets(binding: ReferenceBinding) -> tuple[EntityReference, ...]:
    if binding.override is None or not binding.override.substitutions:
        return (binding.target,)

    current_targets: tuple[EntityReference, ...] = (binding.target,)
    for substitution in binding.override.substitutions:
        updated: list[EntityReference] = []
        for target in current_targets:
            if target != substitution.from_:
                updated.append(target)
                continue

            if isinstance(substitution.to, EntityReference):
                updated.append(substitution.to)
            else:
                composition: Composition = substitution.to
                updated.extend(composition.ingredients)
        current_targets = tuple(updated)
    return current_targets


def _rewrite_entities(
    entities: tuple[EntityReference, ...],
    bindings: tuple[ReferenceBinding, ...],
) -> tuple[EntityReference, ...]:
    rewritten = list(entities)
    for binding in bindings:
        targets = _binding_rewrite_targets(binding)
        next_rewritten: list[EntityReference] = []
        for entity in rewritten:
            if entity == binding.target:
                next_rewritten.extend(targets)
            else:
                next_rewritten.append(entity)
        rewritten = next_rewritten
    return tuple(rewritten)


def _binding_transformation_notes(bindings: tuple[ReferenceBinding, ...]) -> tuple[str, ...]:
    notes: list[str] = []
    for binding in bindings:
        if binding.override is None:
            continue
        for substitution in binding.override.substitutions:
            if isinstance(substitution.to, EntityReference):
                notes.append(
                    f"substitute:{substitution.from_.reference_text}->{substitution.to.reference_text}"
                )
                continue

            composition_targets = ",".join(
                ingredient.reference_text for ingredient in substitution.to.ingredients
            )
            notes.append(f"substitute:{substitution.from_.reference_text}->[{composition_targets}]")
    return tuple(notes)


def apply_step(
    input_graph: GraphState,
    step: Step,
    *,
    registries: RegistrySet,
    step_index: int,
) -> tuple[GraphState, StepExecutionRecord]:
    """Apply a single Step transformation to produce G(n+1) and a trace record."""

    action_resolved = resolve_reference(
        step.action,
        path=f"procedure.steps[{step_index}].action",
        registries=registries,
    )

    rewritten_entities = _rewrite_entities(input_graph.entities, step.inputs)
    output_entities = _append_unique(rewritten_entities, step.outputs)

    substituted_entities = tuple(
        item
        for binding in step.inputs
        for item in _binding_rewrite_targets(binding)
        if item != binding.target
    )
    output_derived = _append_unique(input_graph.derived_entities, substituted_entities)
    output_derived = _append_unique(output_derived, step.outputs)

    output_snapshot_id = _next_snapshot_id(input_graph.snapshot_id)

    output_graph = GraphState(
        snapshot_id=output_snapshot_id,
        entities=output_entities,
        derived_entities=output_derived,
        metadata=(*input_graph.metadata, ("last_action", action_resolved.reference.reference_text)),
    )

    step_id = step.id or f"step_{step_index}"
    transformation_items = [
        f"action:{action_resolved.entity}",
        *_binding_transformation_notes(step.inputs),
    ]
    if step.outputs:
        transformation_items.append(
            "outputs:" + ",".join(output.reference_text for output in step.outputs)
        )
    transformations = tuple(transformation_items)

    record = StepExecutionRecord(
        step_id=step_id,
        input_graph_snapshot_ref=input_graph.snapshot_id,
        applied_bindings=step.inputs,
        output_graph_snapshot_ref=output_graph.snapshot_id,
        transformations_applied=transformations,
    )

    return output_graph, record
