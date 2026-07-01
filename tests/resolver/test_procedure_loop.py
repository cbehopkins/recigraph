"""Tests for the Phase 8 procedure compiler loop."""

from recigraph.model import EntityReference, GraphState, Procedure, Step
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import RegistrySet, resolve_procedure_references
from recigraph.resolver.procedure_loop import run_procedure_loop, run_resolved_procedure_loop


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("sugar", "ingredient:sugar")
    ingredients.add("base_mix", "ingredient:base_mix")
    ingredients.add("heated_mix", "ingredient:heated_mix")
    procedures.add("mix", "procedure:mix")
    procedures.add("heat", "procedure:heat")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def _two_step_procedure() -> Procedure:
    return Procedure(
        id="procedure.vanilla_base",
        steps=(
            Step(
                id="mix_base",
                action=EntityReference(domain="procedure", identifier="mix"),
                outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
            ),
            Step(
                id="heat_base",
                action=EntityReference(domain="procedure", identifier="heat"),
                outputs=(EntityReference(domain="ingredient", identifier="heated_mix"),),
            ),
        ),
        inputs=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )


def test_run_procedure_loop_applies_steps_sequentially() -> None:
    procedure = _two_step_procedure()
    initial_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
        derived_entities=(),
    )

    final_graph, trace = run_procedure_loop(
        procedure,
        initial_graph=initial_graph,
        registries=_registry_set(),
    )

    assert final_graph.snapshot_id == "G2"
    assert len(trace) == 2
    assert trace[0].step_id == "mix_base"
    assert trace[1].step_id == "heat_base"
    assert trace[0].input_graph_snapshot_ref == "G0"
    assert trace[0].output_graph_snapshot_ref == "G1"
    assert trace[1].input_graph_snapshot_ref == "G1"
    assert trace[1].output_graph_snapshot_ref == "G2"


def test_run_procedure_loop_does_not_mutate_initial_graph() -> None:
    procedure = _two_step_procedure()
    initial_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
        derived_entities=(),
    )

    final_graph, _ = run_procedure_loop(
        procedure,
        initial_graph=initial_graph,
        registries=_registry_set(),
    )

    assert initial_graph.snapshot_id == "G0"
    assert initial_graph.entities == (
        EntityReference(domain="ingredient", identifier="whole_milk"),
    )
    assert final_graph.snapshot_id == "G2"


def test_run_resolved_procedure_loop_initializes_g0_and_runs_steps() -> None:
    procedure = _two_step_procedure()
    resolved = resolve_procedure_references(procedure, registries=_registry_set())

    final_graph, trace = run_resolved_procedure_loop(resolved, registries=_registry_set())

    assert trace[0].input_graph_snapshot_ref == "G0"
    assert final_graph.snapshot_id == "G2"
    assert EntityReference(domain="ingredient", identifier="heated_mix") in final_graph.entities
