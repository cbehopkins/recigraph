"""Tests for the Phase 7 step execution engine."""

import pytest

from recigraph.model import (
    Composition,
    EntityReference,
    GraphState,
    OverrideSet,
    ReferenceBinding,
    Step,
    Substitution,
)
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import ReferenceResolutionError, RegistrySet
from recigraph.resolver.step_engine import apply_step


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("oat_milk", "ingredient:oat_milk")
    ingredients.add("sugar", "ingredient:sugar")
    ingredients.add("base_mix", "ingredient:base_mix")
    procedures.add("mix", "procedure:mix")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def test_apply_step_creates_next_graph_and_trace_record() -> None:
    input_graph = GraphState(
        snapshot_id="G0",
        entities=(
            EntityReference(domain="ingredient", identifier="whole_milk"),
            EntityReference(domain="ingredient", identifier="sugar"),
        ),
    )
    step = Step(
        id="mix_base",
        action=EntityReference(domain="procedure", identifier="mix"),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )

    output_graph, record = apply_step(input_graph, step, registries=_registry_set(), step_index=0)

    assert input_graph.snapshot_id == "G0"
    assert output_graph.snapshot_id == "G1"
    assert record.step_id == "mix_base"
    assert record.input_graph_snapshot_ref == "G0"
    assert record.output_graph_snapshot_ref == "G1"
    assert record.transformation_summary.startswith("action=procedure.mix;")
    assert EntityReference(domain="ingredient", identifier="base_mix") in output_graph.entities
    assert output_graph.relationships
    assert output_graph.provenance == (("mix_base", "procedure.mix"),)


def test_apply_step_applies_local_substitution_without_mutating_input_graph() -> None:
    input_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )
    step = Step(
        action=EntityReference(domain="procedure", identifier="mix"),
        inputs=(
            ReferenceBinding(
                target=EntityReference(domain="ingredient", identifier="whole_milk"),
                override=OverrideSet(
                    substitutions=(
                        Substitution.model_validate({
                            "from": EntityReference(domain="ingredient", identifier="whole_milk"),
                            "to": EntityReference(domain="ingredient", identifier="oat_milk"),
                        }),
                    )
                ),
            ),
        ),
    )

    output_graph, record = apply_step(input_graph, step, registries=_registry_set(), step_index=0)

    assert input_graph.entities == (EntityReference(domain="ingredient", identifier="whole_milk"),)
    assert output_graph.entities == (EntityReference(domain="ingredient", identifier="oat_milk"),)
    assert "bindings=1" in record.transformation_summary
    assert any(item.startswith("substitute:") for item in record.transformations_applied)


def test_apply_step_supports_composition_substitution() -> None:
    input_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )
    step = Step(
        action=EntityReference(domain="procedure", identifier="mix"),
        inputs=(
            ReferenceBinding(
                target=EntityReference(domain="ingredient", identifier="whole_milk"),
                override=OverrideSet(
                    substitutions=(
                        Substitution.model_validate({
                            "from": EntityReference(domain="ingredient", identifier="whole_milk"),
                            "to": Composition(
                                ingredients=(
                                    EntityReference(domain="ingredient", identifier="oat_milk"),
                                    EntityReference(domain="ingredient", identifier="sugar"),
                                )
                            ),
                        }),
                    )
                ),
            ),
        ),
    )

    output_graph, _ = apply_step(input_graph, step, registries=_registry_set(), step_index=0)

    assert output_graph.entities == (
        EntityReference(domain="ingredient", identifier="oat_milk"),
        EntityReference(domain="ingredient", identifier="sugar"),
    )
    assert (
        EntityReference(domain="ingredient", identifier="oat_milk") in output_graph.derived_entities
    )


def test_apply_step_requires_resolvable_action() -> None:
    input_graph = GraphState(snapshot_id="G0", entities=())
    step = Step(action=EntityReference(domain="procedure", identifier="missing"))

    with pytest.raises(ReferenceResolutionError):
        apply_step(input_graph, step, registries=_registry_set(), step_index=0)
